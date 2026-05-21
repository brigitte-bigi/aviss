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

Typical usage
-------------

Synchronize one row of a CSV file::

    from aviss import CsvReader, Pipeline, Exporter

    reader   = CsvReader("corpus/sessions.csv")
    session  = reader.read_row(1)

    pipeline = Pipeline(session)
    result   = pipeline.run()

    if result.success is True:
        exporter = Exporter(result, stem="Laurent_S09_sent",
                            work_dir="Laurent_S09_sent")
        exporter.to_sppas()
        exporter.montage()

Synchronize all rows::

    from aviss import CsvReader, Pipeline

    reader   = CsvReader("corpus/sessions.csv")
    sessions = reader.read()

    for session in sessions:
        result = Pipeline(session).run()
        if result.success is False:
            print(result.report)

Access or override settings::

    from aviss import cfg

    cfg.output.crf = 14
    cfg.output.copyright = "Copyright (C) 2026 CNRS | LPL"
    cfg.sync.col_audio_file = "my_audio"

"""

from aviss.settings import cfg 
from aviss.models import MediaFile
from aviss.models import Session
from aviss.models import SyncResult
from aviss.core.csv_reader import CsvReader 
from aviss.core.pipeline import Pipeline
from aviss.core.export import Exporter  

__author__ = "Brigitte Bigi"
__copyright__ = "Copyright (C) 2026  Brigitte Bigi, CNRS, Laboratoire Parole et Langage, Aix-en-Provence, France"
__version__ = "0.1"
__all__ = (
    "cfg",
    "MediaFile",
    "Session",
    "SyncResult",
    "CsvReader",
    "Pipeline",
    "Exporter"
)
