import re

class ArduinoOperator():
    def __init__(self,operator):
        self.operator = operator

    def __call__(self,arg1,arg2):
        from ArduinoCodeCreator.variable import ToCode
        def to_code(obscure,indentation):
            op1 = arg1
            op2 = arg2
            try:
                op1=re.sub(";$","",re.sub("\n$","",op1(obscure=obscure,indentation=0)))
            except TypeError :
                pass
            try:
                op2=re.sub(";$","",re.sub("\n$","",op2(obscure=obscure,indentation=0)))
            except TypeError:
                pass
            code =  "({} {} {})".format(op1,self.operator,op2)
            return code

        return ToCode(to_code)

class GetIndex():
    def __call__(self,array,index):
        from ArduinoCodeCreator.variable import ToCode
        def to_code(obscure,indentation):
            code = "({}[{}])".format(array(obscure=obscure,indentation=0),index)
            return code
        return ToCode(to_code)

get_index = GetIndex()

equal = ArduinoOperator("==")
gt = ArduinoOperator(">")
lt = ArduinoOperator("<")
get = ArduinoOperator(">=")
let = ArduinoOperator("<=")
not_equal = ArduinoOperator("!=")
and_logical = ArduinoOperator("&&")
or_logical = ArduinoOperator("||")

neq = not_equal
eq = equal

add = ArduinoOperator("+")
sub = ArduinoOperator("-")
mul = ArduinoOperator("*")
mod = ArduinoOperator("%")

and_bit = ArduinoOperator("&")
or_bit = ArduinoOperator("|")
xor_bit = ArduinoOperator("^")
not_bit = ArduinoOperator("~")
bitshift_left = ArduinoOperator("<<")
bitshift_right = ArduinoOperator(">>")

