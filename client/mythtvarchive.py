"""
   :synopsis: MythTV Archive Server Client Script
   :copyright: 2014 Nathan Lewis, See LICENSE.txt
.. moduleauthor:: Nathan Lewis <natewlew@gmail.com>

"""

#!/usr/bin/python

server = '' # Archive Server IP
port = '7080' # Archive Server Port
quality = 'Universal' # Quality Setting. Handbrake preset. Default: Universal

import sys
import xmlrpclib

def log(value):
    sys.stdout.write(value)


chan_id = sys.argv[1] # %CHANID%
start_time = sys.argv[2] # %STARTTIMEISOUTC%

server_url = 'http://%s:%s/' % (server, port)
s = xmlrpclib.Server(server_url)

result = s.archive(chan_id, start_time, quality)

try:
    success = result['success']
    message = result['message']
    log(result['message'])
except (KeyError, TypeError):
    log('Server Response Error')
    sys.exit(1)

if success is True:
    sys.exit(0)
else:
    sys.exit(1)