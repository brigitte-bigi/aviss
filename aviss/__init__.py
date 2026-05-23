"""
:filename: __init__.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Public API of AViSS (Audio-Video Synchronization).

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

from aviss.settings import cfg 
from aviss.models import avMediaFile
from aviss.models import avSession
from aviss.models import avSyncResult
from aviss.core.csv_reader import avCsvReader 
from aviss.core.pipeline import avPipeline
from aviss.core.export import avExporter  

__author__ = "Brigitte Bigi"
__copyright__ = "Copyright (C) 2026  Brigitte Bigi, CNRS, Laboratoire Parole et Langage, Aix-en-Provence, France"
__version__ = "1.0"
__all__ = (
    "cfg",
    "avMediaFile",
    "avSession",
    "avSyncResult",
    "avCsvReader",
    "avPipeline",
    "avExporter"
)
