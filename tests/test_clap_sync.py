"""
:filename: test_clap_sync.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Unit tests for aviss.core.clap_sync module.

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

from aviss.models import MediaFile
from aviss.models import Session
from aviss.core.clap_sync import ClapSync
from aviss.core.video_ops import VideoOps

# ---------------------------------------------------------------------------

DATA_DIR  = os.path.join(os.path.dirname(__file__), "data")
TEST_MP4  = os.path.join(DATA_DIR, "test_video.mp4")

# ---------------------------------------------------------------------------


class TestClapSyncInit(unittest.TestCase):

    def setUp(self):
        audio = MediaFile("rec.wav", 3.843)
        video = MediaFile("rec.mp4", 6.0)
        self.__session = Session(audio, video, delay=0.0, duration=10.0)

    # -----------------------------------------------------------------------

    def test_type_error_session(self):
        with self.assertRaises(TypeError):
            ClapSync("not_a_session", fps=25.)

    # -----------------------------------------------------------------------

    def test_type_error_fps(self):
        with self.assertRaises(TypeError):
            ClapSync(self.__session, fps="25")

    # -----------------------------------------------------------------------

    def test_value_error_fps_zero(self):
        with self.assertRaises(ValueError):
            ClapSync(self.__session, fps=0.)

    # -----------------------------------------------------------------------

    def test_value_error_fps_negative(self):
        with self.assertRaises(ValueError):
            ClapSync(self.__session, fps=-25.)

    # -----------------------------------------------------------------------

    def test_clap_frame_index(self):
        sync = ClapSync(self.__session, fps=25.)
        self.assertEqual(150, sync.clap_frame_index)

    # -----------------------------------------------------------------------

    def test_clap_frame_time(self):
        sync = ClapSync(self.__session, fps=25.)
        self.assertAlmostEqual(6.0, sync.clap_frame_time, places=6)

    # -----------------------------------------------------------------------

    def test_end_frame_index(self):
        sync = ClapSync(self.__session, fps=25.)
        self.assertEqual(401, sync.end_frame_index)

    # -----------------------------------------------------------------------

    def test_end_frame_time(self):
        sync = ClapSync(self.__session, fps=25.)
        self.assertAlmostEqual(16.04, sync.end_frame_time, places=6)

    # -----------------------------------------------------------------------

    def test_fps_stored(self):
        sync = ClapSync(self.__session, fps=50.)
        self.assertAlmostEqual(50., sync.fps, places=3)

    # -----------------------------------------------------------------------

    def test_fps_int_accepted(self):
        sync = ClapSync(self.__session, fps=25)
        self.assertAlmostEqual(25., sync.fps, places=3)

    # -----------------------------------------------------------------------

    def test_video_clap_overrides_session_video(self):
        # session.video.clap_time = 6.0 → clap_frame_index = 150 at 25fps
        # override with 8.0 → clap_frame_index = 200 at 25fps
        sync = ClapSync(self.__session, fps=25., video_clap=8.0)
        self.assertEqual(200, sync.clap_frame_index)

    # -----------------------------------------------------------------------

    def test_video_clap_type_error(self):
        with self.assertRaises(TypeError):
            ClapSync(self.__session, fps=25., video_clap="bad")

    # -----------------------------------------------------------------------

    def test_video_clap_negative_raises(self):
        with self.assertRaises(ValueError):
            ClapSync(self.__session, fps=25., video_clap=-1.0)

    # -----------------------------------------------------------------------

    def test_clap_delta_is_non_negative(self):
        sync = ClapSync(self.__session, fps=25.)
        self.assertGreaterEqual(sync.clap_delta, 0.)

    # -----------------------------------------------------------------------

    def test_clap_delta_less_than_one_frame(self):
        sync = ClapSync(self.__session, fps=25.)
        self.assertLess(sync.clap_delta, 1. / 25.)

    # -----------------------------------------------------------------------

    def test_reference_delta_cross_sync(self):
        # Reference video: 25fps, video_clap=6.0 → frame 150 → frame_time=6.0 → delta=0.0
        # Secondary video: 60fps, video_clap=8.0, reference_delta=0.0
        # → target = 8.0 - 0.0 = 8.0 → frame int(8.0*60)=480 → delta=0.0
        # Both deltas must be equal (cross-sync).
        audio = MediaFile("rec.wav", 3.843)
        video = MediaFile("rec.mp4", 6.0)
        session = Session(audio, video, delay=0.0, duration=10.0)
        ref_sync = ClapSync(session, fps=25.)
        ref_delta = ref_sync.clap_delta
        other_sync = ClapSync(session, fps=60., video_clap=8.0,
                              reference_delta=ref_delta)
        self.assertAlmostEqual(ref_sync.clap_delta, other_sync.clap_delta, places=6)

    # -----------------------------------------------------------------------

    def test_reference_delta_type_error(self):
        with self.assertRaises(TypeError):
            ClapSync(self.__session, fps=25., reference_delta="bad")

    # -----------------------------------------------------------------------

    def test_reference_delta_negative_raises(self):
        with self.assertRaises(ValueError):
            ClapSync(self.__session, fps=25., reference_delta=-0.1)


# ---------------------------------------------------------------------------


class TestClapSyncWithDelay(unittest.TestCase):

    def setUp(self):
        audio = MediaFile("rec.wav", 3.843)
        video = MediaFile("rec.mp4", 6.41)
        self.__session = Session(audio, video, delay=0.2, duration=10.0)

    # -----------------------------------------------------------------------

    def test_clap_frame_index_with_delay(self):
        sync = ClapSync(self.__session, fps=25.)
        self.assertEqual(165, sync.clap_frame_index)

    # -----------------------------------------------------------------------

    def test_clap_frame_time_with_delay(self):
        sync = ClapSync(self.__session, fps=25.)
        self.assertAlmostEqual(6.6, sync.clap_frame_time, places=6)

    # -----------------------------------------------------------------------

    def test_end_frame_index_with_delay(self):
        sync = ClapSync(self.__session, fps=25.)
        self.assertEqual(416, sync.end_frame_index)

    # -----------------------------------------------------------------------

    def test_end_frame_time_with_delay(self):
        sync = ClapSync(self.__session, fps=25.)
        self.assertAlmostEqual(16.64, sync.end_frame_time, places=6)


# ---------------------------------------------------------------------------


class TestClapSyncProperties(unittest.TestCase):

    def setUp(self):
        audio = MediaFile("rec.wav", 3.843)
        video = MediaFile("rec.mp4", 6.0)
        session = Session(audio, video, delay=0.0, duration=10.0)
        self.__sync = ClapSync(session, fps=25.)

    # -----------------------------------------------------------------------

    def test_audio_reference_clap(self):
        self.assertAlmostEqual(self.__sync.clap_frame_time, self.__sync.audio_reference_clap, places=6)

    # -----------------------------------------------------------------------

    def test_get_audio_clap_with_delay(self):
        result = self.__sync.get_audio_clap_with_delay(3.843)
        self.assertAlmostEqual(3.843, result, places=6)

    # -----------------------------------------------------------------------

    def test_get_audio_clap_with_delay_type_error(self):
        with self.assertRaises(TypeError):
            self.__sync.get_audio_clap_with_delay("bad")

    # -----------------------------------------------------------------------

    def test_check_video_duration_valid(self):
        self.__sync.check_video_duration(300.)

    # -----------------------------------------------------------------------

    def test_check_video_duration_type_error(self):
        with self.assertRaises(TypeError):
            self.__sync.check_video_duration("bad")

    # -----------------------------------------------------------------------

    def test_check_video_duration_value_error(self):
        with self.assertRaises(ValueError):
            self.__sync.check_video_duration(1.)

    # -----------------------------------------------------------------------

    def test_repr(self):
        r = repr(self.__sync)
        self.assertIsInstance(r, str)
        self.assertIn("ClapSync", r)
        self.assertIn("fps=25.0", r)

# ---------------------------------------------------------------------------


class TestClapSyncWithRealVideo(unittest.TestCase):
    """Verify ClapSync built with the actual video fps gives coherent indices.

    This test catches the bug where the pipeline passes cfg.output.video_fps
    (a configured value) instead of the actual fps read from the video file.
    If the fps used to build ClapSync does not match the video's real fps,
    clap_frame_index is inconsistent with the video timeline.

    Values from tests/data/test.csv:
        video_clap = 10.000s, delay = 1.000s → video_clap_with_delay = 11.000s
        duration   = 10.466s

    """

    # video_clap + delay as declared in test.csv
    VIDEO_CLAP_WITH_DELAY = 11.0
    DURATION              = 10.466

    def setUp(self):
        info        = VideoOps.get_video_info(TEST_MP4)
        self.__fps  = info["fps"]
        self.__vdur = info["duration"]
        audio       = MediaFile("rec.wav", 6.0)
        video       = MediaFile(TEST_MP4,  10.0)
        session     = Session(audio, video, delay=1.0, duration=self.DURATION)
        self.__sync = ClapSync(session, self.__fps)

    # -----------------------------------------------------------------------

    def test_clap_frame_index_matches_actual_fps(self):
        # clap_frame_index must equal int(video_clap_with_delay * actual_fps).
        # Fails if a wrong fps (e.g. cfg.output.video_fps) was used instead.
        expected = int(self.VIDEO_CLAP_WITH_DELAY * self.__fps)
        self.assertEqual(expected, self.__sync.clap_frame_index)

    # -----------------------------------------------------------------------

    def test_clap_frame_index_differs_with_wrong_fps(self):
        # Building ClapSync with a fps that does not match the video gives a
        # different clap_frame_index, which would produce a wrong trim.
        wrong_fps  = self.__fps * 2.
        audio      = MediaFile("rec.wav", 6.0)
        video      = MediaFile(TEST_MP4,  10.0)
        session    = Session(audio, video, delay=1.0, duration=self.DURATION)
        sync_wrong = ClapSync(session, wrong_fps)
        self.assertNotEqual(self.__sync.clap_frame_index, sync_wrong.clap_frame_index)

    # -----------------------------------------------------------------------

    def test_end_frame_time_within_video_duration(self):
        self.assertLessEqual(self.__sync.end_frame_time, self.__vdur)

    # -----------------------------------------------------------------------

    def test_clap_frame_time_matches_index(self):
        # clap_frame_time must equal clap_frame_index / actual_fps.
        expected = self.__sync.clap_frame_index / self.__fps
        self.assertAlmostEqual(expected, self.__sync.clap_frame_time, places=6)

# ---------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main()
