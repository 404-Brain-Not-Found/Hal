import RPi.GPIO as IO
import serial
import time
import sys
import functools
import os
import random
from piui import PiUi
current_dir = os.path.dirname(os.path.abspath(__file__))
global modRecords
modules = []
#arduio con
arduinoCodes = {
    'off': 0,
    'on': 1,
    'dim': 2,
    'updata' : 1,
    'newMod' : 2,
    }
conPin = 11
def sendDataToArduino(code):
    code = bin(code)
    for i in range(4, 10):
        IO.setup(i,IO.OUT)
        IO.output(i, code[i-2])
        break
    IO.setup(conPin, IO.IN)
    while not IO.input(conPin) :
          break

    

def dataFromArduino():
    data = range(6)
    for i in range(4, 10):
          IO.setup(i,IO.IN)
          data[i - 4] = IO.input(i)
          break
    IO.setup(conPin, IO.OUT)
    IO.output(conPin, IO.HIGH)
    return (1 * data[0] + 2 * data[1] + 4 * data[2] + 8 * data[3] + 16 * data[4] + 32 * data[5])
#x10


#-----------------------------------------------------------
# Firecracker spec requires at least 0.5ms between bits
#-----------------------------------------------------------
DELAY_BIT = 0.001 # Seconds between bits
DELAY_FIN = 1     # Seconds to wait before disabling after transmit

#-----------------------------------------------------------
# House and unit code table
#-----------------------------------------------------------
HOUSE_LIST = {
   'A' : 0x6000, # a
   'B' : 0x7000, # b
   'C' : 0x4000, # c
   'D' : 0x5000, # d
   'E' : 0x8000, # e
   'F' : 0x9000, # f
   'G' : 0xA000, # g
   'H' : 0xB000, # h
   'I' : 0xE000, # i
   'J' : 0xF000, # j
   'K' : 0xC000, # k
   'L' : 0xD000, # l
   'M' : 0x0000, # m
   'N' : 0x1000, # n
   'O' : 0x2000, # o
   'P' : 0x3000  # p
   }

UNIT_LIST = {
  '1' : 0x0000, # 1
  '2' : 0x0010, # 2
  '3' : 0x0008, # 3
  '4' : 0x0018, # 4
  '5' : 0x0040, # 5
  '6' : 0x0050, # 6
  '7' : 0x0048, # 7
  '8' : 0x0058, # 8
  '9' : 0x0400, # 9
  '10' : 0x0410, # 10
  '11' : 0x0408, # 11
  '12' : 0x0400, # 12
  '13' : 0x0440, # 13
  '14' : 0x0450, # 14
  '15' : 0x0448, # 15
  '16' : 0x0458  # 16
  }
MAX_UNIT = 16
    
#-----------------------------------------------------------
# Command Code Masks
#-----------------------------------------------------------
CMD_ON   = 0x0000
CMD_OFF  = 0x0020
CMD_BRT  = 0x0088
CMD_DIM  = 0x0098

#-----------------------------------------------------------
# Data header and footer
#-----------------------------------------------------------
DATA_HDR = 0xD5AA
DATA_FTR = 0xAD

#-----------------------------------------------------------
# Put firecracker in standby
#-----------------------------------------------------------
def set_standby(s):
    s.setDTR(True)
    s.setRTS(True)
    
#-----------------------------------------------------------
# Turn firecracker "off"
#-----------------------------------------------------------
def set_off(s):
    s.setDTR(False)
    s.setRTS(False)

#-----------------------------------------------------------
# Send data to firecracker
#-----------------------------------------------------------
def send_data(s, data, bytes):
    mask = 1 << (bytes - 1)
    
    set_standby(s)
    time.sleep(DELAY_BIT)    

    for i in range(bytes):
        bit = data & mask        
        if bit == mask:
            s.setDTR(False)
        elif bit == 0:
            s.setRTS(False)

        time.sleep(DELAY_BIT)
        set_standby(s)
        
        # Then stay in standby at least 0.5ms before next bit
        time.sleep(DELAY_BIT)

        # Move to next bit in sequence
        data = data << 1
    
#-----------------------------------------------------------
# Generate the command word
#-----------------------------------------------------------
def build_command(house, unit, action):
    cmd = 0x00000000    
    house_int = ord(house.upper()) - ord('A')

    #-------------------------------------------------------
    # Add in the house code
    #-------------------------------------------------------
    if house_int >= 0 and house_int <= ord('P') - ord('A'):
        cmd = cmd | HOUSE_LIST[ house_int ]
    else:
        print "Invalid house code ", house, house_int
        return
        
    #-------------------------------------------------------
    # Add in the unit code. Ignore if bright or dim command,
    # which just applies to last unit.
    #-------------------------------------------------------
    if unit > 0 and unit < MAX_UNIT:
        if action.upper() != 'BRT' and action.upper() != 'DIM':
            cmd = cmd | UNIT_LIST[ unit - 1 ]
    else:
        print "Invalid Unit Code", unit
        return

    #-------------------------------------------------------
    # Add the action code
    #-------------------------------------------------------
    if action.upper() == 'ON':
        cmd = cmd | CMD_ON
    elif action.upper() == 'OFF':
        cmd = cmd | CMD_OFF
    elif action.upper() == 'BRT':
        cmd = cmd | CMD_BRT
    elif action.upper() == 'DIM':
        cmd = cmd | CMD_DIM
    else:
        print "Invalid Action Code", action
        return
    
    return cmd

#-----------------------------------------------------------
# Send Command to Firecracker
#   portname: Serial port to send to
#   house:    house code, character 'a' to 'p'
#   unit:     unit code, integer 1 to 16
#   action:   string 'ON', 'OFF', 'BRT' or 'DIM'
#-----------------------------------------------------------
def send_command( portname, house, unit, action ):
    cmd = build_command( house, unit, action )
    if cmd != None:
        try:
            s = serial.Serial(portname)
            send_data( s, DATA_HDR, 16 ) # Send data header
            send_data( s, cmd, 16 )      # Send data
            send_data( s, DATA_FTR, 8 )  # Send footer
            time.sleep( DELAY_FIN )      # Wait for firecracker to finish transmitting
            set_off(s)                   # Shut off the firecracker
            s.close()
            return True

        except serial.SerialException:
            print 'ERROR opening serial port', portname
            return False
#data storage

def updataStoredData():
    np.save('mod_records', modrecords)
def recoverData():
    modRecords = np.load('mod_records')
#user interface
class userInterface(object):
    def __init__(self):
        self.title = None
        self.txt = None
        self.nameTxt = None
        self.houseTxt = None
        self.tempTxt = None
        self.img = None
        self.ui = PiUi(img_dir=os.path.join(current_dir, 'imgs'))
        self.src = "sunset.png"

    def swicthState(self, mod):
        modules[mod][4] = not modules[mod][4]
        
    def House(self, house):
        self.page=self.ui.new_ui_page(title="House " + house, prev_text="Back", onprevclick=self.Houses)
        self.list = self.page.add_list()
        lookFor = HOUSE_LIST[house]
        for i in modules:
            if modules[i][1] == lookFor:
                if modules[i][5]:
                    self.list.add_item(module[i][0] + " is on", onclick=functools.partial(self.swicthState, i))
                else:
                    self.list.add_item(module[i][0] + " is on", onclick=functools.partial(self.swicthState, i))
            
        
    def Houses(self):
        self.page = self.ui.new_ui_page(title="Pick house", prev_text="Back", onprevclick=self.main_menu)
        self.list = self.page.add_list()
        self.list.add_item("House A", chevron=True, onclick=functools.partial(self.House, 'A'))
        self.list.add_item("House B", chevron=True, onclick=functools.partial(self.House, 'B'))
        self.list.add_item("House C", chevron=True, onclick=functools.partial(self.House, 'C'))
        self.list.add_item("House D", chevron=True, onclick=functools.partial(self.House, 'D'))
        self.list.add_item("House E", chevron=True, onclick=functools.partial(self.House, 'E'))
        self.list.add_item("House F", chevron=True, onclick=functools.partial(self.House, 'F'))
        self.list.add_item("House G", chevron=True, onclick=functools.partial(self.House, 'G'))
        self.list.add_item("House H", chevron=True, onclick=functools.partial(self.House, 'H'))
        self.list.add_item("House I", chevron=True, onclick=functools.partial(self.House, 'I'))
        self.list.add_item("House J", chevron=True, onclick=functools.partial(self.House, 'J'))
        self.list.add_item("House K", chevron=True, onclick=functools.partial(self.House, 'K'))
        self.list.add_item("House L", chevron=True, onclick=functools.partial(self.House, 'L'))
        self.list.add_item("House M", chevron=True, onclick=functools.partial(self.House, 'M'))
        self.list.add_item("House N", chevron=True, onclick=functools.partial(self.House, 'N'))
        self.list.add_item("House O", chevron=True, onclick=functools.partial(self.House, 'O'))
        self.list.add_item("House P", chevron=True, onclick=functools.partial(self.House, 'P'))
        self.ui.done()

    def addMod(self):
        currentNumberInHouse = 1
        tempCon = False
        for i in modules:
            if modules[i][0] == self.houseTxt.get_text():
                currentNumberInHouse =+ 1
        if self.tempTxt.get_text().lower() == 'yes':
            tempCon = True
        if currentNumberInHouse <= 16:
            modules.append([self.nameTxt.get_text(), HOUSE_LIST[self.houseTxt.get_text().upper()], UNIT_LIST[str(currentNumberInHouse)], tempCon, False])
            self.page = self.ui.new_ui_page(title="You successfuly add a new Module", prev_text="Back to Main menu", onprevclick=self.main_menu)
            self.title = self.page.add_textbox("Set the X10 module to unit number:", "h1")
            self.title = self.page.add_textbox(str(currentNumberInHouse), "h1")
            button = self.page.add_button('Return to home page', self.main_menu)
            self.ui.done()
        else:
            self.page = self.ui.new_ui_page(title="Failed to add the new module.")
            self.title = self.page.add_textbox("There too many modules for the choosen house. Pick another house.", 'h1')
            button = self.page.add_button("return to page to add module", self.addModule)

    def addModule(self):
        self.page = self.ui.new_ui_page(title="Add Module" , prev_text="Back", onprevclick=self.main_menu)
        self.title = self.page.add_textbox("Name of Module", 'h1')
        self.nameTxt = self.page.add_input('text', 'name')
        self.title = self.page.add_textbox('House name', 'h1')
        self.houseTxt = self.page.add_input('text', 'House Letter')
        self.title = self.page.add_textbox('Tempture controled', 'h1')
        self.tempTxt = self.page.add_input('text', 'Control by Temp')
        button = self.page.add_button('Add Module', self.addMod)
        self.ui.done()
                                        
    
    def main_menu(self):
        self.page = self.ui.new_ui_page(title="Welcome to the HAL interface.")
        self.list = self.page.add_list()
        self.list.add_item("Check Houses", chevron=True, onclick=self.Houses)
        self.list.add_item("Add Module", chevron=True, onclick=self.addModule)
        self.ui.done()

    def main(self):
        self.main_menu()
        self.ui.done()
def main():
    piui = userInterface()
    piui.main()
if __name__ == "__main__":
    main()
