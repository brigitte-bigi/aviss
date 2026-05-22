"""
:filename: pipeline.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Synchronization pipeline orchestrator for AViSS.

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

from aviss.settings import cfg
from aviss.models import Session, SyncResult
from aviss.utils import build_output_name, check_command, create_working_dir
from aviss.core.audio_ops import AudioOps
from aviss.core.video_ops import VideoOps
from aviss.core.clap_sync import ClapSync

# ---------------------------------------------------------------------------


class Pipeline:
    """Orchestrate the AViSS synchronization pipeline for one Session.

    A Pipeline instance is created for one Session. Calling run() executes
    all steps and returns a SyncResult. Intermediate files are written to
    a working directory named after the output filename stem.

    :example:
    >>> pipeline = Pipeline(session)
    >>> result = pipeline.run()
    >>> result.success
    True
    >>> result.synced_files
    ['/out/Laurent_S09_sent.wav', '/out/Laurent_S09_sent.mkv']

    """

    # Names of required external commands.
    REQUIRED_COMMANDS = ("ffmpeg", "sox")

    # -----------------------------------------------------------------------

    def __init__(self, session: Session):
        """Initialize the pipeline for the given session.

        :param session: (Session) Session to process.
        :raises: TypeError: session is not a Session instance.

        """
        if isinstance(session, Session) is False:
            raise TypeError("session must be a Session instance.")

        self.__session    = session
        self.__result     = SyncResult()
        self.__work_dir   = None
        self.__stem       = None

    # -----------------------------------------------------------------------
    # Public interface
    # -----------------------------------------------------------------------

    def run(self) -> SyncResult:
        """Execute all pipeline steps and return the synchronization result.

        :return: (SyncResult) Result of the pipeline run.

        """
        try:
            self.__step_prepare()
            pairs = self.__step_build_pairs()
            self.__step_sync_audios(pairs)
            self.__step_trim_videos(pairs)
            self.__step_post_process_videos(pairs)
            self.__result.success = True

        except Exception as e:
            self.__result.add_message(f"ERROR: {e}")
            self.__result.success = False

        return self.__result

    # -----------------------------------------------------------------------
    # Pipeline steps (private)
    # -----------------------------------------------------------------------

    def __step_prepare(self) -> None:
        """Verify dependencies, build the output stem and create the working dir.

        """
        self.__result.add_message("Step 0: Prepare.")

        for cmd in Pipeline.REQUIRED_COMMANDS:
            check_command(cmd)

        if self.__session.all_files_exist() is False:
            raise FileNotFoundError(
                "One or more media files declared in the session do not exist on disk."
            )

        self.__stem = build_output_name(
            self.__session.output_name_meta,
            cfg.output.output_name_cols,
            cfg.output.output_sep
        )
        if len(self.__stem) == 0:
            raise ValueError(
                "The output filename stem is empty. "
                "Check cfg.output.output_name_cols and the CSV metadata columns."
            )

        work_dir_name = self.__stem + cfg.output.work_dir_suffix
        self.__work_dir = create_working_dir(work_dir_name)
        self.__result.add_message(f"  Working directory: {self.__work_dir!r}")
        self.__result.add_message(f"  Output stem: {self.__stem!r}")

    # -----------------------------------------------------------------------

    def __step_build_pairs(self) -> list:
        """Compute one ClapSync per video and assemble (video, audio, sync, audio_out, video_out) tuples.

        Each pair drives one complete audio+video output. The secondary video
        gets its own ClapSync built from its own clap time and fps. When only
        one audio is present, it is reused for the secondary video.

        :return: (list) List of (video_media, audio_media, ClapSync, audio_out_name, video_out_name).

        """
        self.__result.add_message("Step 1: Compute synchronization boundaries.")

        pairs = []

        info1 = VideoOps.get_video_info(self.__session.video.path)

        if self.__session.has_second_video() is True:
            info2 = VideoOps.get_video_info(self.__session.video2.path)

            # The video with the lowest fps defines the reference delta.
            # All videos share this delta so the clap appears at the same
            # sub-frame position in every output (cross-video synchronization).
            if info2["fps"] < info1["fps"]:
                ref_sync = ClapSync(self.__session, info2["fps"],
                                    video_clap=self.__session.video2.clap_time)
                ref_delta = ref_sync.clap_delta
                sync1 = ClapSync(self.__session, info1["fps"],
                                 reference_delta=ref_delta)
                sync2 = ref_sync
            else:
                sync1 = ClapSync(self.__session, info1["fps"])
                ref_delta = sync1.clap_delta
                sync2 = ClapSync(self.__session, info2["fps"],
                                 video_clap=self.__session.video2.clap_time,
                                 reference_delta=ref_delta)

            sync1.check_video_duration(info1["duration"])
            sync2.check_video_duration(info2["duration"])
            self.__result.add_message(f"  Reference delta: {ref_delta:.6f}s")
            self.__result.add_message(
                f"  Primary:   clap frame {sync1.clap_frame_index} ({sync1.clap_frame_time:.3f}s), "
                f"delta {sync1.clap_delta:.6f}s, "
                f"end frame {sync1.end_frame_index} ({sync1.end_frame_time:.3f}s)"
            )

            if self.__session.has_second_audio() is True:
                audio2 = self.__session.audio2
            else:
                audio2 = self.__session.audio

            suffix1 = "_" + self.__session.video_name  if self.__session.video_name  is not None else "_1"
            suffix2 = "_" + self.__session.video_name2 if self.__session.video_name2 is not None else "_2"

            pairs.append((self.__session.video, self.__session.audio, sync1,
                          self.__stem + suffix1 + ".wav", self.__stem + suffix1 + ".mkv"))
            self.__result.add_message(
                f"  Secondary: clap frame {sync2.clap_frame_index} ({sync2.clap_frame_time:.3f}s), "
                f"delta {sync2.clap_delta:.6f}s, "
                f"end frame {sync2.end_frame_index} ({sync2.end_frame_time:.3f}s)"
            )
            pairs.append((self.__session.video2, audio2, sync2,
                          self.__stem + suffix2 + ".wav", self.__stem + suffix2 + ".mkv"))

        else:
            sync1 = ClapSync(self.__session, info1["fps"])
            sync1.check_video_duration(info1["duration"])
            self.__result.add_message(
                f"  Primary:   clap frame {sync1.clap_frame_index} ({sync1.clap_frame_time:.3f}s), "
                f"delta {sync1.clap_delta:.6f}s, "
                f"end frame {sync1.end_frame_index} ({sync1.end_frame_time:.3f}s)"
            )
            pairs.append((self.__session.video, self.__session.audio, sync1,
                          self.__stem + ".wav", self.__stem + ".mkv"))

        return pairs

    # -----------------------------------------------------------------------

    def __step_sync_audios(self, pairs: list) -> None:
        """Align each audio to its video's clap frame time and trim to duration.

        :param pairs: (list) List of (video_media, audio_media, ClapSync, audio_out, video_out).

        """
        self.__result.add_message("Step 2: Synchronize audio files.")

        for _video, audio, sync, audio_out, _video_out in pairs:
            self.__sync_one_audio(audio.path, audio.clap_time, sync, audio_out)

    # -----------------------------------------------------------------------

    def __sync_one_audio(self, audio_path: str, raw_clap: float,
                         sync: ClapSync, out_name: str) -> None:
        """Align and trim a single audio file.

        :param audio_path: (str) Path to the input audio file.
        :param raw_clap: (float) Raw clap time in the audio (seconds).
        :param sync: (ClapSync) Synchronization boundaries.
        :param out_name: (str) Filename (not path) for the final output.

        """
        effective_clap = sync.get_audio_clap_with_delay(raw_clap)

        tmp_clap = os.path.join(self.__work_dir, "_audio_clap.wav")
        tmp_dur  = os.path.join(self.__work_dir, "_audio_dur.wav")
        final    = os.path.join(self.__work_dir, out_name)

        # Pass 1: align to clap frame time.
        AudioOps.adjust_audio_at_clap(
            audio_path, effective_clap, sync.audio_reference_clap, tmp_clap
        )

        # Pass 2: match end frame time exactly.
        AudioOps.adjust_audio_duration(tmp_clap, sync.end_frame_time, tmp_dur)

        # Pass 3: trim the leading silence up to clap_frame_time.
        AudioOps.trim_audio(tmp_dur, sync.clap_frame_time, final, begin=True)

        if os.path.isfile(tmp_clap) is True:
            os.remove(tmp_clap)
        if os.path.isfile(tmp_dur) is True:
            os.remove(tmp_dur)

        self.__result.add_synced_file(final)
        self.__result.add_message(f"  Audio synced: {final!r}")

    # -----------------------------------------------------------------------

    def __step_trim_videos(self, pairs: list) -> None:
        """Trim each video between its own clap frame and end frame.

        :param pairs: (list) List of (video_media, audio_media, ClapSync, audio_out, video_out).

        """
        self.__result.add_message("Step 3: Trim video files.")

        for video, _audio, sync, _audio_out, video_out in pairs:
            out_path = os.path.join(self.__work_dir, video_out)
            VideoOps.trim(
                video.path,
                sync.clap_frame_index,
                sync.end_frame_index,
                out_path
            )
            self.__result.add_synced_file(out_path)
            self.__result.add_message(f"  Video trimmed: {out_path!r}")

    # -----------------------------------------------------------------------

    def __step_post_process_videos(self, pairs: list) -> None:
        """Apply crop and copyright overlay to each trimmed video.

        :param pairs: (list) List of (video_media, audio_media, ClapSync, audio_out, video_out).

        """
        self.__result.add_message("Step 4: Post-process video files.")

        for video, _audio, _sync, _audio_out, video_out in pairs:
            current = os.path.join(self.__work_dir, video_out)
            current = self.__apply_crop(video, current)
            current = self.__apply_copyright(current)
            self.__result.add_message(f"  Video post-processed: {current!r}")

    # -----------------------------------------------------------------------

    def __apply_crop(self, media, video_path: str) -> str:
        """Apply crop to a video if the media file defines a crop region.

        :param media: (MediaFile) Media file with optional crop parameters.
        :param video_path: (str) Path to the current video file.
        :return: (str) Path to the (possibly cropped) video file.

        """
        if media.has_crop() is False:
            return video_path

        self.__result.add_message(
            f"  Crop: x={media.crop_x} y={media.crop_y} "
            f"w={media.crop_w} h={media.crop_h}"
        )
        tmp_path = video_path.replace(".mkv", "_tmp_crop.mkv")
        VideoOps.crop(video_path, media.crop_x, media.crop_y,
                      media.crop_w, media.crop_h, tmp_path)
        os.remove(video_path)
        os.rename(tmp_path, video_path)
        return video_path

    # -----------------------------------------------------------------------

    def __apply_copyright(self, video_path: str) -> str:
        """Apply a copyright overlay to a video if configured.

        :param video_path: (str) Path to the current video file.
        :return: (str) Path to the (possibly annotated) video file.

        """
        if cfg.output.copyright is None:
            return video_path

        self.__result.add_message(f"  Copyright: {cfg.output.copyright!r}")
        tmp_path = video_path.replace(".mkv", "_tmp_copy.mkv")
        VideoOps.add_copyright(video_path, cfg.output.copyright, tmp_path)
        os.remove(video_path)
        os.rename(tmp_path, video_path)
        return video_path
