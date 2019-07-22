from IMAPDownloader import IMAPDownloader
from optparse import OptionParser

if __name__ == '__main__':

    parser = OptionParser()
    parser.add_option("-f", "--file", dest="filename", action="store", type="string", help="read from FILE", metavar="FILE")
    parser.add_option("-u", "--user", dest="username", action="store", type="string", help="username of single account", metavar="USER")
    parser.add_option("-p", "--password", dest="password", action="store", type="string", help="password for user", metavar="PW")

    (options, args) = parser.parse_args()

    dl = IMAPDownloader()

    if (options.filename is not None):
        dl.set_csv('users.csv')
    elif (options.username is not None and options.password is not None):
        dl.add_user(options.username, options.password)
    else:
        print("Not enough commands! Exiting...")
        exit(1)

    dl.run()
    exit(0)