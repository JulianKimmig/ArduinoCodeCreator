from ArduinoCodeCreator import arduino_data_types as dt
from ArduinoCodeCreator.arduino import Arduino, Eeprom
from ArduinoCodeCreator.arduino_data_types import uint16_t
from ArduinoCodeCreator.basic_types import (
    Variable,
    Function,
    Definition,
    Array,
    FunctionArray,
    ArduinoClass,
)
from ArduinoCodeCreator.statements import for_


class ArduinoCodeCreator:
    def __init__(self):
        self.classes = []
        self.definitions = []
        self.imports = []
        self.global_variables = []
        self.functions = []
        self.includes = []
        self.setup = Function(return_type=dt.void, name="setup", obscurable=False)
        self.loop = Function(return_type=dt.void, name="loop", obscurable=False)

    def create_code(self, obscure=False):
        self.add(self.setup)
        self.add(self.loop)
        code = ""
        for definition in self.definitions:
            code += definition.initalize_code(obscure=obscure, indentation=0)

        for includeclass in self.classes:
            code += (
                "#include {}\n".format(includeclass.include)
                if includeclass.include is not None
                else ""
            )

        for global_variable in self.global_variables:
            code += global_variable.initalize_code(obscure=obscure, indentation=0)

        for function in self.functions:
            code += function.initalize_code(obscure=obscure, indentation=0)

        return code

    def add(self, arduino_object):
        if isinstance(arduino_object, Definition):
            return self.add_definition(arduino_object)
        if isinstance(arduino_object, Function):
            return self.add_function(arduino_object)
        if isinstance(arduino_object, Variable):
            return self.add_global_variable(arduino_object)
        if isinstance(arduino_object, ArduinoClass):
            return self.add_class(arduino_object)
        # if isinstance(arduino_object,ArduinoInclude):
        #    return self.add_include(arduino_object)

        return None

    def add_definition(self, arduino_object):
        self.definitions.append(arduino_object)
        return arduino_object

    def add_global_variable(self, arduino_object):
        self.global_variables.append(arduino_object)
        return arduino_object

    def add_function(self, arduino_object):
        self.functions.append(arduino_object)
        return arduino_object

    def add_include(self, arduino_object):
        self.includes.append(arduino_object)
        return arduino_object

    def add_class(self, arduino_object):
        self.classes.append(arduino_object)
        return arduino_object


if __name__ == "__main__":
    acc = ArduinoCodeCreator()
    var1 = acc.add(Variable("test", dt.uint32_t, 23))

    D1 = acc.add(Definition("DEF1", 100))
    array1 = acc.add(Array("array", dt.uint32_t, size=D1))
    array2 = acc.add(Array("array", dt.uint16_t, size=2))
    farray = acc.add(
        FunctionArray(
            "functionarray",
            arguments=[
                Array("data", dt.uint8_t, 0),
                Variable(type=dt.uint8_t, name="s"),
            ],
            return_type=dt.void,
            size=2,
        )
    )
    acc.add(Eeprom)
    func1 = acc.add(
        Function(
            name="testfunction",
            arguments=[array1, Variable("a2", dt.uint8_t)],
            return_type=uint16_t,
            code=var1.set(var1 + D1),
            variables=[(dt.uint8_t, "B", 1)],
        )
    )
    #   print(func1.arg1,func1.arg2)
    func1.add_call(
        var1.set(func1.arg2 * func1.var1),
        func1.arg1[var1].set(10),
        func1.arg1[2].set(var1 % 3),
        ((var1 | (D1 & var1)) ^ D1 + ~var1) >> 3,
    )

    acc.setup.add_call(
        func1(var1, D1),
        var1.set((var1 + D1) * 10),
        var1.set(var1 + (D1 * 10)),
        var1.set(var1 + D1 * 10),
        Arduino.memcpy(var1.to_pointer(), var1.to_pointer(), var1.type.byte_size),
    )

    acc.loop.add_call(
        for_(
            for_.i,
            for_.i < var1,
            -1,
            code=(var1.set(var1 / 2), farray[2].set(-farray[2])),
        )
    )

    code = acc.create_code(
        # obscure=True
    )
    print(code)
