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
Version: 2.0

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
from AppKit import NSWorkspace, NSBundle
from urllib2 import urlopen, URLError, HTTPError
from nibbler import *


listed_manifests = [
                    "manifest A",
                    "manifest B",
                    "manifest C",
                    ]
mwa2_url = "http://localhost:8000"

# Authrozation key for mwa2 API. Create this string via:
#   python -c 'import base64; print "Authorization: Basic %s" % base64.b64encode("username:password")'
# Make sure and only paste the "Basic STRINGVALUE"
authorization = "Basic ABBAABAABAABBAAB"

# Default munki catalog
default_catalog = "production"

# You should only rarely use the following...AKA: almost never!
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
    # Figure out how to pass an exit(20) to the imagr script component.


def show_msg(message):
    """Show feedback to our label"""
    feedback = n.views['feedback_result']
    feedback.setStringValue_(message)

def get_serialnumber():
    '''Returns the serial number of the Mac'''
    cmd = "/usr/sbin/ioreg -c \"IOPlatformExpertDevice\" | awk -F '\"' \
                                    '/IOPlatformSerialNumber/ {print $4}'"
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    (out, err) = proc.communicate()
    return out.strip()


def download_file(url, temp_file=None):
    """Download a simple file from the Internet."""
    print("Download a file")
    try:
        if not temp_file:
            temp_file = os.path.join(tempfile.mkdtemp(), 'tempdata')
        f = urlopen(url)
        with open(temp_file, "wb") as local_file:
            local_file.write(f.read())
        print("Download successful")
    except HTTPError, e:
        print("HTTP Error: %s, %s", e.code, url)
    except URLError, e:
        print("URL Error: %s, %s", e.reason, url)
    try:
        file_handle = open(temp_file)
        data = file_handle.read()
        file_handle.close()
    except (OSError, IOError):
        print("Couldn't read %s", temp_file)
        return False
    return data, temp_file


def api_caller(url, machine_serial, method='GET', data=None):
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


def api_handler(included_manifests, user, display_name):
    machine_serial = get_serialnumber()
    url = mwa2_url + '/api/manifests/' + machine_serial
    print url
    data = {"catalogs": [default_catalog],
            "display_name": display_name,
            "included_manifests": [included_manifests],
            "managed_installs": default_managed_installs,
            "managed_uninstalls": default_managed_uninstalls,
            "managed_updates": default_managed_updates,
            "optional_installs": default_optional_installs,
            "user": user
            }

    # check with api and make modifications if needed
    loop_handler = True
    x = 1
    while loop_handler:
        print "We're on api loop %d" % (x)
        x += 1
        get_request = api_caller(url, machine_serial)
        print "API call status code: " + str(get_request[0])
        if get_request[0] == 200:  # manifest already exists
            checkbox = n.views['override_checkbox'].state()
            print "checkbox state is %s" % str(checkbox)
            if checkbox == 1:
                delete_request = api_caller(url, machine_serial, 'DELETE')
                if delete_request[0] == 204:
                    show_msg(u"✅ SUCESS: A manifest was deleted")
                else:
                    print delete_request
                    error = u"❌ An error occurred while deleting the previous manifest."
                    show_msg(error)
            else:
                error = u"❌ A manifest was already found for this machine."
                show_msg(error)
                loop_handler = False
        elif get_request[0] == 401:  # unauthorized attempt
            error = u"❌ An unauthorized attempt to make modifications. Please verify your API key."
            show_msg(error)
            loop_handler = False
        elif get_request[0] == 404:  # manifest does not exist
            post_request = api_caller(url, machine_serial, 'POST', data)
            if post_request[0] == 201:
                show_msg(u"✅ SUCESS: A manifest was created")
            else:
                error = 'Unable to create our manifest'
                show_msg(u"❌ Error code: %s \n %s \n\nNo modifications have been made." % get_request[0], error)
            loop_handler = False
        else:
            show_msg(u"❌ Error code: %s \n\nNo modifications have been made." % get_request[0])
            loop_handler = False


def setItems(items):
    '''
    Set the items to appear in the pop up list.
    '''
    menu = n.views['manifest_input']
    menu.removeAllItems()
    for item in items:
        menu.addItemWithTitle_(item)


def PopUpButton():
    index = n.views['manifest_input'].indexOfSelectedItem()
    values = n.views['manifest_input'].itemTitles()
    return values[index]


def exitScript():
    '''Exit BananaEndocarp and don't continue the imagr workflow'''
    print "Goodbye!"
    n.quit()
    # Figure out how to pass an exit(1) to the imagr script component.


def runner():
    '''Wrapper to call the getADGroup method on button click. Handles feedback
    to feedback_result text field.'''
    username = n.views['username_input'].stringValue()
    hostname = n.views['hostname_input'].stringValue()
    feedback = n.views['feedback_result']

    # Get the current manifest selection
    manifest = PopUpButton()

    # Print values
    print manifest
    print username
    print hostname

    api_handler(manifest, username, hostname)


def main():
    '''Main method.'''
    n.attach(runner, 'continueButton')
    n.attach(exitScript, 'exitButton')

    # Debug statements
    # print n.nib_contents
    # print n.views

    # Set values for PopUpButton
    setItems(listed_manifests)

    # Set default override state for the checkbox
    n.views['override_checkbox'].setState_(always_override)

    n.hidden = False
    n.run()

if __name__ == '__main__':
    main()
