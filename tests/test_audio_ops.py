"""
:filename: test_audio_ops.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Unit tests for aviss.core.audio_ops module.

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
import shutil
import tempfile
import unittest

from aviss.core.audio_ops import AudioOps

# ---------------------------------------------------------------------------

DATA_DIR  = os.path.join(os.path.dirname(__file__), "data")
TEST_WAV  = os.path.join(DATA_DIR, "test_audio.wav")
TEST_MP4  = os.path.join(DATA_DIR, "test_video.mp4")

# ---------------------------------------------------------------------------


class TestGetAudioInfo(unittest.TestCase):

    # -----------------------------------------------------------------------

    def test_returns_expected_keys(self):
        info = AudioOps.get_audio_info(TEST_WAV)
        self.assertIn("framerate",  info)
        self.assertIn("nchannels",  info)
        self.assertIn("sampwidth",  info)
        self.assertIn("duration",   info)

    # -----------------------------------------------------------------------

    def test_duration_is_positive(self):
        info = AudioOps.get_audio_info(TEST_WAV)
        self.assertGreater(info["duration"], 0.)

    # -----------------------------------------------------------------------

    def test_framerate_is_positive(self):
        info = AudioOps.get_audio_info(TEST_WAV)
        self.assertGreater(info["framerate"], 0)

    # -----------------------------------------------------------------------

    def test_type_error_non_string(self):
        with self.assertRaises(TypeError):
            AudioOps.get_audio_info(None)
        with self.assertRaises(TypeError):
            AudioOps.get_audio_info(42)

    # -----------------------------------------------------------------------

    def test_type_error_empty_string(self):
        with self.assertRaises(TypeError):
            AudioOps.get_audio_info("   ")

    # -----------------------------------------------------------------------

    def test_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            AudioOps.get_audio_info("/nonexistent/path/rec.wav")

# ---------------------------------------------------------------------------


class TestAudioDuration(unittest.TestCase):

    # -----------------------------------------------------------------------

    def test_returns_positive_float(self):
        duration = AudioOps.audio_duration(TEST_WAV)
        self.assertIsInstance(duration, float)
        self.assertGreater(duration, 0.)

    # -----------------------------------------------------------------------

    def test_consistent_with_get_audio_info(self):
        info     = AudioOps.get_audio_info(TEST_WAV)
        duration = AudioOps.audio_duration(TEST_WAV)
        self.assertAlmostEqual(info["duration"], duration, places=3)

    # -----------------------------------------------------------------------

    def test_type_error_non_string(self):
        with self.assertRaises(TypeError):
            AudioOps.audio_duration(None)

    # -----------------------------------------------------------------------

    def test_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            AudioOps.audio_duration("/nonexistent/path/rec.wav")

# ---------------------------------------------------------------------------


class TestExtractAudioFromVideo(unittest.TestCase):

    def setUp(self):
        self.__tmp_dir  = tempfile.mkdtemp()
        # Synthetic 2-second video with a sine audio track.
        self.__test_mp4 = os.path.join(self.__tmp_dir, "synth.mp4")
        from aviss.utils import run_command
        run_command(
            f"ffmpeg -f lavfi -i testsrc=duration=2:size=64x64:rate=25 "
            f"-f lavfi -i sine=frequency=440:duration=2 "
            f"-c:v libx264 -c:a aac "
            f"'{self.__test_mp4}' -nostdin -y"
        )

    def tearDown(self):
        shutil.rmtree(self.__tmp_dir, ignore_errors=True)

    # -----------------------------------------------------------------------

    def test_creates_wav_file(self):
        audio_out = os.path.join(self.__tmp_dir, "extracted.wav")
        AudioOps.extract_audio_from_video(self.__test_mp4, audio_out)
        self.assertTrue(os.path.isfile(audio_out))
        self.assertGreater(os.path.getsize(audio_out), 0)

    # -----------------------------------------------------------------------

    def test_extracted_audio_is_readable(self):
        audio_out = os.path.join(self.__tmp_dir, "extracted.wav")
        AudioOps.extract_audio_from_video(self.__test_mp4, audio_out)
        info = AudioOps.get_audio_info(audio_out)
        self.assertGreater(info["duration"], 0.)

    # -----------------------------------------------------------------------

    def test_type_error_video_path(self):
        audio_out = os.path.join(self.__tmp_dir, "out.wav")
        with self.assertRaises(TypeError):
            AudioOps.extract_audio_from_video(None, audio_out)
        with self.assertRaises(TypeError):
            AudioOps.extract_audio_from_video("", audio_out)

    # -----------------------------------------------------------------------

    def test_type_error_audio_out(self):
        with self.assertRaises(TypeError):
            AudioOps.extract_audio_from_video(self.__test_mp4, None)
        with self.assertRaises(TypeError):
            AudioOps.extract_audio_from_video(self.__test_mp4, "")

    # -----------------------------------------------------------------------

    def test_file_not_found_video(self):
        audio_out = os.path.join(self.__tmp_dir, "out.wav")
        with self.assertRaises(FileNotFoundError):
            AudioOps.extract_audio_from_video("/nonexistent/video.mp4", audio_out)

# ---------------------------------------------------------------------------


class TestTrimAudio(unittest.TestCase):

    def setUp(self):
        self.__tmp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.__tmp_dir, ignore_errors=True)

    # -----------------------------------------------------------------------

    def test_trim_from_beginning_shortens_audio(self):
        audio_out    = os.path.join(self.__tmp_dir, "trimmed.wav")
        original_dur = AudioOps.audio_duration(TEST_WAV)
        trim_dur     = 0.5
        AudioOps.trim_audio(TEST_WAV, trim_dur, audio_out, begin=True)
        result_dur   = AudioOps.audio_duration(audio_out)
        self.assertAlmostEqual(original_dur - trim_dur, result_dur, delta=0.05)

    # -----------------------------------------------------------------------

    def test_trim_from_end_shortens_audio(self):
        audio_out    = os.path.join(self.__tmp_dir, "trimmed_end.wav")
        original_dur = AudioOps.audio_duration(TEST_WAV)
        trim_dur     = 0.5
        AudioOps.trim_audio(TEST_WAV, trim_dur, audio_out, begin=False)
        result_dur   = AudioOps.audio_duration(audio_out)
        self.assertAlmostEqual(original_dur - trim_dur, result_dur, delta=0.05)

    # -----------------------------------------------------------------------

    def test_type_error_audio_in(self):
        audio_out = os.path.join(self.__tmp_dir, "out.wav")
        with self.assertRaises(TypeError):
            AudioOps.trim_audio(None, 1.0, audio_out)
        with self.assertRaises(TypeError):
            AudioOps.trim_audio("", 1.0, audio_out)

    # -----------------------------------------------------------------------

    def test_type_error_audio_out(self):
        with self.assertRaises(TypeError):
            AudioOps.trim_audio(TEST_WAV, 1.0, None)
        with self.assertRaises(TypeError):
            AudioOps.trim_audio(TEST_WAV, 1.0, "")

    # -----------------------------------------------------------------------

    def test_type_error_trim_duration(self):
        audio_out = os.path.join(self.__tmp_dir, "out.wav")
        with self.assertRaises(TypeError):
            AudioOps.trim_audio(TEST_WAV, "1.0", audio_out)
        with self.assertRaises(TypeError):
            AudioOps.trim_audio(TEST_WAV, None, audio_out)

    # -----------------------------------------------------------------------

    def test_value_error_trim_duration_zero(self):
        audio_out = os.path.join(self.__tmp_dir, "out.wav")
        with self.assertRaises(ValueError):
            AudioOps.trim_audio(TEST_WAV, 0., audio_out)

    # -----------------------------------------------------------------------

    def test_value_error_trim_duration_negative(self):
        audio_out = os.path.join(self.__tmp_dir, "out.wav")
        with self.assertRaises(ValueError):
            AudioOps.trim_audio(TEST_WAV, -1., audio_out)

    # -----------------------------------------------------------------------

    def test_file_not_found(self):
        audio_out = os.path.join(self.__tmp_dir, "out.wav")
        with self.assertRaises(FileNotFoundError):
            AudioOps.trim_audio("/nonexistent/rec.wav", 1.0, audio_out)

# ---------------------------------------------------------------------------


class TestAddSilence(unittest.TestCase):

    def setUp(self):
        self.__tmp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.__tmp_dir, ignore_errors=True)

    # -----------------------------------------------------------------------

    def test_prepend_silence_lengthens_audio(self):
        audio_out    = os.path.join(self.__tmp_dir, "prepend.wav")
        original_dur = AudioOps.audio_duration(TEST_WAV)
        silence_dur  = 1.0
        AudioOps.add_silence(TEST_WAV, silence_dur, audio_out, begin=True)
        result_dur   = AudioOps.audio_duration(audio_out)
        self.assertAlmostEqual(original_dur + silence_dur, result_dur, delta=0.05)

    # -----------------------------------------------------------------------

    def test_append_silence_lengthens_audio(self):
        audio_out    = os.path.join(self.__tmp_dir, "append.wav")
        original_dur = AudioOps.audio_duration(TEST_WAV)
        silence_dur  = 1.0
        AudioOps.add_silence(TEST_WAV, silence_dur, audio_out, begin=False)
        result_dur   = AudioOps.audio_duration(audio_out)
        self.assertAlmostEqual(original_dur + silence_dur, result_dur, delta=0.05)

    # -----------------------------------------------------------------------

    def test_output_preserves_framerate(self):
        audio_out = os.path.join(self.__tmp_dir, "silence.wav")
        info_in   = AudioOps.get_audio_info(TEST_WAV)
        AudioOps.add_silence(TEST_WAV, 0.5, audio_out, begin=True)
        info_out  = AudioOps.get_audio_info(audio_out)
        self.assertEqual(info_in["framerate"], info_out["framerate"])
        self.assertEqual(info_in["nchannels"], info_out["nchannels"])

    # -----------------------------------------------------------------------

    def test_type_error_audio_in(self):
        audio_out = os.path.join(self.__tmp_dir, "out.wav")
        with self.assertRaises(TypeError):
            AudioOps.add_silence(None, 1.0, audio_out)
        with self.assertRaises(TypeError):
            AudioOps.add_silence("", 1.0, audio_out)

    # -----------------------------------------------------------------------

    def test_type_error_audio_out(self):
        with self.assertRaises(TypeError):
            AudioOps.add_silence(TEST_WAV, 1.0, None)
        with self.assertRaises(TypeError):
            AudioOps.add_silence(TEST_WAV, 1.0, "")

    # -----------------------------------------------------------------------

    def test_type_error_silence_duration(self):
        audio_out = os.path.join(self.__tmp_dir, "out.wav")
        with self.assertRaises(TypeError):
            AudioOps.add_silence(TEST_WAV, "1.0", audio_out)
        with self.assertRaises(TypeError):
            AudioOps.add_silence(TEST_WAV, None, audio_out)

    # -----------------------------------------------------------------------

    def test_value_error_silence_duration_zero(self):
        audio_out = os.path.join(self.__tmp_dir, "out.wav")
        with self.assertRaises(ValueError):
            AudioOps.add_silence(TEST_WAV, 0., audio_out)

    # -----------------------------------------------------------------------

    def test_value_error_silence_duration_negative(self):
        audio_out = os.path.join(self.__tmp_dir, "out.wav")
        with self.assertRaises(ValueError):
            AudioOps.add_silence(TEST_WAV, -0.5, audio_out)

    # -----------------------------------------------------------------------

    def test_file_not_found(self):
        audio_out = os.path.join(self.__tmp_dir, "out.wav")
        with self.assertRaises(FileNotFoundError):
            AudioOps.add_silence("/nonexistent/rec.wav", 1.0, audio_out)

# ---------------------------------------------------------------------------


class TestAdjustAudioAtClap(unittest.TestCase):

    def setUp(self):
        self.__tmp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.__tmp_dir, ignore_errors=True)

    # -----------------------------------------------------------------------

    def test_equal_claps_copies_file(self):
        audio_out = os.path.join(self.__tmp_dir, "equal.wav")
        AudioOps.adjust_audio_at_clap(TEST_WAV, 2.0, 2.0, audio_out)
        self.assertTrue(os.path.isfile(audio_out))
        self.assertAlmostEqual(
            AudioOps.audio_duration(TEST_WAV),
            AudioOps.audio_duration(audio_out),
            delta=0.01
        )

    # -----------------------------------------------------------------------

    def test_audio_clap_later_trims_beginning(self):
        audio_out    = os.path.join(self.__tmp_dir, "trimmed.wav")
        original_dur = AudioOps.audio_duration(TEST_WAV)
        # audio_clap=2.0, reference=1.0 → delta=-1.0 → trim 1.0s from start
        AudioOps.adjust_audio_at_clap(TEST_WAV, 2.0, 1.0, audio_out)
        result_dur   = AudioOps.audio_duration(audio_out)
        self.assertAlmostEqual(original_dur - 1.0, result_dur, delta=0.05)

    # -----------------------------------------------------------------------

    def test_audio_clap_earlier_prepends_silence(self):
        audio_out    = os.path.join(self.__tmp_dir, "padded.wav")
        original_dur = AudioOps.audio_duration(TEST_WAV)
        # audio_clap=1.0, reference=2.0 → delta=+1.0 → prepend 1.0s silence
        AudioOps.adjust_audio_at_clap(TEST_WAV, 1.0, 2.0, audio_out)
        result_dur   = AudioOps.audio_duration(audio_out)
        self.assertAlmostEqual(original_dur + 1.0, result_dur, delta=0.05)

    # -----------------------------------------------------------------------

    def test_type_error_audio_in(self):
        audio_out = os.path.join(self.__tmp_dir, "out.wav")
        with self.assertRaises(TypeError):
            AudioOps.adjust_audio_at_clap(None, 1.0, 1.0, audio_out)
        with self.assertRaises(TypeError):
            AudioOps.adjust_audio_at_clap("", 1.0, 1.0, audio_out)

    # -----------------------------------------------------------------------

    def test_type_error_audio_out(self):
        with self.assertRaises(TypeError):
            AudioOps.adjust_audio_at_clap(TEST_WAV, 1.0, 1.0, None)
        with self.assertRaises(TypeError):
            AudioOps.adjust_audio_at_clap(TEST_WAV, 1.0, 1.0, "")

    # -----------------------------------------------------------------------

    def test_type_error_clap_times(self):
        audio_out = os.path.join(self.__tmp_dir, "out.wav")
        with self.assertRaises(TypeError):
            AudioOps.adjust_audio_at_clap(TEST_WAV, "1.0", 1.0, audio_out)
        with self.assertRaises(TypeError):
            AudioOps.adjust_audio_at_clap(TEST_WAV, 1.0, None, audio_out)

    # -----------------------------------------------------------------------

    def test_file_not_found(self):
        audio_out = os.path.join(self.__tmp_dir, "out.wav")
        with self.assertRaises(FileNotFoundError):
            AudioOps.adjust_audio_at_clap("/nonexistent/rec.wav", 1.0, 1.0, audio_out)

# ---------------------------------------------------------------------------


class TestAdjustAudioDuration(unittest.TestCase):

    def setUp(self):
        self.__tmp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.__tmp_dir, ignore_errors=True)

    # -----------------------------------------------------------------------

    def test_shorter_audio_is_padded(self):
        audio_out    = os.path.join(self.__tmp_dir, "padded.wav")
        original_dur = AudioOps.audio_duration(TEST_WAV)
        target_dur   = original_dur + 2.0
        AudioOps.adjust_audio_duration(TEST_WAV, target_dur, audio_out)
        self.assertAlmostEqual(target_dur, AudioOps.audio_duration(audio_out), delta=0.05)

    # -----------------------------------------------------------------------

    def test_longer_audio_is_trimmed(self):
        audio_out    = os.path.join(self.__tmp_dir, "trimmed.wav")
        original_dur = AudioOps.audio_duration(TEST_WAV)
        target_dur   = original_dur - 1.0
        AudioOps.adjust_audio_duration(TEST_WAV, target_dur, audio_out)
        self.assertAlmostEqual(target_dur, AudioOps.audio_duration(audio_out), delta=0.05)

    # -----------------------------------------------------------------------

    def test_equal_duration_copies_file(self):
        audio_out    = os.path.join(self.__tmp_dir, "copy.wav")
        original_dur = AudioOps.audio_duration(TEST_WAV)
        AudioOps.adjust_audio_duration(TEST_WAV, original_dur, audio_out)
        self.assertTrue(os.path.isfile(audio_out))
        self.assertAlmostEqual(original_dur, AudioOps.audio_duration(audio_out), delta=0.01)

    # -----------------------------------------------------------------------

    def test_type_error_audio_in(self):
        audio_out = os.path.join(self.__tmp_dir, "out.wav")
        with self.assertRaises(TypeError):
            AudioOps.adjust_audio_duration(None, 5.0, audio_out)
        with self.assertRaises(TypeError):
            AudioOps.adjust_audio_duration("", 5.0, audio_out)

    # -----------------------------------------------------------------------

    def test_type_error_audio_out(self):
        with self.assertRaises(TypeError):
            AudioOps.adjust_audio_duration(TEST_WAV, 5.0, None)
        with self.assertRaises(TypeError):
            AudioOps.adjust_audio_duration(TEST_WAV, 5.0, "")

    # -----------------------------------------------------------------------

    def test_type_error_target_duration(self):
        audio_out = os.path.join(self.__tmp_dir, "out.wav")
        with self.assertRaises(TypeError):
            AudioOps.adjust_audio_duration(TEST_WAV, "5.0", audio_out)
        with self.assertRaises(TypeError):
            AudioOps.adjust_audio_duration(TEST_WAV, None, audio_out)

    # -----------------------------------------------------------------------

    def test_value_error_target_duration_zero(self):
        audio_out = os.path.join(self.__tmp_dir, "out.wav")
        with self.assertRaises(ValueError):
            AudioOps.adjust_audio_duration(TEST_WAV, 0., audio_out)

    # -----------------------------------------------------------------------

    def test_value_error_target_duration_negative(self):
        audio_out = os.path.join(self.__tmp_dir, "out.wav")
        with self.assertRaises(ValueError):
            AudioOps.adjust_audio_duration(TEST_WAV, -1., audio_out)

    # -----------------------------------------------------------------------

    def test_file_not_found(self):
        audio_out = os.path.join(self.__tmp_dir, "out.wav")
        with self.assertRaises(FileNotFoundError):
            AudioOps.adjust_audio_duration("/nonexistent/rec.wav", 5.0, audio_out)

# ---------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main()
