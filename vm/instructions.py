# -*- coding: utf-8  -*-
import operator
import functools

from vm.values import Value, ValueInt, ValueFloat, ValueString
from vm.exceptions import InstructionException, RuntimeException


class ExpectedValues(object):
    def __init__(self, *args, no_nulls=False):
        self.args = list(args)
        self.no_nulls = no_nulls

    def __call__(self, f):
        @functools.wraps(f)
        def test_values(inner_self, vm):
            for i, a in enumerate(reversed(self.args)):
                idx = -(i + 1)
                v = vm.stack_index(idx)
                if self.no_nulls and v.is_none:
                    raise RuntimeException('instruction %s cannot operate on empty value' % inner_self.__class__)
                if not a.is_type(v):
                    raise RuntimeException(
                        'stack value at %d expected %s got %s in %s' % (idx, a, v, inner_self.__class__))
            f(inner_self, vm)

        return test_values


class Instruction():

    def __str__(self):
        return "%s" % self.__class__.__name__

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.__class__ == other.__class__


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

    def __eq__(self, other):
        c = super().__eq__(other)
        v = self.argument == other.argument
        return c and v


class InsArgString(InsArgument):

    def __init__(self, arg=None):
        super().__init__(arg)
        if not isinstance(self.argument, ValueString):
            raise InstructionException('ins with string argument, got type: %s' % self.argument.value.__class__)


class InsArgNumber(InsArgument):

    def __init__(self, arg=None):
        super().__init__(arg)
        if not isinstance(self.argument, self.arg_class):
            raise InstructionException('ins with {} argument, got type: {}'.format(self.arg_class,
                                                                                   self.argument.value.__class__))


class InsArgInteger(InsArgNumber):
    arg_class = ValueInt


class InsArgFloat(InsArgNumber):
    arg_class = ValueFloat


class InsTypeArg(InsArgString):

    def __init__(self, arg=None):
        super().__init__(arg)
        if self.argument.value.lower() == 'int':
            self.argument = ValueInt()
        elif self.argument.value.lower() == 'float':
            self.argument = ValueFloat()
        else:
            raise InstructionException('bad variable type: %s' % self.argument.value)


class InsCompareBase(InsArgInteger):
    opr = lambda a, b, c: None

    def _execute(self, vm):
        val2 = vm.stack_pop()
        val1 = vm.stack_pop()
        if self.opr(val1.value, val2.value):
            vm.pc = self.argument.value
        else:
            vm.pc += 1


class InsICompareBase(InsCompareBase):

    @ExpectedValues(ValueInt, ValueInt, no_nulls=True)
    def execute(self, vm):
        self._execute(vm)


class InsFCompareBase(InsCompareBase):

    @ExpectedValues(ValueFloat, ValueFloat, no_nulls=True)
    def execute(self, vm):
        self._execute(vm)


class InsMathBase(Instruction):
    opr = lambda a, b, c: None

    def _execute(self, vm, result_class=None):
        val2 = vm.stack_pop()
        val1 = vm.stack_pop()
        pval = self.opr(val1.value, val2.value)
        vm.stack_push(result_class(pval))
        vm.pc += 1


class InsIMathBase(InsMathBase):

    @ExpectedValues(ValueInt, ValueInt, no_nulls=True)
    def execute(self, vm):
        self._execute(vm, result_class=ValueInt)


class InsFMathBase(InsMathBase):

    @ExpectedValues(ValueFloat, ValueFloat, no_nulls=True)
    def execute(self, vm):
        self._execute(vm, result_class=ValueFloat)


class InsIPush(InsArgInteger):
    """
    code> ipush <value>
    value: number

    stack: -> value

    push integer value onto the stack
    """
    def execute(self, vm):
        vm.stack_push(self.argument)
        vm.pc += 1


class InsFPush(InsArgFloat):
    """
    code> fpush <value>
    value: number

    stack: -> value

    push float value onto the stack
    """
    def execute(self, vm):
        vm.stack_push(self.argument)
        vm.pc += 1


class InsILoad(InsArgInteger):
    """
    code> iload <index>
    index: number

    stack: value ->

    load integer value from local variable at index
    """
    def execute(self, vm):
        vm.stack_push(vm.local_vars[self.argument.value])
        vm.pc += 1


class InsFLoad(InsArgInteger):
    """
    code> fload <index>
    index: number

    stack: value ->

    load float value from local variable at index
    """
    def execute(self, vm):
        vm.stack_push(vm.local_vars[self.argument.value])
        vm.pc += 1


class InsIStore(InsArgInteger):
    """
    code> istore <index>
    index: number

    stack: value ->

    store integer value to local variable at index
    """
    @ExpectedValues(ValueInt)
    def execute(self, vm):
        vm.local_vars[self.argument.value] = vm.stack_pop()
        vm.pc += 1


class InsFStore(InsArgInteger):
    """
    code> fstore <index>
    index: number

    stack: value ->

    store float value to local variable at index
    """
    @ExpectedValues(ValueFloat)
    def execute(self, vm):
        vm.local_vars[self.argument.value] = vm.stack_pop()
        vm.pc += 1


class InsGoto(InsArgInteger):
    """
    code> goto <offset>
    offset: number

    stack: ->

    move pointer by offset, can be negative
    """
    def execute(self, vm):
        # TODO validation should be done statically during code loading
        vm.pc = self.argument.value


class InsIReturn(Instruction):
    """
    code> ireturn

    stack: value ->

    pops value from stack and set it as return value of the code and finishes execution
    """
    @ExpectedValues(ValueInt)
    def execute(self, vm):
        vm.finished = True
        vm.return_value = vm.stack_pop()
        vm.pc += 1


class InsFReturn(Instruction):
    """
    code> freturn

    stack: value ->

    pops value from stack and set it as return value of the code and finishes execution
    """
    @ExpectedValues(ValueFloat)
    def execute(self, vm):
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


class InsIIfCmpEq(InsICompareBase):
    """
    code> if_icmpeq <offset>
    offset: number

    stack: value1, value2 ->
    value1: integer
    value2: integer
    if two values are equal, move pointer by offset
    """
    opr = operator.eq


class InsIIfCmpNe(InsICompareBase):
    """
    code> if_icmpne <offset>
    offset: number

    stack: value1, value2 ->
    value1: integer
    value2: integer
    if two values are not equal, move pointer by offset
    """
    opr = operator.ne


class InsIIfCmpGe(InsICompareBase):
    """
    code> if_icmpge <offset>
    offset: number

    stack: value1, value2 ->
    value1: integer
    value2: integer
    if value1 is greater or equal to value2, move pointer by offset
    """
    opr = operator.ge


class InsIIfCmpGt(InsICompareBase):
    """
    code> if_icmpgt <offset>
    offset: number

    stack: value1, value2 ->
    value1: integer
    value2: integer
    if value1 is greater than value2, move pointer by offset
    """
    opr = operator.gt


class InsIIfCmpLe(InsICompareBase):
    """
    code> if_icmple <offset>
    offset: number

    stack: value1, value2 ->
    value1: integer
    value2: integer
    if value1 is lower or equal than value2, move pointer by offset
    """
    opr = operator.le


class InsIIfCmpLt(InsICompareBase):
    """
    code> if_icmplt <offset>
    offset: number

    stack: value1, value2 ->
    value1: integer
    value2: integer
    if value1 is lower than value2, move pointer by offset
    """
    opr = operator.lt


class InsFIfCmpEq(InsFCompareBase):
    """
    code> if_fcmpeq <offset>
    offset: number

    stack: value1, value2 ->
    value1: float
    value2: float
    if two values are equal, move pointer by offset
    """
    opr = operator.eq


class InsFIfCmpNe(InsFCompareBase):
    """
    code> if_fcmpne <offset>
    offset: number

    stack: value1, value2 ->
    value1: float
    value2: float
    if two values are not equal, move pointer by offset
    """
    opr = operator.ne


class InsFIfCmpGe(InsFCompareBase):
    """
    code> if_fcmpge <offset>
    offset: number

    stack: value1, value2 ->
    value1: float
    value2: float
    if value1 is greater or equal to value2, move pointer by offset
    """
    opr = operator.ge


class InsFIfCmpGt(InsFCompareBase):
    """
    code> if_fcmpgt <offset>
    offset: number

    stack: value1, value2 ->
    value1: float
    value2: float
    if value1 is greater than value2, move pointer by offset
    """
    opr = operator.gt


class InsFIfCmpLe(InsFCompareBase):
    """
    code> if_fcmple <offset>
    offset: number

    stack: value1, value2 ->
    value1: float
    value2: float
    if value1 is lower or equal than value2, move pointer by offset
    """
    opr = operator.le


class InsFIfCmpLt(InsFCompareBase):
    """
    code> if_fcmplt <offset>
    offset: number

    stack: value1, value2 ->
    value1: float
    value2: float
    if value1 is lower than value2, move pointer by offset
    """
    opr = operator.lt


class InsIfNonNull(InsArgInteger):
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


class InsIfNull(InsArgInteger):
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


class InsIAdd(InsIMathBase):
    """
    code> iadd

    stack: value1, value2 -> value3
    value1: integer
    value2: integer
    value3: integer
    value3 = value1 + value2
    """
    opr = operator.add


class InsISub(InsIMathBase):
    """
    code> isub

    stack: value1, value2 -> value3
    value1: integer
    value2: integer
    value3: integer
    value3 = value1 - value2
    """
    opr = operator.sub


class InsIMul(InsIMathBase):
    """
    code> imul

    stack: value1, value2 -> value3
    value1: integer
    value2: integer
    value3: integer
    value3 = value1 * value2
    """
    opr = operator.mul


class InsIDiv(InsIMathBase):
    """
    code> idiv

    stack: value1, value2 -> value3
    value1: integer
    value2: integer
    value3: integer
    value3 = value1 // value2
    """
    opr = operator.floordiv


class InsFAdd(InsFMathBase):
    """
    code> iadd

    stack: value1, value2 -> value3
    value1: float
    value2: float
    value3: float
    value3 = value1 + value2
    """
    opr = operator.add


class InsFSub(InsFMathBase):
    """
    code> isub

    stack: value1, value2 -> value3
    value1: float
    value2: float
    value3: float
    value3 = value1 - value2
    """
    opr = operator.sub


class InsFMul(InsFMathBase):
    """
    code> imul

    stack: value1, value2 -> value3
    value1: float
    value2: float
    value3: float
    value3 = value1 * value2
    """
    opr = operator.mul


class InsFDiv(InsFMathBase):
    """
    code> idiv

    stack: value1, value2 -> value3
    value1: float
    value2: float
    value3: float
    value3 = value1 / value2
    """
    opr = operator.truediv


class InsFloat2Int(Instruction):
    """
    code> f2i

    stack: value1 -> value2
    value1: float
    value2: int
    converts float to int
    """
    @ExpectedValues(ValueFloat)
    def execute(self, vm):
        val1 = vm.stack_pop()
        pval = int(val1.value)
        vm.stack_push(ValueInt(pval))
        vm.pc += 1


class InsInt2Float(Instruction):
    """
    code> i2f

    stack: value1 -> value2
    value1: int
    value2: float
    converts int to float
    """
    @ExpectedValues(ValueInt)
    def execute(self, vm):
        val1 = vm.stack_pop()
        pval = float(val1.value)
        vm.stack_push(ValueFloat(pval))
        vm.pc += 1


keywords = {
    'ipush': InsIPush,
    'fpush': InsFPush,
    'iload': InsILoad,
    'fload': InsFLoad,
    'istore': InsIStore,
    'fstore': InsFStore,
    'goto': InsGoto,

    'ireturn': InsIReturn,
    'freturn': InsFReturn,
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

    'if_fcmpeq': InsFIfCmpEq,
    'if_fcmpne': InsFIfCmpNe,
    'if_fcmpge': InsFIfCmpGe,
    'if_fcmpgt': InsFIfCmpGt,
    'if_fcmple': InsFIfCmpLe,
    'if_fcmplt': InsFIfCmpLt,

    'ifnonnull': InsIfNonNull,
    'ifnull': InsIfNull,

    'iadd': InsIAdd,
    'isub': InsISub,
    'imul': InsIMul,
    'idiv': InsIDiv,
    'fadd': InsFAdd,
    'fsub': InsFSub,
    'fmul': InsFMul,
    'fdiv': InsFDiv,

    'f2i': InsFloat2Int,
    'i2f': InsInt2Float
    }
