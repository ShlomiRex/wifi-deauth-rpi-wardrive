FILENAME=$1
sudo killall wpa_supplicant
sudo wpa_supplicant -B -i wlan0 -c $FILENAME
