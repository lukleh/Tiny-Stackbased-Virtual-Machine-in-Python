# -*- coding: utf-8  -*-
import operator

from vm.values import Value, ValueInt, ValueFloat, ValueString
from vm.exceptions import InstructionException


class Instruction():

    def __str__(self):
        return "%s" % self.__class__.__name__

    def __repr__(self):
        return self.__str__()


class InsArgument(Instruction):

    def __str__(self):
        return "%s <%s>" % (self.__class__.__name__, self.argument)

    def __init__(self, arg=None):
        if arg is None:
            raise InstructionException('instruction argument is None')
        if not isinstance(arg, Value):
            raise InstructionException('instruction argument not type Value: %s' % arg.__class__)
        if arg.is_none:
            raise InstructionException('instruction cannot have argument Value with value None')
        self.argument = arg


class InsArgString(InsArgument):

    def __init__(self, arg=None):
        super().__init__(arg)
        if not isinstance(self.argument, ValueString):
            raise InstructionException('ins with string argument, got type: %s' % self.argument.value.__class__)


class InsArgNumber(InsArgument):
    def __init__(self, arg=None):
        super().__init__(arg)
        if not isinstance(self.argument, ValueInt):
            raise InstructionException('ins with int argument, got type: %s' % self.argument.value.__class__)


class InsTypeArg(InsArgString):

    def __init__(self, arg=None):
        super().__init__(arg)
        if self.argument.value.lower() == 'int':
            self.argument = ValueInt()
        elif self.argument.value.lower() == 'float':
            self.argument = ValueFloat()
        else:
            raise InstructionException('bad variable type: %s' % self.argument.value.__class__)


class InsCompareBase(InsArgNumber):
    opr = lambda a, b, c: None

    def execute(self, vm):
        val2 = vm.stack_pop()
        val1 = vm.stack_pop()
        if self.opr(val1.value, val2.value):
            vm.pc += self.argument.value
        else:
            vm.pc += 1


class InsMathBase(Instruction):
    opr = lambda a, b, c: None

    def execute(self, vm):
        val2 = vm.stack_pop()
        val1 = vm.stack_pop()
        pval = self.opr(val1.value, val2.value)
        vm.stack_push(ValueInt(pval))
        vm.pc += 1


class InsFunc(InsArgString):
    """
    code> func <name>
    name: string

    stack: ->

    defines a name for the following code
    currently has no effect on the execution
    """


class InsArg(InsTypeArg):
    """
    code> arg <name>
    name: string
    now only supports 'int'

    stack: ->

    defines argument with a type that the code will be executed with
    adds local variable
    """


class InsVar(InsTypeArg):
    """
    code> var <name>
    name: string
    now only supports 'int'

    stack: ->

    defines local variable with a type that the code can use
    """


class InsIPush(InsArgNumber):
    """
    code> ipush <value>
    value: number

    stack: -> value

    push integer value onto the stack
    """
    def execute(self, vm):
        vm.stack_push(self.argument)
        vm.pc += 1


class InsILoad(InsArgNumber):
    """
    code> iload <index>
    index: number

    stack: value ->

    load integer value from local variable at index
    """
    def execute(self, vm):
        vm.stack_push(vm.local_vars[self.argument.value])
        vm.pc += 1


class InsIStore(InsArgNumber):
    """
    code> istore <index>
    index: number

    stack: value ->

    store integer value to local variable at index
    """
    def execute(self, vm):
        vm.local_vars[self.argument.value] = vm.stack_pop()
        vm.pc += 1


class InsGoto(InsArgNumber):
    """
    code> goto <offset>
    offset: number

    stack: ->

    move pointer by offset, can be negative
    """
    def execute(self, vm):
        vm.pc += self.argument.value


class InsIReturn(Instruction):
    """
    code> ireturn

    stack: value ->

    pops value from stack and set it as return value of the code and finishes execution
    """
    @staticmethod
    def execute(vm):
        vm.finished = True
        vm.return_value = vm.stack_pop()
        vm.pc += 1


class InsNop(Instruction):
    """
    code> nop

    stack: ->

    no effect, no operation
    """
    @staticmethod
    def execute(vm):
        vm.pc += 1


class InsPop(Instruction):
    """
    code> pop

    stack: value ->

    pops value from stack
    """
    @staticmethod
    def execute(vm):
        vm.stack_pop()
        vm.pc += 1


class InsDup(Instruction):
    """
    code> dup

    stack: value -> value, value

    duplicates value on the stack
    """
    @staticmethod
    def execute(vm):
        val = vm.stack_pop()
        vm.stack_push(val)
        vm.stack_push(val.copy())
        vm.pc += 1


class InsSwap(Instruction):
    """
    code> swap

    stack: value1, value2 -> value2, value1

    swaps values on the stack
    """
    @staticmethod
    def execute(vm):
        val1 = vm.stack_pop()
        val2 = vm.stack_pop()
        vm.stack_push(val1)
        vm.stack_push(val2)
        vm.pc += 1


class InsIIfCmpEq(InsCompareBase):
    """
    code> if_icmpeq <offset>
    offset: number

    stack: value1, value2 ->
    value1: integer
    value2: integer
    if two values are equal, move pointer by offset
    """
    opr = operator.eq


class InsIIfCmpNe(InsCompareBase):
    """
    code> if_icmpne <offset>
    offset: number

    stack: value1, value2 ->
    value1: integer
    value2: integer
    if two values are not equal, move pointer by offset
    """
    opr = operator.ne


class InsIIfCmpGe(InsCompareBase):
    """
    code> if_icmpge <offset>
    offset: number

    stack: value1, value2 ->
    value1: integer
    value2: integer
    if value1 is greater or equal to value2, move pointer by offset
    """
    opr = operator.ge


class InsIIfCmpGt(InsCompareBase):
    """
    code> if_icmpgt <offset>
    offset: number

    stack: value1, value2 ->
    value1: integer
    value2: integer
    if value1 is greater than value2, move pointer by offset
    """
    opr = operator.gt


class InsIIfCmpLe(InsCompareBase):
    """
    code> if_icmple <offset>
    offset: number

    stack: value1, value2 ->
    value1: integer
    value2: integer
    if value1 is lower or equal than value2, move pointer by offset
    """
    opr = operator.le


class InsIIfCmpLt(InsCompareBase):
    """
    code> if_icmplt <offset>
    offset: number

    stack: value1, value2 ->
    value1: integer
    value2: integer
    if value1 is lower than value2, move pointer by offset
    """
    opr = operator.lt


class InsIfNonNull(InsArgNumber):
    """
    code> ifnonnull <offset>
    offset: number

    stack: value ->
    if value is not null, move pointer by offset
    """
    def execute(self, vm):
        val = vm.stack_pop()
        if not val.is_none:
            vm.pc += self.argument.value
        else:
            vm.pc += 1


class InsIfNull(InsArgNumber):
    """
    code> ifnull <offset>
    offset: number

    stack: value ->
    if value is null, move pointer by offset
    """
    def execute(self, vm):
        val = vm.stack_pop()
        if val.is_none:
            vm.pc += self.argument.value
        else:
            vm.pc += 1


class InsIAdd(InsMathBase):
    """
    code> iadd

    stack: value1, value2 -> value3
    value1: integer
    value2: integer
    value3: integer
    value3 = value1 + value2
    """
    opr = operator.add


class InsISub(InsMathBase):
    """
    code> isub

    stack: value1, value2 -> value3
    value1: integer
    value2: integer
    value3: integer
    value3 = value1 - value2
    """
    opr = operator.sub


class InsIMul(InsMathBase):
    """
    code> imul

    stack: value1, value2 -> value3
    value1: integer
    value2: integer
    value3: integer
    value3 = value1 * value2
    """
    opr = operator.mul


class InsIDiv(InsMathBase):
    """
    code> idiv

    stack: value1, value2 -> value3
    value1: integer
    value2: integer
    value3: integer
    value3 = value1 / value2
    """
    opr = operator.floordiv


keywords = {
    'func': InsFunc,
    'arg': InsArg,
    'var': InsVar,
    'ipush': InsIPush,
    'iload': InsILoad,
    'istore': InsIStore,
    'goto': InsGoto,

    'ireturn': InsIReturn,
    'nop': InsNop,
    'pop': InsPop,
    'dup': InsDup,
    'swap': InsSwap,

    'if_icmpeq': InsIIfCmpEq,
    'if_icmpne': InsIIfCmpNe,
    'if_icmpge': InsIIfCmpGe,
    'if_icmpgt': InsIIfCmpGt,
    'if_icmple': InsIIfCmpLe,
    'if_icmplt': InsIIfCmpLt,

    'ifnonnull': InsIfNonNull,
    'ifnull': InsIfNull,

    'iadd': InsIAdd,
    'isub': InsISub,
    'imul': InsIMul,
    'idiv': InsIDiv,
    }
