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

This module implements the clap-based synchronization logic of AViSS.

The ClapSync class computes the frame-accurate time boundaries shared by
all media files in a session, given a reference video. All audio files are
then aligned to those boundaries.

The synchronization principle is:
    1. The clap frame index is derived from the video clap time and fps.
       This snaps the start position to an exact frame boundary, which is
       essential for frame-accurate video trimming.
    2. The end frame index is derived from clap time + expected duration.
    3. Audio files are aligned so that their clap matches the frame-snapped
       clap time of the video (clap_frame_time), plus the delay.
    4. Audio files are then padded or trimmed to match the exact frame
       duration of the video output (end_frame_time - clap_frame_time).

The delay is applied after the clap: the actual cut starts at
clap_frame_time + delay, not at the raw clap time.

"""

from aviss.models import Session
from aviss.core.video_ops import VideoOps

# ---------------------------------------------------------------------------


class ClapSync:
    """Compute frame-accurate synchronization boundaries from a Session.

    A ClapSync instance is built from a Session and the fps of the reference
    video. It exposes the computed frame indices and time values used by the
    pipeline to trim video and align audio files.

    The reference video is always the primary video (session.video).
    If a secondary video is present, it is trimmed using the same frame
    indices, which assumes both videos share the same fps. If they differ,
    two ClapSync instances must be created.

    :example:
    >>> sync = ClapSync(session, fps=50.)
    >>> sync.clap_frame_index
    304
    >>> sync.clap_frame_time
    6.08
    >>> sync.end_frame_index
    10806
    >>> sync.end_frame_time
    216.12

    """

    def __init__(self, session: Session, fps: float):
        """Compute synchronization boundaries from the given session and fps.

        :param session: (Session) Session containing media files and timing.
        :param fps: (float) Frame rate of the reference video (frames/second).
        :raises: TypeError: session is not a Session instance.
        :raises: TypeError: fps is not a number.
        :raises: ValueError: fps is not strictly positive.
        :raises: ValueError: The computed end frame time exceeds the video duration.

        """
        if isinstance(session, Session) is False:
            raise TypeError("session must be a Session instance.")
        if isinstance(fps, (int, float)) is False:
            raise TypeError("fps must be a number.")
        if float(fps) <= 0.:
            raise ValueError("fps must be strictly positive.")

        self.__session = session
        self.__fps     = float(fps)

        # The reference clap time in the video, shifted by delay.
        # Cutting starts after the clap, not on it.
        video_clap_with_delay = session.video.clap_time + session.delay

        # Frame index of the clap: snaps to the nearest lower frame boundary.
        self.__clap_frame_index = VideoOps.time_to_frame(video_clap_with_delay, self.__fps)

        # Exact start time corresponding to that frame boundary.
        self.__clap_frame_time = VideoOps.frame_to_time(self.__clap_frame_index, self.__fps)

        # Index of the first frame NOT included in the output.
        self.__end_frame_index = VideoOps.end_frame_index(
            video_clap_with_delay, session.duration, self.__fps
        )

        # Exact end time of the last included frame.
        self.__end_frame_time = VideoOps.frame_to_time(self.__end_frame_index, self.__fps)

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

        This is clap_frame_time: the frame-snapped start time derived from
        the video clap. Audio files are shifted so that their own clap
        (plus delay) coincides with this value.

        :return: (float) Audio alignment target in seconds.

        """
        return self.__clap_frame_time

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
            f"ClapSync("
            f"fps={self.__fps}, "
            f"clap_frame={self.__clap_frame_index} ({self.__clap_frame_time:.3f}s), "
            f"end_frame={self.__end_frame_index} ({self.__end_frame_time:.3f}s)"
            f")"
        )
