package main

import (
	"fmt"
	"github.com/ignw/cisco-aci-go-sdk/src/service"
	"github.com/ignw/cisco-aci-go-sdk/src/models"
    "os"
)

func main() {
	var client *service.Client
	var tenant *models.Tenant
    var appProfile *models.AppProfile
    var epg *models.EPG
    var contract *models.Contract
    var bridgedomain *models.BridgeDomain
	var err error

    // Setup a Client to maintain a connection to the APIC
	client = service.GetClient()

    //  Create new Tenant
    //  Define the new Tenant
    tenant = client.Tenants.New("Example-Tenant", "This is an example tenant")
    // Save the new Tenant to the APIC
    _, err = client.Tenants.Save(tenant)
    if err != nil {
        fmt.Printf("Error creating tenant: %s", err.Error())
        client.Tenants.Delete("uni/tn-Example-Tenant")
        fmt.Printf("Tenant deleted.")
        os.Exit(2)
    } else {
        fmt.Println("Successfully created new tenant!")
    }

    //  Create new Application Profile
    //  Define the new Application Profile
    appProfile = client.AppProfiles.New("Example-AppProfile", "This is an example Application Profile")
    // Link the Application Profile to the Tenant
    tenant.AddAppProfile(appProfile)
    // Save the new Application Profile to the APIC
    _, err = client.AppProfiles.Save(appProfile)

	if err != nil {
		fmt.Printf("Error creating appProfile: %s", err.Error())
	} else {
		fmt.Println("Successfully created new appProfile!")
	}

    //  Create new End-Point Group
    //  Define the new End-Point Group
    epg = client.EPGs.New("Example-EPG", "This is an example End-Point Group")
    //  Set attributes of the EPG
    epg.IsAttributeBased = false
    epg.PreferredPolicyControl = "unenforced"
    epg.LabelMatchCriteria = "All"
    epg.IsPreferredGroupMember = "exclude"


    // Link the End-Point Group to the Application Profile
    appProfile.AddEPG(epg)
    // Save the new End-Point Group to the APIC
    _, err = client.EPGs.Save(epg)

	if err != nil {
		fmt.Printf("Error creating End-Point Group: %s", err.Error())
	} else {
		fmt.Println("Successfully created new End-Point Group!")
	}

    //  Create new Contract
    //  Define the new Contract
    contract = client.Contracts.New("Example-Contract", "This is an example of a Contract")
    //  Set attributes of the EPG
    contract.Scope = "application-profile"
    // Link the Contract to the Tenant
    tenant.AddContract(contract)
    // Save the new Contract to the APIC
    _, err = client.Contracts.Save(contract)

	if err != nil {
		fmt.Printf("Error creating Contract: %s", err.Error())
	} else {
		fmt.Println("Successfully created new Contract!")
	}

    //  Create new Bridge Domain
    //  Define the new Bridge Domain
    bridgedomain = client.BridgeDomains.New("Example-BridgeDomain", "This is an example of a Bridge Domain")
    //bridgedomain.Scope = "application-profile"
    // Link the Bridge Domain to the Tenant
    tenant.AddBridgeDomain(bridgedomain)
    // Save the new Contract to the APIC
    _, err = client.BridgeDomains.Save(bridgedomain)

    if err != nil {
        fmt.Printf("Error creating Bridge Domain: %s", err.Error())
    } else {
        fmt.Println("Successfully created new Bridge Domain!")
    }
}
