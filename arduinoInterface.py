import numpy as np
import smbus
import time

add = []
modules = {}
roomControllers = {}
groups = {}
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


def _update_data():
    np.save('/home/pi/Documents/HAL/modules', modules)
    np.save('/home/pi/Documents/HAL/roomControllers', roomControllers)
    np.save('/home/pi/Documents/HAL/groups', groups)
    np.save('/home/pi/Documents/HAL/add', add)


def _recover_data_():
    global modules
    global roomControllers
    global groups
    global add
    modules = np.load('/home/pi/Documents/HAL/modules')
    roomControllers = np.load('/home/pi/Documents/HAL/roomControllers')
    groups = np.load('/home/pi/Documents/HAL/groups')
    add = np.load('/home/pi/Documents/HAL/add')


def _read_room_controllers_():
    for i in roomControllers:
        data = [1, i]
        bus.write_i2c_block_data(x10Arduino, data[0], data[1])
        states = [bus.read_byte_data(arduinoArduino, 200), bus.read_byte_data(add, 201)]
        roomControllers[i]['temp'] = states[0]
        roomControllers[i]['pir'] = states[1]


def _set_modules_():
    for i in modules:
        for x in roomControllers:
            if modules[i]['arduino'] == roomControllers[x]['name']:
                on = 0
                if modules[i]['temp']:
                    if roomControllers[x]['temp'] or modules[i]['user']:
                        on = 1
                    state = [groups[[modules[i]['class']]], _letter_to_num[modules[i]['house']],
                             modules[i]['unit'], on]
                    modules[i]['state'] = on
                else:
                    if roomControllers[x]['pir'] or modules[i]['user']:
                        on = 1
                    state = [_letter_to_num[modules[i]['class']], _letter_to_num[modules[i]['house']],
                             modules[i]['unit'], on]
                    modules[i]['state'] = on
                bus.write_i2c_block_data(x10Arduino, state[0], state[1:3])
                if time.time() - modules[i]['start'] > 18000:
                    modules[i]['user'] = False


def _add_room_controller():
    data = [2, len(roomControllers)]
    bus.write_i2c_block_data(arduinoArduino, data[0], data[1])


def _add_group_():
    data = [2, len(groups)]
    bus.write_i2c_block_data(x10Arduino, data[0], data[1])


while __name__ == "__main__":
    _recover_data_()
    if add[0]:
        _add_room_controller()
        add[0] = False
        np.save('/home/pi/Documents/HAL/add', add)
    else:
        _read_room_controllers_()
        np.save('/home/pi/Documents/HAL/roomControllers', roomControllers)
    if add[1]:
        _add_group_()
        add[1] = False
        np.save('/home/pi/Documents/HAL/add', add)
    else:
        _set_modules_()
    break