from ArduinoCodeCreator.arduino_data_types import *
from ArduinoCodeCreator.basic_types import Function, ArduinoClass, Array, Variable


class ArduinoBaseClass(ArduinoClass):
    class_name="Arduino"
    # Digital I/O
    INPUT = Variable("INPUT", obscurable=False)
    OUTPUT = Variable("OUTPUT", obscurable=False)
    INPUT_PULLUP = Variable("INPUT_PULLUP", obscurable=False)
    EXTERNAL = Variable("EXTERNAL", obscurable=False)
    LOW = Variable("LOW", obscurable=False)
    HIGH = Variable("HIGH", obscurable=False)
    true = Variable("true", obscurable=False)
    false = Variable("false", obscurable=False)

    digitalRead = Function("digitalRead", [(uint8_t,"pin")], uint8_t)
    digitalWrite = Function("digitalWrite", [(uint8_t,"pin"), (uint8_t,"value")])
    pinMode = Function("pinMode", [(uint8_t,"pin"), (uint8_t,"mode")])

    analogRead = Function("analogRead", [(uint8_t,"pin")], uint16_t)
    analogWrite = Function("analogWrite", [(uint8_t,"pin"), (uint8_t,"value")])
    analogReference = Function("analogReference", [(uint8_t,"pin")])

    random = Function("random", arguments=[], return_type=uint16_t)
    randomSeed = Function(name="randomSeed", arguments=[(uint32_t,"seed")])
    memcpy = Function(
        name="memcpy", arguments=[(uint8_t_pointer,"dest"), (uint8_t_pointer,"src"), (uint8_t,"size")]
    )
    millis = Function(return_type=uint32_t, name="millis")
    max = Function(return_type=uint32_t, name="max", arguments=[(uint32_t,"val1"), (uint32_t,"val2")])
    min = Function(return_type=uint32_t, name="min", arguments=[(uint32_t,"val1"), (uint32_t,"val2")])
    delay = Function(name="delay", arguments=[(uint32_t,"millis")])
    delayMicroseconds = Function(name="delayMicroseconds", arguments=[(uint32_t,"micros")])
    sizeof = Function(name="sizeof", arguments=[(uint32_t,"var")])
    map = Function(
        return_type=uint32_t,
        name="map",
        arguments=[(uint32_t,"value"), (uint32_t,"fromLow"), (uint32_t,"fromHigh"), (uint32_t,"toLow"), (uint32_t,"toHigh")],
    )


Arduino = ArduinoBaseClass()


class SerialClass(ArduinoClass):
    _tempvar_T = Variable("var", T)
    class_name = "Serial"
    begin = Function("begin", Variable("var", uint32_t))
    end = Function("end")
    read = Function("read", return_type=int16_t)
    peek = Function("peek", return_type=int16_t)
    flush = Function("flush")
    print = Function("print", _tempvar_T)
    print_format = Function("print", [_tempvar_T, Variable("format", uint8_t)])
    println = Function("println", _tempvar_T)
    println_format = Function("println", [_tempvar_T, Variable("format", uint8_t)])
    write = Function("write", Variable("var", uint16_t))
    write_buf = Function(
        "write", [Array("buffer", uint8_t), Variable("length", uint16_t)]
    )
    available = Function("available", return_type=int16_t)


Serial = SerialClass()


class EepromClass(ArduinoClass):
    class_name = "EEPROM"
    get = Function("get", [Variable("adress", uint16_t), Variable("target", uint32_t)])
    write = Function(
        "write", [Variable("adress", uint16_t), Variable("value", uint8_t)]
    )
    put = Function("put", [Variable("adress", uint16_t), Variable("source", uint32_t)])
    read = Function("read", [Variable("adress", uint16_t)], return_type=uint8_t)
    update = Function(
        "update", [Variable("adress", uint16_t), Variable("value", uint8_t)]
    )
    include = "<EEPROM.h>"


Eeprom = EepromClass()
