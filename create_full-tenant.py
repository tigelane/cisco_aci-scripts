#!/usr/bin/env python
import requests, json, sys, getpass


''' create_full_tenant.py
    The goal of this application is to create a new Tenant and associated Security Domain.
    It then creates a local user with full admin access to that Tenant.
    I have also put some pauses in the script so that you could use it to show a customer
    that the items are being built in the APIC before moving to the next item.
      
    This application does the following:
    1.  Collect a current valid admin username and password
    2.  Login to the system
    3.  Collect a new Tenants name
    4.  Create the new security group
    5.  Create the new Tenant
    6.  Collect the new admin username and password
    7.  Create the new user and place them in the proper security group
    *.  Display information back to the user (some day)
    
    Application created by Tige Phillips.  
    Please note that very little error checking is being done.  It's entirely possible 
    that my code could crash your system (not likely).  You have been warned!
'''

''' Version 1.5 changes
    1. Fixed the permissions of the users so they now have full read/write access to their tenant
    2. Added a list (users) that can be used to populate any number of users/tenants automatically (tenant, username, and password are all the same)
    3. Added "123" to a password if it's not 8 characters
'''

''' debug is used to hard code the IP address, admin username, and password.
    It also skips the press a key to continue (this is used for demonstration 
    purposes so you could walk a customer though the creation of all items.
'''

version = 1.5
admin = {}

# Populate the following list with userids and set DEBUG and CREATE_ALL to True
users = ['example','testing']
DEBUG = False
CREATE_ALL = False

def error_message(error):
    '''  Calls and error message.  This takes 1 list argument with 3 components.  #1 is the error number, #2 is the error text, 
         #3 is if the application should continue or not.  Use -1 to kill the application.  Any other number
         continues the application.  You must code in a loop and go back to where you want.
    '''
    print '\n================================='
    print   '  ERROR Number: ' + str(error[0])
    print   '  ERROR Text: ' + str(error[1])
    print '=================================\n'
    
    if error[2] == -1:
        print 'Applicaiton ended due to error.\n'
        sys.exit()
    
def hello_message():
    print '\n'
    print 'Please be cautious with this application.  The author did very little error\nchecking and can\'t ensure it will work as expected.\n'
    return
    
def collect_admin_info():
  ''' Collect the information that we need to login to the system 
  '''

  if DEBUG:
    ip_addr = ''
    user = ''
    password = ''
  else:
    ip_addr = raw_input('Name/Address of the APIC: ')
    user = raw_input('Administrative Login: ')
    password = getpass.getpass('Administrative Password: ')  
    
  return {"ip_addr":ip_addr,"user":user,"password":password}

def login(admin):
  ''' Login to the system.  Takes information in a dictionary form for the admin user and password
  '''
  headers = {'Content-type': 'application/json'}
  
  login_url = 'https://{0}/api/aaaLogin.json?gui-token-request=yes'.format(admin['ip_addr'])
  payload = '{"aaaUser":{"attributes":{"name":"' + admin['user']  + '","pwd":"' + admin['password'] + '"}}}'
  
  try:
    result = requests.post(login_url, data=payload, verify=False)
  except requests.exceptions.RequestException as error:   
    error_message ([1,'There was an error with the connection to the APIC.', -1])
    
  decoded_json = json.loads(result.text)

  if (result.status_code != 200):
    error_message ([decoded_json['imdata'][0]['error']['attributes']['code'], decoded_json['imdata'][0]['error']['attributes']['text'], -1])
    
  urlToken = decoded_json['imdata'][0]['aaaLogin']['attributes']['urlToken']
  refresh = decoded_json['imdata'][0]['aaaLogin']['attributes']['refreshTimeoutSeconds']
  cookie = result.cookies['APIC-cookie']

  return [urlToken, refresh, cookie]
  
def collect_tenant():
  ''' Collect information needed to create the tenant.  Not all items are asked for.
  '''
  name = raw_input('Name for the new Tenant: ')
  description = raw_input('Tenant Description: ')
  
  return {"name":name,"description":description}

def create_security_domain(admin,tenant):
  ''' Create the security domain that will govern the userid to the tenant
  '''
  new_tenant = tenant['name']
  new_desc = tenant['description']
  headers = {'Content-type': 'application/json', 'APIC-challenge':admin['urlToken']}
  cookie = {'APIC-cookie':admin['APIC-cookie']}
  
  url = 'https://{0}/api/node/mo/uni/userext/domain-{1}.json'.format(admin['ip_addr'], tenant['name'])
  
  payload = '{"aaaDomain": {"attributes": {"name": "' + new_tenant + '",'
  payload += '"descr": "' + new_desc + '","rn": "domain-' + new_tenant + '","status": "created"},"children": []}}'

  try:
    result = requests.post(url, data=payload, headers=headers, cookies=cookie, verify=False)
  except requests.exceptions.RequestException as error:   
    error_message ([1,'There was an error with the connection to the APIC.', -1])
    
  decoded_json = json.loads(result.text)

  if (result.status_code != 200):
    error_message ([decoded_json['imdata'][0]['error']['attributes']['code'], decoded_json['imdata'][0]['error']['attributes']['text'], -1])

  return

def create_tenant(admin,tenant):
  ''' Create our new tenant
  '''
  new_tenant = tenant['name']
  new_desc = tenant['description']
  headers = {'Content-type': 'application/json', 'APIC-challenge':admin['urlToken']}
  cookie = {'APIC-cookie':admin['APIC-cookie']}
  
  url = 'https://{0}/api/node/mo/uni/tn-{1}.json'.format(admin['ip_addr'], new_tenant)


  '''  This is all one json string.  broken up so it's a little easier to read
  '''
  payload = '{"fvTenant": {"attributes": {"name": "' + new_tenant + '",'
  payload += '"descr": "' + new_desc + '",'
  payload += '"rn": "tn-' + new_tenant + '",'
  payload += '"status": "created"},'
  payload += '"children": ['
  payload += '{"aaaDomainRef": { "attributes": {'
  payload += '"dn": "uni/tn-' + new_tenant + '/domain-' + new_tenant + '",'
  payload += '"name": "' + new_tenant + '",'
  payload += '"rn": "domain-' + new_tenant + '",'
  payload += '"status": "created"},'
  payload += '"children": []}}'
  payload += ']}}'

  try:
    result = requests.post(url, data=payload, headers=headers, cookies=cookie, verify=False)
  except requests.exceptions.RequestException as error:   
    error_message ([1,'There was an error with the connection to the APIC.', -1])
    
  decoded_json = json.loads(result.text)

  if (result.status_code != 200):
    error_message ([decoded_json['imdata'][0]['error']['attributes']['code'], decoded_json['imdata'][0]['error']['attributes']['text'], -1])

  return
  
def collect_user():
  '''  Collect information for the new admin user.  Once again, I'm not collecting everything I could
       There is no full name, phone number, etc.  
       I've done some rudimentary error checking on the password length and making sure they match.
  '''
  
  # loop is used to make sure the password is acceptable
  loop = True
  
  name = raw_input('Name of the new admin user: ')
  description = raw_input('User description: ')
  
  while loop:
    pass1 = getpass.getpass('User Password: ')
    pass2 = getpass.getpass('Verify Password: ')
    
    if len(pass1) > 7:
      if (pass1 == pass2):
        loop = False
      else:
          error_message ([1,'Passwords did not match', 1])
    else:
      error_message ([2,'Passwords must be 8 characters or longer', 1])
  
  return {"name":name,"description":description,"password":pass1}

def create_user(admin,tenant,user):
  ''' Creating the userid.  This is huge because we not only create the user, but we also need to 
      assign privileges to the new tenant.  That's is what's going on in the for loop.  I hard coded 
      a loop that goes through all of the roles and creates the WR json code for them.
  '''
  
  new_tenant = tenant['name']
  new_user = user['name']
  new_pass = user['password']
  new_desc = tenant['description']
  headers = {'Content-type': 'application/json', 'APIC-challenge':admin['urlToken']}
  cookie = {'APIC-cookie':admin['APIC-cookie']}
  roles = ['aaa','access-admin','admin','fabric-admin','nw-svc-admin','ops','read-all','tenant-admin','tenant-ext-admin','vmm-admin']
  
  url = 'https://{0}/api/node/mo/uni/userext/user-{1}.json'.format(admin['ip_addr'], new_user)
  
  #  user_role is used as a var in payload.  Check the second ot last line
  #  I create the large block of json code here, the use it later.
  user_role = ''
  loopnum = 1
  for role in roles:
    user_role += '{"aaaUserRole": {"attributes":{'
    user_role += '"dn": "uni/userext/user-' + new_user + '/userdomain-' + new_tenant + '/role-' + role + '",'
    user_role += '"name": "' + role + '",'
    user_role += '"privType" : "writePriv",'
    user_role += '"rn": "role-' + role + '",'
    user_role += '"status": "created,modified",'
    user_role += '},"children": []}}'
    if len(roles) != (loopnum - 1):
      user_role += ','
    loopnum += 1
 
  if len(new_user) < 8:
    new_pass += '123'
    
  payload = '{"aaaUser": {"attributes":'
  payload += '{"name": "' + new_user + '",'
  payload += '"pwd": "' + new_pass + '",'
  payload += '"descr": "' + new_desc + '",'
  payload += '"rn": "user-' + new_user + '",'
  payload += '"status": "created"},'
  payload += '"children": ['
  payload += '{"aaaUserDomain": { "attributes": {'
  payload += '"dn": "uni/userext/user-' + new_user + '/userdomain-' + new_tenant + '",'
  payload += '"name": "' + new_tenant + '",'
  payload += '"rn": "userdomain-' + new_tenant + '",'
  payload += '"status": "created,modified"},'
  payload += '"children": [' + user_role + ']}}'
  payload += ']}}'
  
  try:
    result = requests.post(url, data=payload, headers=headers, cookies=cookie, verify=False)
  except requests.exceptions.RequestException as error:   
    error_message ([1,'There was an error with the connection to the APIC.', -1])
    
  decoded_json = json.loads(result.text)

  if (result.status_code != 200):
    error_message ([decoded_json['imdata'][0]['error']['attributes']['code'], decoded_json['imdata'][0]['error']['attributes']['text'], -1])

  return
  
def auto_create():
  for name in users:
    new_tenant = {"name":name,"description":name}
    create_security_domain(admin,new_tenant)
    create_tenant(admin,new_tenant)
    new_user = {"name":name,"description":'AutoCreation',"password":name}
    create_user(admin,new_tenant,new_user)
    print 'User created: ' + name

  
  
def main():
  global admin
  '''  No arguments are used for the program.  This could be modified to take the required 
      input on the command line.  The benefit to this would be bulk creation from another script.
      Right now, it's human driven.
  '''
  hello_message()
  admin = collect_admin_info()
  add_admin = login(admin)
  ''' Add the session urlToken for future use with security, and the refresh timeout for future use '''
  admin.update({'urlToken':add_admin[0],'refreshTimeoutSeconds':add_admin[1], 'APIC-cookie':add_admin[2]})
#   print admin
  print 'Login Accepted\n'
  if not DEBUG:
    junk = raw_input('Press Enter when ready to continue.')

  if CREATE_ALL and DEBUG:
    auto_create()
  else:
    new_tenant = collect_tenant()
    create_security_domain(admin,new_tenant)
    print 'Security Domain successfully created...'
    if not DEBUG:
      junk = raw_input('Press Enter when ready to continue.')
  
    create_tenant(admin,new_tenant)
    print 'Tenant successfully created...'
    if not DEBUG:
      junk = raw_input('Press Enter when ready to continue.')

    new_user = collect_user()
    create_user(admin,new_tenant,new_user)
    print 'New user successfully created...'
  
#   End the application
  print '\n'
  print "We're done!"


if __name__ == '__main__':
    main()
