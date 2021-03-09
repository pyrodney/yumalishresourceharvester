# YumalishResourceHarvester 0.1: Capture hyperlinks for later addition
# to Yumalish.com

import re
import sqlite3
from urllib.parse import urlparse


def add_record(old_url, old_title, conn, cur):
    url, title = prepare_record(old_url, old_title)
    cur.execute("INSERT INTO Hyperlinks (url, title) VALUES (?, ?)",
                (url, title))
    conn.commit()

    return url, title

def prepare_record(raw_url, raw_title):
    # Come take a closer look at this
    # regex pattern at https://regex101.com/r/91FdiZ/1
    regex_pattern = r'\/(index\.\w?html|default\.asp)'
    preurl = urlparse(raw_url)

    url = preurl.scheme + '://' + preurl.netloc + preurl.path
    if 'youtube' in raw_url:
        url += preurl.query
    url = re.sub(regex_pattern, '', url)
    url = url.rstrip('/')

    title = raw_title.strip()

    return url, title

def yumalishresourceharvester():
    conn = sqlite3.connect('yumalishresourceharvester.sqlite')
    cur = conn.cursor()

    quit = False

    cur.execute('CREATE TABLE IF NOT EXISTS Hyperlinks (date DATETIME DEFAULT CURRENT_TIMESTAMP, url TEXT UNIQUE, title TEXT)')

    while quit is not True:
        command = input("Enter URL or command: ")

        if command.startswith('http://') or command.startswith('https://'):
            url, title = add_record(command.strip(),
                input("Enter URL's title: "), conn, cur)
            print("Add Successful!!! -- URL: \"{}\" -- Title: \"{}\"\n".format(url, title))
        elif command == 'q':
            quit = True
        else:
            # SELECT url, title FROM Hyperlinks WHERE url LIKE '%lukas%' UNION SELECT url, title FROM Hyperlinks WHERE title LIKE '%lukas%'
            print("Does not compute, Homie!\n")

    conn.close()

if __name__ == '__main__':
    yumalishresourceharvester()