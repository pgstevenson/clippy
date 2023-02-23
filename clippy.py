import argparse
import classes as cl
from json import load
from pandas import read_csv
from re import match
from sys import exit

def validTimestamp(x):
  return bool(match("^\\d*:\\d*:\\d*(\\.\\d*)?$", x))

parser = argparse.ArgumentParser(description="Crop a video file and rip the audio track",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-i", "--input", help="video clip id")
args = parser.parse_args()
config = vars(args)

if config["input"] is None:
  print("Video clip id:")
  config["input"] = input()

df = read_csv("clips.csv")
# print(df.to_markdown())

if not config["input"] in df.id.values:
  exit("ID not found. Exiting.")

f = open('conf.json')
etl = load(f)
f.close()

f = open('secrets.json')
secrets = load(f)
f.close()

# Extract

match df["e"][df.id == config["input"]][0]:
  case 0:
    e = cl.ExtractLocal(secrets[str(etl["extract"][0]["uri"])])
    
print(e.uri)
    
clip = cl.Clip( config["input"], 
                e.uri, 
                None,
                df["uri"][df.id == config["input"]][0], 
                df["start_time"][df.id == config["input"]][0],
                df["end_time"][df.id == config["input"]][0])

if not validTimestamp(clip.start):
  exit("Invalid start time.")
if not validTimestamp(clip.end):
  exit("Invalid end time.")
if clip.endTimestamp <= clip.startTimestamp:
  exit("End time should be after start time.")

# Transform

match df["t"][df.id == config["input"]][0]:
  case 0:
    clip.outLoc = secrets[str(etl["transform"][0]["path"])]
    clip.rip()
  case 1:
    clip.outLoc = secrets[str(etl["transform"][1]["path"])]
    clip.crop()
  case 2:
    clip.outLoc = secrets[str(etl["transform"][2]["path"])]
    clip.cropAndRip()

# Load

match df["l"][df.id == config["input"]][0]:
  case 0:
    l = 99
