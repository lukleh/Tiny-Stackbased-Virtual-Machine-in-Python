# -*- coding: utf8 -*-
import pytest

import TSBVMIP.values as values
import TSBVMIP.instructions as instructions
import TSBVMIP.engine as engine
import TSBVMIP.yparser as parser
from TSBVMIP.exceptions import RuntimeException, InstructionException


VM_PC_START = 10


def make_vm():
    c = parser.Code(func={'name': 'n',
                          'args': [
                              {'type': 'int'},
                              {'type': 'float'}
                          ]},
                    lvars=[
                        {'type': 'int'},
                        {'type': 'float'},
                        {'type': 'intarray'},
                        {'type': 'floatarray'}
                    ])
    vme = engine.VM(c)
    vme.assign_arguments(vme.convert_args([1, 1.0]))
    vme.pc = VM_PC_START  # shift pointer so we can check absolute jumps
    return vme


def test_args():
    for name, ins in instructions.keywords.items():
        if issubclass(ins, instructions.InsArgument):
            pytest.raises(InstructionException, ins)
            if issubclass(ins, instructions.InsArgInteger):
                assert ins(values.ValueInt(1)) is not None
                pytest.raises(InstructionException, ins, 'int')
                pytest.raises(InstructionException, ins, values.ValueInt())
            elif issubclass(ins, instructions.InsArgFloat):
                assert ins(values.ValueFloat(1.0)) is not None
                pytest.raises(InstructionException, ins, 'float')
                pytest.raises(InstructionException, ins, values.ValueFloat())
        else:
            assert ins() is not None


def test_expected_values():
    vm = make_vm()
    vm.stack_push(values.ValueInt(99))
    vm.stack_push(values.ValueInt(99))

    class T():
        stack_input_arguments = [values.ValueInt, values.ValueInt]
        stack_output_arguments = []
        @instructions.check_inout_values
        def f(self, _):
            pass
    pytest.raises(RuntimeException, T().f, vm)


def test_ins_ipush():
    vm = make_vm()
    value = values.ValueInt(99)
    assert len(vm.stack) == 0
    instructions.keywords['ipush'](value).execute(vm)
    assert vm.pc == VM_PC_START + 1
    assert vm.stack[0] == value


def test_ins_fpush():
    vm = make_vm()
    value = values.ValueFloat(9.9)
    assert len(vm.stack) == 0
    instructions.keywords['fpush'](value).execute(vm)
    assert vm.pc == VM_PC_START + 1
    assert vm.stack[0] == value


def test_ins_iload():
    vm = make_vm()
    value = values.ValueInt(99)
    vm.local_vars[0] = value
    assert len(vm.stack) == 0
    instructions.keywords['iload'](values.ValueInt(0)).execute(vm)
    assert vm.pc == VM_PC_START + 1
    assert vm.stack[0] == value


def test_ins_fload():
    vm = make_vm()
    value = values.ValueFloat(9.9)
    vm.local_vars[0] = value
    assert len(vm.stack) == 0
    instructions.keywords['fload'](values.ValueInt(0)).execute(vm)
    assert vm.pc == VM_PC_START + 1
    assert vm.stack[0] == value


def test_ins_istore():
    ins = instructions.keywords['istore']
    vm = make_vm()
    value = values.ValueInt(99)
    vm.stack_push(value)
    ins(values.ValueInt(0)).execute(vm)
    assert vm.local_vars[0] == value
    assert vm.pc == VM_PC_START + 1
    assert len(vm.stack) == 0
    vm.stack_push(values.ValueFloat(9.9))
    pytest.raises(RuntimeException, ins(values.ValueInt(0)).execute, vm)


def test_ins_fstore():
    ins = instructions.keywords['fstore']
    vm = make_vm()
    value = values.ValueFloat(9.9)
    vm.stack_push(value)
    ins(values.ValueInt(0)).execute(vm)
    assert vm.local_vars[0] == value
    assert vm.pc == VM_PC_START + 1
    assert len(vm.stack) == 0
    vm.stack_push(values.ValueInt(99))
    pytest.raises(RuntimeException, ins(values.ValueInt(0)).execute, vm)


def test_ins_goto():
    ins = instructions.keywords['goto']
    vm = make_vm()
    ins(values.ValueInt(8)).execute(vm)
    assert vm.pc == 8


def test_ins_ireturn():
    ins = instructions.keywords['ireturn']
    vm = make_vm()
    value = values.ValueInt(99)
    vm.stack_push(value)
    ins().execute(vm)
    assert vm.pc == VM_PC_START
    assert vm.finished is True
    assert vm.return_value == value
    vm.stack_push(values.ValueFloat(9.9))
    pytest.raises(RuntimeException, ins().execute, vm)


def test_ins_freturn():
    ins = instructions.keywords['freturn']
    vm = make_vm()
    value = values.ValueFloat(9.9)
    vm.stack_push(value)
    ins().execute(vm)
    assert vm.pc == VM_PC_START
    assert vm.finished is True
    assert vm.return_value == value
    vm.stack_push(values.ValueInt(99))
    pytest.raises(RuntimeException, ins().execute, vm)


def test_ins_nop():
    vm = make_vm()
    instructions.keywords['nop']().execute(vm)
    assert vm.pc == VM_PC_START + 1
    assert len(vm.stack) == 0


def test_ins_pop():
    vm = make_vm()
    vm.stack_push(values.ValueInt(99))
    assert len(vm.stack) == 1
    instructions.keywords['pop']().execute(vm)
    assert vm.pc == VM_PC_START + 1
    assert len(vm.stack) == 0


def test_ins_dup():
    vm = make_vm()
    vm.stack_push(values.ValueInt(99))
    assert len(vm.stack) == 1
    instructions.keywords['dup']().execute(vm)
    assert vm.pc == VM_PC_START + 1
    assert len(vm.stack) == 2
    assert vm.stack[0].__class__ == vm.stack[1].__class__
    assert vm.stack[0].value == vm.stack[1].value


def test_ins_swap():
    vm = make_vm()
    vm.stack_push(values.ValueInt(99))
    vm.stack_push(values.ValueFloat(5.5))
    assert len(vm.stack) == 2
    assert isinstance(vm.stack[0], values.ValueInt)
    assert isinstance(vm.stack[1], values.ValueFloat)
    assert vm.stack[0].value == 99
    assert vm.stack[1].value == 5.5
    instructions.keywords['swap']().execute(vm)
    assert vm.pc == VM_PC_START + 1
    assert len(vm.stack) == 2
    assert isinstance(vm.stack[1], values.ValueInt)
    assert isinstance(vm.stack[0], values.ValueFloat)
    assert vm.stack[1].value == 99
    assert vm.stack[0].value == 5.5


def test_ins_if_icmpeq():
    ins = instructions.keywords['if_icmpeq']
    vm = make_vm()
    vm.stack_push(values.ValueInt(99))
    vm.stack_push(values.ValueInt(99))
    assert len(vm.stack) == 2
    ins(values.ValueInt(2)).execute(vm)
    assert vm.pc == 2
    assert len(vm.stack) == 0
    vm = make_vm()
    vm.stack_push(values.ValueInt(99))
    vm.stack_push(values.ValueInt(100))
    ins(values.ValueInt(2)).execute(vm)
    assert vm.pc == VM_PC_START + 1
    vm.stack_push(values.ValueFloat(9.9))
    vm.stack_push(values.ValueFloat(9.9))
    pytest.raises(RuntimeException, ins(values.ValueInt(0)).execute, vm)


def test_ins_if_fcmpeq():
    ins = instructions.keywords['if_fcmpeq']
    vm = make_vm()
    vm.stack_push(values.ValueFloat(9.9))
    vm.stack_push(values.ValueFloat(9.9))
    assert len(vm.stack) == 2
    ins(values.ValueInt(2)).execute(vm)
    assert vm.pc == 2
    assert len(vm.stack) == 0
    vm = make_vm()
    vm.stack_push(values.ValueFloat(9.9))
    vm.stack_push(values.ValueFloat(9.91))
    ins(values.ValueInt(2)).execute(vm)
    assert vm.pc == VM_PC_START + 1
    vm.stack_push(values.ValueInt(99))
    vm.stack_push(values.ValueInt(99))
    pytest.raises(RuntimeException, ins(values.ValueInt(0)).execute, vm)


def test_ins_if_icmpne():
    ins = instructions.keywords['if_icmpne']
    vm = make_vm()
    vm.stack_push(values.ValueInt(99))
    vm.stack_push(values.ValueInt(100))
    ins(values.ValueInt(2)).execute(vm)
    assert vm.pc == 2
    vm.stack_push(values.ValueFloat(9.9))
    vm.stack_push(values.ValueFloat(9.9))
    pytest.raises(RuntimeException, ins(values.ValueInt(0)).execute, vm)


def test_ins_if_icmpge():
    ins = instructions.keywords['if_icmpge']
    vm = make_vm()
    vm.stack_push(values.ValueInt(100))
    vm.stack_push(values.ValueInt(99))
    vm.stack_push(values.ValueInt(100))
    vm.stack_push(values.ValueInt(100))
    ins(values.ValueInt(2)).execute(vm)
    assert vm.pc == 2
    ins(values.ValueInt(4)).execute(vm)
    assert vm.pc == 4
    vm.stack_push(values.ValueFloat(9.9))
    vm.stack_push(values.ValueFloat(9.9))
    pytest.raises(RuntimeException, ins(values.ValueInt(0)).execute, vm)


def test_ins_if_icmpgt():
    ins = instructions.keywords['if_icmpgt']
    vm = make_vm()
    vm.stack_push(values.ValueInt(100))
    vm.stack_push(values.ValueInt(99))
    ins(values.ValueInt(2)).execute(vm)
    assert vm.pc == 2
    vm.stack_push(values.ValueFloat(9.9))
    vm.stack_push(values.ValueFloat(9.9))
    pytest.raises(RuntimeException, ins(values.ValueInt(0)).execute, vm)


def test_ins_if_icmple():
    ins = instructions.keywords['if_icmple']
    vm = make_vm()
    vm.stack_push(values.ValueInt(100))
    vm.stack_push(values.ValueInt(101))
    vm.stack_push(values.ValueInt(100))
    vm.stack_push(values.ValueInt(100))
    ins(values.ValueInt(2)).execute(vm)
    assert vm.pc == 2
    ins(values.ValueInt(4)).execute(vm)
    assert vm.pc == 4
    vm.stack_push(values.ValueFloat(9.9))
    vm.stack_push(values.ValueFloat(9.9))
    pytest.raises(RuntimeException, ins(values.ValueInt(0)).execute, vm)


def test_ins_if_icmplt():
    ins = instructions.keywords['if_icmple']
    vm = make_vm()
    vm.stack_push(values.ValueInt(100))
    vm.stack_push(values.ValueInt(101))
    ins(values.ValueInt(2)).execute(vm)
    assert vm.pc == 2
    vm.stack_push(values.ValueFloat(9.9))
    vm.stack_push(values.ValueFloat(9.9))
    pytest.raises(RuntimeException, ins(values.ValueInt(0)).execute, vm)


def test_ins_ifnonnull():
    vm = make_vm()
    vm.stack_push(values.ValueInt(100))
    instructions.keywords['ifnonnull'](values.ValueInt(2)).execute(vm)
    assert vm.pc == 2


def test_ins_ifnull():
    vm = make_vm()
    vm.stack_push(values.ValueInt())
    instructions.keywords['ifnull'](values.ValueInt(2)).execute(vm)
    assert vm.pc == 2


def test_ins_iadd():
    ins = instructions.keywords['iadd']
    vm = make_vm()
    vm.stack_push(values.ValueInt(100))
    vm.stack_push(values.ValueInt(101))
    ins().execute(vm)
    assert vm.pc == VM_PC_START + 1
    assert vm.stack[0] == values.ValueInt(201)
    vm.stack_push(values.ValueFloat(9.9))
    vm.stack_push(values.ValueFloat(9.9))
    pytest.raises(RuntimeException, ins().execute, vm)


def test_ins_isub():
    ins = instructions.keywords['isub']
    vm = make_vm()
    vm.stack_push(values.ValueInt(100))
    vm.stack_push(values.ValueInt(101))
    ins().execute(vm)
    assert vm.stack[0] == values.ValueInt(-1)
    vm.stack_push(values.ValueFloat(9.9))
    vm.stack_push(values.ValueFloat(9.9))
    pytest.raises(RuntimeException, ins().execute, vm)


def test_ins_imul():
    ins = instructions.keywords['imul']
    vm = make_vm()
    vm.stack_push(values.ValueInt(100))
    vm.stack_push(values.ValueInt(101))
    ins().execute(vm)
    assert vm.stack[0] == values.ValueInt(10100)
    vm.stack_push(values.ValueFloat(9.9))
    vm.stack_push(values.ValueFloat(9.9))
    pytest.raises(RuntimeException, ins().execute, vm)


def test_ins_idiv():
    ins = instructions.keywords['idiv']
    vm = make_vm()
    vm.stack_push(values.ValueInt(55))
    vm.stack_push(values.ValueInt(10))
    ins().execute(vm)
    assert vm.stack[0] == values.ValueInt(5)
    vm.stack_push(values.ValueFloat(9.9))
    vm.stack_push(values.ValueFloat(9.9))
    pytest.raises(RuntimeException, ins().execute, vm)


def test_ins_fdiv():
    ins = instructions.keywords['fdiv']
    vm = make_vm()
    vm.stack_push(values.ValueFloat(55.0))
    vm.stack_push(values.ValueFloat(10.0))
    ins().execute(vm)
    assert vm.stack[0] == values.ValueFloat(5.5)
    vm.stack_push(values.ValueInt(9))
    vm.stack_push(values.ValueInt(9))
    pytest.raises(RuntimeException, ins().execute, vm)


def test_ins_i2f():
    ins = instructions.keywords['i2f']
    vm = make_vm()
    vm.stack_push(values.ValueInt(55))
    ins().execute(vm)
    assert vm.stack[0] == values.ValueFloat(55.0)
    vm.stack_push(values.ValueFloat(9.9))
    pytest.raises(RuntimeException, ins().execute, vm)


def test_ins_f2i():
    ins = instructions.keywords['f2i']
    vm = make_vm()
    vm.stack_push(values.ValueFloat(9.9))
    ins().execute(vm)
    assert vm.stack[0] == values.ValueInt(9)
    vm.stack_push(values.ValueInt(9))
    pytest.raises(RuntimeException, ins().execute, vm)


def test_newarray():
    ins = instructions.keywords['newarray']
    vm = make_vm()
    vm.stack_push(values.ValueInt(10))
    ins(values.ValueInt(1)).execute(vm)
    assert vm.stack_pop().__class__ == values.ValueFloatArrayRef


def test_aload():
    ins = instructions.keywords['aload']
    vm = make_vm()
    arr = values.ValueIntArrayRef()
    vm.local_vars[4] = arr
    ins(values.ValueInt(4)).execute(vm)
    assert vm.stack_pop() == arr


def test_astore():
    ins = instructions.keywords['astore']
    vm = make_vm()
    arr = values.ValueIntArrayRef()
    vm.stack_push(arr)
    ins(values.ValueInt(4)).execute(vm)
    assert vm.local_vars[4] == arr


def test_aiload():
    vt = values.ValueInt
    ins = instructions.keywords['aiload']
    vm = make_vm()
    arr = values.ValueIntArrayRef()
    arr.allocate(10)
    arr[2] = values.ValueInt(4)
    vm.stack_push(arr)
    vm.stack_push(values.ValueInt(2))
    ins().execute(vm)
    assert vm.stack_pop() == vt(4)
    vm.stack_push(arr)
    vm.stack_push(values.ValueInt(1))
    ins().execute(vm)
    sv = vm.stack_pop()
    assert sv.is_none
    assert sv.__class__ == vt


def test_afload():
    vt = values.ValueFloat
    ins = instructions.keywords['afload']
    vm = make_vm()
    arr = values.ValueFloatArrayRef()
    arr.allocate(10)
    arr[2] = values.ValueFloat(4.0)
    vm.stack_push(arr)
    vm.stack_push(values.ValueInt(2))
    ins().execute(vm)
    assert vm.stack_pop() == vt(4.0)
    vm.stack_push(arr)
    vm.stack_push(values.ValueInt(1))
    ins().execute(vm)
    sv = vm.stack_pop()
    assert sv.is_none
    assert sv.__class__ == vt


def test_aistore():
    vt = values.ValueInt
    ins = instructions.keywords['aistore']
    vm = make_vm()
    arr = values.ValueIntArrayRef()
    arr.allocate(10)
    arr[2] = values.ValueInt(4)
    vm.stack_push(arr)
    vm.stack_push(values.ValueInt(0))
    vm.stack_push(values.ValueInt(5))
    ins().execute(vm)
    assert arr[0] == vt(5)
    assert arr[1].is_none
    assert arr[1].__class__ == vt


def test_afstore():
    vt = values.ValueFloat
    ins = instructions.keywords['afstore']
    vm = make_vm()
    arr = values.ValueFloatArrayRef()
    arr.allocate(10)
    arr[2] = values.ValueFloat(4.0)
    vm.stack_push(arr)
    vm.stack_push(values.ValueInt(0))
    vm.stack_push(values.ValueFloat(5.0))
    ins().execute(vm)
    assert arr[0] == vt(5.0)
    assert arr[1].is_none
    assert arr[1].__class__ == vt


def test_ins_array_length():
    ins = instructions.keywords['arraylength']
    vm = make_vm()
    value = values.ValueFloatArrayRef()
    value.allocate(10)
    value[2] = values.ValueFloat(4.0)
    vm.stack_push(value)
    ins().execute(vm)
    assert vm.pc == VM_PC_START + 1
    v = vm.stack_pop()
    assert v == values.ValueInt(10)
    pytest.raises(RuntimeException, ins().execute, vm)


def test_ins_areturn():
    ins = instructions.keywords['areturn']
    vm = make_vm()
    value = values.ValueFloatArrayRef()
    value.allocate(10)
    value[2] = values.ValueFloat(4.0)
    vm.stack_push(value)
    ins().execute(vm)
    assert vm.pc == VM_PC_START
    assert vm.finished is True
    assert vm.return_value == value
    vm.stack_push(values.ValueInt(99))
    pytest.raises(RuntimeException, ins().execute, vm)