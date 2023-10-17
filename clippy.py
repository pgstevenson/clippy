import argparse
import classes as cl
import json
import pathlib
import os
import re
from sys import exit


def validate_timestamp(x) -> bool:
    return bool(re.match("^\\d*:\\d*:\\d*(\\.\\d*)?$", x))


parser = argparse.ArgumentParser(description="Crop a video file and rip the audio track",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-j", "--json", help="video clip json config")
args = parser.parse_args()
config = vars(args)

if config["json"] is None:
    exit("Missing input JSON parameters.")

episode = json.loads(config["json"])
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

clip = cl.Clip(episode["id"],
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
    case 2:
        clip.crop()
    case 3:
        clip.crop_and_rip()
    case _:
        exit("Not a valid transform 't' method.")

# Load

match episode["l"]:
    case 0:
        load = 99
    case 1:
        if not os.path.isfile(clip.uri_mp3):
            exit("Load: Podbean: mp3 file does not exist.")
        # uri_logo = os.path.join(secrets["2"], episode["episode_logo"])
        # if not os.path.isfile(uri_logo):
        #     exit("Load: Podbean: Logo does not exist.")
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

        # if bool(re.match("^.*jp(g|eg)$", uri_logo)):
        #     logo = load.upload_auth(uri_logo, "image/jpeg")
        #     load.logo_key = logo["file_key"]
        #     cl.upload(logo["presigned_url"], uri_logo, "image/jpeg")

        # if bool(re.match("^.*png$", uri_logo)):
        #     logo = load.upload_auth(uri_logo, "image/png")
        #     load.logo_key = logo["file_key"]
        #     cl.upload(logo["presigned_url"], uri_logo, "image/png")

        load.publish()

    case _:
        exit("Not a valid load 'l' method.")
