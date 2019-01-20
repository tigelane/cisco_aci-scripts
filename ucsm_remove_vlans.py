#!/usr/bin/env python

from ucsmsdk.ucshandle import UcsHandle

# Create a connection handle
handle = UcsHandle("172.xx.xx.xx", "admin", "cisco!098")

# Put in the VLANs you want to remove first one, and then the last one.
vlan_start = 400
vlan_end = 499
vlan_name_prefix = "vmware_client_"

# Login to the server
handle.login()


for a in range(vlan_start, vlan_end + 1):
    mydn = vlan_name_prefix + str(a)
    print "Removing " + (mydn)
    myfulldn = "fabric/lan/net-" + mydn

    # Query for an existing Mo
    sp = handle.query_dn(myfulldn)

    # Remove the object
    handle.remove_mo(sp)
    # and commit the changes (actually happens now)
    handle.commit()


# Logout from the server
handle.logout()
