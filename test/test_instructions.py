# -*- coding: utf8 -*-
import pytest

import TSBVMIP.value_containers as value_containers
import TSBVMIP.instructions as instructions
import TSBVMIP.engine as engine
import TSBVMIP.code_parser as parser
from TSBVMIP.exceptions import RuntimeException, InstructionException


VM_PC_START = 10


def make_vm():
    c = parser.process_yaml(dict(func={'name': 'n',
                                       'args': [
                                           {'type': 'int', 'label': 'a'},
                                           {'type': 'float', 'label': 'b'}
                                       ],
                                       'type': 'int'},
                                 lvars=[
                                     {'type': 'int', 'label': 'c'},
                                     {'type': 'float', 'label': 'd'},
                                     {'type': 'intarray', 'label': 'e'},
                                     {'type': 'floatarray', 'label': 'f'}
    ]))
    vme = engine.VM(c)
    vme.assign_arguments(vme.convert_args([1, 1.0]))
    vme.pc = VM_PC_START  # shift pointer so we can check absolute jumps
    return vme


def test_args():
    for name, ins in instructions.keywords.items():
        if issubclass(ins, instructions.InsArgument):
            pytest.raises(InstructionException, ins)
            if issubclass(ins, instructions.InsArgInteger):
                assert ins(value_containers.ValueInt(1)) is not None
            elif issubclass(ins, instructions.InsArgFloat):
                assert ins(value_containers.ValueFloat(1.0)) is not None
        else:
            assert ins() is not None


def test_ins_ipush():
    vm = make_vm()
    value = value_containers.ValueInt(99)
    assert len(vm.stack) == 0
    instructions.keywords['ipush'](value).execute(vm)
    assert vm.pc == VM_PC_START + 1
    assert vm.stack[0] == value


def test_ins_fpush():
    vm = make_vm()
    value = value_containers.ValueFloat(9.9)
    assert len(vm.stack) == 0
    instructions.keywords['fpush'](value).execute(vm)
    assert vm.pc == VM_PC_START + 1
    assert vm.stack[0] == value


def test_ins_iload():
    vm = make_vm()
    value = value_containers.ValueInt(99)
    vm.variables[0] = value
    assert len(vm.stack) == 0
    instructions.keywords['iload'](value_containers.ValueInt(0)).execute(vm)
    assert vm.pc == VM_PC_START + 1
    assert vm.stack[0] == value


def test_ins_fload():
    vm = make_vm()
    value = value_containers.ValueFloat(9.9)
    vm.variables[0] = value
    assert len(vm.stack) == 0
    instructions.keywords['fload'](value_containers.ValueInt(0)).execute(vm)
    assert vm.pc == VM_PC_START + 1
    assert vm.stack[0] == value


def test_ins_istore():
    ins = instructions.keywords['istore']
    vm = make_vm()
    value = value_containers.ValueInt(99)
    vm.stack_push(value)
    ins(value_containers.ValueInt(0)).execute(vm)
    assert vm.variables[0] == value
    assert vm.pc == VM_PC_START + 1
    assert len(vm.stack) == 0


def test_ins_fstore():
    ins = instructions.keywords['fstore']
    vm = make_vm()
    value = value_containers.ValueFloat(9.9)
    vm.stack_push(value)
    ins(value_containers.ValueInt(0)).execute(vm)
    assert vm.variables[0] == value
    assert vm.pc == VM_PC_START + 1
    assert len(vm.stack) == 0


def test_ins_goto():
    ins = instructions.keywords['goto']
    vm = make_vm()
    ins(value_containers.ValueInt(8)).execute(vm)
    assert vm.pc == 8


def test_ins_ireturn():
    ins = instructions.keywords['ireturn']
    vm = make_vm()
    value = value_containers.ValueInt(99)
    vm.stack_push(value)
    ins().execute(vm)
    assert vm.pc == VM_PC_START
    assert vm.finished is True
    assert vm.return_value == value


def test_ins_freturn():
    ins = instructions.keywords['freturn']
    vm = make_vm()
    value = value_containers.ValueFloat(9.9)
    vm.stack_push(value)
    ins().execute(vm)
    assert vm.pc == VM_PC_START
    assert vm.finished is True
    assert vm.return_value == value


def test_ins_nop():
    vm = make_vm()
    instructions.keywords['nop']().execute(vm)
    assert vm.pc == VM_PC_START + 1
    assert len(vm.stack) == 0


def test_ins_pop():
    vm = make_vm()
    vm.stack_push(value_containers.ValueInt(99))
    assert len(vm.stack) == 1
    instructions.keywords['pop']().execute(vm)
    assert vm.pc == VM_PC_START + 1
    assert len(vm.stack) == 0


def test_ins_dup():
    vm = make_vm()
    vm.stack_push(value_containers.ValueInt(99))
    assert len(vm.stack) == 1
    instructions.keywords['dup']().execute(vm)
    assert vm.pc == VM_PC_START + 1
    assert len(vm.stack) == 2
    assert vm.stack[0].__class__ == vm.stack[1].__class__
    assert vm.stack[0].value == vm.stack[1].value


def test_ins_swap():
    vm = make_vm()
    vm.stack_push(value_containers.ValueInt(99))
    vm.stack_push(value_containers.ValueFloat(5.5))
    assert len(vm.stack) == 2
    assert isinstance(vm.stack[0], value_containers.ValueInt)
    assert isinstance(vm.stack[1], value_containers.ValueFloat)
    assert vm.stack[0].value == 99
    assert vm.stack[1].value == 5.5
    instructions.keywords['swap']().execute(vm)
    assert vm.pc == VM_PC_START + 1
    assert len(vm.stack) == 2
    assert isinstance(vm.stack[1], value_containers.ValueInt)
    assert isinstance(vm.stack[0], value_containers.ValueFloat)
    assert vm.stack[1].value == 99
    assert vm.stack[0].value == 5.5


def test_ins_if_icmpeq():
    ins = instructions.keywords['if_icmpeq']
    vm = make_vm()
    vm.stack_push(value_containers.ValueInt(99))
    vm.stack_push(value_containers.ValueInt(99))
    assert len(vm.stack) == 2
    ins(value_containers.ValueInt(2)).execute(vm)
    assert vm.pc == 2
    assert len(vm.stack) == 0
    vm = make_vm()
    vm.stack_push(value_containers.ValueInt(99))
    vm.stack_push(value_containers.ValueInt(100))
    ins(value_containers.ValueInt(2)).execute(vm)
    assert vm.pc == VM_PC_START + 1


def test_ins_if_fcmpeq():
    ins = instructions.keywords['if_fcmpeq']
    vm = make_vm()
    vm.stack_push(value_containers.ValueFloat(9.9))
    vm.stack_push(value_containers.ValueFloat(9.9))
    assert len(vm.stack) == 2
    ins(value_containers.ValueInt(2)).execute(vm)
    assert vm.pc == 2
    assert len(vm.stack) == 0
    vm = make_vm()
    vm.stack_push(value_containers.ValueFloat(9.9))
    vm.stack_push(value_containers.ValueFloat(9.91))
    ins(value_containers.ValueInt(2)).execute(vm)
    assert vm.pc == VM_PC_START + 1


def test_ins_if_icmpne():
    ins = instructions.keywords['if_icmpne']
    vm = make_vm()
    vm.stack_push(value_containers.ValueInt(99))
    vm.stack_push(value_containers.ValueInt(100))
    ins(value_containers.ValueInt(2)).execute(vm)
    assert vm.pc == 2


def test_ins_if_icmpge():
    ins = instructions.keywords['if_icmpge']
    vm = make_vm()
    vm.stack_push(value_containers.ValueInt(100))
    vm.stack_push(value_containers.ValueInt(99))
    vm.stack_push(value_containers.ValueInt(100))
    vm.stack_push(value_containers.ValueInt(100))
    ins(value_containers.ValueInt(2)).execute(vm)
    assert vm.pc == 2
    ins(value_containers.ValueInt(4)).execute(vm)
    assert vm.pc == 4


def test_ins_if_icmpgt():
    ins = instructions.keywords['if_icmpgt']
    vm = make_vm()
    vm.stack_push(value_containers.ValueInt(100))
    vm.stack_push(value_containers.ValueInt(99))
    ins(value_containers.ValueInt(2)).execute(vm)
    assert vm.pc == 2


def test_ins_if_icmple():
    ins = instructions.keywords['if_icmple']
    vm = make_vm()
    vm.stack_push(value_containers.ValueInt(100))
    vm.stack_push(value_containers.ValueInt(101))
    vm.stack_push(value_containers.ValueInt(100))
    vm.stack_push(value_containers.ValueInt(100))
    ins(value_containers.ValueInt(2)).execute(vm)
    assert vm.pc == 2
    ins(value_containers.ValueInt(4)).execute(vm)
    assert vm.pc == 4


def test_ins_if_icmplt():
    ins = instructions.keywords['if_icmple']
    vm = make_vm()
    vm.stack_push(value_containers.ValueInt(100))
    vm.stack_push(value_containers.ValueInt(101))
    ins(value_containers.ValueInt(2)).execute(vm)
    assert vm.pc == 2


def test_ins_ifnonnull():
    vm = make_vm()
    vm.stack_push(value_containers.ValueInt(100))
    instructions.keywords['ifnonnull'](value_containers.ValueInt(2)).execute(vm)
    assert vm.pc == 2


def test_ins_ifnull():
    vm = make_vm()
    vm.stack_push(value_containers.ValueInt())
    instructions.keywords['ifnull'](value_containers.ValueInt(2)).execute(vm)
    assert vm.pc == 2


def test_ins_iadd():
    ins = instructions.keywords['iadd']
    vm = make_vm()
    vm.stack_push(value_containers.ValueInt(100))
    vm.stack_push(value_containers.ValueInt(101))
    ins().execute(vm)
    assert vm.pc == VM_PC_START + 1
    assert vm.stack[0] == value_containers.ValueInt(201)


def test_ins_isub():
    ins = instructions.keywords['isub']
    vm = make_vm()
    vm.stack_push(value_containers.ValueInt(100))
    vm.stack_push(value_containers.ValueInt(101))
    ins().execute(vm)
    assert vm.stack[0] == value_containers.ValueInt(-1)


def test_ins_imul():
    ins = instructions.keywords['imul']
    vm = make_vm()
    vm.stack_push(value_containers.ValueInt(100))
    vm.stack_push(value_containers.ValueInt(101))
    ins().execute(vm)
    assert vm.stack[0] == value_containers.ValueInt(10100)


def test_ins_idiv():
    ins = instructions.keywords['idiv']
    vm = make_vm()
    vm.stack_push(value_containers.ValueInt(55))
    vm.stack_push(value_containers.ValueInt(10))
    ins().execute(vm)
    assert vm.stack[0] == value_containers.ValueInt(5)
    vm.stack_push(value_containers.ValueFloat(9.9))
    vm.stack_push(value_containers.ValueFloat(9.9))
    pytest.raises(TypeError, ins().execute, vm)


def test_ins_fdiv():
    ins = instructions.keywords['fdiv']
    vm = make_vm()
    vm.stack_push(value_containers.ValueFloat(55.0))
    vm.stack_push(value_containers.ValueFloat(10.0))
    ins().execute(vm)
    assert vm.stack[0] == value_containers.ValueFloat(5.5)
    vm.stack_push(value_containers.ValueInt(9))
    vm.stack_push(value_containers.ValueInt(9))
    pytest.raises(TypeError, ins().execute, vm)


def test_ins_i2f():
    ins = instructions.keywords['i2f']
    vm = make_vm()
    vm.stack_push(value_containers.ValueInt(55))
    ins().execute(vm)
    assert vm.stack[0] == value_containers.ValueFloat(55.0)


def test_ins_f2i():
    ins = instructions.keywords['f2i']
    vm = make_vm()
    vm.stack_push(value_containers.ValueFloat(9.9))
    ins().execute(vm)
    assert vm.stack[0] == value_containers.ValueInt(9)


def test_newarray():
    ins = instructions.keywords['newarray']
    vm = make_vm()
    vm.stack_push(value_containers.ValueInt(10))
    ins(value_containers.ValueInt(1)).execute(vm)
    assert vm.stack_pop().__class__ == value_containers.ValueFloatArrayRef


def test_aload():
    ins = instructions.keywords['aload']
    vm = make_vm()
    arr = value_containers.ValueIntArrayRef()
    vm.variables[4] = arr
    ins(value_containers.ValueInt(4)).execute(vm)
    assert vm.stack_pop() == arr


def test_astore():
    ins = instructions.keywords['astore']
    vm = make_vm()
    arr = value_containers.ValueIntArrayRef()
    vm.stack_push(arr)
    ins(value_containers.ValueInt(4)).execute(vm)
    assert vm.variables[4] == arr


def test_iaload():
    vt = value_containers.ValueInt
    ins = instructions.keywords['iaload']
    vm = make_vm()
    arr = value_containers.ValueIntArrayRef()
    arr.allocate(10)
    arr[2] = value_containers.ValueInt(4)
    vm.stack_push(arr)
    vm.stack_push(value_containers.ValueInt(2))
    ins().execute(vm)
    assert vm.stack_pop() == vt(4)
    vm.stack_push(arr)
    vm.stack_push(value_containers.ValueInt(1))
    ins().execute(vm)
    sv = vm.stack_pop()
    assert sv.is_none
    assert sv.__class__ == vt


def test_faload():
    vt = value_containers.ValueFloat
    ins = instructions.keywords['faload']
    vm = make_vm()
    arr = value_containers.ValueFloatArrayRef()
    arr.allocate(10)
    arr[2] = value_containers.ValueFloat(4.0)
    vm.stack_push(arr)
    vm.stack_push(value_containers.ValueInt(2))
    ins().execute(vm)
    assert vm.stack_pop() == vt(4.0)
    vm.stack_push(arr)
    vm.stack_push(value_containers.ValueInt(1))
    ins().execute(vm)
    sv = vm.stack_pop()
    assert sv.is_none
    assert sv.__class__ == vt


def test_iastore():
    vt = value_containers.ValueInt
    ins = instructions.keywords['iastore']
    vm = make_vm()
    arr = value_containers.ValueIntArrayRef()
    arr.allocate(10)
    arr[2] = value_containers.ValueInt(4)
    vm.stack_push(arr)
    vm.stack_push(value_containers.ValueInt(0))
    vm.stack_push(value_containers.ValueInt(5))
    ins().execute(vm)
    assert arr[0] == vt(5)
    assert arr[1].is_none
    assert arr[1].__class__ == vt


def test_fastore():
    vt = value_containers.ValueFloat
    ins = instructions.keywords['fastore']
    vm = make_vm()
    arr = value_containers.ValueFloatArrayRef()
    arr.allocate(10)
    arr[2] = value_containers.ValueFloat(4.0)
    vm.stack_push(arr)
    vm.stack_push(value_containers.ValueInt(0))
    vm.stack_push(value_containers.ValueFloat(5.0))
    ins().execute(vm)
    assert arr[0] == vt(5.0)
    assert arr[1].is_none
    assert arr[1].__class__ == vt


def test_ins_array_length():
    ins = instructions.keywords['arraylength']
    vm = make_vm()
    value = value_containers.ValueFloatArrayRef()
    value.allocate(10)
    value[2] = value_containers.ValueFloat(4.0)
    vm.stack_push(value)
    ins().execute(vm)
    assert vm.pc == VM_PC_START + 1
    v = vm.stack_pop()
    assert v == value_containers.ValueInt(10)
    pytest.raises(RuntimeException, ins().execute, vm)


def test_ins_areturn():
    ins = instructions.keywords['areturn']
    vm = make_vm()
    value = value_containers.ValueFloatArrayRef()
    value.allocate(10)
    value[2] = value_containers.ValueFloat(4.0)
    vm.stack_push(value)
    ins().execute(vm)
    assert vm.pc == VM_PC_START
    assert vm.finished is True
    assert vm.return_value == value
