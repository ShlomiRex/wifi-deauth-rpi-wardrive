IFACE=$1    #Interface (wlan1 usually - your monitor card)
FILENAME=$2 #This is wpa_supplicant conf file

if [ $# -ne 2 ]
then
	echo "Argument 1 is interface"
	echo "Argument 2 is filename (wpa_supplicant.conf)"
	exit 1
fi

sudo rm /var/run/wpa_supplicant/$IFACE
sudo wpa_supplicant -B -i $IFACE -c $FILENAME
