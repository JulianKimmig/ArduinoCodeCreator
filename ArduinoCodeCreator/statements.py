from functools import partial

from ArduinoCodeCreator.arduino_data_types import uint8_t
from ArduinoCodeCreator.basic_types import ArduinoStatement, Variable, lambda_remove_tabs_newline, Function


class ForStatement(ArduinoStatement):
    def __init__(self):
        super().__init__("for({}{};{}){{\n{}\i}}\n")
        self.i = Variable(type=uint8_t, value=0, name="i")
        self.j = Variable(type=uint8_t, value=0, name="j")
        self.k = Variable(type=uint8_t, value=0, name="k")

    def __call__(self, count_vaiable, continue_condition, raising_value=1, code=None):
        count_vaiable_code = partial(lambda_remove_tabs_newline,func=count_vaiable.initalize_code)
        continue_condition = continue_condition.inline
        try:
            1+raising_value
            if(raising_value<0):
                raising_value=count_vaiable.set(count_vaiable-abs(raising_value))
            else:
                raising_value=count_vaiable.set(count_vaiable+raising_value)
        except:
            pass
        raising_value_code = partial(lambda_remove_tabs_newline,func=raising_value)
        inner_code = Function(code=code).inner_code
        #(lambda obscure, intendation: "") if code is None else code

        return super().__call__(count_vaiable_code, continue_condition, raising_value_code, inner_code)

for_=ForStatement()