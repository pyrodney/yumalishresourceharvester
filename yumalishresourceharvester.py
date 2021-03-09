# YumalishResourceHarvester 0.2: Capture hyperlinks for later addition
# to Yumalish.com

from bs4 import BeautifulSoup
import re
import sqlite3
import ssl
import urllib.request, urllib.parse, urllib.error


# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def prepare_title(url):
    title = ''

    if url.startswith("https://en.wikipedia.org/wiki"):
        title = urllib.parse.unquote(url.lstrip("https://en.wikipedia.org/wiki/").replace('_', ' '))
    else:
        html = urllib.request.urlopen(url, context=ctx).read()
        soup = BeautifulSoup( html, 'html.parser')

        title = soup.title.string.strip().strip('\n')

    if url.startswith("https://wwww.youtube.com") or title == '':
        title = input("Enter URL's title: ")

    return title.strip().strip('\n')

def add_record(url, connection, cursor):
    title = prepare_title(url)
    cursor.execute("INSERT INTO Hyperlinks (url, title) VALUES (?, ?)",
                (url, title))
    connection.commit()

    return title

def prepare_url(raw_url):
    # Come take a closer look at this
    # regex pattern at https://regex101.com/r/91FdiZ/1
    regex_pattern = r'\/(index\.\w?html|default\.asp)'
    preurl = urllib.parse.urlparse(raw_url)

    url = preurl.scheme + '://' + preurl.netloc + preurl.path
    if url.startswith("https://wwww.youtube.com"):
        url += preurl.query
    url = re.sub(regex_pattern, '', url)

    return url.rstrip('/')

def yumalishresourceharvester():
    connection = sqlite3.connect('yumalishresourceharvester.sqlite')
    cursor = connection.cursor()

    quit = False

    cursor.execute("""CREATE TABLE IF NOT EXISTS Hyperlinks
                      (date DATETIME DEFAULT CURRENT_TIMESTAMP,
                      url TEXT UNIQUE, title TEXT)""")

    while quit is not True:
        command = input("Enter URL or command: ")

        if command.startswith('http://') or command.startswith('https://'):
            url = prepare_url(command)

            try:
                cursor.execute("""SELECT url, title
                                  FROM Hyperlinks WHERE url=?""", (url,))
                # Using underscore as a throwaway variable:
                # https://hackernoon.com/understanding-the-underscore-of-python-309d1a029edc
                _ = cursor.fetchone()[0]
                print("ERROR: Record already exists, dog.\n")
            except TypeError as e:
                # print("{}\n".format(e))
                title = add_record(url, connection, cursor)
                print("Add Successful!!! -- URL: \"{}\" -- Title: \"{}\"\n".format(url, title))

        elif command == 'q':
            quit = True
        else:
            # SELECT url, title FROM Hyperlinks WHERE url LIKE '%lukas%' UNION SELECT url, title FROM Hyperlinks WHERE title LIKE '%lukas%'
            print("Does not compute, Homie!\n")

    connection.close()

if __name__ == '__main__':
    yumalishresourceharvester()
