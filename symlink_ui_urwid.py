#!/usr/bin/python3
# Copyright (c) 2010-2019 Rob Lanphier
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.

import urwid
from collections import OrderedDict

FIELD_DEFS = [
    ['origlink', 'Link name', 'readonlytext', ''],
    ['origreadlink', 'Full link (readlink -f)', 'readonlytext', ''],
    ['targetref', 'Target value', 'text', ''],
    ['targetref-userroot',
        'Alternative (userroot-based)', 'readonlytext', ''],
    ['targetref-relpath',
        'Alternative (relpath-based)', 'readonlytext', ''],
    ['allowbroken', 'Allow writing broken symlink?', 'checkbox', False]
]


class ExitUrwidForm(Exception):

    def __init__(self, exit_token=None):
        self.exit_token = exit_token


class FieldManager(object):
    """ 
    This class manages the field data without being entangled in the 
    implementation details of the widget set.
    """

    def __init__(self, defaults):
        self.fieldset = OrderedDict()
        self.getters = {}
        for i, d in enumerate(FIELD_DEFS):
            key = d[0]
            self.fieldset[key] = {}
            self.getters[key] = {}
            self.fieldset[key]['label'] = d[1]
            self.fieldset[key]['type'] = d[2]
            self.fieldset[key]['default'] = d[3]
            self.getters[key] = lambda k=key: self.fieldset[k]['default']
        for key, val in defaults.items():
            self.fieldset[key]['default'] = val

    def set_getter(self, name, function):
        """ 
        This is where we collect all of the field getter functions.
        """
        self.getters[name] = function

    def get_value(self, name):
        """
        This will actually get the value associated with a field name.
        """
        return self.getters[name]()

    def get_value_dict(self):
        """
        Dump everything we've got.
        """
        retval = OrderedDict()
        for key in self.fieldset:
            retval[key] = self.getters[key]()
        return retval


def get_field(fieldname, fielddef, fieldmgr):
    """ Build a field in our form.  Called from get_body()"""
    # we don't have hanging indent, but we can stick a bullet out into the
    # left column.
    asterisk = urwid.Text(('label', '* '))
    label = urwid.Text(('label', fielddef['label']))
    colon = urwid.Text(('label', ': '))

    defaultval = fieldmgr.get_value(fieldname)
    if fielddef['type'] == 'text':
        field = urwid.Edit('', defaultval)

        def getter():
            """ 
            Closure around urwid.Edit.get_edit_text(), which we'll
            use to scrape the value out when we're all done.
            """
            return field.get_edit_text()
        fieldmgr.set_getter(fieldname, getter)
    elif fielddef['type'] == 'readonlytext':
        field = urwid.Text(('label', defaultval))
    elif fielddef['type'] == 'checkbox':
        field = urwid.CheckBox('', defaultval)

        def getter():
            """ 
            Closure around urwid.CheckBox.get_state(), which we'll
            use to scrape the value out when we're all done. 
            """
            return field.get_state()
        fieldmgr.set_getter(fieldname, getter)

    field = urwid.AttrWrap(field, 'field', 'fieldfocus')

    # put everything together.  Each column is either 'fixed' for a fixed width,
    # or given a 'weight' to help determine the relative width of the column
    # such that it can fill the row.
    editwidget = urwid.Columns([('fixed', 2, asterisk),
                                ('weight', 1, label),
                                ('fixed', 2, colon),
                                ('weight', 2, field)])

    wrapper = urwid.AttrWrap(editwidget, None, {'label': 'labelfocus'})
    return urwid.Padding(wrapper, ('fixed left', 3), ('fixed right', 3))


def get_buttons():
    """ renders the ok and cancel buttons.  Called from get_body() """

    # this is going to be what we actually do when someone clicks the button
    def ok_button_callback(button):
        raise ExitUrwidForm(exit_token='ok')

    # leading spaces to center it....seems like there should be a better way
    b = urwid.Button('  OK', on_press=ok_button_callback)
    okbutton = urwid.AttrWrap(b, 'button', 'buttonfocus')

    # second verse, same as the first....
    def cancel_button_callback(button):
        raise ExitUrwidForm(exit_token='cancel')
    b = urwid.Button('Cancel', on_press=cancel_button_callback)
    cancelbutton = urwid.AttrWrap(b, 'button', 'buttonfocus')

    return urwid.GridFlow([okbutton, cancelbutton], 10, 7, 1, 'center')


def get_header():
    """ the header of our form, called from main() """
    text_header = ("lnedit - symlink editor"
                   " - Use arrow keys to select a field to edit, select 'OK'"
                   " when finished, or press ESC/select 'Cancel' to exit")
    header = urwid.Text(text_header)
    return urwid.AttrWrap(header, 'header')


class AdvancingListBox(urwid.ListBox):
    """
    This class makes it so that the cursor advances to the "<Ok>"
    button upon receiving an 'enter'.
    """

    def keypress(self, size, key):
        key = super(AdvancingListBox, self).keypress(size, key)
        if key == 'enter':
            if self.focus_position == 3:
                self.focus_position = 8
            return key


def get_body(fieldmgr):
    """ the body of our form, called from main() """
    # build the list of field widgets
    fieldwidgets = [urwid.Divider(bottom=2)]
    for fieldname, fielddef in fieldmgr.fieldset.items():
        fieldwidgets.append(get_field(fieldname, fielddef, fieldmgr))

    fieldwidgets.append(urwid.Divider(bottom=1))

    fieldwidgets.append(get_buttons())

    # SimpleListWalker provides simple linear navigation between the widgets
    listwalker = urwid.SimpleListWalker(fieldwidgets)

    # ListBox is a scrollable frame around a list of elements
    #listbox = urwid.ListBox(listwalker)
    listbox = AdvancingListBox(listwalker)
    return urwid.AttrWrap(listbox, 'body')


def start_main_loop(defaults):
    # call our homebrewed object for managing our fields
    fieldmgr = FieldManager(defaults)

    #  Our main loop is going to need three things:
    #  1. topmost widget - a "box widget" at the top of the widget hierarchy
    #  2. palette - style information for the UI
    #  3. unhandled_input function - to deal with top level keystrokes

    #  1. topmost widget - a "box widget" at the top of the widget hierarchy
    header = get_header()
    body = get_body(fieldmgr)
    frame = urwid.Frame(body, header=header)

    #  2. palette - style information for the UI
    palette = [
        ('body', 'white', 'black', 'standout'),
        ('header', 'white', 'dark blue', 'bold'),
        ('labelfocus', 'white', 'dark blue', 'bold, underline'),
        ('label', 'white', 'black'),
        ('fieldfocus', 'white,underline', 'dark blue', 'bold, underline'),
        ('field', 'white', 'black'),
        ('button', 'light gray', 'black', 'bold'),
        ('buttonfocus', 'white', 'dark blue'),
    ]

    #  3. unhandled_input function - to deal with top level keystrokes
    def unhandled(key):
        """ 
        Function to pass in to MainLoop to handle otherwise unhandled 
        keystrokes.
        """
        if key == 'esc':
            raise ExitUrwidForm(exit_token='cancel')

    # Pass the topmost box widget to the MainLoop to start the show
    urwidloop = urwid.MainLoop(frame, palette, unhandled_input=unhandled)
    try:
        urwidloop.run()
    except ExitUrwidForm as inst:
        import json
        print(json.dumps(fieldmgr.get_value_dict(), indent=4))
        print("Exit value: " + inst.exit_token)

def main():
    testvalues = {
        "origlink": "18W28tmp",
        "origreadlink": "/home/robla/tech/util/timeutil/weekutil/src-timeutil/18W28tmp",
        "targetref": ".userroot/tmp/2018/18W28/timeutil",
        "targetref-userroot": ".userroot/tmp/2018/18W28/timeutil",
        "targetref-relpath": "../../../../../../tech/util/timeutil/weekutil/src-timeutil/18W28tmp",
        "allowbroken": False
    }

    start_main_loop(testvalues)

if '__main__' == __name__:
    main()
