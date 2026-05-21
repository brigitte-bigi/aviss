"""
:filename: video_ops.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Video operations for AViSS.

..
    This file is part of AViSS.
    -------------------------------------------------------------------------
    Copyright (C) 2026  Brigitte Bigi, CNRS
    Laboratoire Parole et Langage, Aix-en-Provence, France

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.

    This banner notice must not be removed.
    -------------------------------------------------------------------------

This module provides video file operations used by the AViSS pipeline.
All operations are grouped in the VideoOps class as static methods.

sppasVideoReader (OpenCV wrapper from SPPAS) is used for reading video
metadata. It guarantees frame-accurate seeking, which is essential for
synchronization. ffmpeg is used for all video transformations.

The recommended processing order when trimming a video is:
    1. trim  (frame-accurate, re-encode to MKV/H265)
    2. crop  (if requested)
    3. copyright overlay (if configured)
    4. rotate (if requested)

Each step produces an intermediate MKV file. Intermediate files are removed
after each step to save disk space.

"""

import os

from sppas.src.videodata import sppasVideoReader

from aviss.settings import cfg
from aviss.utils import check_file, run_command

# ---------------------------------------------------------------------------


class VideoOps:
    """Static methods for video file operations used by the AViSS pipeline.

    All methods wrap ffmpeg commands or sppasVideoReader calls.
    sppasVideoReader is used exclusively for reading video metadata because
    it guarantees frame-accurate seeking via OpenCV.

    :example:
    >>> info = VideoOps.get_video_info("/data/rec.mp4")
    >>> info["fps"]
    50.0
    >>> info["nframes"]
    750

    """

    # -----------------------------------------------------------------------
    # Video metadata
    # -----------------------------------------------------------------------

    @staticmethod
    def get_video_info(path: str) -> dict:
        """Return basic metadata of a video file via sppasVideoReader.

        :example:
        >>> info = VideoOps.get_video_info("/data/rec.mp4")
        >>> info["fps"]
        50.0
        >>> info["duration"]
        15.0

        :param path: (str) Path to the video file.
        :return: (dict) Keys: "fps" (float), "nframes" (int),
                 "duration" (float, seconds), "width" (int), "height" (int).
        :raises: TypeError: path is not a non-empty string.
        :raises: FileNotFoundError: The file does not exist.
        :raises: IOError: sppasVideoReader could not open the file.

        """
        if isinstance(path, str) is False or len(path.strip()) == 0:
            raise TypeError("path must be a non-empty string.")
        check_file(path)

        bv = sppasVideoReader()
        try:
            bv.open(path)
            info = {
                "fps":      bv.get_framerate(),
                "nframes":  bv.get_nframes(),
                "duration": bv.get_duration(),
                "width":    bv.get_width(),
                "height":   bv.get_height(),
            }
        except Exception as e:
            raise IOError(f"sppasVideoReader could not open {path!r}: {e}.")
        finally:
            bv.close()

        return info

    # -----------------------------------------------------------------------
    # Frame index helpers
    # -----------------------------------------------------------------------

    @staticmethod
    def time_to_frame(time_seconds: float, fps: float) -> int:
        """Return the index of the frame that contains a given time position.

        The frame index is the integer part of time * fps.
        Frame indices are 0-based: frame 0 covers [0, 1/fps[.

        :example:
        >>> VideoOps.time_to_frame(0.120, 25.)
        3
        >>> VideoOps.time_to_frame(0.0, 50.)
        0

        :param time_seconds: (float) Time position in seconds.
        :param fps: (float) Frame rate of the video in frames per second.
        :return: (int) 0-based frame index.
        :raises: TypeError: time_seconds or fps is not a number.
        :raises: ValueError: time_seconds is negative or fps is not positive.

        """
        if isinstance(time_seconds, (int, float)) is False:
            raise TypeError("time_seconds must be a number.")
        if isinstance(fps, (int, float)) is False:
            raise TypeError("fps must be a number.")
        if float(time_seconds) < 0.:
            raise ValueError("time_seconds must be zero or positive.")
        if float(fps) <= 0.:
            raise ValueError("fps must be strictly positive.")

        return int(float(time_seconds) * float(fps))

    # -----------------------------------------------------------------------

    @staticmethod
    def frame_to_time(frame_index: int, fps: float) -> float:
        """Return the start time of a frame given its index and the frame rate.

        :example:
        >>> VideoOps.frame_to_time(3, 25.)
        0.12
        >>> VideoOps.frame_to_time(0, 50.)
        0.0

        :param frame_index: (int) 0-based frame index.
        :param fps: (float) Frame rate of the video in frames per second.
        :return: (float) Start time of the frame in seconds.
        :raises: TypeError: frame_index is not an integer or fps is not a number.
        :raises: ValueError: frame_index is negative or fps is not positive.

        """
        if isinstance(frame_index, int) is False:
            raise TypeError("frame_index must be an integer.")
        if isinstance(fps, (int, float)) is False:
            raise TypeError("fps must be a number.")
        if frame_index < 0:
            raise ValueError("frame_index must be zero or positive.")
        if float(fps) <= 0.:
            raise ValueError("fps must be strictly positive.")

        return float(frame_index) / float(fps)

    # -----------------------------------------------------------------------

    @staticmethod
    def end_frame_index(clap_time: float, duration: float, fps: float) -> int:
        """Return the index of the first frame NOT included in the output.

        The end frame is computed as 1 + int((clap_time + duration) * fps).
        This guarantees that the last included frame fully covers the expected
        duration.

        :param clap_time: (float) Clap time in the video (seconds).
        :param duration: (float) Expected output duration (seconds).
        :param fps: (float) Frame rate in frames per second.
        :return: (int) Index of the first excluded frame.
        :raises: TypeError: Any argument is not a number.
        :raises: ValueError: Any argument is not strictly positive (clap_time >= 0).

        """
        if isinstance(clap_time, (int, float)) is False:
            raise TypeError("clap_time must be a number.")
        if isinstance(duration, (int, float)) is False:
            raise TypeError("duration must be a number.")
        if isinstance(fps, (int, float)) is False:
            raise TypeError("fps must be a number.")
        if float(clap_time) < 0.:
            raise ValueError("clap_time must be zero or positive.")
        if float(duration) <= 0.:
            raise ValueError("duration must be strictly positive.")
        if float(fps) <= 0.:
            raise ValueError("fps must be strictly positive.")

        real_end_time = float(clap_time) + float(duration)
        return 1 + int(real_end_time * float(fps))

    # -----------------------------------------------------------------------
    # Transformations
    # -----------------------------------------------------------------------

    @staticmethod
    def trim(video_in: str, start_frame: int, end_frame: int,
             video_out: str, crf: int = None) -> None:
        """Trim a video between two frame indices and re-encode to MKV/H265.

        The output covers frames in the range [start_frame, end_frame[.
        The PTS-STARTPTS filter resets the timestamp origin to zero.

        The ':' separator used in ffmpeg filter syntax requires that the
        output path does not contain colons.

        :param video_in: (str) Path to the input video file.
        :param start_frame: (int) Index of the first frame to include (0-based).
        :param end_frame: (int) Index of the first frame to exclude.
        :param video_out: (str) Path for the output MKV file.
        :param crf: (int|None) CRF encoding quality. Uses cfg.output.crf if None.
        :raises: TypeError: Any string argument is not a non-empty string.
        :raises: TypeError: start_frame or end_frame is not an integer.
        :raises: ValueError: start_frame is negative or end_frame <= start_frame.
        :raises: FileNotFoundError: video_in does not exist.

        """
        if isinstance(video_in, str) is False or len(video_in.strip()) == 0:
            raise TypeError("video_in must be a non-empty string.")
        if isinstance(video_out, str) is False or len(video_out.strip()) == 0:
            raise TypeError("video_out must be a non-empty string.")
        if isinstance(start_frame, int) is False:
            raise TypeError("start_frame must be an integer.")
        if isinstance(end_frame, int) is False:
            raise TypeError("end_frame must be an integer.")
        if start_frame < 0:
            raise ValueError("start_frame must be zero or positive.")
        if end_frame <= start_frame:
            raise ValueError("end_frame must be strictly greater than start_frame.")
        check_file(video_in)

        effective_crf = crf if crf is not None else cfg.output.crf

        command = (
            f"ffmpeg -i '{video_in}' "
            f"-f matroska -vcodec libx265 -crf {effective_crf:d} "
            f"-pix_fmt yuv420p "
            f"-vf trim=start_frame={start_frame:d}:end_frame={end_frame:d},setpts=PTS-STARTPTS "
            f"-an '{video_out}' "
            f"-nostdin -y"
        )
        run_command(command)

    # -----------------------------------------------------------------------

    @staticmethod
    def crop(video_in: str, x: int, y: int, w: int, h: int, video_out: str) -> None:
        """Crop a video to the given region.

        :param video_in: (str) Path to the input video file.
        :param x: (int) Left edge of the crop region (pixels).
        :param y: (int) Top edge of the crop region (pixels).
        :param w: (int) Width of the crop region (pixels).
        :param h: (int) Height of the crop region (pixels).
        :param video_out: (str) Path for the output video file.
        :raises: TypeError: Any string argument is not a non-empty string.
        :raises: TypeError: x, y, w or h is not an integer.
        :raises: ValueError: x or y is negative, or w or h is not strictly positive.
        :raises: FileNotFoundError: video_in does not exist.

        """
        if isinstance(video_in, str) is False or len(video_in.strip()) == 0:
            raise TypeError("video_in must be a non-empty string.")
        if isinstance(video_out, str) is False or len(video_out.strip()) == 0:
            raise TypeError("video_out must be a non-empty string.")
        for name, val in (("x", x), ("y", y), ("w", w), ("h", h)):
            if isinstance(val, int) is False:
                raise TypeError(f"{name} must be an integer.")
        if x < 0:
            raise ValueError("x must be zero or positive.")
        if y < 0:
            raise ValueError("y must be zero or positive.")
        if w <= 0:
            raise ValueError("w must be strictly positive.")
        if h <= 0:
            raise ValueError("h must be strictly positive.")
        check_file(video_in)

        command = (
            f"ffmpeg -i '{video_in}' "
            f"-filter:v 'crop=w={w:d}:h={h:d}:x={x:d}:y={y:d}' "
            f"'{video_out}' "
            f"-nostdin -y"
        )
        run_command(command)

    # -----------------------------------------------------------------------

    @staticmethod
    def add_copyright(video_in: str, copyright_text: str,
                      video_out: str, crf: int = None) -> None:
        """Overlay a copyright text on the top-left area of the video.

        The text is rendered in white Arial 18pt at position (40, 12).
        The ':' character in the copyright string must be escaped as '\\:'
        for the ffmpeg drawtext filter.

        :param video_in: (str) Path to the input video file.
        :param copyright_text: (str) Copyright string to overlay.
        :param video_out: (str) Path for the output MKV file.
        :param crf: (int|None) CRF encoding quality. Uses cfg.output.crf if None.
        :raises: TypeError: Any string argument is not a non-empty string.
        :raises: FileNotFoundError: video_in does not exist.

        """
        if isinstance(video_in, str) is False or len(video_in.strip()) == 0:
            raise TypeError("video_in must be a non-empty string.")
        if isinstance(copyright_text, str) is False or len(copyright_text.strip()) == 0:
            raise TypeError("copyright_text must be a non-empty string.")
        if isinstance(video_out, str) is False or len(video_out.strip()) == 0:
            raise TypeError("video_out must be a non-empty string.")
        check_file(video_in)

        effective_crf = crf if crf is not None else cfg.output.crf

        command = (
            f"ffmpeg -i '{video_in}' "
            f"-f matroska "
            f"-vcodec libx265 "
            f"-crf {effective_crf:d} "
            f"-pix_fmt yuv420p "
            f"-filter_complex \"[0:v] drawtext="
            f"fontfile='arial.ttf':fontsize=18:x=40:y=12:"
            f"text='{copyright_text}':fontcolor=white\" "
            f"-an '{video_out}' "
            f"-nostdin -y"
        )
        run_command(command)

    # -----------------------------------------------------------------------

    @staticmethod
    def rotate(video_in: str, video_out: str, transpose: int = 2) -> None:
        """Rotate a video using the ffmpeg transpose filter.

        Transpose values:
            0 = 90° counter-clockwise and vertical flip
            1 = 90° clockwise
            2 = 90° counter-clockwise
            3 = 90° clockwise and vertical flip

        :param video_in: (str) Path to the input video file.
        :param video_out: (str) Path for the output video file.
        :param transpose: (int) Transpose filter value (0, 1, 2 or 3).
                          Defaults to 2 (90° counter-clockwise, portrait mode).
        :raises: TypeError: video_in or video_out is not a non-empty string.
        :raises: TypeError: transpose is not an integer.
        :raises: ValueError: transpose is not in [0, 3].
        :raises: FileNotFoundError: video_in does not exist.

        """
        if isinstance(video_in, str) is False or len(video_in.strip()) == 0:
            raise TypeError("video_in must be a non-empty string.")
        if isinstance(video_out, str) is False or len(video_out.strip()) == 0:
            raise TypeError("video_out must be a non-empty string.")
        if isinstance(transpose, int) is False:
            raise TypeError("transpose must be an integer.")
        if transpose < 0 or transpose > 3:
            raise ValueError("transpose must be in [0, 3].")
        check_file(video_in)

        command = (
            f"ffmpeg -i '{video_in}' "
            f"-v 0 "
            f"-filter:v 'transpose={transpose:d}' "
            f"-qscale 0 "
            f"'{video_out}' "
            f"-nostdin -y"
        )
        run_command(command)

    # -----------------------------------------------------------------------
    # Merge audio and video
    # -----------------------------------------------------------------------

    @staticmethod
    def merge_av(video_in: str, audio_in: str, av_out: str) -> None:
        """Merge a video file and an audio file into a single MP4 container.

        The video and audio streams are copied without re-encoding.
        The output duration is determined by the shortest stream.

        :param video_in: (str) Path to the input video file (no audio track).
        :param audio_in: (str) Path to the input audio file.
        :param av_out: (str) Path for the output MP4 file.
        :raises: TypeError: Any argument is not a non-empty string.
        :raises: FileNotFoundError: video_in or audio_in does not exist.

        """
        if isinstance(video_in, str) is False or len(video_in.strip()) == 0:
            raise TypeError("video_in must be a non-empty string.")
        if isinstance(audio_in, str) is False or len(audio_in.strip()) == 0:
            raise TypeError("audio_in must be a non-empty string.")
        if isinstance(av_out, str) is False or len(av_out.strip()) == 0:
            raise TypeError("av_out must be a non-empty string.")
        check_file(video_in)
        check_file(audio_in)

        command = (
            f"ffmpeg "
            f"-i '{video_in}' "
            f"-i '{audio_in}' "
            f"-c:v copy -c:a copy "
            f"-shortest "
            f"'{av_out}' "
            f"-nostdin -y"
        )
        run_command(command)

    # -----------------------------------------------------------------------
    # WebM conversion
    # -----------------------------------------------------------------------

    @staticmethod
    def to_webm(video_in: str, webm_out: str, audio_in: str = None, crf: int = 16) -> None:
        """Convert a video file to WebM format using libvpx-vp9 (two-pass).

        Two-pass encoding is used to achieve better quality at a given CRF.
        Pass 1 analyses the video and writes statistics to /dev/null.
        Pass 2 produces the final WebM file.

        If audio_in is provided, its audio track is encoded with libvorbis
        and muxed into the WebM container. Otherwise the output is video-only.

        :example:
        >>> VideoOps.to_webm("out.mkv", "out.webm")
        >>> VideoOps.to_webm("out.mkv", "out.webm", audio_in="out.wav")

        :param video_in: (str) Path to the input video file.
        :param webm_out: (str) Path for the output WebM file.
        :param audio_in: (str|None) Path to an optional audio file to mux.
                         If None, no audio track is included.
        :param crf: (int) CRF quality value for libvpx-vp9 in [0, 63].
                    Lower is better. Defaults to 16.
        :raises: TypeError: video_in or webm_out is not a non-empty string.
        :raises: TypeError: audio_in is not a string or None.
        :raises: TypeError: crf is not an integer.
        :raises: ValueError: crf is not in range [0, 63].
        :raises: FileNotFoundError: video_in or audio_in does not exist.

        """
        if isinstance(video_in, str) is False or len(video_in.strip()) == 0:
            raise TypeError("video_in must be a non-empty string.")
        if isinstance(webm_out, str) is False or len(webm_out.strip()) == 0:
            raise TypeError("webm_out must be a non-empty string.")
        if audio_in is not None:
            if isinstance(audio_in, str) is False or len(audio_in.strip()) == 0:
                raise TypeError("audio_in must be a non-empty string or None.")
        if isinstance(crf, int) is False:
            raise TypeError("crf must be an integer.")
        if crf < 0 or crf > 63:
            raise ValueError("crf must be in range [0, 63].")
        check_file(video_in)
        if audio_in is not None:
            check_file(audio_in)

        if audio_in is not None:
            pass1 = (
                f"ffmpeg -i '{video_in}' -i '{audio_in}' "
                f"-b:v 0 -crf {crf:d} -pass 1 "
                f"-an -f webm -y /dev/null"
            )
            pass2 = (
                f"ffmpeg -i '{video_in}' -i '{audio_in}' "
                f"-b:v 0 -crf {crf:d} -pass 2 "
                f"-c:v libvpx-vp9 -c:a libvorbis -q:a 5 "
                f"-map 0:v:0 -map 1:a:0 "
                f"'{webm_out}'"
            )
        else:
            pass1 = (
                f"ffmpeg -i '{video_in}' "
                f"-b:v 0 -crf {crf:d} -pass 1 "
                f"-an -f webm -y /dev/null"
            )
            pass2 = (
                f"ffmpeg -i '{video_in}' "
                f"-b:v 0 -crf {crf:d} -pass 2 "
                f"-c:v libvpx-vp9 "
                f"'{webm_out}'"
            )

        run_command(pass1)
        run_command(pass2)

