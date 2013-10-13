import os
import sys
from argparse import ArgumentParser
import traceback
from automail.automail import parse_settings, send_email
sys.path.append(os.path.join(os.path.dirname(__file__), 'tweepy'))
from tweepy.auth import OAuthHandler
from tweepy.streaming import Stream, StreamListener
import re


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

    def __init__(self, mail_settings_loc):
        StreamListener.__init__(self)
        self.mail_settings = parse_settings(mail_settings_loc)
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
    
        pl = PaxListener(args.mail_settings_file)
    
        auth = OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
    
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
