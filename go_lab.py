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

	config = '''#
# DO NOT REMOVE ANY VALUES FROM THIS FILE!  Leave the string empty if you don't need it.
# Everything is a String and must be encapsulated in quotes as you see below.  Don't remove the quotes.
#
credentials = dict(
	accessmethod = 'https',
	ip_addr = '192.168.1.10',
    user = 'admin',
    # The password can be entered interactively.  It's ok to leave this empty
    password = 'Cisco!SecreT'
    )

leafs = dict(
	# This will create names like 'leaf-201'
	namebase = 'leaf',
	numberbase = '101',
	totalnumber = '2',
	)

spines = dict(
	# This will create names like 'spine-201'
	namebase = 'spine',
	numberbase = '201',
	totalnumber = '2',
	)

bgp = dict(
	# All spines will be used as BGP route reflectors.
	asnum = '65001'
	)

oob = dict(
	dg_mask = '192.168.1.1/24',
	start_ip = '192.168.1.100',
	end_ip = '192.168.1.199'
	)

time = dict(
	# These are defaults
	minpoll = '4',
	maxpoll = '6',
	server1 = 'pool.ntp.org',
	server2 = 'time1.google.com',
	server3 = ''
	)

dns = dict(
	# server1 will be preferred
	server1 = '8.8.8.8',
	server2 = '8.8.8.7',
	# search1 will be default
	search1 = 'yourorg.org',
	search2 = ''
	)
	'''
	config_file.write(config)
	config_file.close()
    
def collect_admin_info():

    if DEBUG:
        ip_addr = go_lab_config.credentials['accessmethod'] + '://' + go_lab_config.credentials['ip_addr']
        user = go_lab_config.credentials['user']
        password = go_lab_config.credentials['password']
        if password == '':
        	password = getpass.getpass('Administrative Password: ')
    else:
        ip_addr = raw_input('Name/Address of the APIC: ')
        user = raw_input('Administrative Login: ')
        password = getpass.getpass('Administrative Password: ')  
    
    return [ip_addr, user, password]

def login(ip_addr, user, password):
	# log into an APIC and create a directory object
	ls = cobra.mit.session.LoginSession(ip_addr, user, password)
	md = cobra.mit.access.MoDirectory(ls)
	md.login()
	return md

def create_bgp(md):
	asnum = go_lab_config.bgp['asnum']

	polUni = cobra.model.pol.Uni('')
	fabricInst = cobra.model.fabric.Inst(polUni)

	bgpInstPol = cobra.model.bgp.InstPol(fabricInst, ownerKey=u'', name=u'default', descr=u'', ownerTag=u'')
	bgpRRP = cobra.model.bgp.RRP(bgpInstPol, name=u'', descr=u'')
	bgpRRNodePEp = cobra.model.bgp.RRNodePEp(bgpRRP, id=u'201', descr=u'')
	bgpAsP = cobra.model.bgp.AsP(bgpInstPol, asn=asnum, descr=u'', name=u'')

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
	dg_mask = go_lab_config.oob['dg_mask']
	start_ip = go_lab_config.oob['start_ip']
	end_ip = go_lab_config.oob['end_ip']

	polUni = cobra.model.pol.Uni('')
	fvTenant = cobra.model.fv.Tenant(polUni, 'mgmt')

	fvnsAddrInst = cobra.model.fvns.AddrInst(fvTenant, ownerKey=u'', addr=dg_mask, descr=u'', skipGwVal=u'no', ownerTag=u'', name=u'Switch-OOB_addrs')
	fvnsUcastAddrBlk = cobra.model.fvns.UcastAddrBlk(fvnsAddrInst, to=end_ip, from_=start_ip, name=u'', descr=u'')

	c = cobra.mit.request.ConfigRequest()
	c.addMo(polUni)
	md.commit(c)
	return True

def create_oob_connGroup(md):
	polUni = cobra.model.pol.Uni('')
	infraInfra = cobra.model.infra.Infra(polUni)
	infraFuncP = cobra.model.infra.FuncP(infraInfra)

	mgmtGrp = cobra.model.mgmt.Grp(infraFuncP, name=u'Switch-OOB_conngrp')
	mgmtOoBZone = cobra.model.mgmt.OoBZone(mgmtGrp, name=u'', descr=u'')
	mgmtRsAddrInst = cobra.model.mgmt.RsAddrInst(mgmtOoBZone, tDn=u'uni/tn-mgmt/addrinst-Switch-OOB_addrs')
	mgmtRsOobEpg = cobra.model.mgmt.RsOobEpg(mgmtOoBZone, tDn=u'uni/tn-mgmt/mgmtp-default/oob-default')

	c = cobra.mit.request.ConfigRequest()
	c.addMo(polUni)
	md.commit(c)

	return True

def create_oob_nodeMgmt(md):
	polUni = cobra.model.pol.Uni('')
	infraInfra = cobra.model.infra.Infra(polUni)

	mgmtNodeGrp = cobra.model.mgmt.NodeGrp(infraInfra, ownerKey=u'', name=u'Switch-OOB_nodes', ownerTag=u'', type=u'range')
	mgmtRsGrp = cobra.model.mgmt.RsGrp(mgmtNodeGrp, tDn=u'uni/infra/funcprof/grp-Switch-OOB_conngrp')
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
	fabricRsPodPGrpBGPRRP = cobra.model.fabric.RsPodPGrpBGPRRP(fabricPodPGrp, tnBgpInstPolName=u'default')
	fabricRsTimePol = cobra.model.fabric.RsTimePol(fabricPodPGrp, tnDatetimePolName=u'default')

	# Feel free to uncomment if any of these are needed.
	# fabricRsSnmpPol = cobra.model.fabric.RsSnmpPol(fabricPodPGrp, tnSnmpPolName=u'')
	# fabricRsCommPol = cobra.model.fabric.RsCommPol(fabricPodPGrp, tnCommPolName=u'')
	# fabricRsPodPGrpCoopP = cobra.model.fabric.RsPodPGrpCoopP(fabricPodPGrp, tnCoopPolName=u'')
	# fabricRsPodPGrpIsisDomP = cobra.model.fabric.RsPodPGrpIsisDomP(fabricPodPGrp, tnIsisDomPolName=u'')

	c = cobra.mit.request.ConfigRequest()
	c.addMo(polUni)
	md.commit(c)

def create_pod_policy_profile(md):
	polUni = cobra.model.pol.Uni('')
	fabricInst = cobra.model.fabric.Inst(polUni)
	fabricPodP = cobra.model.fabric.PodP(fabricInst, 'default')

	fabricPodS = cobra.model.fabric.PodS(fabricPodP, ownerKey=u'', name=u'default', descr=u'', ownerTag=u'', type=u'ALL')
	fabricRsPodPGrp = cobra.model.fabric.RsPodPGrp(fabricPodS, tDn=u'uni/fabric/funcprof/podpgrp-PodPolicy')

	c = cobra.mit.request.ConfigRequest()
	c.addMo(polUni)
	md.commit(c)

def create_time_policy(md):
	minpoll = go_lab_config.time['minpoll']
	maxpoll = go_lab_config.time['maxpoll']
	server1 = go_lab_config.time['server1']
	server2 = go_lab_config.time['server2']
	server3 = go_lab_config.time['server3']

	polUni = cobra.model.pol.Uni('')
	fabricInst = cobra.model.fabric.Inst(polUni)

	datetimePol = cobra.model.datetime.Pol(fabricInst, ownerKey=u'', name=u'default', descr=u'', adminSt=u'enabled', authSt=u'disabled', ownerTag=u'')
	if server1:
		datetimeNtpProv = cobra.model.datetime.NtpProv(datetimePol, maxPoll=maxpoll, keyId=u'0', name=server1, descr=u'', preferred=u'no', minPoll=minpoll)
	if server2:
		datetimeNtpProv = cobra.model.datetime.NtpProv(datetimePol, maxPoll=maxpoll, keyId=u'0', name=server2, descr=u'', preferred=u'no', minPoll=minpoll)
	if server3:
		datetimeNtpProv = cobra.model.datetime.NtpProv(datetimePol, maxPoll=maxpoll, keyId=u'0', name=server3, descr=u'', preferred=u'no', minPoll=minpoll)
	
	datetimeRsNtpProvToEpg = cobra.model.datetime.RsNtpProvToEpg(datetimeNtpProv, tDn=u'uni/tn-mgmt/mgmtp-default/oob-default')

	c = cobra.mit.request.ConfigRequest()
	c.addMo(polUni)
	md.commit(c)

def create_dns_profile(md):
	server1 = go_lab_config.dns['server1']
	server2 = go_lab_config.dns['server2']
	search1 = go_lab_config.dns['search1']
	search2 = go_lab_config.dns['search2']

	polUni = cobra.model.pol.Uni('')
	fabricInst = cobra.model.fabric.Inst(polUni)

	dnsProfile = cobra.model.dns.Profile(fabricInst, ownerKey=u'', name=u'default', descr=u'', ownerTag=u'')
	dnsRsProfileToEpg = cobra.model.dns.RsProfileToEpg(dnsProfile, tDn=u'uni/tn-mgmt/mgmtp-default/oob-default')
	if server1:
		dnsProv = cobra.model.dns.Prov(dnsProfile, addr=server1, preferred=u'yes', name=u'')
	if server2:
		dnsProv = cobra.model.dns.Prov(dnsProfile, addr=server2, preferred=u'no', name=u'')
	if search1:
		dnsDomain = cobra.model.dns.Domain(dnsProfile, isDefault=u'yes', descr=u'', name=search1)
	if search2:
		dnsDomain = cobra.model.dns.Domain(dnsProfile, isDefault=u'no', descr=u'', name=search2)

	c = cobra.mit.request.ConfigRequest()
	c.addMo(polUni)
	md.commit(c)



	polUni = cobra.model.pol.Uni('')
	fvTenant = cobra.model.fv.Tenant(polUni, 'mgmt')
	fvCtx = cobra.model.fv.Ctx(fvTenant, ownerKey=u'', name=u'oob', descr=u'', knwMcastAct=u'permit', ownerTag=u'', pcEnfPref=u'enforced')
	dnsLbl = cobra.model.dns.Lbl(fvCtx, ownerKey=u'', tag=u'yellow-green', name=u'default', descr=u'', ownerTag=u'')


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
		global go_lab_config
		import go_lab_config
	except ImportError:
		print 'No config file found (go_lab_config.py).  Use "go_lab.py --makeconfig" to create a base file.'
		exit()
	except:
		print 'There is an error with your config file.  Please use the interactive interpreture to diagnose.'
		exit()

	# Login and get things going.  Use 'md' as our session.
	admin = collect_admin_info()
	md = login(admin[0],admin[1],admin[2])
	create_bgp(md)
	create_oob_policy(md)
	create_time_policy(md)
	create_pod_policy(md)
	create_pod_policy_profile(md)
	create_dns_profile(md)

	print "We're all done!"

if __name__ == '__main__':
    main(sys.argv)