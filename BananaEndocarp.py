#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
BananaEndocarp

BananaEndocarp is a GUI built using nibbler for interacting with mwa2's api.
It was designed to work in a limited environment such as an NetInstall
environment. It connects to a mwa2 instance utilizing the API to create
a manifest per machine based off of the serial number.


Author: Clayton Burlison <https://clburlison.com>
Last modified: Aug 4, 2016
Version: 2.1

Referenced code:
https://gist.github.com/pudquick/f27efd1ddcbf57be0d14031a5e692015
https://github.com/typesupply/vanilla/blob/master/Lib/vanilla/vanillaPopUpButton.py
https://github.com/typesupply/vanilla/blob/master/Lib/vanilla/vanillaCheckBox.py
'''

import os
import sys
import time
import tempfile
import httplib
import urllib
import urllib2
import json
import subprocess
from urllib2 import urlopen, URLError, HTTPError
from nibbler import *


# Included manifests
included_manifests_options = [
    "manifest A",
    "manifest B",
    "manifest C",
]

# Your mwa2 URL
mwa2_url = "http://localhost:8000"

# Authorization key for mwa2 API. Create this string via:
#   python -c 'import base64; print "Authorization: Basic %s" % base64.b64encode("username:password")'
# Make sure and only paste the "Basic STRINGVALUE"
authorization = "Basic ABBAABAABAABBAAB"

# Default munki catalog
default_catalog = "production"

# You should rarely use the following...AKA: almost never!
default_managed_installs = []
default_managed_uninstalls = []
default_managed_updates = []
default_optional_installs = []

# When set to True, always override repo manifest with values from GUI prompt.
# DEFAULT value for always_override  = False
always_override = False

try:
    script_path = os.path.dirname(os.path.realpath(__file__))
    n = Nibbler(os.path.join(script_path, 'BananaEndocarp.nib'))
except IOError, ImportError:
    print "Unable to load nib!"
    exit(20)


def showMsg(message):
    """
    Show feedback to our label field.
    """
    feedback = n.views['feedback_result']
    feedback.setStringValue_(message)


def getSerialNumber():
    """
    Returns the serial number of the Mac.
    """
    cmd = "/usr/sbin/ioreg -c \"IOPlatformExpertDevice\" | awk -F '\"' \
                                    '/IOPlatformSerialNumber/ {print $4}'"
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    (out, err) = proc.communicate()
    return out.strip()


def setItems(items):
    """
    Function to set items to appear in the drop down menu.
    """
    menu = n.views['manifest_input']
    menu.removeAllItems()
    for item in items:
        menu.addItemWithTitle_(item)


def getItem():
    """
    Return the manifest value from our selected drop down menu item.
    """
    index = n.views['manifest_input'].indexOfSelectedItem()
    values = n.views['manifest_input'].itemTitles()
    return values[index]


def exitScript():
    """
    Exit BananaEndocarp.
    """
    print "Goodbye!"
    n.quit()


def apiCaller(url, machine_serial, method='GET', data=None):
    """
    Funtion to make requests to the api end point.
    """
    request = urllib2.Request(url,
                              headers={
                               "Authorization": authorization,
                               "Content-Type": "application/json"
                              }, data=json.dumps(data))
    request.get_method = lambda: method
    try:
        f = urllib2.urlopen(request)
        contents = f.read()
        code = f.getcode()
        return (code, contents)
    except urllib2.HTTPError as e:
        return (e.code, e.read())
    except urllib2.URLError as e:
        return e


def apiHandler():
    """
    Function to process api calls and return feedback to the user.
    """
    username = n.views['username_input'].stringValue()
    hostname = n.views['hostname_input'].stringValue()

    # Get the current manifest selection
    manifest = getItem()

    # Print values
    print manifest
    print username
    print hostname

    machine_serial = getSerialNumber()
    url = "{0}{1}{2}".format(mwa2_url, '/api/manifests/', machine_serial)
    print url
    data = {"catalogs": [default_catalog],
            "display_name": hostname,
            "included_manifests": [manifest],
            "managed_installs": default_managed_installs,
            "managed_uninstalls": default_managed_uninstalls,
            "managed_updates": default_managed_updates,
            "optional_installs": default_optional_installs,
            "user": username
            }

    # Run our api caller on a loop so we can handle errors,
    # typos, and modifications.
    loop_handler = True
    x = 1
    while loop_handler:
        print "We're on api loop {0}".format(x)
        x += 1
        no_mod = " \n\nNo modifications have been made."
        get_request = apiCaller(url, machine_serial)
        print "API call status code: {0}".format(get_request[0])
        if get_request[0] == 200:  # manifest already exists
            checkbox = n.views['override_checkbox'].state()
            print "checkbox state is {0}".format(checkbox)
            if checkbox == 1:
                delete_request = apiCaller(url, machine_serial, 'DELETE')
                if delete_request[0] == 204:
                    showMsg("SUCESS: A manifest was deleted")
                else:
                    print delete_request
                    showMsg("ERROR: An error occurred while deleting the"
                            "previous manifest.{0}".format(no_mod))
            else:
                showMsg("WARNING: A manifest was already found for"
                        "this machine.{0}".format(no_mod))
                loop_handler = False
        elif get_request[0] == 401:  # unauthorized attempt
            showMsg("ERROR: An unauthorized attempt to make modifications."
                    "Please verify your API key.{0}".format(no_mod))
            loop_handler = False
        elif get_request[0] == 404:  # manifest does not exist
            post_request = apiCaller(url, machine_serial, 'POST', data)
            if post_request[0] == 201:
                showMsg("SUCESS: A manifest was created")
            else:
                showMsg("ERROR: {0} \n {1}{2}".format(get_request[0],
                        "Unable to create our manifest", no_mod))
            loop_handler = False
        else:
            showMsg("ERROR: {0}{1}".format(get_request[0], no_mod))
            loop_handler = False


def main():
    """
    Main method to handle setting GUI properties and attaching buttons.
    """
    n.attach(apiHandler, 'continueButton')
    n.attach(exitScript, 'exitButton')

    # Debug statements
    # print n.nib_contents
    # print n.views

    # Set values for drop down menu
    setItems(included_manifests_options)

    # Set default override state for the checkbox
    n.views['override_checkbox'].setState_(always_override)

    n.hidden = False
    n.run()

if __name__ == '__main__':
    main()
