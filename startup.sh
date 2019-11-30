#sudo ifconfig wlan1 down
#sudo iwconfig wlan1 mode monitor
#sudo ifconfig wlan1 up
#sudo touch /home/pi/capture.pcap
#sudo chown pi:pi /home/pi/capture.pcap
#sudo chmod a+rw /home/pi/capture.pcap
#sudo tshark -i wlan1 -w /home/pi/capture.pcap

#touch /home/pi/StartupFileCreationTest
#sudo wpa_supplicant -B -i wlan0 -c /home/pi/wpa_supplicant_hotspot.conf
sudo bash /home/pi/wifi-connect.sh /home/pi/wpa_supplicant_hotspot.conf
