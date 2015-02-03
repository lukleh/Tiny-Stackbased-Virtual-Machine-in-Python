# -*- coding: utf8 -*-
import pytest

import TSBVMIP.value_containers as value_containers
import TSBVMIP.instructions as instructions
import TSBVMIP.engine as engine
import TSBVMIP.frame as frame
import TSBVMIP.code_parser as parser
from TSBVMIP.exceptions import InstructionException
from TSBVMIP.engine import VM


VM_PC_START = 10


def make_frame():
    method = parser.process_yaml(dict(func={'name': 'n',
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
    vm = engine.VM()
    vm.method = method
    conv_args = vm.convert_args([1, 1.0])
    cont_args = vm.contain_arguments(conv_args)
    frm = frame.Frame(method, cont_args)
    frm.pc = VM_PC_START  # shift pointer so we can check absolute jumps
    return frm


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
    frm = make_frame()
    value = value_containers.ValueInt(99)
    assert len(frm.stack) == 0
    VM.exec_frame(frm, instructions.keywords['ipush'](value))
    assert frm.pc == VM_PC_START + 1
    assert frm.stack[0] == value


def test_ins_fpush():
    frm = make_frame()
    value = value_containers.ValueFloat(9.9)
    assert len(frm.stack) == 0
    VM.exec_frame(frm, instructions.keywords['fpush'](value))
    assert frm.pc == VM_PC_START + 1
    assert frm.stack[0] == value


def test_ins_iload():
    frm = make_frame()
    value = value_containers.ValueInt(99)
    frm.variables[0] = value
    assert len(frm.stack) == 0
    VM.exec_frame(frm, instructions.keywords['iload'](value_containers.ValueInt(0)))
    assert frm.pc == VM_PC_START + 1
    assert frm.stack[0] == value


def test_ins_fload():
    frm = make_frame()
    value = value_containers.ValueFloat(9.9)
    frm.variables[0] = value
    assert len(frm.stack) == 0
    VM.exec_frame(frm, instructions.keywords['fload'](value_containers.ValueInt(0)))
    assert frm.pc == VM_PC_START + 1
    assert frm.stack[0] == value


def test_ins_istore():
    ins = instructions.keywords['istore']
    frm = make_frame()
    value = value_containers.ValueInt(99)
    frm.stack.append(value)
    VM.exec_frame(frm, ins(value_containers.ValueInt(0)))
    assert frm.variables[0] == value
    assert frm.pc == VM_PC_START + 1
    assert len(frm.stack) == 0


def test_ins_fstore():
    ins = instructions.keywords['fstore']
    frm = make_frame()
    value = value_containers.ValueFloat(9.9)
    frm.stack.append(value)
    VM.exec_frame(frm, ins(value_containers.ValueInt(0)))
    assert frm.variables[0] == value
    assert frm.pc == VM_PC_START + 1
    assert len(frm.stack) == 0


def test_ins_goto():
    ins = instructions.keywords['goto']
    frm = make_frame()
    VM.exec_frame(frm, ins(value_containers.ValueInt(8)))
    assert frm.pc == 8


def test_ins_ireturn():
    ins = instructions.keywords['ireturn']
    frm = make_frame()
    value = value_containers.ValueInt(99)
    frm.stack.append(value)
    VM.exec_frame(frm, ins())
    assert frm.pc == VM_PC_START + 1
    assert frm.finished is True
    assert frm.return_value == value


def test_ins_freturn():
    ins = instructions.keywords['freturn']
    frm = make_frame()
    value = value_containers.ValueFloat(9.9)
    frm.stack.append(value)
    VM.exec_frame(frm, ins())
    assert frm.pc == VM_PC_START + 1
    assert frm.finished is True
    assert frm.return_value == value


def test_ins_nop():
    frm = make_frame()
    VM.exec_frame(frm, instructions.keywords['nop']())
    assert frm.pc == VM_PC_START + 1
    assert len(frm.stack) == 0


def test_ins_pop():
    frm = make_frame()
    frm.stack.append(value_containers.ValueInt(99))
    assert len(frm.stack) == 1
    VM.exec_frame(frm, instructions.keywords['pop']())
    assert frm.pc == VM_PC_START + 1
    assert len(frm.stack) == 0


def test_ins_dup():
    frm = make_frame()
    frm.stack.append(value_containers.ValueInt(99))
    assert len(frm.stack) == 1
    VM.exec_frame(frm, instructions.keywords['dup']())
    assert frm.pc == VM_PC_START + 1
    assert len(frm.stack) == 2
    assert frm.stack[0].__class__ == frm.stack[1].__class__
    assert frm.stack[0].value == frm.stack[1].value


def test_ins_swap():
    frm = make_frame()
    frm.stack.append(value_containers.ValueInt(99))
    frm.stack.append(value_containers.ValueFloat(5.5))
    assert len(frm.stack) == 2
    assert isinstance(frm.stack[0], value_containers.ValueInt)
    assert isinstance(frm.stack[1], value_containers.ValueFloat)
    assert frm.stack[0].value == 99
    assert frm.stack[1].value == 5.5
    VM.exec_frame(frm, instructions.keywords['swap']())
    assert frm.pc == VM_PC_START + 1
    assert len(frm.stack) == 2
    assert isinstance(frm.stack[1], value_containers.ValueInt)
    assert isinstance(frm.stack[0], value_containers.ValueFloat)
    assert frm.stack[1].value == 99
    assert frm.stack[0].value == 5.5


def test_ins_if_icmpeq():
    ins = instructions.keywords['if_icmpeq']
    frm = make_frame()
    frm.stack.append(value_containers.ValueInt(99))
    frm.stack.append(value_containers.ValueInt(99))
    assert len(frm.stack) == 2
    VM.exec_frame(frm, ins(value_containers.ValueInt(2)))
    assert frm.pc == 2
    assert len(frm.stack) == 0
    frm = make_frame()
    frm.stack.append(value_containers.ValueInt(99))
    frm.stack.append(value_containers.ValueInt(100))
    VM.exec_frame(frm, ins(value_containers.ValueInt(2)))
    assert frm.pc == VM_PC_START + 1


def test_ins_if_fcmpeq():
    ins = instructions.keywords['if_fcmpeq']
    frm = make_frame()
    frm.stack.append(value_containers.ValueFloat(9.9))
    frm.stack.append(value_containers.ValueFloat(9.9))
    assert len(frm.stack) == 2
    VM.exec_frame(frm, ins(value_containers.ValueInt(2)))
    assert frm.pc == 2
    assert len(frm.stack) == 0
    frm = make_frame()
    frm.stack.append(value_containers.ValueFloat(9.9))
    frm.stack.append(value_containers.ValueFloat(9.91))
    VM.exec_frame(frm, ins(value_containers.ValueInt(2)))
    assert frm.pc == VM_PC_START + 1


def test_ins_if_icmpne():
    ins = instructions.keywords['if_icmpne']
    frm = make_frame()
    frm.stack.append(value_containers.ValueInt(99))
    frm.stack.append(value_containers.ValueInt(100))
    VM.exec_frame(frm, ins(value_containers.ValueInt(2)))
    assert frm.pc == 2


def test_ins_if_icmpge():
    ins = instructions.keywords['if_icmpge']
    frm = make_frame()
    frm.stack.append(value_containers.ValueInt(100))
    frm.stack.append(value_containers.ValueInt(99))
    frm.stack.append(value_containers.ValueInt(100))
    frm.stack.append(value_containers.ValueInt(100))
    VM.exec_frame(frm, ins(value_containers.ValueInt(2)))
    assert frm.pc == 2
    VM.exec_frame(frm, ins(value_containers.ValueInt(4)))
    assert frm.pc == 4


def test_ins_if_icmpgt():
    ins = instructions.keywords['if_icmpgt']
    frm = make_frame()
    frm.stack.append(value_containers.ValueInt(100))
    frm.stack.append(value_containers.ValueInt(99))
    VM.exec_frame(frm, ins(value_containers.ValueInt(2)))
    assert frm.pc == 2


def test_ins_if_icmple():
    ins = instructions.keywords['if_icmple']
    frm = make_frame()
    frm.stack.append(value_containers.ValueInt(100))
    frm.stack.append(value_containers.ValueInt(101))
    frm.stack.append(value_containers.ValueInt(100))
    frm.stack.append(value_containers.ValueInt(100))
    VM.exec_frame(frm, ins(value_containers.ValueInt(2)))
    assert frm.pc == 2
    VM.exec_frame(frm, ins(value_containers.ValueInt(4)))
    assert frm.pc == 4


def test_ins_if_icmplt():
    ins = instructions.keywords['if_icmple']
    frm = make_frame()
    frm.stack.append(value_containers.ValueInt(100))
    frm.stack.append(value_containers.ValueInt(101))
    VM.exec_frame(frm, ins(value_containers.ValueInt(2)))
    assert frm.pc == 2


def test_ins_ifnonnull():
    frm = make_frame()
    frm.stack.append(value_containers.ValueInt(100))
    VM.exec_frame(frm, instructions.keywords['ifnonnull'](value_containers.ValueInt(2)))
    assert frm.pc == 2


def test_ins_ifnull():
    frm = make_frame()
    frm.stack.append(value_containers.ValueInt())
    VM.exec_frame(frm, instructions.keywords['ifnull'](value_containers.ValueInt(2)))
    assert frm.pc == 2


def test_ins_iadd():
    ins = instructions.keywords['iadd']
    frm = make_frame()
    frm.stack.append(value_containers.ValueInt(100))
    frm.stack.append(value_containers.ValueInt(101))
    VM.exec_frame(frm, ins())
    assert frm.pc == VM_PC_START + 1
    assert frm.stack[0] == value_containers.ValueInt(201)


def test_ins_isub():
    ins = instructions.keywords['isub']
    frm = make_frame()
    frm.stack.append(value_containers.ValueInt(100))
    frm.stack.append(value_containers.ValueInt(101))
    VM.exec_frame(frm, ins())
    assert frm.stack[0] == value_containers.ValueInt(-1)


def test_ins_imul():
    ins = instructions.keywords['imul']
    frm = make_frame()
    frm.stack.append(value_containers.ValueInt(100))
    frm.stack.append(value_containers.ValueInt(101))
    VM.exec_frame(frm, ins())
    assert frm.stack[0] == value_containers.ValueInt(10100)


def test_ins_idiv():
    ins = instructions.keywords['idiv']
    frm = make_frame()
    frm.stack.append(value_containers.ValueInt(55))
    frm.stack.append(value_containers.ValueInt(10))
    VM.exec_frame(frm, ins())
    assert frm.stack[0] == value_containers.ValueInt(5)
    frm.stack.append(value_containers.ValueFloat(9.9))
    frm.stack.append(value_containers.ValueFloat(9.9))
    pytest.raises(TypeError, ins().execute, frm)


def test_ins_fdiv():
    ins = instructions.keywords['fdiv']
    frm = make_frame()
    frm.stack.append(value_containers.ValueFloat(55.0))
    frm.stack.append(value_containers.ValueFloat(10.0))
    VM.exec_frame(frm, ins())
    assert frm.stack[0] == value_containers.ValueFloat(5.5)
    frm.stack.append(value_containers.ValueInt(9))
    frm.stack.append(value_containers.ValueInt(9))
    pytest.raises(TypeError, VM.exec_frame, frm, ins())


def test_ins_i2f():
    ins = instructions.keywords['i2f']
    frm = make_frame()
    frm.stack.append(value_containers.ValueInt(55))
    VM.exec_frame(frm, ins())
    assert frm.stack[0] == value_containers.ValueFloat(55.0)


def test_ins_f2i():
    ins = instructions.keywords['f2i']
    frm = make_frame()
    frm.stack.append(value_containers.ValueFloat(9.9))
    VM.exec_frame(frm, ins())
    assert frm.stack[0] == value_containers.ValueInt(9)


def test_newarray():
    ins = instructions.keywords['newarray']
    frm = make_frame()
    frm.stack.append(value_containers.ValueInt(10))
    VM.exec_frame(frm, ins(value_containers.ValueInt(1)))
    assert frm.stack.pop().__class__ == value_containers.ValueFloatArrayRef


def test_aload():
    ins = instructions.keywords['aload']
    frm = make_frame()
    arr = value_containers.ValueIntArrayRef()
    frm.variables[4] = arr
    VM.exec_frame(frm, ins(value_containers.ValueInt(4)))
    assert frm.stack.pop() == arr


def test_astore():
    ins = instructions.keywords['astore']
    frm = make_frame()
    arr = value_containers.ValueIntArrayRef()
    frm.stack.append(arr)
    VM.exec_frame(frm, ins(value_containers.ValueInt(4)))
    assert frm.variables[4] == arr


def test_iaload():
    vt = value_containers.ValueInt
    ins = instructions.keywords['iaload']
    frm = make_frame()
    arr = value_containers.ValueIntArrayRef()
    arr.allocate(10)
    arr[2] = value_containers.ValueInt(4)
    frm.stack.append(arr)
    frm.stack.append(value_containers.ValueInt(2))
    VM.exec_frame(frm, ins())
    assert frm.stack.pop() == vt(4)
    frm.stack.append(arr)
    frm.stack.append(value_containers.ValueInt(1))
    VM.exec_frame(frm, ins())
    sv = frm.stack.pop()
    assert sv.is_none
    assert sv.__class__ == vt


def test_faload():
    vt = value_containers.ValueFloat
    ins = instructions.keywords['faload']
    frm = make_frame()
    arr = value_containers.ValueFloatArrayRef()
    arr.allocate(10)
    arr[2] = value_containers.ValueFloat(4.0)
    frm.stack.append(arr)
    frm.stack.append(value_containers.ValueInt(2))
    VM.exec_frame(frm, ins())
    assert frm.stack.pop() == vt(4.0)
    frm.stack.append(arr)
    frm.stack.append(value_containers.ValueInt(1))
    VM.exec_frame(frm, ins())
    sv = frm.stack.pop()
    assert sv.is_none
    assert sv.__class__ == vt


def test_iastore():
    vt = value_containers.ValueInt
    ins = instructions.keywords['iastore']
    frm = make_frame()
    arr = value_containers.ValueIntArrayRef()
    arr.allocate(10)
    arr[2] = value_containers.ValueInt(4)
    frm.stack.append(arr)
    frm.stack.append(value_containers.ValueInt(0))
    frm.stack.append(value_containers.ValueInt(5))
    VM.exec_frame(frm, ins())
    assert arr[0] == vt(5)
    assert arr[1].is_none
    assert arr[1].__class__ == vt


def test_fastore():
    vt = value_containers.ValueFloat
    ins = instructions.keywords['fastore']
    frm = make_frame()
    arr = value_containers.ValueFloatArrayRef()
    arr.allocate(10)
    arr[2] = value_containers.ValueFloat(4.0)
    frm.stack.append(arr)
    frm.stack.append(value_containers.ValueInt(0))
    frm.stack.append(value_containers.ValueFloat(5.0))
    VM.exec_frame(frm, ins())
    assert arr[0] == vt(5.0)
    assert arr[1].is_none
    assert arr[1].__class__ == vt


def test_ins_array_length():
    ins = instructions.keywords['arraylength']
    frm = make_frame()
    value = value_containers.ValueFloatArrayRef()
    value.allocate(10)
    value[2] = value_containers.ValueFloat(4.0)
    frm.stack.append(value)
    VM.exec_frame(frm, ins())
    assert frm.pc == VM_PC_START + 1
    v = frm.stack.pop()
    assert v == value_containers.ValueInt(10)
    pytest.raises(IndexError, ins().execute, frm)


def test_ins_areturn():
    ins = instructions.keywords['areturn']
    frm = make_frame()
    value = value_containers.ValueFloatArrayRef()
    value.allocate(10)
    value[2] = value_containers.ValueFloat(4.0)
    frm.stack.append(value)
    VM.exec_frame(frm, ins())
    assert frm.pc == VM_PC_START + 1
    assert frm.finished is True
    assert frm.return_value == value
