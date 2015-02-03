# -*- coding: utf-8  -*-
import pytest

import fixtures

from TSBVMIP import value_containers
from TSBVMIP import engine, frame, method
from TSBVMIP.exceptions import RuntimeException


def test_empty_vm():
    frm = frame.Frame(method.Method([]), None)
    assert frm
    assert len(frm.stack) == 0
    assert frm.finished is False
    assert frm.return_value is None


def test_frame_stack():
    frm = frame.Frame(method.Method([]), None)
    frm.stack.append(10)
    assert len(frm.stack) == 1
    assert frm.stack[0] == 10
    assert frm.stack.pop() == 10
    assert len(frm.stack) == 0
    pytest.raises(IndexError, frm.stack.pop)


def test_ok():
    vm = engine.VM()
    vm.load_file_code(fixtures.full_path('parse_ok.code'))
    result = vm.run(1)
    assert result.value == 1
    assert result.__class__ is value_containers.ValueInt


def test_args():
    vm = engine.VM()
    vm.load_file_code(fixtures.full_path('parse_ok.code'))
    pytest.raises(RuntimeException, vm.run)
    pytest.raises(RuntimeException, vm.run, 1, 1)
