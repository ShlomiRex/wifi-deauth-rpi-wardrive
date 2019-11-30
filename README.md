Setup crontab with:
$ crontab -e

put this line:

@reboot bash /home/pi/startup.sh

in order to run a script on startup.