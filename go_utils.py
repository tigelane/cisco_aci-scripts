#!/usr/bin/env python
################################################################################
#   ________ ________     ____ ______________.___.____       _________         #
#  /  _____/ \_____  \   |    |   \__    ___/|   |    |     /   _____/         #
# /   \  ___  /   |   \  |    |   / |    |   |   |    |     \_____  \          #
# \    \_\  \/    |    \ |    |  /  |    |   |   |    |___  /        \         #
#  \______  /\_______  / |______/   |____|   |___|_______ \/_______  /         #
#         \/         \/                                  \/        \/          #
################################################################################
#                                                                              #                                                      
#    Licensed under the Apache License, Version 2.0 (the "License"); you may   #
#    not use this file except in compliance with the License. You may obtain   #
#    a copy of the License at                                                  #
#                                                                              #
#         http://www.apache.org/licenses/LICENSE-2.0                           #
#                                                                              #
#    Unless required by applicable law or agreed to in writing, software       #
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT #
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the  #
#    License for the specific language governing permissions and limitations   #
#    under the License.                                                        #
#                                                                              #
#    This work contains code from: https://github.com/datacenter/acitoolkit    #
#                                                                              #
################################################################################
'''
    Base methods for use by the "go" scripts.
'''

# list of packages that should be imported for this code to work
import cobra.mit.access, cobra.mit.session
import acitoolkit.acitoolkit as ACI

import sys, getpass, random, string, json

connected = False

def error_message(error):
    '''  Calls an error message.  This takes 1 list argument with 3 components.  #1 is the error number, #2 is the error text, 
         #3 is if the application should continue or not.  Use -1 to kill the application.  Any other number
         continues the application.  You must code in a loop and go back to where you want unless you are exiting.
    '''
    
    print '\n================================='
    print   '  ERROR Number: ' + str(error[0])
    print   '  ERROR Text: ' + str(error[1])
    print '=================================\n'
    
    if error[2] == -1:
        print 'Application ended due to error.\n'
        sys.exit()

def create_configfile():
	my_config_file = 'go_lab_config.py'
	try:
		config_file = open(my_config_file, 'w')
	except:
		print ('\n\nConfiguration file can not be created: ' + my_config_file + '\n\n')
		exit()

	config = '''#
# DO NOT REMOVE ANY VALUES FROM THIS FILE!  Leave the string empty if you don't need it.
# Everything is a String and must be encapsulated in quotes as you see below.  Don't remove the quotes.
#
credentials = dict(
	accessmethod = 'https',
	ip_addr = '192.168.1.10',
	user = 'admin',
	# The password can be entered interactively.  It's ok to make this empty.
	password = 'suPer@secReT'
	)

leafs = dict(
	# This will create names like 'leaf-201'
	namebase = 'leaf',
	numberbase = '101',
	totalnumber = '2',
	)

spines = dict(
	# This will create names like 'spine-201'
	namebase = 'spine',
	numberbase = '201',
	totalnumber = '2',
	)

bgp = dict(
	# All spines will be used as BGP route reflectors.
	asnum = '65001'
	)

oob = dict(
	dg_mask = '192.168.1.1/24',
	start_ip = '192.168.1.100',
	end_ip = '192.168.1.199'
	)

time = dict(
	# Poll rate values are default, up to 10 servers will be accepted
	minpoll = '4',
	maxpoll = '6',
	server0 = 'pool.ntp.org',
	server1 = 'time1.google.com',
	server2 = ''
	)

dns = dict(
	# server0 will be preferred, up to 10 servers will be accepted
	server0 = '8.8.8.8',
	server1 = '8.8.8.7',
	server2 = '',
	server3 = '',
	server4 = '',

	# search0 will be default, up to 10 domains will be accepted
	search0 = 'yourorg.org',
	search1 = ''
	)

vmware_vmm = dict(
	# namebase will be used to start the naming of everything releated to VMware
	namebase = 'aci-test',
	vcenterip = '10.95.43.45',
	vlan_start = '2300',
	vlan_end = '2499',
	user = 'administrator',
	password = 'seC43t',
	datacenter = 'ACI_Lab'
	)

esxi_servers = dict(
	# Interface speed can be 1 or 10
	speed = '10',
	cdp = 'enabled',
	lldp = 'disabled',
	# Interface configuration will be attached to all leaf switches
	# Only a single interface statement can be used in this script
	# valid values: 1/13 or 1/22-24
	interfaces = '1/16-17'
	)
	'''
	config_file.write(config)
	config_file.close()
	print 'Configuration file created:  go_lab_config.py'

def collect_admin(config):
	if config.credentials['accessmethod'] and config.credentials['ip_addr']:
		ip_addr = config.credentials['accessmethod'] + '://' + config.credentials['ip_addr']
	else:
		ip_addr = raw_input('URL of the APIC: ')
        
	if config.credentials['user']:
		user = config.credentials['user']
	else:
		user = raw_input('Administrative Login: ')

	if config.credentials['password']:
		password = config.credentials['password']
	else:
		password = getpass.getpass('Administrative Password: ')

	return {'ip_addr':ip_addr, 'user':user, 'password':password}

def cobra_login(admin_info):
	# log into an APIC and create a directory object
	ls = cobra.mit.session.LoginSession(admin_info['ip_addr'], admin_info['user'], admin_info['password'])
	md = cobra.mit.access.MoDirectory(ls)
	md.login()
	return md

def toolkit_login(admin_info):
    session = ACI.Session(admin_info['ip_addr'], admin_info['user'], admin_info['password'])
    response = session.login()
 
    if not response.ok:
        error_message ([1,'There was an error with the connection to the APIC.', -1])
        return False

    decoded_response = json.loads(response.text)

    if (response.status_code != 200):
        if (response.status_code == 401):
            connection_status = 'Username/Password incorrect'
            return False
        else:
            error_message ([decoded_response['imdata'][0]['error']['attributes']['code'], decoded_response['imdata'][0]['error']['attributes']['text'], -1])
            return False
    
    elif (response.status_code == 200):
        refresh = decoded_response['imdata'][0]['aaaLogin']['attributes']['refreshTimeoutSeconds']
        cookie = response.cookies['APIC-cookie']
        return session
    else:
        return False

    return False
