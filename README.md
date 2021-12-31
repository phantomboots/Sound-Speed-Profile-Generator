# Sound-Speed-Profile-Generator

This program is a standalone Python based GUI that uses log files created by the Advanced Serial Data Logger program to generate an in-situ Sound Speed profile, to aid with acoustic tracking of NDST vehicles. This is particular important when operating in very stratified waters offshore, but the effects will benefit acoustic tracking at any depth. This GUI is specifically designed to generate sound speed profiles that can be used with EgdeTech's TrackMan software.

The program can be run on a PC with an existing Python 3 installation, or can be 'boxed up' as a standalone folder using a program such as PyInstaller (https://www.pyinstaller.org/) to generate a more portable version. Note that PyInstaller can also generate a single executable, but this method makes the script much slower since all dependencies are loaded at run time each time the executable is run.

Regardless of which method is chosen, the GUI should be run on the same program that TrackMan is running on. This is not strictly necessary, but will make things easier as you won't need to copy and paste the output files from one compute to another.

The GUI is intended to be run when the vehicle first reaches target depth -- the idea is that a profile is collected as the vehicel descends from surface, and this in-situ profile of sound speed is used to provide the most accurate model of the sound speed at the location that is about to be surveyed. The GUI should be relatively intuitive. The program will generate a graphical preview of the sound speed, so that you can assess and determine is if looks and expected profile in BC waters should looks (and as a quick check of file import errors). From here it is simply a matter of clipping the file to the time period from vehicle launch to time the bottom was reached. The program will automatically remove any values that are above sea surface depths (in case a few of these manage to sneak in...). 

TrackMan accepts a profile contains up to 1000 data points -- if the CTD has collected more data points than this, the dataset with be sliced (evenly) to ensure that no more than 1000 data points are exported. A future improvement could be a weighted slicer that prioritized areas where the slope of the sound speed profile is steepest (i.e. areas of greatest change), which could potentially give better results.

The NDST TrackMan guide describes how to load a sound speed profile, and should be consulted for this step.
