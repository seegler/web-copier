import os, sys, requests, getopt
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from urllib.request import  urlretrieve
import time
from django.utils.text import get_valid_filename

def filter_for_medium(soup):
    for noscript in soup.findAll('noscript'):
        print(f"NSCRIPT tag: ")
        noscript.decompose()
    for figure in soup.findAll('figure'):
        #print(f"figure tag: {figure}")
        imgs=[]
        for img in figure.findAll("img"):
            imgs.append(img)
        print(f"figure imgs: {len(imgs)}")
        if len(imgs) >1:
            if hasattr(imgs[1],'srcset') or not hasattr(imgs[0],'srcset'):
                print(f"Set src of img[1] in [0] {imgs[1]['src']}")
                imgs[0]['src'] = imgs[1]['src']
                print(f"Decompose img[1]")
                imgs[1].decompose()
            else:
                print(f"Decompose [1] imge in figure {imgs[1]['src']}")
                imgs[1].decompose()


clipboard_filters = {'medium': filter_for_medium}


def get_clipbaord_html():
    plt = which_platform()
    if(plt =='win'):
        import win32clipboard
        win32clipboard.OpenClipboard()
        data = win32clipboard.GetClipboardData()
        win32clipboard.CloseClipboard()
        return data
    else:
        import subprocess
        p = subprocess.Popen(['xclip', '-selection', 'clipboard', '-o'], stdout=subprocess.PIPE)
        #, '-t','text/html'
        retcode = p.wait()
        data = p.stdout.read()
        return data.decode("utf-8")


def download_and_convert_links(folder):
    html = get_clipbaord_html()
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


def convert_html_links(folder, site):
    sfile = os.path.join(folder, "source.html_")
    if not os.path.isfile(sfile):
        raise ValueError(f"{folder} is not found")
    html = None
    with open(sfile, "r", encoding="utf-8") as inf:
        html =inf.read()
    #print(html)
    soup = BeautifulSoup(html, 'html.parser')

    #handle site filtering
    if site:
        clipboard_filters[site](soup)

    for link in soup.findAll('img'):
        img_src=None
        try:
            img_src=link['src']
        except KeyError:
            print(f"IMG SRC not found in {link}")
            try:
                img_src = link['data-src']
            except KeyError:
                print(f"IMG DATA-SRC not found in {link}")
                continue
        iurl = urlparse(img_src)

        iname=os.path.basename(iurl.path)
        inamevalid = get_valid_filename(iname)
        #ifilelink = "/".join([os.path.basename(folder),inamevalid])
        ifilelink = inamevalid
        ifilepath = os.path.join(folder,inamevalid)

        print(f"{img_src}")
        url_get_content(img_src, ifilepath)
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


def do_web_copy_main(argv):
    #if (len(sys.argv) < 2):
    #    print("Usage: python Webcopy folder")
    #    exit(1)
    opts = parse_args(argv)
    folder = sanitize_filename(opts['title'])
    print(f"Downloading in {folder}")
    download_and_convert_links(folder)
    convert_html_links(folder, opts['site'])

def sanitize_filename_main():
    print(sanitize_filename(sys.argv[1]))



def web_copy_main():
    args=[]
    if (len(sys.argv) >1):
        args=sys.argv[1].split(" ")
    do_web_copy_main(args)


def which_platform():
    import platform
    pf = platform.system().lower()
    if pf == "linux" or pf == "linux2":
        return"lin"
    elif pf == "darwin":
        return "mac"
    elif pf == "win32" or pf=="windows":
        return "win"
    return "unknown"


def help():
    print("Usage: python ClipboardCopy -s {medium|} -f {/home/user/download}")
    print("Enter title:...")


def parse_args(argv):
    print(f"Args: {argv}")
    try:
        opts, args = getopt.getopt(argv, "s:f", ["site","folder"])
    except getopt.GetoptError:
        print("Invalid command {}".format(argv))
        help()
        sys.exit(2)
    site = None
    folder = ""
    for opt, arg in opts:
        if opt in ("-s", "--site"):
            site = arg
        if opt in ("-f", "--folder"):
            folder = arg

    title = input("Enter title :")
    return {'title': title, 'site': site, 'folder':folder}


if __name__ == '__main__':
    do_web_copy_main(sys.argv)
