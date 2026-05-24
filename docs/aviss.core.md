# aviss.core module

## List of classes

## Class `avAudioOps`

### Description

*Static methods for audio file operations used by the AViSS pipeline.*

audioopy is used for reading audio metadata (duration, framerate, channels,
sample width). sox is used for all audio transformations (trim, silence,
concatenation, resampling, channel mixing).

##### Example

    >>> info = avAudioOps.get_audio_info("/data/rec.wav")
    >>> info["duration"]
    > 248.32
    >>> avAudioOps.audio_duration("/data/rec.wav")
    > 248.32


### Public functions

#### get_audio_info

```python
@staticmethod
def get_audio_info(path: str) -> dict:
    """Return basic metadata of an audio file via audioopy.

        :example:
        >>> info = get_audio_info("/data/rec.wav")
        >>> info["duration"]
        248.32
        >>> info["framerate"]
        44100

        :param path: (str) Path to the audio file.
        :return: (dict) Keys: "framerate" (int), "nchannels" (int),
                 "sampwidth" (int, bytes), "duration" (float, seconds).
        :raises: TypeError: path is not a non-empty string.
        :raises: FileNotFoundError: The file does not exist.
        :raises: IOError: audioopy could not read the file.

        """
    if isinstance(path, str) is False or len(path.strip()) == 0:
        raise TypeError('path must be a non-empty string.')
    check_file(path)
    try:
        fa = audioopy.aio.open(path)
        info = {'framerate': fa.get_framerate(), 'nchannels': fa.get_nchannels(), 'sampwidth': fa.get_sampwidth(), 'duration': fa.get_duration()}
        fa.close()
    except Exception as e:
        raise IOError(f'audioopy could not read {path!r}: {e}.')
    return info
```

*Return basic metadata of an audio file via audioopy.*

##### Example

    >>> info = get_audio_info("/data/rec.wav")
    >>> info["duration"]
    > 248.32
    >>> info["framerate"]
    > 44100

##### Parameters

- **path**: (*str*) Path to the audio file.


##### Returns

- **(dict) Keys**: "framerate"(*int*), "nchannels" (int), "sampwidth" (int, bytes), "duration" (float, seconds).


##### Raises

- *TypeError*: path is not a non-empty string.
- *FileNotFoundError*: The file does not exist.
- *IOError*: audioopy could not read the file.

#### open_audio

```python
@staticmethod
def open_audio(path: str, work_dir: str) -> str:
    """Return a path to a readable WAV file, converting with sox if needed.

        If audioopy can open the file directly, the original path is returned.
        Otherwise a 16-bit WAV conversion is written to work_dir and that path
        is returned instead.

        :param path: (str) Path to the audio file.
        :param work_dir: (str) Directory where the converted file is written.
        :return: (str) Path to a WAV file readable by audioopy.
        :raises: TypeError: path or work_dir is not a non-empty string.
        :raises: FileNotFoundError: path does not exist.
        :raises: IOError: Conversion with sox failed.

        """
    if isinstance(path, str) is False or len(path.strip()) == 0:
        raise TypeError('path must be a non-empty string.')
    if isinstance(work_dir, str) is False or len(work_dir.strip()) == 0:
        raise TypeError('work_dir must be a non-empty string.')
    check_file(path)
    try:
        fa = audioopy.aio.open(path)
        fa.close()
        return path
    except Exception:
        pass
    converted = os.path.join(work_dir, 'audio_converted.wav')
    if os.path.exists(converted) is True:
        raise IOError(f'Conversion target already exists: {converted!r}. Remove it before retrying.')
    run_command(f"sox '{path}' -b 16 '{converted}'")
    check_file(converted)
    return converted
```

*Return a path to a readable WAV file, converting with sox if needed.*

If audioopy can open the file directly, the original path is returned.
Otherwise a 16-bit WAV conversion is written to work_dir and that path
is returned instead.

##### Parameters

- **path**: (*str*) Path to the audio file.
- **work_dir**: (*str*) Directory where the converted file is written.


##### Returns

- (*str*) Path to a WAV file readable by audioopy.


##### Raises

- *TypeError*: path or work_dir is not a non-empty string.
- *FileNotFoundError*: path does not exist.
- *IOError*: Conversion with sox failed.

#### extract_audio_from_video

```python
@staticmethod
def extract_audio_from_video(video_path: str, audio_out: str) -> None:
    """Extract the audio track of a video and re-encode it as 16-bit PCM WAV.

        :param video_path: (str) Path to the input video file.
        :param audio_out: (str) Path for the output WAV file.
        :raises: TypeError: video_path or audio_out is not a non-empty string.
        :raises: FileNotFoundError: video_path does not exist.

        """
    if isinstance(video_path, str) is False or len(video_path.strip()) == 0:
        raise TypeError('video_path must be a non-empty string.')
    if isinstance(audio_out, str) is False or len(audio_out.strip()) == 0:
        raise TypeError('audio_out must be a non-empty string.')
    check_file(video_path)
    command = f"ffmpeg -i '{video_path}' -vn -acodec pcm_s16le '{audio_out}' -nostdin -y"
    run_command(command)
```

*Extract the audio track of a video and re-encode it as 16-bit PCM WAV.*

##### Parameters

- **video_path**: (*str*) Path to the input video file.
- **audio_out**: (*str*) Path for the output WAV file.


##### Raises

- *TypeError*: video_path or audio_out is not a non-empty string.
- *FileNotFoundError*: video_path does not exist.

#### audio_duration

```python
@staticmethod
def audio_duration(path: str) -> float:
    """Return the duration of an audio file in seconds.

        :param path: (str) Path to the audio file.
        :return: (float) Duration in seconds.
        :raises: TypeError: path is not a non-empty string.
        :raises: FileNotFoundError: The file does not exist.
        :raises: IOError: audioopy could not read the file.

        """
    info = avAudioOps.get_audio_info(path)
    return info['duration']
```

*Return the duration of an audio file in seconds.*

##### Parameters

- **path**: (*str*) Path to the audio file.


##### Returns

- (*float*) Duration in seconds.


##### Raises

- *TypeError*: path is not a non-empty string.
- *FileNotFoundError*: The file does not exist.
- *IOError*: audioopy could not read the file.

#### trim_audio

```python
@staticmethod
def trim_audio(audio_in: str, trim_duration: float, audio_out: str, begin: bool=True) -> None:
    """Trim a fixed duration from the beginning or the end of an audio file.

        :param audio_in: (str) Path to the input audio file.
        :param trim_duration: (float) Duration to remove (seconds).
        :param audio_out: (str) Path for the output audio file.
        :param begin: (bool) True to trim from the beginning, False from the end.
        :raises: TypeError: audio_in or audio_out is not a non-empty string.
        :raises: TypeError: trim_duration is not a number.
        :raises: ValueError: trim_duration is not strictly positive.
        :raises: FileNotFoundError: audio_in does not exist.

        """
    if isinstance(audio_in, str) is False or len(audio_in.strip()) == 0:
        raise TypeError('audio_in must be a non-empty string.')
    if isinstance(audio_out, str) is False or len(audio_out.strip()) == 0:
        raise TypeError('audio_out must be a non-empty string.')
    if isinstance(trim_duration, (int, float)) is False:
        raise TypeError('trim_duration must be a number.')
    if float(trim_duration) <= 0.0:
        raise ValueError('trim_duration must be strictly positive.')
    check_file(audio_in)
    cur_dur = avAudioOps.audio_duration(audio_in)
    remaining = cur_dur - float(trim_duration)
    if begin is True:
        trim_start = float(trim_duration)
    else:
        trim_start = 0.0
    command = f"sox '{audio_in}' '{audio_out}' trim {trim_start:f} {remaining:f}"
    run_command(command)
```

*Trim a fixed duration from the beginning or the end of an audio file.*

##### Parameters

- **audio_in**: (*str*) Path to the input audio file.
- **trim_duration**: (*float*) Duration to remove (seconds).
- **audio_out**: (*str*) Path for the output audio file.
- **begin**: (*bool*) True to trim from the beginning, False from the end.


##### Raises

- *TypeError*: audio_in or audio_out is not a non-empty string.
- *TypeError*: trim_duration is not a number.
- *ValueError*: trim_duration is not strictly positive.
- *FileNotFoundError*: audio_in does not exist.

#### add_silence

```python
@staticmethod
def add_silence(audio_in: str, silence_duration: float, audio_out: str, begin: bool=True) -> None:
    """Prepend or append silence to an audio file.

        The silence is generated with the same framerate, channel count and
        sample width as the input file.

        :param audio_in: (str) Path to the input audio file.
        :param silence_duration: (float) Duration of silence to add (seconds).
        :param audio_out: (str) Path for the output audio file.
        :param begin: (bool) True to prepend silence, False to append it.
        :raises: TypeError: audio_in or audio_out is not a non-empty string.
        :raises: TypeError: silence_duration is not a number.
        :raises: ValueError: silence_duration is not strictly positive.
        :raises: FileNotFoundError: audio_in does not exist.

        """
    if isinstance(audio_in, str) is False or len(audio_in.strip()) == 0:
        raise TypeError('audio_in must be a non-empty string.')
    if isinstance(audio_out, str) is False or len(audio_out.strip()) == 0:
        raise TypeError('audio_out must be a non-empty string.')
    if isinstance(silence_duration, (int, float)) is False:
        raise TypeError('silence_duration must be a number.')
    if float(silence_duration) <= 0.0:
        raise ValueError('silence_duration must be strictly positive.')
    check_file(audio_in)
    info = avAudioOps.get_audio_info(audio_in)
    silence_tmp = os.path.join(os.path.dirname(audio_out), '_silence_tmp.wav')
    command = f"sox -n -r {info['framerate']:d} -c {info['nchannels']:d} -b {info['sampwidth'] * 8:d} '{silence_tmp}' trim 0.0 {float(silence_duration):f}"
    run_command(command)
    if begin is True:
        command = f"sox '{silence_tmp}' '{audio_in}' '{audio_out}'"
    else:
        command = f"sox '{audio_in}' '{silence_tmp}' '{audio_out}'"
    run_command(command)
    if os.path.isfile(silence_tmp) is True:
        os.remove(silence_tmp)
```

*Prepend or append silence to an audio file.*

The silence is generated with the same framerate, channel count and
sample width as the input file.

##### Parameters

- **audio_in**: (*str*) Path to the input audio file.
- **silence_duration**: (*float*) Duration of silence to add (seconds).
- **audio_out**: (*str*) Path for the output audio file.
- **begin**: (*bool*) True to prepend silence, False to append it.


##### Raises

- *TypeError*: audio_in or audio_out is not a non-empty string.
- *TypeError*: silence_duration is not a number.
- *ValueError*: silence_duration is not strictly positive.
- *FileNotFoundError*: audio_in does not exist.

#### adjust_audio_at_clap

```python
@staticmethod
def adjust_audio_at_clap(audio_in: str, audio_clap: float, reference_clap: float, audio_out: str) -> None:
    """Align an audio file so that its clap matches a reference clap time.

        The reference clap is typically the video clap time (plus delay).
        Three cases are handled:
            - clap times are equal: the file is copied unchanged.
            - audio clap is later than reference: the beginning is trimmed.
            - audio clap is earlier than reference: silence is prepended.

        :param audio_in: (str) Path to the input audio file.
        :param audio_clap: (float) Time of the clap in the audio file (seconds).
        :param reference_clap: (float) Target clap time to align to (seconds).
        :param audio_out: (str) Path for the output audio file.
        :raises: TypeError: audio_in or audio_out is not a non-empty string.
        :raises: TypeError: audio_clap or reference_clap is not a number.
        :raises: FileNotFoundError: audio_in does not exist.

        """
    if isinstance(audio_in, str) is False or len(audio_in.strip()) == 0:
        raise TypeError('audio_in must be a non-empty string.')
    if isinstance(audio_out, str) is False or len(audio_out.strip()) == 0:
        raise TypeError('audio_out must be a non-empty string.')
    if isinstance(audio_clap, (int, float)) is False:
        raise TypeError('audio_clap must be a number.')
    if isinstance(reference_clap, (int, float)) is False:
        raise TypeError('reference_clap must be a number.')
    check_file(audio_in)
    delta = float(reference_clap) - float(audio_clap)
    if delta == 0.0:
        aviss_logger.write('Already matching. Nothing to do.')
        shutil.copy(audio_in, audio_out)
    elif delta < 0.0:
        aviss_logger.write(f'Trim the beginning of the audio of {-delta:f} seconds')
        avAudioOps.trim_audio(audio_in, -delta, audio_out, begin=True)
    else:
        aviss_logger.write(f'Add {delta:f} seconds of silence at the beginning of the audio')
        avAudioOps.add_silence(audio_in, delta, audio_out, begin=True)
```

*Align an audio file so that its clap matches a reference clap time.*

The reference clap is typically the video clap time (plus delay).
Three cases are handled:
- clap times are equal: the file is copied unchanged.
- audio clap is later than reference: the beginning is trimmed.
- audio clap is earlier than reference: silence is prepended.

##### Parameters

- **audio_in**: (*str*) Path to the input audio file.
- **audio_clap**: (*float*) Time of the clap in the audio file (seconds).
- **reference_clap**: (*float*) Target clap time to align to (seconds).
- **audio_out**: (*str*) Path for the output audio file.


##### Raises

- *TypeError*: audio_in or audio_out is not a non-empty string.
- *TypeError*: audio_clap or reference_clap is not a number.
- *FileNotFoundError*: audio_in does not exist.

#### adjust_audio_duration

```python
@staticmethod
def adjust_audio_duration(audio_in: str, target_duration: float, audio_out: str) -> None:
    """Pad or trim an audio file to match a target duration.

        Three cases are handled:
            - durations are equal: the file is copied unchanged.
            - audio is shorter than target: silence is appended.
            - audio is longer than target: the end is trimmed.

        :param audio_in: (str) Path to the input audio file.
        :param target_duration: (float) Expected output duration (seconds).
        :param audio_out: (str) Path for the output audio file.
        :raises: TypeError: audio_in or audio_out is not a non-empty string.
        :raises: TypeError: target_duration is not a number.
        :raises: ValueError: target_duration is not strictly positive.
        :raises: FileNotFoundError: audio_in does not exist.

        """
    if isinstance(audio_in, str) is False or len(audio_in.strip()) == 0:
        raise TypeError('audio_in must be a non-empty string.')
    if isinstance(audio_out, str) is False or len(audio_out.strip()) == 0:
        raise TypeError('audio_out must be a non-empty string.')
    if isinstance(target_duration, (int, float)) is False:
        raise TypeError('target_duration must be a number.')
    if float(target_duration) <= 0.0:
        raise ValueError('target_duration must be strictly positive.')
    check_file(audio_in)
    cur_dur = avAudioOps.audio_duration(audio_in)
    aviss_logger.write(f'Duration of the audio is {cur_dur:f} seconds')
    delta = float(target_duration) - cur_dur
    if delta == 0.0:
        aviss_logger.write('Already matching. Nothing to do.')
        shutil.copy(audio_in, audio_out)
    elif delta > 0.0:
        aviss_logger.write(f'Add {delta:f} seconds of silence at the end of the audio')
        avAudioOps.add_silence(audio_in, delta, audio_out, begin=False)
    else:
        aviss_logger.write(f'Trim the end of the audio of {-delta:f} seconds')
        avAudioOps.trim_audio(audio_in, -delta, audio_out, begin=False)
```

*Pad or trim an audio file to match a target duration.*

Three cases are handled:
- durations are equal: the file is copied unchanged.
- audio is shorter than target: silence is appended.
- audio is longer than target: the end is trimmed.

##### Parameters

- **audio_in**: (*str*) Path to the input audio file.
- **target_duration**: (*float*) Expected output duration (seconds).
- **audio_out**: (*str*) Path for the output audio file.


##### Raises

- *TypeError*: audio_in or audio_out is not a non-empty string.
- *TypeError*: target_duration is not a number.
- *ValueError*: target_duration is not strictly positive.
- *FileNotFoundError*: audio_in does not exist.

#### to_mono

```python
@staticmethod
def to_mono(audio_in: str, audio_out: str) -> None:
    """Mix all channels down to mono, keeping the original sample rate.

        If the input is already mono, the file is copied unchanged.

        :param audio_in: (str) Path to the input audio file.
        :param audio_out: (str) Path for the output mono WAV file.
        :raises: TypeError: audio_in or audio_out is not a non-empty string.
        :raises: FileNotFoundError: audio_in does not exist.

        """
    if isinstance(audio_in, str) is False or len(audio_in.strip()) == 0:
        raise TypeError('audio_in must be a non-empty string.')
    if isinstance(audio_out, str) is False or len(audio_out.strip()) == 0:
        raise TypeError('audio_out must be a non-empty string.')
    check_file(audio_in)
    info = avAudioOps.get_audio_info(audio_in)
    if info['nchannels'] == 1:
        shutil.copy(audio_in, audio_out)
        return
    command = f"sox '{audio_in}' '{audio_out}' channels 1"
    run_command(command)
```

*Mix all channels down to mono, keeping the original sample rate.*

If the input is already mono, the file is copied unchanged.

##### Parameters

- **audio_in**: (*str*) Path to the input audio file.
- **audio_out**: (*str*) Path for the output mono WAV file.


##### Raises

- *TypeError*: audio_in or audio_out is not a non-empty string.
- *FileNotFoundError*: audio_in does not exist.

#### to_mono_16k

```python
@staticmethod
def to_mono_16k(audio_in: str, audio_out: str) -> None:
    """Convert an audio file to mono at 16000 Hz.

        :param audio_in: (str) Path to the input audio file.
        :param audio_out: (str) Path for the output mono 16000 Hz WAV file.
        :raises: TypeError: audio_in or audio_out is not a non-empty string.
        :raises: FileNotFoundError: audio_in does not exist.

        """
    if isinstance(audio_in, str) is False or len(audio_in.strip()) == 0:
        raise TypeError('audio_in must be a non-empty string.')
    if isinstance(audio_out, str) is False or len(audio_out.strip()) == 0:
        raise TypeError('audio_out must be a non-empty string.')
    check_file(audio_in)
    command = f"sox '{audio_in}' -r 16000 '{audio_out}' channels 1"
    run_command(command)
```

*Convert an audio file to mono at 16000 Hz.*

##### Parameters

- **audio_in**: (*str*) Path to the input audio file.
- **audio_out**: (*str*) Path for the output mono 16000 Hz WAV file.


##### Raises

- *TypeError*: audio_in or audio_out is not a non-empty string.
- *FileNotFoundError*: audio_in does not exist.



## Class `avVideoOps`

### Description

*Static methods for video file operations used by the AViSS pipeline.*

All methods wrap ffmpeg commands or sppasVideoReader calls.
sppasVideoReader is used exclusively for reading video metadata because
it guarantees frame-accurate seeking via OpenCV.

##### Example

    >>> info = avVideoOps.get_video_info("/data/rec.mp4")
    >>> info["fps"]
    > 50.0
    >>> info["nframes"]
    > 750


### Public functions

#### get_video_info

```python
@staticmethod
def get_video_info(path: str) -> dict:
    """Return basic metadata of a video file via sppasVideoReader.

        :example:
        >>> info = avVideoOps.get_video_info("/data/rec.mp4")
        >>> info["fps"]
        50.0
        >>> info["duration"]
        15.0

        :param path: (str) Path to the video file.
        :return: (dict) Keys: "fps" (float), "nframes" (int),
                 "duration" (float, seconds), "width" (int), "height" (int).
        :raises: TypeError: path is not a non-empty string.
        :raises: FileNotFoundError: The file does not exist.
        :raises: IOError: sppasVideoReader could not open the file.

        """
    if isinstance(path, str) is False or len(path.strip()) == 0:
        raise TypeError('path must be a non-empty string.')
    check_file(path)
    bv = sppasVideoReader()
    try:
        bv.open(path)
        info = {'fps': bv.get_framerate(), 'nframes': bv.get_nframes(), 'duration': bv.get_duration(), 'width': bv.get_width(), 'height': bv.get_height()}
    except Exception as e:
        raise IOError(f'sppasVideoReader could not open {path!r}: {e}.')
    finally:
        bv.close()
    return info
```

*Return basic metadata of a video file via sppasVideoReader.*

##### Example

    >>> info = avVideoOps.get_video_info("/data/rec.mp4")
    >>> info["fps"]
    > 50.0
    >>> info["duration"]
    > 15.0

##### Parameters

- **path**: (*str*) Path to the video file.


##### Returns

- **(dict) Keys**: "fps"(*float*), "nframes" (int), "duration" (float, seconds), "width" (int), "height" (int).


##### Raises

- *TypeError*: path is not a non-empty string.
- *FileNotFoundError*: The file does not exist.
- *IOError*: sppasVideoReader could not open the file.

#### time_to_frame

```python
@staticmethod
def time_to_frame(time_seconds: float, fps: float) -> int:
    """Return the index of the frame that contains a given time position.

        The frame index is the integer part of time * fps.
        Frame indices are 0-based: frame 0 covers [0, 1/fps[.

        :example:
        >>> avVideoOps.time_to_frame(0.120, 25.)
        3
        >>> avVideoOps.time_to_frame(0.0, 50.)
        0

        :param time_seconds: (float) Time position in seconds.
        :param fps: (float) Frame rate of the video in frames per second.
        :return: (int) 0-based frame index.
        :raises: TypeError: time_seconds or fps is not a number.
        :raises: ValueError: time_seconds is negative or fps is not positive.

        """
    if isinstance(time_seconds, (int, float)) is False:
        raise TypeError('time_seconds must be a number.')
    if isinstance(fps, (int, float)) is False:
        raise TypeError('fps must be a number.')
    if float(time_seconds) < 0.0:
        raise ValueError('time_seconds must be zero or positive.')
    if float(fps) <= 0.0:
        raise ValueError('fps must be strictly positive.')
    return int(float(time_seconds) * float(fps))
```

*Return the index of the frame that contains a given time position.*

The frame index is the integer part of time * fps.
Frame indices are 0-based: frame 0 covers [0, 1/fps[.

##### Example

    >>> avVideoOps.time_to_frame(0.120, 25.)
    > 3
    >>> avVideoOps.time_to_frame(0.0, 50.)
    > 0

##### Parameters

- **time_seconds**: (*float*) Time position in seconds.
- **fps**: (*float*) Frame rate of the video in frames per second.


##### Returns

- (*int*) 0-based frame index.


##### Raises

- *TypeError*: time_seconds or fps is not a number.
- *ValueError*: time_seconds is negative or fps is not positive.

#### frame_to_time

```python
@staticmethod
def frame_to_time(frame_index: int, fps: float) -> float:
    """Return the start time of a frame given its index and the frame rate.

        :example:
        >>> avVideoOps.frame_to_time(3, 25.)
        0.12
        >>> avVideoOps.frame_to_time(0, 50.)
        0.0

        :param frame_index: (int) 0-based frame index.
        :param fps: (float) Frame rate of the video in frames per second.
        :return: (float) Start time of the frame in seconds.
        :raises: TypeError: frame_index is not an integer or fps is not a number.
        :raises: ValueError: frame_index is negative or fps is not positive.

        """
    if isinstance(frame_index, int) is False:
        raise TypeError('frame_index must be an integer.')
    if isinstance(fps, (int, float)) is False:
        raise TypeError('fps must be a number.')
    if frame_index < 0:
        raise ValueError('frame_index must be zero or positive.')
    if float(fps) <= 0.0:
        raise ValueError('fps must be strictly positive.')
    return float(frame_index) / float(fps)
```

*Return the start time of a frame given its index and the frame rate.*

##### Example

    >>> avVideoOps.frame_to_time(3, 25.)
    > 0.12
    >>> avVideoOps.frame_to_time(0, 50.)
    > 0.0

##### Parameters

- **frame_index**: (*int*) 0-based frame index.
- **fps**: (*float*) Frame rate of the video in frames per second.


##### Returns

- (*float*) Start time of the frame in seconds.


##### Raises

- *TypeError*: frame_index is not an integer or fps is not a number.
- *ValueError*: frame_index is negative or fps is not positive.

#### end_frame_index

```python
@staticmethod
def end_frame_index(clap_time: float, duration: float, fps: float) -> int:
    """Return the index of the first frame NOT included in the output.

        The end frame is computed as 1 + int((clap_time + duration) * fps).
        This guarantees that the last included frame fully covers the expected
        duration.

        :param clap_time: (float) Clap time in the video (seconds).
        :param duration: (float) Expected output duration (seconds).
        :param fps: (float) Frame rate in frames per second.
        :return: (int) Index of the first excluded frame.
        :raises: TypeError: Any argument is not a number.
        :raises: ValueError: Any argument is not strictly positive (clap_time >= 0).

        """
    if isinstance(clap_time, (int, float)) is False:
        raise TypeError('clap_time must be a number.')
    if isinstance(duration, (int, float)) is False:
        raise TypeError('duration must be a number.')
    if isinstance(fps, (int, float)) is False:
        raise TypeError('fps must be a number.')
    if float(clap_time) < 0.0:
        raise ValueError('clap_time must be zero or positive.')
    if float(duration) <= 0.0:
        raise ValueError('duration must be strictly positive.')
    if float(fps) <= 0.0:
        raise ValueError('fps must be strictly positive.')
    real_end_time = float(clap_time) + float(duration)
    return 1 + int(real_end_time * float(fps))
```

*Return the index of the first frame NOT included in the output.*

The end frame is computed as 1 + int((clap_time + duration) * fps).
This guarantees that the last included frame fully covers the expected
duration.

##### Parameters

- **clap_time**: (*float*) Clap time in the video (seconds).
- **duration**: (*float*) Expected output duration (seconds).
- **fps**: (*float*) Frame rate in frames per second.


##### Returns

- (*int*) Index of the first excluded frame.


##### Raises

- *TypeError*: Any argument is not a number.
- *ValueError*: Any argument is not strictly positive (clap_time >= 0).

#### trim

```python
@staticmethod
def trim(video_in: str, start_frame: int, end_frame: int, video_out: str, crf: int=None) -> None:
    """Trim a video between two frame indices and re-encode to MKV/H265.

        The output covers frames in the range [start_frame, end_frame[.
        The PTS-STARTPTS filter resets the timestamp origin to zero.

        The ':' separator used in ffmpeg filter syntax requires that the
        output path does not contain colons.

        :param video_in: (str) Path to the input video file.
        :param start_frame: (int) Index of the first frame to include (0-based).
        :param end_frame: (int) Index of the first frame to exclude.
        :param video_out: (str) Path for the output MKV file.
        :param crf: (int|None) CRF encoding quality. Uses cfg.output.crf if None.
        :raises: TypeError: Any string argument is not a non-empty string.
        :raises: TypeError: start_frame or end_frame is not an integer.
        :raises: ValueError: start_frame is negative or end_frame <= start_frame.
        :raises: FileNotFoundError: video_in does not exist.

        """
    if isinstance(video_in, str) is False or len(video_in.strip()) == 0:
        raise TypeError('video_in must be a non-empty string.')
    if isinstance(video_out, str) is False or len(video_out.strip()) == 0:
        raise TypeError('video_out must be a non-empty string.')
    if isinstance(start_frame, int) is False:
        raise TypeError('start_frame must be an integer.')
    if isinstance(end_frame, int) is False:
        raise TypeError('end_frame must be an integer.')
    if start_frame < 0:
        raise ValueError('start_frame must be zero or positive.')
    if end_frame <= start_frame:
        raise ValueError('end_frame must be strictly greater than start_frame.')
    check_file(video_in)
    effective_crf = crf if crf is not None else cfg.output.crf
    command = f"ffmpeg -i '{video_in}' -f matroska -vcodec libx265 -crf {effective_crf:d} -pix_fmt yuv420p -vf trim=start_frame={start_frame:d}:end_frame={end_frame:d},setpts=PTS-STARTPTS -an '{video_out}' -nostdin -y"
    run_command(command)
```

*Trim a video between two frame indices and re-encode to MKV/H265.*

The output covers frames in the range [start_frame, end_frame[.
The PTS-STARTPTS filter resets the timestamp origin to zero.

The ':' separator used in ffmpeg filter syntax requires that the
output path does not contain colons.

##### Parameters

- **video_in**: (*str*) Path to the input video file.
- **start_frame**: (*int*) Index of the first frame to include (0-based).
- **end_frame**: (*int*) Index of the first frame to exclude.
- **video_out**: (*str*) Path for the output MKV file.
- **crf**: (*int*|None) CRF encoding quality. Uses cfg.output.crf if None.


##### Raises

- *TypeError*: Any string argument is not a non-empty string.
- *TypeError*: start_frame or end_frame is not an integer.
- *ValueError*: start_frame is negative or end_frame <= start_frame.
- *FileNotFoundError*: video_in does not exist.

#### crop

```python
@staticmethod
def crop(video_in: str, x: int, y: int, w: int, h: int, video_out: str) -> None:
    """Crop a video to the given region.

        :param video_in: (str) Path to the input video file.
        :param x: (int) Left edge of the crop region (pixels).
        :param y: (int) Top edge of the crop region (pixels).
        :param w: (int) Width of the crop region (pixels).
        :param h: (int) Height of the crop region (pixels).
        :param video_out: (str) Path for the output video file.
        :raises: TypeError: Any string argument is not a non-empty string.
        :raises: TypeError: x, y, w or h is not an integer.
        :raises: ValueError: x or y is negative, or w or h is not strictly positive.
        :raises: FileNotFoundError: video_in does not exist.

        """
    if isinstance(video_in, str) is False or len(video_in.strip()) == 0:
        raise TypeError('video_in must be a non-empty string.')
    if isinstance(video_out, str) is False or len(video_out.strip()) == 0:
        raise TypeError('video_out must be a non-empty string.')
    for name, val in (('x', x), ('y', y), ('w', w), ('h', h)):
        if isinstance(val, int) is False:
            raise TypeError(f'{name} must be an integer.')
    if x < 0:
        raise ValueError('x must be zero or positive.')
    if y < 0:
        raise ValueError('y must be zero or positive.')
    if w <= 0:
        raise ValueError('w must be strictly positive.')
    if h <= 0:
        raise ValueError('h must be strictly positive.')
    check_file(video_in)
    command = f"ffmpeg -i '{video_in}' -filter:v 'crop=w={w:d}:h={h:d}:x={x:d}:y={y:d}' '{video_out}' -nostdin -y"
    run_command(command)
```

*Crop a video to the given region.*

##### Parameters

- **video_in**: (*str*) Path to the input video file.
- **x**: (*int*) Left edge of the crop region (pixels).
- **y**: (*int*) Top edge of the crop region (pixels).
- **w**: (*int*) Width of the crop region (pixels).
- **h**: (*int*) Height of the crop region (pixels).
- **video_out**: (*str*) Path for the output video file.


##### Raises

- *TypeError*: Any string argument is not a non-empty string.
- *TypeError*: x, y, w or h is not an integer.
- *ValueError*: x or y is negative, or w or h is not strictly positive.
- *FileNotFoundError*: video_in does not exist.

#### add_copyright

```python
@staticmethod
def add_copyright(video_in: str, copyright_text: str, video_out: str, crf: int=None) -> None:
    """Overlay a copyright text on the top-left area of the video.

        The text is rendered in white Arial 18pt at position (40, 12).
        The ':' character in the copyright string must be escaped as '\\:'
        for the ffmpeg drawtext filter.

        :param video_in: (str) Path to the input video file.
        :param copyright_text: (str) Copyright string to overlay.
        :param video_out: (str) Path for the output MKV file.
        :param crf: (int|None) CRF encoding quality. Uses cfg.output.crf if None.
        :raises: TypeError: Any string argument is not a non-empty string.
        :raises: FileNotFoundError: video_in does not exist.

        """
    if isinstance(video_in, str) is False or len(video_in.strip()) == 0:
        raise TypeError('video_in must be a non-empty string.')
    if isinstance(copyright_text, str) is False or len(copyright_text.strip()) == 0:
        raise TypeError('copyright_text must be a non-empty string.')
    if isinstance(video_out, str) is False or len(video_out.strip()) == 0:
        raise TypeError('video_out must be a non-empty string.')
    check_file(video_in)
    effective_crf = crf if crf is not None else cfg.output.crf
    command = f"""ffmpeg -i '{video_in}' -f matroska -vcodec libx265 -crf {effective_crf:d} -pix_fmt yuv420p -filter_complex "[0:v] drawtext=fontfile='arial.ttf':fontsize=18:x=40:y=12:text='{copyright_text}':fontcolor=white" -an '{video_out}' -nostdin -y"""
    run_command(command)
```

*Overlay a copyright text on the top-left area of the video.*

The text is rendered in white Arial 18pt at position (40, 12).
The ':' character in the copyright string must be escaped as '\:'
for the ffmpeg drawtext filter.

##### Parameters

- **video_in**: (*str*) Path to the input video file.
- **copyright_text**: (*str*) Copyright string to overlay.
- **video_out**: (*str*) Path for the output MKV file.
- **crf**: (*int*|None) CRF encoding quality. Uses cfg.output.crf if None.


##### Raises

- *TypeError*: Any string argument is not a non-empty string.
- *FileNotFoundError*: video_in does not exist.

#### rotate

```python
@staticmethod
def rotate(video_in: str, video_out: str, transpose: int=2) -> None:
    """Rotate a video using the ffmpeg transpose filter.

        Transpose values:
            0 = 90° counter-clockwise and vertical flip
            1 = 90° clockwise
            2 = 90° counter-clockwise
            3 = 90° clockwise and vertical flip

        :param video_in: (str) Path to the input video file.
        :param video_out: (str) Path for the output video file.
        :param transpose: (int) Transpose filter value (0, 1, 2 or 3).
                          Defaults to 2 (90° counter-clockwise, portrait mode).
        :raises: TypeError: video_in or video_out is not a non-empty string.
        :raises: TypeError: transpose is not an integer.
        :raises: ValueError: transpose is not in [0, 3].
        :raises: FileNotFoundError: video_in does not exist.

        """
    if isinstance(video_in, str) is False or len(video_in.strip()) == 0:
        raise TypeError('video_in must be a non-empty string.')
    if isinstance(video_out, str) is False or len(video_out.strip()) == 0:
        raise TypeError('video_out must be a non-empty string.')
    if isinstance(transpose, int) is False:
        raise TypeError('transpose must be an integer.')
    if transpose < 0 or transpose > 3:
        raise ValueError('transpose must be in [0, 3].')
    check_file(video_in)
    command = f"ffmpeg -i '{video_in}' -v 0 -filter:v 'transpose={transpose:d}' -qscale 0 '{video_out}' -nostdin -y"
    run_command(command)
```

*Rotate a video using the ffmpeg transpose filter.*

Transpose values:
0 = 90° counter-clockwise and vertical flip
1 = 90° clockwise
2 = 90° counter-clockwise
3 = 90° clockwise and vertical flip

##### Parameters

- **video_in**: (*str*) Path to the input video file.
- **video_out**: (*str*) Path for the output video file.
- **transpose**: (*int*) Transpose filter value (0, 1, 2 or 3). Defaults to 2 (90° counter-clockwise, portrait mode).


##### Raises

- *TypeError*: video_in or video_out is not a non-empty string.
- *TypeError*: transpose is not an integer.
- *ValueError*: transpose is not in [0, 3].
- *FileNotFoundError*: video_in does not exist.

#### merge_av

```python
@staticmethod
def merge_av(video_in: str, audio_in: str, av_out: str) -> None:
    """Merge a video file and an audio file into a single MP4 container.

        The video and audio streams are copied without re-encoding.
        The output duration is determined by the shortest stream.

        :param video_in: (str) Path to the input video file (no audio track).
        :param audio_in: (str) Path to the input audio file.
        :param av_out: (str) Path for the output MP4 file.
        :raises: TypeError: Any argument is not a non-empty string.
        :raises: FileNotFoundError: video_in or audio_in does not exist.

        """
    if isinstance(video_in, str) is False or len(video_in.strip()) == 0:
        raise TypeError('video_in must be a non-empty string.')
    if isinstance(audio_in, str) is False or len(audio_in.strip()) == 0:
        raise TypeError('audio_in must be a non-empty string.')
    if isinstance(av_out, str) is False or len(av_out.strip()) == 0:
        raise TypeError('av_out must be a non-empty string.')
    check_file(video_in)
    check_file(audio_in)
    command = f"ffmpeg -i '{video_in}' -i '{audio_in}' -c:v copy -c:a copy -shortest '{av_out}' -nostdin -y"
    run_command(command)
```

*Merge a video file and an audio file into a single MP4 container.*

The video and audio streams are copied without re-encoding.
The output duration is determined by the shortest stream.

##### Parameters

- **video_in**: (*str*) Path to the input video file (no audio track).
- **audio_in**: (*str*) Path to the input audio file.
- **av_out**: (*str*) Path for the output MP4 file.


##### Raises

- *TypeError*: Any argument is not a non-empty string.
- *FileNotFoundError*: video_in or audio_in does not exist.

#### to_webm

```python
@staticmethod
def to_webm(video_in: str, webm_out: str, audio_in: str=None, crf: int=16) -> None:
    """Convert a video file to WebM format using libvpx-vp9 (two-pass).

        Two-pass encoding is used to achieve better quality at a given CRF.
        Pass 1 analyses the video and writes statistics to /dev/null.
        Pass 2 produces the final WebM file.

        If audio_in is provided, its audio track is encoded with libvorbis
        and muxed into the WebM container. Otherwise the output is video-only.

        :example:
        >>> avVideoOps.to_webm("out.mkv", "out.webm")
        >>> avVideoOps.to_webm("out.mkv", "out.webm", audio_in="out.wav")

        :param video_in: (str) Path to the input video file.
        :param webm_out: (str) Path for the output WebM file.
        :param audio_in: (str|None) Path to an optional audio file to mux.
                         If None, no audio track is included.
        :param crf: (int) CRF quality value for libvpx-vp9 in [0, 63].
                    Lower is better. Defaults to 16.
        :raises: TypeError: video_in or webm_out is not a non-empty string.
        :raises: TypeError: audio_in is not a string or None.
        :raises: TypeError: crf is not an integer.
        :raises: ValueError: crf is not in range [0, 63].
        :raises: FileNotFoundError: video_in or audio_in does not exist.

        """
    if isinstance(video_in, str) is False or len(video_in.strip()) == 0:
        raise TypeError('video_in must be a non-empty string.')
    if isinstance(webm_out, str) is False or len(webm_out.strip()) == 0:
        raise TypeError('webm_out must be a non-empty string.')
    if audio_in is not None:
        if isinstance(audio_in, str) is False or len(audio_in.strip()) == 0:
            raise TypeError('audio_in must be a non-empty string or None.')
    if isinstance(crf, int) is False:
        raise TypeError('crf must be an integer.')
    if crf < 0 or crf > 63:
        raise ValueError('crf must be in range [0, 63].')
    check_file(video_in)
    if audio_in is not None:
        check_file(audio_in)
    if audio_in is not None:
        pass1 = f"ffmpeg -i '{video_in}' -i '{audio_in}' -b:v 0 -crf {crf:d} -pass 1 -an -f webm -y /dev/null"
        pass2 = f"ffmpeg -i '{video_in}' -i '{audio_in}' -b:v 0 -crf {crf:d} -pass 2 -c:v libvpx-vp9 -c:a libvorbis -q:a 5 -map 0:v:0 -map 1:a:0 '{webm_out}'"
    else:
        pass1 = f"ffmpeg -i '{video_in}' -b:v 0 -crf {crf:d} -pass 1 -an -f webm -y /dev/null"
        pass2 = f"ffmpeg -i '{video_in}' -b:v 0 -crf {crf:d} -pass 2 -c:v libvpx-vp9 '{webm_out}'"
    run_command(pass1)
    run_command(pass2)
```

*Convert a video file to WebM format using libvpx-vp9 (two-pass).*

Two-pass encoding is used to achieve better quality at a given CRF.
Pass 1 analyses the video and writes statistics to /dev/null.
Pass 2 produces the final WebM file.

If audio_in is provided, its audio track is encoded with libvorbis
and muxed into the WebM container. Otherwise the output is video-only.

##### Example

    >>> avVideoOps.to_webm("out.mkv", "out.webm")
    >>> avVideoOps.to_webm("out.mkv", "out.webm", audio_in="out.wav")

##### Parameters

- **video_in**: (*str*) Path to the input video file.
- **webm_out**: (*str*) Path for the output WebM file.
- **audio_in**: (*str*|None) Path to an optional audio file to mux. If None, no audio track is included.
- **crf**: (*int*) CRF quality value for libvpx-vp9 in [0, 63]. Lower is better. Defaults to 16.


##### Raises

- *TypeError*: video_in or webm_out is not a non-empty string.
- *TypeError*: audio_in is not a string or None.
- *TypeError*: crf is not an integer.
- *ValueError*: crf is not in range [0, 63].
- *FileNotFoundError*: video_in or audio_in does not exist.



## Class `avClapSync`

### Description

*Compute frame-accurate synchronization boundaries from a avSession.*

A avClapSync instance is built from a avSession and the fps of the reference
video. It exposes the computed frame indices and time values used by the
pipeline to trim video and align audio files.

The reference video is always the primary video (session.video).
If a secondary video is present, it is trimmed using the same frame
indices, which assumes both videos share the same fps. If they differ,
two avClapSync instances must be created.

##### Example

    >>> sync = avClapSync(session, fps=50.)
    >>> sync.clap_frame_index
    > 304
    >>> sync.clap_frame_time
    > 6.08
    >>> sync.end_frame_index
    > 10806
    >>> sync.end_frame_time
    > 216.12


### Constructor

#### __init__

```python
def __init__(self, session: avSession, fps: float, video_clap: float=None, reference_delta: float=None):
    """Compute synchronization boundaries from the given session and fps.

    Algorithm — faithful transcription of the original montage scripts
    (montage_step1.py / montage.py, Brigitte Bigi, CNRS/LPL 2021-2024):

    Notation:
      vc   = video_clap + delay       (effective clap time in the video)
      fps  = frame rate of this video
      dur  = session.duration

    Step 1 — clap frame (primary / reference video):
      clap_frame_index = int(vc * fps)          # floor, 0-based
      clap_frame_time  = clap_frame_index / fps
      clap_delta       = vc - clap_frame_time   # in [0, 1/fps)

    Step 2 — end frame (first excluded frame):
      end_frame_index  = 1 + int((vc + dur) * fps)
      end_frame_time   = end_frame_index / fps

    Step 3 — cross-sync (secondary video, fps2 != fps_ref):
      Given reference_delta = clap_delta of the reference (lowest-fps) video:
      shift_frames     = int(reference_delta * fps2)
      clap_frame_index = int(vc2 * fps2) - shift_frames
      end_frame_index  = 1 + int((vc2 + dur) * fps2) + shift_frames

      IMPORTANT: the subtraction int(A*fps) - int(d*fps) is used, NOT
      int((A-d)*fps), to match the original script exactly. These differ
      by 1 when frac(A*fps) < frac(d*fps).

    Audio alignment (per audio file, handled by the pipeline):
      Pass 1: shift audio so its effective clap matches vc (trim or pad).
      Pass 2: pad or trim to reach end_frame_time.
      Pass 3: trim clap_frame_time from the start.

    :param session: (avSession) avSession containing media files and timing.
    :param fps: (float) Frame rate of the reference video (frames/second).
    :param video_clap: (float|None) Clap time in the video (seconds). When
        None, session.videos[0].clap_time is used.
    :param reference_delta: (float|None) clap_delta of the reference
        (lowest-fps) video. When provided, applies cross-video
        synchronization (Step 3 above). When None, each video snaps
        independently to its own frame boundary (Step 1 above).
    :raises: TypeError: session is not a avSession instance.
    :raises: TypeError: fps is not a number.
    :raises: ValueError: fps is not strictly positive.
    :raises: TypeError: video_clap is not a number when not None.
    :raises: ValueError: video_clap is negative.
    :raises: TypeError: reference_delta is not a number when not None.
    :raises: ValueError: reference_delta is negative.

    """
    if isinstance(session, avSession) is False:
        raise TypeError('session must be a avSession instance.')
    if isinstance(fps, (int, float)) is False:
        raise TypeError('fps must be a number.')
    if float(fps) <= 0.0:
        raise ValueError('fps must be strictly positive.')
    if video_clap is None:
        raw_video_clap = session.videos[0].clap_time
    else:
        if isinstance(video_clap, (int, float)) is False:
            raise TypeError('video_clap must be a number.')
        if float(video_clap) < 0.0:
            raise ValueError('video_clap must be zero or positive.')
        raw_video_clap = float(video_clap)
    if reference_delta is not None:
        if isinstance(reference_delta, (int, float)) is False:
            raise TypeError('reference_delta must be a number.')
        if float(reference_delta) < 0.0:
            raise ValueError('reference_delta must be zero or positive.')
    self.__session = session
    self.__fps = float(fps)
    video_clap_with_delay = raw_video_clap + session.delay
    self.__video_clap_with_delay = video_clap_with_delay
    if reference_delta is None:
        self.__clap_frame_index = avVideoOps.time_to_frame(video_clap_with_delay, self.__fps)
    else:
        shift_frames = int(float(reference_delta) * self.__fps)
        self.__clap_frame_index = avVideoOps.time_to_frame(video_clap_with_delay, self.__fps) - shift_frames
    self.__clap_frame_time = avVideoOps.frame_to_time(self.__clap_frame_index, self.__fps)
    self.__clap_delta = video_clap_with_delay - self.__clap_frame_time
    self.__end_frame_index = avVideoOps.end_frame_index(video_clap_with_delay, session.duration, self.__fps)
    if reference_delta is not None:
        self.__end_frame_index = self.__end_frame_index + shift_frames
    self.__end_frame_time = avVideoOps.frame_to_time(self.__end_frame_index, self.__fps)
```

*Compute synchronization boundaries from the given session and fps.*

Algorithm — faithful transcription of the original montage scripts
(montage_step1.py / montage.py, Brigitte Bigi, CNRS/LPL 2021-2024):

Notation:
vc   = video_clap + delay       (effective clap time in the video)
fps  = frame rate of this video
dur  = session.duration

Step 1 — clap frame (primary / reference video):
clap_frame_index = int(vc * fps)          # floor, 0-based
clap_frame_time  = clap_frame_index / fps
clap_delta       = vc - clap_frame_time   # in [0, 1/fps)

Step 2 — end frame (first excluded frame):
end_frame_index  = 1 + int((vc + dur) * fps)
end_frame_time   = end_frame_index / fps

Step 3 — cross-sync (secondary video, fps2 != fps_ref):
Given reference_delta = clap_delta of the reference (lowest-fps) video:
shift_frames     = int(reference_delta * fps2)
clap_frame_index = int(vc2 * fps2) - shift_frames
end_frame_index  = 1 + int((vc2 + dur) * fps2) + shift_frames

IMPORTANT: the subtraction int(A*fps) - int(d*fps) is used, NOT
int((A-d)*fps), to match the original script exactly. These differ
by 1 when frac(A*fps) < frac(d*fps).

Audio alignment (per audio file, handled by the pipeline):
Pass 1: shift audio so its effective clap matches vc (trim or pad).
Pass 2: pad or trim to reach end_frame_time.
Pass 3: trim clap_frame_time from the start.

##### Parameters

- **session**: (avSession) avSession containing media files and timing.
- **fps**: (*float*) Frame rate of the reference video (frames/second).
- **video_clap**: (*float*|None) Clap time in the video (seconds). When None, session.videos[0].clap_time is used.
- **reference_delta**: (*float*|None) clap_delta of the reference (lowest-fps) video. When provided, applies cross-video synchronization (Step 3 above). When None, each video snaps independently to its own frame boundary (Step 1 above).


##### Raises

- *TypeError*: session is not a avSession instance.
- *TypeError*: fps is not a number.
- *ValueError*: fps is not strictly positive.
- *TypeError*: video_clap is not a number when not None.
- *ValueError*: video_clap is negative.
- *TypeError*: reference_delta is not a number when not None.
- *ValueError*: reference_delta is negative.



### Public functions

#### get_fps

```python
def get_fps(self) -> float:
    """Return the frame rate used for synchronization.

        :return: (float) Frame rate in frames per second.

        """
    return self.__fps
```

*Return the frame rate used for synchronization.*

##### Returns

- (*float*) Frame rate in frames per second.

#### get_clap_frame_index

```python
def get_clap_frame_index(self) -> int:
    """Return the 0-based index of the frame containing the clap.

        This is the start frame for video trimming.

        :return: (int) Start frame index.

        """
    return self.__clap_frame_index
```

*Return the 0-based index of the frame containing the clap.*

This is the start frame for video trimming.

##### Returns

- (*int*) Start frame index.

#### get_clap_delta

```python
def get_clap_delta(self) -> float:
    """Return the gap between the actual clap time and its frame boundary (seconds).

        This is the sub-frame offset used for cross-video synchronization:
        all videos in a session share the same delta so the clap appears at
        the same position in every output file.

        :return: (float) Delta in seconds (always in [0, 1/fps[).

        """
    return self.__clap_delta
```

*Return the gap between the actual clap time and its frame boundary (seconds).*

This is the sub-frame offset used for cross-video synchronization:
all videos in a session share the same delta so the clap appears at
the same position in every output file.

##### Returns

- (*float*) Delta in seconds (always in [0, 1/fps[).

#### get_clap_frame_time

```python
def get_clap_frame_time(self) -> float:
    """Return the start time of the clap frame (seconds).

        This is the reference time to which all audio files are aligned.
        It corresponds to the exact beginning of the frame containing the
        clap, which may differ slightly from the raw clap time.

        :return: (float) Clap frame start time in seconds.

        """
    return self.__clap_frame_time
```

*Return the start time of the clap frame (seconds).*

This is the reference time to which all audio files are aligned.
It corresponds to the exact beginning of the frame containing the
clap, which may differ slightly from the raw clap time.

##### Returns

- (*float*) Clap frame start time in seconds.

#### get_end_frame_index

```python
def get_end_frame_index(self) -> int:
    """Return the index of the first frame NOT included in the output.

        This is the end frame for video trimming (exclusive upper bound).

        :return: (int) End frame index (exclusive).

        """
    return self.__end_frame_index
```

*Return the index of the first frame NOT included in the output.*

This is the end frame for video trimming (exclusive upper bound).

##### Returns

- (*int*) End frame index (exclusive).

#### get_end_frame_time

```python
def get_end_frame_time(self) -> float:
    """Return the time of the end frame boundary (seconds).

        This is the exact duration target to which all audio files are
        padded or trimmed after clap alignment.

        :return: (float) End frame time in seconds.

        """
    return self.__end_frame_time
```

*Return the time of the end frame boundary (seconds).*

This is the exact duration target to which all audio files are
padded or trimmed after clap alignment.

##### Returns

- (*float*) End frame time in seconds.

#### get_audio_reference_clap

```python
def get_audio_reference_clap(self) -> float:
    """Return the clap time to which audio files must be aligned.

        This is the effective video clap time (raw video clap + delay).
        Audio files are shifted so that their own clap (plus delay) coincides
        with this value. The sub-frame offset (clap_delta) is preserved in the
        output, matching the original script behaviour.

        :return: (float) Audio alignment target in seconds.

        """
    return self.__video_clap_with_delay
```

*Return the clap time to which audio files must be aligned.*

This is the effective video clap time (raw video clap + delay).
Audio files are shifted so that their own clap (plus delay) coincides
with this value. The sub-frame offset (clap_delta) is preserved in the
output, matching the original script behaviour.

##### Returns

- (*float*) Audio alignment target in seconds.

#### get_audio_clap_with_delay

```python
def get_audio_clap_with_delay(self, audio_clap: float) -> float:
    """Return the effective audio clap time, shifted by the session delay.

        :param audio_clap: (float) Raw clap time in the audio file (seconds).
        :return: (float) Effective clap time in seconds (audio_clap + delay).
        :raises: TypeError: audio_clap is not a number.

        """
    if isinstance(audio_clap, (int, float)) is False:
        raise TypeError('audio_clap must be a number.')
    return float(audio_clap) + self.__session.delay
```

*Return the effective audio clap time, shifted by the session delay.*

##### Parameters

- **audio_clap**: (*float*) Raw clap time in the audio file (seconds).


##### Returns

- (*float*) Effective clap time in seconds (audio_clap + delay).


##### Raises

- *TypeError*: audio_clap is not a number.

#### check_video_duration

```python
def check_video_duration(self, video_duration: float) -> None:
    """Raise ValueError if the expected end time exceeds the video duration.

        This check must be performed before trimming to avoid requesting more
        frames than the video contains.

        :param video_duration: (float) Actual duration of the video (seconds).
        :raises: TypeError: video_duration is not a number.
        :raises: ValueError: The expected end frame time exceeds video_duration.

        """
    if isinstance(video_duration, (int, float)) is False:
        raise TypeError('video_duration must be a number.')
    if self.__end_frame_time > float(video_duration):
        raise ValueError(f'The expected end time ({self.__end_frame_time:.3f}s) exceeds the video duration ({float(video_duration):.3f}s). Check the duration value in the CSV.')
```

*Raise ValueError if the expected end time exceeds the video duration.*

This check must be performed before trimming to avoid requesting more
frames than the video contains.

##### Parameters

- **video_duration**: (*float*) Actual duration of the video (seconds).


##### Raises

- *TypeError*: video_duration is not a number.
- *ValueError*: The expected end frame time exceeds video_duration.



### Overloads

#### __repr__

```python
def __repr__(self) -> str:
    return f'avClapSync(fps={self.__fps}, clap_frame={self.__clap_frame_index} ({self.__clap_frame_time:.3f}s), end_frame={self.__end_frame_index} ({self.__end_frame_time:.3f}s))'
```





## Class `avPipeline`

### Description

*Orchestrate the AViSS synchronization pipeline for one avSession.*

A avPipeline instance is created for one avSession. Calling run() executes
all steps and returns a avSyncResult. Intermediate files are written to
a working directory named after the output filename stem.

##### Example

    >>> pipeline = avPipeline(session)
    >>> result = pipeline.run()
    >>> result.success
    > True
    >>> result.synced_files
    > ['/out/Laurent_S09_sent.wav', '/out/Laurent_S09_sent.mkv']


### Constructor

#### __init__

```python
def __init__(self, session: avSession):
    """Initialize the pipeline for the given session.

    :param session: (avSession) avSession to process.
    :raises: TypeError: session is not a avSession instance.

    """
    if isinstance(session, avSession) is False:
        raise TypeError('session must be a avSession instance.')
    self.__session = session
    self.__result = avSyncResult()
    self.__work_dir = None
    self.__stem = None
```

*Initialize the pipeline for the given session.*

##### Parameters

- **session**: (avSession) avSession to process.


##### Raises

- *TypeError*: session is not a avSession instance.



### Public functions

#### run

```python
def run(self) -> avSyncResult:
    """Execute all pipeline steps and return the synchronization result.

        :return: (avSyncResult) Result of the pipeline run.

        """
    try:
        self.__step_prepare()
        audio_items, video_items = self.__step_build_items()
        self.__step_sync_audios(audio_items)
        self.__step_trim_videos(video_items)
        self.__step_post_process_videos(video_items)
        self.__result.success = True
    except Exception as e:
        self.__log(f'ERROR: {e}')
        self.__result.success = False
    return self.__result
```

*Execute all pipeline steps and return the synchronization result.*

##### Returns

- (avSyncResult) Result of the pipeline run.



### Protected functions

#### __log

```python
def __log(self, message: str) -> None:
    """Add a message to the result report and write it to the logger.

        :param message: (str) Message to log.

        """
    self.__result.add_message(message)
    aviss_logger.write(message)
```

*Add a message to the result report and write it to the logger.*

##### Parameters

- **message**: (*str*) Message to log.

#### __log_step

```python
def __log_step(self, number: int, title: str) -> None:
    """Write a step separator matching the original script log format.

        :param number: (int) Step number.
        :param title: (str) Step title.

        """
    msg = f'STEP {number}: {title}'
    space = ' ' * ((60 - len(msg)) // 2)
    self.__log('')
    self.__log('----------------------------------------------------------------')
    self.__log(space + msg)
    self.__log('----------------------------------------------------------------')
```

*Write a step separator matching the original script log format.*

##### Parameters

- **number**: (*int*) Step number.
- **title**: (*str*) Step title.

#### __log_ok

```python
def __log_ok(self, path: str) -> None:
    """Write an [  OK  ] confirmation line for the given path.

        :param path: (str) Path to confirm.

        """
    self.__log(f'[  OK  ] {path}')
```

*Write an [  OK  ] confirmation line for the given path.*

##### Parameters

- **path**: (*str*) Path to confirm.

#### __log_audio_info

```python
def __log_audio_info(self, path: str) -> None:
    """Write an audio file info block matching the original script format.

        :param path: (str) Path to the audio file.

        """
    info = avAudioOps.get_audio_info(path)
    self.__log(f' ... Test audio file: {path}')
    self.__log(f'    - duration: {info['duration']:.3f}')
    self.__log(f'    - framerate: {info['framerate']:d}')
    self.__log(f'    - channels: {info['nchannels']:d}')
    self.__log(f'    - bitrate: {info['sampwidth'] * 8:d}')
```

*Write an audio file info block matching the original script format.*

##### Parameters

- **path**: (*str*) Path to the audio file.

#### __log_video_info

```python
def __log_video_info(self, path: str) -> None:
    """Write a video file info block matching the original script format.

        :param path: (str) Path to the video file.

        """
    info = avVideoOps.get_video_info(path)
    self.__log('  - video container: mkv')
    self.__log(f'  - video codec: libx265 (crf={cfg.output.crf:d})')
    if cfg.output.copyright is not None:
        self.__log(f'  - copyright: {cfg.output.copyright}')
    self.__log('  - no audio')
    self.__log(f'  - fps: {info['fps']:.2f}')
    self.__log(f'  - nframes: {info['nframes']:d}')
    self.__log(f'  - duration: {info['duration']:f}')
    self.__log(f'  - size: ({info['width']}, {info['height']})')
```

*Write a video file info block matching the original script format.*

##### Parameters

- **path**: (*str*) Path to the video file.

#### __step_prepare

```python
def __step_prepare(self) -> None:
    """Verify dependencies, build the output stem and create the working dir.

        """
    for cmd in avPipeline.REQUIRED_COMMANDS:
        check_command(cmd)
    missing = [m.path for m in self.__session.audios + self.__session.videos if m.exists() is False]
    if len(missing) > 0:
        raise FileNotFoundError('Media file(s) not found: ' + ', '.join((repr(p) for p in missing)))
    self.__stem = build_output_name(self.__session.output_name_meta, cfg.output.output_name_cols, cfg.output.output_sep)
    if len(self.__stem) == 0:
        raise ValueError('The output filename stem is empty. Check cfg.output.output_name_cols and the CSV metadata columns.')
    work_dir_name = self.__stem + cfg.output.work_dir_suffix
    self.__work_dir = create_working_dir(work_dir_name)
    self.__log_step(0, 'Parse CSV and check media files')
    self.__log(f' ... Output working dir: {self.__work_dir}')
    for audio in self.__session.audios:
        self.__log_audio_info(audio.path)
        self.__log(f' ... Input audio file: {audio.path}')
        self.__log_ok(audio.path)
    for video in self.__session.videos:
        info = avVideoOps.get_video_info(video.path)
        self.__log(f' ... Input video file: {video.path} ({info['fps']:.2f} fps)')
        self.__log_ok(video.path)
    delay = self.__session.delay
    self.__log(f' ... Given delta: {delay:.3f}')
    for audio in self.__session.audios:
        self.__log(f' ... Given audio clap: {audio.clap_time + delay:.3f}')
    for video in self.__session.videos:
        self.__log(f' ... Given video clap: {video.clap_time + delay:.3f}')
    self.__log(f' ... Given expected duration: {self.__session.duration:.3f}')
```

*Verify dependencies, build the output stem and create the working dir.*



#### __step_build_items

```python
def __step_build_items(self) -> tuple:
    """Compute sync objects and build independent audio and video item lists.

        All media share the same clap event. The video with the lowest fps
        defines the reference avClapSync used by all audios. Each video gets
        its own avClapSync (frame-accurate at its own fps).

        Audio suffixes (from CSV column index):
            audio_file  -> ""
            audio_file2 -> "_audio2", audio_file3 -> "_audio3", ...

        Video suffixes (from video_name or CSV column index):
            single video           -> ""
            multiple, named        -> "_" + video_name
            multiple, unnamed      -> "_video2", "_video3", ...

        :return: (tuple) (audio_items, video_items) where each list contains
                 (avMediaFile, avClapSync, out_name) tuples.

        """
    self.__log_step(1, 'Compute synchronization boundaries')
    videos = self.__session.videos
    audios = self.__session.audios
    names = self.__session.video_names
    n = len(videos)
    m = len(audios)
    infos = [avVideoOps.get_video_info(v.path) for v in videos]
    ref_idx = min(range(n), key=lambda i: infos[i]['fps'])
    ref_sync = avClapSync(self.__session, infos[ref_idx]['fps'], video_clap=videos[ref_idx].clap_time)
    ref_delta = ref_sync.clap_delta
    if n > 1:
        self.__log(f'  Reference delta: {ref_delta:.6f}s (video {ref_idx + 1}, {infos[ref_idx]['fps']:.2f} fps)')
    video_syncs = []
    for i in range(n):
        if i == ref_idx:
            video_syncs.append(ref_sync)
        else:
            video_syncs.append(avClapSync(self.__session, infos[i]['fps'], video_clap=videos[i].clap_time, reference_delta=ref_delta))
    for i, (sync, info) in enumerate(zip(video_syncs, infos)):
        sync.check_video_duration(info['duration'])
        self.__log(f' ... Video {i + 1}: start time value of the frame with the clap: {sync.clap_frame_index} frames = {sync.clap_frame_time:.3f} seconds')
        self.__log(f' ... ... Delta among the real clap position in the video and the start time of the first frame in the video = {sync.clap_delta:.6f}')
        self.__log(f' ... estimated end time of video {i + 1}: {sync.end_frame_index} frames = {sync.end_frame_time:.3f} seconds')
    if n == 1:
        video_suffixes = ['']
    else:
        video_suffixes = []
        for i, name in enumerate(names):
            if name is not None:
                video_suffixes.append('_' + name)
            else:
                video_suffixes.append('_video' + str(i + 1))
    if m == 1:
        audio_suffixes = ['']
    else:
        audio_suffixes = [''] + ['_audio' + str(i + 1) for i in range(1, m)]
    video_items = []
    for video, sync, suffix in zip(videos, video_syncs, video_suffixes):
        video_items.append((video, sync, self.__stem + suffix + '.mkv'))
    audio_items = []
    for audio, suffix in zip(audios, audio_suffixes):
        audio_items.append((audio, ref_sync, self.__stem + suffix + '.wav'))
    return (audio_items, video_items)
```

*Compute sync objects and build independent audio and video item lists.*

All media share the same clap event. The video with the lowest fps
defines the reference avClapSync used by all audios. Each video gets
its own avClapSync (frame-accurate at its own fps).

Audio suffixes (from CSV column index):
audio_file  -> ""
audio_file2 -> "_audio2", audio_file3 -> "_audio3", ...

Video suffixes (from video_name or CSV column index):
single video           -> ""
multiple, named        -> "_" + video_name
multiple, unnamed      -> "_video2", "_video3", ...

##### Returns

- (*tuple*) (audio_items, video_items) where each list contains (avMediaFile, avClapSync, out_name) tuples.

#### __step_sync_audios

```python
def __step_sync_audios(self, audio_items: list) -> None:
    """Align and trim each audio file to the reference synchronization.

        :param audio_items: (list) List of (audio_media, avClapSync, out_name) tuples.

        """
    self.__log_step(2, 'Synchronize audio files')
    for audio, sync, audio_out in audio_items:
        self.__sync_one_audio(audio.path, audio.clap_time, sync, audio_out)
```

*Align and trim each audio file to the reference synchronization.*

##### Parameters

- **audio_items**: (*list*) List of (audio_media, avClapSync, out_name) tuples.

#### __sync_one_audio

```python
def __sync_one_audio(self, audio_path: str, raw_clap: float, sync: avClapSync, out_name: str) -> None:
    """Align and trim a single audio file.

        :param audio_path: (str) Path to the input audio file.
        :param raw_clap: (float) Raw clap time in the audio (seconds).
        :param sync: (avClapSync) Synchronization boundaries.
        :param out_name: (str) Filename (not path) for the final output.

        """
    effective_clap = sync.get_audio_clap_with_delay(raw_clap)
    tmp_clap = os.path.join(self.__work_dir, '_audio_clap.wav')
    tmp_dur = os.path.join(self.__work_dir, '_audio_dur.wav')
    raw_name = out_name.replace('.wav', '-audio.wav')
    final_raw = os.path.join(self.__work_dir, raw_name)
    final = os.path.join(self.__work_dir, out_name)
    avAudioOps.adjust_audio_at_clap(audio_path, effective_clap, sync.audio_reference_clap, tmp_clap)
    self.__log_ok(tmp_clap)
    self.__log(f'  - expected end time of audio: {sync.end_frame_time:.3f}')
    avAudioOps.adjust_audio_duration(tmp_clap, sync.end_frame_time, tmp_dur)
    self.__log_ok(tmp_dur)
    self.__log(f'  - expected start time of audio: {sync.clap_frame_time:.3f}')
    avAudioOps.trim_audio(tmp_dur, sync.clap_frame_time, final_raw, begin=True)
    self.__log_ok(final_raw)
    self.__log_audio_info(final_raw)
    avAudioOps.to_mono_16k(final_raw, final)
    self.__log_ok(final)
    self.__log_audio_info(final)
    if os.path.isfile(tmp_clap) is True:
        os.remove(tmp_clap)
    if os.path.isfile(tmp_dur) is True:
        os.remove(tmp_dur)
    self.__result.add_synced_file(final_raw)
    self.__result.add_synced_file(final)
```

*Align and trim a single audio file.*

##### Parameters

- **audio_path**: (*str*) Path to the input audio file.
- **raw_clap**: (*float*) Raw clap time in the audio (seconds).
- **sync**: (avClapSync) Synchronization boundaries.
- **out_name**: (*str*) Filename (not path) for the final output.

#### __step_trim_videos

```python
def __step_trim_videos(self, video_items: list) -> None:
    """Trim each video between its own clap frame and end frame.

        :param video_items: (list) List of (video_media, avClapSync, out_name) tuples.

        """
    self.__log_step(3, 'Trim video files')
    for video, sync, video_out in video_items:
        out_path = os.path.join(self.__work_dir, video_out)
        avVideoOps.trim(video.path, sync.clap_frame_index, sync.end_frame_index, out_path)
        self.__result.add_synced_file(out_path)
        self.__log_ok(out_path)
```

*Trim each video between its own clap frame and end frame.*

##### Parameters

- **video_items**: (*list*) List of (video_media, avClapSync, out_name) tuples.

#### __step_post_process_videos

```python
def __step_post_process_videos(self, video_items: list) -> None:
    """Apply crop and copyright overlay to each trimmed video.

        :param video_items: (list) List of (video_media, avClapSync, out_name) tuples.

        """
    self.__log_step(4, 'Post-process video files')
    for video, _sync, video_out in video_items:
        current = os.path.join(self.__work_dir, video_out)
        current = self.__apply_crop(video, current)
        current = self.__apply_copyright(current)
        self.__log_video_info(current)
        self.__log_ok(current)
```

*Apply crop and copyright overlay to each trimmed video.*

##### Parameters

- **video_items**: (*list*) List of (video_media, avClapSync, out_name) tuples.

#### __apply_crop

```python
def __apply_crop(self, media, video_path: str) -> str:
    """Apply crop to a video if the media file defines a crop region.

        :param media: (avMediaFile) Media file with optional crop parameters.
        :param video_path: (str) Path to the current video file.
        :return: (str) Path to the (possibly cropped) video file.

        """
    if media.has_crop() is False:
        return video_path
    self.__log(f'  - crop: x={media.crop_x} y={media.crop_y} w={media.crop_w} h={media.crop_h}')
    tmp_path = video_path.replace('.mkv', '_tmp_crop.mkv')
    avVideoOps.crop(video_path, media.crop_x, media.crop_y, media.crop_w, media.crop_h, tmp_path)
    os.remove(video_path)
    os.rename(tmp_path, video_path)
    return video_path
```

*Apply crop to a video if the media file defines a crop region.*

##### Parameters

- **media**: (avMediaFile) Media file with optional crop parameters.
- **video_path**: (*str*) Path to the current video file.


##### Returns

- (*str*) Path to the (possibly cropped) video file.

#### __apply_copyright

```python
def __apply_copyright(self, video_path: str) -> str:
    """Apply a copyright overlay to a video if configured.

        :param video_path: (str) Path to the current video file.
        :return: (str) Path to the (possibly annotated) video file.

        """
    if cfg.output.copyright is None:
        return video_path
    self.__log('  - copyright overlay applied')
    tmp_path = video_path.replace('.mkv', '_tmp_copy.mkv')
    avVideoOps.add_copyright(video_path, cfg.output.copyright, tmp_path)
    os.remove(video_path)
    os.rename(tmp_path, video_path)
    return video_path
```

*Apply a copyright overlay to a video if configured.*

##### Parameters

- **video_path**: (*str*) Path to the current video file.


##### Returns

- (*str*) Path to the (possibly annotated) video file.



## Class `avCsvReader`

### Description

*Parse an AViSS CSV file and produce a list of avSession objects.*

The CSV file must have a header row as its first line. Column names in
the header are matched against the names declared in cfg.sync and
cfg.output. Matching is case-sensitive.

The separator is auto-detected: ';' is tried first, then ','.
A minimum of 6 columns is required (audio_file, audio_clap, video_file,
video_clap, delay, duration).

##### Example

    >>> reader = avCsvReader("corpus/sessions.csv")
    >>> sessions = reader.read()
    >>> len(sessions)
    > 10
    >>> sessions[0].audio.path
    > '/data/corpus/Laurent_S01_s1.wav'


### Constructor

#### __init__

```python
def __init__(self, csv_path: str):
    """Initialize the avCsvReader with the path to the CSV file.

    :param csv_path: (str) Path to the CSV file.
    :raises: TypeError: csv_path is not a non-empty string.
    :raises: FileNotFoundError: The file does not exist.
    :raises: ValueError: The file is empty.

    """
    if isinstance(csv_path, str) is False or len(csv_path.strip()) == 0:
        raise TypeError('csv_path must be a non-empty string.')
    check_file(csv_path)
    self.__csv_path = csv_path.strip()
    self.__csv_dir = os.path.dirname(os.path.abspath(csv_path))
    self.__separator = None
```

*Initialize the avCsvReader with the path to the CSV file.*

##### Parameters

- **csv_path**: (*str*) Path to the CSV file.


##### Raises

- *TypeError*: csv_path is not a non-empty string.
- *FileNotFoundError*: The file does not exist.
- *ValueError*: The file is empty.



### Public functions

#### get_csv_path

```python
def get_csv_path(self) -> str:
    """Return the path to the CSV file.

        :return: (str) CSV file path.

        """
    return self.__csv_path
```

*Return the path to the CSV file.*

##### Returns

- (*str*) CSV file path.

#### read

```python
def read(self) -> list:
    """Parse the CSV file and return a list of avSession objects.

        The first row is interpreted as the header. Each subsequent non-empty
        row produces one avSession. Rows with all-empty cells are silently skipped.

        :return: (list) List of avSession instances, one per data row.
        :raises: ValueError: The header row is missing or invalid.
        :raises: ValueError: A data row cannot be parsed into a avSession.

        """
    raw_lines = self.__read_raw_lines()
    if len(raw_lines) < 2:
        raise ValueError(f'CSV file {self.__csv_path!r} must have at least one header row and one data row.')
    header = self.__parse_header(raw_lines[0])
    self.__check_required_columns(header)
    sessions = []
    for row_index, raw_line in enumerate(raw_lines[1:], start=2):
        row = self.__split_row(raw_line)
        if len(row) == 0 or all((len(v.strip()) == 0 for v in row)):
            continue
        session = self.__build_session(header, row, row_index)
        sessions.append(session)
    return sessions
```

*Parse the CSV file and return a list of avSession objects.*

The first row is interpreted as the header. Each subsequent non-empty
row produces one avSession. Rows with all-empty cells are silently skipped.

##### Returns

- (*list*) List of avSession instances, one per data row.


##### Raises

- *ValueError*: The header row is missing or invalid.
- *ValueError*: A data row cannot be parsed into a avSession.

#### read_row

```python
def read_row(self, row_number: int) -> avSession:
    """Parse a single data row and return the corresponding avSession.

        Row numbering starts at 1 (the first data row, after the header).

        :param row_number: (int) 1-based index of the data row to parse.
        :return: (avSession) avSession built from the given row.
        :raises: TypeError: row_number is not an integer.
        :raises: ValueError: row_number is out of range.
        :raises: ValueError: The row cannot be parsed into a avSession.

        """
    if isinstance(row_number, int) is False:
        raise TypeError('row_number must be an integer.')
    if row_number < 1:
        raise ValueError('row_number must be >= 1.')
    raw_lines = self.__read_raw_lines()
    if len(raw_lines) < 2:
        raise ValueError(f'CSV file {self.__csv_path!r} must have at least one header row and one data row.')
    header = self.__parse_header(raw_lines[0])
    self.__check_required_columns(header)
    data_lines = [ln for ln in raw_lines[1:] if len(ln.strip()) > 0]
    if row_number > len(data_lines):
        raise ValueError(f'Row number {row_number} is out of range. The CSV file has {len(data_lines)} data row(s).')
    row = self.__split_row(data_lines[row_number - 1])
    return self.__build_session(header, row, row_number + 1)
```

*Parse a single data row and return the corresponding avSession.*

Row numbering starts at 1 (the first data row, after the header).

##### Parameters

- **row_number**: (*int*) 1-based index of the data row to parse.


##### Returns

- (avSession) avSession built from the given row.


##### Raises

- *TypeError*: row_number is not an integer.
- *ValueError*: row_number is out of range.
- *ValueError*: The row cannot be parsed into a avSession.



### Protected functions

#### __read_raw_lines

```python
def __read_raw_lines(self) -> list:
    """Read the CSV file and return its non-empty lines as strings.

        :return: (list) List of raw line strings.

        """
    with open(self.__csv_path, 'r', encoding='utf-8') as fh:
        lines = fh.readlines()
    return [ln.rstrip('\n').rstrip('\r') for ln in lines if len(ln.strip()) > 0]
```

*Read the CSV file and return its non-empty lines as strings.*

##### Returns

- (*list*) List of raw line strings.

#### __split_row

```python
def __split_row(self, line: str) -> list:
    """Split a CSV row using the detected or auto-detected separator.

        :param line: (str) Raw CSV line.
        :return: (list) List of cell strings.

        """
    if self.__separator is not None:
        return line.split(self.__separator)
    for sep in avCsvReader.SEPARATORS:
        parts = line.split(sep)
        if len(parts) >= avCsvReader.MIN_COLUMNS:
            self.__separator = sep
            return parts
    return line.split(avCsvReader.SEPARATORS[0])
```

*Split a CSV row using the detected or auto-detected separator.*

##### Parameters

- **line**: (*str*) Raw CSV line.


##### Returns

- (*list*) List of cell strings.

#### __parse_header

```python
def __parse_header(self, line: str) -> list:
    """Parse the header row and return a list of stripped column names.

        :param line: (str) Raw header line.
        :return: (list) List of column name strings.
        :raises: ValueError: The header row has fewer columns than the minimum.

        """
    columns = self.__split_row(line)
    columns = [c.strip() for c in columns]
    if len(columns) < avCsvReader.MIN_COLUMNS:
        raise ValueError(f'CSV header has only {len(columns)} column(s). At least {avCsvReader.MIN_COLUMNS} are required.')
    return columns
```

*Parse the header row and return a list of stripped column names.*

##### Parameters

- **line**: (*str*) Raw header line.


##### Returns

- (*list*) List of column name strings.


##### Raises

- *ValueError*: The header row has fewer columns than the minimum.

#### __check_required_columns

```python
def __check_required_columns(self, header: list) -> None:
    """Raise ValueError if any required synchronization column is missing.

        :param header: (list) List of column names from the header row.
        :raises: ValueError: One or more required columns are absent.

        """
    required = [cfg.sync.col_audio_file, cfg.sync.col_audio_clap, cfg.sync.col_video_file, cfg.sync.col_video_clap, cfg.sync.col_delay, cfg.sync.col_duration]
    missing = [col for col in required if col not in header]
    if len(missing) > 0:
        raise ValueError(f'The following required columns are missing from the CSV header: {missing}. Check cfg.sync column name settings.')
```

*Raise ValueError if any required synchronization column is missing.*

##### Parameters

- **header**: (*list*) List of column names from the header row.


##### Raises

- *ValueError*: One or more required columns are absent.

#### __get_cell

```python
def __get_cell(self, header: list, row: list, col_name: str) -> str:
    """Return the stripped cell value for the given column name, or "".

        :param header: (list) List of column names.
        :param row: (list) List of cell values for the current row.
        :param col_name: (str) Column name to look up.
        :return: (str) Cell value, or "" if the column is absent or the row
                 is too short.

        """
    if col_name not in header:
        return ''
    idx = header.index(col_name)
    if idx >= len(row):
        return ''
    return row[idx].strip()
```

*Return the stripped cell value for the given column name, or "".*

##### Parameters

- **header**: (*list*) List of column names.
- **row**: (*list*) List of cell values for the current row.
- **col_name**: (*str*) Column name to look up.


##### Returns

- (*str*) Cell value, or "" if the column is absent or the row is too short.

#### __resolve_path

```python
def __resolve_path(self, relative: str) -> str:
    """Resolve a relative file path against the CSV directory.

        :param relative: (str) Relative path as found in the CSV cell.
        :return: (str) Absolute path.

        """
    if os.path.isabs(relative) is True:
        return relative
    return os.path.join(self.__csv_dir, relative)
```

*Resolve a relative file path against the CSV directory.*

##### Parameters

- **relative**: (*str*) Relative path as found in the CSV cell.


##### Returns

- (*str*) Absolute path.

#### __build_crop

```python
def __build_crop(self, header: list, row: list, suffix: str='') -> tuple:
    """Extract crop parameters for a video column set.

        The suffix is "" for the primary video and "2" for the secondary one.
        All four values must be present and non-empty for crop to be applied;
        otherwise (None, None, None, None) is returned.

        :param header: (list) List of column names.
        :param row: (list) List of cell values for the current row.
        :param suffix: (str) Column name suffix ("" or "2").
        :return: (tuple) (x, y, w, h) as int|None values.

        """
    x_str = self.__get_cell(header, row, cfg.sync.col_video_crop_x + suffix)
    y_str = self.__get_cell(header, row, cfg.sync.col_video_crop_y + suffix)
    w_str = self.__get_cell(header, row, cfg.sync.col_video_crop_w + suffix)
    h_str = self.__get_cell(header, row, cfg.sync.col_video_crop_h + suffix)
    if len(x_str) == 0 or len(y_str) == 0 or len(w_str) == 0 or (len(h_str) == 0):
        return (None, None, None, None)
    try:
        return (int(x_str), int(y_str), int(w_str), int(h_str))
    except ValueError:
        return (None, None, None, None)
```

*Extract crop parameters for a video column set.*

The suffix is "" for the primary video and "2" for the secondary one.
All four values must be present and non-empty for crop to be applied;
otherwise (None, None, None, None) is returned.

##### Parameters

- **header**: (*list*) List of column names.
- **row**: (*list*) List of cell values for the current row.
- **suffix**: (*str*) Column name suffix ("" or "2").


##### Returns

- (*tuple*) (x, y, w, h) as int|None values.

#### __build_media_file

```python
def __build_media_file(self, header: list, row: list, col_file: str, col_clap: str, crop: tuple, row_index: int) -> avMediaFile:
    """Build a avMediaFile from the given column names and crop tuple.

        :param header: (list) List of column names.
        :param row: (list) List of cell values.
        :param col_file: (str) Column name for the file path.
        :param col_clap: (str) Column name for the clap time.
        :param crop: (tuple) (x, y, w, h) as int|None.
        :param row_index: (int) 1-based row number, used in error messages.
        :return: (avMediaFile) Constructed avMediaFile instance.
        :raises: ValueError: A required cell is empty or invalid.

        """
    path_raw = self.__get_cell(header, row, col_file)
    clap_raw = self.__get_cell(header, row, col_clap)
    if len(path_raw) == 0:
        raise ValueError(f'Row {row_index}: column {col_file!r} is empty.')
    if len(clap_raw) == 0:
        raise ValueError(f'Row {row_index}: column {col_clap!r} is empty.')
    try:
        clap_seconds = time_to_seconds(clap_raw)
    except ValueError as e:
        raise ValueError(f'Row {row_index}: invalid clap time in column {col_clap!r}. {e}.')
    media = avMediaFile(self.__resolve_path(path_raw), clap_seconds)
    x, y, w, h = crop
    if x is not None:
        media.crop_x = x
        media.crop_y = y
        media.crop_w = w
        media.crop_h = h
    return media
```

*Build a avMediaFile from the given column names and crop tuple.*

##### Parameters

- **header**: (*list*) List of column names.
- **row**: (*list*) List of cell values.
- **col_file**: (*str*) Column name for the file path.
- **col_clap**: (*str*) Column name for the clap time.
- **crop**: (*tuple*) (x, y, w, h) as int|None.
- **row_index**: (*int*) 1-based row number, used in error messages.


##### Returns

- (avMediaFile) Constructed avMediaFile instance.


##### Raises

- *ValueError*: A required cell is empty or invalid.

#### __build_session

```python
def __build_session(self, header: list, row: list, row_index: int) -> avSession:
    """Build a avSession from a parsed header and data row.

        :param header: (list) List of column names.
        :param row: (list) List of cell values.
        :param row_index: (int) 1-based row number, used in error messages.
        :return: (avSession) Constructed avSession instance.
        :raises: ValueError: Any required cell is empty or cannot be parsed.

        """
    audio_crop = (None, None, None, None)
    audio = self.__build_media_file(header, row, cfg.sync.col_audio_file, cfg.sync.col_audio_clap, audio_crop, row_index)
    video_crop = self.__build_crop(header, row, suffix='')
    video = self.__build_media_file(header, row, cfg.sync.col_video_file, cfg.sync.col_video_clap, video_crop, row_index)
    delay_raw = self.__get_cell(header, row, cfg.sync.col_delay)
    duration_raw = self.__get_cell(header, row, cfg.sync.col_duration)
    try:
        delay = float(delay_raw) if len(delay_raw) > 0 else 0.0
    except ValueError:
        raise ValueError(f'Row {row_index}: invalid delay value {delay_raw!r}.')
    try:
        duration = time_to_seconds(duration_raw)
    except ValueError as e:
        raise ValueError(f'Row {row_index}: invalid duration in column {cfg.sync.col_duration!r}. {e}.')
    session = avSession(audio, video, delay=delay, duration=duration)
    video_name_raw = self.__get_cell(header, row, cfg.sync.col_video_name)
    if len(video_name_raw) > 0:
        session.set_video_name(0, video_name_raw)
    i = 2
    while True:
        col_file = cfg.sync.col_audio_file + str(i)
        if col_file not in header:
            break
        audio_raw = self.__get_cell(header, row, col_file)
        if len(audio_raw) > 0:
            audio_n = self.__build_media_file(header, row, col_file, cfg.sync.col_audio_clap + str(i), (None, None, None, None), row_index)
            session.add_audio(audio_n)
        i += 1
    i = 2
    while True:
        col_file = cfg.sync.col_video_file + str(i)
        if col_file not in header:
            break
        video_raw = self.__get_cell(header, row, col_file)
        if len(video_raw) > 0:
            video_crop = self.__build_crop(header, row, suffix=str(i))
            video_n = self.__build_media_file(header, row, col_file, cfg.sync.col_video_clap + str(i), video_crop, row_index)
            name_raw = self.__get_cell(header, row, cfg.sync.col_video_name + str(i))
            session.add_video(video_n, name=name_raw if len(name_raw) > 0 else None)
        i += 1
    sync_cols = {cfg.sync.col_audio_file, cfg.sync.col_audio_clap, cfg.sync.col_video_file, cfg.sync.col_video_clap, cfg.sync.col_video_name, cfg.sync.col_video_crop_x, cfg.sync.col_video_crop_y, cfg.sync.col_video_crop_w, cfg.sync.col_video_crop_h, cfg.sync.col_delay, cfg.sync.col_duration}
    for j in range(2, 20):
        suffix = str(j)
        sync_cols.add(cfg.sync.col_audio_file + suffix)
        sync_cols.add(cfg.sync.col_audio_clap + suffix)
        sync_cols.add(cfg.sync.col_video_file + suffix)
        sync_cols.add(cfg.sync.col_video_clap + suffix)
        sync_cols.add(cfg.sync.col_video_name + suffix)
        sync_cols.add(cfg.sync.col_video_crop_x + suffix)
        sync_cols.add(cfg.sync.col_video_crop_y + suffix)
        sync_cols.add(cfg.sync.col_video_crop_w + suffix)
        sync_cols.add(cfg.sync.col_video_crop_h + suffix)
    name_col_names = {entry[0] for entry in cfg.output.output_name_cols}
    output_name_meta = {}
    for col_name in name_col_names:
        value = self.__get_cell(header, row, col_name)
        if len(value) > 0:
            output_name_meta[col_name] = value
    session.output_name_meta = output_name_meta
    metadata = {}
    for col_name in header:
        if col_name in sync_cols:
            continue
        if col_name in name_col_names:
            continue
        value = self.__get_cell(header, row, col_name)
        if len(value) > 0:
            metadata[col_name] = value
    session.metadata = metadata
    return session
```

*Build a avSession from a parsed header and data row.*

##### Parameters

- **header**: (*list*) List of column names.
- **row**: (*list*) List of cell values.
- **row_index**: (*int*) 1-based row number, used in error messages.


##### Returns

- (avSession) Constructed avSession instance.


##### Raises

- *ValueError*: Any required cell is empty or cannot be parsed.



## Class `avExporter`

### Description

*Apply optional post-pipeline export operations to a avSyncResult.*

An avExporter is created from a avSyncResult. Each export method adds new
output files and appends messages to the result report.

##### Example

    >>> exporter = avExporter(result, stem="Laurent_S09_sent", work_dir="/out/Laurent_S09_sent")
    >>> exporter.to_sppas()
    >>> exporter.rotate(transpose=2)
    >>> exporter.montage()


### Constructor

#### __init__

```python
def __init__(self, result: avSyncResult, stem: str, work_dir: str):
    """Initialize the avExporter with a avSyncResult and output paths.

    :param result: (avSyncResult) Result produced by avPipeline.run().
    :param stem: (str) Output filename stem (e.g. "Laurent_S09_sent").
    :param work_dir: (str) Working directory containing the synced files.
    :raises: TypeError: result is not a avSyncResult instance.
    :raises: TypeError: stem or work_dir is not a non-empty string.
    :raises: ValueError: result.success is False.

    """
    if isinstance(result, avSyncResult) is False:
        raise TypeError('result must be a avSyncResult instance.')
    if isinstance(stem, str) is False or len(stem.strip()) == 0:
        raise TypeError('stem must be a non-empty string.')
    if isinstance(work_dir, str) is False or len(work_dir.strip()) == 0:
        raise TypeError('work_dir must be a non-empty string.')
    if result.success is False:
        raise ValueError('The given avSyncResult reports a failed pipeline run. Export operations cannot be applied to a failed result.')
    self.__result = result
    self.__stem = stem.strip()
    self.__work_dir = work_dir.strip()
```

*Initialize the avExporter with a avSyncResult and output paths.*

##### Parameters

- **result**: (avSyncResult) Result produced by avPipeline.run().
- **stem**: (*str*) Output filename stem (e.g. "Laurent_S09_sent").
- **work_dir**: (*str*) Working directory containing the synced files.


##### Raises

- *TypeError*: result is not a avSyncResult instance.
- *TypeError*: stem or work_dir is not a non-empty string.
- *ValueError*: result.success is False.



### Public functions

#### rotate

```python
def rotate(self, transpose_list: list) -> None:
    """Rotate synchronized video files using per-video transpose values.

        Each element of transpose_list corresponds to one video in order
        (primary first, secondary second, etc.). Use None to skip a video.

        Transpose values:
            0 = 90° counter-clockwise + vertical flip
            1 = 90° clockwise
            2 = 90° counter-clockwise  (portrait mode)
            3 = 90° clockwise + vertical flip

        The rotated file replaces the input MKV in the working directory.

        :param transpose_list: (list) List of int|None values, one per video.
        :raises: TypeError: transpose_list is not a list, or a value is not int|None.
        :raises: ValueError: A value is not in [0, 3].

        """
    if isinstance(transpose_list, list) is False:
        raise TypeError('transpose_list must be a list.')
    for i, value in enumerate(transpose_list):
        avExporter.__check_transpose_value(i, value)
    self.__result.add_message(f'Export: rotate {transpose_list}.')
    videos = self.__all_synced_videos()
    for i, t in enumerate(transpose_list):
        if t is None:
            continue
        if i >= len(videos):
            continue
        video_path = videos[i]
        if os.path.isfile(video_path) is False:
            continue
        tmp_path = video_path.replace('.mkv', '_tmp_rot.mkv')
        avVideoOps.rotate(video_path, tmp_path, t)
        os.remove(video_path)
        os.rename(tmp_path, video_path)
        self.__result.add_message(f'  Rotated: {video_path!r}')
```

*Rotate synchronized video files using per-video transpose values.*

Each element of transpose_list corresponds to one video in order
(primary first, secondary second, etc.). Use None to skip a video.

Transpose values:
0 = 90° counter-clockwise + vertical flip
1 = 90° clockwise
2 = 90° counter-clockwise  (portrait mode)
3 = 90° clockwise + vertical flip

The rotated file replaces the input MKV in the working directory.

##### Parameters

- **transpose_list**: (*list*) List of int|None values, one per video.


##### Raises

- *TypeError*: transpose_list is not a list, or a value is not int|None.
- *ValueError*: A value is not in [0, 3].

#### montage

```python
def montage(self, fps: int=None, crf: int=None) -> str:
    """Assemble synchronized video(s) and audio(s) into a compressed MP4.

        Video codec  : libx264, preset slow, profile main, yuv420p.
        Audio codec  : AAC.
        Frame rate   : MONTAGE_FPS (default 25) or the given fps value.
        CRF          : MONTAGE_CRF (default 18) or the given crf value.

        Behavior by media count:

        Videos:
            1 video  : encoded directly.
            2 videos : assembled side by side (hstack), scaled to the same
                       height as the primary video; black bars if needed.
            3+ videos: not supported — raises NotImplementedError.

        Audios:
            0 or 3+ audios: no audio track in the output. A warning is logged
                            when 3+ files are present (limitation, not an error).
            1 audio : mono, original sample rate.
            2 audios: stereo 48 kHz (audio1 = left channel, audio2 = right
                      channel), merged with amerge and resampled to 48000 Hz.

        :param fps: (int|None) Output frame rate. Uses MONTAGE_FPS if None.
        :param crf: (int|None) CRF quality value. Uses MONTAGE_CRF if None.
        :return: (str) Path to the produced MP4 file.
        :raises: TypeError: fps or crf is not an integer or None.
        :raises: ValueError: fps or crf is out of valid range.
        :raises: FileNotFoundError: No MKV file is found in the result.
        :raises: NotImplementedError: More than 2 synchronized videos.

        """
    avExporter.__check_montage_params(fps, crf)
    effective_fps = fps if fps is not None else avExporter.MONTAGE_FPS
    effective_crf = crf if crf is not None else avExporter.MONTAGE_CRF
    audios = self.__all_synced_audios()
    videos = self.__all_synced_videos()
    n_v = len(videos)
    n_a = len(audios)
    if n_v == 0:
        raise FileNotFoundError(f'No MKV file found in avSyncResult for stem {self.__stem!r}.')
    if n_v >= 3:
        raise NotImplementedError(f'Montage with {n_v} videos is not yet supported. Maximum: 2 videos.')
    for v in videos:
        check_file(v)
    if n_a > 2:
        self.__result.add_message(f'  Warning: montage supports at most 2 audio files. Got {n_a} — no audio track in the montage output.')
        n_a = 0
    for a in audios[:n_a]:
        check_file(a)
    mp4_out = self.__path(self.__stem + '-av.mp4')
    self.__result.add_message(f'Export: montage ({n_v} video(s), {n_a} audio(s), fps={effective_fps}, crf={effective_crf}).')
    command = self.__montage_command(videos, audios[:n_a], mp4_out, effective_fps, effective_crf)
    from aviss.utils import run_command
    run_command(command)
    check_file(mp4_out)
    self.__result.montage_file = mp4_out
    self.__result.add_message(f'  Montage: {mp4_out!r}')
    return mp4_out
```

*Assemble synchronized video(s) and audio(s) into a compressed MP4.*

Video codec  : libx264, preset slow, profile main, yuv420p.
Audio codec  : AAC.
Frame rate   : MONTAGE_FPS (default 25) or the given fps value.
CRF          : MONTAGE_CRF (default 18) or the given crf value.

Behavior by media count:

Videos:
1 video  : encoded directly.
2 videos : assembled side by side (hstack), scaled to the same
height as the primary video; black bars if needed.
3+ videos: not supported — raises NotImplementedError.

Audios:
0 or 3+ audios: no audio track in the output. A warning is logged
when 3+ files are present (limitation, not an error).
1 audio : mono, original sample rate.
2 audios: stereo 48 kHz (audio1 = left channel, audio2 = right
channel), merged with amerge and resampled to 48000 Hz.

##### Parameters

- **fps**: (*int*|None) Output frame rate. Uses MONTAGE_FPS if None.
- **crf**: (*int*|None) CRF quality value. Uses MONTAGE_CRF if None.


##### Returns

- (*str*) Path to the produced MP4 file.


##### Raises

- *TypeError*: fps or crf is not an integer or None.
- *ValueError*: fps or crf is out of valid range.
- *FileNotFoundError*: No MKV file is found in the result.
- *NotImplementedError*: More than 2 synchronized videos.

#### webm

```python
def webm(self, crf: int=16) -> str:
    """Convert the primary synchronized video to WebM using libvpx-vp9.

        The primary synchronized audio is muxed into the WebM container.
        Two-pass encoding is used for better quality at the given CRF.

        :param crf: (int) CRF quality value for libvpx-vp9 in [0, 63].
                    Lower is better. Defaults to 16.
        :return: (str) Path to the produced WebM file.
        :raises: TypeError: crf is not an integer.
        :raises: ValueError: crf is not in range [0, 63].
        :raises: FileNotFoundError: Primary audio or video is not available.

        """
    if isinstance(crf, int) is False:
        raise TypeError('crf must be an integer.')
    if crf < 0 or crf > 63:
        raise ValueError('crf must be in range [0, 63].')
    self.__result.add_message(f'Export: webm (crf={crf}).')
    audio_in = self.__primary_audio()
    video_in = self.__primary_video()
    webm_out = self.__path(self.__stem + '-av.webm')
    check_file(audio_in)
    check_file(video_in)
    avVideoOps.to_webm(video_in, webm_out, audio_in=audio_in, crf=crf)
    check_file(webm_out)
    if self.__result.montage_file is None:
        self.__result.montage_file = webm_out
    self.__result.add_message(f'  WebM: {webm_out!r}')
    return webm_out
```

*Convert the primary synchronized video to WebM using libvpx-vp9.*

The primary synchronized audio is muxed into the WebM container.
Two-pass encoding is used for better quality at the given CRF.

##### Parameters

- **crf**: (*int*) CRF quality value for libvpx-vp9 in [0, 63]. Lower is better. Defaults to 16.


##### Returns

- (*str*) Path to the produced WebM file.


##### Raises

- *TypeError*: crf is not an integer.
- *ValueError*: crf is not in range [0, 63].
- *FileNotFoundError*: Primary audio or video is not available.



### Protected functions

#### __path

```python
def __path(self, filename: str) -> str:
    """Return the full path for a file in the working directory.

        :param filename: (str) Filename (not path).
        :return: (str) Full path.

        """
    return os.path.join(self.__work_dir, filename)
```

*Return the full path for a file in the working directory.*

##### Parameters

- **filename**: (*str*) Filename (not path).


##### Returns

- (*str*) Full path.

#### __all_synced_audios

```python
def __all_synced_audios(self) -> list:
    """Return all full-quality audio files for this stem, in session order.

        Full-quality files are named <stem>*-audio.wav (original sample rate
        and channel count, before the 16 kHz mono conversion).

        :return: (list) Sorted list of paths to -audio.wav files.

        """
    return sorted([f for f in self.__result.synced_files if os.path.basename(f).startswith(self.__stem) and f.endswith('-audio.wav')])
```

*Return all full-quality audio files for this stem, in session order.*

Full-quality files are named <stem>*-audio.wav (original sample rate
and channel count, before the 16 kHz mono conversion).

##### Returns

- (*list*) Sorted list of paths to -audio.wav files.

#### __all_synced_videos

```python
def __all_synced_videos(self) -> list:
    """Return all synchronized MKV files for this stem, in session order.

        :return: (list) Sorted list of paths to .mkv files.

        """
    return sorted([f for f in self.__result.synced_files if os.path.basename(f).startswith(self.__stem) and f.endswith('.mkv')])
```

*Return all synchronized MKV files for this stem, in session order.*

##### Returns

- (*list*) Sorted list of paths to .mkv files.

#### __primary_audio

```python
def __primary_audio(self) -> str:
    """Return the path of the primary full-quality audio file.

        Prefers the -audio.wav file (original sample rate and channels).
        Falls back to .wav if no -audio.wav is found.

        :return: (str) Path to the primary WAV file.
        :raises: FileNotFoundError: No matching WAV file is found in the result.

        """
    candidates = self.__all_synced_audios()
    if len(candidates) == 0:
        candidates = [f for f in self.__result.synced_files if os.path.basename(f).startswith(self.__stem) and f.endswith('.wav')]
    if len(candidates) == 0:
        raise FileNotFoundError(f'No primary WAV file found in avSyncResult for stem {self.__stem!r}.')
    return candidates[0]
```

*Return the path of the primary full-quality audio file.*

Prefers the -audio.wav file (original sample rate and channels).
Falls back to .wav if no -audio.wav is found.

##### Returns

- (*str*) Path to the primary WAV file.


##### Raises

- *FileNotFoundError*: No matching WAV file is found in the result.

#### __primary_video

```python
def __primary_video(self) -> str:
    """Return the path of the primary synchronized video file.

        :return: (str) Path to the primary MKV file.
        :raises: FileNotFoundError: No matching MKV file is found in the result.

        """
    candidates = self.__all_synced_videos()
    if len(candidates) == 0:
        raise FileNotFoundError(f'No primary MKV file found in avSyncResult for stem {self.__stem!r}.')
    return candidates[0]
```

*Return the path of the primary synchronized video file.*

##### Returns

- (*str*) Path to the primary MKV file.


##### Raises

- *FileNotFoundError*: No matching MKV file is found in the result.

#### __check_transpose_value

```python
@staticmethod
def __check_transpose_value(index: int, value) -> None:
    """Raise if a single transpose value is invalid.

        :param index: (int) Position in the transpose_list (for error messages).
        :param value: (int|None) Transpose value to validate.
        :raises: TypeError: value is not an integer or None.
        :raises: ValueError: value is not in [0, 3].

        """
    if value is None:
        return
    if isinstance(value, int) is False:
        raise TypeError(f'transpose_list[{index}] must be an integer or None.')
    if value < 0 or value > 3:
        raise ValueError(f'transpose_list[{index}] must be in [0, 3].')
```

*Raise if a single transpose value is invalid.*

##### Parameters

- **index**: (*int*) Position in the transpose_list (for error messages).
- **value**: (*int*|None) Transpose value to validate.


##### Raises

- *TypeError*: value is not an integer or None.
- *ValueError*: value is not in [0, 3].

#### __check_montage_params

```python
@staticmethod
def __check_montage_params(fps, crf) -> None:
    """Raise if fps or crf arguments are invalid.

        :param fps: (int|None) Frame rate to validate.
        :param crf: (int|None) CRF value to validate.
        :raises: TypeError: fps or crf is not an integer or None.
        :raises: ValueError: fps or crf is out of valid range.

        """
    if fps is not None:
        if isinstance(fps, int) is False:
            raise TypeError('fps must be an integer or None.')
        if fps <= 0:
            raise ValueError('fps must be strictly positive.')
    if crf is not None:
        if isinstance(crf, int) is False:
            raise TypeError('crf must be an integer or None.')
        if crf < 0 or crf > 51:
            raise ValueError('crf must be in range [0, 51].')
```

*Raise if fps or crf arguments are invalid.*

##### Parameters

- **fps**: (*int*|None) Frame rate to validate.
- **crf**: (*int*|None) CRF value to validate.


##### Raises

- *TypeError*: fps or crf is not an integer or None.
- *ValueError*: fps or crf is out of valid range.

#### __montage_command

```python
def __montage_command(self, videos: list, audios: list, mp4_out: str, fps: int, crf: int) -> str:
    """Build the ffmpeg command for the montage.

        :param videos: (list) List of 1 or 2 MKV paths (already validated).
        :param audios: (list) List of 0, 1, or 2 WAV paths (already validated).
        :param mp4_out: (str) Output MP4 path.
        :param fps: (int) Output frame rate.
        :param crf: (int) CRF quality value.
        :return: (str) Full ffmpeg command string.

        """
    n_v = len(videos)
    n_a = len(audios)
    codec = f'-f mp4 -vcodec libx264 -crf {crf:d} -preset slow -profile:v main -pix_fmt yuv420p'
    if n_v == 1:
        v = videos[0]
        if n_a == 0:
            return f"ffmpeg -i '{v}' -filter:v fps=fps={fps:d} {codec} -an '{mp4_out}' -hide_banner -nostdin -y"
        if n_a == 1:
            return f"ffmpeg -i '{v}' -i '{audios[0]}' -filter:v fps=fps={fps:d} {codec} -c:a aac -strict -2 '{mp4_out}' -hide_banner -nostdin -y"
        fc = f'[0:v]fps=fps={fps:d}[vout];[1:a][2:a]amerge=inputs=2,aresample=48000[aout]'
        return f"""ffmpeg -i '{v}' -i '{audios[0]}' -i '{audios[1]}' -filter_complex "{fc}" -map "[vout]" -map "[aout]" {codec} -c:a aac -ac 2 -strict -2 '{mp4_out}' -hide_banner -nostdin -y"""
    h = avVideoOps.get_video_info(videos[0])['height']
    v0_f = f'[0:v]fps=fps={fps:d},scale=-2:{h}[v0]'
    v1_f = f'[1:v]fps=fps={fps:d},scale=-2:{h}[v1]'
    hstack = '[v0][v1]hstack=inputs=2[vout]'
    iv = f"-i '{videos[0]}' -i '{videos[1]}' "
    if n_a == 0:
        fc = f'{v0_f};{v1_f};{hstack}'
        return f"""ffmpeg {iv}-filter_complex "{fc}" -map "[vout]" {codec} -an '{mp4_out}' -hide_banner -nostdin -y"""
    if n_a == 1:
        fc = f'{v0_f};{v1_f};{hstack}'
        return f"""ffmpeg {iv}-i '{audios[0]}' -filter_complex "{fc}" -map "[vout]" -map 2:a {codec} -c:a aac -strict -2 '{mp4_out}' -hide_banner -nostdin -y"""
    fc = f'{v0_f};{v1_f};{hstack};[2:a][3:a]amerge=inputs=2,aresample=48000[aout]'
    return f"""ffmpeg {iv}-i '{audios[0]}' -i '{audios[1]}' -filter_complex "{fc}" -map "[vout]" -map "[aout]" {codec} -c:a aac -ac 2 -strict -2 '{mp4_out}' -hide_banner -nostdin -y"""
```

*Build the ffmpeg command for the montage.*

##### Parameters

- **videos**: (*list*) List of 1 or 2 MKV paths (already validated).
- **audios**: (*list*) List of 0, 1, or 2 WAV paths (already validated).
- **mp4_out**: (*str*) Output MP4 path.
- **fps**: (*int*) Output frame rate.
- **crf**: (*int*) CRF quality value.


##### Returns

- (*str*) Full ffmpeg command string.





~ Created using [Clamming](https://clamming.sf.net) version 2.3 ~
