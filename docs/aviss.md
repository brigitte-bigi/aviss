# aviss module

## List of classes

## Class `avMediaFile`

### Description

*Represent a single media file (audio or video) with sync parameters.*

A avMediaFile stores the path to the original file and the time of the
synchronization clap within that file. For video files, an optional
crop region (x, y, w, h) can be specified in pixels; if any of the
four values is None, no crop is applied.

##### Example

    >>> m = avMediaFile("/data/rec.wav", 3.843)
    >>> m.path
    > '/data/rec.wav'
    >>> m.clap_time
    > 3.843
    >>> m.is_audio()
    > True
    >>> m.has_crop()
    > False


### Constructor

#### __init__

```python
def __init__(self, path: str, clap_time: float):
    """Initialize a avMediaFile with a file path and a clap time.

    :param path: (str) Absolute or relative path to the media file.
    :param clap_time: (float) Time of the synchronization clap (seconds).
    :raises: TypeError: path is not a non-empty string.
    :raises: TypeError: clap_time is not a number.
    :raises: ValueError: clap_time is negative.

    """
    if isinstance(path, str) is False or len(path.strip()) == 0:
        raise TypeError('path must be a non-empty string.')
    if isinstance(clap_time, (int, float)) is False:
        raise TypeError('clap_time must be a number.')
    if float(clap_time) < 0.0:
        raise ValueError('clap_time must be zero or positive.')
    self.__path = path.strip()
    self.__clap_time = float(clap_time)
    self.__crop_x = None
    self.__crop_y = None
    self.__crop_w = None
    self.__crop_h = None
```

*Initialize a avMediaFile with a file path and a clap time.*

##### Parameters

- **path**: (*str*) Absolute or relative path to the media file.
- **clap_time**: (*float*) Time of the synchronization clap (seconds).


##### Raises

- *TypeError*: path is not a non-empty string.
- *TypeError*: clap_time is not a number.
- *ValueError*: clap_time is negative.



### Public functions

#### get_path

```python
def get_path(self) -> str:
    """Return the path to the media file.

        :return: (str) File path.

        """
    return self.__path
```

*Return the path to the media file.*

##### Returns

- (*str*) File path.

#### set_path

```python
def set_path(self, value: str) -> None:
    """Set the path to the media file.

        :param value: (str) Absolute or relative path to the media file.
        :raises: TypeError: The given value is not a non-empty string.

        """
    if isinstance(value, str) is False or len(value.strip()) == 0:
        raise TypeError('path must be a non-empty string.')
    self.__path = value.strip()
```

*Set the path to the media file.*

##### Parameters

- **value**: (*str*) Absolute or relative path to the media file.


##### Raises

- *TypeError*: The given value is not a non-empty string.

#### get_clap_time

```python
def get_clap_time(self) -> float:
    """Return the time of the synchronization clap (seconds).

        :return: (float) Clap time in seconds.

        """
    return self.__clap_time
```

*Return the time of the synchronization clap (seconds).*

##### Returns

- (*float*) Clap time in seconds.

#### set_clap_time

```python
def set_clap_time(self, value) -> None:
    """Set the time of the synchronization clap.

        :param value: (int|float) Clap time in seconds.
        :raises: TypeError: The given value is not a number.
        :raises: ValueError: The given value is negative.

        """
    if isinstance(value, (int, float)) is False:
        raise TypeError('clap_time must be a number.')
    if float(value) < 0.0:
        raise ValueError('clap_time must be zero or positive.')
    self.__clap_time = float(value)
```

*Set the time of the synchronization clap.*

##### Parameters

- **value**: (*int*|*float*) Clap time in seconds.


##### Raises

- *TypeError*: The given value is not a number.
- *ValueError*: The given value is negative.

#### get_crop_x

```python
def get_crop_x(self) -> int | None:
    """Return the left edge of the crop region in pixels, or None.

        :return: (int|None) Left edge in pixels, or None if not set.

        """
    return self.__crop_x
```

*Return the left edge of the crop region in pixels, or None.*

##### Returns

- (*int*|None) Left edge in pixels, or None if not set.

#### set_crop_x

```python
def set_crop_x(self, value: int | None) -> None:
    """Set the left edge of the crop region in pixels.

        :param value: (int|None) Left edge in pixels, or None to unset.
        :raises: TypeError: The given value is not an integer or None.
        :raises: ValueError: The given value is negative.

        """
    if value is not None:
        if isinstance(value, int) is False:
            raise TypeError('crop_x must be an integer or None.')
        if value < 0:
            raise ValueError('crop_x must be zero or positive.')
    self.__crop_x = value
```

*Set the left edge of the crop region in pixels.*

##### Parameters

- **value**: (*int*|None) Left edge in pixels, or None to unset.


##### Raises

- *TypeError*: The given value is not an integer or None.
- *ValueError*: The given value is negative.

#### get_crop_y

```python
def get_crop_y(self) -> int | None:
    """Return the top edge of the crop region in pixels, or None.

        :return: (int|None) Top edge in pixels, or None if not set.

        """
    return self.__crop_y
```

*Return the top edge of the crop region in pixels, or None.*

##### Returns

- (*int*|None) Top edge in pixels, or None if not set.

#### set_crop_y

```python
def set_crop_y(self, value: int | None) -> None:
    """Set the top edge of the crop region in pixels.

        :param value: (int|None) Top edge in pixels, or None to unset.
        :raises: TypeError: The given value is not an integer or None.
        :raises: ValueError: The given value is negative.

        """
    if value is not None:
        if isinstance(value, int) is False:
            raise TypeError('crop_y must be an integer or None.')
        if value < 0:
            raise ValueError('crop_y must be zero or positive.')
    self.__crop_y = value
```

*Set the top edge of the crop region in pixels.*

##### Parameters

- **value**: (*int*|None) Top edge in pixels, or None to unset.


##### Raises

- *TypeError*: The given value is not an integer or None.
- *ValueError*: The given value is negative.

#### get_crop_w

```python
def get_crop_w(self) -> int | None:
    """Return the width of the crop region in pixels, or None.

        :return: (int|None) Width in pixels, or None if not set.

        """
    return self.__crop_w
```

*Return the width of the crop region in pixels, or None.*

##### Returns

- (*int*|None) Width in pixels, or None if not set.

#### set_crop_w

```python
def set_crop_w(self, value: int | None) -> None:
    """Set the width of the crop region in pixels.

        :param value: (int|None) Width in pixels, or None to unset.
        :raises: TypeError: The given value is not an integer or None.
        :raises: ValueError: The given value is not strictly positive.

        """
    if value is not None:
        if isinstance(value, int) is False:
            raise TypeError('crop_w must be an integer or None.')
        if value <= 0:
            raise ValueError('crop_w must be strictly positive.')
    self.__crop_w = value
```

*Set the width of the crop region in pixels.*

##### Parameters

- **value**: (*int*|None) Width in pixels, or None to unset.


##### Raises

- *TypeError*: The given value is not an integer or None.
- *ValueError*: The given value is not strictly positive.

#### get_crop_h

```python
def get_crop_h(self) -> int | None:
    """Return the height of the crop region in pixels, or None.

        :return: (int|None) Height in pixels, or None if not set.

        """
    return self.__crop_h
```

*Return the height of the crop region in pixels, or None.*

##### Returns

- (*int*|None) Height in pixels, or None if not set.

#### set_crop_h

```python
def set_crop_h(self, value: int | None) -> None:
    """Set the height of the crop region in pixels.

        :param value: (int|None) Height in pixels, or None to unset.
        :raises: TypeError: The given value is not an integer or None.
        :raises: ValueError: The given value is not strictly positive.

        """
    if value is not None:
        if isinstance(value, int) is False:
            raise TypeError('crop_h must be an integer or None.')
        if value <= 0:
            raise ValueError('crop_h must be strictly positive.')
    self.__crop_h = value
```

*Set the height of the crop region in pixels.*

##### Parameters

- **value**: (*int*|None) Height in pixels, or None to unset.


##### Raises

- *TypeError*: The given value is not an integer or None.
- *ValueError*: The given value is not strictly positive.

#### is_audio

```python
def is_audio(self) -> bool:
    """Return True if this file is an audio file.

        :return: (bool) True if the file extension is a known audio extension.

        """
    ext = os.path.splitext(self.__path)[-1].lower()
    return ext in audio_extensions
```

*Return True if this file is an audio file.*

##### Returns

- (*bool*) True if the file extension is a known audio extension.

#### is_video

```python
def is_video(self) -> bool:
    """Return True if this file is a video file.

        :return: (bool) True if the file extension is not a known audio extension.

        """
    return self.is_audio() is False
```

*Return True if this file is a video file.*

##### Returns

- (*bool*) True if the file extension is not a known audio extension.

#### has_crop

```python
def has_crop(self) -> bool:
    """Return True if all four crop parameters are set.

        Crop is applied only when all four values (x, y, w, h) are defined.

        :return: (bool) True if crop_x, crop_y, crop_w and crop_h are all set.

        """
    return self.__crop_x is not None and self.__crop_y is not None and (self.__crop_w is not None) and (self.__crop_h is not None)
```

*Return True if all four crop parameters are set.*

Crop is applied only when all four values (x, y, w, h) are defined.

##### Returns

- (*bool*) True if crop_x, crop_y, crop_w and crop_h are all set.

#### exists

```python
def exists(self) -> bool:
    """Return True if the media file exists on disk.

        :return: (bool) True if the path points to an existing file.

        """
    return os.path.isfile(self.__path)
```

*Return True if the media file exists on disk.*

##### Returns

- (*bool*) True if the path points to an existing file.



### Overloads

#### __repr__

```python
def __repr__(self) -> str:
    crop = f' crop=({self.__crop_x},{self.__crop_y},{self.__crop_w},{self.__crop_h})' if self.has_crop() is True else ''
    return f'avMediaFile({self.__path!r}, clap={self.__clap_time:.3f}s{crop})'
```





## Class `avSession`

### Description

*Represent one row of the input CSV file.*

A avSession groups:
- one or more avMediaFile instances for audio,
- one or more avMediaFile instances for video,
- timing parameters (delay and duration),
- output filename metadata (values used to build the output name),
- free metadata (any other CSV column, stored as a dict).

At least one audio and one video must be provided.

##### Example

    >>> audio = avMediaFile("/data/rec.wav", 3.843)
    >>> video = avMediaFile("/data/rec.mp4", 6.410)
    >>> s = avSession(audio, video, delay=0.2, duration=248.25)
    >>> s.output_name_meta
    > {}
    >>> s.has_second_audio()
    > False


### Constructor

#### __init__

```python
def __init__(self, audio: avMediaFile, video: avMediaFile, delay: float, duration: float):
    """Initialize a avSession with its primary media files and timing.

    :param audio: (avMediaFile) Primary audio file.
    :param video: (avMediaFile) Primary video file.
    :param delay: (float) Offset applied after the clap (seconds).
    :param duration: (float) Expected output duration (seconds).
    :raises: TypeError: audio is not a avMediaFile instance.
    :raises: ValueError: audio is not an audio file.
    :raises: TypeError: video is not a avMediaFile instance.
    :raises: ValueError: video is not a video file.
    :raises: TypeError: delay is not a number.
    :raises: TypeError: duration is not a number.
    :raises: ValueError: duration is not strictly positive.

    """
    if isinstance(audio, avMediaFile) is False:
        raise TypeError('audio must be a avMediaFile instance.')
    if audio.is_audio() is False:
        raise ValueError(f'The given audio avMediaFile does not have an audio extension: {audio.path!r}.')
    if isinstance(video, avMediaFile) is False:
        raise TypeError('video must be a avMediaFile instance.')
    if video.is_video() is False:
        raise ValueError(f'The given video avMediaFile does not have a video extension: {video.path!r}.')
    if isinstance(delay, (int, float)) is False:
        raise TypeError('delay must be a number.')
    if isinstance(duration, (int, float)) is False:
        raise TypeError('duration must be a number.')
    if float(duration) <= 0.0:
        raise ValueError('duration must be strictly positive.')
    self.__audios = [audio]
    self.__videos = [video]
    self.__video_names = [None]
    self.__delay = float(delay)
    self.__duration = float(duration)
    self.__output_name_meta = {}
    self.__metadata = {}
```

*Initialize a avSession with its primary media files and timing.*

##### Parameters

- **audio**: (avMediaFile) Primary audio file.
- **video**: (avMediaFile) Primary video file.
- **delay**: (*float*) Offset applied after the clap (seconds).
- **duration**: (*float*) Expected output duration (seconds).


##### Raises

- *TypeError*: audio is not a avMediaFile instance.
- *ValueError*: audio is not an audio file.
- *TypeError*: video is not a avMediaFile instance.
- *ValueError*: video is not a video file.
- *TypeError*: delay is not a number.
- *TypeError*: duration is not a number.
- *ValueError*: duration is not strictly positive.



### Public functions

#### get_audios

```python
def get_audios(self) -> list:
    """Return a copy of the list of audio avMediaFile objects.

        :return: (list) List of avMediaFile instances (audio).

        """
    return list(self.__audios)
```

*Return a copy of the list of audio avMediaFile objects.*

##### Returns

- (*list*) List of avMediaFile instances (audio).

#### get_videos

```python
def get_videos(self) -> list:
    """Return a copy of the list of video avMediaFile objects.

        :return: (list) List of avMediaFile instances (video).

        """
    return list(self.__videos)
```

*Return a copy of the list of video avMediaFile objects.*

##### Returns

- (*list*) List of avMediaFile instances (video).

#### get_video_names

```python
def get_video_names(self) -> list:
    """Return a copy of the list of optional video output labels.

        Each element corresponds to the video at the same index.
        None means no label is set for that video.

        :return: (list) List of str|None values.

        """
    return list(self.__video_names)
```

*Return a copy of the list of optional video output labels.*

Each element corresponds to the video at the same index.
None means no label is set for that video.

##### Returns

- (*list*) List of str|None values.

#### add_audio

```python
def add_audio(self, audio: avMediaFile) -> None:
    """Append an audio avMediaFile to the session.

        :param audio: (avMediaFile) Audio file to add.
        :raises: TypeError: audio is not a avMediaFile instance.
        :raises: ValueError: audio is not an audio file.

        """
    if isinstance(audio, avMediaFile) is False:
        raise TypeError('audio must be a avMediaFile instance.')
    if audio.is_audio() is False:
        raise ValueError(f'The given avMediaFile does not have an audio extension: {audio.path!r}.')
    self.__audios.append(audio)
```

*Append an audio avMediaFile to the session.*

##### Parameters

- **audio**: (avMediaFile) Audio file to add.


##### Raises

- *TypeError*: audio is not a avMediaFile instance.
- *ValueError*: audio is not an audio file.

#### add_video

```python
def add_video(self, video: avMediaFile, name: str | None=None) -> None:
    """Append a video avMediaFile to the session with an optional output label.

        :param video: (avMediaFile) Video file to add.
        :param name: (str|None) Optional label used as suffix in the output filename.
        :raises: TypeError: video is not a avMediaFile instance.
        :raises: ValueError: video is not a video file.
        :raises: TypeError: name is not a non-empty string or None.

        """
    if isinstance(video, avMediaFile) is False:
        raise TypeError('video must be a avMediaFile instance.')
    if video.is_video() is False:
        raise ValueError(f'The given avMediaFile does not have a video extension: {video.path!r}.')
    if name is not None:
        if isinstance(name, str) is False or len(name.strip()) == 0:
            raise TypeError('name must be a non-empty string or None.')
        name = name.strip()
    self.__videos.append(video)
    self.__video_names.append(name)
```

*Append a video avMediaFile to the session with an optional output label.*

##### Parameters

- **video**: (avMediaFile) Video file to add.
- **name**: (*str*|None) Optional label used as suffix in the output filename.


##### Raises

- *TypeError*: video is not a avMediaFile instance.
- *ValueError*: video is not a video file.
- *TypeError*: name is not a non-empty string or None.

#### set_video_name

```python
def set_video_name(self, index: int, name: str | None) -> None:
    """Set the output label for the video at the given index.

        :param index: (int) Index of the video (0-based).
        :param name: (str|None) Label, or None to clear.
        :raises: IndexError: index is out of range.
        :raises: TypeError: name is not a non-empty string or None.

        """
    if index < 0 or index >= len(self.__videos):
        raise IndexError(f'Video index {index} is out of range.')
    if name is not None:
        if isinstance(name, str) is False or len(name.strip()) == 0:
            raise TypeError('name must be a non-empty string or None.')
        name = name.strip()
    self.__video_names[index] = name
```

*Set the output label for the video at the given index.*

##### Parameters

- **index**: (*int*) Index of the video (0-based).
- **name**: (*str*|None) Label, or None to clear.


##### Raises

- *IndexError*: index is out of range.
- *TypeError*: name is not a non-empty string or None.

#### get_delay

```python
def get_delay(self) -> float:
    """Return the offset applied after the clap (seconds).

        :return: (float) Delay in seconds.

        """
    return self.__delay
```

*Return the offset applied after the clap (seconds).*

##### Returns

- (*float*) Delay in seconds.

#### set_delay

```python
def set_delay(self, value) -> None:
    """Set the offset applied after the clap.

        :param value: (int|float) Delay in seconds.
        :raises: TypeError: The given value is not a number.

        """
    if isinstance(value, (int, float)) is False:
        raise TypeError('delay must be a number.')
    self.__delay = float(value)
```

*Set the offset applied after the clap.*

##### Parameters

- **value**: (*int*|*float*) Delay in seconds.


##### Raises

- *TypeError*: The given value is not a number.

#### get_duration

```python
def get_duration(self) -> float:
    """Return the expected output duration (seconds).

        :return: (float) Duration in seconds.

        """
    return self.__duration
```

*Return the expected output duration (seconds).*

##### Returns

- (*float*) Duration in seconds.

#### set_duration

```python
def set_duration(self, value) -> None:
    """Set the expected output duration.

        :param value: (int|float) Duration in seconds.
        :raises: TypeError: The given value is not a number.
        :raises: ValueError: The given value is not strictly positive.

        """
    if isinstance(value, (int, float)) is False:
        raise TypeError('duration must be a number.')
    if float(value) <= 0.0:
        raise ValueError('duration must be strictly positive.')
    self.__duration = float(value)
```

*Set the expected output duration.*

##### Parameters

- **value**: (*int*|*float*) Duration in seconds.


##### Raises

- *TypeError*: The given value is not a number.
- *ValueError*: The given value is not strictly positive.

#### get_output_name_meta

```python
def get_output_name_meta(self) -> dict:
    """Return the dict of values used to build the output filename.

        Keys are CSV column names as declared in cfg.output.output_name_cols.
        Values are raw strings read from the CSV.

        :return: (dict) Output name metadata.

        """
    return self.__output_name_meta
```

*Return the dict of values used to build the output filename.*

Keys are CSV column names as declared in cfg.output.output_name_cols.
Values are raw strings read from the CSV.

##### Returns

- (*dict*) Output name metadata.

#### set_output_name_meta

```python
def set_output_name_meta(self, value: dict) -> None:
    """Set the dict of values used to build the output filename.

        :param value: (dict) Mapping of column name to raw CSV value.
        :raises: TypeError: The given value is not a dict.

        """
    if isinstance(value, dict) is False:
        raise TypeError('output_name_meta must be a dict.')
    self.__output_name_meta = value
```

*Set the dict of values used to build the output filename.*

##### Parameters

- **value**: (*dict*) Mapping of column name to raw CSV value.


##### Raises

- *TypeError*: The given value is not a dict.

#### get_metadata

```python
def get_metadata(self) -> dict:
    """Return the dict of free metadata (all other CSV columns).

        :return: (dict) Free metadata.

        """
    return self.__metadata
```

*Return the dict of free metadata (all other CSV columns).*

##### Returns

- (*dict*) Free metadata.

#### set_metadata

```python
def set_metadata(self, value: dict) -> None:
    """Set the dict of free metadata.

        :param value: (dict) Mapping of column name to raw CSV value.
        :raises: TypeError: The given value is not a dict.

        """
    if isinstance(value, dict) is False:
        raise TypeError('metadata must be a dict.')
    self.__metadata = value
```

*Set the dict of free metadata.*

##### Parameters

- **value**: (*dict*) Mapping of column name to raw CSV value.


##### Raises

- *TypeError*: The given value is not a dict.

#### has_second_audio

```python
def has_second_audio(self) -> bool:
    """Return True if more than one audio file is set.

        :return: (bool) True if the session has at least two audio files.

        """
    return len(self.__audios) > 1
```

*Return True if more than one audio file is set.*

##### Returns

- (*bool*) True if the session has at least two audio files.

#### has_second_video

```python
def has_second_video(self) -> bool:
    """Return True if more than one video file is set.

        :return: (bool) True if the session has at least two video files.

        """
    return len(self.__videos) > 1
```

*Return True if more than one video file is set.*

##### Returns

- (*bool*) True if the session has at least two video files.

#### all_files_exist

```python
def all_files_exist(self) -> bool:
    """Return True if all media files in this session exist on disk.

        :return: (bool) True if every defined avMediaFile exists on disk.

        """
    for media in self.__audios + self.__videos:
        if media.exists() is False:
            return False
    return True
```

*Return True if all media files in this session exist on disk.*

##### Returns

- (*bool*) True if every defined avMediaFile exists on disk.



### Overloads

#### __repr__

```python
def __repr__(self) -> str:
    return f'avSession({len(self.__audios)} audio, {len(self.__videos)} video, delay={self.__delay:.3f}s, duration={self.__duration:.3f}s, meta={self.__output_name_meta})'
```





## Class `avSyncResult`

### Description

*Represent the output of a synchronization pipeline run.*

A avSyncResult is produced by the pipeline after processing one avSession.
It stores the paths of the files produced (synchronized media and
optional montage video) and a human-readable processing report.

##### Example

    >>> r = avSyncResult()
    >>> r.add_synced_file("/out/Laurent_S09_s2.wav")
    >>> r.add_synced_file("/out/Laurent_S09_s2.mp4")
    >>> len(r.synced_files)
    > 2
    >>> r.success
    > False
    >>> r.success = True
    >>> r.success
    > True


### Constructor

#### __init__

```python
def __init__(self):
    """Initialize an empty avSyncResult.

    """
    self.__synced_files = []
    self.__montage_file = None
    self.__success = False
    self.__report = []
```

*Initialize an empty avSyncResult.*





### Public functions

#### get_synced_files

```python
def get_synced_files(self) -> list:
    """Return the list of paths of synchronized output files.

        :return: (list) List of file path strings.

        """
    return self.__synced_files
```

*Return the list of paths of synchronized output files.*

##### Returns

- (*list*) List of file path strings.

#### add_synced_file

```python
def add_synced_file(self, path: str) -> None:
    """Append a synchronized output file path to the result.

        :param path: (str) Path to a produced synchronized file.
        :raises: TypeError: The given value is not a non-empty string.

        """
    if isinstance(path, str) is False or len(path.strip()) == 0:
        raise TypeError('path must be a non-empty string.')
    self.__synced_files.append(path.strip())
```

*Append a synchronized output file path to the result.*

##### Parameters

- **path**: (*str*) Path to a produced synchronized file.


##### Raises

- *TypeError*: The given value is not a non-empty string.

#### get_montage_file

```python
def get_montage_file(self) -> str | None:
    """Return the path to the optional montage video, or None.

        :return: (str|None) Montage file path, or None if not produced.

        """
    return self.__montage_file
```

*Return the path to the optional montage video, or None.*

##### Returns

- (*str*|None) Montage file path, or None if not produced.

#### set_montage_file

```python
def set_montage_file(self, value: str | None) -> None:
    """Set the path to the optional montage video.

        :param value: (str|None) Montage file path, or None.
        :raises: TypeError: The given value is not a non-empty string or None.

        """
    if value is not None:
        if isinstance(value, str) is False or len(value.strip()) == 0:
            raise TypeError('montage_file must be a non-empty string or None.')
    self.__montage_file = value
```

*Set the path to the optional montage video.*

##### Parameters

- **value**: (*str*|None) Montage file path, or None.


##### Raises

- *TypeError*: The given value is not a non-empty string or None.

#### get_success

```python
def get_success(self) -> bool:
    """Return True if the pipeline completed without error.

        :return: (bool) True if the synchronization succeeded.

        """
    return self.__success
```

*Return True if the pipeline completed without error.*

##### Returns

- (*bool*) True if the synchronization succeeded.

#### set_success

```python
def set_success(self, value: bool) -> None:
    """Set the success flag of this result.

        :param value: (bool) True if the pipeline completed without error.
        :raises: TypeError: The given value is not a boolean.

        """
    if isinstance(value, bool) is False:
        raise TypeError('success must be a boolean.')
    self.__success = value
```

*Set the success flag of this result.*

##### Parameters

- **value**: (*bool*) True if the pipeline completed without error.


##### Raises

- *TypeError*: The given value is not a boolean.

#### get_report

```python
def get_report(self) -> list:
    """Return the processing report as a list of message strings.

        :return: (list) List of report message strings.

        """
    return self.__report
```

*Return the processing report as a list of message strings.*

##### Returns

- (*list*) List of report message strings.

#### add_message

```python
def add_message(self, message: str) -> None:
    """Append a message to the processing report.

        :param message: (str) Message to append.
        :raises: TypeError: The given value is not a string.

        """
    if isinstance(message, str) is False:
        raise TypeError('message must be a string.')
    self.__report.append(message)
```

*Append a message to the processing report.*

##### Parameters

- **message**: (*str*) Message to append.


##### Raises

- *TypeError*: The given value is not a string.



### Overloads

#### __repr__

```python
def __repr__(self) -> str:
    status = 'OK' if self.__success is True else 'FAILED'
    n = len(self.__synced_files)
    montage = f', montage={self.__montage_file!r}' if self.__montage_file is not None else ''
    return f'avSyncResult({status}, {n} synced file(s){montage})'
```





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
    if self.__session.all_files_exist() is False:
        raise FileNotFoundError('One or more media files declared in the session do not exist on disk.')
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
        and channel count, before the 16 kHz mono conversion for SPPAS).

        :return: (list) Sorted list of paths to -audio.wav files.

        """
    return sorted([f for f in self.__result.synced_files if os.path.basename(f).startswith(self.__stem) and f.endswith('-audio.wav')])
```

*Return all full-quality audio files for this stem, in session order.*

Full-quality files are named <stem>*-audio.wav (original sample rate
and channel count, before the 16 kHz mono conversion for SPPAS).

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
