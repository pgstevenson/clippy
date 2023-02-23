from moviepy.editor import *
from numpy import dot
import os
from shutil import rmtree

class ExtractLocal:
  def __init__(self, uri):
    self.uri = uri

class Clip:
  def __init__(self, id, inLoc, outLoc, filename, start, end):
    self.id = id
    self.inLoc = inLoc
    self.outLoc = outLoc
    self.filename = filename
    self.start = start
    self.end = end
    
  @property
  def inPath(self):
    return os.path.join(self.inLoc, self.filename)
  
  @property
  def outPath(self):
    return os.path.join(self.outLoc, self.id)
  
  @property
  def outFile(self):
    return os.path.join(self.outPath, self.id)
  
  @property
  def startTimestamp(self):
    return parseTime(self.start)
  
  @property
  def endTimestamp(self):
    return parseTime(self.end)
  
  def createDir(self):
    if os.path.exists(self.outPath):
      print(f"Output directory '{self.id}' is not empty, continue? [Enter 'y' for yes.]")
      fl = input()
      if not (fl in ["Y", "y"] or len(fl) == 0):
        exit()
    rmtree(self.outPath)
    if not os.path.exists(self.outPath):
      os.mkdir(self.outPath)
  
  def clip(self):
    x = VideoFileClip(self.inPath)
    return x.subclip(self.startTimestamp, self.endTimestamp) # seconds

  def crop(self):
    self.createDir()
    self.clip().write_videofile(self.outFile + ".mp4")
    return 99
  
  def rip(self):
    self.createDir()
    self.clip().audio.write_audiofile(self.outFile + ".mp3")
    return 99
  
  def cropAndRip(self):
    self.createDir()
    self.clip().audio.write_audiofile(self.outFile + ".mp3")
    self.clip().write_videofile(self.outFile + ".mp4")
    return 99

def parseTime(x): # takes time in "HH:MM:SS" format and converts to seconds
    a = [int(i) for i in x.split(":", 3)]
    b = [3600, 60, 1]
    return dot(a, b)
