# -*- coding: utf-8  -*-

import pytest

import vm.values as values
from vm.exceptions import ValueException


def test_value_string():
    vs = values.ValueString()
    assert vs.is_none
    vs = values.ValueString('hello')
    assert vs.value == 'hello'
    pytest.raises(ValueException, values.ValueString, 10)


def test_value_int():
    vs = values.ValueInt()
    assert vs.is_none
    vs = values.ValueInt(99)
    assert vs.value == 99
    pytest.raises(ValueException, values.ValueInt, '99')