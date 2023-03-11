from datetime import datetime
from moviepy.editor import *
from numpy import dot
import os
import requests
from shutil import rmtree


class ExtractLocal:
    def __init__(self, uri):
        self.uri = uri


class Clip:
    def __init__(self, episode_id, in_location, filename, out_location, start, end):
        self.id = episode_id
        self.in_location = in_location
        self.filename = filename
        self.out_location = out_location
        self.start = start
        self.end = end

    @property
    def uri_in(self):
        return os.path.join(self.in_location, self.filename)

    @property
    def uri_out(self):
        return os.path.join(self.out_location, self.id)

    @property
    def uri_mp3(self):
        return os.path.join(self.uri_out, self.id + ".mp3")

    @property
    def uri_mp4(self):
        return os.path.join(self.uri_out, self.id + ".mp4")

    @property
    def start_timestamp(self):
        return parse_time(self.start)

    @property
    def end_timestamp(self):
        return parse_time(self.end)

    def create_directory(self):
        if os.path.exists(self.uri_out):
            print(f"Output directory '{self.id}' is not empty, continue? [Enter 'y' for yes.]")
            fl = input()
            if not (fl in ["Y", "y"] or len(fl) == 0):
                exit()
            rmtree(self.uri_out)
        if not os.path.exists(self.uri_out):
            os.mkdir(self.uri_out)

    def clip(self):
        x = VideoFileClip(self.uri_in)
        return x.subclip(self.start_timestamp, self.end_timestamp)  # seconds

    def crop(self):
        self.create_directory()
        self.clip().write_videofile(self.uri_mp4)
        return 99

    def rip(self, intro_path):
        self.create_directory()
        intro_clip = AudioFileClip(intro_path)
        concat = concatenate_audioclips([intro_clip, self.clip().audio])
        concat.write_audiofile(self.uri_mp3)
        return 99

    def crop_and_rip(self):
        self.create_directory()
        self.clip().audio.write_audiofile(self.uri_mp3)
        self.clip().write_videofile(self.uri_mp4)
        return 99


class Podbean:
    def __init__(self, token_endpoint, upload_endpoint, episode_endpoint, client_id, client_secret, title, content,
                 status, publish_type):
        self.token_endpoint = token_endpoint
        self.upload_endpoint = upload_endpoint
        self.episode_endpoint = episode_endpoint
        self.client_id = client_id
        self.client_secret = client_secret
        self.title = title
        self.content = content
        self.status = status
        self.type = publish_type
        self.token = None
        self.media_key = None
        self.logo_key = None

    def request_token(self):
        params = {"grant_type": "client_credentials"}
        r = requests.post(self.token_endpoint,
                          auth=(self.client_id, self.client_secret),
                          data=params)
        print(datetime.now(), f" Token request status code: {r.status_code}")
        x = r.json()
        self.token = x["access_token"]
        if r.status_code != 200:
            print(x["error"])
            print(x["error_description"])
        return 0

    def upload_auth(self, file, content_type):
        params = {"access_token": self.token,
                  "filename": os.path.basename(file),
                  "filesize": os.path.getsize(file),
                  "content_type": content_type}
        r = requests.get(self.upload_endpoint, params=params)
        x = r.json()
        print(datetime.now(), f" Authorise file upload status code: {r.status_code}")
        if r.status_code != 200:
            print(x["error"])
            print(x["error_description"])
        return x

    def publish(self):
        data = {"access_token": self.token,
                "title": self.title,
                "content": self.content,
                "status": self.status,
                "type": self.type}
        if self.media_key is not None:
            data["media_key"] = self.media_key
        if self.logo_key is not None:
            data["logo_key"] = self.logo_key
        r = requests.post(self.episode_endpoint, data=data)
        print(datetime.now(), f" Episode status code: {r.status_code}")
        if r.status_code != 200:
            x = r.json()
            print(x["error"])
            print(x["error_description"])


def parse_time(x):  # takes time in "HH:MM:SS" format and converts to seconds
    a = [int(i) for i in x.split(":", 3)]
    b = [3600, 60, 1]
    return dot(a, b)


def upload(url, file, content_type) -> int:
    headers = {"Content-Type": content_type}
    files = {"file": (os.path.basename(file), open(file, 'rb'))}
    r = requests.put(url, headers=headers, files=files)
    print(datetime.now(), f" {os.path.basename(file)} Upload status code: {r.status_code}")
    if r.status_code != 200:
        x = r.json()
        print(x["error"])
        print(x["error_description"])
    return 0
