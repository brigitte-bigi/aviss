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
from aviss.models import avSession, avSyncResult
from aviss.utils import aviss_logger, build_output_name, check_command, create_working_dir
from aviss.core.audio_ops import avAudioOps
from aviss.core.video_ops import avVideoOps
from aviss.core.clap_sync import avClapSync

# ---------------------------------------------------------------------------


class avPipeline:
    """Orchestrate the AViSS synchronization pipeline for one avSession.

    A avPipeline instance is created for one avSession. Calling run() executes
    all steps and returns a avSyncResult. Intermediate files are written to
    a working directory named after the output filename stem.

    :example:
    >>> pipeline = avPipeline(session)
    >>> result = pipeline.run()
    >>> result.success
    True
    >>> result.synced_files
    ['/out/Laurent_S09_sent.wav', '/out/Laurent_S09_sent.mkv']

    """

    # Names of required external commands.
    REQUIRED_COMMANDS = ("ffmpeg", "sox")

    # -----------------------------------------------------------------------

    def __init__(self, session: avSession):
        """Initialize the pipeline for the given session.

        :param session: (avSession) avSession to process.
        :raises: TypeError: session is not a avSession instance.

        """
        if isinstance(session, avSession) is False:
            raise TypeError("session must be a avSession instance.")

        self.__session    = session
        self.__result     = avSyncResult()
        self.__work_dir   = None
        self.__stem       = None

    # -----------------------------------------------------------------------
    # Public interface
    # -----------------------------------------------------------------------

    def run(self) -> avSyncResult:
        """Execute all pipeline steps and return the synchronization result.

        :return: (avSyncResult) Result of the pipeline run.

        """
        try:
            self.__step_prepare()
            audio_items, video_items = self.__step_build_items()
            self.__step_sync_audios(audio_items)
            self.__step_trim_videos(video_items)
            self.__step_post_process_videos(video_items)
            self.__result.success = True

        except Exception as e:
            self.__log(f"ERROR: {e}")
            self.__result.success = False

        return self.__result

    def __log(self, message: str) -> None:
        """Add a message to the result report and write it to the logger.

        :param message: (str) Message to log.

        """
        self.__result.add_message(message)
        aviss_logger.write(message)

    def __log_step(self, number: int, title: str) -> None:
        """Write a step separator matching the original script log format.

        :param number: (int) Step number.
        :param title: (str) Step title.

        """
        msg   = f"STEP {number}: {title}"
        space = " " * ((60 - len(msg)) // 2)
        self.__log("")
        self.__log("----------------------------------------------------------------")
        self.__log(space + msg)
        self.__log("----------------------------------------------------------------")

    def __log_ok(self, path: str) -> None:
        """Write an [  OK  ] confirmation line for the given path.

        :param path: (str) Path to confirm.

        """
        self.__log(f"[  OK  ] {path}")

    def __log_audio_info(self, path: str) -> None:
        """Write an audio file info block matching the original script format.

        :param path: (str) Path to the audio file.

        """
        info = avAudioOps.get_audio_info(path)
        self.__log(f" ... Test audio file: {path}")
        self.__log(f"    - duration: {info['duration']:.3f}")
        self.__log(f"    - framerate: {info['framerate']:d}")
        self.__log(f"    - channels: {info['nchannels']:d}")
        self.__log(f"    - bitrate: {info['sampwidth'] * 8:d}")

    def __log_video_info(self, path: str) -> None:
        """Write a video file info block matching the original script format.

        :param path: (str) Path to the video file.

        """
        info = avVideoOps.get_video_info(path)
        self.__log("  - video container: mkv")
        self.__log(f"  - video codec: libx265 (crf={cfg.output.crf:d})")
        if cfg.output.copyright is not None:
            self.__log(f"  - copyright: {cfg.output.copyright}")
        self.__log("  - no audio")
        self.__log(f"  - fps: {info['fps']:.2f}")
        self.__log(f"  - nframes: {info['nframes']:d}")
        self.__log(f"  - duration: {info['duration']:f}")
        self.__log(f"  - size: ({info['width']}, {info['height']})")

    # -----------------------------------------------------------------------
    # avPipeline steps (private)
    # -----------------------------------------------------------------------

    def __step_prepare(self) -> None:
        """Verify dependencies, build the output stem and create the working dir.

        """
        for cmd in avPipeline.REQUIRED_COMMANDS:
            check_command(cmd)

        missing = [
            m.path for m in self.__session.audios + self.__session.videos
            if m.exists() is False
        ]
        if len(missing) > 0:
            raise FileNotFoundError(
                "Media file(s) not found: " + ", ".join(repr(p) for p in missing)
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

        self.__log_step(0, "Parse CSV and check media files")
        self.__log(f" ... Output working dir: {self.__work_dir}")

        for audio in self.__session.audios:
            self.__log_audio_info(audio.path)
            self.__log(f" ... Input audio file: {audio.path}")
            self.__log_ok(audio.path)

        for video in self.__session.videos:
            info = avVideoOps.get_video_info(video.path)
            self.__log(f" ... Input video file: {video.path} ({info['fps']:.2f} fps)")
            self.__log_ok(video.path)

        delay = self.__session.delay
        self.__log(f" ... Given delta: {delay:.3f}")
        for audio in self.__session.audios:
            self.__log(f" ... Given audio clap: {audio.clap_time + delay:.3f}")
        for video in self.__session.videos:
            self.__log(f" ... Given video clap: {video.clap_time + delay:.3f}")
        self.__log(f" ... Given expected duration: {self.__session.duration:.3f}")

    # -----------------------------------------------------------------------

    def __step_build_items(self) -> tuple:
        """Compute sync objects and build independent audio and video item lists.

        All media share the same clap event. The video with the lowest fps
        defines the reference avClapSync used by all audios. Each video gets
        its own avClapSync (frame-accurate at its own fps).

        Audio suffixes (from CSV column index):
            audio_file  -> ""
            audio_file2 -> "_audio2", audio_file3 -> "_audio3", ...

        Video suffixes (from video_name or CSV column index):
            single video           -> ""
            multiple, named        -> "_" + video_name
            multiple, unnamed      -> "_video2", "_video3", ...

        :return: (tuple) (audio_items, video_items) where each list contains
                 (avMediaFile, avClapSync, out_name) tuples.

        """
        self.__log_step(1, "Compute synchronization boundaries")

        videos = self.__session.videos
        audios = self.__session.audios
        names  = self.__session.video_names
        n      = len(videos)
        m      = len(audios)

        infos = [avVideoOps.get_video_info(v.path) for v in videos]

        # Reference sync: always the lowest-fps video.
        ref_idx  = min(range(n), key=lambda i: infos[i]["fps"])
        ref_sync = avClapSync(self.__session, infos[ref_idx]["fps"],
                            video_clap=videos[ref_idx].clap_time)
        ref_delta = ref_sync.clap_delta

        if n > 1:
            self.__log(
                f"  Reference delta: {ref_delta:.6f}s "
                f"(video {ref_idx + 1}, {infos[ref_idx]['fps']:.2f} fps)"
            )

        # Build one avClapSync per video.
        video_syncs = []
        for i in range(n):
            if i == ref_idx:
                video_syncs.append(ref_sync)
            else:
                video_syncs.append(avClapSync(
                    self.__session, infos[i]["fps"],
                    video_clap=videos[i].clap_time,
                    reference_delta=ref_delta
                ))

        # Validate and log each video sync.
        for i, (sync, info) in enumerate(zip(video_syncs, infos)):
            sync.check_video_duration(info["duration"])
            self.__log(
                f" ... Video {i + 1}: start time value of the frame with the clap: "
                f"{sync.clap_frame_index} frames = {sync.clap_frame_time:.3f} seconds"
            )
            self.__log(
                f" ... ... Delta among the real clap position in the video and "
                f"the start time of the first frame in the video = {sync.clap_delta:.6f}"
            )
            self.__log(
                f" ... estimated end time of video {i + 1}: "
                f"{sync.end_frame_index} frames = {sync.end_frame_time:.3f} seconds"
            )

        # Video suffixes.
        if n == 1:
            video_suffixes = [""]
        else:
            video_suffixes = []
            for i, name in enumerate(names):
                if name is not None:
                    video_suffixes.append("_" + name)
                else:
                    video_suffixes.append("_video" + str(i + 1))

        # Audio suffixes (independent of videos).
        if m == 1:
            audio_suffixes = [""]
        else:
            audio_suffixes = [""] + ["_audio" + str(i + 1) for i in range(1, m)]

        # Build video items: (video_media, sync, out_name).
        video_items = []
        for video, sync, suffix in zip(videos, video_syncs, video_suffixes):
            video_items.append((video, sync, self.__stem + suffix + ".mkv"))

        # Build audio items: (audio_media, ref_sync, out_name).
        audio_items = []
        for audio, suffix in zip(audios, audio_suffixes):
            audio_items.append((audio, ref_sync, self.__stem + suffix + ".wav"))

        return audio_items, video_items

    # -----------------------------------------------------------------------

    def __step_sync_audios(self, audio_items: list) -> None:
        """Align and trim each audio file to the reference synchronization.

        :param audio_items: (list) List of (audio_media, avClapSync, out_name) tuples.

        """
        self.__log_step(2, "Synchronize audio files")

        for audio, sync, audio_out in audio_items:
            self.__sync_one_audio(audio.path, audio.clap_time, sync, audio_out)

    # -----------------------------------------------------------------------

    def __sync_one_audio(self, audio_path: str, raw_clap: float,
                         sync: avClapSync, out_name: str) -> None:
        """Align and trim a single audio file.

        :param audio_path: (str) Path to the input audio file.
        :param raw_clap: (float) Raw clap time in the audio (seconds).
        :param sync: (avClapSync) Synchronization boundaries.
        :param out_name: (str) Filename (not path) for the final output.

        """
        effective_clap = sync.get_audio_clap_with_delay(raw_clap)

        tmp_clap  = os.path.join(self.__work_dir, "_audio_clap.wav")
        tmp_dur   = os.path.join(self.__work_dir, "_audio_dur.wav")
        raw_name  = out_name.replace(".wav", "-audio.wav")
        final_raw = os.path.join(self.__work_dir, raw_name)
        final     = os.path.join(self.__work_dir, out_name)

        # Pass 1: align to clap frame time.
        avAudioOps.adjust_audio_at_clap(
            audio_path, effective_clap, sync.audio_reference_clap, tmp_clap
        )
        self.__log_ok(tmp_clap)

        # Pass 2: match end frame time exactly.
        self.__log(f"  - expected end time of audio: {sync.end_frame_time:.3f}")
        avAudioOps.adjust_audio_duration(tmp_clap, sync.end_frame_time, tmp_dur)
        self.__log_ok(tmp_dur)

        # Pass 3: trim the leading silence up to clap_frame_time.
        self.__log(f"  - expected start time of audio: {sync.clap_frame_time:.3f}")
        avAudioOps.trim_audio(tmp_dur, sync.clap_frame_time, final_raw, begin=True)
        self.__log_ok(final_raw)
        self.__log_audio_info(final_raw)

        # Pass 4: convert to 16kHz mono.
        avAudioOps.to_mono_16k(final_raw, final)
        self.__log_ok(final)
        self.__log_audio_info(final)

        if os.path.isfile(tmp_clap) is True:
            os.remove(tmp_clap)
        if os.path.isfile(tmp_dur) is True:
            os.remove(tmp_dur)

        self.__result.add_synced_file(final_raw)
        self.__result.add_synced_file(final)

    # -----------------------------------------------------------------------

    def __step_trim_videos(self, video_items: list) -> None:
        """Trim each video between its own clap frame and end frame.

        :param video_items: (list) List of (video_media, avClapSync, out_name) tuples.

        """
        self.__log_step(3, "Trim video files")

        for video, sync, video_out in video_items:
            out_path = os.path.join(self.__work_dir, video_out)
            avVideoOps.trim(
                video.path,
                sync.clap_frame_index,
                sync.end_frame_index,
                out_path
            )
            self.__result.add_synced_file(out_path)
            self.__log_ok(out_path)

    # -----------------------------------------------------------------------

    def __step_post_process_videos(self, video_items: list) -> None:
        """Apply crop and copyright overlay to each trimmed video.

        :param video_items: (list) List of (video_media, avClapSync, out_name) tuples.

        """
        self.__log_step(4, "Post-process video files")

        for video, _sync, video_out in video_items:
            current = os.path.join(self.__work_dir, video_out)
            current = self.__apply_crop(video, current)
            current = self.__apply_copyright(current)
            self.__log_video_info(current)
            self.__log_ok(current)

    # -----------------------------------------------------------------------

    def __apply_crop(self, media, video_path: str) -> str:
        """Apply crop to a video if the media file defines a crop region.

        :param media: (avMediaFile) Media file with optional crop parameters.
        :param video_path: (str) Path to the current video file.
        :return: (str) Path to the (possibly cropped) video file.

        """
        if media.has_crop() is False:
            return video_path

        self.__log(f"  - crop: x={media.crop_x} y={media.crop_y} w={media.crop_w} h={media.crop_h}")
        tmp_path = video_path.replace(".mkv", "_tmp_crop.mkv")
        avVideoOps.crop(video_path, media.crop_x, media.crop_y,
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

        self.__log("  - copyright overlay applied")
        tmp_path = video_path.replace(".mkv", "_tmp_copy.mkv")
        avVideoOps.add_copyright(video_path, cfg.output.copyright, tmp_path)
        os.remove(video_path)
        os.rename(tmp_path, video_path)
        return video_path
