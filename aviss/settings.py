"""
:filename: settings.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Central configuration of AViSS.

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
import importlib.util

# ---------------------------------------------------------------------------


class AViSSSyncSettings:
    """Mutable settings for CSV column names used in synchronization.

    Each attribute stores the name of a CSV column header. Changing an
    attribute makes AViSS read a differently named column in the CSV file.

    The crop attributes are optional: if the corresponding CSV cell is empty,
    no crop is applied to that video.

    :example:
    >>> s = AViSSSyncSettings()
    >>> s.col_audio_file
    'audio_file'
    >>> s.col_audio_file = 'my_audio'
    >>> s.col_audio_file
    'my_audio'

    """

    def __init__(self):
        """Initialize synchronization column names with default values.

        """
        self.__col_audio_file  = "audio_file"
        self.__col_audio_clap  = "audio_clap"
        self.__col_video_file  = "video_file"
        self.__col_video_clap  = "video_clap"
        self.__col_video_crop_x = "video_crop_x"
        self.__col_video_crop_y = "video_crop_y"
        self.__col_video_crop_w = "video_crop_w"
        self.__col_video_crop_h = "video_crop_h"
        self.__col_delay       = "delay"
        self.__col_duration    = "duration"

    # -----------------------------------------------------------------------
    # col_audio_file
    # -----------------------------------------------------------------------

    def get_col_audio_file(self) -> str:
        """Return the CSV column name for the audio file path.

        :return: (str) Column name.

        """
        return self.__col_audio_file

    def set_col_audio_file(self, value: str) -> None:
        """Set the CSV column name for the audio file path.

        :param value: (str) Column name.
        :raises: TypeError: The given value is not a non-empty string.

        """
        if isinstance(value, str) is False or len(value.strip()) == 0:
            raise TypeError("col_audio_file must be a non-empty string.")
        self.__col_audio_file = value.strip()

    col_audio_file = property(get_col_audio_file, set_col_audio_file)

    # -----------------------------------------------------------------------
    # col_audio_clap
    # -----------------------------------------------------------------------

    def get_col_audio_clap(self) -> str:
        """Return the CSV column name for the audio clap time.

        :return: (str) Column name.

        """
        return self.__col_audio_clap

    def set_col_audio_clap(self, value: str) -> None:
        """Set the CSV column name for the audio clap time.

        :param value: (str) Column name.
        :raises: TypeError: The given value is not a non-empty string.

        """
        if isinstance(value, str) is False or len(value.strip()) == 0:
            raise TypeError("col_audio_clap must be a non-empty string.")
        self.__col_audio_clap = value.strip()

    col_audio_clap = property(get_col_audio_clap, set_col_audio_clap)

    # -----------------------------------------------------------------------
    # col_video_file
    # -----------------------------------------------------------------------

    def get_col_video_file(self) -> str:
        """Return the CSV column name for the video file path.

        :return: (str) Column name.

        """
        return self.__col_video_file

    def set_col_video_file(self, value: str) -> None:
        """Set the CSV column name for the video file path.

        :param value: (str) Column name.
        :raises: TypeError: The given value is not a non-empty string.

        """
        if isinstance(value, str) is False or len(value.strip()) == 0:
            raise TypeError("col_video_file must be a non-empty string.")
        self.__col_video_file = value.strip()

    col_video_file = property(get_col_video_file, set_col_video_file)

    # -----------------------------------------------------------------------
    # col_video_clap
    # -----------------------------------------------------------------------

    def get_col_video_clap(self) -> str:
        """Return the CSV column name for the video clap time.

        :return: (str) Column name.

        """
        return self.__col_video_clap

    def set_col_video_clap(self, value: str) -> None:
        """Set the CSV column name for the video clap time.

        :param value: (str) Column name.
        :raises: TypeError: The given value is not a non-empty string.

        """
        if isinstance(value, str) is False or len(value.strip()) == 0:
            raise TypeError("col_video_clap must be a non-empty string.")
        self.__col_video_clap = value.strip()

    col_video_clap = property(get_col_video_clap, set_col_video_clap)

    # -----------------------------------------------------------------------
    # col_video_crop_x
    # -----------------------------------------------------------------------

    def get_col_video_crop_x(self) -> str:
        """Return the CSV column name for the video crop left edge.

        :return: (str) Column name.

        """
        return self.__col_video_crop_x

    def set_col_video_crop_x(self, value: str) -> None:
        """Set the CSV column name for the video crop left edge (pixels).

        :param value: (str) Column name.
        :raises: TypeError: The given value is not a non-empty string.

        """
        if isinstance(value, str) is False or len(value.strip()) == 0:
            raise TypeError("col_video_crop_x must be a non-empty string.")
        self.__col_video_crop_x = value.strip()

    col_video_crop_x = property(get_col_video_crop_x, set_col_video_crop_x)

    # -----------------------------------------------------------------------
    # col_video_crop_y
    # -----------------------------------------------------------------------

    def get_col_video_crop_y(self) -> str:
        """Return the CSV column name for the video crop top edge.

        :return: (str) Column name.

        """
        return self.__col_video_crop_y

    def set_col_video_crop_y(self, value: str) -> None:
        """Set the CSV column name for the video crop top edge (pixels).

        :param value: (str) Column name.
        :raises: TypeError: The given value is not a non-empty string.

        """
        if isinstance(value, str) is False or len(value.strip()) == 0:
            raise TypeError("col_video_crop_y must be a non-empty string.")
        self.__col_video_crop_y = value.strip()

    col_video_crop_y = property(get_col_video_crop_y, set_col_video_crop_y)

    # -----------------------------------------------------------------------
    # col_video_crop_w
    # -----------------------------------------------------------------------

    def get_col_video_crop_w(self) -> str:
        """Return the CSV column name for the video crop width.

        :return: (str) Column name.

        """
        return self.__col_video_crop_w

    def set_col_video_crop_w(self, value: str) -> None:
        """Set the CSV column name for the video crop width (pixels).

        :param value: (str) Column name.
        :raises: TypeError: The given value is not a non-empty string.

        """
        if isinstance(value, str) is False or len(value.strip()) == 0:
            raise TypeError("col_video_crop_w must be a non-empty string.")
        self.__col_video_crop_w = value.strip()

    col_video_crop_w = property(get_col_video_crop_w, set_col_video_crop_w)

    # -----------------------------------------------------------------------
    # col_video_crop_h
    # -----------------------------------------------------------------------

    def get_col_video_crop_h(self) -> str:
        """Return the CSV column name for the video crop height.

        :return: (str) Column name.

        """
        return self.__col_video_crop_h

    def set_col_video_crop_h(self, value: str) -> None:
        """Set the CSV column name for the video crop height (pixels).

        :param value: (str) Column name.
        :raises: TypeError: The given value is not a non-empty string.

        """
        if isinstance(value, str) is False or len(value.strip()) == 0:
            raise TypeError("col_video_crop_h must be a non-empty string.")
        self.__col_video_crop_h = value.strip()

    col_video_crop_h = property(get_col_video_crop_h, set_col_video_crop_h)

    # -----------------------------------------------------------------------
    # col_delay
    # -----------------------------------------------------------------------

    def get_col_delay(self) -> str:
        """Return the CSV column name for the delay applied after the clap.

        :return: (str) Column name.

        """
        return self.__col_delay

    def set_col_delay(self, value: str) -> None:
        """Set the CSV column name for the delay applied after the clap.

        :param value: (str) Column name.
        :raises: TypeError: The given value is not a non-empty string.

        """
        if isinstance(value, str) is False or len(value.strip()) == 0:
            raise TypeError("col_delay must be a non-empty string.")
        self.__col_delay = value.strip()

    col_delay = property(get_col_delay, set_col_delay)

    # -----------------------------------------------------------------------
    # col_duration
    # -----------------------------------------------------------------------

    def get_col_duration(self) -> str:
        """Return the CSV column name for the expected output duration.

        :return: (str) Column name.

        """
        return self.__col_duration

    def set_col_duration(self, value: str) -> None:
        """Set the CSV column name for the expected output duration.

        :param value: (str) Column name.
        :raises: TypeError: The given value is not a non-empty string.

        """
        if isinstance(value, str) is False or len(value.strip()) == 0:
            raise TypeError("col_duration must be a non-empty string.")
        self.__col_duration = value.strip()

    col_duration = property(get_col_duration, set_col_duration)

# ---------------------------------------------------------------------------


class AViSSOutputSettings:
    """Mutable settings for output filename construction and video encoding.

    output_name_cols controls which CSV columns are included in the output
    filename, in which order, with which prefix and numeric format.

    Each entry in output_name_cols is a tuple:
        (csv_column_name, prefix, fmt)

        csv_column_name : str       -- must match a header in the CSV file.
        prefix          : str       -- prepended to the value ("S", "T"...).
                                       Use "" for no prefix.
        fmt             : str|None  -- None  -> raw string (e.g. "sent").
                                       "02d" -> zero-padded int (e.g. "09").
                                       "d"   -> plain int (e.g. "9").

    A column whose CSV cell is empty is silently skipped.
    Tokens are joined with output_sep.

    :example:
    >>> s = AViSSOutputSettings()
    >>> s.output_sep
    '_'
    >>> s.crf
    18
    >>> s.output_name_cols[0]
    ('ID', '', None)

    """

    def __init__(self):
        """Initialize output settings with default values.

        """
        self.__output_sep = "_"
        self.__output_name_cols = [
            ("ID",         "",  None),
            ("Session",    "S", "02d"),
            ("Theme",      "T", "02d"),
            ("SerieNum",   "s", "02d"),
            ("SerieLabel", "",  None),
        ]
        self.__crf            = 18
        self.__video_fps      = 50.
        self.__copyright      = None
        self.__work_dir_suffix = ""

    # -----------------------------------------------------------------------
    # output_sep
    # -----------------------------------------------------------------------

    def get_output_sep(self) -> str:
        """Return the separator used between tokens in the output filename.

        :return: (str) Separator string.

        """
        return self.__output_sep

    def set_output_sep(self, value: str) -> None:
        """Set the separator used between tokens in the output filename.

        :param value: (str) Separator string.
        :raises: TypeError: The given value is not a string.

        """
        if isinstance(value, str) is False:
            raise TypeError("output_sep must be a string.")
        self.__output_sep = value

    output_sep = property(get_output_sep, set_output_sep)

    # -----------------------------------------------------------------------
    # output_name_cols
    # -----------------------------------------------------------------------

    def get_output_name_cols(self) -> list:
        """Return the list of column rules for the output filename.

        Each entry is a tuple (csv_column_name, prefix, fmt).

        :return: (list) List of (str, str, str|None) tuples.

        """
        return self.__output_name_cols

    def set_output_name_cols(self, value: list) -> None:
        """Set the list of column rules for the output filename.

        :param value: (list) List of (csv_column_name, prefix, fmt) tuples.
        :raises: TypeError: The given value is not a non-empty list of 3-tuples.

        """
        if isinstance(value, list) is False or len(value) == 0:
            raise TypeError("output_name_cols must be a non-empty list.")
        for entry in value:
            if isinstance(entry, tuple) is False or len(entry) != 3:
                raise TypeError("Each entry in output_name_cols must be a tuple of 3 elements.")
            col, prefix, fmt = entry
            if isinstance(col, str) is False or len(col.strip()) == 0:
                raise TypeError("The column name in each entry must be a non-empty string.")
            if isinstance(prefix, str) is False:
                raise TypeError("The prefix in each entry must be a string.")
            if fmt is not None and isinstance(fmt, str) is False:
                raise TypeError("The format in each entry must be a string or None.")
        self.__output_name_cols = value

    output_name_cols = property(get_output_name_cols, set_output_name_cols)

    # -----------------------------------------------------------------------
    # crf
    # -----------------------------------------------------------------------

    def get_crf(self) -> int:
        """Return the CRF value for video encoding quality.

        :return: (int) CRF value in range [0, 51].

        """
        return self.__crf

    def set_crf(self, value: int) -> None:
        """Set the CRF value for video encoding quality.

        A lower value means better quality and a larger file size.
        0 is lossless, 51 is the worst quality.

        :param value: (int) CRF value in range [0, 51].
        :raises: TypeError: The given value is not an integer.
        :raises: ValueError: The given value is not in range [0, 51].

        """
        if isinstance(value, int) is False:
            raise TypeError("crf must be an integer.")
        if value < 0 or value > 51:
            raise ValueError("crf must be in range [0, 51].")
        self.__crf = value

    crf = property(get_crf, set_crf)

    # -----------------------------------------------------------------------
    # video_fps
    # -----------------------------------------------------------------------

    def get_video_fps(self) -> float:
        """Return the native frame rate of the recording camera.

        :return: (float) Frame rate in frames per second.

        """
        return self.__video_fps

    def set_video_fps(self, value) -> None:
        """Set the native frame rate of the recording camera.

        :param value: (int|float) Frame rate in frames per second.
        :raises: TypeError: The given value is not a number.
        :raises: ValueError: The given value is not strictly positive.

        """
        if isinstance(value, (int, float)) is False:
            raise TypeError("video_fps must be a number.")
        if float(value) <= 0.:
            raise ValueError("video_fps must be strictly positive.")
        self.__video_fps = float(value)

    video_fps = property(get_video_fps, set_video_fps)

    # -----------------------------------------------------------------------
    # copyright
    # -----------------------------------------------------------------------

    def get_copyright(self) -> str | None:
        """Return the copyright string overlaid on the video, or None.

        :return: (str|None) Copyright string, or None if disabled.

        """
        return self.__copyright

    def set_copyright(self, value: str | None) -> None:
        """Set the copyright string overlaid on the video.

        Set to None to disable the copyright overlay.
        The ':' character must be escaped as '\\:' for the ffmpeg drawtext filter.

        :param value: (str|None) Copyright string, or None to disable.
        :raises: TypeError: The given value is neither a string nor None.

        """
        if value is not None and isinstance(value, str) is False:
            raise TypeError("copyright must be a string or None.")
        self.__copyright = value

    copyright = property(get_copyright, set_copyright)

    # -----------------------------------------------------------------------
    # work_dir_suffix
    # -----------------------------------------------------------------------

    def get_work_dir_suffix(self) -> str:
        """Return the optional suffix appended to the output directory name.

        :return: (str) Suffix string. An empty string means no suffix.

        """
        return self.__work_dir_suffix

    def set_work_dir_suffix(self, value: str) -> None:
        """Set the optional suffix appended to the output directory name.

        :param value: (str) Suffix string. Use "" for no suffix.
        :raises: TypeError: The given value is not a string.

        """
        if isinstance(value, str) is False:
            raise TypeError("work_dir_suffix must be a string.")
        self.__work_dir_suffix = value

    work_dir_suffix = property(get_work_dir_suffix, set_work_dir_suffix)

# ---------------------------------------------------------------------------


class AViSSSettings:
    """Mutable global settings of AViSS.

    This class groups synchronization column settings (AViSSSyncSettings)
    and output settings (AViSSOutputSettings) into a single entry point.

    User overrides are loaded explicitly by calling load_user_settings(directory)
    with the directory that contains the CSV file being processed. Each corpus
    directory may have its own settings_user.py.

    :example:
    >>> cfg.sync.col_audio_file
    'audio_file'
    >>> cfg.output.crf
    18
    >>> cfg.output.crf = 14
    >>> cfg.output.crf
    14

    """

    def __init__(self):
        """Initialize AViSS settings with default values.

        """
        self.__sync   = AViSSSyncSettings()
        self.__output = AViSSOutputSettings()

    # -----------------------------------------------------------------------

    def load_user_settings(self, directory: str) -> None:
        """Load settings_user.py from the given directory if it exists.

        The file may override any attribute of cfg.sync or cfg.output.
        Call this method once, passing the directory that contains the CSV
        file being processed. If the file raises any exception, a warning is
        printed and the default settings are kept.

        :param directory: (str) Directory to search for settings_user.py.
        :raises: TypeError: directory is not a non-empty string.

        :example: (in settings_user.py)
        >>> cfg.output.crf = 14
        >>> cfg.sync.col_audio_file = "my_audio"

        """
        if isinstance(directory, str) is False or len(directory.strip()) == 0:
            raise TypeError("directory must be a non-empty string.")

        user_file = os.path.join(directory.strip(), "settings_user.py")
        if os.path.isfile(user_file) is False:
            return

        try:
            spec   = importlib.util.spec_from_file_location("settings_user", user_file)
            module = importlib.util.module_from_spec(spec)
            module.__dict__["cfg"] = self
            spec.loader.exec_module(module)
        except Exception as e:
            print(f"Warning: settings_user.py could not be loaded ({e}). Default settings are used.")

    # -----------------------------------------------------------------------
    # sync
    # -----------------------------------------------------------------------

    def get_sync(self) -> AViSSSyncSettings:
        """Return the synchronization column settings.

        :return: (AViSSSyncSettings) Synchronization settings instance.

        """
        return self.__sync

    sync = property(get_sync, None)

    # -----------------------------------------------------------------------
    # output
    # -----------------------------------------------------------------------

    def get_output(self) -> AViSSOutputSettings:
        """Return the output filename and encoding settings.

        :return: (AViSSOutputSettings) Output settings instance.

        """
        return self.__output

    output = property(get_output, None)

    # -----------------------------------------------------------------------

    def __enter__(self):
        return self

    # -----------------------------------------------------------------------

    def __exit__(self, exc_type, exc_value, traceback):
        pass

# ---------------------------------------------------------------------------
# Global settings instance.
# Loaded once at import time; user overrides are applied automatically.
# ---------------------------------------------------------------------------

cfg = AViSSSettings()
