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
import psutil
from SimConnect import *
import configparser

TITLE = 'msfs-screenshot-gps-data'
VERSION = 'v0.1'
print('{} {}'.format(TITLE, VERSION))

CONFIG_FILE = '{}-{}.ini'.format(TITLE, VERSION)
DEFAULT_PREFERENCES = {
    'General': [
        {
            'name': 'WatchDirectory',
            'value': os.path.join(os.path.expanduser('~') + "\\Pictures\\Screenshots"),
            'comment': "Directory containing screenshots to watch for changes. By default '%USERPROFILE%\Pictures\Screenshots'."
        },
        {
            'name': 'Overwrite',
            'value': False,
            'comment': 'Set to true to disable exiftool creating a backup before adding the EXIF data.'
        }
    ],
    'Developer': [
        {
            'name': 'Debug',
            'value': False,
            'comment': 'Print more information for debugging purposes when set to true.'
        }
    ]
}

# Create config file if it doesn't exist
if not os.path.isfile(CONFIG_FILE):
    with open(CONFIG_FILE, 'w') as file:
        output = ''

        for section, preferences in DEFAULT_PREFERENCES.items():
            output = output + '\n\n[{}]'.format(section)

            for preference in preferences:
                output = output + '\n{} = {}'.format(preference['name'], preference['value'])
                output = output + '\n; {}'.format(preference['comment'])

        output = output.strip() + '\n'
        file.write(output)

# Load the configuration file
config = configparser.ConfigParser()
config.read(CONFIG_FILE)

WATCH_DIR = config.get('General', 'WatchDirectory')
OVERWRITE = config.getboolean('General', 'Overwrite')
DEBUG = config.getboolean('Developer', 'Debug')

# Download 'exiftool' (https://exiftool.org/)
exiftool = './exiftool(-k).exe'
if not os.path.isfile(exiftool):
    print("Downloading 'exiftool'..", end='', flush=True)
    url = 'https://exiftool.org/exiftool-12.06.zip'
    request = requests.get(url)
    archive = zipfile.ZipFile(io.BytesIO(request.content))
    archive.extractall()
    print('  --> Done.')


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

        if DEBUG:
            print("event: src_path='{}', event_type='{}'".format(event.src_path, event.event_type))

    def on_modified(self, event):
        self.process(event)

    def on_created(self, event):
        print("\nFile created: '{}'.".format(event.src_path))

        # Check if sim is running (https://stackoverflow.com/a/7788702)
        if not 'FlightSimulator.exe' in (p.name() for p in psutil.process_iter()):
            print('Warning: The simulator is not running. Not going to add GPS data to this file.')
            return

        # Connect to sim
        print('Getting data from sim..')
        sm = SimConnect()
        aq = AircraftRequests(sm)

        # Get data from sim
        data = {
            'GPSLatitude': round(aq.get("GPS_POSITION_LAT"), 5),    # degrees
            'GPSLongitude': round(aq.get("GPS_POSITION_LON"), 5),   # degrees
            'GPSAltitude': round(aq.get('GPS_POSITION_ALT'), 2),    # meter
            'GPSSpeed': aq.get('GPS_GROUND_SPEED')                  # m/s
        }

        # Disconnect from sim
        sm.exit()

        # Check if player is not in flight
        if round(data['GPSLatitude'], 2) < 0.1 and round(data['GPSLongitude'], 2) < 0.1 and data['GPSSpeed'] < 0.1:
            print('Warning: It looks like the player is in a menu. Not going to add GPS data to this file.')
            return

        # Set additional tags (https://exiftool.org/TagNames/GPS.html)
        data['GPSLatitudeRef'] = 'North'
        if data['GPSLatitude'] < 0:
            data['GPSLatitudeRef'] = 'South'

        data['GPSLongitudeRef'] = 'East'
        if data['GPSLongitude'] < 0:
            data['GPSLongitudeRef'] = 'West'

        data['GPSAltitudeRef'] = 'Above Sea Level'

        data['GPSSpeed'] = round(data['GPSSpeed']*3.6, 2)   # Convert m/s to km/h
        data['GPSSpeedRef'] = 'km/h'                        # Set unit to km/h

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
            cmdline.append('-verbose')

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
