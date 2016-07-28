import RPi.GPIO as IO
import serial
import smbus
import time
import sys
import functools
from multiprocessing import Process, Queue
import os
import random
from piui import PiUi
current_dir = os.path.dirname(os.path.abspath(__file__))
port = 1
addArduino = False
modules = {}
arduinos = {}
groups = {}
# arduino con
arduinoCodes = {
    'off': 0,
    'on': 1,
    'dim': 2,
    'updata': 1,
    'newMod': 2,
    }
_letter_to_num = {
    'A': 1,
    'B': 2,
    'C': 3,
    'D': 4,
    'E': 5,
    'F': 6,
    'G': 7,
    'H': 8,
    'I': 9,
    'J': 10,
    'K': 11,
    'L': 12,
    'M': 13,
    'N': 14,
    'O': 15,
    'P': 16
}
bus = smbus.SMBus(1)
x10Arduino = 4
arduinoArduino = 5


def _i2c_write_(address, var):
    bus.write_byte(address, var)


def _i2c_read_(address):
    return bus.read_byte(address)
# data storage


def _update_stored_data():
    np.save('modules', modules)
    np.save('arduinos', arduinos)


def _recover_data_():
    global modules
    global arduinos
    modules = np.load('modules')
    arduinos = np.load('arduinos')

# user interface


class _UserInterface_(object):
    global addArduino

    def __init__(self):
        self.title = None
        self.txt = None
        self.nameTxt = None
        self.houseTxt = None
        self.tempTxt = None
        self.arduinoTxt = None
        self.classTxt= None
        self.img = None
        self.ui = PiUi(img_dir=os.path.join(current_dir, 'imgs'))
        self.src = "sunset.png"

    def _swicth_state_(self, mod, value):
        modules[mod]['state'] = not modules[mod]['state']
        modules[mod]['user'] = True
        modules[mod]['start'] = time.time()
        _loop_()
        
    def _house_(self, house, group):
        self.page = self.ui.new_ui_page(title= house, prev_text="Back", onprevclick=self._houses_)
        self.list = self.page.add_list()
        _loop_()
        for i in modules:
            if modules[i]["house"] == house and modules[i]['class'] == group:
                self.list.add_item(modules[i]['name'], chevron=False, toggle=modules[i]["house"],
                                   ontoggle=functools.partial(self._swicth_state_, i))

    def _houses_(self, group):
        self.page = self.ui.new_ui_page(title="Pick house", prev_text="Back", onprevclick=self._main_menu_)
        self.list = self.page.add_list()
        self.list.add_item("House A", chevron=True, onclick=functools.partial(self._house_, 'A', group))
        self.list.add_item("House B", chevron=True, onclick=functools.partial(self._house_, 'B', group))
        self.list.add_item("House C", chevron=True, onclick=functools.partial(self._house_, 'C', group))
        self.list.add_item("House D", chevron=True, onclick=functools.partial(self._house_, 'D', group))
        self.list.add_item("House E", chevron=True, onclick=functools.partial(self._house_, 'E', group))
        self.list.add_item("House F", chevron=True, onclick=functools.partial(self._house_, 'F', group))
        self.list.add_item("House G", chevron=True, onclick=functools.partial(self._house_, 'G', group))
        self.list.add_item("House H", chevron=True, onclick=functools.partial(self._house_, 'H', group))
        self.list.add_item("House I", chevron=True, onclick=functools.partial(self._house_, 'I', group))
        self.list.add_item("House J", chevron=True, onclick=functools.partial(self._house_, 'J', group))
        self.list.add_item("House K", chevron=True, onclick=functools.partial(self._house_, 'K', group))
        self.list.add_item("House L", chevron=True, onclick=functools.partial(self._house_, 'L', group))
        self.list.add_item("House M", chevron=True, onclick=functools.partial(self._house_, 'M', group))
        self.list.add_item("House N", chevron=True, onclick=functools.partial(self._house_, 'N', group))
        self.list.add_item("House O", chevron=True, onclick=functools.partial(self._house_, 'O', group))
        self.list.add_item("House P", chevron=True, onclick=functools.partial(self._house_, 'P', group))
        self.ui.done()
        _loop_()

    def _classes_(self):
        found = []
        _loop_()
        self.page = self.ui.new_ui_page(title='Groups', prev_text="Back", onprevclick=self._main_)
        self.list = self.page.add_list()
        for i in modules:
            for x in range(len(found)):
                if modules[i]['class'] != found[x]:
                    self.list.add_item(modules[i]['class'], chevron=True,
                                       onclick=functools.partial(self._houses_, modules[i]['class']))

    def _add_mod_(self):
        current_number_in_house = 1
        temp_con = False
        for i in modules:
            if modules[i]['house'] == self.houseTxt.get_text() and modules[i]['class'] == self.classTxt.get_text():
                current_number_in_house = + 1
        if self.tempTxt.get_text().lower() == 'yes':
            temp_con = True
        if current_number_in_house <= 16:
            modules[len(modules)] = ({'name': self.nameTxt.get_text(), 'arduino': self.arduinoTxt,
                                      'class': self.classTxt.get_text(),
                                      'house': self.houseTxt.get_text().upper(),
                                      'unit': int(current_number_in_house), 'temp': temp_con,
                                      'state': False})
            _update_stored_data()
            self.page = self.ui.new_ui_page(title="You successfully add a new Module")
            self.title = self.page.add_textbox("Set the X10 module to unit number:", "h1")
            self.title = self.page.add_textbox(str(current_number_in_house), "h1")
            button = self.page.add_button('Return to home page', self._main_menu_)
            self.ui.done()
        else:
            self.page = self.ui.new_ui_page(title="Failed to add the new module.")
            self.title = self.page.add_textbox("There too many modules for the choosen house. Pick another house.", 'h1')
            button = self.page.add_button("return to page to add module", self._add_module_)
        _loop_()

    def _add_module_(self):
        self.page = self.ui.new_ui_page(title="Add Module" , prev_text="Back", onprevclick=self._main_menu_)
        self.title = self.page.add_textbox("Name of Module", 'h1')
        self.nameTxt = self.page.add_input('text', 'name')
        self.title = self.page.add_textbox('Name of Group', 'h1')
        self.classTxt = self.page.add_image('text', 'Group')
        self.title = self.page.add_textbox('House name', 'h1')
        self.houseTxt = self.page.add_input('text', 'House Letter')
        self.title = self.page.add_textbox("Arduino", "h1")
        self.arduinoTxt = self.page.add_input('text', 'Arduino name')
        self.title = self.page.add_textbox('Tempture controled', 'h1')
        self.tempTxt = self.page.add_input('text', 'Control by Temp')
        button = self.page.add_button('Add Module', self._add_mod_)
        self.ui.done()
        _loop_()

    def _new_arduino_(self):
        arduinos[len(arduinos)] = {'name': self.arduinoTxt.get_text(), 'temp': 0, 'pir': 0}
        _update_stored_data()
        self.page = self.ui.new_ui_page(title="Successfully added an arduino")
        button = self.page.add_button('Return to Main page', self._main_menu_)
        _loop_()

    def _add_arduino_(self):
        self.page = self.ui.new_ui_page(title="Add Arduino", prev_text="Back", onprevclick=self._main_menu_)
        self.title = self.page.add_textbox("Enter name")
        self.arduinoTxt = self.page.add_input("text", "Name")
        button = self.page.add_button("Add Arduino", self._new_arduino_)
        global addArduino
        addArduino = True
        self.ui.done()
        _loop_()

    def _new_group_(self):
        groups.append({'name': self.classTxt.get_text(), 'number': len(groups)})
        self.page = self.ui.new_ui_page(title="Succesfully added the Group")
        button =self.page.add_button("Return the Main Menu", self._main_menu_)

    def _add_group_(self):
        _loop_()
        self.page = self.ui.new_ui_page(title="Add Group", prev_text='Back', onprevclick=self._main_)
        self.title = self.page.add_textbox("Enter Name of Group", 'h1')
        self.classTxt = self.page.add_input('type',"Name of Group")
        button = self.page.add_button("Add Group", self._new_group_)

    def _check_help_(self):
        self.page = self.ui.new_ui_page(title='Checking Module Help', prev_text='Back', onprevclick=self._help_)
        self.title = self.page.add_textbox("Point:", 'h1')
        self.title = self.page.add_textbox("    On or off module manualy")
        self.title = self.page.add_textbox("How to use", 'h1')
        self.title = self.page.add_textbox("    Click on the House the module is in.")
        self.title = self.page.add_textbox("    The toggle button is used to turn on and off the module")
        self.ui.done()
        _loop_()

    def _mod_help_(self):
        self.page = self.ui.new_ui_page(title='Adding Module Help', prev_text='Back', onprevclick=self._help_)
        self.title = self.page.add_textbox("First: Enter the name that you want the module to be called.")
        self.title = self.page.add_textbox("Second: Enter the House that you want the module to be in.")
        self.title = self.page.add_textbox("Third: Enter the name of the arduino you want to control the module.")
        self.title = self.page.add_textbox("Fourth: Enter 'yes' if you want the "
                                           "module to be controlled by a thermometer.")
        self.title = self.page.add_textbox("Fifth: Hit the 'Add Module' button.")
        self.title = self.page.add_textbox("Sixth: Set the number on the module to the number the Pi display.")
        _loop_()

    def _arduino_help_(self):
        self.page = self.ui.new_ui_page(title="Adding Arduino Help", prev_text='Back', onprevclick=self._help_)
        self.title = self.page.add_textbox("Just enter the name of the arduino that you want.")
        self.ui.done()
        _loop_()

    def _help_(self):
        self.page = self.ui.new_ui_page(title="Help", prev_text="Back", onprevclick=self._main_menu_)
        self.list = self.page.add_list()
        self.list.add_item("Check House", chevron=True, onclick=self._check_help_)
        self.list.add_item("Add Module", chevron=True, onclick=self._mod_help_)
        self.list.add_item("add Arduino", chevron=True, onclick=self._arduino_help_)
        self.ui.done()
        _loop_()

    def _main_menu_(self):
        self.page = self.ui.new_ui_page(title="Welcome to the HAL interface.")
        self.list = self.page.add_list()
        self.list.add_item("Check Houses", chevron=True, onclick=self._classes_)
        self.list.add_item("Add Module", chevron=True, onclick=self._add_module_)
        self.list.add_item("Add Arduino", chevron=True, onclick=self._add_arduino_)
        self.list.add_item("Help", chevron=True, onclick=self._help_)
        self.ui.done()
        _loop_()

    def _main_(self):
        self._main_menu_()
        self.ui.done()
        _loop_()


def _main_():
    piui = _UserInterface_()
    piui._main_()


def _read_arduinos_():
    for i in arduinos:
        _i2c_write_(arduinoArduino, 1)
        _i2c_write_(arduinoArduino, i)
        _i2c_write_(arduinoArduino, 0)
        states = _i2c_read_(arduinoArduino)
        arduinos[i]['temp'] = states[0]
        arduinos[i]['pir'] = states[1]


def _set_modules_():
    for i in modules:
        for x in arduinos:
            if modules[i]['arduino'] == arduinos[x]['name']:
                on = 0
                if modules[i]['temp']:
                    if arduinos[x]['temp'] or modules[i]['user']:
                        on = 1
                    state = [groups[[modules[i]['class']]], _letter_to_num[modules[i]['house']],
                             modules[i]['unit'], on]
                    modules[i]['state'] = on
                else:
                    if arduinos[x]['pir'] or modules[i]['user']:
                        on = 1
                    state = [_letter_to_num[modules[i]['class']], _letter_to_num[modules[i]['house']],
                             modules[i]['unit'], on]
                    modules[i]['state'] = on
                _i2c_write_(x10Arduino, state)
                if time.time() - modules[i]['start'] > 18000:
                    modules[i]['user'] = False


def _new_arduino(number):
    _i2c_write_(arduinoArduino, 2)
    _i2c_write_(arduinoArduino, number)


def _arduino_():
    if addArduino:
        _new_arduino(len(arduinos) - 1)
        global addArduino
        addArduino = False
    else:
        _read_arduinos_()


def _loop_():
    _arduino_()
    _set_modules_()


if __name__ == "__main__":
    _main_()
