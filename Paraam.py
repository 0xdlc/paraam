#!/opt/homebrew/bin/python3

import requests
import argparse
import re
from urllib.parse import urlparse
import subprocess
import os
from bs4 import BeautifulSoup


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
  parser.add_argument('-show_urls', required=False,nargs='?', const='true', metavar='Show the urls', type=bool)
  parser.add_argument('-permute', required=False,nargs='?', const='true', metavar='Make permutation of words (Adding ._- to the words)', type=bool)
  parser.add_argument('-domain_only', required=False,nargs='?', const='true', metavar='only scan the given url (Do not crawl for other urls)', type=bool)
  parser.add_argument('-x8', required=False,nargs='?', const='true', metavar='test the words with x8 after being done', type=bool)
  dir = os.path.expanduser('~/params')
  args = parser.parse_args()
  Headers = ({'User-Agent':
      'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 \
      (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',\
      'Accept-Language': 'en-US, en;q=0.5'})
  print(f'[+] Program: {args.u}')
  res = requests.get(args.u,Headers)
  parseurl = urlparse(f"{args.u}")
  host = '{uri.netloc}'.format(uri=parseurl)
  urls = [f"{args.u}"]
  soup = BeautifulSoup(res.text,features="html.parser")
  #Using bs4 to get inside src,href,... becuase we cant regex some of them
  regex = r"(?:https?:)?\w*\/[^\"'\s]*(?:\/[^\"'\s]+)?\/?"
  all_urls = re.findall(regex,res.text)
  for i in soup.find_all('a',href=True):
    all_urls.append(i['href'])
  for i in soup.find_all('script',src=True):
    all_urls.append(i['src'])
  for i in soup.find_all('link',href=True):
    all_urls.append(i['href'])
  for i in all_urls: 
    if i.find('>') == -1:
      if i.find(f"{host}") == 0:
          urls.append(i)
      elif i.find('http') == -1:
        if i.startswith('/') is True:
          urls.append(f'https://{host}{i}')
        else:
          urls.append(f'https://{host}/{i}')
#Removin duplicates V:
  urls = list(set(urls))
  print(f'[+] Found {len(urls)} urls')
  if args.show_urls:    
    for i in urls:
      print(f'{i}\n')
  if args.domain_only:
    finder(args.u,Headers,host,dir)
  else:
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



