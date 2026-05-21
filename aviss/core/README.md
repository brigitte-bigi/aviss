# aviss.core

Internal processing classes of AViSS. `Pipeline` is the central orchestrator;
all other classes are called by it or feed into it.

## Classes

| Class | Role |
|---|---|
| `CsvReader` | Parse the input CSV file and produce `Session` objects |
| `ClapSync` | Compute frame-accurate start/end boundaries from the video clap and fps |
| `AudioOps` | Audio operations: extract, trim, pad, align to clap, resample |
| `VideoOps` | Video operations: read metadata, trim, crop, overlay, rotate |
| `Pipeline` | Orchestrate all synchronization steps for one `Session` |
| `Exporter` | Apply optional post-pipeline exports (SPPAS, montage, WebM) |

## Processing flow inside Pipeline

```
Session
   │
   ├─ VideoOps.get_video_info()       ← read actual fps and duration
   │
   ├─ ClapSync(session, fps)          ← compute clap_frame and end_frame
   │
   ├─ AudioOps.*                      ← align and trim each audio file
   │
   ├─ VideoOps.trim()                 ← trim each video file
   │
   └─ VideoOps.crop / add_copyright   ← optional post-processing
```
