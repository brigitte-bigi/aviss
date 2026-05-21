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

The Pipeline class orchestrates all steps of the AViSS synchronization
process for a single Session.

Processing steps:
    0. Prepare the working directory and verify external dependencies.
    1. Compute frame-accurate synchronization boundaries (ClapSync).
    2. Extract the audio track from the video and verify the video duration.
    3. Synchronize each audio file to the clap frame time.
    4. Trim each video between the clap frame and the end frame.
    5. Apply crop, copyright overlay, and rotation to each video if needed.
    6. Optionally produce a SPPAS-ready mono 16kHz audio file.

Each step logs its progress to the SyncResult report. On error, the
exception is caught, logged, and the SyncResult.success flag is set to False.

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
            sync   = self.__step_clap_sync()
            v_dur  = self.__step_extract_video_audio()
            sync.check_video_duration(v_dur)
            self.__step_sync_audios(sync)
            self.__step_trim_videos(sync)
            self.__step_post_process_videos()
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

    def __step_clap_sync(self) -> ClapSync:
        """Compute frame-accurate synchronization boundaries.

        The fps is read from the primary video file. If the session carries a
        secondary video with a different fps, a dedicated ClapSync must be
        computed by the export module.

        :return: (ClapSync) Synchronization boundaries for the primary video.

        """
        self.__result.add_message("Step 1: Compute clap synchronization boundaries.")

        fps  = VideoOps.get_video_info(self.__session.video.path)["fps"]
        sync = ClapSync(self.__session, fps)

        self.__result.add_message(
            f"  Clap frame: {sync.clap_frame_index} ({sync.clap_frame_time:.3f}s)"
        )
        self.__result.add_message(
            f"  End frame:  {sync.end_frame_index} ({sync.end_frame_time:.3f}s)"
        )
        return sync

    # -----------------------------------------------------------------------

    def __step_extract_video_audio(self) -> float:
        """Read the primary video metadata and return its duration.

        The duration is used to verify that the video is long enough
        to cover the requested synchronization range.

        :return: (float) Duration of the primary video in seconds.

        """
        self.__result.add_message("Step 2: Read primary video duration.")

        info     = VideoOps.get_video_info(self.__session.video.path)
        duration = info["duration"]

        self.__result.add_message(f"  Primary video duration: {duration:.3f}s")
        return duration

    # -----------------------------------------------------------------------

    def __step_sync_audios(self, sync: ClapSync) -> None:
        """Align all audio files to the clap frame time and trim to duration.

        Each audio is processed in two passes:
            1. Align: shift the audio so that its clap matches
               sync.audio_reference_clap.
            2. Duration: pad or trim to sync.end_frame_time.

        Intermediate files are removed after each audio is processed.

        :param sync: (ClapSync) Synchronization boundaries.

        """
        self.__result.add_message("Step 3: Synchronize audio files.")

        audio_items = [(self.__session.audio, self.__stem + ".wav")]
        if self.__session.has_second_audio() is True:
            audio_items.append((self.__session.audio2, self.__stem + "_2.wav"))

        for media, out_name in audio_items:
            self.__sync_one_audio(media.path, media.clap_time, sync, out_name)

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

    def __step_trim_videos(self, sync: ClapSync) -> None:
        """Trim all video files between the clap frame and the end frame.

        :param sync: (ClapSync) Synchronization boundaries.

        """
        self.__result.add_message("Step 4: Trim video files.")

        video_items = [(self.__session.video, self.__stem + ".mkv")]
        if self.__session.has_second_video() is True:
            video_items.append((self.__session.video2, self.__stem + "_2.mkv"))

        for media, out_name in video_items:
            out_path = os.path.join(self.__work_dir, out_name)
            VideoOps.trim(
                media.path,
                sync.clap_frame_index,
                sync.end_frame_index,
                out_path
            )
            self.__result.add_synced_file(out_path)
            self.__result.add_message(f"  Video trimmed: {out_path!r}")

    # -----------------------------------------------------------------------

    def __step_post_process_videos(self) -> None:
        """Apply crop, copyright overlay and rotation to each trimmed video.

        Each operation is applied in sequence if relevant. Intermediate MKV
        files are removed after each step. The final MKV replaces the
        trimmed MKV in the result file list.

        """
        self.__result.add_message("Step 5: Post-process video files.")

        video_items = [(self.__session.video, self.__stem + ".mkv")]
        if self.__session.has_second_video() is True:
            video_items.append((self.__session.video2, self.__stem + "_2.mkv"))

        for media, out_name in video_items:
            current = os.path.join(self.__work_dir, out_name)
            current = self.__apply_crop(media, current)
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
        cropped = video_path.replace(".mkv", "_crop.mkv")
        VideoOps.crop(video_path, media.crop_x, media.crop_y,
                      media.crop_w, media.crop_h, cropped)
        os.remove(video_path)
        return cropped

    # -----------------------------------------------------------------------

    def __apply_copyright(self, video_path: str) -> str:
        """Apply a copyright overlay to a video if configured.

        :param video_path: (str) Path to the current video file.
        :return: (str) Path to the (possibly annotated) video file.

        """
        if cfg.output.copyright is None:
            return video_path

        self.__result.add_message(f"  Copyright: {cfg.output.copyright!r}")
        copy_path = video_path.replace(".mkv", "_copy.mkv")
        VideoOps.add_copyright(video_path, cfg.output.copyright, copy_path)
        os.remove(video_path)
        return copy_path
