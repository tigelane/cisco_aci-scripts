# Branch
cd /root/go/src/github.com/ignw/
rm -R cisco*
git clone --single-branch -b fix-ap-children https://github.com/IGNW/cisco-aci-go-sdk.git
cd cisco-aci-go-sdk
make fmt
make


# Master
cd /root/go/src/github.com/ignw/
rm -R cisco*
git clone https://github.com/IGNW/cisco-aci-go-sdk.git
cd cisco-aci-go-sdk
make fmt
make



export APIC_PASS=Zh2V7x7Q7,c6v[av4T,8,6dJbY-r9{y]r8K?%si$
export APIC_USER=admin
export APIC_HOST=https://10.4.1.5
export APIC_ALLOW_INSECURE=true
cd /root/go/src/github.com/ignw/cisco-aci-go-sdk
# git checkout -b origin/master
# git checkout -b origin/fix-ap-children
make integration
cd
