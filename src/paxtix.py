from argparse import ArgumentParser
from tweepy.auth import OAuthHandler
from tweepy.streaming import Stream, StreamListener


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

    '''
    uncomment this if you want to see what a 'status' object will look like
    '''
    '''
    def on_data(self, data):
        print data
        return True
    '''

    def on_status(self, status):
        print "%s: %s" % (status.user.name, status.text)
        return True

    def on_error(self, status):
        print status
        return False


def main():
    parser = ArgumentParser()
    parser.add_argument("oauth_keys_file",
                    help="The location of a file containing the application " +
                    "oath consumer key, consumer secret, " +
                    "access token, and access token secret, " +
                    "each on its own line, in that order.  " +
                    "See the tweepy example on oauth to figure " +
                    "out how to get these keys."
                    )
    args = parser.parse_args()
    (consumer_key, consumer_secret, access_token, access_token_secret) = \
        parse_oauth_file(args.oauth_keys_file)

    pl = PaxListener()

    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    #open a stream, with ourself as the listener
    stream = Stream(auth, pl)
    #stream.filter(track=["the"])

    stream.filter(track=['ticket', 'tickets', 'east'],
    follow=['@Official_PAX'])


if __name__ == "__main__":
    main()
