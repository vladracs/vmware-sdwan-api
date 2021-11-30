#!/usr/bin/env python3
#
# Author: vfrancadesou@vmware.com
# vfrancad@gmail.com

# Very simple script that leverages VMware SD-WAN Orchestrator API to:
# provision a new profile and a new virtual vmware sd-wan edge (VCE)

# It will change the edge device settings to be compatible with cloud deployments
# vlan1 ip, ge1, ge2 as routed with public auto overlay

# Pre-requisites:
# VMware SD-WAN:
# Orchestrator Target
# Enterprise admin account
# Enterprise user and user VCO API token

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
from copy import deepcopy

######### VELO VARIABLES AND FUNCTIONS

########## VCO info and credentials
# Prefer to use OS environments to hold token variable
token = "Token %s" %(os.environ['VCO_TOKEN'])
VCO_FQDN=os.environ['VCO_HOSTNAME']
vco_url = 'https://' + VCO_FQDN + '/portal/rest/'
headers = {"Content-Type": "application/json", "Authorization": token}
ProfileName='CLOUD-PROFILE'
EdgeName='cloudVCE-'+str(random.randint(1,10000))
EdgeContactName='Vladimir'
EdgeContactEmail='vfrancadesou-aws@vmware.com'

### EDGE contact information
site={
      "contactName": EdgeContactName,
      "contactEmail": EdgeContactEmail,
            "streetAddress": None,
      "streetAddress2": None,
      "city": None,
      "state": None,
      "postalCode": None,
      "country": None,
      "lat": None,
      "lon": None,
      "timezone": None,
      "locale": None,
      "shippingSameAsLocation": 1,
      "shippingContactName": None,
      "shippingAddress": None,
      "shippingAddress2": None,
      "shippingCity": None,
      "shippingState": None,
      "shippingPostalCode": None,
      "shippingCountry": None,
       "modified": None
    }
######## VCO API methods
get_enterprise = vco_url + 'enterprise/getEnterprise'
get_edgelist = vco_url+'enterprise/getEnterpriseEdgeList'
get_edgeconfig = vco_url + 'edge/getEdgeConfigurationStack'
update_edgeconfig = vco_url+'configuration/updateConfigurationModule'
edge_prov = vco_url+'edge/edgeProvision'
get_profiles =vco_url + 'enterprise/getEnterpriseConfigurationsPolicies'
create_profile = vco_url+'configuration/cloneEnterpriseTemplate'

#######
######## VCO FUNCTIONS
#######

#### RETRIEVE ENTERPRISE ID for this user
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
	eid=ent_j['id']
	print('Enterprise Id = %d'%(eid))
	return eid

#### CREATE NEW VMWARE SD-WAN CONFIGURATION PROFILE

def create_velo_profile(eid,ProfileName):
 pid=0
### Confirm existing profile names, if "AWS-PROFILE" not found, create a new profile
 params = {	}
 try:
         profile = requests.post(get_profiles, headers=headers, data=json.dumps(params))
         #print(profile.json())
 except Exception as e:
	   print('error getting profiles')
	   print(e)
	   sys.exit()
 prof_dict = profile.json()
 for p in prof_dict:
    if p['name'].lower() == ProfileName.lower():
     print('found')
     print ('Profile named '+ProfileName+' already found on VCO '+VCO_FQDN+' with Profile id: '+str(p['id']))
     return p['id']

 if(pid==0):
		#Provision new Profile and grab its id
		 params = {"id" : eid,"name":ProfileName}
		 print('Profile not found, creating new one')
		 profile_resp = requests.post(create_profile, headers=headers, data=json.dumps(params))
		 prof_dict=profile_resp.json()

		 pid = prof_dict['id']
		 print('New Profile named '+ProfileName+' created with Id = %d'%(pid))
		 return pid

#### PROVISION NEW VMWARE SD-WAN EDGE
def provision_velo_edge(eid,pid,EdgeName,site):
	#### Provision new virtual edge in the AWS Profile
	#Provision new Profile and grab its id
	rEdgeName=EdgeName
	params = {'id' : eid,'name':rEdgeName,'modelNumber': 'virtual','configurationId': pid,'site': site}
	edid = requests.post(edge_prov, headers=headers, data=json.dumps(params))
	edid_j = edid.json()
	edid=edid_j['id']
	activationkey=edid_j['activationKey']
	print('New Edge named '+rEdgeName+' created with Id '+str(edid)+' and activation key '+activationkey)
	return [edid,activationkey]

def change_edge_config(eid,edid):
    ### Grab Edge Device Settings
    params = {'edgeId': edid}
    respj = requests.post(get_edgeconfig, headers=headers, data=json.dumps(params))
    resp=respj.json()
    edgeSpecificProfile = dict(resp[0])
    edgeSpecificProfileDeviceSettings = [m for m in edgeSpecificProfile['modules'] if m['name'] == 'deviceSettings'][0]
    edgeSpecificProfileDeviceSettingsData = edgeSpecificProfileDeviceSettings['data']
    moduleId = edgeSpecificProfileDeviceSettings['id']
    ### Adding an IP on Vlan 1
    edgeSpecificProfileDeviceSettingsData['lan']['networks'][0]['cidrIp'] = '127.0.0.10'
    edgeSpecificProfileDeviceSettingsData['lan']['networks'][0]['advertise'] = False
    edgeSpecificProfileDeviceSettingsData['lan']['networks'][0]['cidrPrefix'] = '30'
    edgeSpecificProfileDeviceSettingsData['lan']['networks'][0]['netmask'] = '255.255.255.252'
    edgeSpecificProfileDeviceSettingsData['lan']['networks'][0]['dhcp']['enabled'] = False
# Changing GE1-3 defaults
    routedInterfaces = edgeSpecificProfileDeviceSettingsData['routedInterfaces']
    interface={"name":"GE"}
    routedInterfaces.insert(0,interface)
    routedInterfaces.insert(1,interface)
    routedInterfaces[0]=deepcopy(routedInterfaces[2])
    routedInterfaces[1]=deepcopy(routedInterfaces[2])
    routedInterfaces[0]['name'] = 'GE1'
    routedInterfaces[1]['name'] = 'GE2'
    for iface in routedInterfaces:
        if iface['name'] == 'GE1':
            iface['override'] = True
            iface['advertise'] = True
            iface['natDirect'] = False
            iface['wanOverlay'] = 'DISABLED'
        if iface['name'] == 'GE2':
            iface['override'] = True
            iface['advertise'] = False
            iface['natDirect'] = True
            iface['wanOverlay'] = 'AUTO_DISCOVERED'
        if iface['name'] == 'GE3':
            iface['override'] = True
            iface['advertise'] = True
            iface['natDirect'] = False
            iface['wanOverlay'] = 'DISABLED'
    edgeSpecificProfileDeviceSettingsData['routedInterfaces']=deepcopy(routedInterfaces)
    testResponse = {}
    testResponse['data'] = edgeSpecificProfileDeviceSettingsData
########### Change VCE device settings so it matches AWS cloudformation
    params3 = {
    "id" : moduleId,
    "returnData" : 'true',
    "_update":  testResponse,
    "name":"deviceSettings"}
    resp = requests.post(update_edgeconfig, headers=headers, data=(json.dumps(params3)))
    respo_j=resp.json()
######################### Main Program #####################
def main():
        eid = find_velo_enterpriseId()
        pid = create_velo_profile(eid,ProfileName)
        new_edge_l = provision_velo_edge(eid,pid,EdgeName,site)
        edid=new_edge_l[0]
        activationkey=new_edge_l[1]
        change_edge_config(eid,edid)
if __name__ == "__main__":
    main()
