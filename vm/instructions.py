# -*- coding: utf-8  -*-
import operator
import functools

from vm.values import Value, ValueInt, ValueFloat, ValueIntArrayRef, ValueFloatArrayRef, ArrayObjectRef
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

    def __init__(self, arg=None):
        super().__init__(arg)
        if not isinstance(self.argument, self.arg_class):
            raise InstructionException('ins with {} argument, got type: {}'.format(self.arg_class,
                                                                                   self.argument.value.__class__))


class InsArgInteger(InsArgNumber):
    arg_class = ValueInt


class InsArgFloat(InsArgNumber):
    arg_class = ValueFloat


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


class InsArrayLoad(Instruction):
    arr_type = None

    @ExpectedValues(ArrayObjectRef, ValueInt, no_nulls=True)
    def execute(self, vm):
        index = vm.stack_pop().value
        arr = vm.stack_pop()
        arr.contains_type(self.arr_type)
        vm.stack_push(arr[index])
        vm.pc += 1


class InsArrayStore(Instruction):
    arr_type = None

    def _execute(self, vm):
        value = vm.stack_pop()
        index = vm.stack_pop().value
        arr = vm.stack_pop()
        arr.contains_type(self.arr_type)
        arr[index] = value
        vm.pc += 1


class InsIPush(InsArgInteger):
    """
    code> ipush <value>
    value: int

    stack: -> value

    push integer value onto the stack
    """
    def execute(self, vm):
        vm.stack_push(self.argument)
        vm.pc += 1


class InsFPush(InsArgFloat):
    """
    code> fpush <value>
    value: float

    stack: -> value

    push float value onto the stack
    """
    def execute(self, vm):
        vm.stack_push(self.argument)
        vm.pc += 1


class InsILoad(InsArgInteger):
    """
    code> iload <var>

    stack: value ->

    load integer value from local variable at index
    """
    def execute(self, vm):
        vm.stack_push(vm.local_vars[self.argument.value])
        vm.pc += 1


class InsFLoad(InsArgInteger):
    """
    code> fload <var>

    stack: value ->

    load float value from local variable at index
    """
    def execute(self, vm):
        vm.stack_push(vm.local_vars[self.argument.value])
        vm.pc += 1


class InsIStore(InsArgInteger):
    """
    code> istore <var>

    stack: value ->

    store integer value to local variable at index
    """
    @ExpectedValues(ValueInt)
    def execute(self, vm):
        vm.local_vars[self.argument.value] = vm.stack_pop()
        vm.pc += 1


class InsFStore(InsArgInteger):
    """
    code> fstore <var>

    stack: value ->

    store float value to local variable at index
    """
    @ExpectedValues(ValueFloat)
    def execute(self, vm):
        vm.local_vars[self.argument.value] = vm.stack_pop()
        vm.pc += 1


class InsGoto(InsArgInteger):
    """
    code> goto <var>

    stack: ->

    move pointer to <var>, can be negative
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

    pops value from stack and discards it
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
    code> if_icmpeq <var>

    stack: value1, value2 ->
    value1: integer
    value2: integer

    if two values are equal, move pointer to <var>
    """
    opr = operator.eq


class InsIIfCmpNe(InsICompareBase):
    """
    code> if_icmpne <var>

    stack: value1, value2 ->
    value1: integer
    value2: integer

    if two values are not equal, move pointer to <var>
    """
    opr = operator.ne


class InsIIfCmpGe(InsICompareBase):
    """
    code> if_icmpge <var>

    stack: value1, value2 ->
    value1: integer
    value2: integer

    if value1 is greater or equal to value2, move pointer to <var>
    """
    opr = operator.ge


class InsIIfCmpGt(InsICompareBase):
    """
    code> if_icmpgt <var>

    stack: value1, value2 ->
    value1: integer
    value2: integer

    if value1 is greater than value2, move pointer to <var>
    """
    opr = operator.gt


class InsIIfCmpLe(InsICompareBase):
    """
    code> if_icmple <var>

    stack: value1, value2 ->
    value1: integer
    value2: integer

    if value1 is lower or equal than value2, move pointer to <var>
    """
    opr = operator.le


class InsIIfCmpLt(InsICompareBase):
    """
    code> if_icmplt <var>

    stack: value1, value2 ->
    value1: integer
    value2: integer

    if value1 is lower than value2, move pointer to <var>
    """
    opr = operator.lt


class InsFIfCmpEq(InsFCompareBase):
    """
    code> if_fcmpeq <var>

    stack: value1, value2 ->
    value1: float
    value2: float

    if two values are equal, move pointer to <var>
    """
    opr = operator.eq


class InsFIfCmpNe(InsFCompareBase):
    """
    code> if_fcmpne <var>

    stack: value1, value2 ->
    value1: float
    value2: float

    if two values are not equal, move pointer to <var>
    """
    opr = operator.ne


class InsFIfCmpGe(InsFCompareBase):
    """
    code> if_fcmpge <var>

    stack: value1, value2 ->
    value1: float
    value2: float

    if value1 is greater or equal to value2, move pointer to <var>
    """
    opr = operator.ge


class InsFIfCmpGt(InsFCompareBase):
    """
    code> if_fcmpgt <var>

    stack: value1, value2 ->
    value1: float
    value2: float

    if value1 is greater than value2, move pointer to <var>
    """
    opr = operator.gt


class InsFIfCmpLe(InsFCompareBase):
    """
    code> if_fcmple <var>

    stack: value1, value2 ->
    value1: float
    value2: float

    if value1 is lower or equal than value2, move pointer to <var>
    """
    opr = operator.le


class InsFIfCmpLt(InsFCompareBase):
    """
    code> if_fcmplt <var>

    stack: value1, value2 ->
    value1: float
    value2: float

    if value1 is lower than value2, move pointer to <var>
    """
    opr = operator.lt


class InsIfNonNull(InsArgInteger):
    """
    code> ifnonnull <var>

    stack: value ->

    if value is not null, move pointer to <var>
    """
    def execute(self, vm):
        val = vm.stack_pop()
        if not val.is_none:
            vm.pc += self.argument.value
        else:
            vm.pc += 1


class InsIfNull(InsArgInteger):
    """
    code> ifnull <var>

    stack: value ->

    if value is null, move pointer to <var>
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


class InsNewArray(InsArgInteger):
    """
    code> newarray <var>

    stack: value1 -> value2
    value1: int
    value2: reference

    makes an array of size value1 with type <var>
    """

    def __init__(self, arg=None):
        super().__init__(arg)
        if self.argument.value == 0:
            self.array_type = ValueIntArrayRef
        elif self.argument.value == 1:
            self.array_type = ValueFloatArrayRef
        else:
            raise InstructionException('newarray can accept only type 0 or 1, received %s' % self.argument.value)

    @ExpectedValues(ValueInt, no_nulls=True)
    def execute(self, vm):
        size = vm.stack_pop().value
        arr = self.array_type()
        arr.allocate(asize=size)
        vm.stack_push(arr)
        vm.pc += 1


class InsALoad(InsArgInteger):
    """
    code> aload <var>

    stack: -> arrayref
    arrayref: reference

    load array reference from local variable <var>
    """

    def execute(self, vm):
        vm.stack_push(vm.local_vars[self.argument.value])
        vm.pc += 1


class InsAStore(InsArgInteger):
    """
    code> astore <var>

    stack: value ->
    value: reference

    store array reference to local variable <var>
    """

    @ExpectedValues(ArrayObjectRef)
    def execute(self, vm):
        arr = vm.stack_pop()
        if vm.local_vars[self.argument.value].__class__ != arr.__class__:
            raise RuntimeException('arrays differ in inner type, cannot assign')
        vm.local_vars[self.argument.value] = arr
        vm.pc += 1


class InsAILoad(InsArrayLoad):
    """
    code> aiload

    stack: value1, value2 -> value3
    value1: reference
    value2: int
    value3: int

    load an int from an array
    """
    arr_type = ValueInt


class InsAFLoad(InsArrayLoad):
    """
    code> afload

    stack: value1, value2 -> value3
    value1: reference
    value2: int
    value3: float

    load an float from an array
    """
    arr_type = ValueFloat


class InsArrayLength(Instruction):
    """
    code> arraylength

    stack: value1 -> value2
    value1: reference
    value2: int

    returns length of an array
    """

    @ExpectedValues(ArrayObjectRef)
    def execute(self, vm):
        arr = vm.stack_pop()
        vm.stack_push(ValueInt(arr.length))
        vm.pc += 1


class InsAIStore(InsArrayStore):
    """
    code> aistore

    stack: ref, index, value ->
    ref: arrayref
    index: int
    value: int

    store an int to array index
    """
    arr_type = ValueInt

    @ExpectedValues(ArrayObjectRef, ValueInt, ValueInt)
    def execute(self, vm):
        self._execute(vm)


class InsAFStore(InsArrayStore):
    """
    code> afstore

    stack: ref, index, value ->
    ref: arrayref
    index: int
    value: float

    store an float to array index
    """
    arr_type = ValueFloat

    @ExpectedValues(ArrayObjectRef, ValueInt, ValueFloat)
    def execute(self, vm):
        self._execute(vm)


class InsAReturn(Instruction):
    """
    code> areturn

    stack: value ->

    pops value from stack and set it as return value of the code and finishes execution
    """
    @ExpectedValues(ArrayObjectRef)
    def execute(self, vm):
        vm.finished = True
        vm.return_value = vm.stack_pop()


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
    'i2f': InsInt2Float,

    'newarray': InsNewArray,
    'aload': InsALoad,
    'astore': InsAStore,
    'aiload': InsAILoad,
    'afload': InsAFLoad,
    'aistore': InsAIStore,
    'afstore': InsAFStore,
    'arraylength': InsArrayLength,
    'areturn': InsAReturn
    }
