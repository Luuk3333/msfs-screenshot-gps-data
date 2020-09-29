# msfs-screenshot-gps-data
This tool looks for new screenshots while Microsoft Flight Simulator is running, retrieves GPS data including location and altitude and adds this information to the screenshot.

## Important notes
- The aircraft is used as the source of the GPS data. The location of the in-game camera may not match that of the aircraft. When using the drone- or developer camera you may end up with a location that does not match what's in the screenshot. This could be fixed if dedicated in-game camera variables are added by the developers of the simulator in the future.
- This tool saves GPS data when the simulator is running in an active state. No distinction is made between the simulator and other applications running. Screenshots taken of other applications while the simulator is running may also be included. In the future more checks could be performed to make sure the simulator is the active window.
- The addition of exif information in PNG images [is relatively new](https://stackoverflow.com/a/9576717). Image editors and other geotagging-related features and applications may not support this. Possible solutions are converting screenshots to JPEG images (which exif data is more supported in applications) or configuring the screenshot software to create JPEG images in the first place. Note that these solutions may degrade the image quality depending on the set compression level.

## Installation
1. Read the notes above.
2. Download the latest `.exe` from [the releases page](https://github.com/Luuk3333/msfs-screenshot-gps-data/releases).
3. On the first launch an `.ini` file will be created containing preferences. You may want to change the folder which will be watched for changes. By default the built-in Windows screenshot directory is used located at `%USERPROFILE%\Pictures\Screenshots` (press WIN+PRINTSCREEN to capture a screenshot).

## Build from source:
1. Install dependencies: `pip3 install -r requirements.txt`.
2. Build `.exe`: `pyinstaller --add-data="SimConnect/SimConnect.dll;SimConnect/" --clean --exclude-module=.git --name="msfs-screenshot-gps-data" --onefile app.py`. Note: currently the script expects `SimConnect.dllc` for unknown reasons, this is solved by changing `SimConnect\SimConnect.dll` to `SimConnect\SimConnect.dllc` with a hex editor in the output `.exe`.

## Attributions
- This project includes unmodified source code (the directory `SimConnect/`) of the project '[Python-SimConnect](https://github.com/odwdinc/Python-SimConnect)' by odwdinc licensed under the 'GNU Affero General Public License v3.0' (located at `SimConnect/LICENSE`) to interface with the simulator.
