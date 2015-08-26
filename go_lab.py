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
import cobra.model.mgmt
import cobra.model.infra
import cobra.model.fvns
from cobra.internal.codec.xmlcodec import toXMLStr

import sys
import getpass

DEBUG = True


def hello_message():
    print "\nPlease be cautious with this application.  The author did very little error checking and can't ensure it will work as expected.\n"
    junk = raw_input('Press Enter/Return to continue.')
    return

def create_configfile():
	config_file = open('go_lab_config.py', 'w')

	config = '''credentials = dict(
		ip_addr = '10.93.130.125',
    	user = 'tige',
    	password = 'Cisco098'
    	)

leafs = dict(
		namebase = 'leaf',
		numberbase = 101,
		totalnumber = 2,
		)

spines = dict(
		namebase = 'spine',
		numberbase = 201,
		totalnumber = 2,
		)

bgp = dict(
		asnum = '65001'
		# All spines will be used.
		)
	'''
	config_file.write(config)
	config_file.close()
    
def collect_admin_info():

    if DEBUG:
        ip_addr = '10.93.130.125'
        user = 'tige'
        password = 'Cisco098'
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

def create_oob_policy(md):
    if not create_oob_ipPool(md):
    	return False
    if not create_oob_connGroup(md):
    	return False
    if not create_oob_nodeMgmt(md):
    	return False

def create_oob_ipPool(md):
	polUni = cobra.model.pol.Uni('')
	fvTenant = cobra.model.fv.Tenant(polUni, 'mgmt')

	fvnsAddrInst = cobra.model.fvns.AddrInst(fvTenant, ownerKey=u'', addr=u'10.93.130.127/24', descr=u'', skipGwVal=u'no', ownerTag=u'', name=u'Switch-OOBoobaddr')
	fvnsUcastAddrBlk = cobra.model.fvns.UcastAddrBlk(fvnsAddrInst, to=u'10.93.130.199', from_=u'10.93.130.195', name=u'', descr=u'')

	c = cobra.mit.request.ConfigRequest()
	c.addMo(polUni)
	md.commit(c)
	return True

def create_oob_connGroup(md):
	polUni = cobra.model.pol.Uni('')
	infraInfra = cobra.model.infra.Infra(polUni)
	infraFuncP = cobra.model.infra.FuncP(infraInfra)

	mgmtGrp = cobra.model.mgmt.Grp(infraFuncP, name=u'Switch-OOB')
	mgmtOoBZone = cobra.model.mgmt.OoBZone(mgmtGrp, name=u'', descr=u'')
	mgmtRsAddrInst = cobra.model.mgmt.RsAddrInst(mgmtOoBZone, tDn=u'uni/tn-mgmt/addrinst-Switch-OOBoobaddr')
	mgmtRsOobEpg = cobra.model.mgmt.RsOobEpg(mgmtOoBZone, tDn=u'uni/tn-mgmt/mgmtp-default/oob-default')

	c = cobra.mit.request.ConfigRequest()
	c.addMo(polUni)
	md.commit(c)

	return True

def create_oob_nodeMgmt(md):
	polUni = cobra.model.pol.Uni('')
	infraInfra = cobra.model.infra.Infra(polUni)

	mgmtNodeGrp = cobra.model.mgmt.NodeGrp(infraInfra, ownerKey=u'', name=u'Switch-OOB', ownerTag=u'', type=u'range')
	mgmtRsGrp = cobra.model.mgmt.RsGrp(mgmtNodeGrp, tDn=u'uni/infra/funcprof/grp-Switch-OOB')
	infraNodeBlk = cobra.model.infra.NodeBlk(mgmtNodeGrp, from_=u'101', name=u'61894b1293c1f36f', to_=u'101')
	infraNodeBlk3 = cobra.model.infra.NodeBlk(mgmtNodeGrp, from_=u'102', name=u'ddddc0b616224e1b', to_=u'102')
	infraNodeBlk4 = cobra.model.infra.NodeBlk(mgmtNodeGrp, from_=u'103', name=u'd34dc0b616224e1b', to_=u'103')
	infraNodeBlk5 = cobra.model.infra.NodeBlk(mgmtNodeGrp, from_=u'104', name=u'13a4dfaa330fb166', to_=u'104')
	infraNodeBlk2 = cobra.model.infra.NodeBlk(mgmtNodeGrp, from_=u'201', name=u'5277f3fd527d1725', to_=u'201')
	infraNodeBlk6 = cobra.model.infra.NodeBlk(mgmtNodeGrp, from_=u'202', name=u'5277f3fd527ag983', to_=u'202')

	c = cobra.mit.request.ConfigRequest()
	c.addMo(polUni)
	md.commit(c)

	return True

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

def main(argv):
	hello_message()
	if len(argv) > 1:
		if argv[1] == '--makeconfig':
			create_configfile()
			exit()
	try:
		import go_lab_config
	except ImportError:
		print 'No config file found (go_lab_config.py).  Use "go_lab.py --makeconfig" to create a base file.'
		exit()
	except:
		print 'There is an error with your config file.  Please use the interactive interpreture to diagnose.'
		exit()

	# Login and get things going.  Use 'md' as our session.
	# admin = collect_admin_info()
	# md = login(admin[0],admin[1],admin[2])
	# create_bgp(md)
	# create_oob_policy(md)
	# create_time_policy(md)
	# create_pod_policy(md)

	print "We're all done!"

if __name__ == '__main__':
    main(sys.argv)