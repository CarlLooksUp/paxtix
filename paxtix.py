import os
import sys
from argparse import ArgumentParser
import traceback
from automail.automail import parse_settings, send_email
from tweepy.api import API
import datetime
import threading
sys.path.append(os.path.join(os.path.dirname(__file__), 'tweepy'))
from tweepy.auth import OAuthHandler
from tweepy.streaming import Stream, StreamListener
import re

sa = '''
This was a triumph.
I'm making a note here: HUGE SUCCESS.
It's hard to overstate my satisfaction.
Aperture Science
We do what we must
because we can.
For the good of all of us.
Except the ones who are dead.
But there's no sense crying over every mistake.
You just keep on trying till you run out of cake.
And the Science gets done.
And you make a neat gun.
For the people who are still alive.
I'm not even angry.
I'm being so sincere right now.
Even though you broke my heart.
And killed me.
And tore me to pieces.
And threw every piece into a fire.
As they burned it hurt because I was so happy for you!
Now these points of data make a beautiful line.
And we're out of beta.
We're releasing on time.
So I'm GLaD. I got burned.
Think of all the things we learned
for the people who are still alive.
Go ahead and leave me.
I think I prefer to stay inside.
Maybe you'll find someone else to help you.
Maybe Black Mesa
THAT WAS A JOKE.
HAHA. FAT CHANCE.
Anyway, this cake is great.
It's so delicious and moist.
Look at me still talking
when there's Science to do.
When I look out there, it makes me GLaD I'm not you.
I've experiments to run.
There is research to be done.
On the people who are still alive.
And believe me I am still alive.
I'm doing Science and I'm still alive.
I feel FANTASTIC and I'm still alive.
While you're dying I'll be still alive.
And when you're dead I will be still alive.
STILL ALIVE
STILL ALIVE
'''.splitlines()


def parse_oauth_file(oauthFileLoc):
    readCleanLine = lambda f: f.readline().strip()
    with open(oauthFileLoc, 'r') as f:
        consumer_key = readCleanLine(f)
        consumer_secret = readCleanLine(f)
        access_token = readCleanLine(f)
        access_token_secret = readCleanLine(f)
        return (consumer_key, consumer_secret,
                access_token, access_token_secret)


class PaxListener(StreamListener):

    def __init__(self, mail_settings_loc, auth):
        StreamListener.__init__(self, API(auth))
        self.mail_settings = parse_settings(mail_settings_loc)
        self.c = 0
        self.hourly_heartbeat()
    '''
    uncomment this if you want to see what a 'status' object will look like
    '''
    '''
    def on_data(self, data):
        print data
        return True
    '''

    def on_status(self, status):
        if re.search(r'east|ticket|tickets|registration|open', status.text, re.IGNORECASE): #regex open for editing
            subject = "New message from %s" % status.user.name.encode('ascii', 'xmlcharrefreplace')
            message = status.text.encode('ascii', 'xmlcharrefreplace')
            send_email(self.mail_settings, subject, message)
        return True

    def on_error(self, status_code):
        subject = status_code + "error recieved by tweepy!"
        message = "PAX tix listener recieved a " + status_code + " error from twitter"
        send_email(self.mail_settings, subject, message)
        return True
    
    def hourly_heartbeat(self):
        global sa
        if self.c < 48:
            msg = "heatbeat"
        elif self.c < 48 + len(sa):
            msg = sa[self.c - 48]
        else:
            msg = "heatbeat"
        self.api.update_status("%s %s" % (timestr, msg))
        t = threading.Timer(3600, self.hourly_heartbeat)
        t.start()
        self.c = self.c + 1
        
    def daily_heartbeat(self):
        subject = "PAX ticket listener heatbeat"
        msg = "Heartbeat for %s" % datetime.datetime.utcnow().isoformat()
        send_email(self.mail_settings, subject, msg)
        t = threading.Timer(86400, self.daily_heartbeat)


def main():
    try:
        parser = ArgumentParser()
        parser.add_argument("oauth_keys_file",
                        help="The location of a file containing the application " +
                        "oath consumer key, consumer secret, " +
                        "access token, and access token secret, " +
                        "each on its own line, in that order.  " +
                        "See the tweepy example on oauth to figure " +
                        "out how to get these keys."
                        )
        parser.add_argument("mail_settings_file", help="The automail settings file for sending emails.")
        args = parser.parse_args()
        (consumer_key, consumer_secret, access_token, access_token_secret) = \
            parse_oauth_file(args.oauth_keys_file)
    
        auth = OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
    
        pl = PaxListener(args.mail_settings_file, auth)
        
        #open a stream, with ourself as the listener
        stream = Stream(auth, pl)
        #stream.filter(track=["the"])
    
        pax_user_id = '26281970' #follow requires userid, found at mytwitterid.com
        stream.filter(follow=['1954653840']) #track ignores follow, pulls from firehose regardless (this is testing acct)

    except BaseException as e:
        subject = "Exception from paxtix"
        exc_type, exc_value, exc_traceback = sys.exc_info()
        message = '\n'.join(["Pax tix listener has hit an exception!",] + 
                             traceback.format_exception(exc_type, exc_value, exc_traceback),
                             )
        send_email(parse_settings(args.mail_settings_file), subject, message)
        traceback.print_exception(exc_type, exc_value, exc_traceback)

if __name__ == "__main__":
    main()
