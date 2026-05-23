"""
:filename: models.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Core data models of AViSS.

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
from audioopy.aio import extensions as audio_extensions


# ---------------------------------------------------------------------------


class avMediaFile:
    """Represent a single media file (audio or video) with sync parameters.

    A avMediaFile stores the path to the original file and the time of the
    synchronization clap within that file. For video files, an optional
    crop region (x, y, w, h) can be specified in pixels; if any of the
    four values is None, no crop is applied.

    :example:
    >>> m = avMediaFile("/data/rec.wav", 3.843)
    >>> m.path
    '/data/rec.wav'
    >>> m.clap_time
    3.843
    >>> m.is_audio()
    True
    >>> m.has_crop()
    False

    """

    def __init__(self, path: str, clap_time: float):
        """Initialize a avMediaFile with a file path and a clap time.

        :param path: (str) Absolute or relative path to the media file.
        :param clap_time: (float) Time of the synchronization clap (seconds).
        :raises: TypeError: path is not a non-empty string.
        :raises: TypeError: clap_time is not a number.
        :raises: ValueError: clap_time is negative.

        """
        if isinstance(path, str) is False or len(path.strip()) == 0:
            raise TypeError("path must be a non-empty string.")
        if isinstance(clap_time, (int, float)) is False:
            raise TypeError("clap_time must be a number.")
        if float(clap_time) < 0.:
            raise ValueError("clap_time must be zero or positive.")

        self.__path      = path.strip()
        self.__clap_time = float(clap_time)

        # Optional crop region (pixels). All four must be set to apply crop.
        self.__crop_x = None
        self.__crop_y = None
        self.__crop_w = None
        self.__crop_h = None

    # -----------------------------------------------------------------------
    # path
    # -----------------------------------------------------------------------

    def get_path(self) -> str:
        """Return the path to the media file.

        :return: (str) File path.

        """
        return self.__path

    def set_path(self, value: str) -> None:
        """Set the path to the media file.

        :param value: (str) Absolute or relative path to the media file.
        :raises: TypeError: The given value is not a non-empty string.

        """
        if isinstance(value, str) is False or len(value.strip()) == 0:
            raise TypeError("path must be a non-empty string.")
        self.__path = value.strip()

    path = property(get_path, set_path)

    # -----------------------------------------------------------------------
    # clap_time
    # -----------------------------------------------------------------------

    def get_clap_time(self) -> float:
        """Return the time of the synchronization clap (seconds).

        :return: (float) Clap time in seconds.

        """
        return self.__clap_time

    def set_clap_time(self, value) -> None:
        """Set the time of the synchronization clap.

        :param value: (int|float) Clap time in seconds.
        :raises: TypeError: The given value is not a number.
        :raises: ValueError: The given value is negative.

        """
        if isinstance(value, (int, float)) is False:
            raise TypeError("clap_time must be a number.")
        if float(value) < 0.:
            raise ValueError("clap_time must be zero or positive.")
        self.__clap_time = float(value)

    clap_time = property(get_clap_time, set_clap_time)

    # -----------------------------------------------------------------------
    # crop
    # -----------------------------------------------------------------------

    def get_crop_x(self) -> int | None:
        """Return the left edge of the crop region in pixels, or None.

        :return: (int|None) Left edge in pixels, or None if not set.

        """
        return self.__crop_x

    def set_crop_x(self, value: int | None) -> None:
        """Set the left edge of the crop region in pixels.

        :param value: (int|None) Left edge in pixels, or None to unset.
        :raises: TypeError: The given value is not an integer or None.
        :raises: ValueError: The given value is negative.

        """
        if value is not None:
            if isinstance(value, int) is False:
                raise TypeError("crop_x must be an integer or None.")
            if value < 0:
                raise ValueError("crop_x must be zero or positive.")
        self.__crop_x = value

    crop_x = property(get_crop_x, set_crop_x)

    # -----------------------------------------------------------------------

    def get_crop_y(self) -> int | None:
        """Return the top edge of the crop region in pixels, or None.

        :return: (int|None) Top edge in pixels, or None if not set.

        """
        return self.__crop_y

    def set_crop_y(self, value: int | None) -> None:
        """Set the top edge of the crop region in pixels.

        :param value: (int|None) Top edge in pixels, or None to unset.
        :raises: TypeError: The given value is not an integer or None.
        :raises: ValueError: The given value is negative.

        """
        if value is not None:
            if isinstance(value, int) is False:
                raise TypeError("crop_y must be an integer or None.")
            if value < 0:
                raise ValueError("crop_y must be zero or positive.")
        self.__crop_y = value

    crop_y = property(get_crop_y, set_crop_y)

    # -----------------------------------------------------------------------

    def get_crop_w(self) -> int | None:
        """Return the width of the crop region in pixels, or None.

        :return: (int|None) Width in pixels, or None if not set.

        """
        return self.__crop_w

    def set_crop_w(self, value: int | None) -> None:
        """Set the width of the crop region in pixels.

        :param value: (int|None) Width in pixels, or None to unset.
        :raises: TypeError: The given value is not an integer or None.
        :raises: ValueError: The given value is not strictly positive.

        """
        if value is not None:
            if isinstance(value, int) is False:
                raise TypeError("crop_w must be an integer or None.")
            if value <= 0:
                raise ValueError("crop_w must be strictly positive.")
        self.__crop_w = value

    crop_w = property(get_crop_w, set_crop_w)

    # -----------------------------------------------------------------------

    def get_crop_h(self) -> int | None:
        """Return the height of the crop region in pixels, or None.

        :return: (int|None) Height in pixels, or None if not set.

        """
        return self.__crop_h

    def set_crop_h(self, value: int | None) -> None:
        """Set the height of the crop region in pixels.

        :param value: (int|None) Height in pixels, or None to unset.
        :raises: TypeError: The given value is not an integer or None.
        :raises: ValueError: The given value is not strictly positive.

        """
        if value is not None:
            if isinstance(value, int) is False:
                raise TypeError("crop_h must be an integer or None.")
            if value <= 0:
                raise ValueError("crop_h must be strictly positive.")
        self.__crop_h = value

    crop_h = property(get_crop_h, set_crop_h)

    # -----------------------------------------------------------------------
    # Convenience methods
    # -----------------------------------------------------------------------

    def is_audio(self) -> bool:
        """Return True if this file is an audio file.

        :return: (bool) True if the file extension is a known audio extension.

        """
        ext = os.path.splitext(self.__path)[-1].lower()
        return ext in audio_extensions

    # -----------------------------------------------------------------------

    def is_video(self) -> bool:
        """Return True if this file is a video file.

        :return: (bool) True if the file extension is not a known audio extension.

        """
        return self.is_audio() is False

    # -----------------------------------------------------------------------

    def has_crop(self) -> bool:
        """Return True if all four crop parameters are set.

        Crop is applied only when all four values (x, y, w, h) are defined.

        :return: (bool) True if crop_x, crop_y, crop_w and crop_h are all set.

        """
        return (
            self.__crop_x is not None
            and self.__crop_y is not None
            and self.__crop_w is not None
            and self.__crop_h is not None
        )

    # -----------------------------------------------------------------------

    def exists(self) -> bool:
        """Return True if the media file exists on disk.

        :return: (bool) True if the path points to an existing file.

        """
        return os.path.isfile(self.__path)

    # -----------------------------------------------------------------------

    def __repr__(self) -> str:
        crop = f" crop=({self.__crop_x},{self.__crop_y},{self.__crop_w},{self.__crop_h})" \
            if self.has_crop() is True else ""
        return f"avMediaFile({self.__path!r}, clap={self.__clap_time:.3f}s{crop})"

# ---------------------------------------------------------------------------


class avSession:
    """Represent one row of the input CSV file.

    A avSession groups:
        - one or more avMediaFile instances for audio,
        - one or more avMediaFile instances for video,
        - timing parameters (delay and duration),
        - output filename metadata (values used to build the output name),
        - free metadata (any other CSV column, stored as a dict).

    At least one audio and one video must be provided.

    :example:
    >>> audio = avMediaFile("/data/rec.wav", 3.843)
    >>> video = avMediaFile("/data/rec.mp4", 6.410)
    >>> s = avSession(audio, video, delay=0.2, duration=248.25)
    >>> s.output_name_meta
    {}
    >>> s.has_second_audio()
    False

    """

    def __init__(self, audio: avMediaFile, video: avMediaFile, delay: float, duration: float):
        """Initialize a avSession with its primary media files and timing.

        :param audio: (avMediaFile) Primary audio file.
        :param video: (avMediaFile) Primary video file.
        :param delay: (float) Offset applied after the clap (seconds).
        :param duration: (float) Expected output duration (seconds).
        :raises: TypeError: audio is not a avMediaFile instance.
        :raises: ValueError: audio is not an audio file.
        :raises: TypeError: video is not a avMediaFile instance.
        :raises: ValueError: video is not a video file.
        :raises: TypeError: delay is not a number.
        :raises: TypeError: duration is not a number.
        :raises: ValueError: duration is not strictly positive.

        """
        if isinstance(audio, avMediaFile) is False:
            raise TypeError("audio must be a avMediaFile instance.")
        if audio.is_audio() is False:
            raise ValueError(f"The given audio avMediaFile does not have an audio extension: {audio.path!r}.")
        if isinstance(video, avMediaFile) is False:
            raise TypeError("video must be a avMediaFile instance.")
        if video.is_video() is False:
            raise ValueError(f"The given video avMediaFile does not have a video extension: {video.path!r}.")
        if isinstance(delay, (int, float)) is False:
            raise TypeError("delay must be a number.")
        if isinstance(duration, (int, float)) is False:
            raise TypeError("duration must be a number.")
        if float(duration) <= 0.:
            raise ValueError("duration must be strictly positive.")

        self.__audios      = [audio]
        self.__videos      = [video]
        self.__video_names = [None]
        self.__delay       = float(delay)
        self.__duration    = float(duration)

        # Values from CSV columns used to build the output filename.
        # Keys are CSV column names; values are raw strings from the CSV.
        self.__output_name_meta = {}

        # Any other CSV column not used for sync or output naming.
        self.__metadata = {}

    # -----------------------------------------------------------------------
    # Media file lists
    # -----------------------------------------------------------------------

    def get_audios(self) -> list:
        """Return a copy of the list of audio avMediaFile objects.

        :return: (list) List of avMediaFile instances (audio).

        """
        return list(self.__audios)

    audios = property(get_audios, None)

    # -----------------------------------------------------------------------

    def get_videos(self) -> list:
        """Return a copy of the list of video avMediaFile objects.

        :return: (list) List of avMediaFile instances (video).

        """
        return list(self.__videos)

    videos = property(get_videos, None)

    # -----------------------------------------------------------------------

    def get_video_names(self) -> list:
        """Return a copy of the list of optional video output labels.

        Each element corresponds to the video at the same index.
        None means no label is set for that video.

        :return: (list) List of str|None values.

        """
        return list(self.__video_names)

    video_names = property(get_video_names, None)

    # -----------------------------------------------------------------------

    def add_audio(self, audio: avMediaFile) -> None:
        """Append an audio avMediaFile to the session.

        :param audio: (avMediaFile) Audio file to add.
        :raises: TypeError: audio is not a avMediaFile instance.
        :raises: ValueError: audio is not an audio file.

        """
        if isinstance(audio, avMediaFile) is False:
            raise TypeError("audio must be a avMediaFile instance.")
        if audio.is_audio() is False:
            raise ValueError(f"The given avMediaFile does not have an audio extension: {audio.path!r}.")
        self.__audios.append(audio)

    # -----------------------------------------------------------------------

    def add_video(self, video: avMediaFile, name: str | None = None) -> None:
        """Append a video avMediaFile to the session with an optional output label.

        :param video: (avMediaFile) Video file to add.
        :param name: (str|None) Optional label used as suffix in the output filename.
        :raises: TypeError: video is not a avMediaFile instance.
        :raises: ValueError: video is not a video file.
        :raises: TypeError: name is not a non-empty string or None.

        """
        if isinstance(video, avMediaFile) is False:
            raise TypeError("video must be a avMediaFile instance.")
        if video.is_video() is False:
            raise ValueError(f"The given avMediaFile does not have a video extension: {video.path!r}.")
        if name is not None:
            if isinstance(name, str) is False or len(name.strip()) == 0:
                raise TypeError("name must be a non-empty string or None.")
            name = name.strip()
        self.__videos.append(video)
        self.__video_names.append(name)

    # -----------------------------------------------------------------------

    def set_video_name(self, index: int, name: str | None) -> None:
        """Set the output label for the video at the given index.

        :param index: (int) Index of the video (0-based).
        :param name: (str|None) Label, or None to clear.
        :raises: IndexError: index is out of range.
        :raises: TypeError: name is not a non-empty string or None.

        """
        if index < 0 or index >= len(self.__videos):
            raise IndexError(f"Video index {index} is out of range.")
        if name is not None:
            if isinstance(name, str) is False or len(name.strip()) == 0:
                raise TypeError("name must be a non-empty string or None.")
            name = name.strip()
        self.__video_names[index] = name

    # -----------------------------------------------------------------------
    # Timing
    # -----------------------------------------------------------------------

    def get_delay(self) -> float:
        """Return the offset applied after the clap (seconds).

        :return: (float) Delay in seconds.

        """
        return self.__delay

    def set_delay(self, value) -> None:
        """Set the offset applied after the clap.

        :param value: (int|float) Delay in seconds.
        :raises: TypeError: The given value is not a number.

        """
        if isinstance(value, (int, float)) is False:
            raise TypeError("delay must be a number.")
        self.__delay = float(value)

    delay = property(get_delay, set_delay)

    # -----------------------------------------------------------------------

    def get_duration(self) -> float:
        """Return the expected output duration (seconds).

        :return: (float) Duration in seconds.

        """
        return self.__duration

    def set_duration(self, value) -> None:
        """Set the expected output duration.

        :param value: (int|float) Duration in seconds.
        :raises: TypeError: The given value is not a number.
        :raises: ValueError: The given value is not strictly positive.

        """
        if isinstance(value, (int, float)) is False:
            raise TypeError("duration must be a number.")
        if float(value) <= 0.:
            raise ValueError("duration must be strictly positive.")
        self.__duration = float(value)

    duration = property(get_duration, set_duration)

    # -----------------------------------------------------------------------
    # Output filename metadata
    # -----------------------------------------------------------------------

    def get_output_name_meta(self) -> dict:
        """Return the dict of values used to build the output filename.

        Keys are CSV column names as declared in cfg.output.output_name_cols.
        Values are raw strings read from the CSV.

        :return: (dict) Output name metadata.

        """
        return self.__output_name_meta

    def set_output_name_meta(self, value: dict) -> None:
        """Set the dict of values used to build the output filename.

        :param value: (dict) Mapping of column name to raw CSV value.
        :raises: TypeError: The given value is not a dict.

        """
        if isinstance(value, dict) is False:
            raise TypeError("output_name_meta must be a dict.")
        self.__output_name_meta = value

    output_name_meta = property(get_output_name_meta, set_output_name_meta)

    # -----------------------------------------------------------------------
    # Free metadata
    # -----------------------------------------------------------------------

    def get_metadata(self) -> dict:
        """Return the dict of free metadata (all other CSV columns).

        :return: (dict) Free metadata.

        """
        return self.__metadata

    def set_metadata(self, value: dict) -> None:
        """Set the dict of free metadata.

        :param value: (dict) Mapping of column name to raw CSV value.
        :raises: TypeError: The given value is not a dict.

        """
        if isinstance(value, dict) is False:
            raise TypeError("metadata must be a dict.")
        self.__metadata = value

    metadata = property(get_metadata, set_metadata)

    # -----------------------------------------------------------------------
    # Convenience methods
    # -----------------------------------------------------------------------

    def has_second_audio(self) -> bool:
        """Return True if more than one audio file is set.

        :return: (bool) True if the session has at least two audio files.

        """
        return len(self.__audios) > 1

    # -----------------------------------------------------------------------

    def has_second_video(self) -> bool:
        """Return True if more than one video file is set.

        :return: (bool) True if the session has at least two video files.

        """
        return len(self.__videos) > 1

    # -----------------------------------------------------------------------

    def all_files_exist(self) -> bool:
        """Return True if all media files in this session exist on disk.

        :return: (bool) True if every defined avMediaFile exists on disk.

        """
        for media in self.__audios + self.__videos:
            if media.exists() is False:
                return False
        return True

    # -----------------------------------------------------------------------

    def __repr__(self) -> str:
        return (
            f"avSession({len(self.__audios)} audio, {len(self.__videos)} video, "
            f"delay={self.__delay:.3f}s, duration={self.__duration:.3f}s, "
            f"meta={self.__output_name_meta})"
        )

# ---------------------------------------------------------------------------


class avSyncResult:
    """Represent the output of a synchronization pipeline run.

    A avSyncResult is produced by the pipeline after processing one avSession.
    It stores the paths of the files produced (synchronized media and
    optional montage video) and a human-readable processing report.

    :example:
    >>> r = avSyncResult()
    >>> r.add_synced_file("/out/Laurent_S09_s2.wav")
    >>> r.add_synced_file("/out/Laurent_S09_s2.mp4")
    >>> len(r.synced_files)
    2
    >>> r.success
    False
    >>> r.success = True
    >>> r.success
    True

    """

    def __init__(self):
        """Initialize an empty avSyncResult.

        """
        self.__synced_files  = []
        self.__montage_file  = None
        self.__success       = False
        self.__report        = []

    # -----------------------------------------------------------------------
    # synced_files
    # -----------------------------------------------------------------------

    def get_synced_files(self) -> list:
        """Return the list of paths of synchronized output files.

        :return: (list) List of file path strings.

        """
        return self.__synced_files

    synced_files = property(get_synced_files, None)

    # -----------------------------------------------------------------------

    def add_synced_file(self, path: str) -> None:
        """Append a synchronized output file path to the result.

        :param path: (str) Path to a produced synchronized file.
        :raises: TypeError: The given value is not a non-empty string.

        """
        if isinstance(path, str) is False or len(path.strip()) == 0:
            raise TypeError("path must be a non-empty string.")
        self.__synced_files.append(path.strip())

    # -----------------------------------------------------------------------
    # montage_file
    # -----------------------------------------------------------------------

    def get_montage_file(self) -> str | None:
        """Return the path to the optional montage video, or None.

        :return: (str|None) Montage file path, or None if not produced.

        """
        return self.__montage_file

    def set_montage_file(self, value: str | None) -> None:
        """Set the path to the optional montage video.

        :param value: (str|None) Montage file path, or None.
        :raises: TypeError: The given value is not a non-empty string or None.

        """
        if value is not None:
            if isinstance(value, str) is False or len(value.strip()) == 0:
                raise TypeError("montage_file must be a non-empty string or None.")
        self.__montage_file = value

    montage_file = property(get_montage_file, set_montage_file)

    # -----------------------------------------------------------------------
    # success
    # -----------------------------------------------------------------------

    def get_success(self) -> bool:
        """Return True if the pipeline completed without error.

        :return: (bool) True if the synchronization succeeded.

        """
        return self.__success

    def set_success(self, value: bool) -> None:
        """Set the success flag of this result.

        :param value: (bool) True if the pipeline completed without error.
        :raises: TypeError: The given value is not a boolean.

        """
        if isinstance(value, bool) is False:
            raise TypeError("success must be a boolean.")
        self.__success = value

    success = property(get_success, set_success)

    # -----------------------------------------------------------------------
    # report
    # -----------------------------------------------------------------------

    def get_report(self) -> list:
        """Return the processing report as a list of message strings.

        :return: (list) List of report message strings.

        """
        return self.__report

    report = property(get_report, None)

    # -----------------------------------------------------------------------

    def add_message(self, message: str) -> None:
        """Append a message to the processing report.

        :param message: (str) Message to append.
        :raises: TypeError: The given value is not a string.

        """
        if isinstance(message, str) is False:
            raise TypeError("message must be a string.")
        self.__report.append(message)

    # -----------------------------------------------------------------------

    def __repr__(self) -> str:
        status = "OK" if self.__success is True else "FAILED"
        n = len(self.__synced_files)
        montage = f", montage={self.__montage_file!r}" if self.__montage_file is not None else ""
        return f"avSyncResult({status}, {n} synced file(s){montage})"
