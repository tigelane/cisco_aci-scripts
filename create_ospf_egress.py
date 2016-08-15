#!/usr/bin/env python
################################################################################
#                 _    ____ ___   _____           _ _    _ _                   #
#                / \  / ___|_ _| |_   _|__   ___ | | | _(_) |_                 #
#               / _ \| |    | |    | |/ _ \ / _ \| | |/ / | __|                #
#              / ___ \ |___ | |    | | (_) | (_) | |   <| | |_                 #
#        ____ /_/   \_\____|___|___|_|\___/ \___/|_|_|\_\_|\__|                #
#       / ___|___   __| | ___  / ___|  __ _ _ __ ___  _ __ | | ___  ___        #
#      | |   / _ \ / _` |/ _ \ \___ \ / _` | '_ ` _ \| '_ \| |/ _ \/ __|       #
#      | |__| (_) | (_| |  __/  ___) | (_| | | | | | | |_) | |  __/\__ \       #
#       \____\___/ \__,_|\___| |____/ \__,_|_| |_| |_| .__/|_|\___||___/       #
#                                                    |_|                       #
################################################################################
#                                                                              #
# Copyright (c) 2015 Cisco Systems                                             #
# All Rights Reserved.                                                         #
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
"""
Sample of creating OSPF interface
"""

from acitoolkit.acitoolkit import Credentials, Session, Tenant, Context
from acitoolkit.acitoolkit import OutsideL3, OutsideEPG, Interface, L2Interface
from acitoolkit.acitoolkit import L3Interface, OSPFRouter, OSPFInterfacePolicy
from acitoolkit.acitoolkit import OSPFInterface, Contract


def main():
    creds = Credentials('apic')
    args = creds.get()
    session = Session(args.url, args.login, args.password)
    session.login()

    tenant = 'A_SCRIPT_MADE_ME'
    theTenant = Tenant(tenant)
    create_interface(theTenant, session, {'provide':'Outbound_Server', 'consume':'Web'})

    print ("Created a Layer 3 External gateway in tenant {}.".format(theTenant))
    print ("Everything seems to have worked if you are seeing this.")

def create_interface(tenant, session, epgs):
    ''' The epgs are in the form of a dictionary with provide and consume.  
        There can be only one of each.
    '''

    context = Context('{}_VRF'.format(tenant), tenant)
    outside_l3 = OutsideL3('Campus_Connection', tenant)
    outside_l3.add_context(context)
    phyif = Interface('eth', '1', '201', '1', '6')
    phyif.speed = '1G'
    l2if = L2Interface('eth 201/1/6', 'vlan', '40')
    l2if.attach(phyif)
    l3if = L3Interface('l3if')
    l3if.set_l3if_type('l3-port')
    # l3if.set_mtu('1500')
    l3if.set_addr('192.168.255.2/24')
    l3if.add_context(context)
    l3if.attach(l2if)
    rtr = OSPFRouter('rtr-2')
    rtr.set_router_id('22.22.22.22')
    rtr.set_node_id('201')
    ifpol = OSPFInterfacePolicy('1G_OSPF', tenant)
    #ifpol.set_nw_type('p2p')
    ospfif = OSPFInterface('Campus_IF', router=rtr, area_id='42')
    ospfif.auth_key = ''
    ospfif.int_policy_name = ifpol.name
    ospfif.auth_keyid = '1'
    ospfif.auth_type = 'simple'
    tenant.attach(ospfif)
    ospfif.networks.append('0.0.0.0/0')
    ospfif.attach(l3if)
    contract1 = Contract(epgs['provide'])
    outside_epg = OutsideEPG('Campus_Gateway-EPG', outside_l3)
    outside_epg.provide(contract1)
    contract2 = Contract(epgs['consume'])
    outside_epg.consume(contract2)
    outside_l3.attach(ospfif)

    resp = session.push_to_apic(tenant.get_url(),
                                tenant.get_json())

    if not resp.ok:
        print('%% Error: Could not push configuration to APIC')
        print(resp.text)

if __name__ == '__main__':
    main()
