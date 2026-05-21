"""
:filename: test_utils.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Unit tests for aviss.utils module.

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
import unittest
import tempfile
import shutil

from aviss.utils import (
    time_to_seconds,
    seconds_to_time,
    check_file,
    create_working_dir,
    is_command_available,
    check_command,
    build_output_name,
)

# ---------------------------------------------------------------------------


class TestTimeToSeconds(unittest.TestCase):

    # -----------------------------------------------------------------------

    def test_mm_ss(self):
        self.assertEqual(1.0,   time_to_seconds("00:01"))
        self.assertEqual(61.0,  time_to_seconds("01:01"))
        self.assertEqual(0.0,   time_to_seconds("00:00"))
        self.assertEqual(600.0, time_to_seconds("10:00"))

    # -----------------------------------------------------------------------

    def test_mm_ss_mmm(self):
        self.assertAlmostEqual(1.1,   time_to_seconds("00:01.100"), places=3)
        self.assertAlmostEqual(61.25, time_to_seconds("01:01.250"), places=3)
        self.assertAlmostEqual(6.009, time_to_seconds("00:06.009"), places=3)

    # -----------------------------------------------------------------------

    def test_hh_mm_ss(self):
        self.assertEqual(3661.0, time_to_seconds("01:01:01"))
        self.assertEqual(3600.0, time_to_seconds("01:00:00"))
        self.assertEqual(0.0,    time_to_seconds("00:00:00"))

    # -----------------------------------------------------------------------

    def test_hh_mm_ss_mmm(self):
        self.assertAlmostEqual(1.1,    time_to_seconds("00:00:01.100"), places=3)
        self.assertAlmostEqual(3661.5, time_to_seconds("01:01:01.500"), places=3)

    # -----------------------------------------------------------------------

    def test_type_error(self):
        with self.assertRaises(TypeError):
            time_to_seconds(1.0)
        with self.assertRaises(TypeError):
            time_to_seconds(None)
        with self.assertRaises(TypeError):
            time_to_seconds(["00:01"])

    # -----------------------------------------------------------------------

    def test_value_error_format(self):
        with self.assertRaises(ValueError):
            time_to_seconds("01")
        with self.assertRaises(ValueError):
            time_to_seconds("01:02:03:04")
        with self.assertRaises(ValueError):
            time_to_seconds("ab:cd")

    # -----------------------------------------------------------------------

    def test_value_error_negative(self):
        with self.assertRaises(ValueError):
            time_to_seconds("-01:00")

# ---------------------------------------------------------------------------


class TestSecondsToTime(unittest.TestCase):

    # -----------------------------------------------------------------------

    def test_seconds_only(self):
        self.assertEqual("00:01", seconds_to_time(1.))
        self.assertEqual("00:00", seconds_to_time(0.))
        self.assertEqual("00:59", seconds_to_time(59.))

    # -----------------------------------------------------------------------

    def test_minutes(self):
        self.assertEqual("01:01", seconds_to_time(61.))
        self.assertEqual("10:00", seconds_to_time(600.))

    # -----------------------------------------------------------------------

    def test_hours(self):
        self.assertEqual("01:01:01", seconds_to_time(3661.))
        self.assertEqual("01:00:00", seconds_to_time(3600.))

    # -----------------------------------------------------------------------

    def test_milliseconds(self):
        self.assertEqual("00:01.100", seconds_to_time(1.1))
        self.assertEqual("01:01.250", seconds_to_time(61.25))
        self.assertEqual("01:01:01.500", seconds_to_time(3661.5))

    # -----------------------------------------------------------------------

    def test_no_milliseconds_when_zero(self):
        result = seconds_to_time(60.)
        self.assertFalse("." in result)

    # -----------------------------------------------------------------------

    def test_roundtrip(self):
        for strtime in ("00:06.009", "03:36.000", "01:01:01.500", "00:00"):
            self.assertAlmostEqual(
                time_to_seconds(strtime),
                time_to_seconds(seconds_to_time(time_to_seconds(strtime))),
                places=3
            )

    # -----------------------------------------------------------------------

    def test_type_error(self):
        with self.assertRaises(TypeError):
            seconds_to_time("1.0")
        with self.assertRaises(TypeError):
            seconds_to_time(None)

    # -----------------------------------------------------------------------

    def test_value_error_negative(self):
        with self.assertRaises(ValueError):
            seconds_to_time(-1.)

# ---------------------------------------------------------------------------


class TestCheckFile(unittest.TestCase):

    def setUp(self):
        self.__tmp_dir  = tempfile.mkdtemp()
        self.__tmp_file = os.path.join(self.__tmp_dir, "sample.wav")
        with open(self.__tmp_file, "w") as fh:
            fh.write("dummy")

    def tearDown(self):
        shutil.rmtree(self.__tmp_dir, ignore_errors=True)

    # -----------------------------------------------------------------------

    def test_existing_file(self):
        check_file(self.__tmp_file)

    # -----------------------------------------------------------------------

    def test_missing_file(self):
        with self.assertRaises(FileNotFoundError):
            check_file(os.path.join(self.__tmp_dir, "missing.wav"))

    # -----------------------------------------------------------------------

    def test_empty_file(self):
        empty = os.path.join(self.__tmp_dir, "empty.wav")
        open(empty, "w").close()
        with self.assertRaises(ValueError):
            check_file(empty)

    # -----------------------------------------------------------------------

    def test_type_error(self):
        with self.assertRaises(TypeError):
            check_file(None)
        with self.assertRaises(TypeError):
            check_file("")
        with self.assertRaises(TypeError):
            check_file(42)

# ---------------------------------------------------------------------------


class TestCreateWorkingDir(unittest.TestCase):

    def setUp(self):
        self.__tmp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.__tmp_dir, ignore_errors=True)

    # -----------------------------------------------------------------------

    def test_creates_directory(self):
        new_dir = os.path.join(self.__tmp_dir, "workdir")
        self.assertFalse(os.path.exists(new_dir))
        result = create_working_dir(new_dir)
        self.assertTrue(os.path.isdir(new_dir))
        self.assertEqual(result, new_dir)

    # -----------------------------------------------------------------------

    def test_raises_if_exists(self):
        existing = os.path.join(self.__tmp_dir, "existing")
        os.mkdir(existing)
        with self.assertRaises(FileExistsError):
            create_working_dir(existing)

    # -----------------------------------------------------------------------

    def test_type_error(self):
        with self.assertRaises(TypeError):
            create_working_dir(None)
        with self.assertRaises(TypeError):
            create_working_dir("")

# ---------------------------------------------------------------------------


class TestIsCommandAvailable(unittest.TestCase):

    # -----------------------------------------------------------------------

    def test_known_command(self):
        # 'python3' or 'python' is always available in the test environment.
        result = is_command_available("python3") or is_command_available("python")
        self.assertTrue(result)

    # -----------------------------------------------------------------------

    def test_unknown_command(self):
        self.assertFalse(is_command_available("__aviss_fake_command__"))

    # -----------------------------------------------------------------------

    def test_type_error(self):
        with self.assertRaises(TypeError):
            is_command_available(None)
        with self.assertRaises(TypeError):
            is_command_available("")

# ---------------------------------------------------------------------------


class TestCheckCommand(unittest.TestCase):

    # -----------------------------------------------------------------------

    def test_raises_for_unknown_command(self):
        with self.assertRaises(EnvironmentError):
            check_command("__aviss_fake_command__")

# ---------------------------------------------------------------------------


class TestBuildOutputName(unittest.TestCase):

    COLS = [
        ("ID",         "",  None),
        ("Session",    "S", "02d"),
        ("Theme",      "T", "02d"),
        ("SerieNum",   "s", "02d"),
        ("SerieLabel", "",  None),
    ]

    # -----------------------------------------------------------------------

    def test_full_row(self):
        meta = {"ID": "Laurent", "Session": "9", "Theme": "3",
                "SerieNum": "4", "SerieLabel": "sent"}
        result = build_output_name(meta, self.COLS)
        self.assertEqual("Laurent_S09_T03_s04_sent", result)

    # -----------------------------------------------------------------------

    def test_session_only(self):
        meta = {"ID": "Laurent", "Session": "9"}
        result = build_output_name(meta, self.COLS)
        self.assertEqual("Laurent_S09", result)

    # -----------------------------------------------------------------------

    def test_theme_only(self):
        meta = {"ID": "Laurent", "Theme": "3", "SerieLabel": "sent"}
        result = build_output_name(meta, self.COLS)
        self.assertEqual("Laurent_T03_sent", result)

    # -----------------------------------------------------------------------

    def test_empty_cells_skipped(self):
        meta = {"ID": "Laurent", "Session": "9", "Theme": "",
                "SerieNum": "", "SerieLabel": "sent"}
        result = build_output_name(meta, self.COLS)
        self.assertEqual("Laurent_S09_sent", result)

    # -----------------------------------------------------------------------

    def test_custom_separator(self):
        meta = {"ID": "Laurent", "Session": "9"}
        result = build_output_name(meta, self.COLS, sep="-")
        self.assertEqual("Laurent-S09", result)

    # -----------------------------------------------------------------------

    def test_zero_padding(self):
        meta = {"ID": "X", "Session": "1"}
        result = build_output_name(meta, self.COLS)
        self.assertEqual("X_S01", result)

    # -----------------------------------------------------------------------

    def test_all_empty_returns_empty_string(self):
        meta = {}
        result = build_output_name(meta, self.COLS)
        self.assertEqual("", result)

    # -----------------------------------------------------------------------

    def test_invalid_numeric_format(self):
        meta = {"ID": "Laurent", "Session": "abc"}
        with self.assertRaises(ValueError):
            build_output_name(meta, self.COLS)

    # -----------------------------------------------------------------------

    def test_type_errors(self):
        with self.assertRaises(TypeError):
            build_output_name("not_a_dict", self.COLS)
        with self.assertRaises(TypeError):
            build_output_name({}, "not_a_list")
        with self.assertRaises(TypeError):
            build_output_name({}, self.COLS, sep=None)

# ---------------------------------------------------------------------------


class TestRunCommand(unittest.TestCase):

    # -----------------------------------------------------------------------

    def test_type_error_none(self):
        with self.assertRaises(TypeError):
            from aviss.utils import run_command
            run_command(None)

    # -----------------------------------------------------------------------

    def test_type_error_empty(self):
        with self.assertRaises(TypeError):
            from aviss.utils import run_command
            run_command("")

    # -----------------------------------------------------------------------

    def test_unknown_command_raises(self):
        from aviss.utils import run_command
        with self.assertRaises(EnvironmentError):
            run_command("__aviss_fake_cmd__ --version")

    # -----------------------------------------------------------------------

    def test_valid_command_returns_lines(self):
        from aviss.utils import run_command
        lines = run_command("echo hello")
        self.assertIsInstance(lines, list)
        self.assertEqual(1, len(lines))
        self.assertEqual("hello", lines[0])

# ---------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main()
