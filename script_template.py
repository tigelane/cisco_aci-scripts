#!/usr/bin/env python
################################################################################
#                                                                              #
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
description = '''
    This is a template for scripts.  It will get you logged in and it'scripts
    your job to do more from there. 
'''

# Cisco ACI Cobra packages
import cobra.mit.access
import cobra.mit.request
import cobra.mit.session
import cobra.model.cdp
import cobra.model.fabric
import cobra.model.infra
import cobra.model.lldp
import cobra.model.pol

from cobra.internal.codec.xmlcodec import toXMLStr

# ACI Toolkit packages
import acitoolkit.acitoolkit as ACI

# All the other stuff we might need.
import sys, json

credentials = dict(
    accessmethod = 'https',
    ip_addr = '10.210.20.99',
    user = 'admin',
    # The password can be entered interactively.  It's ok to make this empty.
    password = 'cisco123'
    )

def hello_message():
    print "\nPlease be cautious with this application.  The author did very little error checking and can't ensure it will work as expected.\n"
    print description
    junk = raw_input('Press Enter/Return to continue.')
    return

def collect_admin(config):
    if config['accessmethod'] and config['ip_addr']:
        ip_addr = config['accessmethod'] + '://' + config['ip_addr']
    else:
        ip_addr = raw_input('URL of the APIC: ')
        
    if config['user']:
        user = config['user']
    else:
        user = raw_input('Administrative Login: ')

    if config['password']:
        password = config['password']
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



def main(argv):
	hello_message()

	# Login and setup sessions  
	# admin_info contains the URL, Username, and Password (in clear text)
	# Use 'cobramd' as our session for Cobra interface 
	# Use 'session' as the session for the ACI Toolkit.

	admin_info = collect_admin(credentials)
	cobramd = cobra_login(admin_info)
	session = toolkit_login(admin_info)


	print 'Script completed running'


if __name__ == '__main__':
    main(sys.argv)
