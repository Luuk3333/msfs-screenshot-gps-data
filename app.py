import time
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import sys
import subprocess
import os
import requests
import zipfile
import io
from distutils.dir_util import copy_tree

DEBUG = True        # Print more information for debugging purposes when set to true
OVERWRITE = False   # Set to true to disable exiftool creating a backup before adding the EXIF data.
WATCH_DIR = os.path.join(os.path.expanduser('~') + "\\Pictures\\Screenshots")   # Directory containing screenshots to watch for changes. # By default '%USERPROFILE%\Pictures\Screenshots'.

# Download 'exiftool' (https://exiftool.org/)
exiftool = './exiftool(-k).exe'
if not os.path.isfile(exiftool):
    print("Downloading 'exiftool'..", end='')
    url = 'https://exiftool.org/exiftool-12.06.zip'
    request = requests.get(url)
    archive = zipfile.ZipFile(io.BytesIO(request.content))
    archive.extractall()
    print('  --> Done.')

# Download 'Python-SimConnect' (https://github.com/odwdinc/Python-SimConnect)
simconnect_dir = 'SimConnect/'
if not os.path.isdir(simconnect_dir):
    print("Downloading 'Python-SimConnect'..", end='')
    os.mkdir(simconnect_dir)
    
    url = 'https://github.com/odwdinc/Python-SimConnect/archive/05263a861ad5fad6e5783bc331567f42151ee72e.zip'
    request = requests.get(url)
    archive = zipfile.ZipFile(io.BytesIO(request.content))

    # Only unzip files in 'SimConnect' subdirectory
    for file in archive.namelist():
        if os.path.dirname(file).lower().endswith('simconnect') and not file.endswith('/'):
            newfile = os.path.join(os.getcwd(), simconnect_dir, os.path.basename(file))
            
            if DEBUG:
                print("Unzipping file '{}' to '{}'.".format(file, newfile))

            with open(newfile, 'wb') as f:
                f.write(archive.read(file))
    print('  --> Done.')

from SimConnect import *

class MyHandler(PatternMatchingEventHandler):
    patterns = ['*.jpg', '*.jpeg', '*.png']

    def process(self, event):
        """
        event.event_type 
            'modified' | 'created' | 'moved' | 'deleted'
        event.is_directory
            True | False
        event.src_path
            path/to/observed/file
        """
        # the file will be processed there
        if DEBUG:
            print(event.src_path, event.event_type)  # print now only for degug

    def on_modified(self, event):
        self.process(event)

    def on_created(self, event):
        print("\nFile created: '{}'.".format(event.src_path))

        # Connect to sim
        print('Getting data from sim..')
        sm = SimConnect()
        aq = AircraftRequests(sm)

        # Get data from sim
        data = {
            'GPSLatitude': aq.get("GPS_POSITION_LAT"),      # degrees
            'GPSLongitude': aq.get("GPS_POSITION_LON"),     # degrees
            'GPSAltitude': aq.get('GPS_POSITION_ALT'),      # meter
            'GPSSpeed': aq.get('GPS_GROUND_SPEED')          # m/s
        }

        # Disconnect from sim
        sm.exit()

        data['GPSSpeed'] = data['GPSSpeed']*3.6     # Convert m/s to km/h
        data['GPSSpeedRef'] = 'km/h'                # Set unit to km/h (https://exiftool.org/TagNames/GPS.html)

        # Compile exiftool command
        cmdline = [exiftool]

        for key, value in data.items():
            if value == -999999:
                print('Warning: invalid value for {}: {}.'.format(key, value))
                continue
            cmdline.append('-{}={}'.format(key, value))

        if OVERWRITE:
            cmdline.append('-overwrite_original')

        if DEBUG:
            cmdline.append('-verbose=3')

        cmdline.append(event.src_path)

        if DEBUG:
            import json
            print('data:', json.dumps(data, indent=4))
            print(cmdline)
        
        # Add GPS data to screenshot
        print('Adding EXIF data to image..')
        process = subprocess.Popen(cmdline, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        process.communicate(input=b'\n')    # Pass exiftool's '-- press ENTER --'

        print('Finished. Watching for changes..')

        self.process(event)

if __name__ == '__main__':
    observer = Observer()
    observer.schedule(MyHandler(), WATCH_DIR)
    observer.start()
    
    print("\nWatching for changes in directory: '{}'..".format(WATCH_DIR))

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
