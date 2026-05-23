# aviss

Public API of AViSS. This package exposes the classes needed for a complete
synchronization workflow.

## Classes

| Class | Role |
|---|---|
| `avMediaFile` | One media file (audio or video) with its clap time and optional crop region |
| `avSession` | One recording session: a pair of media files, a delay, and an expected duration |
| `avSyncResult` | Output of a pipeline run: success flag, synced file paths, processing report |
| `avCsvReader` | Parse an AViSS CSV file into a list of `avSession` objects |
| `avPipeline` | Execute all synchronization steps for one `avSession`, return a `avSyncResult` |
| `avExporter` | Apply optional post-pipeline operations (rotation, SPPAS export, montage) |
| `cfg` | Central configuration object (column names, output fps, CRF, copyright…) |

## Workflow

```
CSV file
   │
   ▼
avCsvReader.read()  →  [avSession, avSession, …]
                            │
                            ▼
                       avPipeline.run()  →  avSyncResult
                                               │
                                               ▼
                                          avExporter
                                    (to_sppas / montage)
```

## Usage examples

Synchronize one row of a CSV file:

```python
from aviss import avCsvReader, avPipeline, avExporter

reader   = avCsvReader("corpus/sessions.csv")
session  = reader.read_row(1)

pipeline = avPipeline(session)
result   = pipeline.run()

if result.success is True:
    exporter = avExporter(result, stem="Laurent_S09_sent",
                        work_dir="Laurent_S09_sent")
    exporter.to_sppas()
    exporter.montage()
```

Synchronize all rows:

```python
from aviss import avCsvReader, avPipeline

reader   = avCsvReader("corpus/sessions.csv")
sessions = reader.read()

for session in sessions:
    result = avPipeline(session).run()
    if result.success is False:
        print(result.report)
```

## Customizing settings

Place a `settings_user.py` file in the same directory as your CSV file,
then override only what you need:

```python
cfg.output.crf              = 14
cfg.output.copyright        = "Copyright (C) 2026 CNRS | LPL"
cfg.sync.col_audio_file     = "my_audio"
```

`settings_user.py` is loaded automatically from the CSV directory at sync time.
