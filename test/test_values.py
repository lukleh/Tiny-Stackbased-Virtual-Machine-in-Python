# -*- coding: utf-8  -*-

import pytest

from vm.exceptions import ValueException
from vm.values import ValueFloat, ValueInt, ArrayObjectRef, ValueIntArrayRef


def test_eq():
    assert ValueInt() == ValueInt()
    assert ValueInt(10) == ValueInt(10)
    assert ValueFloat() == ValueFloat()
    assert ValueFloat(1/3) == ValueFloat(1/3)
    assert ValueInt(3) != ValueInt(6)
    assert ValueFloat(4.5) != ValueFloat(7.0)
    ar = ValueIntArrayRef([ValueInt(2), ValueInt(5)])
    ar2 = ValueIntArrayRef([ValueInt(2), ValueInt(5)])
    assert ar == ar2


def test_array_object():
    ar = ValueIntArrayRef()
    ar.allocate(10)
    ar[0] = ValueInt(5)
    assert ar[0] == ValueInt(5)
    assert ar[1] == ValueInt()
    pytest.raises(ValueException, ar.__setitem__, 4, 6)


def test_value_int():
    vs = ValueInt()
    assert vs.is_none
    vs = ValueInt(99)
    assert vs.value == 99
    pytest.raises(ValueException, ValueInt, '99')


def test_value_float():
    vs = ValueFloat()
    assert vs.is_none
    vs = ValueFloat(1/3)
    assert vs.value == 1/3
    pytest.raises(ValueException, ValueFloat, '99')