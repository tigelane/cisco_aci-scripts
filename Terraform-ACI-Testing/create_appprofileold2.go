package main

import (
	"fmt"
	"github.com/ignw/cisco-aci-go-sdk/src/service"
	"github.com/ignw/cisco-aci-go-sdk/src/models"
    "os"
)

func addTenant(tenant *models.Tenant, client *service.Client) {
    //  Create new Tenant
    //  Define the new Tenant
    var err error

    tenant = client.Tenants.New("Example-Tenant", "This is an example tenant")
    // Save the new Tenant to the APIC
    err = client.Tenants.Save(tenant)
    if err != nil {
        fmt.Printf("Error creating tenant: %s", err.Error())
        os.Exit(2)
    } else {
        fmt.Println("Successfully created new tenant!")
    }
}

func addAppProfile() {
    //  Create new Application Profile
    //  Define the new Application Profile
    appProfile = client.AppProfiles.New("Example-AppProfile", "This is an example Application Profile")
    // Link the Application Profile to the Tenant
    tenant.AddAppProfile(appProfile)
    // Save the new Application Profile to the APIC
    err = client.AppProfiles.Save(appProfile)

    if err != nil {
        fmt.Printf("Error creating appProfile: %s", err.Error())
        exit()
    } else {
        fmt.Println("Successfully created new appProfile!")
    }
}

func addEPG() {
    // //  Create new End-Point Group
    // //  Define the new End-Point Group
    // epg = client.EPGs.New("Example-EPG", "This is an example End-Point Group")
    // // Link the End-Point Group to the Application Profile
    // appProfile.AddEPG(epg)
    // // Save the new End-Point Group to the APIC
    // err = client.EPGs.Save(epg)
    //
    // if err != nil {
    // 	fmt.Printf("Error creating End-Point Group: %s", err.Error())
    // } else {
    // 	fmt.Println("Successfully created new End-Point Group!")
    // }
}

func addContract() {
    //  Create new Contract
    //  Define the new Contract
    contract = client.Contracts.New("Example-Contract", "Global")
    // Link the Contract to the Tenant
    tenant.AddContract(contract)
    // Save the new Contract to the APIC
    err = client.Contracts.Save(contract)

    if err != nil {
        fmt.Printf("Error creating Contract: %s", err.Error())
        client.Tenants.Delete("uni/tn-Example-Tenant")
        fmt.Printf("Tenant deleted.")
    } else {
        fmt.Println("Successfully created new Contract!")
    }
}

func main() {
	var client *service.Client
	var tenant *models.Tenant
    var appProfile *models.AppProfile
    // var epg *models.EPG
    var contract *models.Contract
	var err error

    // Setup a Client to maintain a connection to the APIC
	client = service.GetClient()

    addTenant(tenant, client)
    // addAppProfile()
    // addEPG()

}
