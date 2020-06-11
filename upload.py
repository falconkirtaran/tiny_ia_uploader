#!/usr/bin/python3

# usage: upload.py 201601

# This is a script made for uploading a bunch of files in a directory that are named things like
# 20160101T0015.mp3
# and are generated at regular intervals.

# Modify to suit your needs.
# hyphendate is intended to describe the date of the whole item, which is a collection of files
# in the provided code, collections represent a month's worth of audio; use a day for significant volumes of audio
# (this was designed for MP3 streams of 5 minutes, 4.2MB per, 24 times per day); use e.g. YYYY-MM-DD
# please remember to set the metadata according to your specific content; it is very annoying to change later.

import subprocess
import hashlib
import os
import sys
import shutil

basepath = 'https://s3.us.archive.org/ITEM_NAME' #change the item name; it gets concatenated with whatever you choose for date
creds = 'XXXXXXXXXXXXXXXX:XXXXXXXXXXXXXXXX' # IA API key, for use with "Authorization: LOW ..."
olddir = '_old/'

def file_md5(fname):
    md5 = hashlib.md5()
    with open(fname, "rb") as inputfile:
        for block in iter(lambda: inputfile.read(16384), b""):
            md5.update(block)

    return md5.hexdigest()

def sendfile(filename, date, auth):
    print("Sending " + filename)
    hyphendate = '{}-{}'.format(date[:4], date[4:6])
    collectionpath = '{}{}'.format(basepath, date)
    return subprocess.call([
        "curl", "-v", "--location", "--fail",
        "--speed-limit", "1", "--speed-time", "900",
        "--header", "Content-MD5: " + file_md5(filename),
        "--header", "x-archive-queue-derive:0",
        "--header", "x-amz-auto-make-bucket:1",
        "--header", "x-archive-meta-collection:opensource_audio",
        "--header", "x-archive-meta-mediatype:audio",
        "--header", "x-archive-meta-subject:news",
        "--header", "x-archive-meta-title:The thing for month {}".format(hyphendate),
        "--header", "x-archive-meta-date:" + hyphendate,
        "--header", "x-archive-meta-description:The thing; times given in UTC.",
        "--header", "x-archive-meta-creator:Agency",
        "--header", "x-archive-meta-language:eng",
        "--header", "authorization: LOW " + auth,
        "-o", "/dev/stdout",
        "--upload-file", filename,
        "{}/{}".format(collectionpath, filename)])

def sendfiles(filelist, date, creds):
    failed = []
    for f in filelist:
        exitcode = sendfile(f, date, creds)
        if exitcode != 0:
            failed += [f]
        else:
            shutil.move(f, olddir)
    return failed

date = sys.argv[1]
files = [f for f in os.listdir() if os.path.isfile(f) and f[:6] == date]

failed1 = sendfiles(files, date, creds)

failed2 = sendfiles(failed1, date, creds)

if len(failed2) != 0:
    print("Failed to send: " + repr(failed2))
