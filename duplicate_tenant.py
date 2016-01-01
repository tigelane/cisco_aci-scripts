#!/usr/bin/env python
################################################################################
#   Duplicate a tenant.                                                        #
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
################################################################################
'''
    This application will take user input for the Tenant you want to copy.  It
    will then create a duplicate of that tenant with the new name.
'''

from acitoolkit.acisession import Session
from acitoolkit.acitoolkit import Credentials, Tenant, AppProfile, EPG, EPGDomain
from acitoolkit.acitoolkit import Context, BridgeDomain, Contract, FilterEntry, Subnet

import sys, requests, json

session = ''

def error_message(error):
    '''  Calls an error message.  This takes 1 list of argument with 3 components.  #1 is the error number, #2 is the error text, 
         #3 is if the application should continue or not.  Use a bool set to True to kill the application.  Any other number
         continues the application.  You must code in a loop and go back to where you want unless you are exiting.
    '''
    
    print '\n================================='
    print   '  ERROR Number: ' + str(error[0])
    print   '  ERROR Text: ' + str(error[1])
    print '=================================\n'
    
    if error[2]:
        print 'Application ended due to error.\n'
        sys.exit()

def getFullTeanantInfo(oldTenant):
    myTenantDetails = oldTenant.get_deep(session, [oldTenant.name])
    for tenant in myTenantDetails:
        return str(tenant.get_json())

def createTenant(admin, newTenant, oldTenant, fullTenantInfo):
    ''' Create our new tenant
    '''
    headers = {'Content-type': 'application/json', 'APIC-challenge':admin['urlToken']}
    cookie = {'APIC-cookie':admin['APIC-cookie']}

    url = '{0}/api/node/mo/uni/tn-{1}.json'.format(admin['ip_addr'], newTenant)

    # Make the modifications to the string to fit what we need for a post to the system
    payload = fullTenantInfo
    payload = payload.replace("'", '"')
    oldString = '"name": "{}"'.format(oldTenant)
    newString = '"name": "{}"'.format(newTenant)
    payload = payload.replace(oldString, newString)
    payload = payload.replace(': u"', ': "')

    try:
        result = requests.post(url, data=payload, cookies=cookie, headers=headers, verify=False)
    except requests.exceptions.RequestException as error:   
        error_message ([1,'There was an error with the connection to the APIC.', True])
    
    if (result.status_code != 200):
        decoded_json = json.loads(result.text)
        error_message ([decoded_json['imdata'][0]['error']['attributes']['code'], decoded_json['imdata'][0]['error']['attributes']['text'], True])

    return True

def getOldTenant():
    tenants_list = []
    tenants = Tenant.get(session)
    for tenant in tenants:
        if tenant.name != 'mgmt' and tenant.name != 'infra' and tenant.name != 'common':
            tenants_list.append((tenant))
    
    print ('\nTenants on the system')
    print ('=====================')
    for a in range(len(tenants_list)):
        print str(a) + ': ' + tenants_list[a].name

    tenant_in = 99999
    while tenant_in > 99998:
        error = False
        input = raw_input('\nPlease enter the Tenant # where the application is you want to duplicate: ')
        try:
            tenant_in = int(input)
        except:
            error = True
        
        if tenant_in > len(tenants_list)-1:
            error = True

        if error:
            tenant_in = 99999
            print ('Please select a Tenant number from the list.')

    return tenants_list[tenant_in]

def oldSchoolLogin(admin):
    ''' Login to the system.  Takes information in a dictionary form for the admin user and password
    '''
    headers = {'Content-type': 'application/json'}

    login_url = '{0}/api/aaaLogin.json?gui-token-request=yes'.format(admin['ip_addr'])
    payload = '{"aaaUser":{"attributes":{"name":"' + admin['user']  + '","pwd":"' + admin['password'] + '"}}}'

    try:
        result = requests.post(login_url, data=payload, verify=False)
    except requests.exceptions.RequestException as error:   
        error_message ([1,'There was an error with the connection to the APIC.', True])

    decoded_json = json.loads(result.text)

    if (result.status_code != 200):
        error_message ([decoded_json['imdata'][0]['error']['attributes']['code'], decoded_json['imdata'][0]['error']['attributes']['text'], True])

    urlToken = decoded_json['imdata'][0]['aaaLogin']['attributes']['urlToken']
    refresh = decoded_json['imdata'][0]['aaaLogin']['attributes']['refreshTimeoutSeconds']
    cookie = result.cookies['APIC-cookie']

    return [urlToken, refresh, cookie]

def main():
    global session
 
    # Setup or credentials and session
    description = ('Duplicate an application profile with the associate BD and PN')
    creds = Credentials('apic', description)
    args = creds.get()
    
    # Login to APIC
    session = Session(args.url, args.login, args.password)
    session.login()

    oldTenant = getOldTenant()
    newTenant = raw_input('Please enter the new Tenant name: ')
    if newTenant == '':
        error_message ([3,'You must specify a new tenant name.', True])

    if oldTenant.name == newTenant:
       error_message ([3,'The same Tenant name can not be used.', True])


    fullTenantInfo = getFullTeanantInfo(oldTenant)

    #  Login to the system again so I can make direct rest calls without the acitoolkit
    admin = {"ip_addr":args.url,"user":args.login,"password":args.password}
    add_admin = oldSchoolLogin(admin)
    ''' Add the session urlToken for future use with security, and the refresh timeout for future use '''
    admin.update({'urlToken':add_admin[0],'refreshTimeoutSeconds':add_admin[1], 'APIC-cookie':add_admin[2]})

    createTenant(admin, newTenant, oldTenant.name, fullTenantInfo)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass