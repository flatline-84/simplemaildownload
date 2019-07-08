from IMAPDownloader import IMAPDownloader

if __name__ == '__main__':

    dl = IMAPDownloader('users.csv')
    dl.run()
    exit(0)