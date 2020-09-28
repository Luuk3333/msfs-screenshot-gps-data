This tool looks for new screenshots while Microsoft Flight Simulator is running, retrieves GPS data including location and altitude and adds this information to the screenshot.

Important notes:
- The aircraft is used as the source of the GPS data. The location of the in-game camera may not match that of the aircraft. When using the drone- or developer camera you may end up with a location that does not match what's in the screenshot. This could be fixed if dedicated in-game camera variables are added by the developers of the simulator in the future.
- This tool saves GPS data when the simulator is running in an active state. No distinction is made between the simulator and other applications running. Screenshots taken of other applications while the simulator is running may also be included. In the future more checks could be performed to make sure the simulator is the active window.
- The addition of exif information in PNG images [is relatively new](https://stackoverflow.com/a/9576717). Image editors and other geotagging-related features and applications may not support this. Possible solutions are converting screenshots to JPEG images (which exif data is more supported in applications) or configuring the screenshot software to create JPEG images in the first place. Note that these solutions may degrade the image quality depending on the set compression level.

Installation:
- Install dependencies: `pip3 install -r requirements.txt`
- Take a look at the user preferences near the top of the file `app.py`. By default the built-in Windows screenshot directory is used located at `%USERPROFILE%\Pictures\Screenshots` (press WIN+PRINTSCREEN to capture a screenshot).
- Run the application: `python3 app.py`

This project includes unmodified source code (the directory `SimConnect/`) of the project '[Python-SimConnect](https://github.com/odwdinc/Python-SimConnect)' by odwdinc licensed under the 'GNU Affero General Public License v3.0' (located at `SimConnect/LICENSE`) to interface with the simulator.
