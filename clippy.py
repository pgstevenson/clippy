import argparse
import json
import os
import pathlib
import re
from sys import exit
import uuid

import classes as cl


def validate_timestamp(x) -> bool:
    return bool(re.match("^\\d*:\\d*:\\d*(\\.\\d*)?$", x))


parser = argparse.ArgumentParser(description="Crop a video file and rip the audio track",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-j", "--json", help="video clip json config")
args = parser.parse_args()
config = vars(args)

if config["json"] is None:
    exit("Missing input JSON path.")

f = open(config["json"])
episode = json.load(f)
episode["t"] = int(episode["t"])
episode["l"] = int(episode["l"])

os.chdir(pathlib.Path(__file__).parent)

f = open('conf.json')
etl = json.load(f)
f.close()

f = open('secrets.json')
secrets = json.load(f)
f.close()

# Extract

clip = cl.Clip(str(uuid.uuid1()).upper(),
               secrets["0"],
               episode["filename"],
               secrets["1"],
               episode["start_time"],
               episode["end_time"])

if not validate_timestamp(clip.start):
    exit("Invalid start time.")
if not validate_timestamp(clip.end):
    exit("Invalid end time.")
if clip.end <= clip.start:
    exit("End time should be after start time.")

# Transform

match episode["t"]:
    case 0:
        pass
    case 1:
        intro_path = etl["transform"][1]["intro_filename"]
        intro_path = os.path.join(secrets["2"], intro_path)
        outro_path = etl["transform"][1]["outro_filename"]
        outro_path = os.path.join(secrets["2"], outro_path)
        clip.rip(intro_path, outro_path)
    case _:
        exit("Not a valid transform 't' method.")

# Load

match episode["l"]:
    case 0:
        load = 99
    case 1:
        if not os.path.isfile(clip.uri_mp3):
            exit("Load: Podbean: mp3 file does not exist.")
        uri_content = os.path.join(secrets["2"], episode["content"])
        if os.path.isfile(uri_content):
            with open(uri_content) as f:
                content = f.read()
            f.close()
        else:
            exit("Load: Podbean: Content file does not exist.")
        # check for content asset, if exists read file
        load = cl.Podbean(etl["load"][1]["url_token"],
                          etl["load"][1]["url_upload"],
                          etl["load"][1]["url_episode"],
                          secrets[str(etl["load"][1]["client_id"])],
                          secrets[str(etl["load"][1]["client_secret"])],
                          episode["title"],
                          content,
                          episode["status"],
                          episode["type"],
                          episode["logo_url"])

        load.request_token()

        media = load.upload_auth(clip.uri_mp3, "audio/mpeg")
        load.media_key = media["file_key"]
        cl.upload(media["presigned_url"], clip.uri_mp3, "audio/mpeg")

        load.publish()

    case _:
        exit("Not a valid load 'l' method.")

# Clean up TMP files

if os.path.isfile(clip.uri_mp3):
    os.remove(clip.uri_mp3)
if os.path.isfile(config["json"]):
    os.remove(config["json"])
