from globals import *

def downloadQualityURL(url, outFile):
	DOWNLOAD_OPTIONS = " --load-cookies=cookies.txt --log='" + outFile + "_download.log' --log-level=notice --http-accept-gzip=true --quiet=true --retry-wait=1 --max-file-not-found=5 --max-tries=5 --header='Accept: */*' --header='Accept-Language: en-US,en;q=0.8' --header='Origin: https://www.nhl.com' -U='Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.97 Safari/537.36' --enable-http-pipelining=true --auto-file-renaming=false --allow-overwrite=true "

	# Pull url_root
	url_root = re.match('(.*)master_tablet60.m3u8',url, re.M|re.I).group(1)

	# Erase the old master m3u8 files
	command = 'rm temp/master.m3u8'
	subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True).wait()

	# Get the master m3u8
	command = 'aria2c -o temp/master.m3u8' + DOWNLOAD_OPTIONS + url
	subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True).wait()

	# Parse the master and get the quality URL
	command = 'cat ./temp/master.m3u8'
	p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
	pi = iter(p.stdout.readline, b'')
	quality_url = ''
	for line in pi:
		if(QUALITY + 'K' in line):
			quality_url = url_root + line
		if(quality_url == ''):
			quality_url = url_root + line

	# Remove the line break and change http to hls
	quality_url = quality_url[:-1]
	quality_url = quality_url.replace('http://', 'hls://')

	return quality_url

def create_directories():
	# Create a temp directory
	command = 'mkdir ./temp'
	subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True).wait()


def download_nhl(url, outFile):	
	# Create directories
	create_directories()

	# Pull the quality url
	quality_url = downloadQualityURL(url, outFile)

	tprint("Downloading stream...")

	# Construct the livestream command
	command = 'livestreamer '
	command = command + str(quality_url) + ' best'
	command = command + " --hls-live-edge 60"
	command = command + " --hls-segment-threads 10"
	command = command + " --retry-open 200"
	command = command + " --retry-streams 1"
	command = command + " --http-no-ssl-verify"
	command = command + " --ringbuffer-size 128M"
	command = command + " --hls-timeout 120"
	command = command + " --hls-segment-attempts 40"
	command = command + " --http-timeout 120"
	command = command + ' --http-header User-Agent="' + UA_PS4 + '"'

	# Add cookies
	cj = cookielib.LWPCookieJar('cookies.lwp')
	cj.load('cookies.lwp',ignore_discard=False)
	for cookie in cj:
		command = command + " --http-cookie " + str(cookie.name) + "=" + str(cookie.value)
	
	# Add output file
	command = command + " --output " + outFile

	# Add the log pipe
	command = command + " &> ./logs/" + outFile + '.log'
	subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True).wait()
	return
