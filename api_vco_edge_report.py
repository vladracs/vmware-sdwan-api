#!/usr/bin/env python3
#
# Simple Python Script that uses vmware sd-wan orchestrator api read all vmware sd-wan edge addresses
# Not to be considered as best practices in using VMware VCO API
# Meant to be used in Lab environments - Please test it and use at your own risk
#
# please note that VMWare API and Support team - do not guarantee this samples
# It is provided - AS IS - i.e. while we are glad to answer questions about API usage
# and behavior generally speaking, VMware cannot and do not specifically support these scripts
#author: Vladimir F de Sousa vfrancadesou@vmware.com
# vfrancad@gmail.com

import os
import sys
import requests
import json
from copy import deepcopy
import argparse

########## VCO info and credentials
token = "Token %s" %(os.environ['VCO_TOKEN'])
vco_url = 'https://' + os.environ['VCO_HOSTNAME'] + '/portal/rest/'
headers = {"Content-Type": "application/json", "Authorization": token}
######## VCO API methods
get_enterprise = vco_url + 'enterprise/getEnterprise'
get_edgelist = vco_url+'enterprise/getEnterpriseEdgeList'
get_edgeconfig = vco_url + 'edge/getEdgeConfigurationStack'
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
def main():
 eid = find_velo_enterpriseId()
 params = {'enterpriseId': eid}
 edgesList = requests.post(get_edgelist, headers=headers, data=json.dumps(params))
 eList_dict=edgesList.json()
 length = len(eList_dict)
 i=0
 while i < length:
  EdgeId = eList_dict[i]['id']
  print (' '+eList_dict[i]['name']+' id: '+str(EdgeId)+':')
  print(' ')
  params = {'edgeId': EdgeId}
  respj = requests.post(get_edgeconfig, headers=headers, data=json.dumps(params))
  resp=respj.json()
  edgeSpecificProfile = dict(resp[0])
  edgeSpecificProfileDeviceSettings = [m for m in edgeSpecificProfile['modules'] if m['name'] == 'deviceSettings'][0]
  edgeSpecificProfileDeviceSettingsData = edgeSpecificProfileDeviceSettings['data']
  moduleId = edgeSpecificProfileDeviceSettings['id']
  routedInterfaces = edgeSpecificProfileDeviceSettingsData['routedInterfaces']
  for iface in routedInterfaces:
   if(str(iface['addressing']['type'])=='DHCP'):
    print(' -'+str(iface['name'])+' IPv4 '+str(iface['addressing']['type']))
   else:
    print(' -'+str(iface['name'])+' '+str(iface['addressing']['type'])+' IPv4: '+str(iface['addressing']['cidrIp'])+'/'+str(iface['addressing']['cidrPrefix']))
   if(str(iface['v6Detail']['addressing']['type'])=='DHCP_STATELESS'):
    print(' -'+str(iface['name'])+' IPv6 '+str(iface['v6Detail']['addressing']['type']))
   else:
    print(' -'+str(iface['name'])+' '+str(iface['v6Detail']['addressing']['type'])+' IPv6: '+str(iface['v6Detail']['addressing']['cidrIp'])+'/'+str(iface['v6Detail']['addressing']['cidrPrefix']))
  VlansNetworks = edgeSpecificProfileDeviceSettingsData['lan']['networks']
  length2 = len(VlansNetworks)
  h=0
  while h < length2:
	  print(' -Vlan '+str(VlansNetworks[h]['vlanId'])+' IPv4: '+str(VlansNetworks[h]['cidrIp'])+str(VlansNetworks[h]['cidrPrefix']))
	  h+=1
  i+=1
if __name__ == "__main__":
        main()
