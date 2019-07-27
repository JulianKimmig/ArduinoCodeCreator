from ArduinoCodeCreator.arduino_data_types import uint16_t, uint8_t, void, uint32_t, uint8_t_pointer
from ArduinoCodeCreator.basic_types import Function

class ArduinoClass():
    def __init__(self,*attributes):
        for a in attributes:
            a.obscurable = False
            setattr(self,a.name,a)

Arduino = ArduinoClass(
    Function("analogRead", [uint8_t],uint16_t),
    Function("analogWrite", [uint8_t,uint8_t],uint16_t),
    Function("digitalRead", [uint8_t],uint16_t),
    Function("digitalWrite", [uint8_t,uint8_t],uint16_t),
    Function("random", arguments=[],return_type=uint16_t ),
    Function(name="randomSeed", arguments=[uint32_t],return_type=void),
    Function(return_type=void, name="memcpy", arguments=[uint8_t_pointer,uint8_t_pointer,uint8_t]),
    Function(return_type=uint32_t, name="millis"),
    Function(return_type=uint32_t, name="max", arguments=[uint32_t,uint32_t]),
    Function(return_type=uint32_t, name="min", arguments=[uint32_t,uint32_t]),
    Function(return_type=void, name="delay", arguments=[uint32_t,uint32_t]),
)

Serial = ArduinoClass(
    Function("write",void,[])
)
