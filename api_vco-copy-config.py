#!/usr/bin/env python3
#
# Author: vfrancadesou@vmware.com
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
#
# Script that can be used to migrate partial configuration from Profiles Business Policy and Edges Business Policies and Firewall Rules
# Only works on Policies without Object-Groups and Interface mappings or BackHaul Policies - e.g. simpler configurations
#
# The script will read the file and confirm if the Edge Source exists , if not it will exit
# Same applies for the destination edge

import os
import sys
import requests
import json
import copy
import argparse
import csv
from copy import deepcopy
######### VELO VARIABLES AND FUNCTIONS

########## VCO info and credentials
# Prefer to use OS environments to hold token variable
token = "Token %s" %(os.environ['VCO_TOKEN'])
token2 = "Token %s" %(os.environ['VCO2_TOKEN'])

VCO_FQDN=os.environ['VCO_HOSTNAME']
VCO2_FQDN=os.environ['VCO2_HOSTNAME']
vco_url = 'https://' + VCO_FQDN + '/portal/rest/'
vco2_url = 'https://' + VCO2_FQDN + '/portal/rest/'

headers = {"Content-Type": "application/json", "Authorization": token}
headers2 = {"Content-Type": "application/json", "Authorization": token2}

######## VCO API methods
get_enterprise = vco_url + 'enterprise/getEnterprise'
get_edgelist = vco_url+'enterprise/getEnterpriseEdgeList'
get_edgeconfig = vco_url + 'edge/getEdgeConfigurationStack'
get_edgeoverview = vco_url + 'enterprise/getEnterpriseEdges'
update_edgeconfig = vco_url+'configuration/updateConfigurationModule'
edge_prov = vco_url+'edge/edgeProvision'
get_profiles =vco_url + 'enterprise/getEnterpriseConfigurations'
create_profile = vco_url+'configuration/cloneEnterpriseTemplate'
insert_module = vco_url+'configuration/insertConfigurationModule'
##
######## VCO API methods
get_enterprise2 = vco2_url + 'enterprise/getEnterprise'
get_edgelist2 = vco2_url+'enterprise/getEnterpriseEdgeList'
get_edgeconfig2 = vco2_url + 'edge/getEdgeConfigurationStack'
get_edgeoverview2 = vco2_url + 'enterprise/getEnterpriseEdges'
update_edgeconfig2 = vco2_url+'configuration/updateConfigurationModule'
get_profiles2 =vco2_url + 'enterprise/getEnterpriseConfigurations'
insert_module2 = vco2_url+'configuration/insertConfigurationModule'


######## VCO FUNCTIONS

#### RETRIEVE ENTERPRISE ID for this user
def find_velo_enterpriseId():
	#Fetch enterprise id convert to JSON
	eid=0
	try:
	   enterprise = requests.post(get_enterprise, headers=headers, data='')
	except Exception as e:
	   print('Error while retrivieng Enterprise')
	   print(e)
	   sys.exit()
	ent_j = enterprise.json()
	eid=ent_j['id']
	print('Enterprise Id = %d'%(eid))
	return eid

##### Find Edge in the list
def search_name(name,listName):
    for p in listName:
        if p['name'] == name:
            return p

def find_edge_id(eid,headers,EdgeName):
	# Find Source Edge id based on Edge name in Origin VCO
	params = {'enterpriseId': eid	}
	edgesList = requests.post(get_edgelist, headers=headers, data=json.dumps(params))
	eList_dict=edgesList.json()
	length = len(eList_dict)
	#### Find Source Edge
	name=search_name(EdgeName, eList_dict)
	if (str(name)=='None'):
		print('Source Edge '+EdgeName+' not found! Stopping script')
		sys.exit(0)
	else:
		sedid = name['id']
		return (edid)

######################### Main Program #####################
#### MAIN BODY
######################### Main Program #####################

parser = argparse.ArgumentParser()
parser.add_argument("-f", "--firewall",  action='store_true', help="Option: Export Firewall Configurations",default = False)
parser.add_argument("-b", "--business", action='store_true', help="Option: Export Business Policy Configurations",default = False)
parser.add_argument("-pb", "--pbusiness", action='store_true', help="Option: Export Business Policy Configurations",default = False)
#parser.add_argument("-i", "--input", help="input file with edges info",required=True)

args = parser.parse_args()

# Find Enterprise Ids for Original and Target:
enterprise = requests.post(get_enterprise, headers=headers, data='')
ent_j = enterprise.json()
eid1=ent_j['id']
print('Enterprise1 Id = %d'%(eid1))

enterprise = requests.post(get_enterprise2, headers=headers2, data='')
ent_j = enterprise.json()
eid2=ent_j['id']
print('Enterprise2 Id = %d'%(eid2))

if args.pbusiness:
    print("Copying all Profiles to Destination VCO")
#if args.business:
#    print("Exporting Business Policy Configurations")

if(args.business):
	# Copy Edge specific Business Policy Configs
	EdgeSrcName = input("Enter Source Edge name from Origin VCO: ")
	EdgeTrgName = input("Enter Target Edge name from Destination VCO: ")

	params = {'enterpriseId': eid1	}
	edgesList = requests.post(get_edgelist, headers=headers, data=json.dumps(params))
	eList_dict=edgesList.json()
	length = len(eList_dict)
	#### Find Source Edge
	name=search_name(EdgeSrcName, eList_dict)
	if (str(name)=='None'):
		print('Source Edge '+EdgeSrcName+' not found! Stopping script')
		sys.exit(0)
	else:
		sedid = name['id']
	print ('Source Edge: '+EdgeSrcName+' found on VCO with Edge id: '+str(sedid))
    #
	# Find Target EDdge
	params = {'enterpriseId': eid2	}
	edgesList = requests.post(get_edgelist2, headers=headers2, data=json.dumps(params))
	eList_dict=edgesList.json()
	length = len(eList_dict)
	#### Find Source Edge
	name=search_name(EdgeTrgName, eList_dict)
	if (str(name)=='None'):
		print('Source Edge '+EdgeTrgName+' not found - aborting!')
		sys.exit(0)
	else:
		tedid = name['id']
	print ('Target Edge: '+EdgeTrgName+' found on VCO with Edge id: '+str(tedid))

	###### Copy Business Policy (QOS module)
		### Grab  config from Source EDGE
	moduleId=0
	params = {'edgeId': sedid}
	respj = requests.post(get_edgeconfig, headers=headers, data=json.dumps(params))
	resp=respj.json()
	edgeSpecificProfile = dict(resp[0])
	edgeSpecificProfileId=edgeSpecificProfile['id']
	for m in edgeSpecificProfile['modules']:
		if (m['name'] == 'QOS'):
			edgeSpecificProfileQOSData = m['data']
			moduleId=m['id']
			print(moduleId)
	if(moduleId==0):
			print("NO Business Policy override on Source Edge- Abort")
			sys.exit(0)

	#Find Target Edge QOS id
	#print(Edge_QOS_settings)
	T_Edge_qos_id=0
	params = {'edgeId': tedid}
	respj = requests.post(get_edgeconfig2, headers=headers2, data=json.dumps(params))
	resp=respj.json()
	edgeSpecificProfile2 = dict(resp[0])
	edgeSpecificProfileId2=edgeSpecificProfile2['id']
	for m in edgeSpecificProfile2['modules']:
		if (m['name'] == 'QOS'):
			edgeSpecificProfileQOSData2 = m['data']
			T_Edge_qos_id=m['id']

	if T_Edge_qos_id == 0:
			print('Inserting new QOS module')
			params_qos= {  "enterpriseId": eid2,  "name": "QOS",  "data": edgeSpecificProfileQOSData,  "configurationId": edgeSpecificProfileId2}
			resp = requests.post(insert_module2, headers=headers2, data=(json.dumps(params_qos)))
	else:
			print("Updating Module on Target Edge")
			d={"data":{}}
			d['data']=edgeSpecificProfileQOSData
			print(edgeSpecificProfileQOSData)
			params = {"enterpridId": eid2,"configurationModuleId" : T_Edge_qos_id,"returnData" : 'true',"_update":  d,}
			resp = requests.post(update_edgeconfig2, headers=headers2, data=(json.dumps(params)))
			print('Business Policy Rules updated on Target Edge')

###### Copy FW Rules
if(args.firewall):
	EdgeSrcName = input("Enter Source Edge name from Origin VCO: ")
	EdgeTrgName = input("Enter Target Edge name from Destination VCO: ")

	params = {'enterpriseId': eid1	}
	edgesList = requests.post(get_edgelist, headers=headers, data=json.dumps(params))
	eList_dict=edgesList.json()
	length = len(eList_dict)
	#### Find Source Edge
	name=search_name(EdgeSrcName, eList_dict)
	if (str(name)=='None'):
		print('Source Edge '+EdgeSrcName+' not found! Aborting')
		sys.exit(0)
	else:
		sedid = name['id']
	print ('Source Edge: '+EdgeSrcName+' found on VCO with Edge id: '+str(sedid))

	# Find Target EDdge
	params = {'enterpriseId': eid2	}
	edgesList = requests.post(get_edgelist2, headers=headers2, data=json.dumps(params))
	eList_dict=edgesList.json()
	length = len(eList_dict)
	#### Find Source Edge
	name=search_name(EdgeTrgName, eList_dict)
	if (str(name)=='None'):
		print('Source Edge '+EdgeTrgName+' not found - Aborting!')
		sys.exit(0)
	else:
		tedid = name['id']
	print ('Target Edge: '+EdgeTrgName+' found on VCO with Edge id: '+str(tedid))

###### Copy Business Policy (firewall module)
### Grab  config from Source EDGE
	moduleId=0
	params = {'edgeId': sedid}
	respj = requests.post(get_edgeconfig, headers=headers, data=json.dumps(params))
	resp=respj.json()
	edgeSpecificProfile = dict(resp[0])
	edgeSpecificProfileId=edgeSpecificProfile['id']
	for m in edgeSpecificProfile['modules']:
		if (m['name'] == 'firewall'):
			edgeSpecificProfilefirewallData = m['data']
			moduleId=m['id']
			print(moduleId)
	if(moduleId==0):
	    print("No Firewall Policy override on Source Edge - Aborting")
	    sys.exit(0)

	#Find Target Edge firewall id
	#print(Edge_firewall_settings)
	T_Edge_firewall_id=0
	params = {'edgeId': tedid}
	respj = requests.post(get_edgeconfig2, headers=headers2, data=json.dumps(params))
	resp=respj.json()
	edgeSpecificProfile2 = dict(resp[0])
	edgeSpecificProfileId2=edgeSpecificProfile2['id']
	for m in edgeSpecificProfile2['modules']:
	  if (m['name'] == 'firewall'):
	    edgeSpecificProfilefirewallData2 = m['data']
	    T_Edge_firewall_id=m['id']

	if T_Edge_firewall_id == 0:
	    print('Inserting new firewall module')
	    params_firewall= {  "enterpriseId": eid2,  "name": "firewall",  "data": edgeSpecificProfilefirewallData,  "configurationId": edgeSpecificProfileId2}
	    resp = requests.post(insert_module2, headers=headers2, data=(json.dumps(params_firewall)))
	else:
	    print("Updating Module on Target Edge")
	    d={"data":{}}
	    d['data']=edgeSpecificProfilefirewallData
	    params = {"enterpridId": eid2,"configurationModuleId" : T_Edge_firewall_id,"returnData" : 'true',"_update":  d,}
	    resp = requests.post(update_edgeconfig2, headers=headers2, data=(json.dumps(params)))
	    print('Firewall Policy Rules updated on Target Edge')
