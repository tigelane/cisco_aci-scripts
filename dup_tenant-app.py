#!/usr/bin/env python
################################################################################
#   Still a work in progress!                                                  #
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
    Create a simple EPG as a VLAN setup in a Tenant.  Create one contract
    that all of the EPGs provide and consume to allow full communication
    between everything.
    This would mimic a customer data center that only uses security at the edge.
    Once you have servers on these EPGs, you can create specific Application 
    Profiles the provide more seperation, security, and reporting.  They will 
    need to stay on the same Bridge Domain.
'''

from acitoolkit.acisession import Session
from acitoolkit.acitoolkit import Credentials, Tenant, AppProfile, EPG, EPGDomain
from acitoolkit.acitoolkit import Context, BridgeDomain, Contract, FilterEntry, Subnet
import sys, requests, json

# globals that change
vdomain = ''
session = ''
tenants = []
apps = []
epgs = []
bridgeDomains = []
vrfs = []

def error_message(error):
    '''  Calls an error message.  This takes 1 list argument with 3 components.  #1 is the error number, #2 is the error text, 
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

def main():
    global session, oldTenant, oldAppProfile
 
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
        print ("You must specify a new tenant name.")
        exit()

    if oldTenant.name == newTenant:
        print ("The same Tenant name can not be used.")
        exit()

    payload = getFullTeanantInfo(oldTenant)

    admin = {"ip_addr":args.url,"user":args.login,"password":args.password}
    add_admin = oldSchoolLogin(admin)
    ''' Add the session urlToken for future use with security, and the refresh timeout for future use '''
    admin.update({'urlToken':add_admin[0],'refreshTimeoutSeconds':add_admin[1], 'APIC-cookie':add_admin[2]})

    createTenant(admin, newTenant, oldTenant.name, payload)

def getFullTeanantInfo(oldTenant):
    myTenantDetails = oldTenant.get_deep(session, [oldTenant.name])
    for tenant in myTenantDetails:
        return str(tenant.get_json())

def createTenant(admin, newTenant, oldTenant, payload):
    ''' Create our new tenant
    '''
    headers = {'Content-type': 'application/json', 'APIC-challenge':admin['urlToken']}
    cookie = {'APIC-cookie':admin['APIC-cookie']}

    url = '{0}/api/node/mo/uni/tn-{1}.json'.format(admin['ip_addr'], newTenant)

    payload = payload.replace("'", '"')
    oldString = '"name": "{}"'.format(oldTenant)
    newString = '"name": "{}"'.format(newTenant)
    payload = payload.replace(oldString, newString)
    payload = payload.replace(': u"', ': "')
    print ("\n\n\n" + payload)

    try:
        result = requests.post(url, data=payload, cookies=cookie, headers=headers, verify=False)
    except requests.exceptions.RequestException as error:   
        error_message ([1,'There was an error with the connection to the APIC.', -1])
    
    decoded_json = json.loads(result.text)

    if (result.status_code != 200):
        error_message ([decoded_json['imdata'][0]['error']['attributes']['code'], decoded_json['imdata'][0]['error']['attributes']['text'], -1])

    return

def getOldTenant():
    tenants_list = []
    tenants = Tenant.get(session)
    for tenant in tenants:
        if tenant.name != 'mgmt' and tenant.name != 'infra':
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
    
def getAppProfile(oldTenant):
    apps_list = []
    apps = AppProfile.get(session, oldTenant)
    for app in apps:
        apps_list.append((app))
    
    if len(apps) <= 0:
        error_message([2,'Sorry, there are no applications to duplicate in this Tenant yet', True])
        return

    print ('\nApplication Profiles')
    print ('====================')
 
    for a in range(len(apps_list)):
            print str(a) + ': ' + apps_list[a].name

    app_in = 99999
    while app_in > 99998:
        error = False
        input = raw_input('\nEnter the Application Profile # that you want to duplicate: ')
        try:
            app_in = int(input)
        except:
            error = True
        
        if app_in > len(apps_list)-1:
            error = True

        if error:
            app_in = 99999
            print ('Please select an Application Profile number from the list.')

    return apps_list[app_in]


    epgs = ACI.EPG.get(session, apps[app_in], tenants[tenant_in])

def oldSchoolLogin(admin):
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

  return [urlToken, refresh, cookie]


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass