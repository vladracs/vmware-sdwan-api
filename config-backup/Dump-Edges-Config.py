#!/usr/bin/env python3
#
# Simple Python Script to dump Edges Configuration
# 
# usage: python3 api_vco_grab_ofc_routes -e Customer1 -r 500
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

import requests
import json
import copy
import time
import argparse
import json
import os
import sys
import urllib.request
import urllib.response
from copy import deepcopy

import requests

########## VCO info and credentials
token = "Token %s" %(os.environ['VCO_TOKEN'])
vco_domain = 'https://' + os.environ['VCO_HOSTNAME']
vco_url = 'https://' + os.environ['VCO_HOSTNAME'] + '/portal/rest/'
headers = {"Content-Type": "application/json", "Authorization": token}
######## VCO API methods
get_edge = vco_url + 'edge/getEdge'
get_enterprise = vco_url + 'enterprise/getEnterprise'
get_enterprise_operator = vco_url + 'network/getNetworkEnterprises'
get_enterprises = vco_url + 'enterpriseProxy/getEnterpriseProxyEnterprises'
get_ofclist = vco_url+'enterprise/getEnterpriseRouteTable'
get_ent = vco_url+'enterpriseProxy/getEnterpriseProxy'
get_Edges = vco_url+'enterprise/getEnterpriseConfigurations'
get_Edge_configuration = vco_url+'configuration/getConfiguration'
get_edge_list = vco_url+'enterprise/getEnterpriseEdgeList'
get_edge_configuration = vco_url+'edge/getEdgeConfigurationStack'
######## VCO FUNCTIONS
#### RETRIEVE ENTERPRISE ID for this user
def find_velo_enterpriseId():
	#Fetch enterprise id convert to JSON
	eid=0
	enterprise = requests.post(get_enterprise, headers=headers, data='',verify=False)
	ent_j = enterprise.json()
	eid=ent_j['id']
	print('Enterprise Id = %d'%(eid))
	return eid
#### RETRIEVE ENTERPRISE ID for this customer (as a partner user)
def find_customer_enterpriseId(customer):
	#Fetch enterprise id convert to JSON
    eid=0
    enterprises = requests.post(get_enterprises, headers=headers, data='')
    ent_dict = enterprises.json()
    for enterprise in ent_dict:
        print (enterprise)
        if(enterprise['name']==customer):
            eid=enterprise['id']
    print('Enterprise Id = %d'%(eid))
    return eid
#### RETRIEVE ENTERPRISE ID for a customer  (as operator user)
def op_find_customer_enterpriseId(customer):
	#Fetch enterprise id convert to JSON
    eid=0
    enterprises = requests.post(get_enterprise_operator, headers=headers, data='')
    ent_dict = enterprises.json()
    for enterprise in ent_dict:
          if(enterprise['name']==customer):
            eid=enterprise['id']
    print('Enterprise Id = %d'%(eid))
    return eid
######################### Main Program #####################
#### MAIN BODY
######################### Main Program #####################
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--operator", type=str,help="Call API as operator user",required=False)
    parser.add_argument("-p", "--partner", type=str,help="Call API as partner user",required=False)
    parser.add_argument("-e", "--enterprise", type=str,help="Name of Customer",required=True)
    args = parser.parse_args()
    customer=args.enterprise
    partner=args.partner
    operator=args.operator
    #basic access test to VCO (confirm https to the vco name works - fw rules, dns , etc)
    
    code=urllib.request.urlopen(vco_domain).getcode()
    if(code==200): print("HTTPs access to VCO working")
    else: 
         print("Issues access VCO website - Connectivity Troubleshooting Needed")
         sys.exit()
    #Test if token / api access is working
    api_ok=False
    print("Testing if token / api access is working")
    
    if (operator):    
                method=get_enterprise_operator
    elif (partner):
                method=get_enterprises
    else:
                method=get_enterprise
    
    response=requests.post(method, headers=headers, data='')
    if response.status_code == 200:
    # Parse the JSON content of the response
        response_json = response.json()
        # Check if the 'error' key is present in the response
        if 'error' in response_json:
            error_details = response_json['error']
            print(f"Error Code: {error_details['code']}, Message: {error_details['message']}")
        else:
            # No error key found, process the successful response
            print("API request was successful!")
            api_ok=True
    else:
    # Handle non-200 status code (e.g., print an error message)
        print(f"Error: {response.status_code} - {response.text}")
        sys.exit()
    eid=0
    if(api_ok):
       
        print("Api access works!")
        #find enterprise id and enterprise name
        if (operator):    
                print("Looking for %s id"%customer)
                eid = op_find_customer_enterpriseId(customer)
        elif (partner):
                print("Looking for %s id"%customer)
                eid = find_customer_enterpriseId(customer)
        else:
                eid = find_velo_enterpriseId()
    else:
        print("Issues using VCO API - Authentication troubleshoot needed")
        exit
    
    if(eid!=0):
        current_time = time.strftime("%m.%d.%y.%H.%M", time.localtime())
        params = {'enterpriseId': eid}
        response = requests.post(get_edge_list, headers=headers, data=json.dumps(params))
        
        json_response=response.json()
        for item in json_response:
     
          if 'name' in item:
            EdgeName=item['name']
            EdgeId=item['id']
            
            params = {"edgeId": EdgeId,
            "with": "modules",
            "enterpriseId": eid}
            resp2 = requests.post(get_edge_configuration, headers=headers, data=json.dumps(params))
            json_response=resp2.json()
            
            json_file = str(EdgeName)+'-Configuration-'+current_time+'.json'
            with open(json_file, 'w') as json_file:
                json.dump(json_response[0],json_file)

            
            #Save modules individually
            for module in json_response[0]['modules']:
                if module['name'] == 'deviceSettings':
                    deviceSettingsData = copy.copy(module)
                    deviceSettingsId = module['id']
                    #print deviceSettingsId
                    Module_name = str(EdgeName)+'-deviceSettings-'+current_time+'.json'
                    with open(Module_name, 'w') as outfile:
                        outfile.write(json.dumps(deviceSettingsData))
                if module['name'] == 'firewall':
                    firewallData = copy.copy(module)
                    firewallId = module['id']
                    #print firewallId
                    Module_name = str(EdgeName)+'-firewall-'+current_time+'.json'
                    with open(Module_name, 'w') as outfile:
                        outfile.write(json.dumps(firewallData))
                if module['name'] == 'QOS':
                    QOSData = copy.copy(module)
                    QOSId = module['id']
                    #print QOSId
                    Module_name = str(EdgeName)+'-QOS-'+current_time+'.json'
                    with open(Module_name, 'w') as outfile:
                        outfile.write(json.dumps(QOSData))
                if module['name'] == 'WAN':
                    WANData = copy.copy(module)
                    WANId = module['id']
                    #print WANId
                    Module_name = str(EdgeName)+'-WAN-'+current_time+'.json'
                    with open(Module_name, 'w') as outfile:
                        outfile.write(json.dumps(WANData))
                if module['name'] == 'analyticsSettings':
                    ENIData = copy.copy(module)
                    ENIId = module['id']
                    #print WANId
                    Module_name = str(EdgeName)+'-ENI-'+current_time+'.json'
                    with open(Module_name, 'w') as outfile:
                        outfile.write(json.dumps(ENIData))



          
    else:
        print(" Enteprise ID could not be retrieved")
if __name__ == '__main__':
    main()