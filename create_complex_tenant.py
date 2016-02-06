#!/usr/bin/env python
################################################################################
##
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
    Create several different app profiles and contracts.  Built to create a demo
    environement that based on the names and descriptions given below.
    
    This script required modifications that I have added to the acitoolkit.
    These modifications allow the addition of a stateful filter on a contract.
    As of Jan 10th I have made a pull request for branch:
    https://github.com/datacenter/acitoolkit/tree/Add-stateful-to-FilterEntry
    
    If you get the following error, that is the problem:
    TypeError: __init__() got an unexpected keyword argument 'stateful'

    The above pull request was merged into the acitoolkit.  If you get the above error
    you need to get the latest version of the toolkit and install it.

    Usage: create_complex_tenant.py tenant vmmDomain
    tenant and vmmDomain are optional.  Tenant can be used alone, vmmDomain must be used with Tenant.
'''

from acitoolkit.acisession import Session
from acitoolkit.acitoolkit import Credentials, Tenant, AppProfile, EPG, EPGDomain, VmmDomain
from acitoolkit.acitoolkit import Context, BridgeDomain, Contract, FilterEntry, Subnet

import sys
import create_common_contracts
import create_ospf_egress


# You can enter the tenant at runtime
tenant = 'A_SCRIPT_MADE_ME'
ipSubnets = ['192.168.1.1/24', '192.168.2.1/24', '192.168.3.1/24', '192.168.4.1/24', '192.168.5.1/24']

D1 = {'name': 'Patient_RecordView', 'epgs': [
                        {'name':'Web_PRV', 'provide':['Web','Management'], 'consume':['Application', 'Outbound_Server']}, 
                        {'name':'App_PRV', 'provide':['Application','Management'], 'consume':['DataBase', 'Outbound_Server']}]}
D2 = {'name': 'HRMS', 'epgs': [
                        {'name':'Web_HRMS', 'provide':['Web','Management'], 'consume':['Application', 'Outbound_Server']}, 
                        {'name':'App_HRMS', 'provide':['Application','Management'], 'consume':['DataBase', 'Outbound_Server']}]} 
D3 = {'name': 'DataBases', 'epgs': [
                        {'name':'DB_Servers', 'provide':['DataBase','Management'], 'consume':['Outbound_Server']}]}
appProfiles = [D1, D2, D3]

# Valid options for the scope are 'private', 'public', and 'shared'.  Comma seperated, and NO spaces.  
# Private and shared are mutually exclusive.
subnet_scope = 'public'

# This must already exist in the APIC or you will get an error.
# You can enter the VMware Domain at runtime. 
vmmInput = 'aci_lab_none'

# Dont modify these vars.  They are globals that will be used later.
session = None
theTenant = None
theVRF = None
theDB = None
theVmmDomain = None

def collect_vmmdomain():
    global vmmInput
    vmmInput = None
    while not vmmInput:
        vmmInput = raw_input('Please enter the VMMDomain name on the APIC: ')
    return

def check_virtual_domain():
    global theVmmDomain
    # Get the virtual domain we are going to use from the user
    domains = VmmDomain.get(session)

    for domain in domains:
        if domain.name == vmmInput:
            theVmmDomain = EPGDomain.get_by_name(session,vmmInput)
            return True

    print 'There was an error using {} as the VMMDomain.  Are you sure it exists?'.format(vmmInput)
    if len(domains) > 0:
        print ("The following are your options:")
        for n, domain in enumerate(domains):
            print (domain)
    else:
        print ("There are no VMMDomains!")
        sys.exit()
    return False

def create_base_contracts():
    aContract = Contract('Outbound_Access', theTenant)
    aContract.set_scope('context')


def create_base():
    global theTenant, theBD
    vrf = tenant + '_VRF'
    bridge_domain = tenant + '_BD'
    # This creates the tenant, vrf, and bridge domain
    theTenant = Tenant(tenant)
    theVRF = Context(vrf, theTenant)
    theBD = BridgeDomain(bridge_domain, theTenant)
    theBD.add_context(theVRF)

    for ipSubnet in ipSubnets:
        aSubnet = Subnet('VLAN', theBD)
        aSubnet.set_addr(ipSubnet)
        aSubnet.set_scope(subnet_scope)
        theBD.add_subnet(aSubnet)

    return

def create_application_profiles():

    # Create the Application Profile
    for appProfile in appProfiles:
        aApp = AppProfile(appProfile['name'], theTenant)

        for epg in appProfile['epgs']:
            appEpg = EPG(epg['name'], aApp)
            appEpg.add_bd(theBD)
            appEpg.add_infradomain(theVmmDomain)

            for provided in epg['provide']:
                appEpg.provide(Contract(provided, theTenant))
            for consumed in epg['consume']:
                appEpg.consume(Contract(consumed, theTenant))
 
            if not push_to_APIC():
                print ("Sorry for the error.  I'll exit now.")
                sys.exit()

def push_to_APIC():
    resp = theTenant.push_to_apic(session)

    if resp.ok:
        return True

    else:
        print ("We had a problem pushing the information to the APIC.")
        print resp
        print resp.text
        print('URL: '  + str(tenant.get_url()))
        print('JSON: ' + str(tenant.get_json()))
        return False

def main(argv):
    global session, tenant, vmmInput
    if len(argv) > 2:
        vmmInput = argv[2]
        argv.remove(vmmInput)
    if len(argv) > 1:
        tenant = argv[1]
        argv.remove(tenant)

    # Setup or credentials and session
    description = ('Create some stuff.')
    creds = Credentials('apic', description)
    args = creds.get()
    
    # Login to APIC
    session = Session(args.url, args.login, args.password)
    session.login()

    # Get a good Virtual Domain to use
    while True:
        if check_virtual_domain():
            break
        else:
            collect_vmmdomain()
 
    create_base()
    create_common_contracts.create_all_contracts(theTenant, session)
    create_ospf_egress.create_interface(theTenant, session, {'provide':'Outbound_Server', 'consume':'Web'})
    create_application_profiles()

    print ("Everything seems to have worked if you are seeing this.")

if __name__ == '__main__':
    try:
        main(sys.argv)
    except KeyboardInterrupt:
        pass
