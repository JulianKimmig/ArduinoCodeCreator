import time

import random
import string
from functools import partial, partialmethod

from ArduinoCodeCreator import arduino_data_types as dt
from ArduinoCodeCreator.arduino_data_types import void, uint8_t


def lambda_abstract_var_name(obscure,intendation,abstract_variable):
    return "{}{};{}".format("\t"*intendation,abstract_variable.get_name(obscure=obscure,intendation=intendation),"\n" if not obscure else "")

def lambda_operation(obscure,intendation,var1,var2,operator):
    return "({}{}{})".format(var1.inline(obscure=obscure,intendation=0),operator,var2.inline(obscure=obscure,intendation=0))

class AbstractStructureType():
    def __init__(self, name=None,type=dt.void, obscurable=True):
        self._obscure_name = random.choice(string.ascii_letters) + ''.join([random.choice(string.ascii_letters + string.digits) for n in range(24)]) + str(
            time.time()).replace(".", "") if obscurable or name is None else name
        self.name = name
        self.type = type

    def get_name(self,obscure,intendation=0):
        n = self._obscure_name if obscure or self.name is None else self.name
        try:
            print("N: ", n(obscure=obscure,intendation=intendation))
            return n(obscure=obscure,intendation=intendation)
        except Exception as e:
            #import traceback
            #print(traceback.format_exc())
            return n


class AbstractVariable(AbstractStructureType):
    def __init__(self, name=None, type=uint8_t, obscurable=False,settable=True):
        super().__init__(name=name,type=type, obscurable=obscurable)
        self.settable = settable

    def inline(self,obscure,intendation=0):
        return self.get_name(obscure=obscure)

    def set_code(self,value,obscure=True,intendation=0):
        return "{}{}={};{}".format("\t"*intendation,self.inline(obscure = obscure,intendation=0),value.inline(obscure = obscure,intendation=0),"\n" if not obscure else "")

    def set(self,value):
        value = to_abstract_var(value)
        print(value.get_name(False,1))
        return partial(self.set_code,value=value)

    def math_operation(self,other,operation):
        other = to_abstract_var(other)
        return AbstractVariable(partial(lambda_operation,var1=self,var2=other,operator=operation),dt.add_types(self.type,other.type),obscurable=False,settable=False)

    def to_pointer(self):
        return AbstractVariable(
            name=lambda obscure,intendation:"*{}".format(self.get_name(obscure=obscure)),
            type = self.type
        )

    def __call__(self,obscure,indentation):
        return "{}{};{}".format("\t"*indentation,self.get_name(obscure = obscure,intendation=indentation),"\n" if not obscure else "")

    __add__ = partialmethod(math_operation,operation = "+")
    __mul__ = partialmethod(math_operation,operation = "*")


def to_abstract_var(value):
    if isinstance(value,AbstractVariable):
        return value
    else:
        if value is None:
            value = 'null'
        try:
            value(obscure=False,intendation=0)
        except:
            value = str(value)
        return AbstractVariable(name=value,obscurable=False)


class Definition(AbstractVariable):
    def __init__(self, name=None,value=0, obscurable=True):
        super().__init__(name=name, obscurable=obscurable)
        self.value = value

    def initalize_code(self,obscure,intendation=0):
        return "{}#define {} {}\n".format("\t"*intendation,self.get_name(obscure=obscure),self.value)


class Variable(AbstractVariable):
    def __init__(self, name=None, type = uint8_t,value=None, obscurable=True):
        super().__init__(name=name, type=type, obscurable=obscurable)
        self.value = value

    def initalize_code(self,obscure,intendation=0):
        code = "{}{} {}".format("\t"*intendation,self.type,self.get_name(obscure=obscure))
        if self.value is not None:
            code +="={}".format(self.value)
        code +=";"
        if not obscure:
            code +="\n"
        return code

    def initalize(self):
        return self.initalize_code

    def set(self,value=None):
        return partial(self.set_code,
                       value=to_abstract_var(value)
                       )

    def as_attribute(self,obscure,intendation=0):
        return "{}{} {}".format("\t"*intendation,self.type,self.get_name(obscure=obscure))

def to_variables(arguments):
    if arguments is None:
        return None
    try:
        iter(arguments)
    except:
        arguments = [arguments]
    vars=[]
    for arg in arguments:
        if isinstance(arg, Variable):
            vars.append(arg)
            continue
        if isinstance(arg,dt.ArduinoDataType):
            vars.append(Variable(type=arg))
            continue
        try:
            iter(arg)
            var = Variable(type=arg[0])
            try:
                var.name = arg[1]
            except:pass
            try:
                var.value = arg[2]
            except:pass
            vars.append(var)
        except: pass

    return vars

class AbstractFunction(AbstractStructureType):
    def __init__(self,name=None,arguments=None,return_type=void,obscurable=False):
        super().__init__(name=name,type=return_type,obscurable=obscurable)
        self.arguments=[]
        if arguments is not None:
            for variable in to_variables(arguments):
                print("var:" ,variable)
                self.add_argument(variable)

    def add_argument(self,arduino_variable):
        self.arguments.append(arduino_variable)
        setattr(self,"arg{}".format(len(self.arguments)),arduino_variable)

    def __call__(self, *args):
        assert len(args) == len(self.arguments), "function call {}: invalid argumen length ({}) and ({})".format(self.name,", ".join([str(arg) for arg in args]),", ".join([str(argument) for argument in self.arguments]))
        return AbstractVariable(
            name=lambda obscure,intendation:"{}({})".format(self.get_name(obscure=obscure),','.join([to_abstract_var(arg).get_name(obscure=obscure) for arg in args])),
            type = self.type
        )

class Function(AbstractFunction):
    def __init__(self, name, arguments=None, return_type=void,code=None,variables=None,obscurable=True):
        super().__init__(name, arguments, return_type,obscurable=obscurable)
        self.inner_calls = []
        self.variables = []
        if variables is not None:
            for variable in to_variables(variables):
                self.add_variable(variable)

        if code is None:
            code=[]
        if hasattr(code,'__call__'):
            self.add_call(code)
        else:
            self.add_call(*code)

    def add_variable(self,arduino_variable):
        self.variables.append(arduino_variable)
        self.add_call(
            arduino_variable.initalize()
        )
        setattr(self,"var{}".format(len(self.variables)),arduino_variable)


    def add_call(self, *call):
        for c in call:
            if isinstance(c,AbstractVariable):
                print(lambda_abstract_var_name(abstract_variable=c,obscure=False,intendation=0))
                c = partial(lambda_abstract_var_name,abstract_variable=c)
            self.inner_calls.append(c)

    def initalize_code(self,obscure,intendation=0):
        code = "{} {}({}){{".format(self.type,self.get_name(obscure=obscure),','.join([str(arg.as_attribute(obscure = obscure,intendation=intendation)) for arg in self.arguments]))
        if not obscure:
            code +="\n"
        print([c(obscure=obscure,intendation=intendation+1) for c in self.inner_calls])
        code +="".join([c(obscure=obscure,intendation=intendation+1) for c in self.inner_calls])
        code +="}"
        if not obscure:
            code +="\n"
        return code

class Array(Variable):
    def __init__(self, name=None, type=uint8_t,size=0, value=None, obscurable=True):
        super().__init__(name=name, type=type, value=value, obscurable=obscurable)
        self.size = to_abstract_var(size)

    def as_attribute(self,obscure,intendation=0):
        return super().as_attribute(obscure=obscure,intendation=intendation).replace(str(self.type),"*{}".format(self.type),1)

    def initalize_code(self,obscure,intendation=0):
        return super().initalize_code(obscure=obscure,intendation=intendation).replace(
            self.get_name(obscure=obscure,intendation=intendation),
            self[self.size].get_name(obscure=obscure,intendation=intendation),
            1)

    def get_code(self,index_object,obscure,intendation):
        return "{}[{}]".format(self.get_name(obscure=obscure,intendation=intendation),index_object.get_name(obscure=obscure,intendation=intendation))

    def __getitem__(self, index_object):
        return AbstractVariable(
            name= partial(self.get_code,index_object=to_abstract_var(index_object)),
            type = self.type
        )