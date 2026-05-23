"""
:filename: test_settings.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Unit tests for aviss.settings module.

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

from aviss.settings import AViSSSyncSettings
from aviss.settings import AViSSOutputSettings
from aviss.settings import AViSSSettings

# ---------------------------------------------------------------------------


class TestAViSSSyncSettings(unittest.TestCase):

    def setUp(self):
        self.__s = AViSSSyncSettings()

    # -----------------------------------------------------------------------

    def test_defaults(self):
        self.assertEqual("audio_file",    self.__s.col_audio_file)
        self.assertEqual("audio_clap",    self.__s.col_audio_clap)
        self.assertEqual("video_file",    self.__s.col_video_file)
        self.assertEqual("video_clap",    self.__s.col_video_clap)
        self.assertEqual("video_crop_x",  self.__s.col_video_crop_x)
        self.assertEqual("video_crop_y",  self.__s.col_video_crop_y)
        self.assertEqual("video_crop_w",  self.__s.col_video_crop_w)
        self.assertEqual("video_crop_h",  self.__s.col_video_crop_h)
        self.assertEqual("delay",         self.__s.col_delay)
        self.assertEqual("duration",      self.__s.col_duration)

    # -----------------------------------------------------------------------

    def test_set_col_audio_file(self):
        self.__s.col_audio_file = "my_audio"
        self.assertEqual("my_audio", self.__s.col_audio_file)

    # -----------------------------------------------------------------------

    def test_set_col_audio_file_strips(self):
        self.__s.col_audio_file = "  my_audio  "
        self.assertEqual("my_audio", self.__s.col_audio_file)

    # -----------------------------------------------------------------------

    def test_set_col_audio_file_type_error(self):
        with self.assertRaises(TypeError):
            self.__s.col_audio_file = None
        with self.assertRaises(TypeError):
            self.__s.col_audio_file = ""
        with self.assertRaises(TypeError):
            self.__s.col_audio_file = "   "

    # -----------------------------------------------------------------------

    def test_set_col_audio_clap(self):
        self.__s.col_audio_clap = "my_clap"
        self.assertEqual("my_clap", self.__s.col_audio_clap)

    # -----------------------------------------------------------------------

    def test_set_col_audio_clap_type_error(self):
        with self.assertRaises(TypeError):
            self.__s.col_audio_clap = None
        with self.assertRaises(TypeError):
            self.__s.col_audio_clap = ""

    # -----------------------------------------------------------------------

    def test_set_col_video_file(self):
        self.__s.col_video_file = "my_video"
        self.assertEqual("my_video", self.__s.col_video_file)

    # -----------------------------------------------------------------------

    def test_set_col_video_file_type_error(self):
        with self.assertRaises(TypeError):
            self.__s.col_video_file = None
        with self.assertRaises(TypeError):
            self.__s.col_video_file = ""

    # -----------------------------------------------------------------------

    def test_set_col_video_clap(self):
        self.__s.col_video_clap = "my_vclap"
        self.assertEqual("my_vclap", self.__s.col_video_clap)

    # -----------------------------------------------------------------------

    def test_set_col_video_clap_type_error(self):
        with self.assertRaises(TypeError):
            self.__s.col_video_clap = None
        with self.assertRaises(TypeError):
            self.__s.col_video_clap = ""

    # -----------------------------------------------------------------------

    def test_set_col_video_crop_x(self):
        self.__s.col_video_crop_x = "crop_left"
        self.assertEqual("crop_left", self.__s.col_video_crop_x)

    # -----------------------------------------------------------------------

    def test_set_col_video_crop_x_type_error(self):
        with self.assertRaises(TypeError):
            self.__s.col_video_crop_x = None
        with self.assertRaises(TypeError):
            self.__s.col_video_crop_x = ""

    # -----------------------------------------------------------------------

    def test_set_col_video_crop_y(self):
        self.__s.col_video_crop_y = "crop_top"
        self.assertEqual("crop_top", self.__s.col_video_crop_y)

    # -----------------------------------------------------------------------

    def test_set_col_video_crop_y_type_error(self):
        with self.assertRaises(TypeError):
            self.__s.col_video_crop_y = None
        with self.assertRaises(TypeError):
            self.__s.col_video_crop_y = ""

    # -----------------------------------------------------------------------

    def test_set_col_video_crop_w(self):
        self.__s.col_video_crop_w = "crop_width"
        self.assertEqual("crop_width", self.__s.col_video_crop_w)

    # -----------------------------------------------------------------------

    def test_set_col_video_crop_w_type_error(self):
        with self.assertRaises(TypeError):
            self.__s.col_video_crop_w = None
        with self.assertRaises(TypeError):
            self.__s.col_video_crop_w = ""

    # -----------------------------------------------------------------------

    def test_set_col_video_crop_h(self):
        self.__s.col_video_crop_h = "crop_height"
        self.assertEqual("crop_height", self.__s.col_video_crop_h)

    # -----------------------------------------------------------------------

    def test_set_col_video_crop_h_type_error(self):
        with self.assertRaises(TypeError):
            self.__s.col_video_crop_h = None
        with self.assertRaises(TypeError):
            self.__s.col_video_crop_h = ""

    # -----------------------------------------------------------------------

    def test_set_col_delay(self):
        self.__s.col_delay = "my_delay"
        self.assertEqual("my_delay", self.__s.col_delay)

    # -----------------------------------------------------------------------

    def test_set_col_delay_type_error(self):
        with self.assertRaises(TypeError):
            self.__s.col_delay = None
        with self.assertRaises(TypeError):
            self.__s.col_delay = ""

    # -----------------------------------------------------------------------

    def test_set_col_duration(self):
        self.__s.col_duration = "my_duration"
        self.assertEqual("my_duration", self.__s.col_duration)

    # -----------------------------------------------------------------------

    def test_set_col_duration_type_error(self):
        with self.assertRaises(TypeError):
            self.__s.col_duration = None
        with self.assertRaises(TypeError):
            self.__s.col_duration = ""

# ---------------------------------------------------------------------------


class TestAViSSOutputSettings(unittest.TestCase):

    def setUp(self):
        self.__s = AViSSOutputSettings()

    # -----------------------------------------------------------------------

    def test_defaults(self):
        self.assertEqual("_",  self.__s.output_sep)
        self.assertEqual(18,   self.__s.crf)
        self.assertEqual(50.,  self.__s.video_fps)
        self.assertIsNone(self.__s.copyright)
        self.assertEqual("",   self.__s.work_dir_suffix)
        self.assertEqual(5,    len(self.__s.output_name_cols))
        self.assertEqual(("ID", "", None), self.__s.output_name_cols[0])

    # -----------------------------------------------------------------------

    def test_set_output_sep(self):
        self.__s.output_sep = "-"
        self.assertEqual("-", self.__s.output_sep)

    # -----------------------------------------------------------------------

    def test_set_output_sep_empty_allowed(self):
        self.__s.output_sep = ""
        self.assertEqual("", self.__s.output_sep)

    # -----------------------------------------------------------------------

    def test_set_output_sep_type_error(self):
        with self.assertRaises(TypeError):
            self.__s.output_sep = None
        with self.assertRaises(TypeError):
            self.__s.output_sep = 42

    # -----------------------------------------------------------------------

    def test_set_output_name_cols_valid(self):
        cols = [("ID", "", None), ("Session", "S", "02d")]
        self.__s.output_name_cols = cols
        self.assertEqual(cols, self.__s.output_name_cols)

    # -----------------------------------------------------------------------

    def test_set_output_name_cols_type_error_not_list(self):
        with self.assertRaises(TypeError):
            self.__s.output_name_cols = "bad"

    # -----------------------------------------------------------------------

    def test_set_output_name_cols_type_error_empty(self):
        with self.assertRaises(TypeError):
            self.__s.output_name_cols = []

    # -----------------------------------------------------------------------

    def test_set_output_name_cols_type_error_bad_entry(self):
        with self.assertRaises(TypeError):
            self.__s.output_name_cols = [("ID", "", None), "bad"]

    # -----------------------------------------------------------------------

    def test_set_output_name_cols_type_error_bad_col(self):
        with self.assertRaises(TypeError):
            self.__s.output_name_cols = [("", "", None)]

    # -----------------------------------------------------------------------

    def test_set_output_name_cols_type_error_bad_prefix(self):
        with self.assertRaises(TypeError):
            self.__s.output_name_cols = [("ID", None, None)]

    # -----------------------------------------------------------------------

    def test_set_output_name_cols_type_error_bad_fmt(self):
        with self.assertRaises(TypeError):
            self.__s.output_name_cols = [("ID", "", 42)]

    # -----------------------------------------------------------------------

    def test_set_crf_valid(self):
        self.__s.crf = 0
        self.assertEqual(0, self.__s.crf)
        self.__s.crf = 51
        self.assertEqual(51, self.__s.crf)

    # -----------------------------------------------------------------------

    def test_set_crf_type_error(self):
        with self.assertRaises(TypeError):
            self.__s.crf = 18.0
        with self.assertRaises(TypeError):
            self.__s.crf = "18"

    # -----------------------------------------------------------------------

    def test_set_crf_value_error(self):
        with self.assertRaises(ValueError):
            self.__s.crf = -1
        with self.assertRaises(ValueError):
            self.__s.crf = 52

    # -----------------------------------------------------------------------

    def test_set_video_fps_valid(self):
        self.__s.video_fps = 25
        self.assertAlmostEqual(25., self.__s.video_fps, places=3)

    # -----------------------------------------------------------------------

    def test_set_video_fps_type_error(self):
        with self.assertRaises(TypeError):
            self.__s.video_fps = "25"
        with self.assertRaises(TypeError):
            self.__s.video_fps = None

    # -----------------------------------------------------------------------

    def test_set_video_fps_value_error(self):
        with self.assertRaises(ValueError):
            self.__s.video_fps = 0.
        with self.assertRaises(ValueError):
            self.__s.video_fps = -1.

    # -----------------------------------------------------------------------

    def test_set_copyright_valid(self):
        self.__s.copyright = "Copyright (C) 2026 CNRS"
        self.assertEqual("Copyright (C) 2026 CNRS", self.__s.copyright)

    # -----------------------------------------------------------------------

    def test_set_copyright_none(self):
        self.__s.copyright = "Copyright (C) 2026 CNRS"
        self.__s.copyright = None
        self.assertIsNone(self.__s.copyright)

    # -----------------------------------------------------------------------

    def test_set_copyright_type_error(self):
        with self.assertRaises(TypeError):
            self.__s.copyright = 42

    # -----------------------------------------------------------------------

    def test_set_work_dir_suffix_valid(self):
        self.__s.work_dir_suffix = "_out"
        self.assertEqual("_out", self.__s.work_dir_suffix)

    # -----------------------------------------------------------------------

    def test_set_work_dir_suffix_empty_allowed(self):
        self.__s.work_dir_suffix = ""
        self.assertEqual("", self.__s.work_dir_suffix)

    # -----------------------------------------------------------------------

    def test_set_work_dir_suffix_type_error(self):
        with self.assertRaises(TypeError):
            self.__s.work_dir_suffix = None
        with self.assertRaises(TypeError):
            self.__s.work_dir_suffix = 42

# ---------------------------------------------------------------------------


class TestAViSSSettings(unittest.TestCase):

    # -----------------------------------------------------------------------

    def test_sync_is_accessible(self):
        settings = AViSSSettings()
        self.assertIsInstance(settings.sync, AViSSSyncSettings)

    # -----------------------------------------------------------------------

    def test_output_is_accessible(self):
        settings = AViSSSettings()
        self.assertIsInstance(settings.output, AViSSOutputSettings)

    # -----------------------------------------------------------------------

    def test_context_manager(self):
        with AViSSSettings() as settings:
            self.assertIsInstance(settings.sync, AViSSSyncSettings)
            self.assertIsInstance(settings.output, AViSSOutputSettings)

    # -----------------------------------------------------------------------

    def test_load_user_settings_exception_is_caught(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad_file = os.path.join(tmp, "settings_user.toml")
            with open(bad_file, "w") as fh:
                fh.write("[output\n")
            settings = AViSSSettings()
            settings.load_user_settings(tmp)
            self.assertIsInstance(settings.sync, AViSSSyncSettings)

    # -----------------------------------------------------------------------

    def test_load_user_settings_applies_overrides(self):
        with tempfile.TemporaryDirectory() as tmp:
            cfg_file = os.path.join(tmp, "settings_user.toml")
            with open(cfg_file, "w") as fh:
                fh.write("[output]\ncrf = 5\n")
            settings = AViSSSettings()
            settings.load_user_settings(tmp)
            self.assertEqual(5, settings.output.crf)

    # -----------------------------------------------------------------------

    def test_load_user_settings_no_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            settings = AViSSSettings()
            settings.load_user_settings(tmp)
            self.assertEqual(18, settings.output.crf)

    # -----------------------------------------------------------------------

    def test_load_user_settings_type_error(self):
        settings = AViSSSettings()
        with self.assertRaises(TypeError):
            settings.load_user_settings("")

# ---------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main()
