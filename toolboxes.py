#!/usr/bin/env python3

#!/usr/bin/env python3

import sys
import os
import re
import subprocess
from datetime import datetime, timedelta

#Hashable class for checking duplicates during hours_used()
class transaction:
  def __init__(self, time, type, toolbox, username, hostname, day):
    self.time = time
    self.type = type
    self.toolbox = toolbox
    self.username = username
    self.hostname = hostname
    self.day = day
  def __eq__(self, other):
    if isinstance(other, transaction):
      return self.username == other.username
  def __hash__(self):
      return self.username.__hash__()

class counter:
  def __init__(self, name):
    self.number = 0
    self.name=name

#MAKE LIST OF CHECKOUTS AND THEN CHECKINS OBJECTS, SORT THEM BY DATETIME, MATCH CHECKINS TO CHECKOUTS BY USERNAME AND ITERATING THROUGH

#START REGULAR EXPRESSIONS
pattern = '^(\d+:\d+:\d+)\s\(\w+\)\s(\w+)\:\s\"(\w+)\"\s(\w+)\@(\w+)' #Pattern matching a login
# 3:35:07 (MLM) OUT: "Image_Toolbox" sodell@0310328C9TQQ22
spattern = '.*Start-Date:\s(.*)\s(Pacific Standard Time)' #Pattern matching the start of the log

timestamp = '.*\s(TIMESTAMP)\s(.*)' #Pattern for matching the timestamp
# 3:29:08 (lmgrd) (@lmgrd-SLOG@) Start-Date: Sun Dec 13 2020 03:29:08 Pacific Standard Time
#END REGULAR EXPRESSIONS

#Lists for all objects, then toolboxes
checkouts = []
checkins = []
stats = []

#LOOKUP CHECKLIST 4/21/21
#itertool
#Split into sublists based on days!!! Do class inheritance?
#Dedup checkouts and checkins using sets

def parse():
  time = None
  type = None
  toolbox = None
  username = None
  hostname = None
  day = None
  hours = None
  logfile = input("Parse which file?:")
  with open(logfile , 'r') as f:
    lines = f.readlines() #Read all lines
    for line in lines:
      match = re.search(pattern, line) #If line follows regex pattern, then match
      startdate = re.search(spattern, line) #Get the start of log
      current_day = re.search(timestamp, line)
      if current_day:
        day = datetime.strptime(str(current_day.group(2)), '%m/%d/%Y')
      if startdate:
        starttime = startdate.group(1) #Sun Dec 13 2020 03:29:08 Pacific Standard Time
        day = datetime.strptime(str(starttime), '%a %b %d %Y %H:%M:%S')
        day.strftime('%m/%d/%Y')
      if match:
        time = match.group(1)   #the time a toolbox is checked out or in
        newtime = datetime.strptime(str(time), '%H:%M:%S')
        type = match.group(2)   #the type of interaction; checkout or checkin
        toolbox = match.group(3) #the name of the toolbox
        username = match.group(4) #the username who checked out toolbox
        hostname = match.group(5) #the hostname of the computer that toolbox is checked from
      if type == 'OUT':
        checkouts.append(transaction(newtime, type, toolbox, username, hostname, day))
      else:
        checkins.append(transaction(newtime, type, toolbox, username, hostname, day))


    #Building a list of objects that represent a matching checkout and checkin with length of time, and toolbox used
    for outs in checkouts:
      for ins in checkouts:
        if outs == ins:
          timein = ins.time
          timeout = outs.time
          time_used = timein - timeout
          #CHECK HERE FOR DUPLICATES?
          stats.append(transaction(time_used, ins.type, ins.toolbox, ins.username, ins.hostname, ins.day))


def hours_used():
  for obj in stats:
    print(f"{obj.username}@{obj.hostname} used {obj.toolbox} on {obj.day} for {obj.time}")

def num_of_checkouts_toolbox():
  max = 0
  min = 0
  who_min = None
  who_max = None

  toolboxlist = []
  toolboxes = {obj.toolbox for obj in checkouts} #Set comprehension; get unique toolboxes

  for tb in toolboxes: #make list of objects for counting toolboxes
    toolboxlist.append(counter(tb))

  for outs in checkouts:
    if outs.type == 'OUT':
      tbname = outs.toolbox #Grab name of the toolbox that was checked out
      for tb in toolboxlist:
        if tb.name == tbname:
          tb.number = tb.number + 1
        if tb.number > max:
          max = tb.number
          who_max = tb.name
        if tb.number <= min:
          min = tb.number
          who_min = tb.name

  for box in toolboxlist:
    print(f"Toolbox: {box.name} was checked out {box.number} times.")

  print(f"MOST CHECKOUTS FROM TOOLBOX {who_max} at {max}")
  print(f"LEAST CHECKOUTS FROM TOOLBOX {who_min} at {min}")

def num_of_checkouts_user():
  max = 0
  min = 0
  who_min = None
  who_max = None

  namelist = []
  names = {obj.username for obj in checkouts} #Set comprehension; get unique names

  for name in names: #make list of objects for counting number of checkouts per name
    namelist.append(counter(name))

  for outs in checkouts:
    if outs.type == 'OUT':
      name = outs.username
      for x in namelist:
        if x.name == name:
          x.number = x.number + 1
        if x.number > max:
          max = x.number
          who_max = x.name
        if x.number <= min:
          min = x.number
          who_min = x.name
        
  for name in namelist:
    print(f"User: {name.name} has {name.number} checkouts.")

  print(f"MOST CHECKOUTS FROM USER {who_max} at {max}")
  print(f"LEAST CHECKOUTS FROM USER {who_min} at {min}")

def main():
  print("START PARSE")
  parse()
  print("END PARSE")

  go = True

  while go:
    print("Choose an option:")
    print("1: General statistics")
    print("2: Total number of checkouts by toolbox")
    print("3: Total number of checkouts per user")
    print("4: Time statistics")
    print("5: Stop")
                
    val = input("Option = ")
    if val == '1':
      print("----------TOOLBOX STATS----------")
      num_of_checkouts_toolbox()
      print("----------USER STATS----------")
      num_of_checkouts_user()
    elif val == '2':
      num_of_checkouts_toolbox()
    elif val == '3':
      num_of_checkouts_user()
    elif val == '4':
      hours_used()
    else:
      go = False

if __name__ == "__main__":
  main()


