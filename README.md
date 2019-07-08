# Introduction #

The purpose of this tool is to download entire mailboxes from a supplied list of user accounts.
This came about by not having a simple way to back up our cloud-hosted little email provider box.

## Usage ##

Make a copy of `email.conf.example` and rename to `email.conf`. Fill out appropriate server details and file directory options.

Make a copy of `users.csv.example` and rename to `users.csv`. Fill out with usernames and passwords (plain-text unfortunately).

## Dependencies ##

* python3  
* imaplib
