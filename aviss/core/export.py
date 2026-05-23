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

from aviss.models import avSyncResult
from aviss.core.video_ops import avVideoOps
from aviss.utils import check_file

# ---------------------------------------------------------------------------


class avExporter:
    """Apply optional post-pipeline export operations to a avSyncResult.

    An avExporter is created from a avSyncResult. Each export method adds new
    output files and appends messages to the result report.

    :example:
    >>> exporter = avExporter(result, stem="Laurent_S09_sent", work_dir="/out/Laurent_S09_sent")
    >>> exporter.to_sppas()
    >>> exporter.rotate(transpose=2)
    >>> exporter.montage()

    """

    # CRF used for the montage (distribution quality, lower than sync).
    MONTAGE_CRF = 18

    # Frame rate of the montage output (lower than capture fps).
    MONTAGE_FPS = 25

    # -----------------------------------------------------------------------

    def __init__(self, result: avSyncResult, stem: str, work_dir: str):
        """Initialize the avExporter with a avSyncResult and output paths.

        :param result: (avSyncResult) Result produced by avPipeline.run().
        :param stem: (str) Output filename stem (e.g. "Laurent_S09_sent").
        :param work_dir: (str) Working directory containing the synced files.
        :raises: TypeError: result is not a avSyncResult instance.
        :raises: TypeError: stem or work_dir is not a non-empty string.
        :raises: ValueError: result.success is False.

        """
        if isinstance(result, avSyncResult) is False:
            raise TypeError("result must be a avSyncResult instance.")
        if isinstance(stem, str) is False or len(stem.strip()) == 0:
            raise TypeError("stem must be a non-empty string.")
        if isinstance(work_dir, str) is False or len(work_dir.strip()) == 0:
            raise TypeError("work_dir must be a non-empty string.")
        if result.success is False:
            raise ValueError(
                "The given avSyncResult reports a failed pipeline run. "
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

    def __all_synced_audios(self) -> list:
        """Return all full-quality audio files for this stem, in session order.

        Full-quality files are named <stem>*-audio.wav (original sample rate
        and channel count, before the 16 kHz mono conversion for SPPAS).

        :return: (list) Sorted list of paths to -audio.wav files.

        """
        return sorted([
            f for f in self.__result.synced_files
            if os.path.basename(f).startswith(self.__stem) and f.endswith("-audio.wav")
        ])

    # -----------------------------------------------------------------------

    def __all_synced_videos(self) -> list:
        """Return all synchronized MKV files for this stem, in session order.

        :return: (list) Sorted list of paths to .mkv files.

        """
        return sorted([
            f for f in self.__result.synced_files
            if os.path.basename(f).startswith(self.__stem) and f.endswith(".mkv")
        ])

    # -----------------------------------------------------------------------

    def __primary_audio(self) -> str:
        """Return the path of the primary full-quality audio file.

        Prefers the -audio.wav file (original sample rate and channels).
        Falls back to .wav if no -audio.wav is found.

        :return: (str) Path to the primary WAV file.
        :raises: FileNotFoundError: No matching WAV file is found in the result.

        """
        candidates = self.__all_synced_audios()
        if len(candidates) == 0:
            candidates = [
                f for f in self.__result.synced_files
                if os.path.basename(f).startswith(self.__stem) and f.endswith(".wav")
            ]
        if len(candidates) == 0:
            raise FileNotFoundError(
                f"No primary WAV file found in avSyncResult for stem {self.__stem!r}."
            )
        return candidates[0]

    # -----------------------------------------------------------------------

    def __primary_video(self) -> str:
        """Return the path of the primary synchronized video file.

        :return: (str) Path to the primary MKV file.
        :raises: FileNotFoundError: No matching MKV file is found in the result.

        """
        candidates = self.__all_synced_videos()
        if len(candidates) == 0:
            raise FileNotFoundError(
                f"No primary MKV file found in avSyncResult for stem {self.__stem!r}."
            )
        return candidates[0]

    # -----------------------------------------------------------------------

    # -----------------------------------------------------------------------
    # Validation helpers
    # -----------------------------------------------------------------------

    @staticmethod
    def __check_transpose_value(index: int, value) -> None:
        """Raise if a single transpose value is invalid.

        :param index: (int) Position in the transpose_list (for error messages).
        :param value: (int|None) Transpose value to validate.
        :raises: TypeError: value is not an integer or None.
        :raises: ValueError: value is not in [0, 3].

        """
        if value is None:
            return
        if isinstance(value, int) is False:
            raise TypeError(f"transpose_list[{index}] must be an integer or None.")
        if value < 0 or value > 3:
            raise ValueError(f"transpose_list[{index}] must be in [0, 3].")

    # -----------------------------------------------------------------------

    @staticmethod
    def __check_montage_params(fps, crf) -> None:
        """Raise if fps or crf arguments are invalid.

        :param fps: (int|None) Frame rate to validate.
        :param crf: (int|None) CRF value to validate.
        :raises: TypeError: fps or crf is not an integer or None.
        :raises: ValueError: fps or crf is out of valid range.

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
            avExporter.__check_transpose_value(i, value)

        self.__result.add_message(f"Export: rotate {transpose_list}.")

        videos = self.__all_synced_videos()
        for i, t in enumerate(transpose_list):
            if t is None:
                continue
            if i >= len(videos):
                continue
            video_path = videos[i]
            if os.path.isfile(video_path) is False:
                continue
            tmp_path = video_path.replace(".mkv", "_tmp_rot.mkv")
            avVideoOps.rotate(video_path, tmp_path, t)
            os.remove(video_path)
            os.rename(tmp_path, video_path)
            self.__result.add_message(f"  Rotated: {video_path!r}")

    # -----------------------------------------------------------------------

    def montage(self, fps: int = None, crf: int = None) -> str:
        """Assemble synchronized video(s) and audio(s) into a compressed MP4.

        Video codec  : libx264, preset slow, profile main, yuv420p.
        Audio codec  : AAC.
        Frame rate   : MONTAGE_FPS (default 25) or the given fps value.
        CRF          : MONTAGE_CRF (default 18) or the given crf value.

        Behavior by media count:

        Videos:
            1 video  : encoded directly.
            2 videos : assembled side by side (hstack), scaled to the same
                       height as the primary video; black bars if needed.
            3+ videos: not supported — raises NotImplementedError.

        Audios:
            0 or 3+ audios: no audio track in the output. A warning is logged
                            when 3+ files are present (limitation, not an error).
            1 audio : mono, original sample rate.
            2 audios: stereo 48 kHz (audio1 = left channel, audio2 = right
                      channel), merged with amerge and resampled to 48000 Hz.

        :param fps: (int|None) Output frame rate. Uses MONTAGE_FPS if None.
        :param crf: (int|None) CRF quality value. Uses MONTAGE_CRF if None.
        :return: (str) Path to the produced MP4 file.
        :raises: TypeError: fps or crf is not an integer or None.
        :raises: ValueError: fps or crf is out of valid range.
        :raises: FileNotFoundError: No MKV file is found in the result.
        :raises: NotImplementedError: More than 2 synchronized videos.

        """
        avExporter.__check_montage_params(fps, crf)

        effective_fps = fps if fps is not None else avExporter.MONTAGE_FPS
        effective_crf = crf if crf is not None else avExporter.MONTAGE_CRF

        audios = self.__all_synced_audios()
        videos = self.__all_synced_videos()
        n_v    = len(videos)
        n_a    = len(audios)

        if n_v == 0:
            raise FileNotFoundError(
                f"No MKV file found in avSyncResult for stem {self.__stem!r}."
            )
        if n_v >= 3:
            raise NotImplementedError(
                f"Montage with {n_v} videos is not yet supported. Maximum: 2 videos."
            )
        for v in videos:
            check_file(v)

        if n_a > 2:
            self.__result.add_message(
                f"  Warning: montage supports at most 2 audio files. "
                f"Got {n_a} — no audio track in the montage output."
            )
            n_a = 0
        for a in audios[:n_a]:
            check_file(a)

        mp4_out = self.__path(self.__stem + "-av.mp4")
        self.__result.add_message(
            f"Export: montage ({n_v} video(s), {n_a} audio(s), "
            f"fps={effective_fps}, crf={effective_crf})."
        )

        command = self.__montage_command(
            videos, audios[:n_a], mp4_out, effective_fps, effective_crf
        )

        from aviss.utils import run_command
        run_command(command)
        check_file(mp4_out)

        self.__result.montage_file = mp4_out
        self.__result.add_message(f"  Montage: {mp4_out!r}")
        return mp4_out

    # -----------------------------------------------------------------------

    def __montage_command(self, videos: list, audios: list,
                          mp4_out: str, fps: int, crf: int) -> str:
        """Build the ffmpeg command for the montage.

        :param videos: (list) List of 1 or 2 MKV paths (already validated).
        :param audios: (list) List of 0, 1, or 2 WAV paths (already validated).
        :param mp4_out: (str) Output MP4 path.
        :param fps: (int) Output frame rate.
        :param crf: (int) CRF quality value.
        :return: (str) Full ffmpeg command string.

        """
        n_v = len(videos)
        n_a = len(audios)

        codec = (
            f"-f mp4 -vcodec libx264 -crf {crf:d} "
            f"-preset slow -profile:v main -pix_fmt yuv420p"
        )

        if n_v == 1:
            v = videos[0]
            if n_a == 0:
                return (
                    f"ffmpeg -i '{v}' "
                    f"-filter:v fps=fps={fps:d} "
                    f"{codec} -an "
                    f"'{mp4_out}' -hide_banner -nostdin -y"
                )
            if n_a == 1:
                return (
                    f"ffmpeg -i '{v}' -i '{audios[0]}' "
                    f"-filter:v fps=fps={fps:d} "
                    f"{codec} -c:a aac -strict -2 "
                    f"'{mp4_out}' -hide_banner -nostdin -y"
                )
            # n_a == 2 : stereo 48 kHz
            fc = (
                f"[0:v]fps=fps={fps:d}[vout];"
                f"[1:a][2:a]amerge=inputs=2,aresample=48000[aout]"
            )
            return (
                f"ffmpeg -i '{v}' -i '{audios[0]}' -i '{audios[1]}' "
                f"-filter_complex \"{fc}\" "
                f"-map \"[vout]\" -map \"[aout]\" "
                f"{codec} -c:a aac -ac 2 -strict -2 "
                f"'{mp4_out}' -hide_banner -nostdin -y"
            )

        # n_v == 2
        h      = avVideoOps.get_video_info(videos[0])["height"]
        v0_f   = f"[0:v]fps=fps={fps:d},scale=-2:{h}[v0]"
        v1_f   = f"[1:v]fps=fps={fps:d},scale=-2:{h}[v1]"
        hstack = "[v0][v1]hstack=inputs=2[vout]"
        iv     = f"-i '{videos[0]}' -i '{videos[1]}' "

        if n_a == 0:
            fc = f"{v0_f};{v1_f};{hstack}"
            return (
                f"ffmpeg {iv}"
                f"-filter_complex \"{fc}\" "
                f"-map \"[vout]\" "
                f"{codec} -an "
                f"'{mp4_out}' -hide_banner -nostdin -y"
            )
        if n_a == 1:
            fc = f"{v0_f};{v1_f};{hstack}"
            return (
                f"ffmpeg {iv}-i '{audios[0]}' "
                f"-filter_complex \"{fc}\" "
                f"-map \"[vout]\" -map 2:a "
                f"{codec} -c:a aac -strict -2 "
                f"'{mp4_out}' -hide_banner -nostdin -y"
            )
        # n_a == 2 : stereo 48 kHz
        fc = (
            f"{v0_f};{v1_f};{hstack};"
            f"[2:a][3:a]amerge=inputs=2,aresample=48000[aout]"
        )
        return (
            f"ffmpeg {iv}-i '{audios[0]}' -i '{audios[1]}' "
            f"-filter_complex \"{fc}\" "
            f"-map \"[vout]\" -map \"[aout]\" "
            f"{codec} -c:a aac -ac 2 -strict -2 "
            f"'{mp4_out}' -hide_banner -nostdin -y"
        )

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

        avVideoOps.to_webm(video_in, webm_out, audio_in=audio_in, crf=crf)
        check_file(webm_out)

        if self.__result.montage_file is None:
            self.__result.montage_file = webm_out
        self.__result.add_message(f"  WebM: {webm_out!r}")
        return webm_out

