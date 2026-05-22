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
#   test_video[N].mp4 = [X s black] + [1 frame CLAP] + [1 s black]
#                     + [demo.mp4]
#                     + [M s black]
#
#   test_audio[N].wav = [Y s silence] + [1 ms noise] + [1 s silence]
#                     + [demo.wav]
#                     + [P s silence]
#
# X, Y, M, P are drawn independently at random (integer seconds) per file.
# The script writes a ready-to-use test.csv with the exact clap times.
#
# A correct AViSS run on test.csv must reproduce demo.mp4 and demo.wav
# exactly (frame-for-frame, sample-for-sample).
#
# USAGE
# -----
#   ./make_test_data.sh [demo_dir] [output_dir] [n_videos] [n_audios]
#
#   demo_dir   : directory containing demo.mp4 and demo.wav (default: demo)
#   output_dir : directory where test data is written  (default: data)
#   n_videos   : number of video files to generate (default: 1)
#   n_audios   : number of audio files to generate (default: 1)
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
N_VIDEOS="${3:-1}"
N_AUDIOS="${4:-1}"

DEMO_VIDEO="${DEMO_DIR}/demo.mp4"
DEMO_AUDIO="${DEMO_DIR}/demo.wav"

VIDEO_FPS=30
DEMO_VIDEO_DURATION=""
DEMO_AUDIO_DURATION=""

# Random ranges (seconds, integers).
X_MIN=2;  X_MAX=10   # black frames before CLAP in video
Y_MIN=1;  Y_MAX=8    # silence before noise in audio
M_MIN=2;  M_MAX=6    # black frames after demo in video
P_MIN=2;  P_MAX=6    # silence after demo in audio

# Arrays filled during generation.
VIDEO_CLAP_STRS=()
AUDIO_CLAP_STRS=()
VIDEO_NAMES=()
AUDIO_NAMES=()

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
    local min="$1"
    local max="$2"
    echo $(( min + RANDOM % (max - min + 1) ))
}

seconds_to_time() {
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
# Read demo durations and properties
# ---------------------------------------------------------------------------

DEMO_VIDEO_DURATION=$(get_duration "${DEMO_VIDEO}")
DEMO_AUDIO_DURATION=$(get_duration "${DEMO_AUDIO}")
log "demo.mp4 duration : ${DEMO_VIDEO_DURATION}s"
log "demo.wav duration : ${DEMO_AUDIO_DURATION}s"

VIDEO_WIDTH=$(ffprobe -v error -select_streams v:0 \
    -show_entries stream=width -of csv=p=0 "${DEMO_VIDEO}")
VIDEO_HEIGHT=$(ffprobe -v error -select_streams v:0 \
    -show_entries stream=height -of csv=p=0 "${DEMO_VIDEO}")
VIDEO_PIX_FMT=$(ffprobe -v error -select_streams v:0 \
    -show_entries stream=pix_fmt -of csv=p=0 "${DEMO_VIDEO}")
AUDIO_RATE=$(soxi -r "${DEMO_AUDIO}")
AUDIO_CHANNELS=$(soxi -c "${DEMO_AUDIO}")
AUDIO_BITS=$(soxi -b "${DEMO_AUDIO}")

log "Video: ${VIDEO_WIDTH}x${VIDEO_HEIGHT} @ ${VIDEO_FPS}fps pix_fmt=${VIDEO_PIX_FMT}"
log "Audio: ${AUDIO_RATE}Hz ${AUDIO_CHANNELS}ch ${AUDIO_BITS}bit"

DURATION_STR=$(seconds_to_time "${DEMO_VIDEO_DURATION}")

# Pre-encode demo video once (shared by all outputs).
DEMO_VIDEO_TMP="${TMP_DIR}/demo_video.mp4"
ffmpeg -i "${DEMO_VIDEO}" \
    -pix_fmt "${VIDEO_PIX_FMT}" \
    -r "${VIDEO_FPS}" \
    -an "${DEMO_VIDEO_TMP}" \
    -nostdin -y -loglevel error

# ---------------------------------------------------------------------------
# Functions
# ---------------------------------------------------------------------------

build_video() {
    local idx="$1"
    local x="$2"
    local m="$3"

    local suffix=""
    if [[ ${idx} -gt 1 ]]; then
        suffix="${idx}"
    fi
    local out_name="test_video${suffix}.mp4"
    local out_path="${OUT_DIR}/${out_name}"

    log "Building ${out_name} (X=${x}s, M=${m}s) ..."

    local clap_seconds
    clap_seconds=$(echo "${x}" | awk '{printf "%.6f", $1}')
    local clap_str
    clap_str=$(seconds_to_time "${clap_seconds}")

    local frame_duration
    frame_duration=$(echo "${VIDEO_FPS}" | awk '{printf "%.6f", 1.0/$1}')

    local black_before="${TMP_DIR}/black_before${suffix}.mp4"
    ffmpeg -f lavfi \
        -i "color=c=black:s=${VIDEO_WIDTH}x${VIDEO_HEIGHT}:r=${VIDEO_FPS}:d=${x}" \
        -pix_fmt "${VIDEO_PIX_FMT}" \
        -an "${black_before}" \
        -nostdin -y -loglevel error

    local clap_frame="${TMP_DIR}/clap_frame${suffix}.mp4"
    ffmpeg -f lavfi \
        -i "color=c=black:s=${VIDEO_WIDTH}x${VIDEO_HEIGHT}:r=${VIDEO_FPS}:d=${frame_duration}" \
        -vf "drawtext=text='CLAP':fontsize=120:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2" \
        -pix_fmt "${VIDEO_PIX_FMT}" \
        -frames:v 1 \
        -an "${clap_frame}" \
        -nostdin -y -loglevel error

    local black_after_clap="${TMP_DIR}/black_after_clap${suffix}.mp4"
    ffmpeg -f lavfi \
        -i "color=c=black:s=${VIDEO_WIDTH}x${VIDEO_HEIGHT}:r=${VIDEO_FPS}:d=1" \
        -pix_fmt "${VIDEO_PIX_FMT}" \
        -an "${black_after_clap}" \
        -nostdin -y -loglevel error

    local black_end="${TMP_DIR}/black_end${suffix}.mp4"
    ffmpeg -f lavfi \
        -i "color=c=black:s=${VIDEO_WIDTH}x${VIDEO_HEIGHT}:r=${VIDEO_FPS}:d=${m}" \
        -pix_fmt "${VIDEO_PIX_FMT}" \
        -an "${black_end}" \
        -nostdin -y -loglevel error

    local concat_list="${TMP_DIR}/video_concat${suffix}.txt"
    {
        echo "file '${black_before}'"
        echo "file '${clap_frame}'"
        echo "file '${black_after_clap}'"
        echo "file '${DEMO_VIDEO_TMP}'"
        echo "file '${black_end}'"
    } > "${concat_list}"

    ffmpeg -f concat -safe 0 \
        -i "${concat_list}" \
        -c:v libx264 -crf 0 -preset ultrafast \
        -pix_fmt "${VIDEO_PIX_FMT}" \
        -an "${out_path}" \
        -nostdin -y -loglevel error

    log "  -> ${out_path}"

    VIDEO_CLAP_STRS+=("${clap_str}")
    VIDEO_NAMES+=("${out_name}")
}

build_audio() {
    local idx="$1"
    local y="$2"
    local p="$3"

    local suffix=""
    if [[ ${idx} -gt 1 ]]; then
        suffix="${idx}"
    fi
    local out_name="test_audio${suffix}.wav"
    local out_path="${OUT_DIR}/${out_name}"

    log "Building ${out_name} (Y=${y}s, P=${p}s) ..."

    local clap_seconds
    clap_seconds=$(echo "${y}" | awk '{printf "%.6f", $1}')
    local clap_str
    clap_str=$(seconds_to_time "${clap_seconds}")

    local silence_before="${TMP_DIR}/silence_before${suffix}.wav"
    sox -n -r "${AUDIO_RATE}" -c "${AUDIO_CHANNELS}" -b "${AUDIO_BITS}" \
        "${silence_before}" trim 0.0 "${y}.0"

    local noise_burst="${TMP_DIR}/noise_burst${suffix}.wav"
    sox -n -r "${AUDIO_RATE}" -c "${AUDIO_CHANNELS}" -b "${AUDIO_BITS}" \
        "${noise_burst}" synth 0.001 whitenoise vol 0.8

    local silence_after_clap="${TMP_DIR}/silence_after_clap${suffix}.wav"
    sox -n -r "${AUDIO_RATE}" -c "${AUDIO_CHANNELS}" -b "${AUDIO_BITS}" \
        "${silence_after_clap}" trim 0.0 1.0

    local silence_end="${TMP_DIR}/silence_end${suffix}.wav"
    sox -n -r "${AUDIO_RATE}" -c "${AUDIO_CHANNELS}" -b "${AUDIO_BITS}" \
        "${silence_end}" trim 0.0 "${p}.0"

    sox "${silence_before}" \
        "${noise_burst}" \
        "${silence_after_clap}" \
        "${DEMO_AUDIO}" \
        "${silence_end}" \
        "${out_path}"

    log "  -> ${out_path}"

    AUDIO_CLAP_STRS+=("${clap_str}")
    AUDIO_NAMES+=("${out_name}")
}

# ---------------------------------------------------------------------------
# Generate video files
# ---------------------------------------------------------------------------

for (( i=1; i<=N_VIDEOS; i++ )); do
    x=$(random_int ${X_MIN} ${X_MAX})
    m=$(random_int ${M_MIN} ${M_MAX})
    build_video "${i}" "${x}" "${m}"
done

# ---------------------------------------------------------------------------
# Generate audio files
# ---------------------------------------------------------------------------

for (( i=1; i<=N_AUDIOS; i++ )); do
    y=$(random_int ${Y_MIN} ${Y_MAX})
    p=$(random_int ${P_MIN} ${P_MAX})
    build_audio "${i}" "${y}" "${p}"
done

# ---------------------------------------------------------------------------
# Write test.csv
# ---------------------------------------------------------------------------

log "Writing test.csv ..."

TEST_CSV="${OUT_DIR}/test.csv"

HEADER="ID;Session;Serie;audio_file;video_file;audio_clap;video_clap;delay;duration"
for (( i=2; i<=N_AUDIOS; i++ )); do
    HEADER="${HEADER};audio_file${i};audio_clap${i}"
done
for (( i=2; i<=N_VIDEOS; i++ )); do
    HEADER="${HEADER};video_file${i};video_clap${i}"
done

ROW="demo;1;1;${AUDIO_NAMES[0]};${VIDEO_NAMES[0]};${AUDIO_CLAP_STRS[0]};${VIDEO_CLAP_STRS[0]};1.000;${DURATION_STR}"
for (( i=2; i<=N_AUDIOS; i++ )); do
    idx=$(( i - 1 ))
    ROW="${ROW};${AUDIO_NAMES[${idx}]};${AUDIO_CLAP_STRS[${idx}]}"
done
for (( i=2; i<=N_VIDEOS; i++ )); do
    idx=$(( i - 1 ))
    ROW="${ROW};${VIDEO_NAMES[${idx}]};${VIDEO_CLAP_STRS[${idx}]}"
done

{
    echo "${HEADER}"
    echo "${ROW}"
} > "${TEST_CSV}"

log "  -> ${TEST_CSV}"

# ---------------------------------------------------------------------------
# Write expected values
# ---------------------------------------------------------------------------

EXPECTED_FILE="${OUT_DIR}/expected.txt"
{
    echo "# Generated by make_test_data.sh — do not edit manually."
    echo "N_VIDEOS=${N_VIDEOS}"
    echo "N_AUDIOS=${N_AUDIOS}"
    for (( i=0; i<N_VIDEOS; i++ )); do
        echo "VIDEO_CLAP_$((i+1))=${VIDEO_CLAP_STRS[${i}]}"
    done
    for (( i=0; i<N_AUDIOS; i++ )); do
        echo "AUDIO_CLAP_$((i+1))=${AUDIO_CLAP_STRS[${i}]}"
    done
    echo "DEMO_VIDEO_DURATION=${DEMO_VIDEO_DURATION}"
    echo "DEMO_AUDIO_DURATION=${DEMO_AUDIO_DURATION}"
    echo "VIDEO_FPS=${VIDEO_FPS}"
} > "${EXPECTED_FILE}"

log "  -> ${EXPECTED_FILE}"

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

log ""
log "Done. Test data written to: ${OUT_DIR}"
log "  ${N_VIDEOS} video(s), ${N_AUDIOS} audio(s)"
log ""
log "To run the AViSS integration test:"
log "  python cli.py sync -c ${TEST_CSV} -l 1 --verbose"
log ""
