from globals import *
from random import randint


def padding(input):
	tprint("Adding some padding to " + input + ".")
	
	# Generate ffprobe json
	command = "ffprobe -v quiet -print_format json -show_format -show_streams " + input + " > " + input + ".json"
	subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True).wait()

	# Load the json
	vidProbeJSON = None
	with open(input + ".json", "r") as file:
		vidProbeJSON = json.load(file)
	file.close()

	# Get Duration from JSON
	duration = float(vidProbeJSON['format']['duration'])

	# Set target duration to 4 hours +/- 25%
	targetDuration = 15000 * (randint(75,125)/float(100))

	# Cut out a 30 min chunk of video
	command = 'ffmpeg -y -nostats -i ' + input + ' -t ' + str(30 * 60) + ' -c:v copy -c:a copy 30min_' + input
	subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True).wait()

	# Figure out how many 30 min chunks we need to add
	duration_diff = int((targetDuration - duration) / (30*60) + 0.5)

	# If the duration diff is greater than 0 then add to the video
	if(duration_diff > 0):
		# Create file list
		file = open("concat_list.txt", "w")
		file.write("file\t" + input + '\n')
		for i in range(1,duration_diff):
			tprint("Adding 30min of padding...")
			file.write("file\t" + '30min_' + input + '\n')
		file.close()

		# Run the concat
		command = 'ffmpeg -y -nostats -f concat -i concat_list.txt -c copy temp_' + input
		subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True).wait()

		# Clean Up
		command = 'mv temp_' + input + ' ' + input
		subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
		command = 'rm -f concat_list.txt'
		subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
	
	# More clean up
	command = 'rm -f 30min_' + input
	subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
	command = 'rm -f ' + input + '.json'
	subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)