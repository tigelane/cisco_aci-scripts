#!/usr/bin/env python

"""
Application using event subscription to forward events to a Twitter
user ID as a direct message.  
"""
import sys, time, datetime
import acitoolkit.acitoolkit as aci
import tweepy

#  Twitter Handle integration - Get these from developer.twitter.com
ckey = ''
csecret = ''
atoken = ''
asecret = ''

auth = tweepy.OAuthHandler(ckey, csecret)
auth.set_access_token(atoken, asecret)
twitter = tweepy.API(auth)

# Twitter username(s) to send too
# For direct messages, please ensure you have proper twitter rights
#   to send direct messages to the users or you will get an error.
# example: twitter_usernames = ['mavrick86', 'shrek2001']
twitter_usernames = ['', '']

# Valid options are 'screen' and 'twitter' - Use this for testing.
output_screen = True
output_twitter = False

start_time = time.time()
# Time in seconds to wait until the program accepts new events.
# This is to clear out all of the old events built up in the system.
# Adjust this on "screen" mode until you don't see any old events
#    when the application is started.
wait_time = 30

last_update = ''

def display(message):
    # print 'In display'

    if time.time() - start_time < wait_time:
        # print time.time() - start_time
        return

    if output_screen:
        print message

    if output_twitter:
        for user in twitter_usernames:
            print user
            try:
                # Use the following line if you want to make this a status update
                # that will come from the handle associated with the info from developer.twitter.com
                # twitter.update_status(message)
                twitter.send_direct_message(user=user, text=message)
            except tweepy.TweepError as terror:
                print terror
                print "There was a problem posting to twitter.\n"

def main():
    global last_update
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
        message = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
        if aci.Tenant.has_events(session):
            tenant = aci.Tenant.get_event(session)
            if tenant.is_deleted():
                message += ' Tenant:' + tenant.name + ' has been deleted.'
                display(message)
            else:
                if last_update == tenant:
                    last_date = ''
                    continue
                else:
                    last_update = tenant
                    message += ' Tenant:' + tenant.name + ' has been created or modified.'
                    display(message)

        if aci.AppProfile.has_events(session):
            app_profile = aci.AppProfile.get_event(session)
            tenant = app_profile.get_parent()
            message += ' Tenant:' + tenant.name + ' Application:' + app_profile.name + ' has been modified.'
            display(message)
            

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
