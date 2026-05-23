"""
:filename: test_models.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Unit tests for aviss.models module.

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
import tempfile
import unittest

from aviss.models import avMediaFile
from aviss.models import avSession
from aviss.models import avSyncResult

# ---------------------------------------------------------------------------


class TestMediaFile(unittest.TestCase):

    # -----------------------------------------------------------------------

    def test_init_audio(self):
        m = avMediaFile("rec.wav", 3.843)
        self.assertEqual("rec.wav", m.path)
        self.assertAlmostEqual(3.843, m.clap_time, places=3)
        self.assertTrue(m.is_audio())
        self.assertFalse(m.is_video())
        self.assertFalse(m.has_crop())

    # -----------------------------------------------------------------------

    def test_init_video(self):
        m = avMediaFile("rec.mp4", 6.410)
        self.assertEqual("rec.mp4", m.path)
        self.assertAlmostEqual(6.410, m.clap_time, places=3)
        self.assertFalse(m.is_audio())
        self.assertTrue(m.is_video())

    # -----------------------------------------------------------------------

    def test_init_clap_zero(self):
        m = avMediaFile("rec.wav", 0)
        self.assertAlmostEqual(0., m.clap_time, places=3)

    # -----------------------------------------------------------------------

    def test_init_strips_path(self):
        m = avMediaFile("  rec.wav  ", 1.0)
        self.assertEqual("rec.wav", m.path)

    # -----------------------------------------------------------------------

    def test_init_type_error_path(self):
        with self.assertRaises(TypeError):
            avMediaFile(None, 1.0)
        with self.assertRaises(TypeError):
            avMediaFile("", 1.0)
        with self.assertRaises(TypeError):
            avMediaFile(42, 1.0)

    # -----------------------------------------------------------------------

    def test_init_type_error_clap(self):
        with self.assertRaises(TypeError):
            avMediaFile("rec.wav", "1.0")
        with self.assertRaises(TypeError):
            avMediaFile("rec.wav", None)

    # -----------------------------------------------------------------------

    def test_init_value_error_clap_negative(self):
        with self.assertRaises(ValueError):
            avMediaFile("rec.wav", -1.0)

    # -----------------------------------------------------------------------

    def test_set_path_valid(self):
        m = avMediaFile("rec.wav", 1.0)
        m.path = "other.wav"
        self.assertEqual("other.wav", m.path)

    # -----------------------------------------------------------------------

    def test_set_path_change_type(self):
        m = avMediaFile("rec.wav", 1.0)
        m.path = "rec.mp4"
        self.assertTrue(m.is_video())
        self.assertFalse(m.is_audio())

    # -----------------------------------------------------------------------

    def test_set_path_type_error(self):
        m = avMediaFile("rec.wav", 1.0)
        with self.assertRaises(TypeError):
            m.path = ""
        with self.assertRaises(TypeError):
            m.path = None

    # -----------------------------------------------------------------------

    def test_set_clap_time_valid(self):
        m = avMediaFile("rec.wav", 1.0)
        m.clap_time = 5.5
        self.assertAlmostEqual(5.5, m.clap_time, places=3)

    # -----------------------------------------------------------------------

    def test_set_clap_time_zero(self):
        m = avMediaFile("rec.wav", 1.0)
        m.clap_time = 0
        self.assertAlmostEqual(0., m.clap_time, places=3)

    # -----------------------------------------------------------------------

    def test_set_clap_time_type_error(self):
        m = avMediaFile("rec.wav", 1.0)
        with self.assertRaises(TypeError):
            m.clap_time = "1.0"

    # -----------------------------------------------------------------------

    def test_set_clap_time_negative(self):
        m = avMediaFile("rec.wav", 1.0)
        with self.assertRaises(ValueError):
            m.clap_time = -0.001

    # -----------------------------------------------------------------------

    def test_crop_not_set_by_default(self):
        m = avMediaFile("rec.mp4", 1.0)
        self.assertIsNone(m.crop_x)
        self.assertIsNone(m.crop_y)
        self.assertIsNone(m.crop_w)
        self.assertIsNone(m.crop_h)
        self.assertFalse(m.has_crop())

    # -----------------------------------------------------------------------

    def test_crop_full_set(self):
        m = avMediaFile("rec.mp4", 1.0)
        m.crop_x = 0
        m.crop_y = 32
        m.crop_w = 1600
        m.crop_h = 960
        self.assertTrue(m.has_crop())
        self.assertEqual(0,    m.crop_x)
        self.assertEqual(32,   m.crop_y)
        self.assertEqual(1600, m.crop_w)
        self.assertEqual(960,  m.crop_h)

    # -----------------------------------------------------------------------

    def test_crop_partial_is_not_crop(self):
        m = avMediaFile("rec.mp4", 1.0)
        m.crop_x = 0
        m.crop_y = 32
        self.assertFalse(m.has_crop())

    # -----------------------------------------------------------------------

    def test_crop_unset_with_none(self):
        m = avMediaFile("rec.mp4", 1.0)
        m.crop_x = 10
        m.crop_x = None
        self.assertIsNone(m.crop_x)
        self.assertFalse(m.has_crop())

    # -----------------------------------------------------------------------

    def test_crop_type_error(self):
        m = avMediaFile("rec.mp4", 1.0)
        with self.assertRaises(TypeError):
            m.crop_x = "0"
        with self.assertRaises(TypeError):
            m.crop_y = 1.5
        with self.assertRaises(TypeError):
            m.crop_w = "100"
        with self.assertRaises(TypeError):
            m.crop_h = 1.5

    # -----------------------------------------------------------------------

    def test_crop_value_error(self):
        m = avMediaFile("rec.mp4", 1.0)
        with self.assertRaises(ValueError):
            m.crop_x = -1
        with self.assertRaises(ValueError):
            m.crop_y = -1
        with self.assertRaises(ValueError):
            m.crop_w = 0
        with self.assertRaises(ValueError):
            m.crop_h = 0

    # -----------------------------------------------------------------------

    def test_exists_false_for_nonexistent(self):
        m = avMediaFile("does_not_exist.wav", 1.0)
        self.assertFalse(m.exists())

    # -----------------------------------------------------------------------

    def test_repr(self):
        m = avMediaFile("rec.wav", 3.843)
        r = repr(m)
        self.assertTrue("rec.wav" in r)
        self.assertTrue("3.843" in r)

# ---------------------------------------------------------------------------


class TestSession(unittest.TestCase):

    def setUp(self):
        self.__audio = avMediaFile("rec.wav", 3.843)
        self.__video = avMediaFile("rec.mp4", 6.410)

    # -----------------------------------------------------------------------

    def test_init(self):
        s = avSession(self.__audio, self.__video, delay=0.2, duration=216.0)
        self.assertEqual(1, len(s.audios))
        self.assertEqual(1, len(s.videos))
        self.assertEqual(1, len(s.video_names))
        self.assertIsNone(s.video_names[0])
        self.assertAlmostEqual(0.2,   s.delay,    places=3)
        self.assertAlmostEqual(216.0, s.duration, places=3)
        self.assertFalse(s.has_second_audio())
        self.assertFalse(s.has_second_video())
        self.assertEqual({}, s.output_name_meta)
        self.assertEqual({}, s.metadata)

    # -----------------------------------------------------------------------

    def test_init_delay_zero(self):
        s = avSession(self.__audio, self.__video, delay=0, duration=10.0)
        self.assertAlmostEqual(0., s.delay, places=3)

    # -----------------------------------------------------------------------

    def test_init_type_error_audio(self):
        with self.assertRaises(TypeError):
            avSession("not_a_media", self.__video, delay=0., duration=10.)
        with self.assertRaises(TypeError):
            avSession(None, self.__video, delay=0., duration=10.)

    # -----------------------------------------------------------------------

    def test_init_value_error_audio_not_audio(self):
        video = avMediaFile("other.mp4", 1.0)
        with self.assertRaises(ValueError):
            avSession(video, self.__video, delay=0., duration=10.)

    # -----------------------------------------------------------------------

    def test_init_type_error_video(self):
        with self.assertRaises(TypeError):
            avSession(self.__audio, "not_a_media", delay=0., duration=10.)

    # -----------------------------------------------------------------------

    def test_init_value_error_video_not_video(self):
        audio = avMediaFile("other.wav", 1.0)
        with self.assertRaises(ValueError):
            avSession(self.__audio, audio, delay=0., duration=10.)

    # -----------------------------------------------------------------------

    def test_init_value_error_duration_zero(self):
        with self.assertRaises(ValueError):
            avSession(self.__audio, self.__video, delay=0., duration=0.)

    # -----------------------------------------------------------------------

    def test_init_value_error_duration_negative(self):
        with self.assertRaises(ValueError):
            avSession(self.__audio, self.__video, delay=0., duration=-1.)

    # -----------------------------------------------------------------------

    def test_init_type_error_delay(self):
        with self.assertRaises(TypeError):
            avSession(self.__audio, self.__video, delay="bad", duration=10.)

    # -----------------------------------------------------------------------

    def test_init_type_error_duration(self):
        with self.assertRaises(TypeError):
            avSession(self.__audio, self.__video, delay=0., duration="bad")

    # -----------------------------------------------------------------------

    def test_add_audio_valid(self):
        s = avSession(self.__audio, self.__video, delay=0., duration=10.)
        audio2 = avMediaFile("rec2.wav", 2.0)
        s.add_audio(audio2)
        self.assertEqual(2, len(s.audios))
        self.assertTrue(s.has_second_audio())
        self.assertIs(audio2, s.audios[1])

    # -----------------------------------------------------------------------

    def test_add_audio_type_error(self):
        s = avSession(self.__audio, self.__video, delay=0., duration=10.)
        with self.assertRaises(TypeError):
            s.add_audio("not_a_media")

    # -----------------------------------------------------------------------

    def test_add_audio_value_error_not_audio(self):
        s = avSession(self.__audio, self.__video, delay=0., duration=10.)
        with self.assertRaises(ValueError):
            s.add_audio(avMediaFile("other.mp4", 1.0))

    # -----------------------------------------------------------------------

    def test_add_video_valid(self):
        s = avSession(self.__audio, self.__video, delay=0., duration=10.)
        video2 = avMediaFile("rec2.mp4", 5.0)
        s.add_video(video2)
        self.assertEqual(2, len(s.videos))
        self.assertTrue(s.has_second_video())
        self.assertIs(video2, s.videos[1])

    # -----------------------------------------------------------------------

    def test_add_video_with_name(self):
        s = avSession(self.__audio, self.__video, delay=0., duration=10.)
        video2 = avMediaFile("rec2.mp4", 5.0)
        s.add_video(video2, name="side")
        self.assertEqual("side", s.video_names[1])

    # -----------------------------------------------------------------------

    def test_add_video_type_error(self):
        s = avSession(self.__audio, self.__video, delay=0., duration=10.)
        with self.assertRaises(TypeError):
            s.add_video("not_a_media")

    # -----------------------------------------------------------------------

    def test_add_video_value_error_not_video(self):
        s = avSession(self.__audio, self.__video, delay=0., duration=10.)
        with self.assertRaises(ValueError):
            s.add_video(avMediaFile("other.wav", 1.0))

    # -----------------------------------------------------------------------

    def test_add_video_name_type_error(self):
        s = avSession(self.__audio, self.__video, delay=0., duration=10.)
        video2 = avMediaFile("rec2.mp4", 5.0)
        with self.assertRaises(TypeError):
            s.add_video(video2, name="")

    # -----------------------------------------------------------------------

    def test_set_video_name_valid(self):
        s = avSession(self.__audio, self.__video, delay=0., duration=10.)
        s.set_video_name(0, "front")
        self.assertEqual("front", s.video_names[0])

    # -----------------------------------------------------------------------

    def test_set_video_name_none(self):
        s = avSession(self.__audio, self.__video, delay=0., duration=10.)
        s.set_video_name(0, "front")
        s.set_video_name(0, None)
        self.assertIsNone(s.video_names[0])

    # -----------------------------------------------------------------------

    def test_set_video_name_index_error(self):
        s = avSession(self.__audio, self.__video, delay=0., duration=10.)
        with self.assertRaises(IndexError):
            s.set_video_name(5, "x")

    # -----------------------------------------------------------------------

    def test_set_delay(self):
        s = avSession(self.__audio, self.__video, delay=0., duration=10.)
        s.delay = 0.5
        self.assertAlmostEqual(0.5, s.delay, places=3)

    # -----------------------------------------------------------------------

    def test_set_delay_type_error(self):
        s = avSession(self.__audio, self.__video, delay=0., duration=10.)
        with self.assertRaises(TypeError):
            s.delay = "0.5"

    # -----------------------------------------------------------------------

    def test_set_duration_valid(self):
        s = avSession(self.__audio, self.__video, delay=0., duration=10.)
        s.duration = 216.0
        self.assertAlmostEqual(216.0, s.duration, places=3)

    # -----------------------------------------------------------------------

    def test_set_duration_value_error(self):
        s = avSession(self.__audio, self.__video, delay=0., duration=10.)
        with self.assertRaises(ValueError):
            s.duration = 0.
        with self.assertRaises(ValueError):
            s.duration = -1.

    # -----------------------------------------------------------------------

    def test_set_duration_type_error(self):
        s = avSession(self.__audio, self.__video, delay=0., duration=10.)
        with self.assertRaises(TypeError):
            s.duration = "bad"

    # -----------------------------------------------------------------------

    def test_output_name_meta(self):
        s = avSession(self.__audio, self.__video, delay=0., duration=10.)
        meta = {"ID": "Laurent", "Session": "9"}
        s.output_name_meta = meta
        self.assertEqual(meta, s.output_name_meta)

    # -----------------------------------------------------------------------

    def test_output_name_meta_type_error(self):
        s = avSession(self.__audio, self.__video, delay=0., duration=10.)
        with self.assertRaises(TypeError):
            s.output_name_meta = [("ID", "Laurent")]

    # -----------------------------------------------------------------------

    def test_metadata(self):
        s = avSession(self.__audio, self.__video, delay=0., duration=10.)
        s.metadata = {"handedness": "r", "gender": "m"}
        self.assertEqual("r", s.metadata["handedness"])

    # -----------------------------------------------------------------------

    def test_metadata_type_error(self):
        s = avSession(self.__audio, self.__video, delay=0., duration=10.)
        with self.assertRaises(TypeError):
            s.metadata = "not_a_dict"

    # -----------------------------------------------------------------------

    def test_all_files_exist_false(self):
        s = avSession(self.__audio, self.__video, delay=0., duration=10.)
        self.assertFalse(s.all_files_exist())

    # -----------------------------------------------------------------------

    def test_all_files_exist_true(self):
        with tempfile.TemporaryDirectory() as tmp:
            audio_path = os.path.join(tmp, "rec.wav")
            video_path = os.path.join(tmp, "rec.mp4")
            open(audio_path, "w").close()
            open(video_path, "w").close()
            audio = avMediaFile(audio_path, 1.0)
            video = avMediaFile(video_path, 2.0)
            s = avSession(audio, video, delay=0., duration=10.)
            self.assertTrue(s.all_files_exist())

    # -----------------------------------------------------------------------

    def test_repr(self):
        s = avSession(self.__audio, self.__video, delay=0.2, duration=216.0)
        r = repr(s)
        self.assertTrue("1 audio" in r)
        self.assertTrue("1 video" in r)

# ---------------------------------------------------------------------------


class TestSyncResult(unittest.TestCase):

    # -----------------------------------------------------------------------

    def test_init(self):
        r = avSyncResult()
        self.assertFalse(r.success)
        self.assertEqual([], r.synced_files)
        self.assertIsNone(r.montage_file)
        self.assertEqual([], r.report)

    # -----------------------------------------------------------------------

    def test_add_synced_file(self):
        r = avSyncResult()
        r.add_synced_file("/out/Laurent_S09.wav")
        r.add_synced_file("/out/Laurent_S09.mkv")
        self.assertEqual(2, len(r.synced_files))
        self.assertEqual("/out/Laurent_S09.wav", r.synced_files[0])

    # -----------------------------------------------------------------------

    def test_add_synced_file_type_error(self):
        r = avSyncResult()
        with self.assertRaises(TypeError):
            r.add_synced_file(None)
        with self.assertRaises(TypeError):
            r.add_synced_file("")

    # -----------------------------------------------------------------------

    def test_set_montage_file(self):
        r = avSyncResult()
        r.montage_file = "/out/Laurent_S09-av.mp4"
        self.assertEqual("/out/Laurent_S09-av.mp4", r.montage_file)

    # -----------------------------------------------------------------------

    def test_set_montage_file_none(self):
        r = avSyncResult()
        r.montage_file = "/out/Laurent_S09-av.mp4"
        r.montage_file = None
        self.assertIsNone(r.montage_file)

    # -----------------------------------------------------------------------

    def test_set_montage_file_type_error(self):
        r = avSyncResult()
        with self.assertRaises(TypeError):
            r.montage_file = ""
        with self.assertRaises(TypeError):
            r.montage_file = 42

    # -----------------------------------------------------------------------

    def test_set_success(self):
        r = avSyncResult()
        r.success = True
        self.assertTrue(r.success)
        r.success = False
        self.assertFalse(r.success)

    # -----------------------------------------------------------------------

    def test_set_success_type_error(self):
        r = avSyncResult()
        with self.assertRaises(TypeError):
            r.success = 1
        with self.assertRaises(TypeError):
            r.success = "True"

    # -----------------------------------------------------------------------

    def test_add_message(self):
        r = avSyncResult()
        r.add_message("Step 0: done.")
        r.add_message("Step 1: done.")
        self.assertEqual(2, len(r.report))
        self.assertEqual("Step 0: done.", r.report[0])

    # -----------------------------------------------------------------------

    def test_add_message_type_error(self):
        r = avSyncResult()
        with self.assertRaises(TypeError):
            r.add_message(None)
        with self.assertRaises(TypeError):
            r.add_message(42)

    # -----------------------------------------------------------------------

    def test_repr(self):
        r = avSyncResult()
        r.add_synced_file("/out/Laurent_S09.wav")
        r.success = True
        rep = repr(r)
        self.assertTrue("OK" in rep)
        self.assertTrue("1" in rep)

# ---------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main()
