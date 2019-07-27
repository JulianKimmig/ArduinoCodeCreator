from ArduinoCodeCreator import arduino_data_types as dt
from ArduinoCodeCreator.arduino_data_types import uint16_t
from ArduinoCodeCreator.basic_types import Variable, Function, Definition


class ArduinoCodeCreator():
    def __init__(self):
        self.definitions=[]
        self.imports=[]
        self.global_variables=[]
        self.functions=[]
        self.includes = []
        self.setup=Function(return_type=dt.void,name="setup",obscurable=False)
        self.loop=Function(return_type=dt.void,name="loop",obscurable=False)

    def create_code(self,obscure=False):
        self.add(self.setup)
        self.add(self.loop)
        code=""
        for definition in self.definitions:
            code+=definition.initalize_code(obscure=obscure,intendation=0)

        for include in self.includes:
            code+=include.initalize_code(obscure=obscure,intendation=0)

        for global_variable in self.global_variables:
             code+=global_variable.initalize_code(obscure=obscure,intendation=0)

        for function in self.functions:
            code+=function.initalize_code(obscure=obscure,intendation=0)

        return code

    def add(self,arduino_object):
        if isinstance(arduino_object,Definition):
            return self.add_definition(arduino_object)
        if isinstance(arduino_object,Function):
            return self.add_function(arduino_object)
        if isinstance(arduino_object,Variable):
            return self.add_global_variable(arduino_object)
        #if isinstance(arduino_object,ArduinoInclude):
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


if __name__ == "__main__":
    acc = ArduinoCodeCreator()
    var1 = acc.add(Variable("test",dt.uint8_t,23))

    D1 = acc.add(Definition("DEF1",100))

    func1 = acc.add(Function(
        name="testfunction",
        arguments=[dt.uint8_t,Variable("a2",dt.uint8_t)],
        return_type=uint16_t,
        code=var1.set(var1 + D1),
        variables=[(dt.uint8_t,"B",1)]
    ))
    func1.add_call(
        var1.set(func1.arg1*func1.var1)
    )

    acc.setup.add_call(
        func1(var1,D1),
        var1.set((var1+D1)*10),
        var1.set(var1+(D1*10)),
        var1.set(var1+D1*10),
    )



    #var1 = 10
    #d1 = acc.add(ArduinoDefinition(100,"DEF1"))
    #var1 = acc.add(ArduinoVariable(dt.uint8_t, 100,"test"))
    #func1 = acc.add(ArduinoFunction(dt.uint8_t,[(dt.uint8_t,"argument1"),ArduinoVariable(dt.uint8_t,name="a2")],name="testfunction"))
    #print(df.if_statement(df.equal(func1.arg1,d1),
    #                      df.serial_print(df.equal(func1.arg2,d1))
    #                      )()())
    #func1.add_code(
    #    df.serial_print(func1.arg1),
    #    df.if_statement(df.equal(func1.arg1,d1),
    #                    df.if_statement(df.equal(func1.arg1,d1),
    #                                    df.serial_print(df.equal(func1.arg2,d1)))()
   #                     )()
#
 #   )

  #  acc.setup.add_code(func1.call(var1,var1))

    code = acc.create_code(
        #obscure=True
    )
    print(code)