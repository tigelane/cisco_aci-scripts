#!/usr/bin/env python
################################################################################
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
    Creates a number of commontly used contracts and associated filters.  
    These would normaly be placed in the "common" tenant.  I have
    chossen to place them in a noticable tenant name by default 
    so you will be sure to notice if you don't change the name.
'''

from acitoolkit.acisession import Session
from acitoolkit.acitoolkit import Credentials, Tenant, AppProfile, EPG, EPGDomain, VmmDomain
from acitoolkit.acitoolkit import Context, BridgeDomain, Contract, FilterEntry, Subnet

# In case you are running this independantly (it can also be called as a function).
tenant = 'A_SCRIPT_MADE_ME'


def create_all_contracts(theTenant, session):

    ''' Services and Outbound Server '''
    aContract = Contract('Outbound_Server', theTenant)
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
    push_to_APIC(theTenant, session)

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
    push_to_APIC(theTenant, session)

    entry = FilterEntry('DNS',
                        applyToFrag='no',
                        arpOpc='unspecified',
                        dFromPort='53',
                        dToPort='53',
                        etherT='ip',
                        prot='udp',
                        tcpRules='unspecified',
                        parent=aContract)
    push_to_APIC(theTenant, session)

    entry = FilterEntry('NTP',
                        applyToFrag='no',
                        arpOpc='unspecified',
                        dFromPort='123',
                        dToPort='123',
                        etherT='ip',
                        prot='udp',
                        tcpRules='unspecified',
                        parent=aContract)
    push_to_APIC(theTenant, session)

    entry = FilterEntry('Ping',
                        applyToFrag='no',
                        arpOpc='unspecified',
                        dFromPort='unspecified',
                        dToPort='unspecified',
                        etherT='ip',
                        prot='icmp',
                        tcpRules='unspecified',
                        parent=aContract)
    push_to_APIC(theTenant, session)

    ''' Web '''
    aContract = Contract('Web', theTenant)
    aContract.set_scope('context')
    entry = FilterEntry('HTTPS',
                        parent=aContract)
    push_to_APIC(theTenant, session)

    entry = FilterEntry('HTTP',
                        parent=aContract)
    push_to_APIC(theTenant, session)

    entry = FilterEntry('Ping',
                        parent=aContract)
    push_to_APIC(theTenant, session)

    ''' Management '''
    aContract = Contract('Management', theTenant)
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
    push_to_APIC(theTenant, session)

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
    push_to_APIC(theTenant, session)

    entry = FilterEntry('Ping',
                        parent=aContract)
    push_to_APIC(theTenant, session)

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
    push_to_APIC(theTenant, session)

    aContract = Contract('Application', theTenant)
    aContract.set_scope('application-profile')
    entry = FilterEntry('HTTPS',
                        parent=aContract)
    push_to_APIC(theTenant, session)

    ''' Applications '''
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
    push_to_APIC(theTenant, session)

    entry = FilterEntry('NODE',
                        applyToFrag='no',
                        arpOpc='unspecified',
                        dFromPort='8000',
                        dToPort='8000',
                        etherT='ip',
                        prot='tcp',
                        stateful='yes',
                        tcpRules='unspecified',
                        parent=aContract)
    push_to_APIC(theTenant, session)

    ''' Database '''
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
    push_to_APIC(theTenant, session)

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
    push_to_APIC(theTenant, session)

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
    push_to_APIC(theTenant, session)

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
    push_to_APIC(theTenant, session)

def push_to_APIC(theTenant, session):
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
    # Setup or credentials and session
    description = ('Common contracts and filters')
    creds = Credentials('apic', description)
    args = creds.get()
    
    # Login to APIC
    session = Session(args.url, args.login, args.password)
    session.login()

    # This creates the tenant object
    theTenant = Tenant(tenant)

    create_all_contracts(theTenant, session)

    print ("Created common contracts and filters in the {} tenant.".format(theTenant))
    print ("Everything seems to have worked if you are seeing this.")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass