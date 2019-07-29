import time

import random
import re
import string
from functools import partial, partialmethod

from ArduinoCodeCreator import arduino_data_types as dt
from ArduinoCodeCreator.arduino_data_types import void, uint8_t


def lambda_abstract_var_name(obscure,indentation,abstract_variable):
    return "{}{};{}".format("\t"*indentation,abstract_variable.get_name(obscure=obscure,indentation=indentation),"\n" if not obscure else "")

def lambda_operation(obscure,indentation,var1,var2,operator):
    return "({}{}{})".format(var1 if isinstance(var1,str) else var1.inline(obscure=obscure,indentation=0),operator,var2 if isinstance(var2,str) else var2.inline(obscure=obscure,indentation=0))

def lambda_remove_tabs_newline(obscure,indentation,func,remove_endtabs=True):
    s = func(obscure=obscure,indentation=indentation).replace("\t","").replace("\n","")
    if remove_endtabs:
        s=re.sub(";$","",s)
    return s

class AbstractStructureType():
    def __init__(self, name=None,type=dt.void, obscurable=True):
        self._obscure_name = random.choice(string.ascii_letters) + ''.join([random.choice(string.ascii_letters + string.digits) for n in range(24)]) + str(
            time.time()).replace(".", "") if obscurable or name is None else name
        self.name = name if name is not None else self._obscure_name
        self.type = type
        self.obscurable = obscurable


    def get_name(self,obscure,indentation=0):
        n = self._obscure_name if obscure and self.obscurable else self.name
        try:
            return n(obscure=obscure,indentation=indentation)
        except Exception as e:
            #import traceback
            #print(traceback.format_exc())
            return n

    def __str__(self):
        return self.get_name(obscure=False,indentation=0)

class AbstractVariable(AbstractStructureType):
    def __init__(self, name=None, type=uint8_t, obscurable=False,settable=True):
        super().__init__(name=name,type=type, obscurable=obscurable)
        self.settable = settable

    def inline(self,obscure,indentation=0):
        return self.get_name(obscure=obscure)

    def set_code(self,value,obscure=True,indentation=0):
        return "{}{}={};{}".format("\t"*indentation,self.inline(obscure = obscure,indentation=0),value.inline(obscure = obscure,indentation=0),"\n" if not obscure else "")

    def set(self,value):
        value = to_abstract_var(value)
        return partial(self.set_code,value=value)

    def math_operation(self,other,operation):
        other = to_abstract_var(other)
        return AbstractVariable(partial(lambda_operation,var1=self,var2=other,operator=operation),dt.add_types(self.type,other.type),obscurable=False,settable=False)

    def variable_modifier(self,operation):
        return AbstractVariable(partial(lambda_operation,var1="",var2=self,operator=operation),self.type,obscurable=False,settable=False)

    def to_pointer(self):
        return AbstractVariable(
            name=lambda obscure,indentation:"&{}".format(self.get_name(obscure=obscure)),
            type = self.type
        ).cast("(uint8_t*)")

    def cast(self,datatype):
        return AbstractVariable(
            name=lambda obscure,indentation:"(({}){})".format(datatype,self.get_name(obscure=obscure)),
            type = datatype
        )

    def __call__(self,obscure,indentation):
        return "{}{};{}".format("\t"*indentation,self.get_name(obscure = obscure,indentation=indentation),"\n" if not obscure else "")

    __add__ = partialmethod(math_operation,operation = "+")
    __sub__ = partialmethod(math_operation,operation = "-")
    __mul__ = partialmethod(math_operation,operation = "*")
    __truediv__ = partialmethod(math_operation,operation = "/")
    __mod__  = partialmethod(math_operation,operation = "%")
    __lt__ = partialmethod(math_operation,operation = "<")
    __le__ = partialmethod(math_operation,operation = "<=")
    __gt__ = partialmethod(math_operation,operation = ">")
    __ge__ = partialmethod(math_operation,operation = ">=")
    __eq__ = partialmethod(math_operation,operation = "==")
    __ne__ = partialmethod(math_operation,operation = "!=")
    __rshift__ = partialmethod(math_operation,operation = ">>")
    __lshift__ = partialmethod(math_operation,operation = ">>")
    __or__ =  partialmethod(math_operation,operation = "|")
    __and__ =  partialmethod(math_operation,operation = "&")
    __xor__= partialmethod(math_operation,operation = "^")

    __neg__ = partialmethod(variable_modifier,operation = "-")
    __invert__ = partialmethod(variable_modifier,operation = "~")
    #def __invert__(self):
    #    return AbstractVariable(lambda obscure,indentation:"~{}".format(self.inline(obscure=obscure,indentation=0)),self.type,obscurable=False,settable=False)

def to_abstract_var(value):
    if isinstance(value,AbstractVariable):
        return value
    else:
        if value is None:
            value = 'null'
        try:
            value(obscure=False,indentation=0)
        except:
            value = str(value)
        return AbstractVariable(name=value,obscurable=False)


class Definition(AbstractVariable):
    def __init__(self, name=None,value=0, obscurable=True):
        super().__init__(name=name, obscurable=obscurable)
        self.value = value

    def initalize_code(self,obscure,indentation=0):
        return "{}#define {} {}\n".format("\t"*indentation,self.get_name(obscure=obscure),self.value)



class Variable(AbstractVariable):
    def __init__(self, name=None, type = uint8_t,value=None, obscurable=True):
        super().__init__(name=name, type=type, obscurable=obscurable)
        self.value = value

    def initalize_code(self,obscure,indentation=0):
        code = "{}{} {}".format("\t"*indentation,self.type,self.get_name(obscure=obscure))
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

    def as_attribute(self,obscure):
        return "{} {}".format(self.type,self.get_name(obscure=obscure))

def to_variables(arguments):
    if arguments is None:
        return None
    try:
        iter(arguments)
    except:
        arguments = [arguments]
    vars=[]
    for arg in arguments:
        if isinstance(arg, AbstractVariable):
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

class AbstractFunction(AbstractVariable):
    def __init__(self,name=None,arguments=None,return_type=void,obscurable=False):
        super().__init__(name=name,type=return_type,obscurable=obscurable)
        self.arguments=[]
        if arguments is not None:
            for variable in to_variables(arguments):
                self.add_argument(variable)

    def add_argument(self,arduino_variable):
        self.arguments.append(arduino_variable)
        setattr(self,"arg{}".format(len(self.arguments)),arduino_variable)

    def __call__(self, *args):
        assert len(args) == len(self.arguments), "function call '{}' invalid argumen length ({}) and ({})".format(self.name,", ".join([str(arg) for arg in args]),", ".join([str(argument) for argument in self.arguments]))
        return AbstractVariable(
            name=lambda obscure,indentation:"{}({})".format(self.get_name(obscure=obscure),','.join([to_abstract_var(arg).get_name(obscure=obscure) for arg in args])),
            type = self.type
        )

    def as_attribute(self,obscure):
        #void (*func)(uint8_t* data, uint8_t s)
        return "{} (*{})({})".format(self.type,self.get_name(obscure=obscure),','.join([str(arg.as_attribute(obscure = obscure)) for arg in self.arguments]))

class Function(AbstractFunction):
    def __init__(self, name=None, arguments=None, return_type=void,code=None,variables=None,obscurable=True):
        super().__init__(name=name, arguments=arguments, return_type=return_type,obscurable=obscurable)
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
        return arduino_variable


    def add_call(self, *call):
        for c in call:
            if isinstance(c,AbstractVariable):
                c = partial(lambda_abstract_var_name,abstract_variable=c)
            self.inner_calls.append(c)

    def inner_code(self,obscure,indentation=0):
        return "".join([c(obscure=obscure,indentation=indentation) for c in self.inner_calls])

    def initalize_code(self,obscure,indentation=0):
        code = "{} {}({}){{".format(self.type,self.get_name(obscure=obscure),','.join([str(arg.as_attribute(obscure = obscure)) for arg in self.arguments]))
        if not obscure:
            code +="\n"
        code +=self.inner_code(obscure=obscure,indentation=indentation+1)
        code +="}"
        if not obscure:
            code +="\n"
        return code

class Array(Variable):
    def __init__(self, name=None, type=uint8_t,size=0, value=None, obscurable=True):
        super().__init__(name=name, type=type, value=value, obscurable=obscurable)
        self.size = to_abstract_var(size)

    def as_attribute(self,obscure):
        return super().as_attribute(obscure=obscure).replace(str(self.type),"{}*".format(self.type),1)

    def initalize_code(self,obscure,indentation=0):
        return super().initalize_code(obscure=obscure,indentation=indentation).replace(
            self.get_name(obscure=obscure,indentation=indentation),
            self[self.size].get_name(obscure=obscure,indentation=indentation),
            1)

    def get_code(self,index_object,obscure,indentation):
        return "{}[{}]".format(self.get_name(obscure=obscure,indentation=indentation),index_object.get_name(obscure=obscure,indentation=indentation))

    def __getitem__(self, index_object):
        return AbstractVariable(
            name= partial(self.get_code,index_object=to_abstract_var(index_object)),
            type = self.type
        )

class FunctionArray(Array):
    def __init__(self, name=None, return_type=uint8_t,arguments=None, size=0, value=None, obscurable=True):
        super().__init__(name=name, type=return_type, size=size, value=value, obscurable=obscurable)
        self.arguments = arguments

    def initalize_code(self,obscure,indentation=0):
        code = "{}{};{}".format(
            "\t"*indentation,
            self[self.size.get_name(obscure=obscure,indentation=0)].as_attribute(obscure=obscure),
            "\n" if not obscure else "")
        return code

    def __getitem__(self, item):
        return AbstractFunction(
            name= partial(self.get_code,index_object=to_abstract_var(item)),
            arguments=self.arguments,
            return_type=self.type,
            obscurable=False
        )


class ArduinoClass():
    def __init__(self,*attributes,name=None,include=None):
        if name is not None:
            self.class_name = name
        if not hasattr(self,"class_name"):
            self.class_name = None

        for a in attributes:
            setattr(self,a.name,a)
        for attr_name, attribute in {**self.__class__.__dict__,**self.__dict__}.items():
            if isinstance(attribute,AbstractFunction):
                attribute.obscurable=False
                if self.class_name is not None:
                    attribute.name="{}.{}".format(self.class_name,attribute.name)

        self.include = include


class ArduinoStatement():
    def __init__(self,code,ignore_indentations=False):
        self.ignore_indentations = ignore_indentations
        self.code = code

    def to_code(self,args,obscure=True,indentation=0):
        code=""
        selfcode=self.code
        if not obscure :
            code+="\t"*indentation
            if not self.ignore_indentations:
                selfcode = selfcode.replace("\i","\t"*indentation)
        else:
            selfcode =  selfcode.replace("\n","")
        selfcode = selfcode.replace("\i","")
        code += selfcode.format(*[arg(obscure=obscure,indentation=0 if self.ignore_indentations else indentation+1) for arg in args],*["" for i in range(20)])
        return code

    def __call__(self,*args, **kwargs):
        arguments = []
        for arg in args:
            try:
                arg(obscure=False,indentation=0)
                arguments.append(arg)
            except:
                arguments.append(to_abstract_var(arg))

        return partial(self.to_code,args=arguments)

class OneLineStatement(ArduinoStatement):

    def __call__(self,*args, **kwargs):
        arguments = []
        for arg in args:
            try:
                arg(obscure=False,indentation=0)
                arguments.append(arg.inline)
            except:
                arguments.append(to_abstract_var(arg).inline)

        return partial(self.to_code,args=arguments)