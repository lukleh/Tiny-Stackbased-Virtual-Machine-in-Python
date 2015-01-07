# -*- coding: utf-8  -*-
import operator
from collections import OrderedDict

from . import opcodes
from .value_containers import ValueInt, ValueFloat, ValueIntArrayRef, ValueFloatArrayRef
from .exceptions import InstructionException, ValueException


class Instruction():
    opcode = None

    def __str__(self):
        return "%s" % self.__class__.__name__

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.opcode == other.opcode


class InsNoArgument(Instruction):
    pass


class InsReturn(InsNoArgument):
    pass


class InsArgument(Instruction):

    def __str__(self):
        return "%s <%s>" % (self.__class__.__name__, self.argument)

    def __init__(self, arg=None):
        self.argument = arg
        if arg is None:
            raise InstructionException('instruction %s needs argument' % self)

    def __eq__(self, other):
        return super().__eq__(other) and self.argument == other.argument


class InsArgNumber(InsArgument):
    pass


class InsArgInteger(InsArgNumber):
    pass


class InsArgFloat(InsArgNumber):
    pass


class InsArgILabel(InsArgInteger):
    pass


class InsJump(InsArgILabel):
    pass


class InsBranch(InsArgILabel):
    pass


class InsCompareBase(InsBranch):
    opr = lambda a, b, c: None

    def execute(self, vm):
        val2 = vm.stack_pop()
        val1 = vm.stack_pop()
        if self.opr(val1.value, val2.value):
            vm.pc = self.argument.value
        else:
            vm.pc += 1


class InsICompareBase(InsCompareBase):
    pass


class InsFCompareBase(InsCompareBase):
    pass


class InsMathBase(InsNoArgument):
    opr = lambda a, b, cs: None

    def execute(self, vm):
        val2 = vm.stack_pop()
        val1 = vm.stack_pop()
        pval = self.opr(val1, val2)
        vm.stack_push(pval)
        vm.pc += 1


class InsIMathBase(InsMathBase):
    pass


class InsFMathBase(InsMathBase):
    pass


class InsArrayLoad(InsNoArgument):

    def execute(self, vm):
        index = vm.stack_pop().value
        arr = vm.stack_pop()
        vm.stack_push(arr[index])
        vm.pc += 1


class InsArrayStore(InsNoArgument):

    def execute(self, vm):
        value = vm.stack_pop()
        index = vm.stack_pop().value
        arr = vm.stack_pop()
        arr[index] = value
        vm.pc += 1


###########################################################
#
#  INSTRUCTIONS
#
###########################################################


class InsIPush(InsArgInteger):

    """
    push integer value onto the stack
    """
    opcode = opcodes.IPUSH

    def execute(self, vm):
        vm.stack_push(self.argument)
        vm.pc += 1


class InsFPush(InsArgFloat):

    """
    push float value onto the stack
    """
    opcode = opcodes.FPUSH

    def execute(self, vm):
        vm.stack_push(self.argument)
        vm.pc += 1


class InsILoad(InsArgILabel):

    """
    load integer value from local variable at index
    """
    opcode = opcodes.ILOAD

    def execute(self, vm):
        vm.stack_push(vm.variables[self.argument.value])
        vm.pc += 1


class InsFLoad(InsArgILabel):

    """
    load float value from local variable at index
    """
    opcode = opcodes.FLOAD

    def execute(self, vm):
        vm.stack_push(vm.variables[self.argument.value])
        vm.pc += 1


class InsIStore(InsArgILabel):

    """
    store integer value to local variable at index
    """
    opcode = opcodes.ISTORE

    def execute(self, vm):
        vm.variables[self.argument.value] = vm.stack_pop()
        vm.pc += 1


class InsFStore(InsArgILabel):

    """
    store float value to local variable at index
    """
    opcode = opcodes.FSTORE

    def execute(self, vm):
        vm.variables[self.argument.value] = vm.stack_pop()
        vm.pc += 1


class InsGoto(InsJump):

    """
    move pointer to position
    """
    opcode = opcodes.GOTO

    def execute(self, vm):
        vm.pc = self.argument.value


class InsIReturn(InsReturn):

    """
    pops value from stack and set it as return value of the code and finishes execution
    """
    opcode = opcodes.IRETURN

    def execute(self, vm):
        vm.finished = True
        vm.return_value = vm.stack_pop()


class InsFReturn(InsReturn):

    """
    pops value from stack and set it as return value of the code and finishes execution
    """
    opcode = opcodes.FRETURN

    def execute(self, vm):
        vm.finished = True
        vm.return_value = vm.stack_pop()


class InsNop(InsNoArgument):

    """
    no effect, no operation
    """
    opcode = opcodes.NOP

    def execute(self, vm):
        vm.pc += 1


class InsPop(InsNoArgument):

    """
    pops value from stack and discards it
    """
    opcode = opcodes.POP

    def execute(self, vm):
        vm.stack_pop()
        vm.pc += 1


class InsDup(InsNoArgument):

    """
    duplicates value on the stack
    """
    opcode = opcodes.DUP

    def execute(self, vm):
        val = vm.stack_pop()
        vm.stack_push(val)
        vm.stack_push(val.copy())
        vm.pc += 1


class InsSwap(InsNoArgument):

    """
    swaps values on the stack
    """
    opcode = opcodes.SWAP

    def execute(self, vm):
        val1 = vm.stack_pop()
        val2 = vm.stack_pop()
        vm.stack_push(val1)
        vm.stack_push(val2)
        vm.pc += 1


class InsIfICmpEq(InsICompareBase):

    """
    if two values are equal, move pointer to <var>
    """
    opcode = opcodes.IF_ICMPEQ
    opr = operator.eq


class InsIfICmpNe(InsICompareBase):

    """
    if two values are not equal, move pointer to <var>
    """
    opcode = opcodes.IF_ICMPNE
    opr = operator.ne


class InsIfICmpGe(InsICompareBase):

    """
    if value1 is greater or equal to value2, move pointer to <var>
    """
    opcode = opcodes.IF_ICMPGE
    opr = operator.ge


class InsIfICmpGt(InsICompareBase):

    """
    if value1 is greater than value2, move pointer to <var>
    """
    opcode = opcodes.IF_ICMPGT
    opr = operator.gt


class InsIfICmpLe(InsICompareBase):

    """
    if value1 is lower or equal than value2, move pointer to <var>
    """
    opcode = opcodes.IF_ICMPLE
    opr = operator.le


class InsIfICmpLt(InsICompareBase):

    """
    if value1 is lower than value2, move pointer to <var>
    """
    opcode = opcodes.IF_ICMPLT
    opr = operator.lt


class InsIfFCmpEq(InsFCompareBase):

    """
    if two values are equal, move pointer to <var>
    """
    opcode = opcodes.IF_FCMPEQ
    opr = operator.eq


class InsIfFCmpNe(InsFCompareBase):

    """
    if two values are not equal, move pointer to <var>
    """
    opcode = opcodes.IF_FCMPNE
    opr = operator.ne


class InsIfFCmpGe(InsFCompareBase):

    """
    if value1 is greater or equal to value2, move pointer to <var>
    """
    opcode = opcodes.IF_FCMPGE
    opr = operator.ge


class InsIfFCmpGt(InsFCompareBase):

    """
    if value1 is greater than value2, move pointer to <var>
    """
    opcode = opcodes.IF_FCMPGT
    opr = operator.gt


class InsIfFCmpLe(InsFCompareBase):

    """
    if value1 is lower or equal than value2, move pointer to <var>
    """
    opcode = opcodes.IF_FCMPLE
    opr = operator.le


class InsIfFCmpLt(InsFCompareBase):

    """
    if value1 is lower than value2, move pointer to <var>
    """
    opcode = opcodes.IF_FCMPLT
    opr = operator.lt


class InsIfNonNull(InsBranch):

    """
    if value is not null, move pointer to <var>
    """
    opcode = opcodes.IFNONNULL

    def execute(self, vm):
        val = vm.stack_pop()
        if not val.is_none:
            vm.pc = self.argument.value
        else:
            vm.pc += 1


class InsIfNull(InsBranch):

    """
    if value is null, move pointer to <var>
    """
    opcode = opcodes.IFNULL

    def execute(self, vm):
        val = vm.stack_pop()
        if val.is_none:
            vm.pc = self.argument.value
        else:
            vm.pc += 1


class InsIAdd(InsIMathBase):

    """
    add two integers, push result to stack
    """
    opcode = opcodes.IADD
    opr = operator.add


class InsISub(InsIMathBase):

    """
    subsctract two integers, push result to stack
    """
    opcode = opcodes.ISUB
    opr = operator.sub


class InsIMul(InsIMathBase):

    """
    multiply two integers, push result to stack
    """
    opcode = opcodes.IMUL
    opr = operator.mul


class InsIDiv(InsIMathBase):

    """
    divide two integers, push result to stack
    """
    opcode = opcodes.IDIV
    opr = operator.floordiv


class InsFAdd(InsFMathBase):

    """
    add two floats, push result to stack
    """
    opcode = opcodes.FADD
    opr = operator.add


class InsFSub(InsFMathBase):

    """
    subsctract two floats, push result to stack
    """
    opcode = opcodes.FSUB
    opr = operator.sub


class InsFMul(InsFMathBase):

    """
    multiply two floats, push result to stack
    """
    opcode = opcodes.FMUL
    opr = operator.mul


class InsFDiv(InsFMathBase):

    """
    divide two floats, push result to stack
    """
    opcode = opcodes.FDIV
    opr = operator.truediv


class InsFloat2Int(InsNoArgument):

    """
    converts float to int
    """
    opcode = opcodes.F2I

    def execute(self, vm):
        val1 = vm.stack_pop()
        pval = int(val1.value)
        vm.stack_push(ValueInt(pval))
        vm.pc += 1


class InsInt2Float(InsNoArgument):

    """
    converts int to float
    """
    opcode = opcodes.I2F

    def execute(self, vm):
        val1 = vm.stack_pop()
        pval = float(val1.value)
        vm.stack_push(ValueFloat(pval))
        vm.pc += 1


class InsNewArray(InsArgInteger):

    """
    makes an array of size value1 with type <var>
    """
    opcode = opcodes.NEWARRAY

    def __init__(self, arg=None):
        super().__init__(arg)
        if self.argument.value == 0:
            self.array_type = ValueIntArrayRef
        elif self.argument.value == 1:
            self.array_type = ValueFloatArrayRef
        else:
            raise InstructionException('newarray can accept only type 0 or 1, received %s' % self.argument.value)

    def execute(self, vm):
        size = vm.stack_pop().value
        arr = self.array_type()
        arr.allocate(asize=size)
        vm.stack_push(arr)
        vm.pc += 1


class InsALoad(InsArgILabel):

    """
    load array reference from local variable <var>
    """
    opcode = opcodes.ALOAD

    def execute(self, vm):
        vm.stack_push(vm.variables[self.argument.value])
        vm.pc += 1


class InsAStore(InsArgILabel):

    """
    store array reference to local variable <var>
    """
    opcode = opcodes.ASTORE

    def execute(self, vm):
        vm.variables[self.argument.value] = vm.stack_pop()
        vm.pc += 1


class InsIALoad(InsArrayLoad):

    """
    load an int from an array
    """
    opcode = opcodes.IALOAD


class InsFALoad(InsArrayLoad):

    """
    load an float from an array
    """
    opcode = opcodes.FALOAD


class InsArrayLength(InsNoArgument):

    """
    returns length of an array
    """
    opcode = opcodes.ARRAYLENGTH

    def execute(self, vm):
        arr = vm.stack_pop()
        vm.stack_push(ValueInt(arr.length))
        vm.pc += 1


class InsIAStore(InsArrayStore):

    """
    store an int to array index
    """
    opcode = opcodes.IASTORE


class InsFAStore(InsArrayStore):

    """
    store an float to array index
    """
    opcode = opcodes.FASTORE


class InsAReturn(InsReturn):

    """
    pops value from stack and set it as return value of the code and finishes execution
    """
    opcode = opcodes.ARETURN

    def execute(self, vm):
        vm.finished = True
        vm.return_value = vm.stack_pop()


keywords = OrderedDict([
    ('ipush', InsIPush),
    ('fpush', InsFPush),
    ('iload', InsILoad),
    ('fload', InsFLoad),
    ('istore', InsIStore),
    ('fstore', InsFStore),
    ('goto', InsGoto),

    ('ireturn', InsIReturn),
    ('freturn', InsFReturn),
    ('nop', InsNop),
    ('pop', InsPop),
    ('dup', InsDup),
    ('swap', InsSwap),

    ('if_icmpeq', InsIfICmpEq),
    ('if_icmpne', InsIfICmpNe),
    ('if_icmpge', InsIfICmpGe),
    ('if_icmpgt', InsIfICmpGt),
    ('if_icmple', InsIfICmpLe),
    ('if_icmplt', InsIfICmpLt),

    ('if_fcmpeq', InsIfFCmpEq),
    ('if_fcmpne', InsIfFCmpNe),
    ('if_fcmpge', InsIfFCmpGe),
    ('if_fcmpgt', InsIfFCmpGt),
    ('if_fcmple', InsIfFCmpLe),
    ('if_fcmplt', InsIfFCmpLt),

    ('ifnonnull', InsIfNonNull),
    ('ifnull', InsIfNull),

    ('iadd', InsIAdd),
    ('isub', InsISub),
    ('imul', InsIMul),
    ('idiv', InsIDiv),
    ('fadd', InsFAdd),
    ('fsub', InsFSub),
    ('fmul', InsFMul),
    ('fdiv', InsFDiv),

    ('f2i', InsFloat2Int),
    ('i2f', InsInt2Float),

    ('newarray', InsNewArray),
    ('aload', InsALoad),
    ('astore', InsAStore),
    ('iaload', InsIALoad),
    ('faload', InsFALoad),
    ('iastore', InsIAStore),
    ('fastore', InsFAStore),
    ('arraylength', InsArrayLength),
    ('areturn', InsAReturn)
])


def contain_value(inst, value):
    if issubclass(inst, InsArgInteger):
        return ValueInt(value)
    elif issubclass(inst, InsArgFloat):
        return ValueFloat(value)
    else:
        raise ValueException('instruction %s cannot contain value int or float' % inst)
