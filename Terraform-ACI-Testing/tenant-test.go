package main

import (
        "fmt"
        "github.com/ignw/cisco-aci-go-sdk/src/models"
        "github.com/ignw/cisco-aci-go-sdk/src/service"
)

func main() {
        var client *service.Client
        var tenant *models.Tenant
        var err error
        var tenantdn string

        client = service.GetClient()

        tenant = client.Tenants.New("Example-Tenant", "This is an example tenant")

        tenantdn, err = client.Tenants.Save(tenant)

        if err != nil {
                fmt.Printf("Error creating tenant: %s", err.Error())
        } else {
                fmt.Println("Successfully created the new tenant with dn ==", tenantdn)
        }
}
