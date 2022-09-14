#!/usr/bin/env/python
#
# requires a port-name.json file to be able to map strings into port numbers
#
# vco url and token must be input from os environment constant
#
# 
#

import argparse
import csv
import os
import requests
import sys
import traceback
import json

from copy import deepcopy
from ipaddress import IPv4Network

########## VCO info and credentials
# Prefer to use OS environments to hold token variable
token = "Token %s" %(os.environ['VCO_TOKEN'])
VCO_FQDN=os.environ['VCO_HOSTNAME']
vco_url = 'https://' + VCO_FQDN + '/portal/rest/'
vco_live = 'https://'+ VCO_FQDN + '/livepull/liveData'
headers = {"Content-Type": "application/json", "Authorization": token}
######## VCO API methods
get_enterprise = vco_url + 'enterprise/getEnterprise'
get_edgelist = vco_url+'enterprise/getEnterpriseEdgeList'
get_edgeconfig = vco_url + 'edge/getEdgeConfigurationStack'
update_edgeconfig = vco_url+'configuration/updateConfigurationModule'
edge_prov = vco_url+'edge/edgeProvision'
get_profiles =vco_url + 'enterprise/getEnterpriseConfigurationsPolicies'
create_profile = vco_url+'configuration/cloneEnterpriseTemplate'
getObjectGroups = vco_url+'enterprise/getObjectGroups'
updateObjectGroup = vco_url+'enterprise/updateObjectGroup'
insertObjectGroup = vco_url+'enterprise/insertObjectGroup'

objects_template={"name":"tcp-groups","description":"desc","type":"port_group","data":[],"id":1}

def find_velo_enterpriseId():
	#Fetch enterprise id convert to JSON
	eid=0
	try:
         #print(headers)
         enterprise = requests.post(get_enterprise, headers=headers, data='')

	except Exception as e:
	   print('Error while retrivieng Enterprise')
	   print(e)
	   sys.exit()
	ent_j = enterprise.json()
	#print(ent_j)
	eid=ent_j['id']
	print('Enterprise Id = %d'%(eid))
	return eid

def main():
    

#### Find Enterprise Id to which the user belongs to
    #eid = find_velo_enterpriseId()
    #eid for Esselunga
    eid=1146
    params = {'enterpriseId': eid,"type":"address_group"}
    resp = requests.post(getObjectGroups, headers=headers, data=json.dumps(params))
    vcogroups=resp.json()
    i=0
    for group in vcogroups:
                #print(group["name"])
                #print(group["data"])
                list_size=len(group["data"])
                if (list_size==1):
                      print(group["name"])
                      i=i+1
    print("number of obj-groups with single item is ",i)
if __name__ == "__main__":
    main()
