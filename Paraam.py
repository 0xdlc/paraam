#!/Users/Mo/.rye/shims/python

import requests
import argparse
import re
from urllib.parse import urlparse
import subprocess
import os
from bs4 import BeautifulSoup
import sqlite3




def finder(url,headers,host,dir):
  urlreq = requests.get(url,headers)
  words = re.findall(r"\b[^\W\d]\w*\b",urlreq.text)
  for i in words:
    f = open(f"{dir}/{host}.params", "a+")
    f.write(f"{i}\n")
    f.close()
  subprocess.call(["sort","-u","-o",f"{dir}/{host}.params",f"{dir}/{host}.params"])
  count = subprocess.check_output(["wc","-l",f"{dir}/{host}.params"],text=True)
  print(f'[+] Wordcount: {count}')
  print(f'[+] Wordcount: {count}')


def main():
  skips = ('png','jpeg','svg','xml','svg+xml')
  permutes = ['.','_','-']
  parser = argparse.ArgumentParser()
  parser.add_argument('-u', required=True, default=False, metavar='url', type=str)
  parser.add_argument('-depth', required=False, default=1, metavar='recursive depth that the crawler will look for urls: default=1 -> just the main page with urls inside', type=int)
  parser.add_argument('-debug', required=False,nargs='?', const='true', metavar='debug mode', type=bool)
  parser.add_argument('-permute', required=False,nargs='?', const='true', metavar='Make permutation of words (Adding ._- to the words)', type=bool)
  parser.add_argument('-domain_only', required=False,nargs='?', const='true', metavar='only scan the given url (Do not crawl for other urls)', type=bool)
  parser.add_argument('-x8', required=False,nargs='?', const='true', metavar='test the words with x8 after being done', type=bool)
  parser.add_argument('-su', required=False,nargs='?', const='true', metavar='save urls', type=bool)
  dir = os.path.expanduser('~/params')
  args = parser.parse_args()
  Headers = ({'User-Agent':
      'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 \
      (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',\
      'Accept-Language': 'en-US, en;q=0.5'})
  print(f'[+] Program: {args.u}')
  tempUrl = [args.u]
  urls = []
  tempList = []
  gibberish = ['<', '^', '(', ')']
  for d in range(0,args.depth):
    for url in tempUrl:
      try:
        urls.append(url)
        tempUrl.remove(url)
        res = requests.get(url,Headers)
        parseurl = urlparse(f"{url}")
        host = '{uri.netloc}'.format(uri=parseurl)
        soup = BeautifulSoup(res.text,features="html.parser")
        #Using bs4 to get inside src,href,... becuase we cant regex some of them
        regex = r"(?:https?:)?\w*\/[^\"'\s]*(?:\/[^\"'\s]+)?\/?"
        regexedUrls = re.findall(regex,res.text)
        for i in soup.find_all('a',href=True):
          regexedUrls.append(i['href'])
        for i in soup.find_all('script',src=True):
          regexedUrls.append(i['src'])
        for i in soup.find_all('link',href=True):
          regexedUrls.append(i['href'])
        for i in regexedUrls: 
          for gibber in gibberish:
            if gibber in i:
              regexedUrls.remove(i)
        for i in regexedUrls: 
          if i.find(f"{host}") == 0:
              tempList.append(i)
          elif i.find('http') == -1:
            if i.startswith('/') is True:
              tempList.append(f'https://{host}{i}')
            else:
              tempList.append(f'https://{host}/{i}')
      except Exception as e:
        print(f"[-] Error: {e}")
        pass
    print(f"[+] Going to depth {d+1}")
    tempUrl = tempList
    tempList = []
          
  #Removin duplicates V:
  urls = list(set(urls)) #Unique the urls
  print(urls)
  print(f'[+] Found {len(urls)} urls')
  if args.debug:    
    for i in urls:
      print(f'{i}\n')

  for j in urls: 
    if j.endswith(skips) is False:
      urlreq = requests.get(j,Headers)
      words = re.findall(r"\b[^\W\d]\w*\b",urlreq.text)
      if "sourceMappingURL" in words:
        print(f"[!] {j} has Source-Map URL")
      for i in words:
          f = open(f"{dir}/{host}.params", "a+")
          f.write(f"{i}\n")
          f.close()
    subprocess.call(["sort","-u","-o",f"{dir}/{host}.params",f"{dir}/{host}.params"])
  count = subprocess.check_output(["wc","-l",f"{dir}/{host}.params"],text=True)
  print(f'[+] Wordcount: {count}')
  
  # print("[+] Writing in database...")
  # conn = sqlite3.connect('all_parsms.db')
  # cursor = conn.cursor()
  if args.su:
    for i in urls:
      f = open(f"{dir}/{host}.urls", "a+")
      f.write(f"{i}\n")
      f.close()
  if args.permute:
    line = open(f"{dir}/{host}.params", "r")
    file = open(f"{dir}/{host}.params.permutes", "a+")
    while True:
      wrd = line.readline()
      if len(wrd) == 0:
        break
      for i in permutes:
        file.write(i + wrd)
    file.close()
    line.close()
  if args.x8:
    subprocess.check_output(["x8","-u",f"{args.u}","-w",f"{dir}/{host}.params","-o",f"{dir}/{host}.params.x8"], text=True)


if __name__ == '__main__':
    main()



