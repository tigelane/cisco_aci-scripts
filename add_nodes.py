#!/usr/bin/env python
#############################################################  
#    _____       .___  .___  _______             .___       #
#   /  _  \    __| _/__| _/  \      \   ____   __| _/____   #
#  /  /_\  \  / __ |/ __ |   /   |   \ /  _ \ / __ |/ __ \  #
# /    |    \/ /_/ / /_/ |  /    |    (  <_> ) /_/ \  ___/  #
# \____|__  /\____ \____ |  \____|__  /\____/\____ |\___  > #
#         \/      \/    \/          \/            \/    \/  #
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

'''
    Scan an APIC for nodes (switches) that have not been given DHCP addresses.
    This is indicative of it not being accepted into the fabric yet.
    The program then asks if you would like to accept one into the fabric.
    It will prompt the user for a device name and id number.
    And then add it.  You should see an imidiate change in the APIC GUI.
    You will need to run this once for each switch that needs to be added.
    This was done intentionally because the fabric needs a little bit of time
    do discover the next switches (leaf -> spines -> leafs).
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
    print "Please be cautious with this application.  The author did very little error checking and can't ensure it will work as expected.\n"
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
        return 'Name: {0}  Model: {1}  Serial: {2}'.format(self.name, self.model, self.serial)

    def set_name(self, name):
        self.name = name

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

def get_dhcp_nodes(admin):
    all_nodes = []
    payload = ''
    headers = {'Content-type': 'application/json', 'APIC-challenge':admin['urlToken']}
    cookie = {'APIC-cookie':admin['APIC-cookie']}
    url = '{0}/api/node/class/topology/pod-1/node-1/dhcpClient.json'.format(admin['ip_addr'])

    try:
        result = requests.get(url, data=payload, headers=headers, cookies=cookie, verify=False)
    except requests.exceptions.RequestException as error:   
        error_message ([1,'There was an error with the connection to the APIC.', -1])
    
    decoded_json = json.loads(result.text)

    for a in range(0, len(decoded_json['imdata'])):
        clientEvent = decoded_json['imdata'][a]['dhcpClient']['attributes']['clientEvent']
        hwAddr = decoded_json['imdata'][a]['dhcpClient']['attributes']['hwAddr']
        serial = decoded_json['imdata'][a]['dhcpClient']['attributes']['id']
        ip = decoded_json['imdata'][a]['dhcpClient']['attributes']['ip']
        model = decoded_json['imdata'][a]['dhcpClient']['attributes']['model'] 
        name = decoded_json['imdata'][a]['dhcpClient']['attributes']['name']
        nodeId = decoded_json['imdata'][a]['dhcpClient']['attributes']['nodeId']
        nodeRole = decoded_json['imdata'][a]['dhcpClient']['attributes']['nodeRole'] 
        supported = decoded_json['imdata'][a]['dhcpClient']['attributes']['supported']
    
        anode = dhcpNode(clientEvent,hwAddr,serial,ip,model,name,nodeId,nodeRole,supported)
        all_nodes.append(anode)

    return all_nodes

def build_nodes(type):
    node_info = []
    name = go_lab_config.leafs['namebase'] + '-'
    number = go_lab_config.leafs['numberbase']
    total = go_lab_config.leafs['totalnumber']

    for node_number in range(int(number), int(number) + int(total)):
        node_info.append((name +  str(node_number), str(node_number)))

    return node_info

def add_node(all_nodes, admin):
    name = False
    nodeId = False
    leafs = build_nodes('leafs')
    spines = [build_nodes('spines')]

    for node in all_nodes:
        if node.not_installed():
            print '\nWould you like to add this device to the system?'
            print 'Model: {}    Role: {}    Serial: {}'.format(node.model, node.nodeRole, node.serial)
            junk = raw_input('(Yes) or No: ')
            if junk.lower() == 'no' or junk.lower() == 'n':
                print 'Node skipped.'
                continue

            print "YES - Ok, let's add it.\n"

            # if node.nodeRole == 'leaf':
            #     node.set_name(leafs[0][0])
            #     node.set_nodeId(leafs[0][1])
            #     leafs = leafs[1:]
            # if node.nodeRole == 'spine':
            #     node.set_name(spines[0][0])
            #     node.set_nodeId(spines[0][1])
            #     spines = spines[1:]
            while not nodeId:
                nodeId = raw_input('Please enter a node number for the switch (Min: 101): ')

            # while not name:
            #     name = raw_input('Please enter a name for the switch (Example: leaf or spine): ')

            node.set_name(node.nodeRole + '-' + nodeId)
            node.set_nodeId(nodeId)

            result = node.push_to_apic(admin)
            if (result.status_code != 200):
                error_message ([decoded_json['imdata'][0]['error']['attributes']['code'], decoded_json['imdata'][0]['error']['attributes']['text'], -1])

    return True

def main(argv):
    admin = {}
    hello_message()

    try:
        global go_lab_config
        import go_lab_config
    except ImportError:
        print 'No config file found (go_lab_config.py).  Use "go_lab.py --makeconfig" to create a base file.'
        exit()
    except:
        print 'There is an error with your config file.  Please use the interactive interpreture to diagnose.'
        exit()

    admin = collect_admin_info()
    add_admin = login(admin)
    ''' Add the session urlToken for future use with security, and the refresh timeout for future use '''
    admin.update({'urlToken':add_admin[0],'refreshTimeoutSeconds':add_admin[1], 'APIC-cookie':add_admin[2]})
  
    all_nodes = get_dhcp_nodes(admin)
    if not add_node(all_nodes, admin):
        print "\nSorry, there was either a problem, or there were no nodes to add."

    print "We're all done!"

if __name__ == '__main__':
    main(sys.argv)
