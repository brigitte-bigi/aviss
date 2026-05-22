"""
:filename: test_csv_reader.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Unit tests for aviss.core.csv_reader module.

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

Test CSV files are written to a temporary directory and removed after each
test. File paths in the CSV are intentionally fake (the files do not exist
on disk): CsvReader only checks paths when building Session objects, and
MediaFile.exists() is not called during parsing.

The CSV structure used in these tests mirrors the real corpus format
(montage.csv), with the column names matching the defaults in cfg.sync.

"""

import os
import unittest
import tempfile
import shutil

from aviss.core.csv_reader import CsvReader
from aviss.models import Session

# ---------------------------------------------------------------------------

# Minimal valid CSV matching cfg.sync default column names.
CSV_MINIMAL = (
    "ID;Session;Serie;audio_file;video_file;audio_clap;video_clap;delay;duration\n"
    "Laurent;9;2;audio/RME_0038.wav;video/MVI_0038.MP4;00:03.843;00:06.410;0.200;04:08.250\n"
)

# Two data rows.
CSV_TWO_ROWS = (
    "ID;Session;Serie;audio_file;video_file;audio_clap;video_clap;delay;duration\n"
    "Laurent;9;2;audio/RME_0038.wav;video/MVI_0038.MP4;00:03.843;00:06.410;0.200;04:08.250\n"
    "Laurent;8;1;audio/RME_0035.wav;video/MVI_0035.MP4;00:04.787;00:09.995;6.230;02:57.000\n"
)

# CSV with free metadata columns.
CSV_WITH_METADATA = (
    "ID;Session;Serie;audio_file;video_file;audio_clap;video_clap;delay;duration;handedness;gender\n"
    "Laurent;9;2;audio/RME_0038.wav;video/MVI_0038.MP4;00:03.843;00:06.410;0.200;04:08.250;r;m\n"
)

# CSV with a secondary audio and video.
CSV_WITH_SECONDARY = (
    "ID;Session;Serie;"
    "audio_file;video_file;audio_clap;video_clap;delay;duration;"
    "audio_file2;video_file2;audio_clap2;video_clap2\n"
    "Laurent;9;2;"
    "audio/RME_0038.wav;video/MVI_0038.MP4;00:03.843;00:06.410;0.200;04:08.250;"
    "audio/RME_0038b.wav;video/MVI_0038b.MP4;00:04.000;00:07.000\n"
)

# CSV with video name columns (primary and secondary).
CSV_WITH_VIDEO_NAMES = (
    "ID;Session;Serie;"
    "audio_file;video_file;audio_clap;video_clap;video_name;delay;duration;"
    "video_file2;video_clap2;video_name2\n"
    "Laurent;9;2;"
    "audio/RME_0038.wav;video/MVI_0038.MP4;00:03.843;00:06.410;front;0.200;04:08.250;"
    "video/MVI_0038b.MP4;00:07.000;side\n"
)

# CSV with crop columns.
CSV_WITH_CROP = (
    "ID;Session;Serie;audio_file;video_file;audio_clap;video_clap;delay;duration;"
    "video_crop_x;video_crop_y;video_crop_w;video_crop_h\n"
    "Laurent;9;2;audio/RME_0038.wav;video/MVI_0038.MP4;00:03.843;00:06.410;0.200;04:08.250;"
    "0;32;1600;960\n"
)

# CSV with comma separator instead of semicolon.
CSV_COMMA_SEP = (
    "ID,Session,Serie,audio_file,video_file,audio_clap,video_clap,delay,duration\n"
    "Laurent,9,2,audio/RME_0038.wav,video/MVI_0038.MP4,00:03.843,00:06.410,0.200,04:08.250\n"
)

# CSV with an empty data row (should be skipped).
CSV_WITH_EMPTY_ROW = (
    "ID;Session;Serie;audio_file;video_file;audio_clap;video_clap;delay;duration\n"
    "Laurent;9;2;audio/RME_0038.wav;video/MVI_0038.MP4;00:03.843;00:06.410;0.200;04:08.250\n"
    "\n"
    "Laurent;8;1;audio/RME_0035.wav;video/MVI_0035.MP4;00:04.787;00:09.995;6.230;02:57.000\n"
)

# CSV missing the audio_clap column.
CSV_MISSING_REQUIRED = (
    "ID;Session;Serie;audio_file;video_file;video_clap;delay;duration\n"
    "Laurent;9;2;audio/RME_0038.wav;video/MVI_0038.MP4;00:06.410;0.200;04:08.250\n"
)

# Header only, no data row.
CSV_HEADER_ONLY = (
    "ID;Session;Serie;audio_file;video_file;audio_clap;video_clap;delay;duration\n"
)

# ---------------------------------------------------------------------------


def _write_csv(tmp_dir: str, content: str, filename: str = "test.csv") -> str:
    """Write CSV content to a temporary file and return its path.

    """
    path = os.path.join(tmp_dir, filename)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)
    return path

# ---------------------------------------------------------------------------


class TestCsvReaderInit(unittest.TestCase):

    def setUp(self):
        self.__tmp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.__tmp_dir, ignore_errors=True)

    # -----------------------------------------------------------------------

    def test_valid_path(self):
        path = _write_csv(self.__tmp_dir, CSV_MINIMAL)
        reader = CsvReader(path)
        self.assertEqual(path, reader.csv_path)

    # -----------------------------------------------------------------------

    def test_type_error(self):
        with self.assertRaises(TypeError):
            CsvReader(None)
        with self.assertRaises(TypeError):
            CsvReader("")
        with self.assertRaises(TypeError):
            CsvReader(42)

    # -----------------------------------------------------------------------

    def test_missing_file(self):
        with self.assertRaises(FileNotFoundError):
            CsvReader(os.path.join(self.__tmp_dir, "missing.csv"))

    # -----------------------------------------------------------------------

    def test_empty_file(self):
        path = os.path.join(self.__tmp_dir, "empty.csv")
        open(path, "w").close()
        with self.assertRaises(ValueError):
            CsvReader(path)

# ---------------------------------------------------------------------------


class TestCsvReaderRead(unittest.TestCase):

    def setUp(self):
        self.__tmp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.__tmp_dir, ignore_errors=True)

    # -----------------------------------------------------------------------

    def test_read_one_row(self):
        path = _write_csv(self.__tmp_dir, CSV_MINIMAL)
        sessions = CsvReader(path).read()
        self.assertEqual(1, len(sessions))
        self.assertIsInstance(sessions[0], Session)

    # -----------------------------------------------------------------------

    def test_read_two_rows(self):
        path = _write_csv(self.__tmp_dir, CSV_TWO_ROWS)
        sessions = CsvReader(path).read()
        self.assertEqual(2, len(sessions))

    # -----------------------------------------------------------------------

    def test_read_skips_empty_rows(self):
        path = _write_csv(self.__tmp_dir, CSV_WITH_EMPTY_ROW)
        sessions = CsvReader(path).read()
        self.assertEqual(2, len(sessions))

    # -----------------------------------------------------------------------

    def test_read_header_only_raises(self):
        path = _write_csv(self.__tmp_dir, CSV_HEADER_ONLY)
        with self.assertRaises(ValueError):
            CsvReader(path).read()

    # -----------------------------------------------------------------------

    def test_read_missing_required_column_raises(self):
        path = _write_csv(self.__tmp_dir, CSV_MISSING_REQUIRED)
        with self.assertRaises(ValueError):
            CsvReader(path).read()

    # -----------------------------------------------------------------------

    def test_read_comma_separator(self):
        path = _write_csv(self.__tmp_dir, CSV_COMMA_SEP)
        sessions = CsvReader(path).read()
        self.assertEqual(1, len(sessions))

# ---------------------------------------------------------------------------


class TestCsvReaderSessionValues(unittest.TestCase):
    """Verify that parsed Session values match the CSV content.

    """

    def setUp(self):
        self.__tmp_dir = tempfile.mkdtemp()
        path = _write_csv(self.__tmp_dir, CSV_MINIMAL)
        self.__session = CsvReader(path).read()[0]

    def tearDown(self):
        shutil.rmtree(self.__tmp_dir, ignore_errors=True)

    # -----------------------------------------------------------------------

    def test_audio_clap_time(self):
        # 00:03.843 = 3.843s
        self.assertAlmostEqual(3.843, self.__session.audio.clap_time, places=3)

    # -----------------------------------------------------------------------

    def test_video_clap_time(self):
        # 00:06.410 = 6.410s
        self.assertAlmostEqual(6.410, self.__session.video.clap_time, places=3)

    # -----------------------------------------------------------------------

    def test_delay(self):
        self.assertAlmostEqual(0.2, self.__session.delay, places=3)

    # -----------------------------------------------------------------------

    def test_duration(self):
        # 04:08.250 = 248.250s
        self.assertAlmostEqual(248.25, self.__session.duration, places=3)

    # -----------------------------------------------------------------------

    def test_audio_path_resolved(self):
        # Relative paths are resolved against the CSV directory.
        self.assertTrue(os.path.isabs(self.__session.audio.path))

    # -----------------------------------------------------------------------

    def test_video_path_resolved(self):
        self.assertTrue(os.path.isabs(self.__session.video.path))

    # -----------------------------------------------------------------------

    def test_no_secondary_media(self):
        self.assertFalse(self.__session.has_second_audio())
        self.assertFalse(self.__session.has_second_video())

# ---------------------------------------------------------------------------


class TestCsvReaderMetadata(unittest.TestCase):

    def setUp(self):
        self.__tmp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.__tmp_dir, ignore_errors=True)

    # -----------------------------------------------------------------------

    def test_free_metadata_loaded(self):
        path = _write_csv(self.__tmp_dir, CSV_WITH_METADATA)
        session = CsvReader(path).read()[0]
        self.assertIn("handedness", session.metadata)
        self.assertIn("gender",     session.metadata)
        self.assertEqual("r", session.metadata["handedness"])
        self.assertEqual("m", session.metadata["gender"])

    # -----------------------------------------------------------------------

    def test_output_name_meta_loaded(self):
        path = _write_csv(self.__tmp_dir, CSV_MINIMAL)
        session = CsvReader(path).read()[0]
        # "ID" and "Session" are in the default OUTPUT_NAME_COLS.
        self.assertIn("ID",      session.output_name_meta)
        self.assertIn("Session", session.output_name_meta)
        self.assertEqual("Laurent", session.output_name_meta["ID"])

    # -----------------------------------------------------------------------

    def test_sync_columns_not_in_metadata(self):
        path = _write_csv(self.__tmp_dir, CSV_WITH_METADATA)
        session = CsvReader(path).read()[0]
        self.assertNotIn("audio_file",  session.metadata)
        self.assertNotIn("video_file",  session.metadata)
        self.assertNotIn("audio_clap",  session.metadata)
        self.assertNotIn("video_clap",  session.metadata)
        self.assertNotIn("delay",       session.metadata)
        self.assertNotIn("duration",    session.metadata)

# ---------------------------------------------------------------------------


class TestCsvReaderSecondaryMedia(unittest.TestCase):

    def setUp(self):
        self.__tmp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.__tmp_dir, ignore_errors=True)

    # -----------------------------------------------------------------------

    def test_secondary_audio_loaded(self):
        path = _write_csv(self.__tmp_dir, CSV_WITH_SECONDARY)
        session = CsvReader(path).read()[0]
        self.assertTrue(session.has_second_audio())
        self.assertAlmostEqual(4.0, session.audio2.clap_time, places=3)

    # -----------------------------------------------------------------------

    def test_secondary_video_loaded(self):
        path = _write_csv(self.__tmp_dir, CSV_WITH_SECONDARY)
        session = CsvReader(path).read()[0]
        self.assertTrue(session.has_second_video())
        self.assertAlmostEqual(7.0, session.video2.clap_time, places=3)

# ---------------------------------------------------------------------------


class TestCsvReaderVideoNames(unittest.TestCase):

    def setUp(self):
        self.__tmp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.__tmp_dir, ignore_errors=True)

    # -----------------------------------------------------------------------

    def test_video_names_loaded(self):
        path = _write_csv(self.__tmp_dir, CSV_WITH_VIDEO_NAMES)
        session = CsvReader(path).read()[0]
        self.assertEqual("front", session.video_name)
        self.assertEqual("side",  session.video_name2)

    # -----------------------------------------------------------------------

    def test_video_name_not_in_metadata(self):
        path = _write_csv(self.__tmp_dir, CSV_WITH_VIDEO_NAMES)
        session = CsvReader(path).read()[0]
        self.assertNotIn("video_name",  session.metadata)
        self.assertNotIn("video_name2", session.metadata)

    # -----------------------------------------------------------------------

    def test_video_name_absent_is_none(self):
        path = _write_csv(self.__tmp_dir, CSV_MINIMAL)
        session = CsvReader(path).read()[0]
        self.assertIsNone(session.video_name)
        self.assertIsNone(session.video_name2)

# ---------------------------------------------------------------------------


class TestCsvReaderCrop(unittest.TestCase):

    def setUp(self):
        self.__tmp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.__tmp_dir, ignore_errors=True)

    # -----------------------------------------------------------------------

    def test_crop_loaded(self):
        path = _write_csv(self.__tmp_dir, CSV_WITH_CROP)
        session = CsvReader(path).read()[0]
        self.assertTrue(session.video.has_crop())
        self.assertEqual(0,    session.video.crop_x)
        self.assertEqual(32,   session.video.crop_y)
        self.assertEqual(1600, session.video.crop_w)
        self.assertEqual(960,  session.video.crop_h)

    # -----------------------------------------------------------------------

    def test_no_crop_when_columns_absent(self):
        path = _write_csv(self.__tmp_dir, CSV_MINIMAL)
        session = CsvReader(path).read()[0]
        self.assertFalse(session.video.has_crop())

# ---------------------------------------------------------------------------


class TestCsvReaderReadRow(unittest.TestCase):

    def setUp(self):
        self.__tmp_dir = tempfile.mkdtemp()
        self.__path = _write_csv(self.__tmp_dir, CSV_TWO_ROWS)

    def tearDown(self):
        shutil.rmtree(self.__tmp_dir, ignore_errors=True)

    # -----------------------------------------------------------------------

    def test_read_row_1(self):
        session = CsvReader(self.__path).read_row(1)
        self.assertIsInstance(session, Session)
        self.assertAlmostEqual(3.843, session.audio.clap_time, places=3)

    # -----------------------------------------------------------------------

    def test_read_row_2(self):
        session = CsvReader(self.__path).read_row(2)
        self.assertAlmostEqual(4.787, session.audio.clap_time, places=3)

    # -----------------------------------------------------------------------

    def test_read_row_out_of_range(self):
        with self.assertRaises(ValueError):
            CsvReader(self.__path).read_row(3)

    # -----------------------------------------------------------------------

    def test_read_row_zero_raises(self):
        with self.assertRaises(ValueError):
            CsvReader(self.__path).read_row(0)

    # -----------------------------------------------------------------------

    def test_read_row_type_error(self):
        with self.assertRaises(TypeError):
            CsvReader(self.__path).read_row("1")
        with self.assertRaises(TypeError):
            CsvReader(self.__path).read_row(None)

# ---------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main()
