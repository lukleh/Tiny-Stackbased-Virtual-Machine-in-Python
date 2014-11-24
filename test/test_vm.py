# -*- coding: utf-8  -*-
import pytest

import fixtures

from vm import values
from vm import engine
from vm.exceptions import RuntimeException


def test_empty_vm():
    vm = engine.VM()
    assert vm
    assert len(vm.stack) == 0
    assert vm.finished is False
    assert vm.return_value is None


def test_stack():
    vm = engine.VM()
    vm.stack_push(10)
    assert len(vm.stack) == 1
    assert vm.stack_pop() == 10
    assert len(vm.stack) == 0


def test_ok():
    vm = engine.VM()
    vm.load_file_code(fixtures.full_path('parse_ok.code'))
    result = vm.run(1)
    assert result.value == 1
    assert result.__class__ is values.ValueInt


def test_args():
    vm = engine.VM()
    vm.load_file_code(fixtures.full_path('parse_ok.code'))
    pytest.raises(RuntimeException, vm.run)
    pytest.raises(RuntimeException, vm.run, 1, 1)
    pytest.raises(RuntimeException, vm.run, 'a')