import json
import urllib2
data = {"text": "Test"}
req = urllib2.Request('http://10.1.1.4:9090/telegram')
req.add_header('Content-Type', 'application/json')
response = urllib2.urlopen(req, json.dumps(data))
