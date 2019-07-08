# Modules required
import imaplib
import email
import configparser
import os
import sys
from pprint import pprint
import re
import csv

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class IMAPDownloader():

    def __init__(self, csv_filename):

        self.list_response_pattern = re.compile(
            r'\((?P<flags>.*?)\) "(?P<delimiter>.*)" (?P<name>.*)'
        )

        # Terminal attributes
        self.CURSOR_UP_ONE          = '\x1b[1A'
        self.ERASE_LINE             = '\x1b[2K'

        # Read config file
        self.CONFIG                 = configparser.ConfigParser()
        self.CONFIG.read('email.conf')

        self.VERBOSE                = True

        self.BASE_DIR               = self.CONFIG.get('files', 'base_directory')
        self.BASE_MSG_NAME          = self.CONFIG.get('files', 'base_filename')
        self.BASE_FOLDER            = ""

        # Which user is currently downloading
        self.current_user           = None
        self.users                  = {}
        self.csv_filename           = csv_filename
        self.mailboxes              = []

        self.parse_csv()

    def parse_csv(self):
        with open(self.csv_filename) as csv_file:
            csv_reader = csv.DictReader(csv_file)
            # line_count = 0
            for row in csv_reader:
                # if (line_count == 0):
                #     print(f'Column names are {", ".join(row)}')
                #     line_count += 1
                # print(f'{row["username"]} has password of {row["password"]}')
                self.users[row["username"]] = row["password"]
            print(f'There are {len(self.users)} users')
            

    def open_connection(self):
        hostname = self.CONFIG.get('server','hostname')
        ssl_port = self.CONFIG.get('server','ssl_port')
        if self.VERBOSE:
            print("Connecting to <" + hostname + "> on port", ssl_port)

        # Need to check if timeout
        self.connection = imaplib.IMAP4_SSL(host=hostname, port=ssl_port)

        return 0
        #return connection

    def login_as_user(self, username, password):

        if (username is None or password is None):
            if self.VERBOSE:
                print("No credentials!")
            return 1

        self.BASE_FOLDER = username.split('@')[0]
        self.mailboxes = []

        if self.VERBOSE:
            print("Logging in as " + bcolors.WARNING + username + bcolors.ENDC)

        try:
            self.connection.login(username, password)
        except Exception as err:
            print("Logging in error: " + bcolors.FAIL, err, bcolors.ENDC)
            return 1

        typ, data = self.connection.list()
        if self.VERBOSE:
            print("Account connection: " + bcolors.OKGREEN + typ + bcolors.ENDC)
            
        if (typ != "OK"):
            print("Response is NOKAY! Leaving now with error:", typ)
            return 1
        
        self.parse_mailbox_names(data)
        print("Mailboxes:")
        for mb in self.mailboxes:
            print("\t" + mb)
        
        return 0

    def parse_mailbox_names(self, data):
        for line in data:
            flags, delimeter, mailbox_name = self.parse_list_response(line)
            self.mailboxes.append(mailbox_name)

    def parse_list_response(self, line):
        match = self.list_response_pattern.match(line.decode('utf-8'))
        flags, delimiter, mailbox_name = match.groups()
        mailbox_name = mailbox_name.strip('"')
        return (flags, delimiter, mailbox_name)

    def write_email_to_file(self, mailDirectory, name, msg):

        newDir = self.BASE_DIR  + self.BASE_FOLDER +  '/' + mailDirectory
        
        if not os.path.exists(newDir):
            if self.VERBOSE:
                print("Making new directory:", newDir)
            os.makedirs(newDir)
        
        # os.chdir(newDir)

        filename = self.BASE_MSG_NAME + name + '.eml'

        # Check if file exists first before saving
        if (os.path.isfile(newDir + '/' + filename)):
            return 1
        
        fp = open(newDir + '/' + filename, 'w', encoding="utf-8")
        fp.write(msg)
        fp.close()

        # if VERBOSE:
        #     print("Downloaded message:", filename)
        
        return 0

    def download_folder(self, folder):
        if self.VERBOSE:
            print('Downloading folder:', folder)

        # TODO: need error checking
        if (self.connection.state == "NONAUTH"): 
            print("Not authenticated! Can't download.")
            return

        typ, data = self.connection.select(mailbox=folder, readonly=True)
        if (typ != "OK"):
            return 1

        num_msgs = int(data[0])

        typ, data = self.connection.search(None, 'ALL')

        print("There are {} messages in {}".format(num_msgs, folder))
        if (num_msgs == 0):
            return 0

        for num in data[0].split():
            typ, data = self.connection.fetch(num, '(RFC822)')
            # pprint(data)
            msg = email.message_from_bytes(data[0][1])
            message_id = msg.get('Message-ID')
            smsg = msg.as_bytes().decode(encoding='ISO-8859-1')

            eml_name = message_id if message_id is not None else num.decode()

            self.write_email_to_file(folder, eml_name, smsg)
            print("Writing: {} / {}".format(num.decode(), num_msgs))
            if (int(num.decode()) < num_msgs):
                self.delete_last_lines()
        print("Downloaded {} messages from {} successfully!".format(num_msgs, folder))
        self.connection.close()
        return

    def delete_last_lines(self, n=1):
        for _ in range(n):
            sys.stdout.write(self.CURSOR_UP_ONE)
            sys.stdout.write(self.ERASE_LINE)

    def logout(self):
        if (self.connection.state == "NONAUTH"): 
            print("Not authenticated! Can't logout.")
            return
        self.connection.logout()
    def print_block(self):
        print("\n==============================================\n")

    def run(self):

        for username in self.users:
            self.open_connection()
            self.current_user = username
            
            if (self.login_as_user(self.current_user, self.users[self.current_user])):
                continue

            while (len(self.mailboxes) > 0 ):
                self.download_folder(self.mailboxes.pop())
            self.logout()
            self.print_block()
            # self.connection.auth