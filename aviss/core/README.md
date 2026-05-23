# aviss.core

Internal processing classes of AViSS. `avPipeline` is the central orchestrator;
all other classes are called by it or feed into it.

## Classes

| Class | Role |
|---|---|
| `avCsvReader` | Parse the input CSV file and produce `avSession` objects |
| `avClapSync` | Compute frame-accurate start/end boundaries from the video clap and fps |
| `avAudioOps` | Audio operations: extract, trim, pad, align to clap, resample |
| `avVideoOps` | Video operations: read metadata, trim, crop, overlay, rotate |
| `avPipeline` | Orchestrate all synchronization steps for one `avSession` |
| `avExporter` | Apply optional post-pipeline exports (SPPAS, montage, WebM) |

## Processing flow inside avPipeline

```
avSession
   │
   ├─ avVideoOps.get_video_info()       ← read actual fps and duration
   │
   ├─ avClapSync(session, fps)          ← compute clap_frame and end_frame
   │
   ├─ avAudioOps.*                      ← align and trim each audio file
   │
   ├─ avVideoOps.trim()                 ← trim each video file
   │
   └─ avVideoOps.crop / add_copyright   ← optional post-processing
```
