import sys
import numpy as np

class ArduinoDataType:
    def __init__(self,arduino_code,python_type = None,minimum=None,maximum=None):

        self.python_type = python_type
        if self.python_type is None:
            try:
                self.python_type = getattr(np,arduino_code.replace("_t",""))
            except:
                self.python_type = np.uint16


        if minimum is None:
            try:minimum = np.iinfo(self.python_type).min
            except:minimum = -np.inf
        if maximum is None:
            try:maximum = np.iinfo(self.python_type).max
            except:maximum = np.inf
        self.byte_size = np.array([self.python_type(0)]).itemsize
        self.minimum,self.maximum = minimum,maximum
        self.arduino_code = arduino_code

    def __str__(self):
        return self.arduino_code

    def __repr__(self):
        return self.arduino_code

    def __call__(self, *args, **kwargs):
        return self.arduino_code

    def to_pointer(self):
        pointer = getattr(sys.modules[self.__module__],self.arduino_code+"_pointer")
        if pointer is None:
            pointer =  ArduinoDataType(self.arduino_code+"*")
        return pointer

uint8_t = ArduinoDataType("uint8_t")
uint16_t = ArduinoDataType("uint16_t")
uint32_t =  ArduinoDataType("uint32_t")
int32_t =  ArduinoDataType("uint32_t")
uint64_t =  ArduinoDataType("uint64_t")

bool =  ArduinoDataType("bool")

void = ArduinoDataType("void")


uint8_t_pointer =  ArduinoDataType("uint8_t*")
int = uint16_t

template_void =  ArduinoDataType("template< typename T> void")
T =  ArduinoDataType("T")