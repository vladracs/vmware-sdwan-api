#!/usr/bin/env python3
#
# Simple Python Script for MSP users that leverages vmware sd-wan orchestrator api to read OFC route table of a specfic Customer
# 
# it will save results as a json file and shows the number of subnet found
#
# usage: python3 api_vco_grab_ofc_routes -e Customer1 -r 10000
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
get_enterprise_operator = vco_url + 'network/getNetworkEnterprises'
get_enterprises = vco_url + 'enterpriseProxy/getEnterpriseProxyEnterprises'
get_ofclist = vco_url+'enterprise/getEnterpriseRouteTable'
get_ent = vco_url+'enterpriseProxy/getEnterpriseProxy'
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
######################### Main Program #####################
#### MAIN BODY
######################### Main Program #####################
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--routes", type=int,help="Number of Routes to be Displayed",required=True)
    parser.add_argument("-e", "--enterprise", type=str,help="Name of Customer",required=True)
    args = parser.parse_args()
    customer=args.enterprise
    n_of_routes=args.routes
    #test if token / api access is working
    print("Testing if token / api access is working")
    params= {'enterpriseProxyId':1}
    if(str(requests.post(get_enterprises, headers=headers, data=json.dumps(params))).rfind("200")!=1):
        print("Api access works!")
        print("Looking for %s id"%customer)
        eid = op_find_customer_enterpriseId(customer)
    else:
        print("Issues accessing VCO API - troubleshoot needed")
        exit
    if(eid!=0):
        params = {'filter':{'limit':n_of_routes,'rules':[]},'enterpriseId': eid}
        response = requests.post(get_ofclist, headers=headers, data=json.dumps(params))
        resp_dict=response.json()
        outputfile=customer+"routes.json"
        with open(outputfile, 'w') as outfile:
         outfile.write(json.dumps(resp_dict["subnets"]))
        i=0
        for subnets in resp_dict["subnets"]:
            i=i+1
        print("Total number of subnets found is",i)
    else:
        print("No Enteprise ID found")
if __name__ == '__main__':
    main()
