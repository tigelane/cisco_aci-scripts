#!/usr/bin/env python
########################################
#                                      #
#     _____      _____ _               #
#    |____ |    |_   _(_)              #
#        / /______| |  _  ___ _ __     #
#        \ \______| | | |/ _ \ '__|    #
#    .___/ /      | | | |  __/ |       #
#    \____/       \_/ |_|\___|_|       #
#                                      #
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
    Create a three tier application along with associated Tenant, Bridge Domain
    Private Network.  If they do not exist they will be created.
    Associate the three tires to a VMM domain.
    Create simple contracts between each layer.
'''

from acitoolkit.acisession import Session
from acitoolkit.acitoolkit import Credentials, Tenant, AppProfile, EPG, EPGDomain
from acitoolkit.acitoolkit import Context, BridgeDomain, Contract, FilterEntry


this_tenant = 'a1-Tenant'
this_app = 'my_three-tier-app'
tier1_epg = 'www-access'
tier2_epg = 'app-midtier'
tier3_epg = 'db-backend'
private_net = 'a1t_PN'
bridge_domain = 'a1t_BD'

# This must already exist
vmmdomain = 'a1t_VMware-01'

def main():
    # Setup or credentials and session
    description = ('Create 3 EPGs within the same Context, have them '
                   'provide and consume contracts and attach them to '
                   'a vmm domain.')
    creds = Credentials('apic', description)
    args = creds.get()
    
    # Login to APIC
    session = Session(args.url, args.login, args.password)
    session.login()

    # Get the virtual domain we are going to use
    vdomain = EPGDomain.get_by_name(session,vmmdomain)
    
    
    # Create the Tenant
    tenant = Tenant(this_tenant)

    # Create the Application Profile
    app = AppProfile(this_app, tenant)

    # Create the EPGs
    t1_epg = EPG(tier1_epg, app)
    t2_epg = EPG(tier2_epg, app)
    t3_epg = EPG(tier3_epg, app)

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

    ''' 
    Define a contract with a single entry
    Additional entries can be added by duplicating "entry1" 
    '''
    contract1 = Contract('mysql-contract', tenant)
    entry1 = FilterEntry('SQL',
                         applyToFrag='no',
                         arpOpc='unspecified',
                         dFromPort='3306',
                         dToPort='3306',
                         etherT='ip',
                         prot='tcp',
                         tcpRules='unspecified',
                         parent=contract1)
                                                 
    contract2 = Contract('app-contract', tenant)
    contract2.set_scope('application-profile')
    entry1 = FilterEntry('Flask',
                         applyToFrag='no',
                         arpOpc='unspecified',
                         dFromPort='5000',
                         dToPort='5000',
                         etherT='ip',
                         prot='tcp',
                         tcpRules='unspecified',
                         parent=contract2)
                         
    contract3 = Contract('web-contract', tenant)
    contract3.set_scope('application-profile')
    entry1 = FilterEntry('HTTPS',
                         applyToFrag='no',
                         arpOpc='unspecified',
                         dFromPort='443',
                         dToPort='443',
                         etherT='ip',
                         prot='tcp',
                         tcpRules='unspecified',
                         parent=contract3)
 
                         
    # Provide the contract from 1 EPG and consume from the other
    t3_epg.provide(contract1)
    t2_epg.consume(contract1)
    t2_epg.provide(contract2)
    t1_epg.consume(contract2)
    t1_epg.provide(contract3)


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

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass