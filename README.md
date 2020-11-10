Wouldn't is be awesome to de-authenticate all those pesky people from public/private network? Then this repo is for you.

# What is this
Deauthenticate all networks with raspberry pi zero w with minimal effort

Just run 1 command and put raspberry pi zero w in your backpack and the raspberry pi won't stop de-authenticating.

When you get further away from WiFi AP, the script will adjust the best network target to de-authenticate.

The script also saves information about Access Points you visited in your travels as CSV so you can later at home analyze all MAC's, ESSID's, and more.

# How

When raspberry pi zero w is booting, and ready, it executes the first script: `startup.sh`. Setup cronjob below.

This connects the raspberry pi to pre-determined network (for example, your phone hotspot). This allows to SSH into the raspberry pi from your phone. Just open hotspot, change the wpa_supplicant configuration file, and the raspberry pi will connect to it on each startup.

The reason that you need to SSH to raspberry pi zero w instead of just running the attack right away, is that, you travel, you don't have keyboard, mouse, or display. You may want to give the attack diffirent parameters or other scripts. You can't know for sure if the attack succeeded or even if the raspberry pi works. So, SSH into it.

You can SSH into raspberry pi without knowing the IP: you can type the `hostname` of it, example: `$ ssh pi@raspberrypi`. You can change the hostname with `$ sudo raspi-config` and choose `Network Options` and `Change hostname`.

After SSH you just type: `$ sudo python3 attack.py` to run the attack. Enjoy!

You need to create a folder called "dump" where the AP data can be stored.

# What you need

* 1 raspberry pi
* 1 wifi adapter capable of monitor mode, such as Alfa series
* (Optional) External battery to power the pi

# Setup cronjob

Setup crontab with:
`$ crontab -e`

put this line:

`$ @reboot bash /home/pi/startup.sh`

in order to run a script on startup.
