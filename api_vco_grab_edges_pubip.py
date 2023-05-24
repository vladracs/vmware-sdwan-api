#!/usr/bin/env python3
#
# Author: vfrancadesou@vmware.com
# vfrancad@gmail.com

# Very simple script that leverages VMware SD-WAN Orchestrator API to:
# retrieve links ip addresses from activated edges in Vmware sdwan orchestrator

# Pre-requisites:
# VMware SD-WAN:
# Orchestrator Target

# Not to be considered as best practices in using VMware VCO API
# Meant to be used in Lab environments - Please test it and use at your own risk
#
# please note that VMWare API and Support team - do not guarantee this samples
# It is provided - AS IS - i.e. while we are glad to answer questions about API usage
# and behavior generally speaking, VMware cannot and do not specifically support these scripts
#
# Compatible with api v1 of the vmware sd-wan vco api
# using tokens to authenticate

import argparse
import json
import os
import sys
import urllib.request
from copy import deepcopy
import requests

requests.packages.urllib3.disable_warnings()  

########## VCO info and credentials
token = "Token %s" %(os.environ['VCO_TOKEN'])
vco_url = 'https://' + os.environ['VCO_HOSTNAME'] + '/portal/rest/'
headers = {"Content-Type": "application/json", "Authorization": token}
print("VCO URL %s "%vco_url)
######## VCO API methods
get_edge = vco_url + 'edge/getEdge'
get_enterprise = vco_url + 'enterprise/getEnterprise'
get_enterprise_operator = vco_url + 'network/getNetworkEnterprises'
get_enterprises = vco_url + 'enterpriseProxy/getEnterpriseProxyEnterprises'
get_edge_list=vco_url +'enterprise/getEnterpriseEdgeList'
get_ofclist = vco_url+'enterprise/getEnterpriseRouteTable'
get_ent = vco_url+'enterpriseProxy/getEnterpriseProxy'

#### VCO FUNCTIONS

#### RETRIEVE ENTERPRISE ID for this user
def find_velo_enterpriseId():
	#Fetch enterprise id convert to JSON
	eid=0
	enterprise = requests.post(get_enterprise, headers=headers, data='',verify=False)
	ent_j = enterprise.json()
	eid=ent_j['id']
	print('Enterprise Id = %d'%(eid))
	return eid
#### RETRIEVE ENTERPRISE ID for this user
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
#### RETRIEVE ENTERPRISE ID for a customer - as operator
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

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--operator", type=str,help="Call API as operator user",required=False)
    parser.add_argument("-p", "--partner", type=str,help="Call API as partner user",required=False)
    parser.add_argument("-e", "--enterprise", type=str,help="Name of Customer",required=False)
    args = parser.parse_args()
    customer=args.enterprise
    partner=args.partner
    operator=args.operator

#Test if basic access to VCO is possible

    code=urllib.request.urlopen('https://'+os.environ['VCO_HOSTNAME']).getcode()
    if(code==200): print("HTTPs access to VCO working")
    else: print("Issues while tring to access VCO website - Connectivity Troubleshooting Needed")
#Test if token / api access is working
    print("Testing if token / api access is working")
    params= {'enterpriseProxyId':1}
    if(str(requests.post(get_enterprises, headers=headers, data=json.dumps(params))).rfind("200")!=1):
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
       response = requests.post(get_edge_list, headers=headers, data='',verify=False)
       if response.status_code == 200:
        edges = response.json()
        for edge in edges:
            edge_name = edge["name"]
            print(edge_name)
            edgeId = edge["id"]
            params={'id':edgeId,'enterpriseId':eid,'with':['links']}
            response = requests.post(get_edge, headers=headers, data=json.dumps(params),verify=False)
            if response.status_code == 200:
                edgeconfig=response.json()
                if 'links' in edgeconfig:
                    edge_links=edgeconfig['links']
                    for link in edge_links:
                        edge_public_ip = link["ipAddress"]
                        print("Edge Public IP:", edge_public_ip)
            else:
                print("Failed to retrieve edge information.")
            print("---------")
       else:
        print("Failed to retrieve edges.")
    else:
        print("No Enteprise ID found")
    
if __name__ == '__main__':
    main()
