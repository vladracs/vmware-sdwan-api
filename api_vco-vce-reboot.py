#!/usr/bin/env python3
#
# Author: vfrancadesou@vmware.com

# Very simple script that leverages VMware SD-WAN Orchestrator API
# to reboot a VCE

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
import time
from copy import deepcopy

######### VELO VARIABLES AND FUNCTIONS

########## VCO info and credentials
# Prefer to use OS environments to hold token variable
token = "Token %s" %(os.environ['VCO_TOKEN'])
VCO_FQDN=os.environ['VCO_HOSTNAME']
vco_url = 'https://' + VCO_FQDN + '/portal/rest/'
vco_live = 'https://'+ VCO_FQDN + '/livepull/liveData'
headers = {"Content-Type": "application/json", "Authorization": token}

###
######## VCO API methods
get_enterprise = vco_url + 'enterprise/getEnterprise'
get_edgelist = vco_url+'enterprise/getEnterpriseEdgeList'
get_edgeconfig = vco_url + 'edge/getEdgeConfigurationStack'
update_edgeconfig = vco_url+'configuration/updateConfigurationModule'
edge_prov = vco_url+'edge/edgeProvision'
get_profiles =vco_url + 'enterprise/getEnterpriseConfigurationsPolicies'
create_profile = vco_url+'configuration/cloneEnterpriseTemplate'
enter_live = vco_url+'liveMode/enterLiveMode'
########
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
def send_reboot(edid):
        # get email first
        print('Entering Live Mode')
        params = {'edgeId': edid}
        live = requests.post(enter_live, headers=headers, data=json.dumps(params))
        live_j = live.json()
        token=live_j['token']
        #print(token)
        params2 = {"jsonrpc":"2.0","method":"liveMode/requestLiveActions","params":{"token":token,"actions":[{"action":"reboot","parameters":{}}]},"id":1}
        #print(params2)
        time.sleep(5)
        sent = requests.post(vco_live, headers=headers, data=json.dumps(params2))
        print(sent.json())
        print('Sending Reboot request to Edge ')
######################### Main Program #####################
def main():
        parser = argparse.ArgumentParser()
        parser.add_argument("SEdge", help="Edge Name")
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
        	print('Target Edge '+EdgeName+' not found!')
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
        	print ('Target Edge: '+EdgeName+' found on VCO with Edge id: '+str(edid))
        send_reboot(edid)
if __name__ == "__main__":
    main()
