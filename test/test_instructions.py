# -*- coding: utf8 -*-
import pytest

import vm.values as values
import vm.instructions as instructions
import vm.engine as engine
from vm.parser import Code


def make_vm(local_vars=None, ins=None, args=None):
    if not args:
        args = []
    if not ins:
        ins = []
    if not local_vars:
        local_vars = []
    c = Code()
    for lv in local_vars:
        c.add_local_var(lv)
    for it in ins:
        c.add_ins(it)
    vm = engine.VM(c)
    vm.assign_arguments(args)
    return vm


def test_ins_push():
    vm = make_vm()
    value = values.ValueInt(99)
    assert len(vm.stack) == 0
    instructions.keywords['ipush'](value).execute(vm)
    assert vm.pc == 1
    assert vm.stack[0] == value


def test_ins_load():
    vm = make_vm(local_vars=[instructions.InsVar(values.ValueString('int'))])
    value = values.ValueInt(99)
    vm.local_vars[0] = value
    assert len(vm.stack) == 0
    instructions.keywords['iload'](values.ValueInt(0)).execute(vm)
    assert vm.pc == 1
    assert vm.stack[0] == value


def test_ins_store():
    vm = make_vm(local_vars=[instructions.InsVar(values.ValueString('int'))])
    value = values.ValueInt(99)
    vm.stack_push(value)
    instructions.keywords['istore'](values.ValueInt(0)).execute(vm)
    assert vm.local_vars[0] == value
    assert vm.pc == 1
    assert len(vm.stack) == 0


def test_ins_goto():
    inst = instructions.keywords['istore'](values.ValueInt(0))
    vm = make_vm(ins=[inst, inst, inst])
    assert vm.pc == 0
    instructions.keywords['goto'](values.ValueInt(1)).execute(vm)
    assert vm.pc == 1


def test_ins_return():
    vm = make_vm()
    value = values.ValueInt(99)
    vm.stack_push(value)
    instructions.keywords['ireturn']().execute(vm)
    assert vm.pc == 1
    assert vm.finished is True
    assert vm.return_value == value


def test_ins_nop():
    vm = make_vm()
    instructions.keywords['nop']().execute(vm)
    assert vm.pc == 1
    assert len(vm.stack) == 0


def test_ins_pop():
    vm = make_vm()
    vm.stack_push(values.ValueInt(99))
    assert len(vm.stack) == 1
    instructions.keywords['pop']().execute(vm)
    assert vm.pc == 1
    assert len(vm.stack) == 0


def test_ins_dup():
    vm = make_vm()
    vm.stack_push(values.ValueInt(99))
    assert len(vm.stack) == 1
    instructions.keywords['dup']().execute(vm)
    assert vm.pc == 1
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
    assert vm.pc == 1
    assert len(vm.stack) == 2
    assert isinstance(vm.stack[1], values.ValueInt)
    assert isinstance(vm.stack[0], values.ValueFloat)
    assert vm.stack[1].value == 99
    assert vm.stack[0].value == 5.5


def test_ins_if_cmpeq():
    vm = make_vm()
    vm.stack_push(values.ValueInt(99))
    vm.stack_push(values.ValueInt(99))
    assert len(vm.stack) == 2
    instructions.keywords['if_icmpeq'](values.ValueInt(2)).execute(vm)
    assert vm.pc == 2
    assert len(vm.stack) == 0
    vm = make_vm()
    vm.stack_push(values.ValueInt(99))
    vm.stack_push(values.ValueInt(100))
    instructions.keywords['if_icmpeq'](values.ValueInt(2)).execute(vm)
    assert vm.pc == 1


def test_ins_if_cmpne():
    vm = make_vm()
    vm.stack_push(values.ValueInt(99))
    vm.stack_push(values.ValueInt(100))
    instructions.keywords['if_icmpne'](values.ValueInt(2)).execute(vm)
    assert vm.pc == 2


def test_ins_if_cmpge():
    vm = make_vm()
    vm.stack_push(values.ValueInt(100))
    vm.stack_push(values.ValueInt(99))
    vm.stack_push(values.ValueInt(100))
    vm.stack_push(values.ValueInt(100))
    instructions.keywords['if_icmpge'](values.ValueInt(2)).execute(vm)
    assert vm.pc == 2
    instructions.keywords['if_icmpge'](values.ValueInt(2)).execute(vm)
    assert vm.pc == 4


def test_ins_if_cmpgt():
    vm = make_vm()
    vm.stack_push(values.ValueInt(100))
    vm.stack_push(values.ValueInt(99))
    instructions.keywords['if_icmpgt'](values.ValueInt(2)).execute(vm)
    assert vm.pc == 2


def test_ins_if_cmple():
    vm = make_vm()
    vm.stack_push(values.ValueInt(100))
    vm.stack_push(values.ValueInt(101))
    vm.stack_push(values.ValueInt(100))
    vm.stack_push(values.ValueInt(100))
    instructions.keywords['if_icmple'](values.ValueInt(2)).execute(vm)
    assert vm.pc == 2
    instructions.keywords['if_icmple'](values.ValueInt(2)).execute(vm)
    assert vm.pc == 4


def test_ins_if_cmplt():
    vm = make_vm()
    vm.stack_push(values.ValueInt(100))
    vm.stack_push(values.ValueInt(101))
    instructions.keywords['if_icmplt'](values.ValueInt(2)).execute(vm)
    assert vm.pc == 2


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


def test_ins_add():
    vm = make_vm()
    vm.stack_push(values.ValueInt(100))
    vm.stack_push(values.ValueInt(101))
    instructions.keywords['iadd']().execute(vm)
    assert vm.pc == 1
    assert vm.stack[0] == values.ValueInt(201)


def test_ins_sub():
    vm = make_vm()
    vm.stack_push(values.ValueInt(100))
    vm.stack_push(values.ValueInt(101))
    instructions.keywords['isub']().execute(vm)
    assert vm.stack[0] == values.ValueInt(-1)


def test_ins_mul():
    vm = make_vm()
    vm.stack_push(values.ValueInt(100))
    vm.stack_push(values.ValueInt(101))
    instructions.keywords['imul']().execute(vm)
    assert vm.stack[0] == values.ValueInt(10100)


def test_ins_div():
    vm = make_vm()
    vm.stack_push(values.ValueInt(55))
    vm.stack_push(values.ValueInt(10))
    instructions.keywords['idiv']().execute(vm)
    assert vm.stack[0] == values.ValueInt(5)
