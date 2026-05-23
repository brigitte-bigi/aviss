"""
:filename: mp4_to_webm.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Convert an MP4 video to WebM (libvpx-vp9, two-pass).

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

Usage
-----

    python mp4_to_webm.py video.mp4 [audio.wav]

The output file is written next to the input video with a .webm extension.
The optional audio file replaces the video's audio track in the output.

Requirements
------------
    ffmpeg

"""

import os
import sys
from argparse import ArgumentParser

from aviss.utils import check_file, check_command, run_command

# ---------------------------------------------------------------------------

PROGRAM = os.path.abspath(__file__)
parser = ArgumentParser(
    usage=f"python {os.path.basename(PROGRAM)} video.mp4 [audio.wav]",
    description="Convert an MP4 video to WebM (libvpx-vp9, two-pass)."
)
parser.add_argument("video", help="Input MP4 file.")
parser.add_argument("audio", nargs="?", default=None,
                    help="Optional audio file to mux into the output.")

if len(sys.argv) <= 1:
    parser.print_help()
    sys.exit(0)

args = parser.parse_args()

# ---------------------------------------------------------------------------

try:
    check_command("ffmpeg")
    check_file(args.video)
    if args.audio is not None:
        check_file(args.audio)
except (EnvironmentError, FileNotFoundError, ValueError) as e:
    print(f"ERROR: {e}")
    sys.exit(1)

webm_out = os.path.splitext(args.video)[0] + ".webm"
if os.path.isfile(webm_out) is True:
    print(f"ERROR: output file already exists: {webm_out}")
    sys.exit(1)

# ---------------------------------------------------------------------------

if args.audio is not None:
    inputs = f"-i '{args.video}' -i '{args.audio}'"
    audio_opts = "-c:a libvorbis -q:a 5 -map 0:v:0 -map 1:a:0"
else:
    inputs = f"-i '{args.video}'"
    audio_opts = "-an"

try:
    run_command(
        f"ffmpeg {inputs} -b:v 0 -crf 16 -pass 1 -an -f webm -y /dev/null",
        check_returncode=True
    )
    run_command(
        f"ffmpeg {inputs} -b:v 0 -crf 16 -pass 2 -c:v libvpx-vp9 {audio_opts} '{webm_out}'",
        check_returncode=True
    )
    check_file(webm_out)
except (EnvironmentError, FileNotFoundError, ValueError) as e:
    print(f"ERROR: {e}")
    sys.exit(1)

print(f"Done: {webm_out}")
