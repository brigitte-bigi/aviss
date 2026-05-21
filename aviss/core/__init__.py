"""
:filename: __init__.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Public API of the AViSS core package.

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

from aviss.core.audio_ops import AudioOps
from aviss.core.video_ops import VideoOps
from aviss.core.clap_sync import ClapSync
from aviss.core.pipeline import Pipeline
from aviss.core.csv_reader import CsvReader
from aviss.core.export import Exporter

__all__ = (
    "AudioOps",
    "VideoOps",
    "ClapSync",
    "Pipeline",
    "CsvReader",
    "Exporter",
)
