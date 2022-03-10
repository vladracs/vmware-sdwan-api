#!/usr/bin/env python3
# author: vfrancadesou@vmware.com
# Simple Python Script that uses vmware sd-wan orchestrator api to create a csv file with edge list ready for ENI import
#
# if running as operator use:
# python3 api_vco-to-eni-OP.py -o -c "Enterprise-Customer1"
#
# if running as enterprise users:
# run without arguments 

import os
import sys
import requests
import json
import csv
import argparse
#import warnings

### VCO info and credentials
token = "Token %s" %(os.environ['VCO_TOKEN'])
vco_url = 'https://' + os.environ['VCO_HOSTNAME'] + '/portal/rest/'
headers = {"Content-Type": "application/json", "Authorization": token}
### VCO API METHODS
get_enterprise = vco_url + 'enterprise/getEnterprise'
get_enterprise_op = vco_url + 'network/getNetworkEnterprises'
get_edgelist = vco_url+'enterprise/getEnterpriseEdgeList'

       
######################### Main Program #####################
    

def main():
       # warnings.filterwarnings("ignore")
        Operator=False
        parser = argparse.ArgumentParser()
        parser.add_argument("-o", "--operator", action='store_true', help="Option: Login as Operator",default = False)
        parser.add_argument("-c", "--customer", help="Name of the Customer/Enterprise",required=False)
        args = parser.parse_args()
        eid=10
        ename="Test Customer"
        if args.operator:
                print("Running as Operator")
                EntName=args.customer
                params = {}
                enterprises = requests.post(get_enterprise_op, headers=headers, data=json.dumps(params),verify=True)
                ent_dict = enterprises.json()
                print(ent_dict)
                for enterprise in ent_dict:
                        
                        if (enterprise['name']==EntName):
                         eid = enterprise['id']
                         ename=enterprise['name']
                         print("Enterprise found on VCO "+ename+" with id:"+str(eid))    

        else:
            print("Running as Enterprise User")    
            eid=0
            resp = requests.post(get_enterprise, headers=headers, data='', verify=True)
            ent_j = resp.json()
            eid=ent_j['id']
            ename=ent_j['name']
            #print(ename)
        
        enamenospace=ename.replace(" ", "")
        params = {'enterpriseId': eid, 'with': ['site', 'licenses']}
        edgesList = requests.post(get_edgelist, headers=headers, data=json.dumps(params), verify=True)
        eList_dict=edgesList.json()
        site_array = []
        for edge in eList_dict:
                site_array.append({'name': edge['name'],
                                   'CrawlerIds': '',
                                   'ControllerIps': '',
                                   'Subnets': '',
                                   'APs': '',
                                   'Lat': edge['site']['lat'],
                                   'Lng': edge['site']['lon'],
                                   'Place name': '',
                                   'Ignore?': 'FALSE'})
        with open(f'edge_dump-{enamenospace}.csv', 'w') as f:
                writer = csv.DictWriter(f, fieldnames=site_array[0].keys())
                writer.writeheader()
                writer.writerows(site_array)
        print("CSV File Created")
if __name__ == "__main__":
        main()
