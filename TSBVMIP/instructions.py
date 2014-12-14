# -*- coding: utf-8  -*-
import operator
import functools
from collections import OrderedDict

from .values import Value, ValueInt, ValueFloat, ValueIntArrayRef, ValueFloatArrayRef, ArrayObjectRef
from .exceptions import InstructionException, RuntimeException


def check_inout_values(f):
    """
    decorator
    for checking what values are taken from stack and consumed by instruction if any
    then check values pushed to the stack by instruction if any
    """
    @functools.wraps(f)
    def wrfn(self, vm):
        for i, a in enumerate(reversed(self.stack_input_arguments)):
            idx = -(i + 1)
            v = vm.stack_index(idx)
            # if self.no_nulls and v.is_none:
            #     raise RuntimeException('instruction %s cannot operate on empty value' % self.__class__)
            if not a.is_type(v):
                raise RuntimeException('stack value at %d expected %s got %s in %s' % (idx, a, v, self.__class__))
        pre_len = len(vm.stack)
        f(self, vm)
        if len(vm.stack) != (pre_len - len(self.stack_input_arguments) + len(self.stack_output_arguments)):
            raise RuntimeException('stack pre and post lenghts do not match instruction manipulation')
        for i, a in enumerate(reversed(self.stack_output_arguments)):
            idx = -(i + 1)
            v = vm.stack_index(idx)
            # if self.no_nulls and v.is_none:
            #     raise RuntimeException('instruction %s cannot output empty value' % self.__class__)
            if not a.is_type(v):
                raise RuntimeException('stack value at %d should output %s pushed %s in %s' % (idx, a, v, self.__class__))
    return wrfn


class Instruction():

    stack_order = []

    def __str__(self):
        return "%s" % self.__class__.__name__

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.__class__ == other.__class__

    @check_inout_values
    def execute(self, vm):
        self.code(vm)


class InsReturn(Instruction):
    pass


class InsNoArgument(Instruction):
    stack_input_arguments = []
    stack_output_arguments = []


class InsArgument(Instruction):

    def __str__(self):
        return "%s <%s>" % (self.__class__.__name__, self.argument)

    def __init__(self, arg=None):
        if arg is None:
            raise InstructionException('instruction argument is None')
        if type(arg) == type:
            raise InstructionException('argument cannot be class, must be an instance')
        if not isinstance(arg, Value):
            raise InstructionException('instruction argument not type Value: %s' % arg.__class__)
        if arg.is_none:
            raise InstructionException('instruction cannot have argument Value with value None')
        self.argument = arg

    def __eq__(self, other):
        c = super().__eq__(other)
        v = self.argument == other.argument
        return c and v


class InsArgNumber(InsArgument):

    arg_class = None

    def __init__(self, arg=None):
        super().__init__(arg)
        if not isinstance(self.argument, self.arg_class):
            raise InstructionException('ins with {} argument, got type: {}'.format(self.arg_class,
                                                                                   self.argument.value.__class__))


class InsArgInteger(InsArgNumber):
    arg_class = ValueInt


class InsArgFloat(InsArgNumber):
    arg_class = ValueFloat


class InsArgILabel(InsArgInteger):
    pass


class InsJump(InsArgILabel):
    pass


class InsCompareBase(InsJump):
    opr = lambda a, b, c: None

    def code(self, vm):
        val2 = vm.stack_pop()
        val1 = vm.stack_pop()
        if self.opr(val1.value, val2.value):
            vm.pc = self.argument.value
        else:
            vm.pc += 1


class InsICompareBase(InsCompareBase):
    stack_input_arguments = [ValueInt, ValueInt]
    stack_output_arguments = []


class InsFCompareBase(InsCompareBase):
    stack_input_arguments = [ValueFloat, ValueFloat]
    stack_output_arguments = []


class InsMathBase(Instruction):

    def code(self, vm):
        val2 = vm.stack_pop()
        val1 = vm.stack_pop()
        pval = self.opr(val1.value, val2.value)
        vm.stack_push(self.stack_output_arguments[0](pval))
        vm.pc += 1


class InsIMathBase(InsMathBase):
    stack_input_arguments = [ValueInt, ValueInt]
    stack_output_arguments = [ValueInt]


class InsFMathBase(InsMathBase):
    stack_input_arguments = [ValueFloat, ValueFloat]
    stack_output_arguments = [ValueFloat]


class InsArrayLoad(Instruction):
    arr_type = None

    def code(self, vm):
        index = vm.stack_pop().value
        arr = vm.stack_pop()
        arr.contains_type(self.arr_type)
        vm.stack_push(arr[index])
        vm.pc += 1


class InsArrayStore(Instruction):

    def code(self, vm):
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
    stack_input_arguments = []
    stack_output_arguments = [ValueInt]

    def code(self, vm):
        vm.stack_push(self.argument)
        vm.pc += 1


class InsFPush(InsArgFloat):
    """
    push float value onto the stack
    """
    stack_input_arguments = []
    stack_output_arguments = [ValueFloat]

    def code(self, vm):
        vm.stack_push(self.argument)
        vm.pc += 1


class InsILoad(InsArgILabel):
    """
    load integer value from local variable at index
    """
    stack_input_arguments = []
    stack_output_arguments = [ValueInt]

    def code(self, vm):
        vm.stack_push(vm.local_vars[self.argument.value])
        vm.pc += 1


class InsFLoad(InsArgILabel):
    """
    load float value from local variable at index
    """
    stack_input_arguments = []
    stack_output_arguments = [ValueFloat]

    def code(self, vm):
        vm.stack_push(vm.local_vars[self.argument.value])
        vm.pc += 1


class InsIStore(InsArgILabel):
    """
    store integer value to local variable at index
    """
    stack_input_arguments = [ValueInt]
    stack_output_arguments = []

    def code(self, vm):
        vm.local_vars[self.argument.value] = vm.stack_pop()
        vm.pc += 1


class InsFStore(InsArgILabel):
    """
    store float value to local variable at index
    """
    stack_input_arguments = [ValueFloat]
    stack_output_arguments = []

    def code(self, vm):
        vm.local_vars[self.argument.value] = vm.stack_pop()
        vm.pc += 1


class InsGoto(InsJump):
    """
    move pointer to position
    """
    stack_input_arguments = []
    stack_output_arguments = []

    def code(self, vm):
        vm.pc = self.argument.value


class InsIReturn(InsReturn):
    """
    pops value from stack and set it as return value of the code and finishes execution
    """
    stack_input_arguments = [ValueInt]
    stack_output_arguments = []

    def code(self, vm):
        vm.finished = True
        vm.return_value = vm.stack_pop()


class InsFReturn(InsReturn):
    """
    pops value from stack and set it as return value of the code and finishes execution
    """
    stack_input_arguments = [ValueFloat]
    stack_output_arguments = []

    def code(self, vm):
        vm.finished = True
        vm.return_value = vm.stack_pop()


class InsNop(Instruction):
    """
    no effect, no operation
    """
    stack_input_arguments = []
    stack_output_arguments = []

    def code(self, vm):
        vm.pc += 1


class InsPop(Instruction):
    """
    pops value from stack and discards it
    """
    stack_input_arguments = [Value]
    stack_output_arguments = []

    def code(self, vm):
        vm.stack_pop()
        vm.pc += 1


class InsDup(Instruction):
    """
    duplicates value on the stack
    """
    stack_input_arguments = [Value]
    stack_output_arguments = [Value, Value]
    stack_order = [0, 0, 0]

    def code(self, vm):
        val = vm.stack_pop()
        vm.stack_push(val)
        vm.stack_push(val.copy())
        vm.pc += 1


class InsSwap(Instruction):
    """
    swaps values on the stack
    """
    stack_input_arguments = [Value, Value]
    stack_output_arguments = [Value, Value]
    stack_order = [0, 1, 1, 0]

    def code(self, vm):
        val1 = vm.stack_pop()
        val2 = vm.stack_pop()
        vm.stack_push(val1)
        vm.stack_push(val2)
        vm.pc += 1


class InsIIfCmpEq(InsICompareBase):
    """
    if two values are equal, move pointer to <var>
    """
    opr = operator.eq


class InsIIfCmpNe(InsICompareBase):
    """
    if two values are not equal, move pointer to <var>
    """
    opr = operator.ne


class InsIIfCmpGe(InsICompareBase):
    """
    if value1 is greater or equal to value2, move pointer to <var>
    """
    opr = operator.ge


class InsIIfCmpGt(InsICompareBase):
    """
    if value1 is greater than value2, move pointer to <var>
    """
    opr = operator.gt


class InsIIfCmpLe(InsICompareBase):
    """
    if value1 is lower or equal than value2, move pointer to <var>
    """
    opr = operator.le


class InsIIfCmpLt(InsICompareBase):
    """
    if value1 is lower than value2, move pointer to <var>
    """
    opr = operator.lt


class InsFIfCmpEq(InsFCompareBase):
    """
    if two values are equal, move pointer to <var>
    """
    opr = operator.eq


class InsFIfCmpNe(InsFCompareBase):
    """
    if two values are not equal, move pointer to <var>
    """
    opr = operator.ne


class InsFIfCmpGe(InsFCompareBase):
    """
    if value1 is greater or equal to value2, move pointer to <var>
    """
    opr = operator.ge


class InsFIfCmpGt(InsFCompareBase):
    """
    if value1 is greater than value2, move pointer to <var>
    """
    opr = operator.gt


class InsFIfCmpLe(InsFCompareBase):
    """
    if value1 is lower or equal than value2, move pointer to <var>
    """
    opr = operator.le


class InsFIfCmpLt(InsFCompareBase):
    """
    if value1 is lower than value2, move pointer to <var>
    """
    opr = operator.lt


class InsIfNonNull(InsJump):
    """
    if value is not null, move pointer to <var>
    """
    stack_input_arguments = [Value]
    stack_output_arguments = []

    def code(self, vm):
        val = vm.stack_pop()
        if not val.is_none:
            vm.pc = self.argument.value
        else:
            vm.pc += 1


class InsIfNull(InsJump):
    """
    if value is null, move pointer to <var>
    """
    stack_input_arguments = [Value]
    stack_output_arguments = []

    def code(self, vm):
        val = vm.stack_pop()
        if val.is_none:
            vm.pc = self.argument.value
        else:
            vm.pc += 1


class InsIAdd(InsIMathBase):
    """
    add two integers, push result to stack
    """
    opr = operator.add


class InsISub(InsIMathBase):
    """
    subsctract two integers, push result to stack
    """
    opr = operator.sub


class InsIMul(InsIMathBase):
    """
    multiply two integers, push result to stack
    """
    opr = operator.mul


class InsIDiv(InsIMathBase):
    """
    divide two integers, push result to stack
    """
    opr = operator.floordiv


class InsFAdd(InsFMathBase):
    """
    add two floats, push result to stack
    """
    opr = operator.add


class InsFSub(InsFMathBase):
    """
    subsctract two floats, push result to stack
    """
    opr = operator.sub


class InsFMul(InsFMathBase):
    """
    multiply two floats, push result to stack
    """
    opr = operator.mul


class InsFDiv(InsFMathBase):
    """
    divide two floats, push result to stack
    """
    opr = operator.truediv


class InsFloat2Int(Instruction):
    """
    converts float to int
    """
    stack_input_arguments = [ValueFloat]
    stack_output_arguments = [ValueInt]

    def code(self, vm):
        val1 = vm.stack_pop()
        pval = int(val1.value)
        vm.stack_push(ValueInt(pval))
        vm.pc += 1


class InsInt2Float(Instruction):
    """
    converts int to float
    """
    stack_input_arguments = [ValueInt]
    stack_output_arguments = [ValueFloat]

    def code(self, vm):
        val1 = vm.stack_pop()
        pval = float(val1.value)
        vm.stack_push(ValueFloat(pval))
        vm.pc += 1


class InsNewArray(InsArgInteger):
    """
    makes an array of size value1 with type <var>
    """
    stack_input_arguments = [ValueInt]
    stack_output_arguments = [ArrayObjectRef]

    def __init__(self, arg=None):
        super().__init__(arg)
        if self.argument.value == 0:
            self.array_type = ValueIntArrayRef
        elif self.argument.value == 1:
            self.array_type = ValueFloatArrayRef
        else:
            raise InstructionException('newarray can accept only type 0 or 1, received %s' % self.argument.value)

    def code(self, vm):
        size = vm.stack_pop().value
        arr = self.array_type()
        arr.allocate(asize=size)
        vm.stack_push(arr)
        vm.pc += 1


class InsALoad(InsArgILabel):
    """
    load array reference from local variable <var>
    """
    stack_input_arguments = []
    stack_output_arguments = [ArrayObjectRef]

    def code(self, vm):
        vm.stack_push(vm.local_vars[self.argument.value])
        vm.pc += 1


class InsAStore(InsArgILabel):
    """
    store array reference to local variable <var>
    """
    stack_input_arguments = [ArrayObjectRef]
    stack_output_arguments = []

    def code(self, vm):
        arr = vm.stack_pop()
        lvar = vm.local_vars[self.argument.value]
        if not arr.is_type(lvar):
            raise RuntimeException('arrays differ in inner type, cannot assign %s to %s' %
                                   (arr.__class__, lvar.__class__))
        vm.local_vars[self.argument.value] = arr
        vm.pc += 1


class InsAILoad(InsArrayLoad):
    """
    load an int from an array
    """
    stack_input_arguments = [ValueIntArrayRef, ValueInt]
    stack_output_arguments = [ValueInt]


class InsAFLoad(InsArrayLoad):
    """
    load an float from an array
    """
    stack_input_arguments = [ValueFloatArrayRef, ValueInt]
    stack_output_arguments = [ValueFloat]


class InsArrayLength(Instruction):
    """
    returns length of an array
    """
    stack_input_arguments = [ArrayObjectRef]
    stack_output_arguments = [ValueInt]

    def code(self, vm):
        arr = vm.stack_pop()
        vm.stack_push(ValueInt(arr.length))
        vm.pc += 1


class InsAIStore(InsArrayStore):
    """
    store an int to array index
    """
    stack_input_arguments = [ValueIntArrayRef, ValueInt, ValueInt]
    stack_output_arguments = []


class InsAFStore(InsArrayStore):
    """
    store an float to array index
    """
    stack_input_arguments = [ValueFloatArrayRef, ValueInt, ValueFloat]
    stack_output_arguments = []


class InsAReturn(InsReturn):
    """
    pops value from stack and set it as return value of the code and finishes execution
    """
    stack_input_arguments = [ArrayObjectRef]
    stack_output_arguments = []

    def code(self, vm):
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

    ('if_icmpeq', InsIIfCmpEq),
    ('if_icmpne', InsIIfCmpNe),
    ('if_icmpge', InsIIfCmpGe),
    ('if_icmpgt', InsIIfCmpGt),
    ('if_icmple', InsIIfCmpLe),
    ('if_icmplt', InsIIfCmpLt),

    ('if_fcmpeq', InsFIfCmpEq),
    ('if_fcmpne', InsFIfCmpNe),
    ('if_fcmpge', InsFIfCmpGe),
    ('if_fcmpgt', InsFIfCmpGt),
    ('if_fcmple', InsFIfCmpLe),
    ('if_fcmplt', InsFIfCmpLt),

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
    ('aiload', InsAILoad),
    ('afload', InsAFLoad),
    ('aistore', InsAIStore),
    ('afstore', InsAFStore),
    ('arraylength', InsArrayLength),
    ('areturn', InsAReturn)
])
