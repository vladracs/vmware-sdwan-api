#!/usr/bin/env python3
#
# Author: vfrancadesou@vmware.com
# vfrancad@gmail.com

# Very simple script that leverages VMware SD-WAN Orchestrator API to:
# initiate an rma and printe activation key

# Pre-requisites:
# VMware SD-WAN Orchestrator Target
#   Enterprise admin account
#   Enterprise user and user API token
#
# usage: python3 api_vco-vce-rma.py cloudVCE-5661
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
import random
import argparse
from copy import deepcopy

######### VELO VARIABLES AND FUNCTIONS

########## VCO info and credentials
# Prefer to use OS environments to hold token variable
token = "Token %s" %(os.environ['VCO_TOKEN'])
VCO_FQDN=os.environ['VCO_HOSTNAME']
vco_url = 'https://' + VCO_FQDN + '/portal/rest/'
headers = {"Content-Type": "application/json", "Authorization": token}

######## VCO API methods
get_enterprise = vco_url + 'enterprise/getEnterprise'
get_edgelist = vco_url+'enterprise/getEnterpriseEdgeList'
get_edgeconfig = vco_url + 'edge/getEdgeConfigurationStack'
update_edgeconfig = vco_url+'configuration/updateConfigurationModule'
edge_prov = vco_url+'edge/edgeProvision'
get_profiles =vco_url + 'enterprise/getEnterpriseConfigurationsPolicies'
create_profile = vco_url+'configuration/cloneEnterpriseTemplate'
edge_rma=vco_url+'edge/edgeRequestReactivation'
edge_cancel_rma=vco_url+'edge/edgeCancelReactivation'
#######
######## VCO FUNCTIONS
#######

#### RETRIEVE ENTERPRISE ID for this user
def find_velo_enterpriseId():
    #Fetch enterprise id convert to JSON
    eid=0
    resp = requests.post(get_enterprise, headers=headers, data='')
    ent_j = resp.json()
    eid=ent_j['id']
    print('Enterprise Id = %d'%(eid))
    return eid
##### Find Edge in the list
def search_name(name,listName):
    for p in listName:
        if p['name'] == name:
            return p
######################### Main Program #####################
def main():
        parser = argparse.ArgumentParser()
        parser.add_argument("SEdge", help="Source Edge Name")
        args = parser.parse_args()
        eid = find_velo_enterpriseId()
        EdgeName=args.SEdge
        # Find Source Edge id based on Edge name
        params = {'enterpriseId': eid	}
        edgesList = requests.post(get_edgelist, headers=headers, data=json.dumps(params))
        eList_dict=edgesList.json()
        length = len(eList_dict)
        #### Find Source Edge
        name=search_name(EdgeName, eList_dict)
        #print(name)
        if (str(name)=='None'):
        	print('Source Edge '+EdgeName+' not found!')
        	go=False
        	while go==False:
        		a = input("Enter [yes/no] to continue: ").lower()
        		if a=="yes":
        			go=True
        			continue
        		elif a=="no":
        			sys.exit(0)
        		else:
        			print("Enter either yes/no: ")
        else:
        	edid = name['id']
        	print ('Source Edge: '+EdgeName+' found on VCO with Edge id: '+str(edid))

        params={'edgeId':edid}
        resp = requests.post(edge_cancel_rma, headers=headers, data=json.dumps(params))
        params={'edgeId':edid,'revokeCertificate':False}
        resp = requests.post(edge_rma, headers=headers, data=json.dumps(params))
        print(resp.json())
if __name__ == "__main__":
    main()
