```
-------------------------------------------------------------------------

         █████╗  ██╗   ██╗ ██╗  ███████╗  ███████╗
        ██╔══██╗ ██║   ██║ ██║  ██╔════╝  ██╔════╝
        ███████║ ██║   ██║ ██║  ███████╗  ███████╗
        ██╔══██║ ╚██╗ ██╔╝ ██║       ██║       ██║
        ██║  ██║  ╚████╔╝  ██║  ███████║  ███████║
        ╚═╝  ╚═╝   ╚═══╝   ╚═╝  ╚══════╝  ╚══════╝

        Audio-Video Synchronization in Python

        Copyright (C) 2026 Brigitte Bigi, CNRS
   Laboratoire Parole et Langage, Aix-en-Provence, France
-------------------------------------------------------------------------
```

# AViSS description

## Overview

### Use cases

You recorded a speaker with one or two cameras and one or two separate audio
recorders. You used a clap to mark a synchronization point. Now you need all
your media files trimmed and aligned to the exact same frame boundary — ready
for phonetic analysis or corpus annotation.

`AViSS` is the tool you need.

### Features

AViSS performs frame-accurate, clap-based synchronization of audio and video
files for speech corpus recordings. It is designed for researchers who need
reproducible, high-quality media preparation without manual editing.

Among others, it allows the following:

- Frame-accurate video trimming via OpenCV / SPPAS
- Clap-based audio alignment (trim or pad to match the video frame boundary)
- Support for 1 or 2 audio files and 1 or 2 video files per session
- Optional video crop (x, y, w, h per video)
- Optional copyright overlay on video
- Optional video rotation (portrait mode)
- Optional mono 16 kHz WAV export for automatic annotation
- Optional MP4 montage (H.264/AAC) for distribution
- Optional WebM montage (libvpx-vp9, two-pass) for web distribution
- Batch processing from a CSV file
- Fully configurable column names and output filename structure

### How it works

AViSS is a faithful Python migration of the original montage scripts
(`montage_step1.py` / `montage.py`, B. Bigi, CNRS/LPL 2021-2024)
distributed with the CLeLfPC corpus (https://hdl.handle.net/11403/clelfpc).
The algorithm below is reproduced verbatim from those scripts.

**Notation**

| Symbol | Meaning |
|--------|---------|
| `vc`   | `video_clap + delay` — effective clap time in the video (seconds) |
| `fps`  | frame rate of the video (frames/second) |
| `dur`  | expected output duration (seconds) |

**Step 1 — clap frame (primary / reference video)**

```
clap_frame_index = int(vc * fps)           # floor, 0-based
clap_frame_time  = clap_frame_index / fps
clap_delta       = vc - clap_frame_time    # sub-frame offset, in [0, 1/fps)
```

**Step 2 — end frame (first excluded frame)**

```
end_frame_index = 1 + int((vc + dur) * fps)
end_frame_time  = end_frame_index / fps
```

**Step 3 — cross-sync (secondary video, fps2 ≠ fps_ref)**

When two cameras have different frame rates, the reference camera is the
one with the lowest fps. Its `clap_delta` is propagated to the secondary
camera so both outputs share the same sub-frame offset at the clap.

```
shift_frames     = int(reference_delta * fps2)
clap_frame_index = int(vc2 * fps2) - shift_frames
end_frame_index  = 1 + int((vc2 + dur) * fps2) + shift_frames
```

Note: the formula uses `int(A*fps) - int(d*fps)`, not `int((A-d)*fps)`.
These can differ by 1 frame when `frac(A*fps) < frac(d*fps)`.

**Audio alignment (per audio file)**

```
Pass 1: shift audio so its effective clap (audio_clap + delay)
        matches vc — trim from the start or prepend silence.
Pass 2: pad with silence or trim the end to reach end_frame_time.
Pass 3: trim clap_frame_time from the start.
```

The output audio starts at the clap frame boundary, preserving the
`clap_delta` sub-frame offset between the clap and the first sample.

### Scientific context

AViSS was developed at the Laboratoire Parole et Langage (LPL), CNRS,
Aix-en-Provence, France, for the preparation of speech corpora used in
phonetic research, including cued speech and read speech corpora.


## Install AViSS

### Requirements

The following external programs must be installed and available in the PATH:

- `ffmpeg` — video and audio processing
- `sox` — audio processing

### From PyPI

```bash
> python -m pip install aviss
```

### From its wheel package

Download the wheel file (aviss-xxx.whl) and install it with:

```bash
> python -m pip install aviss-xxx.whl
```

### From the repository

Download or clone the repository, then install in editable mode:

```bash
> git clone https://github.com/brigitte-bigi/AViSS.git
> cd AViSS
> python -m pip install -e .
```

### AViSS content

The AViSS package includes the following folders and files:

1. `aviss/` : the source code of the API
2. `aviss/core/` : pipeline, synchronization logic, audio and video operations
3. `scripts/` : ready-to-use scripts for common workflows
4. `tests/` : unit tests
5. `docs/` : code documentation
6. `pyproject.toml` : package configuration


## Quick start

### Prepare the CSV file

The input CSV file describes one recording session per row. The first row
is the header. Columns are separated by `;` (or `,`).

The following columns are required (names are configurable via `settings_user.toml`):

| Column | Description |
|---|---|
| `audio_file` | relative path to the audio file |
| `audio_clap` | clap time in the audio (MM:SS.mmm) |
| `video_file` | relative path to the video file |
| `video_clap` | clap time in the video (MM:SS.mmm) |
| `delay` | offset after the clap before cutting (seconds) |
| `duration` | expected output duration (MM:SS.mmm) |

Optional columns for crop, other media files, and output filename metadata
are described in the `sync` section of [Customizing settings](#customizing-settings).

Example:

```
ID;avSession;Serie;audio_file;video_file;audio_clap;video_clap;delay;duration
spk1;9;2;audio/RME_0038.wav;video/MVI_0038.MP4;00:03.843;00:06.410;0.200;04:08.250
spk2;8;1;audio/RME_0035.wav;video/MVI_0035.MP4;00:04.787;00:09.995;6.230;02:57.000
```

### Command-line usage

Synchronize one row:

```bash
> aviss sync -c corpus/sessions.csv -l 1
```

Synchronize all rows:

```bash
> aviss sync -c corpus/sessions.csv
```

Synchronize and produce a distribution MP4:

```bash
> aviss sync -c corpus/sessions.csv -l 1 --montage
```

Synchronize and produce a WebM for web distribution:

```bash
> aviss sync -c corpus/sessions.csv -l 1 --webm
```

Print the full processing report:

```bash
> aviss sync -c corpus/sessions.csv -l 1 --verbose
```

### Python API usage

```python
from aviss import avCsvReader, avPipeline, avExporter

# Parse one row from the CSV
reader  = avCsvReader("corpus/sessions.csv")
session = reader.read_row(1)

# Run the synchronization pipeline
pipeline = avPipeline(session)
result   = pipeline.run()

if result.success is True:
    exporter = avExporter(result,
                        stem="spk1_S09_s2",
                        work_dir="spk1_S09_s2")
    exporter.montage()

# Process all rows
sessions = avCsvReader("corpus/sessions.csv").read()
for session in sessions:
    result = avPipeline(session).run()
    if result.success is False:
        print(session, result.report)
```

### Customizing settings

Place a `settings_user.toml` file in the same directory as your CSV file,
then override only what you need:

```toml
[output]
crf       = 14
video_fps = 25.0
copyright = "Copyright (C) 2026 CNRS | LPL"

# Rotation — one integer per video in order.
# -1 = no rotation · 0 = CCW+vflip · 1 = CW · 2 = CCW portrait · 3 = CW+vflip
rotate = [2]        # single video, portrait CCW
# rotate = [-1, 2] # two videos: front=none, side=CCW portrait

[[output.name_cols]]
col    = "ID"
prefix = ""
fmt    = ""

[[output.name_cols]]
col    = "avSession"
prefix = "S"
fmt    = "02d"

[[output.name_cols]]
col    = "SerieLabel"
prefix = ""
fmt    = ""

[sync]
col_audio_file = "my_audio"
```

`settings_user.toml` is loaded automatically from the CSV directory at sync time.

#### output keys

| Key | Default | Description |
|---|---|---|
| `crf` | `18` | Video encoding quality (H.264 CRF). Lower = better quality, larger file. Range: 0–51. |
| `video_fps` | `50.0` | Native frame rate of the recording camera (frames per second). |
| `copyright` | _(none)_ | Text overlaid on the video (bottom-left). Use `\\:` to escape colons (ffmpeg). |
| `rotate` | _(none)_ | Per-video transpose list. See values below. |
| `output_sep` | `"_"` | Separator between tokens in the output filename. |
| `work_dir_suffix` | `""` | Suffix appended to the working directory name. |

Rotate values (one integer per video, in order — `-1` = no rotation):

| Value | Effect |
|---|---|
| `-1` | No rotation |
| `0` | 90° counter-clockwise + vertical flip |
| `1` | 90° clockwise |
| `2` | 90° counter-clockwise (portrait mode) |
| `3` | 90° clockwise + vertical flip |

#### sync keys

| Key | Default | Description |
|---|---|---|
| `col_audio_file` | `"audio_file"` | CSV column name for the audio file path. |
| `col_audio_clap` | `"audio_clap"` | CSV column name for the audio clap time. |
| `col_video_file` | `"video_file"` | CSV column name for the video file path. |
| `col_video_clap` | `"video_clap"` | CSV column name for the video clap time. |
| `col_video_name` | `"video_name"` | CSV column name for the optional video label (used in output filename suffix). |
| `col_video_crop_x` | `"video_crop_x"` | CSV column name for the crop left edge (pixels). |
| `col_video_crop_y` | `"video_crop_y"` | CSV column name for the crop top edge (pixels). |
| `col_video_crop_w` | `"video_crop_w"` | CSV column name for the crop width (pixels). |
| `col_video_crop_h` | `"video_crop_h"` | CSV column name for the crop height (pixels). |
| `col_delay` | `"delay"` | CSV column name for the delay after the clap (seconds). |
| `col_duration` | `"duration"` | CSV column name for the expected output duration. |

#### output.name_cols format

Each `[[output.name_cols]]` entry defines one token in the output filename:

| Key | Type | Description |
|---|---|---|
| `col` | str | CSV column header whose value is used |
| `prefix` | str | String prepended to the value (`"S"`, `"T"`, `""` for none) |
| `fmt` | str | `""` → raw string · `"02d"` → zero-padded integer · `"d"` → plain integer |

Tokens are joined with `output_sep` (default `"_"`).
A column whose cell is empty in the CSV is silently skipped.

Example: with `col = "avSession"`, `prefix = "S"`, `fmt = "02d"` and cell value `9`, the token is `S09`.


## Test the source code

Install the optional test dependencies:

```bash
> python -m pip install ".[dev]"
```

### Unit tests

Run the unit test suite with coverage (requires `coverage`, included in the
virtual environment):

```bash
> .venv/bin/python -m coverage run -m unittest discover -s tests -p "test_*.py" \
  && .venv/bin/python -m coverage report -m
```

Expected overall coverage: **≥ 73 %**.

If `coverage` is not installed, run the tests without it:

```bash
> .venv/bin/python -m unittest discover -s tests -p "test_*.py"
```

### Integration test

The integration test uses synthetic media files built from the demo files
shipped in `tests/demo/`.

#### Generate test data

```
bash make_test_data.sh [demo_dir] [output_dir] [n_videos] [n_audios]
```

| Argument | Default | Description |
|---|---|---|
| `demo_dir` | `demo` | Directory containing `demo.mp4` and `demo.wav` |
| `output_dir` | `data` | Directory where test files are written |
| `n_videos` | `1` | Number of video files to generate |
| `n_audios` | `1` | Number of audio files to generate |

Each generated video/audio file contains random silence/black before and
after the content so that every run exercises a different synchronization
offset.

**Single video + single audio (default):**

```bash
> cd tests && bash make_test_data.sh && cd ..
```

Writes `tests/data/test_audio.wav`, `tests/data/test_video.mp4` and
`tests/data/test.csv`.

**Two videos + one audio:**

```bash
> cd tests && bash make_test_data.sh demo data 2 1 && cd ..
```

Writes `test_video.mp4`, `test_video2.mp4`, `test_audio.wav` and a CSV
with columns `video_file`, `video_file2`.

**Two videos + two audios:**

```bash
> cd tests && bash make_test_data.sh demo data 2 2 && cd ..
```

Then run the pipeline on the first CSV row:

```bash
> .venv/bin/python cli.py sync -c tests/data/test.csv -l 1 --verbose
```

**Expected output — audio** (`ffprobe tests/data/demo_S01/demo_S01.wav`):

```
Duration: 00:00:10.47, bitrate: 256 kb/s
Stream #0:0: Audio: pcm_s16le, 16000 Hz, 1 channels, s16, 256 kb/s
```

**Expected output — video** (`ffprobe tests/data/demo_S01/demo_S01.mkv`):

```
Duration: 00:00:10.47, start: 0.000000, bitrate: 3288 kb/s
```

Both files must have the same duration as `tests/demo/demo.mp4`.


## Scripts

### mix_mono.py — mix two mono audio files

Combines two mono WAV files into a single mono WAV by averaging both
channels. Useful when two microphones recorded the same speaker and the
result must be a single audio file before synchronization.

```bash
> python scripts/mix_mono.py audio1.wav audio2.wav output.wav
```

| Argument | Description |
|---|---|
| `audio1` | First mono WAV file |
| `audio2` | Second mono WAV file |
| `output` | Output mono WAV file (must not already exist) |

Requires `sox`. Both input files must be mono WAV at the same sample rate.


## Projects using AViSS

AViSS was developed for the following corpora at LPL, CNRS:

- CLeLfPC — Corpus de Lecture en Langue Française Parlée Complétée
- AutoCuedSpeech — automatic annotation of cued speech recordings

*Contact the author if you want to add a project here.*


## Help / How to contribute

If you want to report a bug or suggest a feature, please send an e-mail
to the author. Any and all constructive comments are welcome.

If you plan to contribute to the code, please read carefully and agree
both the code of conduct and the code style guide.


## AViSS Documentation

Documentation is generated from the source code using ClammingPy:
<https://github.com/brigitte-bigi/ClammingPy>

To generate the documentation locally:

```bash
> python -m pip install ClammingPy
> python makedoc.py
```


## License/Copyright

See the accompanying LICENSE and AUTHORS.md files for the full list of
contributors.

Copyright (C) 2026 Brigitte Bigi, CNRS
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
along with this program. If not, see <https://www.gnu.org/licenses/>.


## Changes

- Version 1.0:

    * Initial version.
    * Support for ANY audio files and ANY video files per session.
    * Optional crop, copyright overlay, rotation, mono 16 kHz WAV export,
      MP4 and WebM montage.
