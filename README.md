cisco_aci-scripts
=========
Requirements: 
    Python 2.7+
    Cisco ACItoolkit https://github.com/datacenter/acitoolkit
    
Repository for work creating setup scripts for ACI

1.  aci_miniapps.py
    This is a conglomoration mostly of the sample scripts in git - datacenter/acitoolkit.
    I have built a scripted front end and a small menu to select items.  I also use a credentials.py
    file that is insecure.

2.  create_full-tenant.py
    This application was written very early in the ACI days.
    The goal of this application is to create a large number of Tenants and associated Security Domain.
    This creates virtual users that can then access the system in an isolated environment.
    **  This would work well for building ACI labs  **
    It then creates a local user with full admin access to that Tenant.
    I have also put some pauses in the script so that you could use it to show a customer
    that the items are being built in the APIC before moving to the next item.
    
    Please note that very little error checking is being done.  It's entirely possible 
    that this code could crash your system (not likely).  You have been warned!

3.  create_three-tier.py
    Create a three tier application along with associated Tenant, Bridge Domain
    Private Network.  If they do not exist they will be created.
    Associate the three tires to a VMM domain.
    Create simple contracts between each layer.
