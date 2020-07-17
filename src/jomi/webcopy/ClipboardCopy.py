import os, sys, requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from urllib.request import  urlretrieve
import time
from django.utils.text import get_valid_filename

from phillippiper.HtmlClipboard import HtmlClipboard
from phillippiper.HtmlClipboard import DumpHtml

def download_and_convert_links(folder):

    cb = HtmlClipboard()
    html = cb.GetHtml()
    if html:
        if not os.path.exists(folder):
            os.makedirs(folder)
        if not os.path.isdir(folder):
            raise ValueError(f"{folder} is not a folder")
        sfile =os.path.join(folder,"source.html_")
        print(f"Save clipbard in {sfile}")
        #print(f"{html}")
        with open(sfile, "w", encoding="utf-8") as outf:
            outf.write(html)

def convert_html_links(folder):
    sfile = os.path.join(folder, "source.html_")
    if not os.path.isfile(sfile):
        raise ValueError(f"{folder} is not found")
    html = None
    with open(sfile, "r", encoding="utf-8") as inf:
        html =inf.read()
    #print(html)
    soup = BeautifulSoup(html, 'html.parser')
    for link in soup.findAll('img'):
        iurl = urlparse(link['src'])

        iname=os.path.basename(iurl.path)
        inamevalid = get_valid_filename(iname)
        #ifilelink = "/".join([os.path.basename(folder),inamevalid])
        ifilelink = inamevalid
        ifilepath = os.path.join(folder,inamevalid)

        print(f"{link['src']}, {ifilepath}")
        url_get_content(link['src'], ifilepath)
        link['src'] = ifilelink
    wfilename = os.path.join(folder,"source.html")
    with open(wfilename, "w", encoding='utf-8') as outf:
        outf.write(str(soup))
    #os.path.basename(path)


def url_get_content(url_string, file_name):
    resp = requests.get(url_string, verify=False)
    with open(file_name, 'wb') as f:
        f.write(resp.content)


def sanitize_filename(name):
    return get_valid_filename(name)


def sanitize_filename_main():
    print(sanitize_filename(sys.argv[1]))

def web_copy_main():
    if (len(sys.argv) < 2):
        print("Usage: python Webcopy folder")
        exit(1)
    folder = sanitize_filename(sys.argv[1])
    print(f"Downloading in {folder}")
    download_and_convert_links(folder)
    convert_html_links(folder)

if __name__ == '__main__':
    web_copy_main()
