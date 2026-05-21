"""
:filename: utils.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Utility functions of AViSS.

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

This module provides small, stateless utility functions used throughout AViSS.
All functions are pure or have only local side effects (filesystem, subprocess).

Functions are grouped into four sections:

    - Time conversions: time_to_seconds, seconds_to_time.
    - Filesystem helpers: check_file, create_working_dir.
    - External command helpers: is_command_available, check_command, run_command.
    - Output filename builder: build_output_name.

"""

import os
import shlex
import shutil
import subprocess

# ---------------------------------------------------------------------------
# Time conversions
# ---------------------------------------------------------------------------


def time_to_seconds(strtime: str) -> float:
    """Convert a time string into a number of seconds.

    Accepted formats: MM:SS, MM:SS.mmm, HH:MM:SS, HH:MM:SS.mmm.

    :example:
    >>> time_to_seconds("00:01")
    1.0
    >>> time_to_seconds("01:01")
    61.0
    >>> time_to_seconds("00:00:01.100")
    1.1
    >>> time_to_seconds("01:01:01")
    3661.0

    :param strtime: (str) Time string in MM:SS or HH:MM:SS format.
    :return: (float) Time value in seconds.
    :raises: TypeError: strtime is not a string.
    :raises: ValueError: strtime does not match an expected format.

    """
    if isinstance(strtime, str) is False:
        raise TypeError("strtime must be a string.")

    parts = strtime.strip().split(":")
    if len(parts) < 2 or len(parts) > 3:
        raise ValueError(
            f"Time format not supported. Expected MM:SS or HH:MM:SS, got {strtime!r}."
        )

    try:
        if len(parts) == 3:
            seconds = float(parts[0]) * 3600. + float(parts[1]) * 60. + float(parts[2])
        else:
            seconds = float(parts[0]) * 60. + float(parts[1])
    except ValueError:
        raise ValueError(
            f"Time string contains non-numeric values: {strtime!r}."
        )

    if seconds < 0.:
        raise ValueError(f"Time value must be zero or positive, got {strtime!r}.")

    return seconds

# ---------------------------------------------------------------------------


def seconds_to_time(value: float) -> str:
    """Convert a number of seconds into a time string.

    The HH: prefix is omitted when the value is less than one hour.
    Milliseconds are omitted when zero.

    :example:
    >>> seconds_to_time(1.)
    '00:01'
    >>> seconds_to_time(61.)
    '01:01'
    >>> seconds_to_time(3661.234)
    '01:01:01.234'

    :param value: (int|float) Time value in seconds.
    :return: (str) Time string in MM:SS or HH:MM:SS format.
    :raises: TypeError: value is not a number.
    :raises: ValueError: value is negative.

    """
    if isinstance(value, (int, float)) is False:
        raise TypeError("value must be a number.")
    if float(value) < 0.:
        raise ValueError("value must be zero or positive.")

    total = float(value)
    hours = int(total // 3600)
    total -= hours * 3600.
    minutes = int(total // 60)
    secs = int(total % 60)
    millis = int(round((total % 1) * 1000.))

    strtime = ""
    if hours > 0:
        strtime += f"{hours:02d}:"
    strtime += f"{minutes:02d}:{secs:02d}"
    if millis > 0:
        strtime += f".{millis:03d}"

    return strtime

# ---------------------------------------------------------------------------
# Filesystem helpers
# ---------------------------------------------------------------------------


def check_file(path: str) -> None:
    """Raise an exception if the given file does not exist or is empty.

    :param path: (str) Path to the file to check.
    :raises: TypeError: path is not a non-empty string.
    :raises: FileNotFoundError: The file does not exist.
    :raises: ValueError: The file is empty.

    """
    if isinstance(path, str) is False or len(path.strip()) == 0:
        raise TypeError("path must be a non-empty string.")
    if os.path.isfile(path) is False:
        raise FileNotFoundError(f"File not found: {path!r}.")
    if os.path.getsize(path) == 0:
        raise ValueError(f"File is empty: {path!r}.")

# ---------------------------------------------------------------------------


def create_working_dir(path: str) -> str:
    """Create a working directory and set its permissions to 777.

    The directory must not already exist; this prevents accidental
    overwriting of previous results.

    :param path: (str) Path of the directory to create.
    :return: (str) Path of the created directory.
    :raises: TypeError: path is not a non-empty string.
    :raises: FileExistsError: The directory already exists.
    :raises: OSError: The directory could not be created.

    """
    if isinstance(path, str) is False or len(path.strip()) == 0:
        raise TypeError("path must be a non-empty string.")
    if os.path.exists(path) is True:
        raise FileExistsError(
            f"Working directory already exists: {path!r}. "
            f"Remove it or use a different name to avoid overwriting previous results."
        )
    os.mkdir(path)
    os.chmod(path, 0o777)
    return path

# ---------------------------------------------------------------------------
# External command helpers
# ---------------------------------------------------------------------------


def is_command_available(name: str) -> bool:
    """Return True if the given system command is available.

    :param name: (str) Command name (e.g. "ffmpeg", "sox").
    :return: (bool) True if the command can be invoked.
    :raises: TypeError: name is not a non-empty string.

    """
    if isinstance(name, str) is False or len(name.strip()) == 0:
        raise TypeError("name must be a non-empty string.")

    return shutil.which(name.strip()) is not None

# ---------------------------------------------------------------------------


def check_command(name: str) -> None:
    """Raise an exception if the given system command is not available.

    :param name: (str) Command name (e.g. "ffmpeg", "sox").
    :raises: TypeError: name is not a non-empty string.
    :raises: EnvironmentError: The command is not available on this system.

    """
    if is_command_available(name) is False:
        raise EnvironmentError(
            f"Required command not found: {name!r}. "
            f"Please install it before running AViSS."
        )

# ---------------------------------------------------------------------------


def run_command(command: str) -> list:
    """Execute a shell command and return its output lines.

    The command is split with shlex so it is safe to pass a full command
    string including arguments.

    :param command: (str) Full command string to execute.
    :return: (list) List of non-empty output lines (stdout + stderr).
    :raises: TypeError: command is not a non-empty string.
    :raises: EnvironmentError: The command could not be executed.

    :example:
    >>> lines = run_command("ffmpeg -version")

    """
    if isinstance(command, str) is False or len(command.strip()) == 0:
        raise TypeError("command must be a non-empty string.")

    args = shlex.split(command)
    try:
        result = subprocess.run(
            args,
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    except OSError as e:
        raise EnvironmentError(f"Command could not be executed: {command!r}. Reason: {e}.")

    lines = []
    for stream in (result.stdout, result.stderr):
        if stream is not None:
            for line in stream.decode(errors="replace").splitlines():
                if len(line.strip()) > 0:
                    lines.append(line.strip())

    return lines

# ---------------------------------------------------------------------------
# Output filename builder
# ---------------------------------------------------------------------------


def build_output_name(output_name_meta: dict, output_name_cols: list, sep: str = "_") -> str:
    """Build the output filename stem from session metadata and column rules.

    Each rule in output_name_cols is a tuple (col, prefix, fmt):
        - col    : CSV column name; looked up in output_name_meta.
        - prefix : string prepended to the formatted value (e.g. "S", "T").
        - fmt    : None for raw string, "02d" or "d" for integer formatting.

    A rule whose column is absent from output_name_meta, or whose value is
    an empty string, is silently skipped.

    :example:
    >>> meta = {"ID": "Laurent", "Session": "9", "SerieLabel": "sent"}
    >>> cols = [("ID", "", None), ("Session", "S", "02d"), ("Theme", "T", "02d"), ("SerieLabel", "", None)]
    >>> build_output_name(meta, cols)
    'Laurent_S09_sent'

    :param output_name_meta: (dict) Mapping of column name to raw CSV value.
    :param output_name_cols: (list) List of (col, prefix, fmt) tuples.
    :param sep: (str) Token separator. Defaults to "_".
    :return: (str) Output filename stem.
    :raises: TypeError: output_name_meta is not a dict.
    :raises: TypeError: output_name_cols is not a list.
    :raises: TypeError: sep is not a string.
    :raises: ValueError: A numeric format is requested but the value is not an integer.

    """
    if isinstance(output_name_meta, dict) is False:
        raise TypeError("output_name_meta must be a dict.")
    if isinstance(output_name_cols, list) is False:
        raise TypeError("output_name_cols must be a list.")
    if isinstance(sep, str) is False:
        raise TypeError("sep must be a string.")

    tokens = []
    for col, prefix, fmt in output_name_cols:
        raw = output_name_meta.get(col, "").strip()
        if len(raw) == 0:
            continue

        if fmt is None:
            tokens.append(f"{prefix}{raw}")
        else:
            try:
                tokens.append(f"{prefix}{int(raw):{fmt}}")
            except ValueError:
                raise ValueError(
                    f"Column {col!r} has value {raw!r} which cannot be formatted as {fmt!r}."
                )

    return sep.join(tokens)
