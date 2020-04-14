# coding=utf-8
# !/usr/bin/python
###############################################################################
# ProxyChecker 1.0.0 by @antidoxable Twitter | @antid0xable IG
# License - GNU GENERAL PUBLIC LICENSE (GPL-3.0) 
# PSNChecker.com Copyright (C) 2020 antidoxable, All Rights Reserved.
# This ProxyChecker is free: you can redistribute it and/or modify 
# it under the terms of the GNU General Public License as published by 
# the Free Software Foundation, either version 3 of the License, or 
# (at your option) any later version. 
# 
# This ProxyChecker is distributed in the hope that it will be useful, 
# but WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. 
# See the GNU General Public License for more details. 
# 
# You should have received a copy of the GNU General Public License
# along with this ProxyChecker file. If not, see <https://www.gnu.org/licenses/>. 

###############################################################################

from __future__ import print_function

import argparse
import logging
import random
import socket
import sys
import threading

try:
    import urllib.request as rq
    from urllib.error import HTTPError
    import urllib.parse as http_parser
except ImportError:
    import urllib2 as rq
    from urllib2 import HTTPError
    import urllib as http_parser

try:
    import Queue
except ImportError:
    import queue as Queue

def check_proxy(q):
    """
    check proxy for and append to working proxies
    :param q:
    """
    if not q.empty():

        proxy = q.get(False)
        proxy = proxy.replace("\r", "").replace("\n", "")

        try:
            opener = rq.build_opener(
                rq.ProxyHandler({'https': 'https://' + proxy}),
                rq.HTTPHandler(),
                rq.HTTPSHandler()
            )

            opener.addheaders = [('User-Agent', 'Mozilla/5.0; ProxyChecker By @antidoxable')]
            rq.install_opener(opener)

            req = rq.Request('https://api.ipify.org/')

            if rq.urlopen(req).read().decode() == proxy.partition(':')[0]:
                proxies_working_list.update({proxy: proxy})
                if _verbose:
                    print("[+] ", proxy, " | PASS\n")
                    f = open("workingproxylist.txt", "a")
                    f.write(proxy+"\n")
                    f.close()
            else:
                if _verbose:
                    proxies_dead_list.update({proxy: proxy})
                    print("[-] ", proxy, " | FAILED\n")
                    f = open("deadproxylist.txt", "a")
                    f.write(proxy+"\n")
                    f.close()

        except Exception as err:
            if _verbose:
                proxies_dead_list.update({proxy: proxy})
                print("[-] ", proxy, " | FAILED")
                f = open("deadproxylist.txt", "a")
                f.write(proxy+"\n")
                f.close()
            if _debug:
                logger.error(err)
            pass

def check_available_proxies(proxies):
    """
        check available proxies from proxy_list file
    """
    socket.setdefaulttimeout(30)

    global proxies_working_list
    global proxies_dead_list
    print("[-] Testing Proxy List...\n")

    proxies_working_list = {}
    proxies_dead_list = {}
    max_thread = THREAD

    queue = Queue.Queue()
    queuelock = threading.Lock()
    threads = []

    for proxy in proxies:
        queue.put(proxy)

    while not queue.empty():
        queuelock.acquire()
        for workers in range(max_thread):
            t = threading.Thread(target=check_proxy, args=(queue,))
            t.setDaemon(True)
            t.start()
            threads.append(t)
        for t in threads:
            t.join()
        queuelock.release()

    print("[+] Alive Proxies: " + str(len(proxies_working_list)) + "\n")
    print("[+] Dead Proxies: " + str(len(proxies_dead_list)) + "\n")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="AntiDoxable's Proxy Checker",
        epilog="./proxycheck -p proxies.txt -t 4 -d -v"
    )

    # required argument
    parser.add_argument('-p', '--proxy', action="store", required=True,
                        help='Proxy list path')
    # optional arguments
    parser.add_argument('-t', '--thread', help='Thread', type=int, default=4)
    parser.add_argument('-v', '--verbose', action='store_const', help='Thread', const=True, default=False)
    parser.add_argument('-d', '--debug', action='store_const', const=True, help='Debug mode', default=False)

    args = parser.parse_args()
    THREAD = args.thread
    _verbose = args.verbose
    _debug = args.debug

    try:
        proxies = open(args.proxy).readlines()
    except IOError:
        print("[-] Error: Check your proxy list file path\n")
        sys.exit(1)

    # enable debugging if its set
    if _debug:
        # Logging stuff
        logging.basicConfig(level=logging.DEBUG, filename="logging.txt",
                            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        logger = logging.getLogger(__name__)


    print("""                 _   _ _____                 _     _              """)    
    print("""     /\         | | (_)  __ \               | |   | |             """)      
    print("""    /  \   _ __ | |_ _| |  | | _____  ____ _| |__ | | ___         """) 
    print("""   / /\ \ | '_ \| __| | |  | |/ _ \ \/ / _` | '_ \| |/ _ \\       """) 
    print("""  / ____ \| | | | |_| | |__| | (_) >  < (_| | |_) | |  __/        """) 
    print(""" /_/    \_\_| |_|\__|_|_____/ \___/_/\_\__,_|_.__/|_|\___|        """) 
    print("""   _____                      _____ _               _             """)             
    print("""  |  __ \                    / ____| |             | |            """)             
    print("""  | |__) | __ _____  ___   _| |    | |__   ___  ___| | _____ _ __ """) 
    print("""  |  ___/ '__/ _ \ \/ / | | | |    | '_ \ / _ \/ __| |/ / _ \ '__|""") 
    print("""  | |   | | | (_) >  <| |_| | |____| | | |  __/ (__|   <  __/ |   """)    
    print("""  |_|   |_|  \___/_/\_\\\__, |\_____|_| |_|\___|\___|_|\_\___|_|  """)    
    print("""                        __/ |                                     """)                                      
    print("""                       |___/                                      """)                                      
    print("[+] Proxies Loaded:", str(len(proxies)))
 

    check_available_proxies(proxies)

