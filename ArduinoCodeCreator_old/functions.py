import re

from ArduinoCodeCreator import arduino_data_types as dt
from ArduinoCodeCreator.arduino_data_types import void
from ArduinoCodeCreator.variable import ArduinoVariable, value_to_lambda, ToCode, ArduinoVariableArray


class ArduinoStatement():
    def __init__(self,code,ignore_intendations=False):
        self.ignore_intendations = ignore_intendations
        self.code = code

    def __call__(self,*args, **kwargs):
        def to_code(obscure,intendation):
            code=""
            selfcode=self.code
            if not obscure :
                code+="\t"*intendation
                if not self.ignore_intendations:
                    selfcode = selfcode.replace("\i","\t"*intendation)
            else:
                selfcode =  selfcode.replace("\n","")
            selfcode = selfcode.replace("\i","")
            #print(self,[arg for arg in args])
            code += selfcode.format(*[value_to_lambda(arg)(obscure,0 if self.ignore_intendations else intendation+1) for arg in args])
            return code
        return ToCode(to_code)

class ArduinoFunctionSet:
    def __init__(self,*functions):
        self.functions = functions

    def __call__(self,obscure,intendation):
        code=""
        for func in self.functions:
            code+=func(obscure=obscure,intendation=intendation)
        return code

class ArduinoFunction(ArduinoVariable):
    def __init__(self, return_type=void, arguments=None,accept_any_type=False,code=None, *args, **kwargs):
        super().__init__(arduino_data_type=return_type,*args,**kwargs)
        self.accept_any_type = accept_any_type
        if arguments is None:
            arguments = []
        self.arguments=[]
        for argument in arguments:
            if isinstance(argument,ArduinoVariable):
                self.add_argument(argument)
            elif isinstance(argument,dt.ArduinoDataType):
                self.add_argument(ArduinoVariable(argument))
            elif isinstance(argument,tuple):
                self.add_argument(ArduinoVariable(argument[0],name=argument[1],value=(argument[2] if len(argument)>2 else None)))
        if code is None:
            code = []
        self.functions=[]
        self.add_code(*code)


    def add_argument(self,arduino_variable):
        self.arguments.append(arduino_variable)
        setattr(self,"arg{}".format(len(self.arguments)),arduino_variable)

    def create_code(self,obscure,intendation):
        super().create_code(obscure=obscure,intendation=intendation)

        code = "{} {}({}){{".format(self.arduino_data_type,self,", ".join([
            arg.to_argument()
            #"{} {}".format(arg.arduino_data_type,arg(obscure=obscure,intendation=0))
            for arg in self.arguments]))
        if not obscure:
            code+="\n"
        code+=self.create_inner_code(obscure=obscure,intendation=intendation)
        code+="}"
        if not obscure:
            code+="\n"
        return code

    def create_inner_code(self,obscure,intendation):
        code = ""
        for func in self.functions:
            code +=func(obscure,intendation=intendation+1)
        return code

    def add_variable(self,*variables):
        new_variables=[]
        for variable in variables:
            if isinstance(variable,ArduinoVariable):
                new_variables.append(variable)
            elif isinstance(variable,dt.ArduinoDataType):
                new_variables.append(ArduinoVariable(variable))
            elif isinstance(variable,tuple):
                new_variables.append(ArduinoVariable(variable[0],name=variable[1],value=(variable[2] if len(variable)>2 else None)))
        for variable in new_variables:
            self.add_code(variable.create_code)
        if len(new_variables)== 0:
            return None
        if len(new_variables)== 1:
            return new_variables[0]

        return new_variables

    def add_code(self, *code):
        for c in code:
            self.functions.append(c)

    def __call__(self, *args):
        assert len(args) == len(self.arguments), "function call {}: invalid argumen length ({}) and ({})".format(self.name,", ".join([str(arg) for arg in args]),", ".join([str(argument) for argument in self.arguments]))
        def to_code(obscure,intendation):
            code=""
            if not obscure:
                code+="\t"*intendation
            #print([value_to_lambda(arg)(obscure=obscure,intendation=0) for arg in args])
            code += "{}({});".format(self,",".join([re.sub(";$","",re.sub("\n$","",value_to_lambda(arg)(obscure=obscure,intendation=0)))
                                                    for arg in args]))+("" if obscure else "\n")
            return code

        return ToCode(to_code)

    def to_argument(self):
        #void (*vgSDyAXPy3xisu6DPyyFeIQpw15639)(uint8_t* data,uint8_t s)
        return "{} (*{})({})".format(self.arduino_data_type,self,', '.join([
            arg.to_argument() for arg in self.arguments
        ]))


class ArduinoFunctionArray(ArduinoFunction,ArduinoVariableArray):
    def __init__(self,array_size=0,*args, **kwargs):
        super().__init__(*args, **kwargs)
        self.array_size = array_size

    def create_code(self,obscure,intendation):
        super().create_code(obscure=obscure,intendation=intendation)
        code = "{} (*{}[{}])({});".format(self.arduino_data_type,self,self.array_size,", ".join(["{} {}".format(arg.arduino_data_type,arg(obscure=obscure,intendation=0)) for arg in self.arguments]))
        if not obscure:
            code+="\n"
        return code

    def __call__(self, index,*args):
        supercall = super().__call__
        def to_code(obscure,intendation):
            return supercall(*args)(obscure,intendation).replace("{}(".format(self),"{}(".format(self.get(index)(obscure,0)))

        return ToCode(to_code)
