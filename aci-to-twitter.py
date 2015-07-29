#!/usr/bin/env python

"""
Application using event subscription to forward events to a Twitter
user ID.  Anyone can then subscribe and get immediate information
regarding events happen in an ACI environment.
"""
import sys
import acitoolkit.acitoolkit as aci
import tweepy

#  Twitter integration
ckey = ''
csecret = ''
atoken = ''
asecret = ''

auth = tweepy.OAuthHandler(ckey, csecret)
auth.set_access_token(atoken, asecret)
twitter = tweepy.API(auth)

# Valid options are 'screen' and 'twitter'
output = 'screen'

def display(message):

    if output == 'screen':
        print message
    if output == 'twitter':
        try:
            twitter.update_status(message)
        except:
            print "There was a problem posting to twitter.\n"

def main():
    """
    Main subscribe tenants routine
    :return: None
    """
    # Take login credentials from the command line if provided
    # Otherwise, take them from your environment variables file ~/.profile
    description = ('Export ACI events to Twitter.')
    creds = aci.Credentials('apic', description)
    args = creds.get()

    # Login to APIC
    session = aci.Session(args.url, args.login, args.password)
    resp = session.login()
    if not resp.ok:
        print('%% Could not login to APIC')
        sys.exit(0)
    

    # Register all of the events we want to watch for.  Comment them out if you don't want to see them
    aci.Tenant.subscribe(session)
    aci.AppProfile.subscribe(session)

    while True:
        if aci.Tenant.has_events(session):
            tenant = aci.Tenant.get_event(session)
            if tenant.is_deleted():
                message = 'Tenant:' + tenant.name + ' has been deleted.'
                display(message)
            else:
                message = 'Tenant:' + tenant.name + ' has been created or modified.'
                display(message)
            

        if aci.AppProfile.has_events(session):
            app_profile = aci.AppProfile.get_event(session)
            tenant = app_profile.get_parent()
            message = 'Application:' + app_profile.name + ' in tenant:' + tenant.name +  ' has changed.'
            display(message)
            

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
