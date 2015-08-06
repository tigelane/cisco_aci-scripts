#!/usr/bin/env python
################################################################################
#                                                                              #
#  _______  _______  _______                 _        _______  _               #
# (  ____ \(  ____ )(  ____ \      |\     /|( \      (  ___  )( (    /|        #
# | (    \/| (    )|| (    \/      | )   ( || (      | (   ) ||  \  ( |        #
# | (__    | (____)|| |      _____ | |   | || |      | (___) ||   \ | |        #
# |  __)   |  _____)| | ____(_____)( (   ) )| |      |  ___  || (\ \) |        #
# | (      | (      | | \_  )       \ \_/ / | |      | (   ) || | \   |        #
# | (____/\| )      | (___) |        \   /  | (____/\| )   ( || )  \  |        #
# (_______/|/       (_______)         \_/   (_______/|/     \||/    )_)        #
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
################################################################################
'''
    Create a simple EPG as a VLAN setup in a Tenant.  Create one contract
    that all of the EPGs both provide and consume to allow full communication
    between everything.
'''

from acitoolkit.acisession import Session
from acitoolkit.acitoolkit import Credentials, Tenant, AppProfile, EPG, EPGDomain
from acitoolkit.acitoolkit import Context, BridgeDomain, Contract, FilterEntry


this_tenant = ''
this_app = 'New-DC'
tier1_epg = 'green'
tier2_epg = 'teal'
tier3_epg = 'red'
tier4_epg = 'blue'
tier5_epg = 'purple'
private_net = 'NewDC_PN'
bridge_domain = 'NewDC_BD'

# This must already exist or you will get an error, I'll do some error checking when 
# I run the code.
vmmdomain = ''


def collect_required():
    global this_tenant, vmmdomain
    this_tenant = raw_input('\nPlease enter the Tenant name: ')
    vmmdomain = raw_input('\nPlease enter the VMMDomain name: ')

def main():
    collect_required()
    # Setup or credentials and session
    description = ('Create 5 EPGs within the same Context, have them '
                   'provide and consume the same contract so that they '
                   'can communicate between eachother.')
    creds = Credentials('apic', description)
    args = creds.get()
    
    # Login to APIC
    session = Session(args.url, args.login, args.password)
    session.login()

    # Get the virtual domain we are going to use
    try:
        vdomain = EPGDomain.get_by_name(session,vmmdomain)
    except:
        print "There was an error using " + vmmdomain + " as the VMMDomain.  Are you sure it exists?"
        exit()
    
    
    # Create the Tenant
    tenant = Tenant(this_tenant)

    # Create the Application Profile
    app = AppProfile(this_app, tenant)

    # Create the EPGs
    t1_epg = EPG(tier1_epg, app)
    t2_epg = EPG(tier2_epg, app)
    t3_epg = EPG(tier3_epg, app)
    t4_epg = EPG(tier4_epg, app)
    t5_epg = EPG(tier5_epg, app)

    # Create a Context and BridgeDomain
    # Place all EPGs in the Context and in the same BD
    context = Context(private_net, tenant)
    bd = BridgeDomain(bridge_domain, tenant)
    bd.add_context(context)
    t1_epg.add_bd(bd)
    t1_epg.add_infradomain(vdomain)
    t2_epg.add_bd(bd)
    t2_epg.add_infradomain(vdomain)
    t3_epg.add_bd(bd)
    t3_epg.add_infradomain(vdomain)
    t4_epg.add_bd(bd)
    t4_epg.add_infradomain(vdomain)
    t5_epg.add_bd(bd)
    t5_epg.add_infradomain(vdomain)

    ''' 
    Define a contract with a single entry
    Additional entries can be added by duplicating "entry1" 
    '''
    contract1 = Contract('allow_all', tenant)
    entry1 = FilterEntry('all',
                         applyToFrag='no',
                         arpOpc='unspecified',
                         dFromPort='unspecified',
                         dToPort='unspecified',
                         etherT='unspecified',
                         prot='unspecified',
                         tcpRules='unspecified',
                         parent=contract1)
                         
    # All the EPGs provide and consume the contract
    t1_epg.consume(contract1)
    t1_epg.provide(contract1)
    t2_epg.consume(contract1)
    t2_epg.provide(contract1)
    t3_epg.consume(contract1)
    t3_epg.provide(contract1)
    t4_epg.consume(contract1)
    t4_epg.provide(contract1)
    t5_epg.consume(contract1)
    t5_epg.provide(contract1)


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
        print('URL: '  + str(tenant.get_url()))
        print('JSON: ' + str(tenant.get_json()))

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass