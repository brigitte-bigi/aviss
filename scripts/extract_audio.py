"""
:filename: extract_audio.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Extract the audio track from a video file as WAV 48 kHz 16-bit.

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

    python extract_audio.py video

The output file is written next to the input video with a .wav extension.
The audio is converted to 48 kHz, 16-bit PCM.

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
    usage=f"python {os.path.basename(PROGRAM)} video",
    description="Extract the audio track from a video file as WAV 48 kHz 16-bit."
)
parser.add_argument("video", help="Input video file.")

if len(sys.argv) <= 1:
    parser.print_help()
    sys.exit(0)

args = parser.parse_args()

# ---------------------------------------------------------------------------

try:
    check_command("ffmpeg")
    check_file(args.video)
except (EnvironmentError, FileNotFoundError, ValueError) as e:
    print(f"ERROR: {e}")
    sys.exit(1)

wav_out = os.path.splitext(args.video)[0] + ".wav"
if os.path.isfile(wav_out) is True:
    print(f"ERROR: output file already exists: {wav_out}")
    sys.exit(1)

try:
    run_command(
        f"ffmpeg -i '{args.video}' -vn -c:a pcm_s16le -ar 48000 '{wav_out}'",
        check_returncode=True
    )
    check_file(wav_out)
except (EnvironmentError, FileNotFoundError, ValueError) as e:
    print(f"ERROR: {e}")
    sys.exit(1)

print(f"Done: {wav_out}")
