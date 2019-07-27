import random
import re
import string
import time

from ArduinoCodeCreator import operators as op
from ArduinoCodeCreator.arduino_data_types import void


class ArduinoObject:
    def __init__(self,name=None,obscurable=True):
        self._obscure_name = random.choice(string.ascii_letters) + ''.join([random.choice(string.ascii_letters + string.digits) for n in range(24)]) + str(
            time.time()).replace(".", "")[:12] if obscurable or name is None else name
        time.sleep(0.01)
        self.name = self._obscure_name if name is None else name
        self._name_to_use = self.name

    def __str__(self):
        return self._name_to_use

    def __repr__(self):
        return self._name_to_use

    def __call__(self, obscure,intendation):
        return self._obscure_name if obscure else self.name

    def create_code(self,obscure,intendation):
        if obscure:
            self._name_to_use = self._obscure_name
        else:
            self._name_to_use = self.name

    def __add__(self, other):
        return op.add(self,other)


    def __sub__(self, other):
        return op.sub(self,other)

    def __rshift__(self, other):
        return op.bitshift_right(self,other)

    def __mul__(self, other):
        return op.mul(self,other)

    def __lshift__(self, other):
        return op.bitshift_left(self,other)

    def __lt__(self, other):
        return op.lt(self,other)

    def __gt__(self, other):
        return op.gt(self,other)

    def __mod__(self, other):
        return op.mod(self,other)

    def __getitem__(self, index):
        return op.get_index(self,index)

    def __or__(self, other):
        return op.or_bit(self,other)

    def __and__(self, other):
        return op.and_bit(self,other)
    def __ne__(self, other):
        return op.neq(self,other)

    def __eq__(self, other):
        return op.eq(self,other)

class ToCode(ArduinoObject):
    def __init__(self, call, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.call = call

    def __call__(self, obscure,intendation):
        return self.call(obscure=obscure,intendation=intendation)

class ArduinoValueObject(ArduinoObject):
    def __init__(self,value=None,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.value = value

    def create_code(self,obscure,intendation):
        super().create_code(obscure=obscure,intendation=intendation)

class ArduinoDefinition(ArduinoValueObject):
    def create_code(self,obscure,intendation):
        super().create_code(obscure=obscure,intendation=intendation)
        return "#define {} {}\n".format(self,self.value)


def value_to_lambda(value):
    if value is None:
        return lambda obscure,intendation:"null"
    try:
        value(obscure=False,intendation=0)
        return value
    except:
        return lambda obscure,intendation: str(value)

class ArduinoVariable(ArduinoValueObject):
    def __init__(self,arduino_data_type,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.arduino_data_type = arduino_data_type

    def get_data_type(self):
        return self.arduino_data_type

    def to_argument(self):
        return "{} {}".format(self.arduino_data_type,self)

    def create_code(self,obscure,intendation):
        super().create_code(obscure=obscure,intendation=intendation)
        code = ""
        if not obscure:
            code+="\t"*intendation
        code += "{} {}".format(self.arduino_data_type,self)
        if self.value is not None:
            code+="={}".format(self.value)
        code+=";"
        if not obscure:
            code+="\n"
        return code

    def set(self,value=None):
        value_func = value_to_lambda(value)

        def to_code(obscure,intendation):
            code = ""
            if not obscure:
                code+="\t"*intendation
            code+= "{}={};".format(self,re.sub(";$","",re.sub("\n$","",value_func(obscure=obscure,intendation=0))))
            if not obscure:
                code+="\n"
            return code
        return to_code

    def add_function(self, code, argumens,return_type=void, caller=None,immutable=True):
        if caller is None:
            caller = code

        from ArduinoCodeCreator.functions import ArduinoFunction
        func = ArduinoFunction(return_type,argumens,name=code,obscurable=not immutable)
        ret = lambda *args,**kwargs: lambda obscure,intendation:"{}.{}".format(self,func(*args,**kwargs))
        setattr(self,caller,ret)


class ArduinoVariableArray(ArduinoVariable):
    def __init__(self, array_size=0, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.array_size = array_size

    def create_code(self,obscure,intendation):
        try:
            array_size_= re.sub(";$","",re.sub("\n$","",self.array_size(obscure=obscure,intendation=0)))
        except TypeError as e:
            array_size_ = self.array_size
        code = super().create_code(obscure=obscure,intendation=intendation).replace(self._name_to_use,"{}[{}]".format(self._name_to_use,array_size_))
        return code

    def set(self,index,value=None):
        superfunc = super().set(value)
        index_func = value_to_lambda(index)
        to_code = lambda obscure,intendation: superfunc(obscure,intendation).replace("{}=".format(self),"{}[{}]=".format(self,index_func(obscure=obscure,intendation=0)))
        return ToCode(to_code)

    def get(self,index):
        index_func = value_to_lambda(index)
        def to_code(obscure,intendation):
            return "{}[{}]".format(self,index_func(obscure,intendation))
        return ToCode(to_code)

class ArduinoInclude(ArduinoObject):
    def __init__(self,relative=False,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.relative = relative

    def create_code(self,obscure,intendation):
        super().create_code(obscure=False,intendation=intendation)
        if self.relative:
            return "#include \"{}\"\n".format(self)
        return "#include <{}>\n".format(self)