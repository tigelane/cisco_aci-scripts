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
Simple script with very little error checking to take all of the SVIs from a IOS
configuration and turn them into EPGs under a single Tenant and single Applicaiton Profile.
By default this script sets all of the subnets to advertise.
'''

from acitoolkit.acisession import Session
from acitoolkit.acitoolkit import Credentials, Tenant, EPG, EPGDomain, VmmDomain
from acitoolkit.acitoolkit import Context, BridgeDomain, Subnet, AppProfile
import sys, re, random, os.path

# local file that contains the IOS config you want to replicate
iosconfig = "cisco.txt"

# You can enter the tenant at runtime
tenant = None
appProfile = 'Legacy_Nets'
vmmInput = 'junk_dvs'
bd_extension = "_bd"
vrf_extension = "_vrf"

# This is for routing.  "public" means it will advertise the subnet.
# Valid options for the scope are 'private', 'public', and 'shared'.  Comma seperated, and NO spaces.  
# Private and shared are mutually exclusive.
subnet_scope = 'public'

# Dont modify these vars.  They are globals that will be used later.
session = None
theTenant = None
all_svi = set()
current_svi = ''
pushing_svi = None
pushcount = 0
theVmmDomain = None

# Regular expressions of information in the IOS config file
vlannumber = re.compile('^vlan\s(\d{1,4})$')
vlanname = re.compile('^\s\sname\s(\S+)')
intnumber = re.compile('^interface\sVlan(\d{1,4})$')
ipaddress = re.compile('^\s\sip\saddress\s(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')
ipsmask = re.compile('^\s\sip\saddress\s\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(/\d{1,2}$)')
iplmask = re.compile('^\s\sip\saddress\s\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\s(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})$')
hsrpaddress = re.compile('^\s\s\s\sip\s(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})$')

def get_tenant():
    global tenant
    while not tenant:
        tenant = raw_input('Please enter a Tenant name for the new networks on the APIC: ')

    return True

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

class SVI:

    def __init__(self, number):
        self.number = number
        self.name = None
        self.ip = None
        self.mask = None
        self.description = None
        self.advertise = True

    def __str__(self):
        return 'Number: {0}  Name: {1} IP: {2}  Mask: {3}  Description: {4} Advertise: {5}'.format(self.number, self.name, self.ip, self.mask, self.description, self.advertise)

    def set_name(self, name):
        self.name = name

    def set_ip(self, ip):
        self.ip = ip

    def set_mask(self, mask):
        self.mask = mask

    def set_description(self, description):
        self.description = description

    def set_advertise(self, advertise):
        self.advertise = advertise

def printsvis():
    for svi in all_svi:
        print svi

def readconfigfile():
    global iosconfig
    while True:
        if os.path.isfile(iosconfig):
            with open(iosconfig) as openfileobject:
                for line in openfileobject:
                    parsetheline(line)
            openfileobject.close()
            break
        else:
            print ("Unable to find file: {}".format(iosconfig))
            iosconfig = raw_input('Please enter a Cisco config file name: ')

def get_svibynumber(number):
    for svi in all_svi:
        if svi.number == number:
            return svi
    return False

def get_cidrfrommask(mask):
    bits = sum([bin(int(x)).count("1") for x in mask.split(".")])
    return  "/" + str(bits)

def parsetheline(iosline):
    global all_svi, current_svi
    
    if vlannumber.match(iosline):
        current_svi = SVI(vlannumber.findall(iosline)[0])
        all_svi.add(current_svi)

    elif vlanname.match(iosline):
        name = vlanname.findall(iosline)[0]
        for cha in [':', '#', '<', '>']:
            if cha in name:
                name = name.replace(cha,"_")
        # name.replace(":", "_")
        current_svi.set_name(name)

    elif intnumber.match(iosline):
        current_svi = get_svibynumber(intnumber.findall(iosline)[0])
        if current_svi == False:
            current_svi = SVI(intnumber.findall(iosline)[0])

    elif ipaddress.match(iosline):
        current_svi.set_ip(ipaddress.findall(iosline)[0])
        if ipsmask.match(iosline):
            current_svi.set_mask(ipsmask.findall(iosline)[0])
        if iplmask.match(iosline):
            current_svi.set_mask(get_cidrfrommask(iplmask.findall(iosline)[0]))

    elif hsrpaddress.match(iosline):
        current_svi.set_ip(hsrpaddress.findall(iosline)[0])

def build_base():
    global theTenant, pushing_svi, pushcount
    count = 0
    pushcount = 0

    # This creates the tenant, vrf, and bridge domain
    theTenant = Tenant(tenant)
    theVRF = Context(tenant + vrf_extension, theTenant)

    for svi in all_svi:
        pushing_svi = svi
        if svi.ip == None:
            continue
        if svi.name == None:
            current_svi.set_name("vlan_" + svi.number)

        theBD = BridgeDomain(svi.name + bd_extension, theTenant)
        theBD.add_context(theVRF)
        aSubnet = Subnet('VLAN', theBD)
        subnet = svi.ip + svi.mask
        aSubnet.set_addr(subnet)
        aSubnet.set_scope(subnet_scope)
        theBD.add_subnet(aSubnet)

        # push_to_APIC()

        aApp = AppProfile(appProfile, theTenant)
        # push_to_APIC()

        theEPG = EPG(svi.name, aApp)
        theEPG.add_bd(theBD)
        theEPG.add_infradomain(theVmmDomain)

        push_to_APIC()

        pushcount += 1
        count += 1
        rand = random.randint(10,18)
        if count >= rand:
            print ("--Number of SVIs created so far: {0}".format(str(pushcount)))
            count = 0

def push_to_APIC():
    global created_svis
    resp = theTenant.push_to_apic(session)

    if resp.ok:
        # Print some confirmation and info if you would like to see it in testing.
        # Uncomment the next lines if you want to see the configuration
        # print('URL: '  + str(tenant.get_url()))
        # print('JSON: ' + str(tenant.get_json()))
        return True

    else:
        print('Error on SVI: '  + str(pushing_svi))
        # print('JSON: ' + str(theTenant.get_json()))
        return False

def main():
    global session
    # Setup or credentials and session
    description = ('Converts an IOS config to ACI EPGs in a Applicaiton Profile.')
    creds = Credentials('apic', description)
    args = creds.get()

    readconfigfile()
    
    print "\n\n"
    # printsvis()

    # Login to APIC
    session = Session(args.url, args.login, args.password)
    session.login()

    # Get a Tenant name
    while not get_tenant():
            pass

    # Get a good Virtual Domain to use
    while not check_virtual_domain():
            collect_vmmdomain()
            

    print "\nPushing configuration into the APIC now.  Please wait."
    
    build_base()

    print ("\nCreated {} SVIs from a total of {} SVIs that we found.".format(pushcount, str(len(all_svi))))

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass