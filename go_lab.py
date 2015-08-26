#!/usr/bin/env python
################################################
#   ________         .____          ___.       #
#  /  _____/  ____   |    |   _____ \_ |__     #
# /   \  ___ /  _ \  |    |   \__  \ | __ \    #
# \    \_\  (  <_> ) |    |___ / __ \| \_\ \   #
#  \______  /\____/  |_______ (____  /___  /   #
#         \/                 \/    \/    \/    #
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
    Create a basic BGP route reflector policy using the first two spine
    switches in the fabric.  All spines should be included before this
    is run.  The user will be asked for the BGP AS number 65001 will be
    offered as a default.

    WebArya was used to build most of REST code.
'''

# list of packages that should be imported for this code to work
import cobra.mit.access
import cobra.mit.session
import cobra.mit.request
import cobra.model.bgp
import cobra.model.pol
import cobra.model.fabric
import cobra.model.datetime
from cobra.internal.codec.xmlcodec import toXMLStr

DEBUG = False


def hello_message():
    print '\n'
    print 'Please be cautious with this application.  The author did very little error\nchecking and can\'t ensure it will work as expected.\n'
    return
    
def collect_admin_info():

    if DEBUG:
        ip_addr = ''
        user = ''
        password = ''
    else:
        ip_addr = raw_input('Name/Address of the APIC: ')
        user = raw_input('Administrative Login: ')
        password = getpass.getpass('Administrative Password: ')  
    
    return [ip_addr, user, password]

def login(ip_addr, user, password):
	# log into an APIC and create a directory object
	ip_addr = 'https://' + ip_addr
	ls = cobra.mit.session.LoginSession(ip_addr, user, password)
	md = cobra.mit.access.MoDirectory(ls)
	md.login()
	return md

def create_bgp(md):
	polUni = cobra.model.pol.Uni('')
	fabricInst = cobra.model.fabric.Inst(polUni)

	bgpInstPol = cobra.model.bgp.InstPol(fabricInst, ownerKey=u'', name=u'default', descr=u'', ownerTag=u'')
	bgpRRP = cobra.model.bgp.RRP(bgpInstPol, name=u'', descr=u'')
	bgpRRNodePEp = cobra.model.bgp.RRNodePEp(bgpRRP, id=u'201', descr=u'')
	bgpAsP = cobra.model.bgp.AsP(bgpInstPol, asn=u'65001', descr=u'', name=u'')

	c = cobra.mit.request.ConfigRequest()
	c.addMo(polUni)
	md.commit(c)

def create_pod_policy(md):
	polUni = cobra.model.pol.Uni('')
	fabricInst = cobra.model.fabric.Inst(polUni)
	fabricFuncP = cobra.model.fabric.FuncP(fabricInst)

	# build the request using cobra syntax
	fabricPodPGrp = cobra.model.fabric.PodPGrp(fabricFuncP, ownerKey=u'', name=u'PodPolicy', descr=u'', ownerTag=u'')
	fabricRsPodPGrpIsisDomP = cobra.model.fabric.RsPodPGrpIsisDomP(fabricPodPGrp, tnIsisDomPolName=u'')
	fabricRsPodPGrpBGPRRP = cobra.model.fabric.RsPodPGrpBGPRRP(fabricPodPGrp, tnBgpInstPolName=u'default')
	fabricRsTimePol = cobra.model.fabric.RsTimePol(fabricPodPGrp, tnDatetimePolName=u'default')
	fabricRsCommPol = cobra.model.fabric.RsCommPol(fabricPodPGrp, tnCommPolName=u'')
	fabricRsPodPGrpCoopP = cobra.model.fabric.RsPodPGrpCoopP(fabricPodPGrp, tnCoopPolName=u'')
	fabricRsSnmpPol = cobra.model.fabric.RsSnmpPol(fabricPodPGrp, tnSnmpPolName=u'LkoLab')


	# commit the generated code to APIC
	print toXMLStr(fabricFuncP)
	c = cobra.mit.request.ConfigRequest()
	c.addMo(polUni)
	md.commit(c)

def create_time_policy(md):
	polUni = cobra.model.pol.Uni('')
	fabricInst = cobra.model.fabric.Inst(polUni)

	datetimePol = cobra.model.datetime.Pol(fabricInst, ownerKey=u'', name=u'default', descr=u'', adminSt=u'enabled', authSt=u'disabled', ownerTag=u'')
	datetimeNtpProv = cobra.model.datetime.NtpProv(datetimePol, maxPoll=u'6', keyId=u'0', name=u'172.18.108.16', descr=u'', preferred=u'no', minPoll=u'4')
	datetimeRsNtpProvToEpg = cobra.model.datetime.RsNtpProvToEpg(datetimeNtpProv, tDn=u'uni/tn-mgmt/mgmtp-default/oob-default')

	c = cobra.mit.request.ConfigRequest()
	c.addMo(polUni)
	md.commit(c)

def main():
    global admin
    hello_message()

    # Login and get things going.  Use 'md' as our session.
    admin = collect_admin_info()
    md = login(admin[0],admin[1],admin[2])

    create_bgp(md)
    create_time_policy(md)
    create_pod_policy(md)

    print "We're all done!"

if __name__ == '__main__':
    main()