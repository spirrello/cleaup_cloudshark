#!/usr/bin/python

import time
import datetime
import json
import urllib2
import re
import requests
from datetime import datetime, timedelta

#You'll need to enter the IP or hostname of your cloudshark box.
cloudshark_host = "cloudshark.example.org"
#The API Token will also need to be specified
cloudshark_api_token = [APITOKEN]
#Delete captures older than this many days
cloudshark_days_stale = 9999
#Put the timezone that the CloudShark Appliance is in. This can be found on the Appliance Setup -> System Info page
cloudshark_timezone = '\-04:00'

def pcap_cleanup():
	  #Enter the an integer to use for the stale_date variable.  This variable indicates anything older than 7 days can be deleted from Cloudshark.
		stale_date = datetime.now() - timedelta(days = cloudshark_days_stale)
		#Need to convert the stale date into a string so we can use it for a date range in the API
		search_date = stale_date.strftime("%m/%d/%Y")

        
		try:
			pcap_list = requests.get("http://" + cloudshark_host + "/api/v1/" + cloudshark_api_token + "/search?search[date]=1/1/2000-" + search_date)
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
			upload_date = re.sub(cloudshark_timezone + '$', '', upload_date)
			upload_date = re.sub('T', ' ', upload_date)
			upload_date = datetime.strptime(upload_date, "%Y" + "-" "%m" + "-" "%d" + " " + "%H" + ":" + "%M" + ":" "%S")
		
			upload_date = upload_date.strftime("%m/%d/%Y")
			print "upload_date = %s" % (upload_date)
			upload_date = datetime.strptime(upload_date, "%m/%d/%Y")
			if upload_date < stale_date:
				time.sleep(1)
				print "%s is stale and will be deleted" % (i["id"])
				payload = {"id" : (i["id"])}
				url = 'http://' + cloudshark_host + '/api/v1/' + cloudshark_api_token + '/delete'
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
