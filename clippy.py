import argparse
import classes as cl
from datetime import datetime
import json
import os
import re
from sys import exit

def validTimestamp(x):
  return bool(re.match("^\\d*:\\d*:\\d*(\\.\\d*)?$", x))

parser = argparse.ArgumentParser(description="Crop a video file and rip the audio track",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-j", "--json", help = "video clip json config")
args = parser.parse_args()
config = vars(args)

if config["json"] is None:
  exit("Missing input JSON parameters.")

episode = json.loads(config["json"])
episode["t"] = int(episode["t"])
episode["l"] = int(episode["l"])

f = open('conf.json')
etl = json.load(f)
f.close()

f = open('secrets.json')
secrets = json.load(f)
f.close()

# Extract
    
clip = cl.Clip( episode["id"],
                secrets["0"], 
                episode["filename"], 
                secrets["1"],
                episode["start_time"],
                episode["end_time"])

if not validTimestamp(clip.start):
  exit("Invalid start time.")
if not validTimestamp(clip.end):
  exit("Invalid end time.")
if clip.endTimestamp <= clip.startTimestamp:
  exit("End time should be after start time.")

# Transform

match episode["t"]:
  case 0:
    pass
  case 1:
    clip.rip()
  case 2:
    clip.crop()
  case 3:
    clip.cropAndRip()
  case _:
    exit("Not a valid tranform 't' method.")

# Load

match episode["l"]:
  case 0:
    l = 99
  case 1:
    if not os.path.isfile(clip.uri_mp3):
      exit("Load: Podbeans: mp3 file does not exist.")
    uri_logo = os.path.join(secrets["2"], episode["episode_logo"])
    if not os.path.isfile(uri_logo):
      exit("Load: Podbeans: Logo does not exist.")
    uri_content = os.path.join(secrets["2"], episode["content"])
    if os.path.isfile(uri_content):
      with open(uri_content) as f:
        content = f.read()
      f.close()
    else:
      exit("Load: Podbeans: Content file does not exist.")
    # check for content asset, if exists read file
    l = cl.Podbean( etl["load"][1]["url_token"],
                    etl["load"][1]["url_upload"],
                    etl["load"][1]["url_episode"],
                    secrets[str(etl["load"][1]["client_id"])],
                    secrets[str(etl["load"][1]["client_secret"])],
                    episode["title"],
                    content,
                    episode["status"],
                    episode["type"])
                    
    l.requestToken()
    
    media = l.uploadAuth(clip.uri_mp3, "auido/mpeg")
    l.media_key = media["file_key"]
    l.upload(media["presigned_url"], clip.uri_mp3, "audio/mpeg")
      
    if bool(re.match("^.*jp(g|eg)$", uri_logo)):
      logo = l.uploadAuth(uri_logo, "image/jpeg")
      l.logo_key = logo["file_key"]
      l.upload(logo["presigned_url"], uri_logo, "image/jpeg")
      
    if bool(re.match("^.*png$", uri_logo)):
      logo = l.uploadAuth(uri_logo, "image/png")
      l.logo_key = logo["file_key"]
      l.upload(logo["presigned_url"], uri_logo, "image/png")
      
    l.publish()
    
  case _:
    exit("Not a valid load 'l' method.")
