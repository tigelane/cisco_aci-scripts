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
    Creates a number of the most commontly used contracts and associated
    filters.  These would normall be placed in the "common" tenant.  I have
    chossen to place them in by default in this script so you will be sure
    to notice if you don't change the name.
'''

from acitoolkit.acisession import Session
from acitoolkit.acitoolkit import Credentials, Tenant, AppProfile, EPG, EPGDomain, VmmDomain
from acitoolkit.acitoolkit import Context, BridgeDomain, Contract, FilterEntry, Subnet


# You can enter the tenant at runtime
tenant = 'A_SCRIPT_MADE_ME'

# Dont modify these vars.  They are globals that will be used later.
session = None
theTenant = None

def create_base_contracts():
    aContract = Contract('Outbound_Server_Access', theTenant)
    aContract.set_scope('context')
    entry = FilterEntry('HTTPS',
                         applyToFrag='no',
                         arpOpc='unspecified',
                         dFromPort='443',
                         dToPort='443',
                         etherT='ip',
                         prot='tcp',
                         stateful='yes',
                         tcpRules='unspecified',
                         parent=aContract)
    push_to_APIC()

    entry = FilterEntry('DNS',
                         applyToFrag='no',
                         arpOpc='unspecified',
                         dFromPort='53',
                         dToPort='53',
                         etherT='ip',
                         prot='udp',
                         tcpRules='unspecified',
                         parent=aContract)
    push_to_APIC()

    entry = FilterEntry('NTP',
                         applyToFrag='no',
                         arpOpc='unspecified',
                         dFromPort='123',
                         dToPort='123',
                         etherT='ip',
                         prot='udp',
                         tcpRules='unspecified',
                         parent=aContract)
    push_to_APIC()

    aContract = Contract('Web_Access', theTenant)
    aContract.set_scope('context')
    entry = FilterEntry('HTTP',
                         applyToFrag='no',
                         arpOpc='unspecified',
                         dFromPort='80',
                         dToPort='80',
                         etherT='ip',
                         prot='tcp',
                         stateful='yes',
                         tcpRules='unspecified',
                         parent=aContract)
    push_to_APIC()

    entry = FilterEntry('HTTPS',
                         applyToFrag='no',
                         arpOpc='unspecified',
                         dFromPort='443',
                         dToPort='443',
                         etherT='ip',
                         prot='tcp',
                         stateful='yes',
                         tcpRules='unspecified',
                         parent=aContract)
    push_to_APIC()

    entry = FilterEntry('Ping',
                         applyToFrag='no',
                         arpOpc='unspecified',
                         dFromPort='unspecified',
                         dToPort='unspecified',
                         etherT='ip',
                         prot='icmp',
                         tcpRules='unspecified',
                         parent=aContract)
    push_to_APIC()


    aContract = Contract('Management_Access', theTenant)
    aContract.set_scope('context')
    entry = FilterEntry('Telnet',
                         applyToFrag='no',
                         arpOpc='unspecified',
                         dFromPort='22',
                         dToPort='22',
                         etherT='ip',
                         prot='tcp',
                         stateful='yes',
                         tcpRules='unspecified',
                         parent=aContract)
    push_to_APIC()

    entry = FilterEntry('SSH',
                         applyToFrag='no',
                         arpOpc='unspecified',
                         dFromPort='23',
                         dToPort='23',
                         etherT='ip',
                         prot='tcp',
                         stateful='yes',
                         tcpRules='unspecified',
                         parent=aContract)
    push_to_APIC()

    entry = FilterEntry('Ping',
                         applyToFrag='no',
                         arpOpc='unspecified',
                         dFromPort='unspecified',
                         dToPort='unspecified',
                         etherT='ip',
                         prot='icmp',
                         tcpRules='unspecified',
                         parent=aContract)
    push_to_APIC()

    entry = FilterEntry('RDP',
                         applyToFrag='no',
                         arpOpc='unspecified',
                         dFromPort='3389',
                         dToPort='3389',
                         etherT='ip',
                         prot='tcp',
                         stateful='yes',
                         tcpRules='unspecified',
                         parent=aContract)
    push_to_APIC()

    aContract = Contract('Application_Server', theTenant)
    aContract.set_scope('application-profile')
    entry = FilterEntry('HTTPS',
                         parent=aContract)

    push_to_APIC()

    entry = FilterEntry('FLASK',
                         applyToFrag='no',
                         arpOpc='unspecified',
                         dFromPort='5000',
                         dToPort='5000',
                         etherT='ip',
                         prot='tcp',
                         stateful='yes',
                         tcpRules='unspecified',
                         parent=aContract)
    push_to_APIC()

    aContract = Contract('DataBase', theTenant)
    aContract.set_scope('context')
    entry = FilterEntry('MySQL',
                         applyToFrag='no',
                         arpOpc='unspecified',
                         dFromPort='3306',
                         dToPort='3306',
                         etherT='ip',
                         prot='tcp',
                         stateful='yes',
                         tcpRules='unspecified',
                         parent=aContract)
    push_to_APIC()

    entry = FilterEntry('Oracle_1521-22',
                         applyToFrag='no',
                         arpOpc='unspecified',
                         dFromPort='1521',
                         dToPort='1522',
                         etherT='ip',
                         prot='tcp',
                         stateful='yes',
                         tcpRules='unspecified',
                         parent=aContract)
    push_to_APIC()

    entry = FilterEntry('Oracle_1525',
                         applyToFrag='no',
                         arpOpc='unspecified',
                         dFromPort='1525',
                         dToPort='1525',
                         etherT='ip',
                         prot='tcp',
                         stateful='yes',
                         tcpRules='unspecified',
                         parent=aContract)
    push_to_APIC()

    entry = FilterEntry('Oracle_1529',
                         applyToFrag='no',
                         arpOpc='unspecified',
                         dFromPort='1529',
                         dToPort='1529',
                         etherT='ip',
                         prot='tcp',
                         stateful='yes',
                         tcpRules='unspecified',
                         parent=aContract)
    push_to_APIC()

def push_to_APIC():
    resp = theTenant.push_to_apic(session)

    if resp.ok:
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
    description = ('common contracts and filters')
    creds = Credentials('apic', description)
    args = creds.get()
    
    # Login to APIC
    session = Session(args.url, args.login, args.password)
    session.login()

    global theTenant
    # This creates the tenant object
    theTenant = Tenant(tenant)

    create_base_contracts()

    print ("Created common contracts and filters in the {} tenant.".format(theTenant))

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass