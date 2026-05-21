#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# :filename: make_test_data.sh
# :author:   Brigitte Bigi
# :contact:  contact@sppas.org
# :summary:  Generate synthetic test data for AViSS integration tests.
#
#   This file is part of AViSS.
#   Copyright (C) 2026  Brigitte Bigi, CNRS
#   Laboratoire Parole et Langage, Aix-en-Provence, France
#   GNU Affero General Public License v3 or later — see LICENSE.
# ---------------------------------------------------------------------------
#
# PRINCIPLE
# ---------
# Starting from a known pair (demo.mp4, demo.wav), this script builds
# synthetic "raw recording" files by adding material before and after:
#
#   test_video.mp4 = [X s black] + [1 frame CLAP] + [1 s black]
#                  + [demo.mp4]
#                  + [M s black]
#
#   test_audio.wav = [Y s silence] + [1 ms noise] + [1 s silence]
#                  + [demo.wav]
#                  + [N s silence]
#
# X, Y, M, N are drawn independently at random (integer seconds).
# The script writes a ready-to-use test.csv with the exact clap times.
#
# A correct AViSS run on test.csv must reproduce demo.mp4 and demo.wav
# exactly (frame-for-frame, sample-for-sample).
#
# USAGE
# -----
#   ./make_test_data.sh [demo_dir] [output_dir]
#
#   demo_dir   : directory containing demo.mp4 and demo.wav (default: demo)
#   output_dir : directory where test data is written  (default: tests/data)
#
# REQUIREMENTS
# ------------
#   ffmpeg, sox
# ---------------------------------------------------------------------------

set -euo pipefail

# ---------------------------------------------------------------------------
# Parameters
# ---------------------------------------------------------------------------

DEMO_DIR="${1:-demo}"
OUT_DIR="${2:-data}"

DEMO_VIDEO="${DEMO_DIR}/demo.mp4"
DEMO_AUDIO="${DEMO_DIR}/demo.wav"

VIDEO_FPS=30
# Duration of demo.mp4 in seconds (exact, used in CSV).
# Derived from ffprobe to avoid hardcoding.
DEMO_VIDEO_DURATION=""
DEMO_AUDIO_DURATION=""

# Random ranges (seconds, integers).
X_MIN=2;  X_MAX=10   # black frames before CLAP in video
Y_MIN=1;  Y_MAX=8    # silence before noise in audio
M_MIN=2;  M_MAX=6    # black frames after demo in video
N_MIN=2;  N_MAX=6    # silence after demo in audio

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

log() {
    echo "[make_test_data] $*"
}

require_command() {
    if ! command -v "$1" &> /dev/null; then
        echo "ERROR: required command not found: $1" >&2
        exit 1
    fi
}

random_int() {
    # Return a random integer in [min, max].
    local min="$1"
    local max="$2"
    echo $(( min + RANDOM % (max - min + 1) ))
}

seconds_to_time() {
    # Convert a float number of seconds to MM:SS.mmm for the CSV.
    local total="$1"
    local mins
    local secs
    local millis
    mins=$(echo "$total" | awk '{printf "%02d", int($1/60)}')
    secs=$(echo "$total" | awk '{printf "%02d", int($1%60)}')
    millis=$(echo "$total" | awk '{printf "%03d", int(($1 - int($1))*1000)}')
    echo "${mins}:${secs}.${millis}"
}

get_duration() {
    # Return the duration of a media file in seconds (float).
    ffprobe -v error \
            -show_entries format=duration \
            -of default=noprint_wrappers=1:nokey=1 \
            "$1"
}

# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

require_command ffmpeg
require_command ffprobe
require_command sox

if [[ ! -f "${DEMO_VIDEO}" ]]; then
    echo "ERROR: demo video not found: ${DEMO_VIDEO}" >&2
    exit 1
fi
if [[ ! -f "${DEMO_AUDIO}" ]]; then
    echo "ERROR: demo audio not found: ${DEMO_AUDIO}" >&2
    exit 1
fi

mkdir -p "${OUT_DIR}"
TMP_DIR=$(mktemp -d)
trap 'rm -rf "${TMP_DIR}"' EXIT

# ---------------------------------------------------------------------------
# Read demo durations
# ---------------------------------------------------------------------------

DEMO_VIDEO_DURATION=$(get_duration "${DEMO_VIDEO}")
DEMO_AUDIO_DURATION=$(get_duration "${DEMO_AUDIO}")
log "demo.mp4 duration : ${DEMO_VIDEO_DURATION}s"
log "demo.wav duration : ${DEMO_AUDIO_DURATION}s"

# ---------------------------------------------------------------------------
# Draw random values
# ---------------------------------------------------------------------------

X=$(random_int ${X_MIN} ${X_MAX})   # seconds of black before CLAP
Y=$(random_int ${Y_MIN} ${Y_MAX})   # seconds of silence before noise
M=$(random_int ${M_MIN} ${M_MAX})   # seconds of black after demo
N=$(random_int ${N_MIN} ${N_MAX})   # seconds of silence after demo

log "Random values drawn:"
log "  X = ${X}s  (black before CLAP in video)"
log "  Y = ${Y}s  (silence before noise in audio)"
log "  M = ${M}s  (black after demo in video)"
log "  N = ${N}s  (silence after demo in audio)"

# ---------------------------------------------------------------------------
# Compute exact clap times for the CSV
# ---------------------------------------------------------------------------

# video_clap : time of the CLAP frame = X seconds (first frame of the CLAP).
# The CLAP is exactly 1 frame long (1/fps seconds).
VIDEO_CLAP_SECONDS=$(echo "${X}" | awk '{printf "%.6f", $1}')

# audio_clap : time of the 1ms noise burst = Y seconds.
AUDIO_CLAP_SECONDS=$(echo "${Y}" | awk '{printf "%.6f", $1}')

VIDEO_CLAP_STR=$(seconds_to_time "${VIDEO_CLAP_SECONDS}")
AUDIO_CLAP_STR=$(seconds_to_time "${AUDIO_CLAP_SECONDS}")

# delay : 1 second (the 1s black/silence after the clap).
DELAY="1.000"

# duration : exact duration of demo.mp4.
DURATION_STR=$(seconds_to_time "${DEMO_VIDEO_DURATION}")

log "CSV clap times:"
log "  video_clap = ${VIDEO_CLAP_STR}"
log "  audio_clap = ${AUDIO_CLAP_STR}"
log "  delay      = ${DELAY}s"
log "  duration   = ${DURATION_STR}"

# ---------------------------------------------------------------------------
# Build test_video.mp4
# ---------------------------------------------------------------------------

log "Building test_video.mp4 ..."

# Read video properties from demo.mp4.
VIDEO_WIDTH=$(ffprobe -v error -select_streams v:0 \
    -show_entries stream=width -of csv=p=0 "${DEMO_VIDEO}")
VIDEO_HEIGHT=$(ffprobe -v error -select_streams v:0 \
    -show_entries stream=height -of csv=p=0 "${DEMO_VIDEO}")
VIDEO_PIX_FMT=$(ffprobe -v error -select_streams v:0 \
    -show_entries stream=pix_fmt -of csv=p=0 "${DEMO_VIDEO}")

log "  Video: ${VIDEO_WIDTH}x${VIDEO_HEIGHT} @ ${VIDEO_FPS}fps pix_fmt=${VIDEO_PIX_FMT}"

# Part 1a: X seconds of black (before CLAP).
BLACK_BEFORE="${TMP_DIR}/black_before.mp4"
ffmpeg -f lavfi \
    -i "color=c=black:s=${VIDEO_WIDTH}x${VIDEO_HEIGHT}:r=${VIDEO_FPS}:d=${X}" \
    -pix_fmt "${VIDEO_PIX_FMT}" \
    -an "${BLACK_BEFORE}" \
    -nostdin -y -loglevel error

# Part 1b: 1 frame CLAP (white text "CLAP" on black background).
FRAME_DURATION=$(echo "${VIDEO_FPS}" | awk '{printf "%.6f", 1.0/$1}')
CLAP_FRAME="${TMP_DIR}/clap_frame.mp4"
ffmpeg -f lavfi \
    -i "color=c=black:s=${VIDEO_WIDTH}x${VIDEO_HEIGHT}:r=${VIDEO_FPS}:d=${FRAME_DURATION}" \
    -vf "drawtext=text='CLAP':fontsize=120:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2" \
    -pix_fmt "${VIDEO_PIX_FMT}" \
    -frames:v 1 \
    -an "${CLAP_FRAME}" \
    -nostdin -y -loglevel error

# Part 1c: 1 second of black (after CLAP).
BLACK_AFTER_CLAP="${TMP_DIR}/black_after_clap.mp4"
ffmpeg -f lavfi \
    -i "color=c=black:s=${VIDEO_WIDTH}x${VIDEO_HEIGHT}:r=${VIDEO_FPS}:d=1" \
    -pix_fmt "${VIDEO_PIX_FMT}" \
    -an "${BLACK_AFTER_CLAP}" \
    -nostdin -y -loglevel error

# Part 2: demo.mp4 (already without audio).
# Re-encode to ensure identical codec/pixel format for concatenation.
DEMO_VIDEO_TMP="${TMP_DIR}/demo_video.mp4"
ffmpeg -i "${DEMO_VIDEO}" \
    -pix_fmt "${VIDEO_PIX_FMT}" \
    -r "${VIDEO_FPS}" \
    -an "${DEMO_VIDEO_TMP}" \
    -nostdin -y -loglevel error

# Part 3: M seconds of black (after demo).
BLACK_END="${TMP_DIR}/black_end.mp4"
ffmpeg -f lavfi \
    -i "color=c=black:s=${VIDEO_WIDTH}x${VIDEO_HEIGHT}:r=${VIDEO_FPS}:d=${M}" \
    -pix_fmt "${VIDEO_PIX_FMT}" \
    -an "${BLACK_END}" \
    -nostdin -y -loglevel error

# Concatenate all parts.
CONCAT_LIST="${TMP_DIR}/video_concat.txt"
{
    echo "file '${BLACK_BEFORE}'"
    echo "file '${CLAP_FRAME}'"
    echo "file '${BLACK_AFTER_CLAP}'"
    echo "file '${DEMO_VIDEO_TMP}'"
    echo "file '${BLACK_END}'"
} > "${CONCAT_LIST}"

TEST_VIDEO="${OUT_DIR}/test_video.mp4"
ffmpeg -f concat -safe 0 \
    -i "${CONCAT_LIST}" \
    -c:v libx264 -crf 0 -preset ultrafast \
    -pix_fmt "${VIDEO_PIX_FMT}" \
    -an "${TEST_VIDEO}" \
    -nostdin -y -loglevel error

log "  -> ${TEST_VIDEO}"

# ---------------------------------------------------------------------------
# Build test_audio.wav
# ---------------------------------------------------------------------------

log "Building test_audio.wav ..."

# Read audio properties from demo.wav.
AUDIO_RATE=$(soxi -r "${DEMO_AUDIO}")
AUDIO_CHANNELS=$(soxi -c "${DEMO_AUDIO}")
AUDIO_BITS=$(soxi -b "${DEMO_AUDIO}")

log "  Audio: ${AUDIO_RATE}Hz ${AUDIO_CHANNELS}ch ${AUDIO_BITS}bit"

# Part 1: Y seconds of silence (before noise).
SILENCE_BEFORE="${TMP_DIR}/silence_before.wav"
sox -n -r "${AUDIO_RATE}" -c "${AUDIO_CHANNELS}" -b "${AUDIO_BITS}" \
    "${SILENCE_BEFORE}" trim 0.0 "${Y}.0"

# Part 2: 1ms noise burst (the clap sound).
NOISE_BURST="${TMP_DIR}/noise_burst.wav"
sox -n -r "${AUDIO_RATE}" -c "${AUDIO_CHANNELS}" -b "${AUDIO_BITS}" \
    "${NOISE_BURST}" synth 0.001 whitenoise vol 0.8

# Part 3: 1 second of silence (after noise).
SILENCE_AFTER_CLAP="${TMP_DIR}/silence_after_clap.wav"
sox -n -r "${AUDIO_RATE}" -c "${AUDIO_CHANNELS}" -b "${AUDIO_BITS}" \
    "${SILENCE_AFTER_CLAP}" trim 0.0 1.0

# Part 4: N seconds of silence (after demo).
SILENCE_END="${TMP_DIR}/silence_end.wav"
sox -n -r "${AUDIO_RATE}" -c "${AUDIO_CHANNELS}" -b "${AUDIO_BITS}" \
    "${SILENCE_END}" trim 0.0 "${N}.0"

# Concatenate all parts.
TEST_AUDIO="${OUT_DIR}/test_audio.wav"
sox "${SILENCE_BEFORE}" \
    "${NOISE_BURST}" \
    "${SILENCE_AFTER_CLAP}" \
    "${DEMO_AUDIO}" \
    "${SILENCE_END}" \
    "${TEST_AUDIO}"

log "  -> ${TEST_AUDIO}"

# ---------------------------------------------------------------------------
# Write test.csv
# ---------------------------------------------------------------------------

log "Writing test.csv ..."

TEST_CSV="${OUT_DIR}/test.csv"
{
    echo "ID;Session;Serie;audio_file;video_file;audio_clap;video_clap;delay;duration"
    echo "demo;1;1;test_audio.wav;test_video.mp4;${AUDIO_CLAP_STR};${VIDEO_CLAP_STR};${DELAY};${DURATION_STR}"
} > "${TEST_CSV}"

log "  -> ${TEST_CSV}"

# ---------------------------------------------------------------------------
# Write expected values for the integration test
# ---------------------------------------------------------------------------

EXPECTED_FILE="${OUT_DIR}/expected.txt"
{
    echo "# Generated by make_test_data.sh — do not edit manually."
    echo "X=${X}"
    echo "Y=${Y}"
    echo "M=${M}"
    echo "N=${N}"
    echo "VIDEO_CLAP=${VIDEO_CLAP_SECONDS}"
    echo "AUDIO_CLAP=${AUDIO_CLAP_SECONDS}"
    echo "DEMO_VIDEO_DURATION=${DEMO_VIDEO_DURATION}"
    echo "DEMO_AUDIO_DURATION=${DEMO_AUDIO_DURATION}"
    echo "VIDEO_FPS=${VIDEO_FPS}"
} > "${EXPECTED_FIecho "demo;1;1;${TEST_AUDIO};LE}"

log "  -> ${EXPECTED_FILE}"

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

log ""
log "Done. Test data written to: ${OUT_DIR}"
log ""
log "To run the AViSS integration test:"
log "  python -m cli.py sync -c ${TEST_CSV} -l 1 --verbose"
log ""
log "Expected output files:"
log "  demo_S01_s1.wav  (must match ${DEMO_AUDIO} exactly)"
log "  demo_S01_s1.mkv  (must match ${DEMO_VIDEO} frame-for-frame)"
