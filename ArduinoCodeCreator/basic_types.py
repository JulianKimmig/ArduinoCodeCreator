import time

import random
import string
from functools import partial, partialmethod

from ArduinoCodeCreator import arduino_data_types as dt
from ArduinoCodeCreator.arduino_data_types import void, uint8_t


def lambda_abstract_var_name(obscure,indentation,abstract_variable):
    return "{}{};{}".format("\t"*indentation,abstract_variable.get_name(obscure,indentation),"\n" if not obscure else "")

def lambda_operation(obscure,indentation,var1,var2,operator):
    return "({}{}{})".format(var1.inline(obscure,0),operator,var2.inline(obscure,0))

class AbstractStructureType():
    def __init__(self, name=None,type=dt.void, obscurable=True):
        self._obscure_name = random.choice(string.ascii_letters) + ''.join([random.choice(string.ascii_letters + string.digits) for n in range(24)]) + str(
            time.time()).replace(".", "") if obscurable or name is None else name
        self.name = name
        self.type = type

    def get_name(self,obscure,intendation=0):
        n = self._obscure_name if obscure or self.name is None else self.name
        try:
            return n(obscure,intendation)
        except Exception as e:
            #print(traceback.format_exc())
            return n


class AbstractVariable(AbstractStructureType):
    def __init__(self, name=None, type=uint8_t, obscurable=False,settable=True):
        super().__init__(name=name,type=type, obscurable=obscurable)
        self.settable = settable

    def inline(self,obscure,intendation=0):
        return self.get_name(obscure)

    def set(self,value):
        return lambda o,i: lambda o,i:"{}+{}".format(self.inline(o,0),value.inline(o,0))

    def math_operation(self,other,operation):
        other = to_abstract_var(other)
        return AbstractVariable(partial(lambda_operation,var1=self,var2=other,operator=operation),dt.add_types(self.type,other.type),obscurable=False,settable=False)

    __add__ = partialmethod(math_operation,operation = "+")
    __mul__ = partialmethod(math_operation,operation = "*")


def to_abstract_var(value):
    if isinstance(value,AbstractVariable):
        return value
    else:
        if value is None:
            value = 'null'
        return AbstractVariable(name=str(value),obscurable=False)


class Definition(AbstractVariable):
    def __init__(self, name=None,value=0, obscurable=True):
        super().__init__(name=name, obscurable=obscurable)
        self.value = value

    def initalize_code(self,obscure,intendation=0):
        return "{}#define {} {}\n".format("\t"*intendation,self.get_name(obscure),self.value)


class Variable(AbstractVariable):
    def __init__(self, name=None, type = uint8_t,value=None, obscurable=True):
        super().__init__(name=name, type=type, obscurable=obscurable)
        self.value = value

    def initalize_code(self,obscure,intendation=0):
        code = self.as_attribute(obscure,intendation)
        if self.value is not None:
            code +="={}".format(self.value)
        code +=";"
        if not obscure:
            code +="\n"
        return code

    def initalize(self):
        return lambda o,i:self.initalize_code(o,i)

    def set(self,value=None):
        return lambda o,i:"{}{}={};{}".format("\t"*i,self.get_name(o),to_abstract_var(value).get_name(o),"\n" if not o else "")

    def as_attribute(self,obscure,intendation=0):
        return "{}{} {}".format("\t"*intendation,self.type,self.get_name(obscure))


def to_variable(arguments):
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

    print(arguments)
    print(vars)
    if len(vars) == 0:
        return None
    if len(vars) == 1:
        return vars[0]
    return vars

class AbstractFunction(AbstractStructureType):
    def __init__(self,name=None,arguments=None,return_type=void,obscurable=False):
        super().__init__(name=name,type=return_type,obscurable=obscurable)
        self.arguments=[]
        if arguments is not None:
            for variable in list([to_variable(arguments)]):
                self.add_argument(variable)

    def add_argument(self,arduino_variable):
        self.arguments.append(arduino_variable)
        setattr(self,"arg{}".format(len(self.arguments)),arduino_variable)

    def __call__(self, *args):
        assert len(args) == len(self.arguments), "function call {}: invalid argumen length ({}) and ({})".format(self.name,", ".join([str(arg) for arg in args]),", ".join([str(argument) for argument in self.arguments]))

        return AbstractVariable(
            name=lambda o,i:"{}({})".format(self.get_name(obscure=o),','.join([to_abstract_var(arg).get_name(o) for arg in args])),
            type = self.type
        )
        def to_code(obscure,intendation):
            code=""
            if not obscure:
                code+="\t"*intendation
            #print([value_to_lambda(arg)(obscure=obscure,intendation=0) for arg in args])
            code += "{}({});".format(self,",".join([re.sub(";$","",re.sub("\n$","",value_to_lambda(arg)(obscure=obscure,intendation=0)))
                                                    for arg in args]))+("" if obscure else "\n")
            return code
        return to_code

class Function(AbstractFunction):
    def __init__(self, name, arguments=None, return_type=void,code=None,variables=None,obscurable=True):
        super().__init__(name, arguments, return_type,obscurable=obscurable)
        self.inner_calls = []
        self.variables = []
        if variables is not None:
            for variable in list([to_variable(variables)]):
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
                c = partial(lambda_abstract_var_name,abstract_variable=c)
            self.inner_calls.append(c)

    def initalize_code(self,obscure,intendation=0):
        code = "{} {}({}){{".format(self.type,self.get_name(obscure),','.join([str(arg.as_attribute(obscure,intendation)) for arg in self.arguments]))
        if not obscure:
            code +="\n"
        code +="".join([c(obscure,intendation+1) for c in self.inner_calls])
        code +="}"
        if not obscure:
            code +="\n"
        return code