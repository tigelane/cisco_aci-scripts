#!/usr/bin/env python
################################################################################
#                                                                              #                                                      #
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
################################################################################

description = '''
    This script uses a csv file to load switches into an environment.  Check the function load_nodes():
    for the file name.  It should be in this format:  Node ID, Name Name, Serial Number

        101,Spine-101,SAL18474V8N
        201,Leaf-201,SAL1910AL9U
        202,Leaf-202,SAL1910AL9E

    Please modify go_lab_config.py to suit your environment. 
'''

import requests, json, sys, getpass

DEBUG = True

def error_message(error):
    '''  Calls and error message.  This takes 1 list argument with 3 components.  #1 is the error number, #2 is the error text, 
         #3 is if the application should continue or not.  Use -1 to kill the application.  Any other number
         continues the application.  You must code in a loop and go back to where you want.
    '''
    print '\n================================='
    print   '  ERROR Number: ' + str(error[0])
    print   '  ERROR Text: ' + str(error[1])
    print '=================================\n'
    
    if error[2] == -1:
        print 'Application ended due to error.\n'
        sys.exit()
    
def hello_message():
    print "\nPlease be cautious with this application.  The author did very little error checking and can't ensure it will work as expected.\n"
    print description
    junk = raw_input('Press enter/return to continue:')
    return
    
def collect_admin_info():

    if DEBUG:
        ip_addr = go_lab_config.credentials['accessmethod'] + '://' + go_lab_config.credentials['ip_addr']
        user = go_lab_config.credentials['user']
        password = go_lab_config.credentials['password']
        if password == '':
            password = getpass.getpass('Administrative Password: ')
    else:
        ip_addr = raw_input('URL of the APIC: ')
        user = raw_input('Administrative Login: ')
        password = getpass.getpass('Administrative Password: ')  
    
    return {"ip_addr":ip_addr,"user":user,"password":password}

def login(admin):
    ''' Login to the system.  Takes information in a dictionary form for the admin user and password
    '''
    headers = {'Content-type': 'application/json'}
  
    login_url = '{0}/api/aaaLogin.json?gui-token-request=yes'.format(admin['ip_addr'])
    payload = '{"aaaUser":{"attributes":{"name":"' + admin['user']  + '","pwd":"' + admin['password'] + '"}}}'
  
    try:
        result = requests.post(login_url, data=payload, verify=False)
    except requests.exceptions.RequestException as error:   
        error_message ([1,'There was an error with the connection to the APIC.', -1])
 
    decoded_json = json.loads(result.text)

    if (result.status_code != 200):
        error_message ([decoded_json['imdata'][0]['error']['attributes']['code'], decoded_json['imdata'][0]['error']['attributes']['text'], -1])
    
    urlToken = decoded_json['imdata'][0]['aaaLogin']['attributes']['urlToken']
    refresh = decoded_json['imdata'][0]['aaaLogin']['attributes']['refreshTimeoutSeconds']
    cookie = result.cookies['APIC-cookie']

    print 'Login Accepted\n'

    return [urlToken, refresh, cookie]

class dhcpNode:

    def __init__(self, clientEvent,hwAddr,serial,ip,model,name,nodeId,nodeRole,supported):
        self.clientEvent = clientEvent
        self.hwAddr = hwAddr
        self.serial = serial
        self.ip = ip
        self.model = model
        self.name = name
        self.nodeId = nodeId
        self.nodeRole = nodeRole
        self.supported = supported

    def __str__(self):
        return 'Name: {0}  Model: {1}  Serial: {2}  ID: {3}'.format(self.name, self.model, self.serial, self.nodeId)

    def set_name(self, name):
        self.name = name

    def set_serial(self, serial):
        self.serial = serial

    def set_nodeId(self, nodeId):
        self.nodeId = nodeId

    def not_installed(self):
        if self.clientEvent == 'denied':
          return True
        else:
          return False

    def push_to_apic(self, admin):
        if self.name == '' or self.nodeId == '':
          return False

        headers = {'Content-type': 'application/json', 'APIC-challenge':admin['urlToken']}
        cookie = {'APIC-cookie':admin['APIC-cookie']}
        url = '{0}/api/node/mo/uni/controller/nodeidentpol.json'.format(admin['ip_addr'])

        payload = '{"fabricNodeIdentP":{"attributes":{'
        payload += '"dn": "uni/controller/nodeidentpol/nodep-' + self.serial
        payload += '","serial": "' + self.serial
        payload += '","nodeId": "' + self.nodeId
        payload += '","name": "' + self.name
        payload += '","status": "created,modified"},"children": []}}'

        result = requests.post(url, data=payload, headers=headers, cookies=cookie, verify=False)
        return result

def load_nodes():
    # Returns a list of nodes to be added to the system
    new_nodes = []
    switches_file = 'load_switches.csv'

    with open(switches_file) as file:
        for line in file:
            # seperate the values
            items = [x.strip() for x in line.split(',')]
            newNode = dhcpNode('','',items[2],'','',items[1],items[0],'','')
            new_nodes.append(newNode)

    return new_nodes

def add_node(node, admin):
    print ('\nWould you like to add this device to the system?')
    print (node)
    junk = raw_input('(Yes) or No: ')
    if junk.lower() == 'no' or junk.lower() == 'n':
        print ('Node skipped.')
        return

    print ("YES - Ok, let's add it.\n")

    result = node.push_to_apic(admin)
    if (result.status_code != 200):
        error_message ([decoded_json['imdata'][0]['error']['attributes']['code'], decoded_json['imdata'][0]['error']['attributes']['text'], -1])

    return True

def main(argv):
    admin = {}
    hello_message()
    print description

    try:
        global go_lab_config
        import go_lab_config
    except ImportError:
        print ('No config file found (go_lab_config.py).  Use "go_lab.py --makeconfig" to create a base file.')
        exit()
    except:
        print ('There is an error with your config file.  Please use the interactive interpreture to diagnose.')
        exit()

    # Read in the csv file on the command line and create Nodes from each line
    # Error and show format if it doesn't work.
    # While I have Nodes in a list, add them to the APIC

    admin = collect_admin_info()
    add_admin = login(admin)
    ''' Add the session urlToken for future use with security, and the refresh timeout for future use '''
    admin.update({'urlToken':add_admin[0],'refreshTimeoutSeconds':add_admin[1], 'APIC-cookie':add_admin[2]})
  
    all_nodes = load_nodes()
    for node in all_nodes:
        add_node(node, admin)

    print ("We're all done!")

if __name__ == '__main__':
    main(sys.argv)
