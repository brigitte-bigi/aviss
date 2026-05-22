"""
:filename: cli.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Command-line interface for AViSS.

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

Usage examples
--------------

Synchronize one row::

    aviss sync -c corpus/sessions.csv -l 1

Synchronize all rows::

    aviss sync -c corpus/sessions.csv

Synchronize with montage output::

    aviss sync -c corpus/sessions.csv -l 1 --montage

Synchronize and produce SPPAS-ready audio::

    aviss sync -c corpus/sessions.csv -l 1 --sppas

Synchronize, rotate portrait, produce montage::

    aviss sync -c corpus/sessions.csv -l 1 --rotate 2 --montage

Override CRF for this run::

    aviss sync -c corpus/sessions.csv --crf 14

"""

import os
import sys
import argparse

from aviss.settings import cfg
from aviss.core.csv_reader import CsvReader
from aviss.core.pipeline import Pipeline
from aviss.core.export import Exporter
from aviss.utils import aviss_logger, build_output_name

# ---------------------------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    """Build and return the argument parser for the AViSS CLI.

    :return: (argparse.ArgumentParser) Configured argument parser.

    """
    parser = argparse.ArgumentParser(
        prog="aviss",
        description=(
            "AViSS — Audio-Video Synchronization.\n"
            "Synchronize one or more audio files with one or two videos "
            "using a clap as the synchronization reference."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", metavar="command")
    subparsers.required = True

    # -- sync subcommand --
    sync_parser = subparsers.add_parser(
        "sync",
        help="Synchronize media files from a CSV file.",
        description="Synchronize audio and video files described in a CSV file.",
    )

    sync_parser.add_argument(
        "-c", "--csv",
        required=True,
        metavar="FILE",
        help="Path to the input CSV file."
    )
    sync_parser.add_argument(
        "-l", "--line",
        type=int,
        default=None,
        metavar="N",
        help=(
            "1-based index of the data row to process. "
            "If omitted, all rows are processed."
        )
    )
    sync_parser.add_argument(
        "--crf",
        type=int,
        default=None,
        metavar="N",
        help=(
            f"CRF encoding quality in [0, 51]. "
            f"Overrides cfg.output.crf (default: {cfg.output.crf})."
        )
    )
    sync_parser.add_argument(
        "--fps",
        type=float,
        default=None,
        metavar="N",
        help=(
            f"Camera frame rate in frames per second. "
            f"Overrides cfg.output.video_fps (default: {cfg.output.video_fps})."
        )
    )
    sync_parser.add_argument(
        "--montage",
        action="store_true",
        default=False,
        help="Produce a compressed MP4 montage (audio + video) for distribution."
    )
    sync_parser.add_argument(
        "--webm",
        action="store_true",
        default=False,
        help="Produce a WebM montage (libvpx-vp9, two-pass) for web distribution."
    )
    sync_parser.add_argument(
        "--rotate",
        type=int,
        nargs="+",
        default=None,
        metavar="T",
        help=(
            "Rotate one or more videos using the ffmpeg transpose filter. "
            "One value per video, in order: --rotate 2 0 rotates video 1 (CCW) and video 2 (CW). "
            "Values: 0=CCW+vflip, 1=CW, 2=CCW (portrait), 3=CW+vflip."
        )
    )
    sync_parser.add_argument(
        "--verbose",
        action="store_true",
        default=False,
        help="Print the full processing report for each session."
    )

    return parser

# ---------------------------------------------------------------------------


def _apply_overrides(args: argparse.Namespace) -> None:
    """Apply command-line overrides to cfg before processing.

    :param args: (argparse.Namespace) Parsed command-line arguments.

    """
    if args.crf is not None:
        cfg.output.crf = args.crf

    if args.fps is not None:
        cfg.output.video_fps = args.fps

# ---------------------------------------------------------------------------


def _process_session(session, args: argparse.Namespace) -> bool:
    """Run the pipeline and optional exports for a single session.

    :param session: (Session) Session to process.
    :param args: (argparse.Namespace) Parsed command-line arguments.
    :return: (bool) True if processing succeeded.

    """
    stem = build_output_name(
        session.output_name_meta,
        cfg.output.output_name_cols,
        cfg.output.output_sep
    )
    work_dir = stem + cfg.output.work_dir_suffix

    aviss_logger.configure(os.path.join(work_dir, stem + ".log"))

    print(f"  Processing: {stem}")

    result = Pipeline(session).run()
    aviss_logger.close()

    if args.verbose is True:
        for message in result.report:
            print(f"    {message}")

    if result.success is False:
        print(f"  FAILED: {stem}")
        for message in result.report:
            if message.startswith("ERROR") is True:
                print(f"    {message}")
        return False

    # Optional export operations.
    if args.montage is True or args.webm is True or args.rotate is not None:
        try:
            exporter = Exporter(result, stem=stem, work_dir=work_dir)

            if args.rotate is not None:
                exporter.rotate(transpose_list=args.rotate)
            if args.montage is True:
                exporter.montage()
            if args.webm is True:
                exporter.webm()
        
        except Exception as e:
            print(f"  Export failed: {e}")
            return False

    print(f"  OK: {stem}")
    return True

# ---------------------------------------------------------------------------


def _cmd_sync(args: argparse.Namespace) -> int:
    """Execute the sync subcommand.

    :param args: (argparse.Namespace) Parsed command-line arguments.
    :return: (int) Exit code: 0 on success, 1 if any session failed.

    """
    _apply_overrides(args)
    cfg.load_user_settings(os.path.dirname(os.path.abspath(args.csv)))

    try:
        reader = CsvReader(args.csv)
    except (TypeError, FileNotFoundError, ValueError) as e:
        print(f"Error: cannot read CSV file: {e}")
        return 1

    # Single row mode.
    if args.line is not None:
        print(f"AViSS sync — {args.csv} row {args.line}")
        try:
            session = reader.read_row(args.line)
        except (TypeError, ValueError) as e:
            print(f"Error: cannot parse row {args.line}: {e}")
            return 1

        success = _process_session(session, args)
        return 0 if success is True else 1

    # All rows mode.
    print(f"AViSS sync — {args.csv} (all rows)")
    try:
        sessions = reader.read()
    except ValueError as e:
        print(f"Error: cannot parse CSV: {e}")
        return 1

    if len(sessions) == 0:
        print("Warning: no data rows found in the CSV file.")
        return 0

    print(f"  {len(sessions)} session(s) to process.")
    n_ok     = 0
    n_failed = 0
    for session in sessions:
        success = _process_session(session, args)
        if success is True:
            n_ok += 1
        else:
            n_failed += 1

    print(f"\nDone: {n_ok} succeeded, {n_failed} failed.")
    return 0 if n_failed == 0 else 1

# ---------------------------------------------------------------------------


def main() -> None:
    """Entry point for the aviss command-line tool.

    """
    parser = _build_parser()
    args   = parser.parse_args()

    if args.command == "sync":
        exit_code = _cmd_sync(args)
    else:
        parser.print_help()
        exit_code = 1

    sys.exit(exit_code)

# ---------------------------------------------------------------------------

if __name__ == "__main__":
    main()
