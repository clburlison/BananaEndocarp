#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
BananaEndocarp is a 'nice' GUI built using Tkinter for interacting with mwa2's api.
It was designed to work in a limited environment such as an NetInstall environment.
It connects to a mwa2 instance utilizing the API to create a manifest per machine.



Author: Clayton Burlison <https://clburlison.com>
Last modified: May 3, 2016
Version: 1.0



Lots of code from:
  http://zetcode.com/gui/tkinter/layout/
  http://stackoverflow.com/a/1451343/4811765 - tab focus window
  http://stackoverflow.com/a/10018670/4811765 - center window
  http://stackoverflow.com/a/24065533/4811765 - python exceptions
  https://goo.gl/Vw0S7p - embed image
"""

import sys
import os
import time
import tempfile
import httplib
import urllib
import urllib2
import json
import subprocess
from AppKit import NSWorkspace, NSBundle
from urllib2 import urlopen, URLError, HTTPError

try:
    # Python2
    from Tkinter import *
    import tkMessageBox as messagebox
except ImportError:
    # Python3
    from tkinter import *

listed_manifests = [
                    "manifestA",
                    "manifestB",
                    "manifestC",
                    ]
mwa2_url = "http://localhost:8000"
logo_url = "https://cburlison.s3.amazonaws.com/BananaEndocarp.gif"

authorization = "Basic ABBAABAABAABBAAB"
default_catalog = "production"
default_managed_installs = []
default_managed_uninstalls = []
default_managed_updates = []
default_optional_installs = []
show_success_status = True # When set to true, success status messages are displayed. DEFAULT = True
always_override = False # When set to true, always use values from GUI prompt. DEFAULT = False


class BananaError(Exception):
    """General exception for error messages"""
    pass

def show_warning(msg):
    """General method for warning messages. Returns bool values."""
    if always_override:
        return always_override
    else:
        return messagebox.askyesno("Warning","%s" % msg)

def show_msg(msg):
    """General method for notification messages"""
    if show_success_status:
        messagebox.showinfo("Notification","%s" % msg)

def focus_next_window(event):
    event.widget.tk_focusNext().focus()
    return "break"

def focus_prev_window(event):
    event.widget.tk_focusPrev().focus()
    return "break"

def center(win):
    """
    centers a Tkinter window. 'win' is the root or toplevel window to center
    """
    win.update_idletasks()
    width = win.winfo_width()
    frm_width = win.winfo_rootx() - win.winfo_x()
    win_width = width + 2 * frm_width
    height = win.winfo_height()
    titlebar_height = win.winfo_rooty() - win.winfo_y()
    win_height = height + titlebar_height + frm_width
    x = win.winfo_screenwidth() // 2 - win_width // 2
    y = win.winfo_screenheight() // 2 - win_height // 2
    win.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    win.deiconify()

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
        headers = {
            "Authorization": authorization,
            "Content-Type": "application/json"
        }, data = json.dumps(data))
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
        if get_request[0] == 200: # manifest already exists
            error = "A manifest was already found for this machine."
            choice = show_warning('%s \n\nDo you wish to override it?' % error)
            print "Override choice was: %s" % str(choice)
            if choice:
                delete_request = api_caller(url, machine_serial, 'DELETE')
                if delete_request[0] == 204:
                    msg = "SUCESS: We successfully deleted a manifest"
                    show_msg(msg)
                else:
                    print delete_request
                    error = "An error occurred while deleting the previous manifest."
                    raise BananaError('%s \n\nNo modifications have been made.' % error)
            else:
                raise BananaError('No modifications have been made.')
        elif get_request[0] == 401: # unauthorized attempt
            error = "An unauthorized attempt to make modifications. Please verify your API key."
            raise BananaError('%s \n\nNo modifications have been made.' % error)
        elif get_request[0] == 404: # manifest does not exist
            post_request = api_caller(url, machine_serial, 'POST', data)
            if post_request[0] == 201:
                loop_handler = False
                msg = "SUCESS: A manifest was created"
                show_msg(msg)
            else:
                error = 'Unable to create our manifest'
                raise BananaError('Error code: %s \n %s \n\nNo modifications have been made.' % get_request[0], error)
        else:
            raise BananaError('Error code: %s \n\nNo modifications have been made.' % get_request[0])

class BananaEndocarp(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent
        self.initUI()

    def initUI(self):
        self.parent.title("BananaEndocarp")
        self.pack(fill=BOTH, expand=True)

        # If logo_url is not set don't display a logo
        try:
            # logo = "/tmp/logo_url_logo.gif"
            # (data, local_path) = download_file(logo_url, logo)
            # image = PhotoImage(file=logo)
            image = PhotoImage(file='/Users/clburlison/Dropbox/src/mine/BananaEndocarp/BananaEndocarp.gif')
            image_logo = Label(self, image=image)
            image_logo.image = image
            image_logo.grid(row=0, column=0)
        except:
            pass

        label = Label(self, text="Select a munki manifest template:")
        label.grid(sticky=W, row=1, column=0)

        drop_down_var = StringVar(self)
        drop_down_var.set("                        ") # set initial value

        drop_down = OptionMenu(self, drop_down_var, *listed_manifests)
        drop_down.config(bg = "#ffffff")  # Set background color for the widget
        drop_down.grid(sticky=W, row=2, column=0)

        label = Label(self, text="User Name:", font="-weight bold")
        label.grid(sticky=W, row=3, column=0)

        label = Label(self, text="IE: John Smith. Blank for lab machines")
        label.grid(sticky=W, row=4, column=0)

        name_text = Text(self, height=1, width=30, font=("Helvetica"))
        name_text.grid(sticky=W, row=5, column=0)
        name_text.bind("<Tab>", focus_next_window)
        name_text.bind("<Shift-Tab>", focus_prev_window)

        label = Label(self, text="Hostname:", font="-weight bold")
        label.grid(sticky=W, row=6,column=0)

        label = Label(self, text="IE: 011-476-mac01.")
        label.grid(sticky=W, row=7,column=0)

        display_text = Text(self, height=1, width=30, font=("Helvetica"))
        display_text.grid(sticky=W, row=8, column=0)
        display_text.bind("<Tab>", focus_next_window)
        display_text.bind("<Shift-Tab>", focus_prev_window)

        cont_button = Button(self,
                             text="Continue",
                             command= lambda:
                             self.cont_button(drop_down_var.get(),
                                              name_text.get(1.0, "end-1c"),
                                              display_text.get("1.0","end-1c")
                                              ))
        cont_button.grid(row=9, column=0)

    def focus_next_window(event):
        self.event.widget.tk_focusNext().focus()
        return("break")

    def cont_button(self, included_manifests, user, display_name):
        print "Dropdown was: ", included_manifests
        print "User Name was: ", user
        print "Display was: %s \n" % display_name
        try:
            api_handler(included_manifests, user, display_name)
        except BananaError, e:
            messagebox.showwarning("Error","%s" % e)
        self.quit()


def main():
    # Disable the Rocket ship in dock
    bundle = NSBundle.mainBundle()
    info = bundle.localizedInfoDictionary() or bundle.infoDictionary()
    info['LSUIElement'] = '1'

    # disturbing hack warning!
    # this works around an issue with App Transport Security on 10.11
    # Reference: https://github.com/munki/munki/commit/1dd8329d665d1d724ddc56ea703552effcd42db8
    bundle = NSBundle.mainBundle()
    info = bundle.localizedInfoDictionary() or bundle.infoDictionary()
    info['NSAppTransportSecurity'] = {'NSAllowsArbitraryLoads': True}

    # Launch our GUI
    root = Tk()
    root.resizable(0,0) # disable resizing the window
    app = BananaEndocarp(root)
    center(root)
    root.mainloop()


if __name__ == '__main__':
    main()