#!/usr/bin/env python
################################################################################
#   ________ ________    ___________ _____________  ___                        #
#  /  _____/ \_____  \   \_   _____//   _____/\   \/  /                        #
# /   \  ___  /   |   \   |    __)_ \_____  \  \     /                         #
# \    \_\  \/    |    \  |        \/        \ /     \                         #
#  \______  /\_______  / /_______  /_______  //___/\  \                        #
#         \/         \/          \/        \/       \_/                        #
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
#    This work contains code from: https://github.com/datacenter/acitoolkit    #
#                                                                              #
################################################################################
'''
    Create an environment for VMware in an ACI fabric.

    1. VMware VMM setup
    2. VMM VLAN pool
    3. Physical interface configs
    4. Switch and Interface linkage from VMM to physical

    Additional ESXi servers can be added in the Interface Policies 

'''

# Cisco ACI Cobra packages
import cobra.mit.access
import cobra.mit.request
import cobra.mit.session
import cobra.model.cdp
import cobra.model.fabric
import cobra.model.infra
import cobra.model.lldp
import cobra.model.pol
import cobra.model.vz
import cobra.model.fvns
import cobra.model.fv

from cobra.internal.codec.xmlcodec import toXMLStr

# ACI Toolkit packages
import acitoolkit.acitoolkit as ACI

# All the other stuff we need.
import sys, random, string

def hello_message():
    print "\nPlease be cautious with this application.  The author did very little error checking and can't ensure it will work as expected.\n"
    junk = raw_input('Press Enter/Return to continue.')
    return

def load_utils():
	try:
		global GO
		import go_utils as GO
	except:
		print 'Can not find go_utils.py.  This file is required.'
		exit()

def load_config():
	try:
		global GO_CONFIG
		import go_lab_config as GO_CONFIG

	except ImportError:
		print 'No config file found (go_lab_config.py).  Use "--makeconfig" to create a base file.'
		exit()
	except:
		print 'There is syntax error with your config file.  Please use the python interactive interpreture to diagnose. (python; import go_lab_config)'
		exit()
def create_vmm_domain(session):
	# Define dynamic vlan range
	pool_name = GO_CONFIG.vmware_vmm['namebase'] + '-esx_vlans'
	encap = 'vlan'
	mode = 'dynamic'
	vlans = ACI.NetworkPool(pool_name, encap, GO_CONFIG.vmware_vmm['vlan_start'], GO_CONFIG.vmware_vmm['vlan_end'], mode)

	# Commit VLAN Range
	vlanresp = session.push_to_apic(vlans.get_url(), vlans.get_json())

	if not vlanresp.ok:
		print('%% Error: Could not push VLAN configuration to APIC')
		print(vlanresp.text)
		exit()

	# Create Credentials object
	vcenter_creds = ACI.VMMCredentials(GO_CONFIG.vmware_vmm['user'], GO_CONFIG.vmware_vmm['user'], GO_CONFIG.vmware_vmm['password'])

	# Vswitch Info object
	vmmtype = 'VMware'
	dvs_name = GO_CONFIG.vmware_vmm['namebase'] + '-' + GO_CONFIG.vmware_vmm['datacenter']
	vswitch_info = ACI.VMMvSwitchInfo(vmmtype, GO_CONFIG.vmware_vmm['datacenter'], dvs_name)

	# Create VMM object
	vmm_name = dvs_name
	vmm = ACI.VMM(vmm_name, GO_CONFIG.vmware_vmm['vcenterip'], vcenter_creds, vswitch_info, vlans)

	# Commit Changes
	resp = session.push_to_apic(vmm.get_url(), vmm.get_json())

	if not resp.ok:
		print('%% Error: Could not push VMM configuration to APIC')
		print(resp.text)
		exit()

def create_int_basics(cobra_md):
	global int_name, cdp_name, lldp_name
	int_name = GO_CONFIG.vmware_vmm['namebase'] + '-link'
	link_speed = GO_CONFIG.esxi_servers['speed'] + 'G'
	cdp_name = GO_CONFIG.vmware_vmm['namebase'] + '-cdp'
	lldp_name = GO_CONFIG.vmware_vmm['namebase'] + '-lldp'
	lldp_state = GO_CONFIG.esxi_servers['lldp']

	polUni = cobra.model.pol.Uni('')
	infraInfra = cobra.model.infra.Infra(polUni)
	
	# build the request using cobra syntax
	fabricHIfPol = cobra.model.fabric.HIfPol(infraInfra, ownerKey=u'', name=int_name, descr=u'', ownerTag=u'', autoNeg=u'on', speed=link_speed, linkDebounce=u'100')
	cdpIfPol = cobra.model.cdp.IfPol(infraInfra, ownerKey=u'', name=cdp_name, descr=u'', adminSt=GO_CONFIG.esxi_servers['cdp'], ownerTag=u'')
	lldpIfPol = cobra.model.lldp.IfPol(infraInfra, ownerKey=u'', name=lldp_name, descr=u'', adminTxSt=lldp_state, adminRxSt=lldp_state, ownerTag=u'')

	# commit the generated code to APIC
	c = cobra.mit.request.ConfigRequest()
	c.addMo(polUni)
	cobra_md.commit(c)

def create_aaep(cobra_md):
	global aaep_name
	aaep_name = GO_CONFIG.vmware_vmm['namebase'] + '-aaep'
	vmm_domain = 'uni/vmmp-VMware/dom-' + GO_CONFIG.vmware_vmm['namebase'] + '-' + GO_CONFIG.vmware_vmm['datacenter']

	polUni = cobra.model.pol.Uni('')
	infraInfra = cobra.model.infra.Infra(polUni)

	# build the request using cobra syntax
	infraAttEntityP = cobra.model.infra.AttEntityP(infraInfra, ownerKey=u'', name=aaep_name, descr=u'', ownerTag=u'')
	infraRsDomP = cobra.model.infra.RsDomP(infraAttEntityP, tDn=vmm_domain)

	c = cobra.mit.request.ConfigRequest()
	c.addMo(polUni)
	cobra_md.commit(c)

def create_int_polgrp(cobra_md):
	global intgrp_name
	intgrp_name = GO_CONFIG.vmware_vmm['namebase'] + '-int_polgrp'
	dnattach_point = 'uni/infra/attentp-' + aaep_name

	polUni = cobra.model.pol.Uni('')
	infraInfra = cobra.model.infra.Infra(polUni)
	infraFuncP = cobra.model.infra.FuncP(infraInfra)

	infraAccPortGrp = cobra.model.infra.AccPortGrp(infraFuncP, ownerKey=u'', name=intgrp_name, descr=u'', ownerTag=u'')
	#infraRsMonIfInfraPol = cobra.model.infra.RsMonIfInfraPol(infraAccPortGrp, tnMonInfraPolName=u'')
	infraRsLldpIfPol = cobra.model.infra.RsLldpIfPol(infraAccPortGrp, tnLldpIfPolName=lldp_name)
	#infraRsStpIfPol = cobra.model.infra.RsStpIfPol(infraAccPortGrp, tnStpIfPolName=u'')
	#infraRsL2IfPol = cobra.model.infra.RsL2IfPol(infraAccPortGrp, tnL2IfPolName=u'')
	infraRsCdpIfPol = cobra.model.infra.RsCdpIfPol(infraAccPortGrp, tnCdpIfPolName=cdp_name)
	#infraRsMcpIfPol = cobra.model.infra.RsMcpIfPol(infraAccPortGrp, tnMcpIfPolName=u'')
	infraRsAttEntP = cobra.model.infra.RsAttEntP(infraAccPortGrp, tDn=dnattach_point)
	#infraRsStormctrlIfPol = cobra.model.infra.RsStormctrlIfPol(infraAccPortGrp, tnStormctrlIfPolName=u'')
	infraRsHIfPol = cobra.model.infra.RsHIfPol(infraAccPortGrp, tnFabricHIfPolName=int_name)

	c = cobra.mit.request.ConfigRequest()
	c.addMo(polUni)
	cobra_md.commit(c)

def create_int_profile(cobra_md):
	global intpro_name
	intpro_name = GO_CONFIG.vmware_vmm['namebase'] + '-int_pro'
	sel_name = GO_CONFIG.vmware_vmm['namebase'] + '-int-sel'
	dnintgrp_name = 'uni/infra/funcprof/accportgrp-' + intgrp_name

	fromcard = GO_CONFIG.esxi_servers['interfaces'].split('/')[0]
	tocard = GO_CONFIG.esxi_servers['interfaces'].split('/')[0]
	fromport = GO_CONFIG.esxi_servers['interfaces'].split('/')[1].split('-')[0]
	toport = GO_CONFIG.esxi_servers['interfaces'].split('/')[1].split('-')[1]

	polUni = cobra.model.pol.Uni('')
	infraInfra = cobra.model.infra.Infra(polUni)

	infraAccPortP = cobra.model.infra.AccPortP(infraInfra, ownerKey=u'', name=intpro_name, descr=u'', ownerTag=u'')
	infraHPortS = cobra.model.infra.HPortS(infraAccPortP, ownerKey=u'', type=u'range', name=sel_name, descr=u'', ownerTag=u'')
	infraRsAccBaseGrp = cobra.model.infra.RsAccBaseGrp(infraHPortS, fexId=u'101', tDn=dnintgrp_name)
	infraPortBlk = cobra.model.infra.PortBlk(infraHPortS, name=u'block1', descr=u'', fromPort=fromport, fromCard=fromcard, toPort=toport, toCard=tocard)

	c = cobra.mit.request.ConfigRequest()
	c.addMo(polUni)
	cobra_md.commit(c)

def get_leafs(session):
    from acitoolkit.aciphysobject import Node
    data = []

    items = Node.get(session)
    for item in items:
        if item.role == 'leaf':
        	data.append(item.node)
    
    return data

def create_sw_profile(cobra_md, leafs):
	swproname = GO_CONFIG.vmware_vmm['namebase'] + '-sw_pro'
	dnintpro_name = 'uni/infra/accportprof-' + intpro_name


	polUni = cobra.model.pol.Uni('')
	infraInfra = cobra.model.infra.Infra(polUni)

	for leaf in leafs:
		blockname = [random.choice(string.hexdigits).lower() for n in xrange(16)]
		blockname = ''.join(blockname)
		b_name = 'leaf-' + leaf

		infraNodeP = cobra.model.infra.NodeP(infraInfra, ownerKey=u'', name=swproname, descr=u'', ownerTag=u'')
		infraLeafS = cobra.model.infra.LeafS(infraNodeP, ownerKey=u'', type=u'range', name=b_name, descr=u'', ownerTag=u'')
		infraNodeBlk = cobra.model.infra.NodeBlk(infraLeafS, from_=leaf, name=blockname, descr=u'', to_=leaf)
		infraRsAccPortP = cobra.model.infra.RsAccPortP(infraNodeP, tDn=dnintpro_name)

		c = cobra.mit.request.ConfigRequest()
		c.addMo(polUni)
		cobra_md.commit(c)

def build_filters(cobra_md, s_tenant, s_app):
    polUni = cobra.model.pol.Uni('')
    fvTenant = cobra.model.fv.Tenant(polUni, s_tenant)

    # for filt in filters:
    #     entry = ACI.FilterEntry(filt[0],
    #                      applyToFrag='no',
    #                      arpOpc='unspecified',
    #                      dFromPort=filt[2],
    #                      dToPort=filt[2],
    #                      etherT='ip',
    #                      prot=filt[1],
    #                      tcpRules='unspecified',
    #                      parent=contract)
    

    contract = cobra.model.vz.BrCP(fvTenant, ownerKey=u'', name=s_app['contract'], prio=u'unspecified', ownerTag=u'', descr=u'')
    subject = cobra.model.vz.Subj(contract, revFltPorts=u'yes', name=s_app['contract'], prio=u'unspecified', descr=u'', consMatchT=u'AtleastOne', provMatchT=u'AtleastOne')
    s_filter = cobra.model.vz.Filter(fvTenant, ownerKey=u'', name=s_app['contract'], descr=u'', ownerTag=u'')

    for filt in s_app['filters']:
        vzEntry = cobra.model.vz.Entry(s_filter, tcpRules=u'', arpOpc=u'unspecified', applyToFrag=u'no', dToPort=filt[2], descr=u'', prot=filt[1], icmpv4T=u'unspecified', sFromPort=u'unspecified', stateful=u'no', icmpv6T=u'unspecified', sToPort=u'unspecified', etherT=u'ip', dFromPort=filt[2], name=filt[0])
    
    vzRsSubjFiltAtt = cobra.model.vz.RsSubjFiltAtt(subject, tnVzFilterName=s_app['contract'])

    c = cobra.mit.request.ConfigRequest()
    c.addMo(polUni)
    cobra_md.commit(c)

def create_common(session, cobra_md):
    # Objects for the Vcenter servers in the common Tenant
    s_tenant = 'My_Common-2'
    s_pn = 'VMware_Infra_PN'
    s_bd = 'VMware_Infra_BD'
    subnet_scope = 'private,shared'

    s_app_1 = {'appname': 'VMware-MGMT', 'epgname':'VCenter', 'contract':'vcenter_clients', 'filters':[['HTTPS', 'tcp', '443'], ['HTTP', 'tcp', '80'], ['SSH', 'tcp', '22']]}
    s_app_2 = {'appname': 'Shared_Services', 'epgname':'Services_Servers', 'contract':'shared_services','filters':[['LDAP_0', 'tcp', '389'], ['LDAP_1', 'udp', '389'], ['SMB_0', 'tcp', '445'], ['SMB_2', 'tcp', '137'], ['SMB_3', 'udp', '137'], ['SMB_4', 'udp','138'], ['SMB_4', 'tcp', '139'], ['DNS_0', 'tcp', '53'], ['DNS_1', 'udp', '53'], ['NTP', 'udp', '123'], ['SNMP_0', 'udp', '161'], ['SNMP_1', 'udp', '162'], ['SNMP_2', 'tcp', '162']]}
    s_app_3 = {'appname': 'IP_Storage', 'epgname':'Storage_Arrays', 'contract':'ip_storage','filters':[['iSCSI_0', 'tcp', '860'], ['iSCSI_1', 'tcp', '3260'], ['NFS_0', 'tcp', '111'], ['NFS_1', 'udp', '111'], ['NFS_2', 'tcp', '2049'],['NFS_3', 'udp','2049']]}
    s_app_4 = {'appname': 'VMware-MGMT', 'epgname':'VCenter', 'contract':'vcenter_esxi','filters':[['HTTPS', 'tcp', '443'], ['HTTP', 'tcp', '80'], ['SSH', 'tcp', '22']]}

    # IP Segments must be the default IP Address for devices on the ip segement with appropriate /subnet mask notation.
    ip_segments = ['10.1.1.1/24', '192.168.1.1/24']

    # Connect to the VMM Domain
    # This must already exist and should have been created in this script
    vmmdomain = 'VMware-LL'

    # Connect to the virtual domain we are going to use
    vdomain = ACI.EPGDomain.get_by_name(session,vmmdomain)

    # Associate the tenant
    tenant = ACI.Tenant(s_tenant)
    app_1 = ACI.AppProfile(s_app_1['appname'], tenant)
    app_2 = ACI.AppProfile(s_app_2['appname'], tenant)
    app_3 = ACI.AppProfile(s_app_3['appname'], tenant)

    # Create the EPGs
    epg_1 = ACI.EPG(s_app_1['epgname'], app_1)
    epg_2 = ACI.EPG(s_app_2['epgname'], app_2)
    epg_3 = ACI.EPG(s_app_3['epgname'], app_3)

    # Create a Context (private network) and Bridge Domain
    # Add the IP Segments to the brdige domain
    context = ACI.Context(s_pn, tenant)
    bd = ACI.BridgeDomain(s_bd, tenant)
    for subnet_ip in ip_segments:
        ran_name = [random.choice(string.hexdigits).lower() for n in xrange(6)]
        sub_name = ''.join(ran_name)
        subnet = ACI.Subnet(sub_name, bd)
        subnet.set_addr(subnet_ip)
        subnet.set_scope(subnet_scope)
        bd.add_subnet(subnet)

    # Place all EPGs in the Context and in the same BD
    epg_1.add_bd(bd)
    epg_1.add_infradomain(vdomain)
    epg_2.add_bd(bd)
    epg_2.add_infradomain(vdomain)
    epg_3.add_bd(bd)
    # This EPG probably contains physcial disk arrays that will be attached to a leaf so I'm not creating it in the VMMDomain

    ''' 
    Define contracts and make filters
    '''
    contract_1 = ACI.Contract(s_app_1['contract'], tenant)
    build_filters(cobra_md, s_tenant, s_app_1)
    contract_2 = ACI.Contract(s_app_2['contract'], tenant)
    build_filters(cobra_md, s_tenant, s_app_2)
    contract_3 = ACI.Contract(s_app_3['contract'], tenant)
    build_filters(cobra_md, s_tenant, s_app_3)
    contract_4 = ACI.Contract(s_app_4['contract'], tenant)
    build_filters(cobra_md, s_tenant, s_app_4)


    ''' 
    Attach the contracts ---   NEED TO WORK ON THIS
    '''
    epg_1.provide(contract_1)
    epg_2.provide(contract_2)
    epg_3.provide(contract_3)
    epg_1.provide(contract_4)

    epg_1.consume(contract_2)
    epg_3.consume(contract_2)


    # Push all of this to the APIC
    print tenant
    resp = tenant.push_to_apic(session)

    if resp.ok:
        # Uncomment the next lines if you want to see the configuration
        # print('URL: '  + str(tenant.get_url()))
        # print('JSON: ' + str(tenant.get_json()))
        return True
    else:
        print resp.text
        print "\n\n"
        print('JSON: ' + str(tenant.get_json()))
        return False

def create_unique(session):
    # Objects for the ESXi servers in a tenant
    unique_tenant = 'ESXi-Tenant'
    uni_pn = 'ESXi_PN'
    uni_bd = 'ESXi_BD'
    uni_app = 'ESXi_mgmt'
    uni_1_epg = 'Management'
    uni_2_epg = 'VMotion'
    uni_3_epg = 'Storage_acc'
    ip_segments = ['10.1.2.1/24']

    # Valid options for the scape are 'private', 'public', and 'shared'.  Comma seperated, and NO spaces
    subnet_scope = 'private,shared'

    # Connect to the VMM Domain
    # This must already exist.  It should have been created in this script
    vmmdomain = 'VMware-LL'

    # Get the virtual domain we are going to use
    vdomain = ACI.EPGDomain.get_by_name(session,vmmdomain)
    tenant = ACI.Tenant(unique_tenant)
    app = ACI.AppProfile(uni_app, tenant)

    # Create the EPGs
    u1_epg = ACI.EPG(uni_1_epg, app)
    u2_epg = ACI.EPG(uni_2_epg, app)
    u3_epg = ACI.EPG(uni_3_epg, app)

    # Create a Context and BridgeDomain
    # Place all EPGs in the Context and in the same BD
    context = ACI.Context(uni_pn, tenant)
    ubd = ACI.BridgeDomain(uni_bd, tenant)
    ubd.add_context(context)
    for subnet_ip in ip_segments:
        ran_name = [random.choice(string.hexdigits).lower() for n in xrange(6)]
        sub_name = ''.join(ran_name)
        subnet = Subnet(sub_name, ubd)
        subnet.set_addr(subnet_ip)
        subnet.set_scope(subnet_scope)
        ubd.add_subnet(subnet)

    u1_epg.add_bd(ubd)
    u1_epg.add_infradomain(vdomain)
    u2_epg.add_bd(ubd)
    u2_epg.add_infradomain(vdomain)
    u3_epg.add_bd(ubd)

    ''' 
    Define contracts with a multiple entries
    '''
    contract1 = ACI.Contract('esxi_clients', tenant)
    filters = [
            ['HTTPS','443','tcp'],
            ['HTTP','80','tcp'],
            ['SSH','22','tcp']
            ]
    for filt in filters:
        entry = ACI.FilterEntry(filt[0],
                         applyToFrag='no',
                         arpOpc='unspecified',
                         dFromPort=filt[1],
                         dToPort=filt[1],
                         etherT='ip',
                         prot=filt[2],
                         tcpRules='unspecified',
                         parent=contract1)
                        
    # Attach the contracts
    u1_epg.provide(contract1)

    # CAUTION:  The next line will DELETE the tenant
    # tenant.mark_as_deleted()
    resp = tenant.push_to_apic(session)

    if resp.ok:
        # Uncomment the next lines if you want to see the configuration
        # print('URL: '  + str(tenant.get_url()))
        # print('JSON: ' + str(tenant.get_json()))
        return True
    else:
        return False


def main(argv):
	hello_message()
	if len(argv) > 1:
		load_utils()
		if argv[1] == '--makeconfig':
			GO.create_configfile()
			exit()

	# Login and setup sessions  
	# admin_info contains the URL, Username, and Password (in clear text)
	# Use 'cobramd' as our session for Cobra interface 
	# Use 'session' as the session for the ACI Toolkit.
	load_utils()
	load_config()

	admin_info = GO.collect_admin(GO_CONFIG)
	cobra_md = GO.cobra_login(admin_info)
	session = GO.toolkit_login(admin_info)

	# create_vmm_domain(session)
	# create_int_basics(cobra_md)
	# create_aaep(cobra_md)
	# create_int_polgrp(cobra_md)
	# create_int_profile(cobra_md)

	# leafs = get_leafs(session)
	# create_sw_profile(cobra_md, leafs)
	create_common(session, cobra_md)
	# create_unique(session)

	print 'Well, that saved a lot of clicking!'


if __name__ == '__main__':
    main(sys.argv)