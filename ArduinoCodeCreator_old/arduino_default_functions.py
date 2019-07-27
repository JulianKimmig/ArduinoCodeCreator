from ArduinoCodeCreator import arduino_data_types as dt
from ArduinoCodeCreator.functions import ArduinoFunction, ArduinoStatement

serial_begin = ArduinoFunction(dt.void, name="Serial.begin", arguments=[dt.uint32_t], obscurable=False,
                               accept_any_type=True)

serial_print = ArduinoFunction(dt.void, name="Serial.print", arguments=[dt.uint8_t], obscurable=False,
                               accept_any_type=True)
serial_println = ArduinoFunction(dt.void, name="Serial.println", arguments=[dt.uint8_t], obscurable=False,
                                 accept_any_type=True)
serial_write = ArduinoFunction(dt.void, name="Serial.write", arguments=[dt.uint8_t, dt.uint8_t], obscurable=False,
                               accept_any_type=True)
serial_available = ArduinoFunction(dt.void, name="Serial.available", arguments=[], obscurable=False,
                               accept_any_type=True)
serial_read = ArduinoFunction(dt.int, name="Serial.read", arguments=[], obscurable=False,
                                   accept_any_type=True)



sizeof = ArduinoFunction(dt.uint16_t, name="sizeof", arguments=[dt.uint8_t], obscurable=False, accept_any_type=True)
eeprom_get = ArduinoFunction(dt.void, name="EEPROM.get", arguments=[dt.uint8_t, dt.uint8_t], obscurable=False,
                             accept_any_type=True)
eeprom_put = ArduinoFunction(dt.void, name="EEPROM.put", arguments=[dt.uint8_t, dt.uint8_t], obscurable=False,
                             accept_any_type=True)




class IfStatement(ArduinoStatement):
    def __init__(self, ):
        super().__init__("if({}){{\n{}\i}}\n")

    def __call__(self, condition, code=""):
        from ArduinoCodeCreator.variable import value_to_lambda

        inner_code = value_to_lambda(code)
        condition = condition
        return super().__call__(condition, inner_code)

class WhileStatement(IfStatement):
    def __init__(self):
        super().__init__()
        self.code = "while({}){{\n{}\i}}\n"

class ElseIfStatement(IfStatement):
    def __init__(self):
        super().__init__()
        self.code = "else if({}){{\n{}\i}}\n"

class ForStatement(ArduinoStatement):
    def __init__(self):
        super().__init__("for({}{};{}){{\n{}\i}}\n")
        from ArduinoCodeCreator.variable import ArduinoVariable
        self.i = ArduinoVariable(dt.uint8_t, 0, "i")
        self.j = ArduinoVariable(dt.uint8_t, 0, "j")
        self.k = ArduinoVariable(dt.uint8_t, 0, "k")

    def __call__(self, count_vaiable, continue_condition, raising_value=1, code=None):
        inner_code = (lambda obscure, intendation: "") if code is None else code
        raising_value_code = lambda obscure, intendation: "{}+={}".format(count_vaiable, raising_value)
        count_vaiable_code = lambda obscure, intendation: count_vaiable.create_code(obscure=obscure,
                                                                                    intendation=0).replace("\n", "")

        return super().__call__(count_vaiable_code, continue_condition, raising_value_code, inner_code)


cast = ArduinoStatement("({}){}", ignore_intendations=True)
to_pointer = ArduinoStatement("&{}", ignore_intendations=True)
return_statement = ArduinoStatement("return {};\n")
continue_statement = ArduinoStatement("return;\n")

if_statement = IfStatement()
else_statement = ArduinoStatement("else{{\n{}\i}}\n")
elseif_statement = ElseIfStatement()
for_statement = ForStatement()
while_statement = WhileStatement()
