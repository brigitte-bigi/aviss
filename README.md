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
- Optional mono 16 kHz WAV export for SPPAS automatic annotation
- Optional MP4 montage (H.264/AAC) for distribution
- Optional WebM montage (libvpx-vp9, two-pass) for web distribution
- Batch processing from a CSV file
- Fully configurable column names and output filename structure

### How it works

The synchronization principle is:

1. The clap time in the video is snapped to the nearest frame boundary
   (frame-accurate, guaranteed by OpenCV via SPPAS).
2. A configurable delay is applied after the clap — the cut starts after
   the clap, not on it.
3. All audio files are shifted (trim or pad with silence) so that their own
   clap coincides with the video frame boundary.
4. All audio files are padded or trimmed to match the exact frame duration
   of the video output.

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

The following columns are required (names are configurable in `settings.py`):

| Column | Description |
|---|---|
| `audio_file` | relative path to the audio file |
| `audio_clap` | clap time in the audio (MM:SS.mmm) |
| `video_file` | relative path to the video file |
| `video_clap` | clap time in the video (MM:SS.mmm) |
| `delay` | offset after the clap before cutting (seconds) |
| `duration` | expected output duration (MM:SS.mmm) |

Optional columns for crop, secondary media, and output filename metadata
are described in `aviss/settings.py`.

Example:

```
ID;Session;Serie;audio_file;video_file;audio_clap;video_clap;delay;duration
Laurent;9;2;audio/RME_0038.wav;video/MVI_0038.MP4;00:03.843;00:06.410;0.200;04:08.250
Laurent;8;1;audio/RME_0035.wav;video/MVI_0035.MP4;00:04.787;00:09.995;6.230;02:57.000
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

Synchronize and produce a SPPAS-ready mono 16 kHz audio:

```bash
> aviss sync -c corpus/sessions.csv -l 1 --sppas
```

Rotate to portrait and produce montage:

```bash
> aviss sync -c corpus/sessions.csv -l 1 --rotate 2 --montage
```

Rotate video 1 to portrait, video 2 unchanged:

```bash
> aviss sync -c corpus/sessions.csv -l 1 --rotate 2
```

Rotate video 1 and video 2 independently:

```bash
> aviss sync -c corpus/sessions.csv -l 1 --rotate 2 1
```

`--rotate` accepts one value per video, in order. Transpose values:

| Value | Effect |
|---|---|
| `0` | 90° counter-clockwise + vertical flip |
| `1` | 90° clockwise |
| `2` | 90° counter-clockwise — portrait mode |
| `3` | 90° clockwise + vertical flip |

Override encoding quality for this run:

```bash
> aviss sync -c corpus/sessions.csv --crf 14
```

Print the full processing report:

```bash
> aviss sync -c corpus/sessions.csv -l 1 --verbose
```

### Python API usage

```python
from aviss import CsvReader, Pipeline, Exporter

# Parse one row from the CSV
reader  = CsvReader("corpus/sessions.csv")
session = reader.read_row(1)

# Run the synchronization pipeline
pipeline = Pipeline(session)
result   = pipeline.run()

if result.success is True:
    exporter = Exporter(result,
                        stem="Laurent_S09_s2",
                        work_dir="Laurent_S09_s2")
    exporter.to_sppas()
    exporter.montage()

# Process all rows
sessions = CsvReader("corpus/sessions.csv").read()
for session in sessions:
    result = Pipeline(session).run()
    if result.success is False:
        print(session, result.report)
```

### Customizing settings

Place a `settings_user.py` file in the same directory as your CSV file,
then override only what you need:

```python
cfg.output.crf              = 14
cfg.output.video_fps        = 25.
cfg.output.copyright        = "Copyright (C) 2026 CNRS | LPL"
cfg.sync.col_audio_file     = "my_audio"

cfg.output.output_name_cols = [
    ("ID",         "",  None),
    ("Session",    "S", "02d"),
    ("SerieLabel", "",  None),
]
```

`settings_user.py` is loaded automatically from the CSV directory at sync time.

#### output_name_cols format

Each entry is a 3-tuple `(csv_column_name, prefix, fmt)`:

| Field | Type | Description |
|---|---|---|
| `csv_column_name` | str | CSV column header whose value is used |
| `prefix` | str | String prepended to the value (`"S"`, `"T"`, `""` for none) |
| `fmt` | str or None | `None` → raw string · `"02d"` → zero-padded integer · `"d"` → plain integer |

Tokens are joined with `cfg.output.output_sep` (default `"_"`).
A column whose cell is empty in the CSV is silently skipped.

Example: with `("Session", "S", "02d")` and cell value `9`, the token is `S09`.


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

- Version 0.1:

    * Initial version.
    * Support for ANY audio files and ANY video files per session.
    * Optional crop, copyright overlay, rotation, SPPAS export,
      MP4 and WebM montage.
