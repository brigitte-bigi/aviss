"""
:filename: mix_mono.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Mix two mono audio files into a single mono file.

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

    python mix_mono.py audio1.wav audio2.wav output.wav

Both input files must be mono WAV. The output is a mono WAV at the same
sample rate and bit depth as audio1.

Requirements
------------
    sox

"""

import os
import sys
import shlex
import subprocess
from argparse import ArgumentParser

# ---------------------------------------------------------------------------


def check_file(path):
    """Exit if the given file does not exist or is empty.

    :param path: (str) Path to check.

    """
    if os.path.isfile(path) is False:
        print(f"ERROR: file not found: {path}")
        sys.exit(1)
    if os.path.getsize(path) == 0:
        print(f"ERROR: file is empty: {path}")
        sys.exit(1)


def check_command(name):
    """Exit if the given command is not available on the system.

    :param name: (str) Command name.

    """
    try:
        subprocess.call(
            [name],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except OSError:
        print(f"ERROR: command not found: {name}")
        sys.exit(1)


def run_command(command):
    """Execute a shell command and print its output.

    :param command: (str) Command string to execute.

    """
    print(f"Run: {command}")
    args = shlex.split(command)
    proc = subprocess.Popen(
        args,
        shell=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    stdout, _ = proc.communicate()
    if len(stdout) > 0:
        print(stdout.decode("utf-8", errors="replace"))
    if proc.returncode != 0:
        print(f"ERROR: command failed with code {proc.returncode}.")
        sys.exit(1)


# ---------------------------------------------------------------------------

PROGRAM = os.path.abspath(__file__)
parser = ArgumentParser(
    usage=f"python {os.path.basename(PROGRAM)} audio1 audio2 output",
    description="Mix two mono audio files into a single mono file."
)
parser.add_argument("audio1", help="First mono WAV file.")
parser.add_argument("audio2", help="Second mono WAV file.")
parser.add_argument("output", help="Output mono WAV file.")

if len(sys.argv) <= 1:
    parser.print_help()
    sys.exit(0)

args = parser.parse_args()

# ---------------------------------------------------------------------------

check_command("sox")
check_file(args.audio1)
check_file(args.audio2)

if os.path.isfile(args.output) is True:
    print(f"ERROR: output file already exists: {args.output}")
    sys.exit(1)

# Sox merges two mono files into one mono file by averaging the two channels.
command = f"sox -m '{args.audio1}' '{args.audio2}' '{args.output}'"
run_command(command)

check_file(args.output)
print(f"Done: {args.output}")
