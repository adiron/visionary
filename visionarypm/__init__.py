#!/usr/bin/env python

from __future__ import print_function, unicode_literals
import codecs

from colorama import init, Fore, Style
from getpass import getpass
from sys import argv
import pyscrypt
import json
import os


# Initialise colours for multi-platform support.
init()

# Initialise input for multi-version support.
try:
    input = raw_input
except NameError:
    pass


def generate(master_password, keyword, cost=2048, oLen=32):
    hashed = pyscrypt.hash (
        password = master_password.encode(),
        salt = keyword.encode(),
        N = cost,
        r = 1,
        p = 1,
        dkLen = 32
    )
    return codecs.encode(hashed, 'hex').decode('utf-8')[0:oLen]


# Output coloring functions

def err(text):
    return '%s%s%s' % (Fore.RED, text, Fore.RESET)


def settings(text):
    return '%s%s%s' % (Fore.YELLOW, text, Fore.RESET)


def password(text):
    return '%s%s%s' % (Fore.CYAN, text, Fore.RESET)


def safe_input(string):
    try:
        return str(input(string))
    except EOFError:
        print(err('Input unusable.\n'))
        return safe_input(string)


def get_defaults():
    """
    Queries the user for their preferred settings and returns a dictionary containing
    those settings.
    """
    print('Enter your preferred settings: (leave blank to accept defaults)\n')
    cost = safe_input('CPU/memory cost parameter [default=2048]: ')
    if cost:
        if cost.isdigit():
            cost = int(cost)
            if (cost & (cost - 1)) or (cost > 16384 or cost < 1024):
                print(err('Input must be a positive power of 2 between 1024 and 16384.\n'))
                return get_defaults()
        else:
            print(err('Input must be a positive power of 2 between 1024 and 16384.\n'))
            return get_defaults()
    else:
        cost = 2048
    oLen = safe_input('Length of generated passwords [default=32]: ')
    if oLen:
        if oLen.isdigit():
            oLen = int(oLen)
            if oLen > 64 or oLen < 16:
                print(err('Input must be a positive integer between 16 and 64.\n'))
                return get_defaults()
        else:
            print(err('Input must be a positive integer between 16 and 64.\n'))
            return get_defaults()
    else:
        oLen = 32
    print() #line break for formatting
    return {"cost" : cost, "oLen" : oLen}


def getPath():
    """
    Get path of config file.
    """
    try:
        return '%s/visionarypm.conf' % os.path.dirname(os.path.abspath(__file__))
    except:
        print(err('\nCannot get path. Are you sure you\'re not running Visionary from IDLE?'))
        raise SystemExit


def getConfig():
    """
    Try to load a configuration from the disk or else get a new one.
    """
    try:
        with open(path) as f:
            config = json.loads(f.read().strip())
        return config, 0
    except IOError:
        config = get_defaults()
        autosave = safe_input('Do you want to save this config? (Y/n) ').lower()
        print() #line break for formatting
        if autosave == 'yes' or autosave == 'y' or autosave == "":
            print('Autosaving configuration...\n')
            try:
                with open(path, 'a') as f:
                    f.write(json.dumps(config))
                return config, 0
            except:
                print(err('Autosaving failed! (Permission denied)\n'))
        print('In order to save these settings, place %s' % settings(json.dumps(config)))
        print('in %s\n' % (settings(path)))
        return config, 1


# Global parameters
params = {}
path = getPath()


def session(first_run=True, keyword=None):
    if first_run or keyword:
        if first_run:
            print("""%s%s
                            _     _
                     /\   /(_)___(_) ___  _ __   __ _ _ __ _   _
                     \ \ / / / __| |/ _ \| '_ \ / _` | '__| | | |
                      \ V /| \__ \ | (_) | | | | (_| | |  | |_| |
                       \_/ |_|___/_|\___/|_| |_|\__,_|_|   \__, |
                                           Password Manager|___/\n
            """ % (Fore.WHITE, Style.BRIGHT)) # Set global default colours.
            print(settings('  Please report any issues at https://github.com/libeclipse/visionary/issues\n'))
        global params
        params, stat = getConfig()
        if stat == 0:
            print('[+] Cost factor: %s\n[+] Password length: %s\n[+] Config file: %s\n' % (settings(params['cost']),
                                                                                           settings(params['oLen']),
                                                                                           settings(path)))
    master_password = getpass('Master password: ')
    master_password_confirm = getpass('Confirm master password: ')
    while master_password != master_password_confirm:
        print(err('Passwords don\'t match!\n'))
        master_password = getpass('Master password: ')
        master_password_confirm = getpass('Confirm master password: ')
    if len(master_password) >= 8:
        print() #line break for formatting
        if not keyword:
            # If the keyword was not specified.
            while True:
                keyword = safe_input('Keyword: ')  # Get the keyword from the terminal.
                if keyword:
                    print('Your password: %s\n' % (password(generate(master_password,
                                                                     keyword,
                                                                     params['cost'],
                                                                     params['oLen']))))
                else:
                    print(err('\nExiting...'))
                    raise SystemExit
        else:
            # If the keyword was specified
            print('Your password: %s\n' % (password(generate(master_password,
                                                             keyword,
                                                             params['cost'],
                                                             params['oLen']))))

    else:
        print(err('Password must be at least 8 characters.\n'))
        session(False)


def main():
    if len(argv) > 1:
        session(first_run=False, keyword=argv[1])
    else:
        try:
            session()
        except KeyboardInterrupt:
            print(err('\n\nKeyboard Interrupt'))


if __name__ == "__main__":
    main()
