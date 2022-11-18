#!/usr/bin/env python3
#
# Simple Python Script that uses vmware sd-wan orchestrator api read OFC route table
#
# usage: python3 api_vco_grab_ofc_routes -r 500
#
# Not to be considered as best practices in using VMware VCO API
# Meant to be used in Lab environments - Please test it and use at your own risk
#
# please note that VMWare API and Support team - do not guarantee this samples
# It is provided - AS IS - i.e. while I am glad to answer questions about API usage
# and behavior generally speaking, VMware/me cannot and do not specifically support these scripts
#
# Compatible with api v1 of the vmware sd-wan vco api
# using tokens to authenticate
# author: Vladimir F de Sousa vfrancadesou@vmware.com

import argparse
import json
import os
import sys
from copy import deepcopy

import requests

########## VCO info and credentials
token = "Token %s" %(os.environ['VCO_TOKEN'])
vco_url = 'https://' + os.environ['VCO_HOSTNAME'] + '/portal/rest/'
headers = {"Content-Type": "application/json", "Authorization": token}
######## VCO API methods
get_edge = vco_url + 'edge/getEdge'
get_enterprise = vco_url + 'enterprise/getEnterprise'
get_ofclist = vco_url+'enterprise/getEnterpriseRouteTable'
######## VCO FUNCTIONS
#### RETRIEVE ENTERPRISE ID for this user
def find_velo_enterpriseId():
	#Fetch enterprise id convert to JSON
	eid=0
	enterprise = requests.post(get_enterprise, headers=headers, data='')
	ent_j = enterprise.json()
	eid=ent_j['id']
	print('Enterprise Id = %d'%(eid))
	return eid
######################### Main Program #####################
#### MAIN BODY
######################### Main Program #####################
parser = argparse.ArgumentParser()
parser.add_argument("-r", "--routes", type=int,help="Number of Routes to be Displayed",required=True)
args = parser.parse_args()
n_of_routes=args.routes
eid = find_velo_enterpriseId()
params = {'filter':{'limit':n_of_routes,'rules':[]},'enterpriseId': eid}
response = requests.post(get_ofclist, headers=headers, data=json.dumps(params))
resp_dict=response.json()
print(resp_dict["subnets"])
