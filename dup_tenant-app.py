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
import sys

# globals that change
vdomain = ''
session = ''
tenants = []
apps = []
epgs = []

# # 
# this_app = 'New-DC'
# tier1_epg = 'VLAN-5'
# tier1_subnet = '192.168.5.1/24'
# tier2_epg = 'VLAN-6'
# tier2_subnet = '192.168.6.1/24'
# tier3_epg = 'VLAN-7'
# tier3_subnet = '192.168.7.1/24'
# tier4_epg = 'VLAN-8'
# tier4_subnet = '192.168.8.1/24'
# tier5_epg = 'VLAN-9'
# tier5_subnet = '192.168.9.1/24'
# private_net = 'NewDC_PN'
# bridge_domain = 'NewDC_BD'

# Valid options for the scape are 'private', 'public', and 'shared'.  Comma seperated, and NO spaces
subnet_scope = 'private,shared'

# This must already exist in the APIC or you will get an error.
# You can enter the VMware Domain at runtime
vmmdomain = 'a1t_VMware-01'

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
    newTenant = raw_input('Please enter the new Tenant name ({}): '.format(oldTenant.name))
    if newTenant == '':
        newTenant = oldTenant.name
    oldAppProfile = getAppProfile(oldTenant)
    newAppProfile = raw_input('Please enter the new Application Profile Name ({}): '.format(oldAppProfile.name))
    if newAppProfile == '':
        newAppProfile = oldAppProfile.name

    if oldTenant.name == newTenant and oldAppProfile.name == newAppProfile:
        print ("The same Tenant and Application Profile can not be used.")
        exit()

    epgs = EPG.get(session, oldAppProfile, oldTenant)

    # Populate the Bridge Domains we need
    bridgeDomains = []
    for epg in epgs:
        print epg.get_json()
        print ('Tenant: {} AppProfile: {} EPG: {} Has BD: {}\n'.format(oldTenant.name, oldAppProfile.name, epg.name, epg.has_bd()))
        bridgeDomains.append(epg.get_bd())

    print bridgeDomains
    testEPG()
    # createEverything(newTenant, newAppProfile) 

def testEPG():

    tenant = Tenant("a1-Tenant")
    app = AppProfile("my_three-tier-app", tenant)
    testEPG = EPG("db-backend", app )
    print ('Does this thing have a BD:', testEPG.has_bd())
    bd = BridgeDomain("my_temp_bd", tenant)
    testEPG.add_bd(bd)
    print ('Does this thing have a BD:', testEPG.has_bd())

    existingEPG = EPG.get(session, app, tenant)
    for epg in existingEPG:
        print (epg.get_json())

    allBDs = BridgeDomain.get(session, tenant)
    for thisBD in allBDs:
        print (thisBD.get_json())

    print (BridgeDomain.get_table(allBDs))
 

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

def createEverything(newTenant, newAppProfile):
    # Create the Tenant
    tenant = Tenant(newTenant)

    # Create the Application Profile
    app = AppProfile(newAppProfile, tenant)

    # # Create the EPGs
    # t1_epg = EPG(tier1_epg, app)
    # t2_epg = EPG(tier2_epg, app)
    # t3_epg = EPG(tier3_epg, app)
    # t4_epg = EPG(tier4_epg, app)
    # t5_epg = EPG(tier5_epg, app)

    # # Create a Context and BridgeDomain
    # # Place all EPGs in the Context and in the same BD
    # context = Context(private_net, tenant)
    # bd = BridgeDomain(bridge_domain, tenant)
    # bd.add_context(context)

    # # Add all the IP Addresses to the bridge domain
    # bd_subnet5 = Subnet(tier1_epg, bd)
    # bd_subnet5.set_addr(tier1_subnet)
    # bd_subnet5.set_scope(subnet_scope)
    # bd.add_subnet(bd_subnet5)
    # bd_subnet6 = Subnet(tier2_epg, bd)
    # bd_subnet6.set_addr(tier2_subnet)
    # bd_subnet6.set_scope(subnet_scope)
    # bd.add_subnet(bd_subnet6)
    # bd_subnet7 = Subnet(tier3_epg, bd)
    # bd_subnet7.set_addr(tier3_subnet)
    # bd_subnet7.set_scope(subnet_scope)
    # bd.add_subnet(bd_subnet7)
    # bd_subnet8 = Subnet(tier4_epg, bd)
    # bd_subnet8.set_addr(tier4_subnet)
    # bd_subnet8.set_scope(subnet_scope)
    # bd.add_subnet(bd_subnet8)
    # bd_subnet9 = Subnet(tier5_epg, bd)
    # bd_subnet9.set_addr(tier5_subnet)
    # bd_subnet9.set_scope(subnet_scope)
    # bd.add_subnet(bd_subnet9)



    # t1_epg.add_bd(bd)
    # t1_epg.add_infradomain(vdomain)
    # t2_epg.add_bd(bd)
    # t2_epg.add_infradomain(vdomain)
    # t3_epg.add_bd(bd)
    # t3_epg.add_infradomain(vdomain)
    # t4_epg.add_bd(bd)
    # t4_epg.add_infradomain(vdomain)
    # t5_epg.add_bd(bd)
    # t5_epg.add_infradomain(vdomain)

    # ''' 
    # Define a contract with a single entry
    # Additional entries can be added by duplicating "entry1" 
    # '''
    # contract1 = Contract('allow_all', tenant)
    # entry1 = FilterEntry('all',
    #                      applyToFrag='no',
    #                      arpOpc='unspecified',
    #                      dFromPort='unspecified',
    #                      dToPort='unspecified',
    #                      etherT='unspecified',
    #                      prot='unspecified',
    #                      tcpRules='unspecified',
    #                      parent=contract1)
                         
    # # All the EPGs provide and consume the contract
    # t1_epg.consume(contract1)
    # t1_epg.provide(contract1)
    # t2_epg.consume(contract1)
    # t2_epg.provide(contract1)
    # t3_epg.consume(contract1)
    # t3_epg.provide(contract1)
    # t4_epg.consume(contract1)
    # t4_epg.provide(contract1)
    # t5_epg.consume(contract1)
    # t5_epg.provide(contract1)


    # Finally, push all this to the APIC
    
    # Cleanup (uncomment the next line to delete the config)
    # CAUTION:  The next line will DELETE the tenant
    # tenant.mark_as_deleted()
    resp = tenant.push_to_apic(session)

    if resp.ok:
        # Print some confirmation
        print('The configuration was sucessfully pushed to the APIC.')
        # Uncomment the next lines if you want to see the configuration
        # print('URL: '  + str(tenant.get_url()))
        # print('JSON: ' + str(tenant.get_json()))
    else:
        print resp
        print resp.text
        print('URL: '  + str(tenant.get_url()))
        print('JSON: ' + str(tenant.get_json()))

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass