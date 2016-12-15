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
Helper functions to get a good VMMDomain
'''

from acitoolkit.acisession import Session
from acitoolkit.acitoolkit import Credentials, Tenant, EPG, EPGDomain
from acitoolkit.acitoolkit import Context, BridgeDomain, Subnet, AppProfile
import sys, re, random


# You can enter the tenant at runtime (maybe)
vmmDomain = 'junk_dvs'


# Dont modify these vars.  They are globals that will be used later.
session = None
theTenant = None
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



def main():
    global session
    # Setup or credentials and session
    description = ('Find the VMM Domain to use for EPGs')
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

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass