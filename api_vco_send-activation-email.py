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
# 
# sample printenv
# export VCO_FQDN="vco.velocloud.net"
# export VCO_TOKEN="TY4ZTg5NDkiLCJpYXQiOjE5551OTkwMTF9.LfneUQWUTvHIo4ZsR6lclGN9G45SYgjZLrufIHob5XA"
import os
import sys
import requests
import json
import argparse

######### VELO VARIABLES AND FUNCTIONS

########## VCO info and credentials
# Prefer to use OS environments to hold token variable
token = "Token %s" %(os.environ['VCO_TOKEN'])
headers = {"Content-Type": "application/json", "Authorization": token}
VCO_FQDN='vco.velocloud.net'
VCO_FQDN=os.environ['VCO_FQDN']
vco_url = 'https://'+ VCO_FQDN+'/portal/rest/'

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
get_act_email = vco_url+'edge/getEdgeActivationEmail'
send_act_email = vco_url+'edge/sendEdgeActivationEmail'

########

# VCO FUNCTIONS

########

#### GET AND SEND ACTIVATION EMAIL 
def send_activation_email(eid,edid):
        # get email first
        print('send act email')
        params = {'edgeId': edid,'enterpriseId': eid}
        try:
                act_email = requests.post(get_act_email, headers=headers, data=json.dumps(params))
                
                act_email_j = act_email.json()
                
                to_email=act_email_j['to']
                actURL=act_email_j['content']['activationURL']
        except Exception as e:
                print(e)
                sys.exit()
          
        # send email
        params2 = { 'content': { 'salutation': 'Hi,','prompt': 'To activate your Edge, please follow these steps:',
        'steps': ['Connect your device to power and any Internet cables or USB modems.',
        'Find and connect to the Wi-Fi network that looks like \'velocloud-\' followed by 3 more letters/numbers (e.g. \'velocloud-01c\'), and use \'vcsecret\' as the password. If your device does not have Wi-Fi, connect to it using an Ethernet cable.',
        'Click the following link to activate your edge'
        ],
        'message': 'If you experience any difficulty, please contact your IT admin.',
        'activationURL': actURL
        },
        'to': to_email,
        'cc': '',
        'subject': 'Edge Activation',
        'edgeId': edid,
        'enterpriseId': eid}
        #print(params2)
        sent_email = requests.post(send_act_email, headers=headers, data=json.dumps(params2))
        print('Sending activation for Edge ',EdgeName,' to ',to_email,'',sent_email)

 #### RETRIEVE EDGE ID
def find_velo_edgeId(eid,EdgeName):
# Find Source Edge id based on Edge name
		params = {'enterpriseId': eid	}
		try:
		  edgesList = requests.post(get_edgelist, headers=headers, data=json.dumps(params))
		except Exception as e:
		  print(e)
		  sys.exit()
		eList_dict=edgesList.json()
		length = len(eList_dict)
		#### Find Source Edge
		name=search_name(EdgeName, eList_dict)
		#print(name)
		if (str(name)=='None'):
			print('Edge '+EdgeName+' not found!')
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
			print ('Edge: '+EdgeName+' found on VCO with Edge id: '+str(edid))
		return edid

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

######################### Main Program #####################

#### MAIN BODY

######################### Main Program #####################

#Get Edge Name as argument
if len(sys.argv) != 2:
		raise ValueError('Please specify Edge Name.  Example usage:  "python3 api_vco_send-activation-email.py edge-name"')
else:
		EdgeName = sys.argv[1]

eid = find_velo_enterpriseId()
edid = find_velo_edgeId(eid,EdgeName)
send_activation_email(eid,edid)
