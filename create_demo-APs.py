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
'''

from acitoolkit.acisession import Session
from acitoolkit.acitoolkit import Credentials, Tenant, AppProfile, EPG, EPGDomain
from acitoolkit.acitoolkit import Context, BridgeDomain, Contract, FilterEntry, Subnet


# You can enter the tenant at runtime
tenant = 'Demo_Tenant'
vrf = tenant + '_VRF'
bridge_domain = tenant + '_BD'
ipSubnets = ['192.168.1.1/24', '192.168.2.1/24', '192.168.3.1/24', '192.168.4.1/24', '192.168.5.1/24']

D1 = {'name': 'D1_Same-IP-Sub', 'desc': 'Devices on the same IP Subnet but are in different EPGs seperated by a contract.'}
D2 = {'name': 'D2_Diff-IP-Sub', 'desc': 'Devices are on different IP Subnets and are in different EPGs seperated by a contract.'}
D3 = {'name': 'D3_Multi-IP-Sub','desc': 'Devices are on different IP Subnets is the same EPG, and are seperated by other devices in another EPG by a contract.'}
D4 = {'name': 'D4_Nano-Seg', 'desc': ''}
appProfiles = [D1, D2, D3, D4]

# Only two EPGs are supported right now
epgs = ['client', 'server']

# Valid options for the scope are 'private', 'public', and 'shared'.  Comma seperated, and NO spaces.  
# Private and shared are mutually exclusive.
subnet_scope = 'private'

# This must already exist in the APIC or you will get an error.
# You can enter the VMware Domain at runtime.
vmmInput = 'ACI_DVS'

# Dont modify these vars.  They are globals that will be used later.
session = None
theTenant = None
theVRF = None
theDB = None
vmmDomain = None

def collect_vmmdomain():
    global vmmDomain
    vmmDomain = None
    while not vmmDomain:
        vmmInput = raw_input('Please enter the VMMDomain name on the APIC: ')
    return

def check_virtual_domain():
    global vmmDomain
    # Get the virtual domain we are going to use from the user
    try:
        vmmDomain = EPGDomain.get_by_name(session,'ACI_VDS')
    except:
        print "There was an error using " + domain + " as the VMMDomain.  Are you sure it exists?"
        return False

    return True

def create_contract(appProfileName):
    ''' 
    Currently not used. 
    '''
    aContract = Contract(appProfileName, theTenant)
    aContract.set_scope('application-profile')
    entry1 = FilterEntry('_HTTP',
                         applyToFrag='no',
                         arpOpc='unspecified',
                         dFromPort='80',
                         dToPort='80',
                         etherT='ip',
                         prot='tcp',
                         tcpRules='unspecified',
                         parent=aContract)

    entry2 = FilterEntry('_Ping',
                         applyToFrag='no',
                         arpOpc='unspecified',
                         dFromPort='unspecified',
                         dToPort='unspecified',
                         etherT='ip',
                         prot='icmp',
                         tcpRules='unspecified',
                         parent=aContract)

    return aContract

def create_base():
    global theTenant, theBD
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
        appEpgs = []
        aApp = AppProfile(appProfile['name'], theTenant)

        for a, epg in enumerate(epgs):
            appEpgs.append(EPG(epg, aApp))
            appEpgs[a].add_bd(theBD)
            appEpgs[a].add_infradomain(vmmDomain)

            contract = create_contract(appProfile['name'])
            # The following code only works for 2 EPGs
            if a == 0:
                appEpgs[a].consume(contract)
                pass
            else:
                appEpgs[a].provide(contract)
                pass

        if not push_to_APIC():
            print ("Sorry for the error.  I'll exit now.")
            sys.exit()


def push_to_APIC():
    # CAUTION:  The next line will DELETE the tenant if it's uncommented
    # tenant.mark_as_deleted()
    resp = theTenant.push_to_apic(session)

    if resp.ok:
        # Print some confirmation
        # print('The configuration was sucessfully pushed to the APIC.')
        # Uncomment the next lines if you want to see the configuration
        # print('URL: '  + str(tenant.get_url()))
        # print('JSON: ' + str(tenant.get_json()))
        return True

    else:
        print resp
        print resp.text
        print('URL: '  + str(tenant.get_url()))
        print('JSON: ' + str(tenant.get_json()))
        return False

def main():
    global session
    # Setup or credentials and session
    description = ('Create a number of demo application profiles')
    creds = Credentials('apic', description)
    args = creds.get()
    
    # Login to APIC
    session = Session(args.url, args.login, args.password)
    session.login()

    # Get a good VMWare Domain to use
    while True:
        if check_virtual_domain():
            print ("Returned true")
            break
        else:
            collect_vmmdomain()

 
    create_base()
    create_application_profiles()

    print ("Everything seems to have worked if you are seeing this!")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass