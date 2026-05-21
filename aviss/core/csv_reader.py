"""
:filename: csv_reader.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: CSV file parser for AViSS.

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

The CsvReader class parses an AViSS CSV file and returns a list of Session
objects. The first row of the CSV must be a header row defining column names.
Rows and values are separated by ';' (preferred) or ',' (fallback).

Required columns (names are read from cfg.sync):
    - audio_file, audio_clap
    - video_file, video_clap
    - delay, duration

Optional columns:
    - video_crop_x, video_crop_y, video_crop_w, video_crop_h
    - a second set of audio/video columns (same names suffixed with "2",
      e.g. audio_file2, video_file2, audio_clap2, video_clap2,
      video_crop_x2, video_crop_y2, video_crop_w2, video_crop_h2)
    - any column declared in cfg.output.output_name_cols
    - any other column (stored as free metadata in Session.metadata)

Relative file paths in the CSV are resolved against the directory that
contains the CSV file.

"""

import os

from aviss.settings import cfg
from aviss.models import MediaFile, Session
from aviss.utils import time_to_seconds, check_file

# ---------------------------------------------------------------------------


class CsvReader:
    """Parse an AViSS CSV file and produce a list of Session objects.

    The CSV file must have a header row as its first line. Column names in
    the header are matched against the names declared in cfg.sync and
    cfg.output. Matching is case-sensitive.

    The separator is auto-detected: ';' is tried first, then ','.
    A minimum of 6 columns is required (audio_file, audio_clap, video_file,
    video_clap, delay, duration).

    :example:
    >>> reader = CsvReader("corpus/sessions.csv")
    >>> sessions = reader.read()
    >>> len(sessions)
    10
    >>> sessions[0].audio.path
    '/data/corpus/Laurent_S01_s1.wav'

    """

    # Minimum number of columns required in the CSV.
    MIN_COLUMNS = 6

    # Separator candidates, tried in order.
    SEPARATORS = (";", ",")

    # -----------------------------------------------------------------------

    def __init__(self, csv_path: str):
        """Initialize the CsvReader with the path to the CSV file.

        :param csv_path: (str) Path to the CSV file.
        :raises: TypeError: csv_path is not a non-empty string.
        :raises: FileNotFoundError: The file does not exist.
        :raises: ValueError: The file is empty.

        """
        if isinstance(csv_path, str) is False or len(csv_path.strip()) == 0:
            raise TypeError("csv_path must be a non-empty string.")
        check_file(csv_path)
        self.__csv_path  = csv_path.strip()
        self.__csv_dir   = os.path.dirname(os.path.abspath(csv_path))
        self.__separator = None

    # -----------------------------------------------------------------------
    # csv_path
    # -----------------------------------------------------------------------

    def get_csv_path(self) -> str:
        """Return the path to the CSV file.

        :return: (str) CSV file path.

        """
        return self.__csv_path

    csv_path = property(get_csv_path, None)

    # -----------------------------------------------------------------------
    # Public interface
    # -----------------------------------------------------------------------

    def read(self) -> list:
        """Parse the CSV file and return a list of Session objects.

        The first row is interpreted as the header. Each subsequent non-empty
        row produces one Session. Rows with all-empty cells are silently skipped.

        :return: (list) List of Session instances, one per data row.
        :raises: ValueError: The header row is missing or invalid.
        :raises: ValueError: A data row cannot be parsed into a Session.

        """
        raw_lines = self.__read_raw_lines()
        if len(raw_lines) < 2:
            raise ValueError(
                f"CSV file {self.__csv_path!r} must have at least one header row "
                f"and one data row."
            )

        header = self.__parse_header(raw_lines[0])
        self.__check_required_columns(header)

        sessions = []
        for row_index, raw_line in enumerate(raw_lines[1:], start=2):
            row = self.__split_row(raw_line)
            if len(row) == 0 or all(len(v.strip()) == 0 for v in row):
                continue
            session = self.__build_session(header, row, row_index)
            sessions.append(session)

        return sessions

    # -----------------------------------------------------------------------

    def read_row(self, row_number: int) -> Session:
        """Parse a single data row and return the corresponding Session.

        Row numbering starts at 1 (the first data row, after the header).

        :param row_number: (int) 1-based index of the data row to parse.
        :return: (Session) Session built from the given row.
        :raises: TypeError: row_number is not an integer.
        :raises: ValueError: row_number is out of range.
        :raises: ValueError: The row cannot be parsed into a Session.

        """
        if isinstance(row_number, int) is False:
            raise TypeError("row_number must be an integer.")
        if row_number < 1:
            raise ValueError("row_number must be >= 1.")

        raw_lines = self.__read_raw_lines()
        if len(raw_lines) < 2:
            raise ValueError(
                f"CSV file {self.__csv_path!r} must have at least one header row "
                f"and one data row."
            )

        header = self.__parse_header(raw_lines[0])
        self.__check_required_columns(header)

        data_lines = [ln for ln in raw_lines[1:] if len(ln.strip()) > 0]
        if row_number > len(data_lines):
            raise ValueError(
                f"Row number {row_number} is out of range. "
                f"The CSV file has {len(data_lines)} data row(s)."
            )

        row = self.__split_row(data_lines[row_number - 1])
        return self.__build_session(header, row, row_number + 1)

    # -----------------------------------------------------------------------
    # Private helpers
    # -----------------------------------------------------------------------

    def __read_raw_lines(self) -> list:
        """Read the CSV file and return its non-empty lines as strings.

        :return: (list) List of raw line strings.

        """
        with open(self.__csv_path, "r", encoding="utf-8") as fh:
            lines = fh.readlines()

        return [ln.rstrip("\n").rstrip("\r") for ln in lines if len(ln.strip()) > 0]

    # -----------------------------------------------------------------------

    def __split_row(self, line: str) -> list:
        """Split a CSV row using the detected or auto-detected separator.

        :param line: (str) Raw CSV line.
        :return: (list) List of cell strings.

        """
        if self.__separator is not None:
            return line.split(self.__separator)

        for sep in CsvReader.SEPARATORS:
            parts = line.split(sep)
            if len(parts) >= CsvReader.MIN_COLUMNS:
                self.__separator = sep
                return parts

        return line.split(CsvReader.SEPARATORS[0])

    # -----------------------------------------------------------------------

    def __parse_header(self, line: str) -> list:
        """Parse the header row and return a list of stripped column names.

        :param line: (str) Raw header line.
        :return: (list) List of column name strings.
        :raises: ValueError: The header row has fewer columns than the minimum.

        """
        columns = self.__split_row(line)
        columns = [c.strip() for c in columns]

        if len(columns) < CsvReader.MIN_COLUMNS:
            raise ValueError(
                f"CSV header has only {len(columns)} column(s). "
                f"At least {CsvReader.MIN_COLUMNS} are required."
            )

        return columns

    # -----------------------------------------------------------------------

    def __check_required_columns(self, header: list) -> None:
        """Raise ValueError if any required synchronization column is missing.

        :param header: (list) List of column names from the header row.
        :raises: ValueError: One or more required columns are absent.

        """
        required = [
            cfg.sync.col_audio_file,
            cfg.sync.col_audio_clap,
            cfg.sync.col_video_file,
            cfg.sync.col_video_clap,
            cfg.sync.col_delay,
            cfg.sync.col_duration,
        ]
        missing = [col for col in required if col not in header]
        if len(missing) > 0:
            raise ValueError(
                f"The following required columns are missing from the CSV header: "
                f"{missing}. "
                f"Check cfg.sync column name settings."
            )

    # -----------------------------------------------------------------------

    def __get_cell(self, header: list, row: list, col_name: str) -> str:
        """Return the stripped cell value for the given column name, or "".

        :param header: (list) List of column names.
        :param row: (list) List of cell values for the current row.
        :param col_name: (str) Column name to look up.
        :return: (str) Cell value, or "" if the column is absent or the row
                 is too short.

        """
        if col_name not in header:
            return ""
        idx = header.index(col_name)
        if idx >= len(row):
            return ""
        return row[idx].strip()

    # -----------------------------------------------------------------------

    def __resolve_path(self, relative: str) -> str:
        """Resolve a relative file path against the CSV directory.

        :param relative: (str) Relative path as found in the CSV cell.
        :return: (str) Absolute path.

        """
        if os.path.isabs(relative) is True:
            return relative
        return os.path.join(self.__csv_dir, relative)

    # -----------------------------------------------------------------------

    def __build_crop(self, header: list, row: list, suffix: str = "") -> tuple:
        """Extract crop parameters for a video column set.

        The suffix is "" for the primary video and "2" for the secondary one.
        All four values must be present and non-empty for crop to be applied;
        otherwise (None, None, None, None) is returned.

        :param header: (list) List of column names.
        :param row: (list) List of cell values for the current row.
        :param suffix: (str) Column name suffix ("" or "2").
        :return: (tuple) (x, y, w, h) as int|None values.

        """
        x_str = self.__get_cell(header, row, cfg.sync.col_video_crop_x + suffix)
        y_str = self.__get_cell(header, row, cfg.sync.col_video_crop_y + suffix)
        w_str = self.__get_cell(header, row, cfg.sync.col_video_crop_w + suffix)
        h_str = self.__get_cell(header, row, cfg.sync.col_video_crop_h + suffix)

        if len(x_str) == 0 or len(y_str) == 0 or len(w_str) == 0 or len(h_str) == 0:
            return None, None, None, None

        try:
            return int(x_str), int(y_str), int(w_str), int(h_str)
        except ValueError:
            return None, None, None, None

    # -----------------------------------------------------------------------

    def __build_media_file(self, header: list, row: list,
                           col_file: str, col_clap: str,
                           crop: tuple, row_index: int) -> MediaFile:
        """Build a MediaFile from the given column names and crop tuple.

        :param header: (list) List of column names.
        :param row: (list) List of cell values.
        :param col_file: (str) Column name for the file path.
        :param col_clap: (str) Column name for the clap time.
        :param crop: (tuple) (x, y, w, h) as int|None.
        :param row_index: (int) 1-based row number, used in error messages.
        :return: (MediaFile) Constructed MediaFile instance.
        :raises: ValueError: A required cell is empty or invalid.

        """
        path_raw = self.__get_cell(header, row, col_file)
        clap_raw = self.__get_cell(header, row, col_clap)

        if len(path_raw) == 0:
            raise ValueError(
                f"Row {row_index}: column {col_file!r} is empty."
            )
        if len(clap_raw) == 0:
            raise ValueError(
                f"Row {row_index}: column {col_clap!r} is empty."
            )

        try:
            clap_seconds = time_to_seconds(clap_raw)
        except ValueError as e:
            raise ValueError(f"Row {row_index}: invalid clap time in column {col_clap!r}. {e}.")

        media = MediaFile(self.__resolve_path(path_raw), clap_seconds)

        x, y, w, h = crop
        if x is not None:
            media.crop_x = x
            media.crop_y = y
            media.crop_w = w
            media.crop_h = h

        return media

    # -----------------------------------------------------------------------

    def __build_session(self, header: list, row: list, row_index: int) -> Session:
        """Build a Session from a parsed header and data row.

        :param header: (list) List of column names.
        :param row: (list) List of cell values.
        :param row_index: (int) 1-based row number, used in error messages.
        :return: (Session) Constructed Session instance.
        :raises: ValueError: Any required cell is empty or cannot be parsed.

        """
        # Primary audio
        audio_crop = (None, None, None, None)
        audio = self.__build_media_file(
            header, row,
            cfg.sync.col_audio_file,
            cfg.sync.col_audio_clap,
            audio_crop, row_index
        )

        # Primary video (with optional crop)
        video_crop = self.__build_crop(header, row, suffix="")
        video = self.__build_media_file(
            header, row,
            cfg.sync.col_video_file,
            cfg.sync.col_video_clap,
            video_crop, row_index
        )

        # Delay and duration
        delay_raw    = self.__get_cell(header, row, cfg.sync.col_delay)
        duration_raw = self.__get_cell(header, row, cfg.sync.col_duration)

        try:
            delay = float(delay_raw) if len(delay_raw) > 0 else 0.
        except ValueError:
            raise ValueError(
                f"Row {row_index}: invalid delay value {delay_raw!r}."
            )

        try:
            duration = time_to_seconds(duration_raw)
        except ValueError as e:
            raise ValueError(
                f"Row {row_index}: invalid duration in column "
                f"{cfg.sync.col_duration!r}. {e}."
            )

        session = Session(audio, video, delay=delay, duration=duration)

        # Optional secondary audio
        audio2_raw = self.__get_cell(header, row, cfg.sync.col_audio_file + "2")
        if len(audio2_raw) > 0:
            audio2 = self.__build_media_file(
                header, row,
                cfg.sync.col_audio_file + "2",
                cfg.sync.col_audio_clap + "2",
                (None, None, None, None), row_index
            )
            session.audio2 = audio2

        # Optional secondary video (with optional crop)
        video2_raw = self.__get_cell(header, row, cfg.sync.col_video_file + "2")
        if len(video2_raw) > 0:
            video2_crop = self.__build_crop(header, row, suffix="2")
            video2 = self.__build_media_file(
                header, row,
                cfg.sync.col_video_file + "2",
                cfg.sync.col_video_clap + "2",
                video2_crop, row_index
            )
            session.video2 = video2

        # Output filename metadata
        sync_cols = {
            cfg.sync.col_audio_file, cfg.sync.col_audio_clap,
            cfg.sync.col_audio_file + "2", cfg.sync.col_audio_clap + "2",
            cfg.sync.col_video_file, cfg.sync.col_video_clap,
            cfg.sync.col_video_file + "2", cfg.sync.col_video_clap + "2",
            cfg.sync.col_video_crop_x, cfg.sync.col_video_crop_y,
            cfg.sync.col_video_crop_w, cfg.sync.col_video_crop_h,
            cfg.sync.col_video_crop_x + "2", cfg.sync.col_video_crop_y + "2",
            cfg.sync.col_video_crop_w + "2", cfg.sync.col_video_crop_h + "2",
            cfg.sync.col_delay, cfg.sync.col_duration,
        }
        name_col_names = {entry[0] for entry in cfg.output.output_name_cols}

        output_name_meta = {}
        for col_name in name_col_names:
            value = self.__get_cell(header, row, col_name)
            if len(value) > 0:
                output_name_meta[col_name] = value
        session.output_name_meta = output_name_meta

        # Free metadata: every column not used for sync or output naming
        metadata = {}
        for col_name in header:
            if col_name in sync_cols:
                continue
            if col_name in name_col_names:
                continue
            value = self.__get_cell(header, row, col_name)
            if len(value) > 0:
                metadata[col_name] = value
        session.metadata = metadata

        return session
