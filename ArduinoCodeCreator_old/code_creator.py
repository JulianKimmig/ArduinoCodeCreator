from ArduinoCodeCreator import arduino_data_types as dt
from ArduinoCodeCreator import arduino_default_functions as df
from ArduinoCodeCreator.functions import ArduinoFunction
from ArduinoCodeCreator.variable import ArduinoDefinition, ArduinoVariable, ArduinoInclude


class ArduinoCodeCreator():
    def __init__(self):
        self.definitions=[]
        self.imports=[]
        self.global_variables=[]
        self.functions=[]
        self.includes = []
        self.setup=ArduinoFunction(dt.void,name="setup",obscurable=False)
        self.loop=ArduinoFunction(dt.void,name="loop",obscurable=False)

    def create_code(self,obscure):
        self.add(self.setup)
        self.add(self.loop)
        code=""
        for definition in self.definitions:
            code+=definition.create_code(obscure=obscure,indentation=0)

        for include in self.includes:
            code+=include.create_code(obscure=obscure,indentation=0)

        for global_variable in self.global_variables:
            code+=global_variable.create_code(obscure=obscure,indentation=0)

        for function in self.functions:
            code+=function.create_code(obscure=obscure,indentation=0)

        return code

    def add(self,arduino_object):
        if isinstance(arduino_object,ArduinoDefinition):
            return self.add_definition(arduino_object)
        if isinstance(arduino_object,ArduinoFunction):
            return self.add_function(arduino_object)
        if isinstance(arduino_object,ArduinoVariable):
            return self.add_global_variable(arduino_object)
        if isinstance(arduino_object,ArduinoInclude):
            return self.add_include(arduino_object)

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


if __name__ == "__main__":
    acc = ArduinoCodeCreator()
    d1 = acc.add(ArduinoDefinition(100,"DEF1"))
    var1 = acc.add(ArduinoVariable(dt.uint8_t, 100,"test"))
    func1 = acc.add(ArduinoFunction(dt.uint8_t,[(dt.uint8_t,"argument1"),ArduinoVariable(dt.uint8_t,name="a2")],name="testfunction"))
    print(df.if_statement(df.equal(func1.arg1,d1),
                          df.serial_print(df.equal(func1.arg2,d1))
                          )()())
    func1.add_code(
        df.serial_print(func1.arg1),
        df.if_statement(df.equal(func1.arg1,d1),
                        df.if_statement(df.equal(func1.arg1,d1),
                                        df.serial_print(df.equal(func1.arg2,d1)))()
                        )()

    )

    acc.setup.add_code(func1.call(var1,var1))

    code = acc.create_code(
        #obscure=True
    )
    print(code)