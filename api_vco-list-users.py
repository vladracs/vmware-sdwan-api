#!/usr/bin/env python3
#
# Author: vfrancadesou@vmware.com
# vfrancad@gmail.com

# Pre-requisites:
# VMware SD-WAN Orchestrator Target
#   Orchestrator/Partner admin account and API Token
#
# Not to be considered as best practices in using VMware VCO API
# Meant to be used in Lab environments - Please test it and use at your own risk
#
# please note that VMWare API and Support team - do not guarantee this samples
# It is provided - AS IS - i.e. while we are glad to answer questions about API usage
# and behavior generally speaking, VMware cannot and do not specifically support these scripts
#
# Compatible with api v1 of the vmware sd-wan vco api
# using tokens to authenticate

import os
import sys
import requests
import json

token = "Token %s" %(os.environ['VCO_TOKEN'])
VCO_FQDN=os.environ['VCO_HOSTNAME']
vco_url = 'https://' + VCO_FQDN + '/portal/rest/'
headers = {"Content-Type": "application/json", "Authorization": token}
get_enterprises = vco_url + 'network/getNetworkEnterprises'
list_users = vco_url + 'enterprise/getEnterpriseUsers'

def main():
	enterprises = requests.post(get_enterprises, headers=headers, data='',verify=False)
	ent_dict = enterprises.json()
	userents = 0
	print('There are %d enterprises to check.  This will take approximately %d seconds' %(len(ent_dict), (len(ent_dict)/3)))
	for enterprise in ent_dict:
		eid = enterprise['id']
		params = {'enterpriseId': eid}
		userlist = requests.post(list_users, headers=headers, data=json.dumps(params),verify=False)
		result = userlist.json()
		for user in result:
			if user['roleName'] == "Enterprise Superuser":
				print('User %s (email = %s) exists in enterprise "%s" with enterprise ID %d' %(user['username'], user['email'],enterprise['name'], eid))
if __name__ == '__main__':
    main()
