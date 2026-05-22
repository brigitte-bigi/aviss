"""
:filename: export.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Export operations for AViSS synchronized outputs.

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

"""

import os

from aviss.models import SyncResult
from aviss.core.video_ops import VideoOps
from aviss.utils import check_file

# ---------------------------------------------------------------------------


class Exporter:
    """Apply optional post-pipeline export operations to a SyncResult.

    An Exporter is created from a SyncResult. Each export method adds new
    output files and appends messages to the result report.

    :example:
    >>> exporter = Exporter(result, stem="Laurent_S09_sent", work_dir="/out/Laurent_S09_sent")
    >>> exporter.to_sppas()
    >>> exporter.rotate(transpose=2)
    >>> exporter.montage()

    """

    # CRF used for the montage (distribution quality, lower than sync).
    MONTAGE_CRF = 18

    # Frame rate of the montage output (lower than capture fps).
    MONTAGE_FPS = 25

    # -----------------------------------------------------------------------

    def __init__(self, result: SyncResult, stem: str, work_dir: str):
        """Initialize the Exporter with a SyncResult and output paths.

        :param result: (SyncResult) Result produced by Pipeline.run().
        :param stem: (str) Output filename stem (e.g. "Laurent_S09_sent").
        :param work_dir: (str) Working directory containing the synced files.
        :raises: TypeError: result is not a SyncResult instance.
        :raises: TypeError: stem or work_dir is not a non-empty string.
        :raises: ValueError: result.success is False.

        """
        if isinstance(result, SyncResult) is False:
            raise TypeError("result must be a SyncResult instance.")
        if isinstance(stem, str) is False or len(stem.strip()) == 0:
            raise TypeError("stem must be a non-empty string.")
        if isinstance(work_dir, str) is False or len(work_dir.strip()) == 0:
            raise TypeError("work_dir must be a non-empty string.")
        if result.success is False:
            raise ValueError(
                "The given SyncResult reports a failed pipeline run. "
                "Export operations cannot be applied to a failed result."
            )

        self.__result   = result
        self.__stem     = stem.strip()
        self.__work_dir = work_dir.strip()

    # -----------------------------------------------------------------------
    # Helpers
    # -----------------------------------------------------------------------

    def __path(self, filename: str) -> str:
        """Return the full path for a file in the working directory.

        :param filename: (str) Filename (not path).
        :return: (str) Full path.

        """
        return os.path.join(self.__work_dir, filename)

    # -----------------------------------------------------------------------

    def __primary_audio(self) -> str:
        """Return the path of the primary full-quality audio file.

        Prefers the -audio.wav file (original sample rate and channels).
        Falls back to .wav if no -audio.wav is found.

        :return: (str) Path to the primary WAV file.
        :raises: FileNotFoundError: No matching WAV file is found in the result.

        """
        candidates = [
            f for f in self.__result.synced_files
            if os.path.basename(f).startswith(self.__stem) and f.endswith("-audio.wav")
        ]
        if len(candidates) == 0:
            candidates = [
                f for f in self.__result.synced_files
                if os.path.basename(f).startswith(self.__stem) and f.endswith(".wav")
            ]
        if len(candidates) == 0:
            raise FileNotFoundError(
                f"No primary WAV file found in SyncResult for stem {self.__stem!r}."
            )
        return candidates[0]

    # -----------------------------------------------------------------------

    def __primary_video(self) -> str:
        """Return the path of the primary synchronized video file.

        :return: (str) Path to the primary MKV file.
        :raises: FileNotFoundError: No matching MKV file is found in the result.

        """
        candidates = [
            f for f in self.__result.synced_files
            if os.path.basename(f).startswith(self.__stem) and f.endswith(".mkv")
        ]
        if len(candidates) == 0:
            raise FileNotFoundError(
                f"No primary MKV file found in SyncResult for stem {self.__stem!r}."
            )
        return candidates[0]

    # -----------------------------------------------------------------------

    # -----------------------------------------------------------------------
    # Export operations
    # -----------------------------------------------------------------------

    def rotate(self, transpose_list: list) -> None:
        """Rotate synchronized video files using per-video transpose values.

        Each element of transpose_list corresponds to one video in order
        (primary first, secondary second, etc.). Use None to skip a video.

        Transpose values:
            0 = 90° counter-clockwise + vertical flip
            1 = 90° clockwise
            2 = 90° counter-clockwise  (portrait mode)
            3 = 90° clockwise + vertical flip

        The rotated file replaces the input MKV in the working directory.

        :param transpose_list: (list) List of int|None values, one per video.
        :raises: TypeError: transpose_list is not a list, or a value is not int|None.
        :raises: ValueError: A value is not in [0, 3].

        """
        if isinstance(transpose_list, list) is False:
            raise TypeError("transpose_list must be a list.")
        for i, value in enumerate(transpose_list):
            if value is not None:
                if isinstance(value, int) is False:
                    raise TypeError(f"transpose_list[{i}] must be an integer or None.")
                if value < 0 or value > 3:
                    raise ValueError(f"transpose_list[{i}] must be in [0, 3].")

        self.__result.add_message(f"Export: rotate {transpose_list}.")

        videos = [
            f for f in self.__result.synced_files
            if os.path.basename(f).startswith(self.__stem) and f.endswith(".mkv")
        ]
        for i, t in enumerate(transpose_list):
            if t is None or i >= len(videos):
                continue
            video_path = videos[i]
            if os.path.isfile(video_path) is False:
                continue
            tmp_path = video_path.replace(".mkv", "_tmp_rot.mkv")
            VideoOps.rotate(video_path, tmp_path, t)
            os.remove(video_path)
            os.rename(tmp_path, video_path)
            self.__result.add_message(f"  Rotated: {video_path!r}")

    # -----------------------------------------------------------------------

    def montage(self, fps: int = None, crf: int = None) -> str:
        """Merge the primary video and audio into a compressed MP4 for distribution.

        The montage is encoded with libx264/AAC at a lower frame rate than
        the capture fps. It is intended for sharing and viewing, not for
        acoustic or phonetic analysis.

        Video codec  : libx264, preset slow, profile main, yuv420p.
        Audio codec  : AAC.
        Frame rate   : MONTAGE_FPS (default 25) or the given fps value.
        CRF          : MONTAGE_CRF (default 18) or the given crf value.

        :param fps: (int|None) Output frame rate. Uses MONTAGE_FPS if None.
        :param crf: (int|None) CRF quality value. Uses MONTAGE_CRF if None.
        :return: (str) Path to the produced MP4 file.
        :raises: TypeError: fps or crf is not an integer or None.
        :raises: ValueError: fps or crf is out of valid range.
        :raises: FileNotFoundError: Primary audio or video is not available.

        """
        if fps is not None:
            if isinstance(fps, int) is False:
                raise TypeError("fps must be an integer or None.")
            if fps <= 0:
                raise ValueError("fps must be strictly positive.")
        if crf is not None:
            if isinstance(crf, int) is False:
                raise TypeError("crf must be an integer or None.")
            if crf < 0 or crf > 51:
                raise ValueError("crf must be in range [0, 51].")

        effective_fps = fps if fps is not None else Exporter.MONTAGE_FPS
        effective_crf = crf if crf is not None else Exporter.MONTAGE_CRF

        self.__result.add_message(
            f"Export: montage (fps={effective_fps}, crf={effective_crf})."
        )

        audio_in  = self.__primary_audio()
        video_in  = self.__primary_video()
        mp4_out   = self.__path(self.__stem + "-av.mp4")

        check_file(audio_in)
        check_file(video_in)

        command = (
            f"ffmpeg "
            f"-i '{video_in}' "
            f"-i '{audio_in}' "
            f"-f mp4 "
            f"-vcodec libx264 "
            f"-crf {effective_crf:d} "
            f"-filter:v fps=fps={effective_fps:d} "
            f"-preset slow "
            f"-profile:v main "
            f"-pix_fmt yuv420p "
            f"-c:a aac -strict -2 "
            f"'{mp4_out}' -hide_banner "
            f"-nostdin -y"
        )

        from aviss.utils import run_command
        run_command(command)
        check_file(mp4_out)

        self.__result.montage_file = mp4_out
        self.__result.add_message(f"  Montage: {mp4_out!r}")
        return mp4_out

    # -----------------------------------------------------------------------

    def webm(self, crf: int = 16) -> str:
        """Convert the primary synchronized video to WebM using libvpx-vp9.

        The primary synchronized audio is muxed into the WebM container.
        Two-pass encoding is used for better quality at the given CRF.

        :param crf: (int) CRF quality value for libvpx-vp9 in [0, 63].
                    Lower is better. Defaults to 16.
        :return: (str) Path to the produced WebM file.
        :raises: TypeError: crf is not an integer.
        :raises: ValueError: crf is not in range [0, 63].
        :raises: FileNotFoundError: Primary audio or video is not available.

        """
        if isinstance(crf, int) is False:
            raise TypeError("crf must be an integer.")
        if crf < 0 or crf > 63:
            raise ValueError("crf must be in range [0, 63].")

        self.__result.add_message(f"Export: webm (crf={crf}).")

        audio_in = self.__primary_audio()
        video_in = self.__primary_video()
        webm_out = self.__path(self.__stem + "-av.webm")

        check_file(audio_in)
        check_file(video_in)

        VideoOps.to_webm(video_in, webm_out, audio_in=audio_in, crf=crf)
        check_file(webm_out)

        if self.__result.montage_file is None:
            self.__result.montage_file = webm_out
        self.__result.add_message(f"  WebM: {webm_out!r}")
        return webm_out

