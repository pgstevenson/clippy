# Clippy

## Overview

Clippy is a Python script that is designed to crop a video file between a set of time codes, rip and save the audio track, and upload the mp3 to a podcast host via the host's API.

The cropped and ripped 'Episode' parameters are added to the 'clips.csv' file. Sensitive information that shouldn't be uploaded to GitHub are saved in the 'secrets.json' file as key-value pairs.

The script is designed to follow a ETL workflow. An overview of the methods that clippy supports and any method-specific parameters are found in the 'conf.json' file.

## Running Clippy

Clippy is run from the terminal and accepts a single argument '-i' '--input', which is the `id` for the clip as recorded in 'clips.csv' under the `id` column header, for example:

    python clippy.py -i 1

If the script is executed without the argument you will be prompted to enter an id number:

    python clippy.py

> Video clip id:

If an invalid id is entered into the terminal the script will exit with the message "ID not found. Exiting."

The script will make a new folder in the output directory (see "secrets.json") named with the clip `id`. If a folder with this name already exists you will be prompted with:

> Output directory '`id`' is not empty, continue [Enter 'y' for yes.]

To remove the existing `id` directory and all its contents enter 'y' and press Return, or just press return. Pressing any other key then Return will exit the script.

## clips.csv

The following table lists the parameters accepted by clippy that are included in 'clips.csv' as column headers:

+---------------+----------------------------------+------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Column Header | Brief Description                | Example          | Description                                                                                                                                                |
+:==============+:=================================+:=================+:===========================================================================================================================================================+
| id            | Clip ID                          | 1                | Clip ID will be used as the output directory and the name for the processed file(s). See 'secrets.json'.                                                   |
+---------------+----------------------------------+------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+
| t             | Transform method                 | 1                | See 'Transform - T' for list of methods.                                                                                                                   |
+---------------+----------------------------------+------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+
| l             | Load method                      | 1                | See 'Load - L' for list of methods.                                                                                                                        |
+---------------+----------------------------------+------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+
| filename      | Name of full/original video file | video.mp4        | See 'secrets.json' below.                                                                                                                                  |
+---------------+----------------------------------+------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+
| start_time    | Clip start time                  | 00:02:15         | Time index in HH:MM:SS format in the original video where the shortened clip should start.                                                                 |
+---------------+----------------------------------+------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+
| end_time      | Clip end time                    | 00:05:43         | Time index in HH:MM:SS format in the original video where the shortened clip should end.                                                                   |
+---------------+----------------------------------+------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+
| title         | Podcast title                    | My first podcast | Title that appears on the published podcast.                                                                                                               |
+---------------+----------------------------------+------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+
| content       | Podcast content text             | content.txt      | A .txt file containing the text content that is published along with the podcast on the host. See 'secrets.json'/assets below.                             |
+---------------+----------------------------------+------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+
| status        | Podcast status                   | publish          | Allowed values: "publish", "draft", "future".                                                                                                              |
+---------------+----------------------------------+------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+
| type          | Podcast access level             | public           | Allowed values: "public", "premium", "private".                                                                                                            |
+---------------+----------------------------------+------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+
| episode_logo  | Podcast episode logo             | test.jpeg        | Between 1400 and 3000 pixels square (jpg or png), maximum allowed single file size of 500 kB, at least 72 dpi. **Need to verify file size and dpi limit.** |
+---------------+----------------------------------+------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+

## secrets.json

The current configuration for the secrets is described as follows:

+-------+-------------------------+---------------------------------------------------------------------------------------------+
| Index | \| Example Value        | \| Description                                                                              |
+:======+:========================+:============================================================================================+
| 0     | ...\\\\clippy\\\\data_r | aw \| Path where full/original videos are saved.                                            |
+-------+-------------------------+---------------------------------------------------------------------------------------------+
| 1     | ...\\\\clippy\\\\data   | \| Output path for cropped/ripped media files.                                              |
+-------+-------------------------+---------------------------------------------------------------------------------------------+
| 2     | ...\\\\clippy\\\\assets | \| Path where podcast assets are saved. Files include episode logos and content .txt files. |
+-------+-------------------------+---------------------------------------------------------------------------------------------+
| 3     | XXXX                    | Podbean developer client ID.                                                                |
+-------+-------------------------+---------------------------------------------------------------------------------------------+
| 4     | XXXX                    | Podbean developer client secret.                                                            |
+-------+-------------------------+---------------------------------------------------------------------------------------------+

## Clippy methods

### Extract - E

There is only one Extract method that cannot be changed in 'clips.csv'. Videos are imported by python from a mapped drive. By default, this location is mapped to 'secrets.json' index `0`.

### Transform - T

Clippy uses the moviepy.editor module in Python to extract a sub clip from a video file and rip the audio track to a .mp3 file.

Transform methods are accessed by updating the value in the `t` column of 'clips.csv'. The available methods build into Clippy are listed in the following table:

+--------+--------+---------------------------------------------------------------------------+------------+
| Index  | Name   | Description                                                               | Method     |
+:=======+:=======+:==========================================================================+:===========+
| 0      | pass   | Do nothing                                                                |            |
+--------+--------+---------------------------------------------------------------------------+------------+
| 1      | mp3    | Extracts the audio from a clip and saves as .mp3.                         | rip        |
+--------+--------+---------------------------------------------------------------------------+------------+
| 2      | mp4    | Saves the video as a .mp4 file.                                           | crop       |
+--------+--------+---------------------------------------------------------------------------+------------+
| 3      | mp3-4  | Saves the video as a .mp4 file and also rips the audio and saves as .mp3. | cropAndRip |
+--------+--------+---------------------------------------------------------------------------+------------+

### Load - L

Clippy automatically uploads the ripped audio file to a Podcast host via the host's API.

Podcast host specific API parameters can be found in the 'conf.json' file.

Load methods are accessed by updating the value in the `l` column of 'clips.csv'. The available methods build into Clippy are listed in the following table:

| Index | Podcast Host | Description                   | URL                             |
|:------|:-------------|:------------------------------|:--------------------------------|
| 0     | Do nothing   | Don't load the file anywhere. |                                 |
| 1     | Podbean      | Upload podcast to Podbean     | <https://www.podbean.com/login> |
