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

    def execute(self, frame):
        val2 = frame.stack.pop()
        val1 = frame.stack.pop()
        if self.opr(val1.value, val2.value):
            frame.pc = self.argument.value - 1


class InsICompareBase(InsCompareBase):
    pass


class InsFCompareBase(InsCompareBase):
    pass


class InsMathBase(InsNoArgument):
    opr = lambda a, b, cs: None

    def execute(self, frame):
        val2 = frame.stack.pop()
        val1 = frame.stack.pop()
        pval = self.opr(val1, val2)
        frame.stack.append(pval)


class InsIMathBase(InsMathBase):
    pass


class InsFMathBase(InsMathBase):
    pass


class InsArrayLoad(InsNoArgument):

    def execute(self, frame):
        index = frame.stack.pop().value
        arr = frame.stack.pop()
        frame.stack.append(arr[index])


class InsArrayStore(InsNoArgument):

    def execute(self, frame):
        value = frame.stack.pop()
        index = frame.stack.pop().value
        arr = frame.stack.pop()
        arr[index] = value


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

    def execute(self, frame):
        frame.stack.append(self.argument)


class InsFPush(InsArgFloat):

    """
    push float value onto the stack
    """
    opcode = opcodes.FPUSH

    def execute(self, frame):
        frame.stack.append(self.argument)


class InsILoad(InsArgILabel):

    """
    load integer value from local variable at index
    """
    opcode = opcodes.ILOAD

    def execute(self, frame):
        frame.stack.append(frame.variables[self.argument.value])


class InsFLoad(InsArgILabel):

    """
    load float value from local variable at index
    """
    opcode = opcodes.FLOAD

    def execute(self, frame):
        frame.stack.append(frame.variables[self.argument.value])


class InsIStore(InsArgILabel):

    """
    store integer value to local variable at index
    """
    opcode = opcodes.ISTORE

    def execute(self, frame):
        frame.variables[self.argument.value] = frame.stack.pop()


class InsFStore(InsArgILabel):

    """
    store float value to local variable at index
    """
    opcode = opcodes.FSTORE

    def execute(self, frame):
        frame.variables[self.argument.value] = frame.stack.pop()


class InsGoto(InsJump):

    """
    move pointer to position
    """
    opcode = opcodes.GOTO

    def execute(self, frame):
        frame.pc = self.argument.value - 1


class InsIReturn(InsReturn):

    """
    pops value from stack and set it as return value of the code and finishes execution
    """
    opcode = opcodes.IRETURN

    def execute(self, frame):
        frame.finished = True
        frame.return_value = frame.stack.pop()


class InsFReturn(InsReturn):

    """
    pops value from stack and set it as return value of the code and finishes execution
    """
    opcode = opcodes.FRETURN

    def execute(self, frame):
        frame.finished = True
        frame.return_value = frame.stack.pop()


class InsNop(InsNoArgument):

    """
    no effect, no operation
    """
    opcode = opcodes.NOP

    def execute(self, frame):
        pass


class InsPop(InsNoArgument):

    """
    pops value from stack and discards it
    """
    opcode = opcodes.POP

    def execute(self, frame):
        frame.stack.pop()


class InsDup(InsNoArgument):

    """
    duplicates value on the stack
    """
    opcode = opcodes.DUP

    def execute(self, frame):
        val = frame.stack.pop()
        frame.stack.append(val)
        frame.stack.append(val.copy())


class InsSwap(InsNoArgument):

    """
    swaps values on the stack
    """
    opcode = opcodes.SWAP

    def execute(self, frame):
        val1 = frame.stack.pop()
        val2 = frame.stack.pop()
        frame.stack.append(val1)
        frame.stack.append(val2)


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

    def execute(self, frame):
        val = frame.stack.pop()
        if not val.is_none:
            frame.pc = self.argument.value - 1


class InsIfNull(InsBranch):

    """
    if value is null, move pointer to <var>
    """
    opcode = opcodes.IFNULL

    def execute(self, frame):
        val = frame.stack.pop()
        if val.is_none:
            frame.pc = self.argument.value - 1


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

    def execute(self, frame):
        val1 = frame.stack.pop()
        pval = int(val1.value)
        frame.stack.append(ValueInt(pval))


class InsInt2Float(InsNoArgument):

    """
    converts int to float
    """
    opcode = opcodes.I2F

    def execute(self, frame):
        val1 = frame.stack.pop()
        pval = float(val1.value)
        frame.stack.append(ValueFloat(pval))


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

    def execute(self, frame):
        size = frame.stack.pop().value
        arr = self.array_type()
        arr.allocate(asize=size)
        frame.stack.append(arr)


class InsALoad(InsArgILabel):

    """
    load array reference from local variable <var>
    """
    opcode = opcodes.ALOAD

    def execute(self, frame):
        frame.stack.append(frame.variables[self.argument.value])


class InsAStore(InsArgILabel):

    """
    store array reference to local variable <var>
    """
    opcode = opcodes.ASTORE

    def execute(self, frame):
        frame.variables[self.argument.value] = frame.stack.pop()


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

    def execute(self, frame):
        arr = frame.stack.pop()
        frame.stack.append(ValueInt(arr.length))


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

    def execute(self, frame):
        frame.finished = True
        frame.return_value = frame.stack.pop()


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
