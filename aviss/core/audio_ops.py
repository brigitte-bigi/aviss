"""
:filename: audio_ops.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Audio operations for AViSS.

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
import shutil

import audioopy.aio

from aviss.utils import aviss_logger, check_file, run_command

# ---------------------------------------------------------------------------
# Audio metadata
# ---------------------------------------------------------------------------

class avAudioOps:
    """Static methods for audio file operations used by the AViSS pipeline.

    audioopy is used for reading audio metadata (duration, framerate, channels,
    sample width). sox is used for all audio transformations (trim, silence,
    concatenation, resampling, channel mixing).

    :example:
    >>> info = avAudioOps.get_audio_info("/data/rec.wav")
    >>> info["duration"]
    248.32
    >>> avAudioOps.audio_duration("/data/rec.wav")
    248.32

    """

    @staticmethod
    def get_audio_info(path: str) -> dict:
        """Return basic metadata of an audio file via audioopy.

        :example:
        >>> info = get_audio_info("/data/rec.wav")
        >>> info["duration"]
        248.32
        >>> info["framerate"]
        44100

        :param path: (str) Path to the audio file.
        :return: (dict) Keys: "framerate" (int), "nchannels" (int),
                 "sampwidth" (int, bytes), "duration" (float, seconds).
        :raises: TypeError: path is not a non-empty string.
        :raises: FileNotFoundError: The file does not exist.
        :raises: IOError: audioopy could not read the file.

        """
        if isinstance(path, str) is False or len(path.strip()) == 0:
            raise TypeError("path must be a non-empty string.")
        check_file(path)

        try:
            fa = audioopy.aio.open(path)
            info = {
                "framerate":  fa.get_framerate(),
                "nchannels":  fa.get_nchannels(),
                "sampwidth":  fa.get_sampwidth(),
                "duration":   fa.get_duration(),
            }
            fa.close()
        except Exception as e:
            raise IOError(f"audioopy could not read {path!r}: {e}.")

        return info

    # ---------------------------------------------------------------------------


    @staticmethod
    def open_audio(path: str, work_dir: str) -> str:
        """Return a path to a readable WAV file, converting with sox if needed.

        If audioopy can open the file directly, the original path is returned.
        Otherwise a 16-bit WAV conversion is written to work_dir and that path
        is returned instead.

        :param path: (str) Path to the audio file.
        :param work_dir: (str) Directory where the converted file is written.
        :return: (str) Path to a WAV file readable by audioopy.
        :raises: TypeError: path or work_dir is not a non-empty string.
        :raises: FileNotFoundError: path does not exist.
        :raises: IOError: Conversion with sox failed.

        """
        if isinstance(path, str) is False or len(path.strip()) == 0:
            raise TypeError("path must be a non-empty string.")
        if isinstance(work_dir, str) is False or len(work_dir.strip()) == 0:
            raise TypeError("work_dir must be a non-empty string.")
        check_file(path)

        try:
            fa = audioopy.aio.open(path)
            fa.close()
            return path
        except Exception:
            pass

        converted = os.path.join(work_dir, "audio_converted.wav")
        if os.path.exists(converted) is True:
            raise IOError(
                f"Conversion target already exists: {converted!r}. "
                f"Remove it before retrying."
            )
        run_command(f"sox '{path}' -b 16 '{converted}'")
        check_file(converted)
        return converted

    # ---------------------------------------------------------------------------
    # Extraction
    # ---------------------------------------------------------------------------


    @staticmethod
    def extract_audio_from_video(video_path: str, audio_out: str) -> None:
        """Extract the audio track of a video and re-encode it as 16-bit PCM WAV.

        :param video_path: (str) Path to the input video file.
        :param audio_out: (str) Path for the output WAV file.
        :raises: TypeError: video_path or audio_out is not a non-empty string.
        :raises: FileNotFoundError: video_path does not exist.

        """
        if isinstance(video_path, str) is False or len(video_path.strip()) == 0:
            raise TypeError("video_path must be a non-empty string.")
        if isinstance(audio_out, str) is False or len(audio_out.strip()) == 0:
            raise TypeError("audio_out must be a non-empty string.")
        check_file(video_path)

        command = (
            f"ffmpeg -i '{video_path}' "
            f"-vn -acodec pcm_s16le "
            f"'{audio_out}' "
            f"-nostdin -y"
        )
        run_command(command)

    # ---------------------------------------------------------------------------
    # Duration
    # ---------------------------------------------------------------------------


    @staticmethod
    def audio_duration(path: str) -> float:
        """Return the duration of an audio file in seconds.

        :param path: (str) Path to the audio file.
        :return: (float) Duration in seconds.
        :raises: TypeError: path is not a non-empty string.
        :raises: FileNotFoundError: The file does not exist.
        :raises: IOError: audioopy could not read the file.

        """
        info = avAudioOps.get_audio_info(path)
        return info["duration"]

    # ---------------------------------------------------------------------------
    # Transformations
    # ---------------------------------------------------------------------------


    @staticmethod
    def trim_audio(audio_in: str, trim_duration: float, audio_out: str, begin: bool = True) -> None:
        """Trim a fixed duration from the beginning or the end of an audio file.

        :param audio_in: (str) Path to the input audio file.
        :param trim_duration: (float) Duration to remove (seconds).
        :param audio_out: (str) Path for the output audio file.
        :param begin: (bool) True to trim from the beginning, False from the end.
        :raises: TypeError: audio_in or audio_out is not a non-empty string.
        :raises: TypeError: trim_duration is not a number.
        :raises: ValueError: trim_duration is not strictly positive.
        :raises: FileNotFoundError: audio_in does not exist.

        """
        if isinstance(audio_in, str) is False or len(audio_in.strip()) == 0:
            raise TypeError("audio_in must be a non-empty string.")
        if isinstance(audio_out, str) is False or len(audio_out.strip()) == 0:
            raise TypeError("audio_out must be a non-empty string.")
        if isinstance(trim_duration, (int, float)) is False:
            raise TypeError("trim_duration must be a number.")
        if float(trim_duration) <= 0.:
            raise ValueError("trim_duration must be strictly positive.")
        check_file(audio_in)

        cur_dur = avAudioOps.audio_duration(audio_in)
        remaining = cur_dur - float(trim_duration)

        if begin is True:
            trim_start = float(trim_duration)
        else:
            trim_start = 0.

        command = f"sox '{audio_in}' '{audio_out}' trim {trim_start:f} {remaining:f}"
        run_command(command)

    # ---------------------------------------------------------------------------


    @staticmethod
    def add_silence(audio_in: str, silence_duration: float, audio_out: str, begin: bool = True) -> None:
        """Prepend or append silence to an audio file.

        The silence is generated with the same framerate, channel count and
        sample width as the input file.

        :param audio_in: (str) Path to the input audio file.
        :param silence_duration: (float) Duration of silence to add (seconds).
        :param audio_out: (str) Path for the output audio file.
        :param begin: (bool) True to prepend silence, False to append it.
        :raises: TypeError: audio_in or audio_out is not a non-empty string.
        :raises: TypeError: silence_duration is not a number.
        :raises: ValueError: silence_duration is not strictly positive.
        :raises: FileNotFoundError: audio_in does not exist.

        """
        if isinstance(audio_in, str) is False or len(audio_in.strip()) == 0:
            raise TypeError("audio_in must be a non-empty string.")
        if isinstance(audio_out, str) is False or len(audio_out.strip()) == 0:
            raise TypeError("audio_out must be a non-empty string.")
        if isinstance(silence_duration, (int, float)) is False:
            raise TypeError("silence_duration must be a number.")
        if float(silence_duration) <= 0.:
            raise ValueError("silence_duration must be strictly positive.")
        check_file(audio_in)

        info = avAudioOps.get_audio_info(audio_in)
        silence_tmp = os.path.join(os.path.dirname(audio_out), "_silence_tmp.wav")

        # Generate a silent WAV matching the input format.
        command = (
            f"sox -n "
            f"-r {info['framerate']:d} "
            f"-c {info['nchannels']:d} "
            f"-b {info['sampwidth'] * 8:d} "
            f"'{silence_tmp}' "
            f"trim 0.0 {float(silence_duration):f}"
        )
        run_command(command)

        # Concatenate silence and audio (or the reverse).
        if begin is True:
            command = f"sox '{silence_tmp}' '{audio_in}' '{audio_out}'"
        else:
            command = f"sox '{audio_in}' '{silence_tmp}' '{audio_out}'"
        run_command(command)

        if os.path.isfile(silence_tmp) is True:
            os.remove(silence_tmp)

    # ---------------------------------------------------------------------------


    @staticmethod
    def adjust_audio_at_clap(audio_in: str, audio_clap: float,
                              reference_clap: float, audio_out: str) -> None:
        """Align an audio file so that its clap matches a reference clap time.

        The reference clap is typically the video clap time (plus delay).
        Three cases are handled:
            - clap times are equal: the file is copied unchanged.
            - audio clap is later than reference: the beginning is trimmed.
            - audio clap is earlier than reference: silence is prepended.

        :param audio_in: (str) Path to the input audio file.
        :param audio_clap: (float) Time of the clap in the audio file (seconds).
        :param reference_clap: (float) Target clap time to align to (seconds).
        :param audio_out: (str) Path for the output audio file.
        :raises: TypeError: audio_in or audio_out is not a non-empty string.
        :raises: TypeError: audio_clap or reference_clap is not a number.
        :raises: FileNotFoundError: audio_in does not exist.

        """
        if isinstance(audio_in, str) is False or len(audio_in.strip()) == 0:
            raise TypeError("audio_in must be a non-empty string.")
        if isinstance(audio_out, str) is False or len(audio_out.strip()) == 0:
            raise TypeError("audio_out must be a non-empty string.")
        if isinstance(audio_clap, (int, float)) is False:
            raise TypeError("audio_clap must be a number.")
        if isinstance(reference_clap, (int, float)) is False:
            raise TypeError("reference_clap must be a number.")
        check_file(audio_in)

        delta = float(reference_clap) - float(audio_clap)

        if delta == 0.:
            aviss_logger.write("Already matching. Nothing to do.")
            shutil.copy(audio_in, audio_out)

        elif delta < 0.:
            aviss_logger.write(f"Trim the beginning of the audio of {-delta:f} seconds")
            avAudioOps.trim_audio(audio_in, -delta, audio_out, begin=True)

        else:
            aviss_logger.write(f"Add {delta:f} seconds of silence at the beginning of the audio")
            avAudioOps.add_silence(audio_in, delta, audio_out, begin=True)

    # ---------------------------------------------------------------------------


    @staticmethod
    def adjust_audio_duration(audio_in: str, target_duration: float, audio_out: str) -> None:
        """Pad or trim an audio file to match a target duration.

        Three cases are handled:
            - durations are equal: the file is copied unchanged.
            - audio is shorter than target: silence is appended.
            - audio is longer than target: the end is trimmed.

        :param audio_in: (str) Path to the input audio file.
        :param target_duration: (float) Expected output duration (seconds).
        :param audio_out: (str) Path for the output audio file.
        :raises: TypeError: audio_in or audio_out is not a non-empty string.
        :raises: TypeError: target_duration is not a number.
        :raises: ValueError: target_duration is not strictly positive.
        :raises: FileNotFoundError: audio_in does not exist.

        """
        if isinstance(audio_in, str) is False or len(audio_in.strip()) == 0:
            raise TypeError("audio_in must be a non-empty string.")
        if isinstance(audio_out, str) is False or len(audio_out.strip()) == 0:
            raise TypeError("audio_out must be a non-empty string.")
        if isinstance(target_duration, (int, float)) is False:
            raise TypeError("target_duration must be a number.")
        if float(target_duration) <= 0.:
            raise ValueError("target_duration must be strictly positive.")
        check_file(audio_in)

        cur_dur = avAudioOps.audio_duration(audio_in)
        aviss_logger.write(f"Duration of the audio is {cur_dur:f} seconds")
        delta = float(target_duration) - cur_dur

        if delta == 0.:
            aviss_logger.write("Already matching. Nothing to do.")
            shutil.copy(audio_in, audio_out)

        elif delta > 0.:
            aviss_logger.write(f"Add {delta:f} seconds of silence at the end of the audio")
            avAudioOps.add_silence(audio_in, delta, audio_out, begin=False)

        else:
            aviss_logger.write(f"Trim the end of the audio of {-delta:f} seconds")
            avAudioOps.trim_audio(audio_in, -delta, audio_out, begin=False)

    # ---------------------------------------------------------------------------
    # SPPAS preparation
    # ---------------------------------------------------------------------------


    @staticmethod
    def to_mono(audio_in: str, audio_out: str) -> None:
        """Mix all channels down to mono, keeping the original sample rate.

        If the input is already mono, the file is copied unchanged.

        :param audio_in: (str) Path to the input audio file.
        :param audio_out: (str) Path for the output mono WAV file.
        :raises: TypeError: audio_in or audio_out is not a non-empty string.
        :raises: FileNotFoundError: audio_in does not exist.

        """
        if isinstance(audio_in, str) is False or len(audio_in.strip()) == 0:
            raise TypeError("audio_in must be a non-empty string.")
        if isinstance(audio_out, str) is False or len(audio_out.strip()) == 0:
            raise TypeError("audio_out must be a non-empty string.")
        check_file(audio_in)

        info = avAudioOps.get_audio_info(audio_in)
        if info["nchannels"] == 1:
            shutil.copy(audio_in, audio_out)
            return

        command = f"sox '{audio_in}' '{audio_out}' channels 1"
        run_command(command)

    # ---------------------------------------------------------------------------

    @staticmethod
    def to_mono_16k(audio_in: str, audio_out: str) -> None:
        """Convert an audio file to mono at 16000 Hz.

        :param audio_in: (str) Path to the input audio file.
        :param audio_out: (str) Path for the output mono 16000 Hz WAV file.
        :raises: TypeError: audio_in or audio_out is not a non-empty string.
        :raises: FileNotFoundError: audio_in does not exist.

        """
        if isinstance(audio_in, str) is False or len(audio_in.strip()) == 0:
            raise TypeError("audio_in must be a non-empty string.")
        if isinstance(audio_out, str) is False or len(audio_out.strip()) == 0:
            raise TypeError("audio_out must be a non-empty string.")
        check_file(audio_in)

        command = f"sox '{audio_in}' -r 16000 '{audio_out}' channels 1"
        run_command(command)

