"""
:filename: clap_sync.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Clap-based synchronization logic for AViSS.

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

from aviss.models import avSession
from aviss.core.video_ops import avVideoOps

# ---------------------------------------------------------------------------


class avClapSync:
    """Compute frame-accurate synchronization boundaries from a avSession.

    A avClapSync instance is built from a avSession and the fps of the reference
    video. It exposes the computed frame indices and time values used by the
    pipeline to trim video and align audio files.

    The reference video is always the primary video (session.video).
    If a secondary video is present, it is trimmed using the same frame
    indices, which assumes both videos share the same fps. If they differ,
    two avClapSync instances must be created.

    :example:
    >>> sync = avClapSync(session, fps=50.)
    >>> sync.clap_frame_index
    304
    >>> sync.clap_frame_time
    6.08
    >>> sync.end_frame_index
    10806
    >>> sync.end_frame_time
    216.12

    """

    def __init__(self, session: avSession, fps: float, video_clap: float = None,
                 reference_delta: float = None):
        """Compute synchronization boundaries from the given session and fps.

        Algorithm — faithful transcription of the original montage scripts
        (montage_step1.py / montage.py, Brigitte Bigi, CNRS/LPL 2021-2024):

        Notation:
          vc   = video_clap + delay       (effective clap time in the video)
          fps  = frame rate of this video
          dur  = session.duration

        Step 1 — clap frame (primary / reference video):
          clap_frame_index = int(vc * fps)          # floor, 0-based
          clap_frame_time  = clap_frame_index / fps
          clap_delta       = vc - clap_frame_time   # in [0, 1/fps)

        Step 2 — end frame (first excluded frame):
          end_frame_index  = 1 + int((vc + dur) * fps)
          end_frame_time   = end_frame_index / fps

        Step 3 — cross-sync (secondary video, fps2 != fps_ref):
          Given reference_delta = clap_delta of the reference (lowest-fps) video:
          shift_frames     = int(reference_delta * fps2)
          clap_frame_index = int(vc2 * fps2) - shift_frames
          end_frame_index  = 1 + int((vc2 + dur) * fps2) + shift_frames

          IMPORTANT: the subtraction int(A*fps) - int(d*fps) is used, NOT
          int((A-d)*fps), to match the original script exactly. These differ
          by 1 when frac(A*fps) < frac(d*fps).

        Audio alignment (per audio file, handled by the pipeline):
          Pass 1: shift audio so its effective clap matches vc (trim or pad).
          Pass 2: pad or trim to reach end_frame_time.
          Pass 3: trim clap_frame_time from the start.

        :param session: (avSession) avSession containing media files and timing.
        :param fps: (float) Frame rate of the reference video (frames/second).
        :param video_clap: (float|None) Clap time in the video (seconds). When
            None, session.videos[0].clap_time is used.
        :param reference_delta: (float|None) clap_delta of the reference
            (lowest-fps) video. When provided, applies cross-video
            synchronization (Step 3 above). When None, each video snaps
            independently to its own frame boundary (Step 1 above).
        :raises: TypeError: session is not a avSession instance.
        :raises: TypeError: fps is not a number.
        :raises: ValueError: fps is not strictly positive.
        :raises: TypeError: video_clap is not a number when not None.
        :raises: ValueError: video_clap is negative.
        :raises: TypeError: reference_delta is not a number when not None.
        :raises: ValueError: reference_delta is negative.

        """
        if isinstance(session, avSession) is False:
            raise TypeError("session must be a avSession instance.")
        if isinstance(fps, (int, float)) is False:
            raise TypeError("fps must be a number.")
        if float(fps) <= 0.:
            raise ValueError("fps must be strictly positive.")
        if video_clap is None:
            raw_video_clap = session.videos[0].clap_time
        else:
            if isinstance(video_clap, (int, float)) is False:
                raise TypeError("video_clap must be a number.")
            if float(video_clap) < 0.:
                raise ValueError("video_clap must be zero or positive.")
            raw_video_clap = float(video_clap)
        if reference_delta is not None:
            if isinstance(reference_delta, (int, float)) is False:
                raise TypeError("reference_delta must be a number.")
            if float(reference_delta) < 0.:
                raise ValueError("reference_delta must be zero or positive.")

        self.__session = session
        self.__fps     = float(fps)

        # The reference clap time in the video, shifted by delay.
        # Cutting starts after the clap, not on it.
        video_clap_with_delay = raw_video_clap + session.delay
        self.__video_clap_with_delay = video_clap_with_delay

        # Clap frame index — see algorithm in docstring.
        # Cross-sync: int(vc*fps) - int(d*fps), NOT int((vc-d)*fps).
        # The two expressions differ by 1 when frac(vc*fps) < frac(d*fps).
        if reference_delta is None:
            self.__clap_frame_index = avVideoOps.time_to_frame(video_clap_with_delay, self.__fps)
        else:
            shift_frames = int(float(reference_delta) * self.__fps)
            self.__clap_frame_index = (
                avVideoOps.time_to_frame(video_clap_with_delay, self.__fps) - shift_frames
            )

        # Exact start time corresponding to that frame boundary.
        self.__clap_frame_time = avVideoOps.frame_to_time(self.__clap_frame_index, self.__fps)

        # Delta: gap between the actual clap time and the frame boundary.
        self.__clap_delta = video_clap_with_delay - self.__clap_frame_time

        # End frame index — see algorithm in docstring (Steps 2 and 3).
        # end_frame_index = 1 + int((vc + dur) * fps)       [primary]
        # end_frame_index += int(reference_delta * fps)     [cross-sync]
        self.__end_frame_index = avVideoOps.end_frame_index(
            video_clap_with_delay, session.duration, self.__fps
        )
        if reference_delta is not None:
            self.__end_frame_index = self.__end_frame_index + shift_frames

        # Exact end time of the last included frame.
        self.__end_frame_time = avVideoOps.frame_to_time(self.__end_frame_index, self.__fps)

    # -----------------------------------------------------------------------
    # Read-only properties
    # -----------------------------------------------------------------------

    def get_fps(self) -> float:
        """Return the frame rate used for synchronization.

        :return: (float) Frame rate in frames per second.

        """
        return self.__fps

    fps = property(get_fps, None)

    # -----------------------------------------------------------------------

    def get_clap_frame_index(self) -> int:
        """Return the 0-based index of the frame containing the clap.

        This is the start frame for video trimming.

        :return: (int) Start frame index.

        """
        return self.__clap_frame_index

    clap_frame_index = property(get_clap_frame_index, None)

    # -----------------------------------------------------------------------

    def get_clap_delta(self) -> float:
        """Return the gap between the actual clap time and its frame boundary (seconds).

        This is the sub-frame offset used for cross-video synchronization:
        all videos in a session share the same delta so the clap appears at
        the same position in every output file.

        :return: (float) Delta in seconds (always in [0, 1/fps[).

        """
        return self.__clap_delta

    clap_delta = property(get_clap_delta, None)

    # -----------------------------------------------------------------------

    def get_clap_frame_time(self) -> float:
        """Return the start time of the clap frame (seconds).

        This is the reference time to which all audio files are aligned.
        It corresponds to the exact beginning of the frame containing the
        clap, which may differ slightly from the raw clap time.

        :return: (float) Clap frame start time in seconds.

        """
        return self.__clap_frame_time

    clap_frame_time = property(get_clap_frame_time, None)

    # -----------------------------------------------------------------------

    def get_end_frame_index(self) -> int:
        """Return the index of the first frame NOT included in the output.

        This is the end frame for video trimming (exclusive upper bound).

        :return: (int) End frame index (exclusive).

        """
        return self.__end_frame_index

    end_frame_index = property(get_end_frame_index, None)

    # -----------------------------------------------------------------------

    def get_end_frame_time(self) -> float:
        """Return the time of the end frame boundary (seconds).

        This is the exact duration target to which all audio files are
        padded or trimmed after clap alignment.

        :return: (float) End frame time in seconds.

        """
        return self.__end_frame_time

    end_frame_time = property(get_end_frame_time, None)

    # -----------------------------------------------------------------------

    def get_audio_reference_clap(self) -> float:
        """Return the clap time to which audio files must be aligned.

        This is the effective video clap time (raw video clap + delay).
        Audio files are shifted so that their own clap (plus delay) coincides
        with this value. The sub-frame offset (clap_delta) is preserved in the
        output, matching the original script behaviour.

        :return: (float) Audio alignment target in seconds.

        """
        return self.__video_clap_with_delay

    audio_reference_clap = property(get_audio_reference_clap, None)

    # -----------------------------------------------------------------------

    def get_audio_clap_with_delay(self, audio_clap: float) -> float:
        """Return the effective audio clap time, shifted by the session delay.

        :param audio_clap: (float) Raw clap time in the audio file (seconds).
        :return: (float) Effective clap time in seconds (audio_clap + delay).
        :raises: TypeError: audio_clap is not a number.

        """
        if isinstance(audio_clap, (int, float)) is False:
            raise TypeError("audio_clap must be a number.")
        return float(audio_clap) + self.__session.delay

    # -----------------------------------------------------------------------

    def check_video_duration(self, video_duration: float) -> None:
        """Raise ValueError if the expected end time exceeds the video duration.

        This check must be performed before trimming to avoid requesting more
        frames than the video contains.

        :param video_duration: (float) Actual duration of the video (seconds).
        :raises: TypeError: video_duration is not a number.
        :raises: ValueError: The expected end frame time exceeds video_duration.

        """
        if isinstance(video_duration, (int, float)) is False:
            raise TypeError("video_duration must be a number.")
        if self.__end_frame_time > float(video_duration):
            raise ValueError(
                f"The expected end time ({self.__end_frame_time:.3f}s) exceeds "
                f"the video duration ({float(video_duration):.3f}s). "
                f"Check the duration value in the CSV."
            )

    # -----------------------------------------------------------------------

    def __repr__(self) -> str:
        return (
            f"avClapSync("
            f"fps={self.__fps}, "
            f"clap_frame={self.__clap_frame_index} ({self.__clap_frame_time:.3f}s), "
            f"end_frame={self.__end_frame_index} ({self.__end_frame_time:.3f}s)"
            f")"
        )
