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

from aviss.models import avMediaFile
from aviss.models import avSession
from aviss.core.clap_sync import avClapSync
from aviss.core.video_ops import avVideoOps

# ---------------------------------------------------------------------------

DATA_DIR  = os.path.join(os.path.dirname(__file__), "data")
TEST_MP4  = os.path.join(DATA_DIR, "test_video.mp4")

# ---------------------------------------------------------------------------


class TestClapSyncInit(unittest.TestCase):

    def setUp(self):
        audio = avMediaFile("rec.wav", 3.843)
        video = avMediaFile("rec.mp4", 6.0)
        self.__session = avSession(audio, video, delay=0.0, duration=10.0)

    # -----------------------------------------------------------------------

    def test_type_error_session(self):
        with self.assertRaises(TypeError):
            avClapSync("not_a_session", fps=25.)

    # -----------------------------------------------------------------------

    def test_type_error_fps(self):
        with self.assertRaises(TypeError):
            avClapSync(self.__session, fps="25")

    # -----------------------------------------------------------------------

    def test_value_error_fps_zero(self):
        with self.assertRaises(ValueError):
            avClapSync(self.__session, fps=0.)

    # -----------------------------------------------------------------------

    def test_value_error_fps_negative(self):
        with self.assertRaises(ValueError):
            avClapSync(self.__session, fps=-25.)

    # -----------------------------------------------------------------------

    def test_clap_frame_index(self):
        sync = avClapSync(self.__session, fps=25.)
        self.assertEqual(150, sync.clap_frame_index)

    # -----------------------------------------------------------------------

    def test_clap_frame_time(self):
        sync = avClapSync(self.__session, fps=25.)
        self.assertAlmostEqual(6.0, sync.clap_frame_time, places=6)

    # -----------------------------------------------------------------------

    def test_end_frame_index(self):
        sync = avClapSync(self.__session, fps=25.)
        self.assertEqual(401, sync.end_frame_index)

    # -----------------------------------------------------------------------

    def test_end_frame_time(self):
        sync = avClapSync(self.__session, fps=25.)
        self.assertAlmostEqual(16.04, sync.end_frame_time, places=6)

    # -----------------------------------------------------------------------

    def test_fps_stored(self):
        sync = avClapSync(self.__session, fps=50.)
        self.assertAlmostEqual(50., sync.fps, places=3)

    # -----------------------------------------------------------------------

    def test_fps_int_accepted(self):
        sync = avClapSync(self.__session, fps=25)
        self.assertAlmostEqual(25., sync.fps, places=3)

    # -----------------------------------------------------------------------

    def test_video_clap_overrides_session_video(self):
        # session.video.clap_time = 6.0 → clap_frame_index = 150 at 25fps
        # override with 8.0 → clap_frame_index = 200 at 25fps
        sync = avClapSync(self.__session, fps=25., video_clap=8.0)
        self.assertEqual(200, sync.clap_frame_index)

    # -----------------------------------------------------------------------

    def test_video_clap_type_error(self):
        with self.assertRaises(TypeError):
            avClapSync(self.__session, fps=25., video_clap="bad")

    # -----------------------------------------------------------------------

    def test_video_clap_negative_raises(self):
        with self.assertRaises(ValueError):
            avClapSync(self.__session, fps=25., video_clap=-1.0)

    # -----------------------------------------------------------------------

    def test_clap_delta_is_non_negative(self):
        sync = avClapSync(self.__session, fps=25.)
        self.assertGreaterEqual(sync.clap_delta, 0.)

    # -----------------------------------------------------------------------

    def test_clap_delta_less_than_one_frame(self):
        sync = avClapSync(self.__session, fps=25.)
        self.assertLess(sync.clap_delta, 1. / 25.)

    # -----------------------------------------------------------------------

    def test_reference_delta_cross_sync(self):
        # Reference video: 25fps, video_clap=6.0 → frame 150 → frame_time=6.0 → delta=0.0
        # Secondary video: 60fps, video_clap=8.0, reference_delta=0.0
        # → target = 8.0 - 0.0 = 8.0 → frame int(8.0*60)=480 → delta=0.0
        # Both deltas must be equal (cross-sync).
        audio = avMediaFile("rec.wav", 3.843)
        video = avMediaFile("rec.mp4", 6.0)
        session = avSession(audio, video, delay=0.0, duration=10.0)
        ref_sync = avClapSync(session, fps=25.)
        ref_delta = ref_sync.clap_delta
        other_sync = avClapSync(session, fps=60., video_clap=8.0,
                              reference_delta=ref_delta)
        self.assertAlmostEqual(ref_sync.clap_delta, other_sync.clap_delta, places=6)

    # -----------------------------------------------------------------------

    def test_reference_delta_type_error(self):
        with self.assertRaises(TypeError):
            avClapSync(self.__session, fps=25., reference_delta="bad")

    # -----------------------------------------------------------------------

    def test_reference_delta_negative_raises(self):
        with self.assertRaises(ValueError):
            avClapSync(self.__session, fps=25., reference_delta=-0.1)


# ---------------------------------------------------------------------------


class TestClapSyncWithDelay(unittest.TestCase):

    def setUp(self):
        audio = avMediaFile("rec.wav", 3.843)
        video = avMediaFile("rec.mp4", 6.41)
        self.__session = avSession(audio, video, delay=0.2, duration=10.0)

    # -----------------------------------------------------------------------

    def test_clap_frame_index_with_delay(self):
        sync = avClapSync(self.__session, fps=25.)
        self.assertEqual(165, sync.clap_frame_index)

    # -----------------------------------------------------------------------

    def test_clap_frame_time_with_delay(self):
        sync = avClapSync(self.__session, fps=25.)
        self.assertAlmostEqual(6.6, sync.clap_frame_time, places=6)

    # -----------------------------------------------------------------------

    def test_end_frame_index_with_delay(self):
        sync = avClapSync(self.__session, fps=25.)
        self.assertEqual(416, sync.end_frame_index)

    # -----------------------------------------------------------------------

    def test_end_frame_time_with_delay(self):
        sync = avClapSync(self.__session, fps=25.)
        self.assertAlmostEqual(16.64, sync.end_frame_time, places=6)


# ---------------------------------------------------------------------------


class TestClapSyncProperties(unittest.TestCase):

    def setUp(self):
        audio = avMediaFile("rec.wav", 3.843)
        video = avMediaFile("rec.mp4", 6.0)
        session = avSession(audio, video, delay=0.0, duration=10.0)
        self.__sync = avClapSync(session, fps=25.)

    # -----------------------------------------------------------------------

    def test_audio_reference_clap_equals_video_clap_with_delay(self):
        # audio_reference_clap is video_clap + delay, not the frame-snapped time.
        # Here video_clap=6.0, delay=0.0 → both happen to coincide with frame boundary.
        self.assertAlmostEqual(6.0, self.__sync.audio_reference_clap, places=6)

    def test_audio_reference_clap_non_boundary(self):
        # With a sub-frame clap, audio_reference_clap must differ from clap_frame_time.
        audio   = avMediaFile("rec.wav", 3.843)
        video   = avMediaFile("rec.mp4", 6.05)
        session = avSession(audio, video, delay=0.0, duration=10.0)
        sync    = avClapSync(session, fps=25.)
        self.assertAlmostEqual(6.04, sync.clap_frame_time, places=6)
        self.assertAlmostEqual(6.05, sync.audio_reference_clap, places=6)
        self.assertGreater(sync.audio_reference_clap, sync.clap_frame_time)

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
        self.assertIn("avClapSync", r)
        self.assertIn("fps=25.0", r)

# ---------------------------------------------------------------------------


class TestClapSyncWithRealVideo(unittest.TestCase):
    """Verify avClapSync built with the actual video fps gives coherent indices.

    This test catches the bug where the pipeline passes cfg.output.video_fps
    (a configured value) instead of the actual fps read from the video file.
    If the fps used to build avClapSync does not match the video's real fps,
    clap_frame_index is inconsistent with the video timeline.

    Values from tests/data/test.csv:
        video_clap = 10.000s, delay = 1.000s → video_clap_with_delay = 11.000s
        duration   = 10.466s

    """

    # video_clap + delay as declared in test.csv
    VIDEO_CLAP_WITH_DELAY = 11.0
    DURATION              = 10.466

    def setUp(self):
        info        = avVideoOps.get_video_info(TEST_MP4)
        self.__fps  = info["fps"]
        self.__vdur = info["duration"]
        audio       = avMediaFile("rec.wav", 6.0)
        video       = avMediaFile(TEST_MP4,  10.0)
        session     = avSession(audio, video, delay=1.0, duration=self.DURATION)
        self.__sync = avClapSync(session, self.__fps)

    # -----------------------------------------------------------------------

    def test_clap_frame_index_matches_actual_fps(self):
        # clap_frame_index must equal int(video_clap_with_delay * actual_fps).
        # Fails if a wrong fps (e.g. cfg.output.video_fps) was used instead.
        expected = int(self.VIDEO_CLAP_WITH_DELAY * self.__fps)
        self.assertEqual(expected, self.__sync.clap_frame_index)

    # -----------------------------------------------------------------------

    def test_clap_frame_index_differs_with_wrong_fps(self):
        # Building avClapSync with a fps that does not match the video gives a
        # different clap_frame_index, which would produce a wrong trim.
        wrong_fps  = self.__fps * 2.
        audio      = avMediaFile("rec.wav", 6.0)
        video      = avMediaFile(TEST_MP4,  10.0)
        session    = avSession(audio, video, delay=1.0, duration=self.DURATION)
        sync_wrong = avClapSync(session, wrong_fps)
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


class TestClapSyncCrossSync(unittest.TestCase):
    """Verify the cross-sync formulas match the original montage scripts exactly.

    Original script (montage.py, 2021):
        shift_frames     = int(reference_delta * fps2)
        clap_frame_index = int(vc2 * fps2) - shift_frames
        end_frame_index  = 1 + int((vc2 + dur) * fps2) + shift_frames

    This differs from int((vc2 - reference_delta) * fps2) when
    frac(vc2 * fps2) < frac(reference_delta * fps2), producing
    a 1-frame error in clap alignment.

    Concrete values used here:
        Reference: fps=25, vc=6.1
            clap_frame_index = int(6.1*25)    = 152
            clap_frame_time  = 152/25         = 6.08
            clap_delta       = 6.1 - 6.08     = 0.02
        Secondary: fps=60, vc2=8.1
            frac(8.1*60)  = frac(486.0) = 0.0
            frac(0.02*60) = frac(1.2)   = 0.2
            0.0 < 0.2 => int(A)-int(B) != int(A-B)
            Correct : int(486) - int(1) = 485
            Wrong   : int(484.8)        = 484

    """

    def setUp(self):
        audio = avMediaFile("rec.wav", 3.843)
        video = avMediaFile("ref.mp4", 6.1)
        self.__session  = avSession(audio, video, delay=0.0, duration=10.0)
        self.__ref_sync = avClapSync(self.__session, fps=25.)
        self.__ref_delta = self.__ref_sync.clap_delta
        self.__sec_sync = avClapSync(self.__session, fps=60., video_clap=8.1,
                                   reference_delta=self.__ref_delta)

    # -----------------------------------------------------------------------

    def test_reference_delta_is_exactly_002(self):
        self.assertAlmostEqual(6.08, self.__ref_sync.clap_frame_time, places=10)
        self.assertAlmostEqual(0.02, self.__ref_delta, places=10)

    # -----------------------------------------------------------------------

    def test_cross_sync_clap_frame_index_original_formula(self):
        self.assertEqual(485, self.__sec_sync.clap_frame_index)
        self.assertNotEqual(484, self.__sec_sync.clap_frame_index)

    # -----------------------------------------------------------------------

    def test_cross_sync_end_frame_index_original_formula(self):
        self.assertEqual(1, int(self.__ref_delta * 60))
        self.assertEqual(1088, self.__sec_sync.end_frame_index)

    # -----------------------------------------------------------------------

    def test_cross_sync_zero_delta_both_formulas_agree(self):
        # When reference_delta=0.0, int(A)-0 == int(A-0) — trivial case.
        # vc=6.0 at 25fps lands exactly on a frame boundary => delta=0.0.
        audio   = avMediaFile("rec.wav", 3.843)
        video   = avMediaFile("ref.mp4", 6.0)
        session = avSession(audio, video, delay=0.0, duration=10.0)
        ref_sync = avClapSync(session, fps=25.)
        sec_sync = avClapSync(session, fps=60., video_clap=8.0,
                            reference_delta=ref_sync.clap_delta)
        self.assertEqual(480, sec_sync.clap_frame_index)


# ---------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main()
