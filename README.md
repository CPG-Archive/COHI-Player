# COHI-Player for STEMlab
This branch contains the last stable version. 

COHI-Player is an application which controls playback of broadband RF signals when using a [STEMLAB125-14](https://redpitaya.com/de/stemlab-125-14/) by Red Pitaya . Main purpose is generating AM radio bands like LW, MW, SW, VLF in the context of [COHIRADIA](https://www.radiomuseum.org/dsp_cohiradia.cfm). While recording the data is stored in IQ data files with 32 bit per sample (2 x 16 bits complex) and carries an extended wav-header in the standard format used for most software defined radios (SDR).

The COHI-Player does not need any manual interaction for loading or starting the playback of a spectrum file. It starts automatically to play all spectrum wav files stored on an USB stick or any internal directory. Thus, it is an ideal source to simulate antenna signals for historic radio receivers in large collections or museums.

The COHI-Player searches automatically for any STEMlab board in the network. It works both in an DHCP controlled complex as well in a standalone configuration using fixed IP addressing or a linked local configuration.

Appropriate recordings can be played back on historic Radio receivers with external antenna jack and all transmitters active at the time of the recording can then be tuned through and listened to on the radio. Detailed information for installation, hardware setup and an archive with many recordings from 2006 on can be found on [COHIRADIA](https://www.cohiradia.org/).

# Installation: 

## Using Linux OS on RaspberryPi (version 4 or 5): 

1) preferred OS is Raspberry Pi OS based on Debian Trixie, user name shall be named 'pi'
2) Python is already installed on your OS
3) clone this repository from GITHUB to your preferred folder, e. g. `COHIRADIA`
4) since there are problems with venv virtual environment and the required libs, a global install of the required packages is needed:
```bash
sudo apt install python3-numpy python3-yaml python3-matplotlib python3-pyqt5 python3-pyqtgraph python3-pandas python3-soundfile python3-paramiko
```
5) adjust the configuration file 'config_sdr.yaml' if needed
```bash
address: 192.168.178.96
filename: /media/pi
filename2: /home/pi/COHIRADIA/WAV
shutdown: false
autovol: 1
```
Explanation:

`address`: IP address of STEMlab board, must be correct for fixed IP configuration mode, otherwise will be updated automatically with first found STEMlab in the network

`filename`: put here the highest directory where COHI-Player shall search for spectrum wav files which can also be located in any subfolder beyond, recommendation: use the USB directory /media/pi

`filename2`: second option for a high-level directory where COHI-Player shall search for spectrum wav files which can also be located in any subfolder beyond, recommendation: use a directory in the SD card, e. g.  directory /home/pi/COHIRADIA/WAV

`shutdown`: definition of the actions after pressing the 'shutdown' button: true: both the STEMlab and the RaspberryPi will be shut down, false only STEMlab will be shut down

`autovol`: level adjust for the wav file

6) run COHI-Player with
```bash
python3 main.py
```
There are fully configured images (OS and COHI-Player) for usage with Raspberry Pi 4/5 and attached 3.5" display board and Raspberry Pi 5 with 7" display on [COHIRADIA](https://www.cohiradia.org/de/docs/getting_started/installation/raspberry-pi-stemlab-linux-cohi-player-mini/).
  

## Using Linux OS or Windows on PC:

1) install Python v3.14 on your PC (development is being done with v3.14.2); the COHI-Player or some of its components may fail with other versions
2) clone the repository from GITHUB to your PC to a folder, say `COHIRADIA`
3) change to this folder
4) create a virtual environment with
```bash
python –m venv venv
```
5) activate the venv by
```bash
venv/Scripts/activate
```
6) install the required packages from the requirements.txt (in `COHIRADIA`) file by typing
```bash
pip install -r requirements.txt
```
7) change dir to `COHIRADIA`/sources
8) in case of using COHI-Player in Windows environment, the attributes 'filename' and 'filename2' in the file 'config_sdr.yaml' must be set to valid directories in Windows notation
9) run the main script:
```bash
python maín.py
```

## Operation of COHI-Player:

The operation of COHI-Player is very simple and almost self-explaining:

![main01](https://github.com/CPG-Archive/COHI-Player/blob/master/www/COHI-Player.jpg)

After starting, the COHI-Player starts immediately with playing the first spectrum file found in the directories indicated by parameter 'filename' and 'filename2'. All valid spectrum files are queued up and will be played endlessly according to their ascending order of their directory/filename. Spectrum files can be either segmented in 2 GB pieces or be combined in one larger file. In any case, the filename of large one file spectrum or the first part of any file sequence must be named as [any name]_0.wav.

Thus, it is possible to operate COHI-Player without any manual interaction. In case you want to navigate thru the currently played file you can use the timing slider. The button 'Restart' jumps to the beginning of the currently playing file. with 'Pause' and 'Continue' you can interrupt or restart the playback at any time.

Pressing the 'Shutdown' button will either shutdown only the Stemlab board or both the STEMlab and the Raspberry Pi depending on the configuration in the 'config_sdr.yaml'.
