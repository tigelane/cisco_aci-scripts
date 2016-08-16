#
# DO NOT REMOVE ANY VALUES FROM THIS FILE!  Leave the string empty if you don't need it.
# Everything is a String and must be encapsulated in quotes as you see below.  Don't remove the quotes.
#
credentials = dict(
    accessmethod = 'https',
    ip_addr = '172.31.0.10',
    user = 'admin',
    # The password can be entered interactively.  It's ok to make this empty.
    password = 'cisco!098'
    )

leafs = dict(
    # This will create names like 'leaf-201'
    namebase = 'leaf',
    numberbase = '201',
    totalnumber = '2',
    )

spines = dict(
    # This will create names like 'spine-101'
    namebase = 'spine',
    numberbase = '101',
    totalnumber = '1',
    )

bgp = dict(
    # All spines will be used as BGP route reflectors.
    asnum = '65001'
    )

oob = dict(
    dg_mask = '172.31.0.1/24',
    start_ip = '172.31.0.12',
    end_ip = '172.31.0.19'
    )

time = dict(
    # Poll rate values are default, up to 10 servers will be accepted
    minpoll = '4',
    maxpoll = '6',
    server0 = '0.pool.ntp.org',
    server1 = '1.pool.ntp.org'
    )

dns = dict(
    # server0 will be preferred, up to 10 servers will be accepted
    server0 = '8.8.8.8',
    server1 = '8.8.8.7',
    server2 = '',

    # search0 will be default, up to 10 domains will be accepted
    search0 = 'lab.convergeone.com',
    search1 = ''
    )

vmware_vmm = dict(
    # namebase will be used to start the naming of everything releated to VMware
    namebase = 'c1_lko-lab',
    vcenterip = '172.31.0.20',
    vlan_start = '2000',
    vlan_end = '2099',
    user = 'administrator',
    password = 'cisco!098',
    datacenter = 'ACI_Lab'
    )

esxi_servers = dict(
    # Interface speed can be 1 or 10
    speed = '10',
    cdp = 'enabled',
    lldp = 'disabled',
    # Interface configuration will be attached to all leaf switches
    # Only a single interface statement can be used in this script
    # valid values: 1/13 or 1/22-24
    interfaces = '1/17-18'
    )