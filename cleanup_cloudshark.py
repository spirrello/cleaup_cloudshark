#!/usr/bin/python

import time
import datetime
import json
import urllib2
import re
import requests
from datetime import datetime, timedelta

#You'll need to enter the IP of your cloudshark box where it's noted as [IPADDRESS].
#The API Token will also need to be replaced where you see [APITOKEN]


def pcap_cleanup():
		stale_date = datetime.now() - timedelta(days = 7)
		#Need to convert the stale date into a string so we can use it for a date range in the API
		search_date = stale_date.strftime("%m/%d/%Y")

        
		try:
			pcap_list = requests.get("http://[IPADDRESS]/api/v1/[APITOKEN]/search?search[date]=1/1/2000-" + search_date)
		except IOError as e:
			print e
			print "Sleeping for 60 seconds...API call failed for some reason"
			time.sleep(60)
			return "FAILED"

        
		pcap_dictionary = pcap_list.json()
		pcap_list = pcap_dictionary["captures"]

		print len(pcap_list)
		if len(pcap_list) == 0:
			print "No stale captures....sleeping for 60 seconds"
			time.sleep(60)



		for i in pcap_list:
			print "Will start in 5 seconds to evaluate the next file...."
			
			print i["id"] + ":" + i["created_at"]
			upload_date = i["created_at"]
			#The following removes the GMT difference from the upload date otherwise the date of the upload can't be compared versus the age.
			#You'll need to modify the removal of the timezone to suite your needs.
			upload_date = re.sub('\-05:00$', '', upload_date)
			upload_date = re.sub('T', ' ', upload_date)
			upload_date = datetime.strptime(upload_date, "%Y" + "-" "%m" + "-" "%d" + " " + "%H" + ":" + "%M" + ":" "%S") # + "-" + "%I" + ":" + "%S")
		
			upload_date = upload_date.strftime("%m/%d/%Y")
			print "upload_date = %s" % (upload_date)
			upload_date = datetime.strptime(upload_date, "%m/%d/%Y")
			if upload_date < stale_date:
				time.sleep(1)
				print "%s is stale and will be deleted" % (i["id"])
				payload = {"id" : (i["id"])}
				url = 'http://[IPADDRESS]/api/v1/[APITOKEN]/delete'
				headers = {'content-type': 'application/json'}
				response = requests.post(url, data=json.dumps(payload), headers=headers)
				print response
			
			else:
				print "%s is relatively new" % (i["id"])

print "calling my function now...."

while True:
	try:
		pcap_cleanup()

	except IOError as e:
		print e
