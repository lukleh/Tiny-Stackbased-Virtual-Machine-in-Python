# -*- coding: utf-8  -*-

import pytest

from TSBVMIP.value_containers import ValueFloat, ValueInt, ValueIntArrayRef, ValueFloatArrayRef, ValueReference, convert_values


def test_eq():
    assert ValueInt() == ValueInt()
    assert ValueInt(10) == ValueInt(10)
    assert ValueFloat() == ValueFloat()
    assert ValueFloat(1 / 3) == ValueFloat(1 / 3)
    assert ValueInt(3) != ValueInt(6)
    assert ValueFloat(4.5) != ValueFloat(7.0)


def test_array_object():
    arr = ValueIntArrayRef()
    assert arr.is_none
    assert arr.length == 0
    pytest.raises(Exception, arr.allocate, 0)
    arr.allocate(10)
    arr[0] = ValueInt(5)
    assert arr[0] == ValueInt(5)
    assert arr[1] == ValueInt()


def test_value_int():
    vs = ValueInt()
    assert vs.is_none
    vs = ValueInt(99)
    assert vs.value == 99


def test_value_float():
    vs = ValueFloat()
    assert vs.is_none
    vs = ValueFloat(1 / 3)
    assert vs.value == 1 / 3


def test_math():
    assert (ValueInt(1) + ValueInt(2)) == ValueInt(3)
    assert (ValueInt(10) // ValueInt(3)) == ValueInt(3)
    assert (ValueFloat(10) / ValueFloat(5)) == ValueFloat(2.0)


def test_convert():
    assert convert_values(ValueInt, '1') == 1
    pytest.raises(Exception, convert_values, ValueInt, '1a')
    assert convert_values(ValueFloat, '1.5') == 1.5
    pytest.raises(Exception, convert_values, ValueFloat, '1a')
    assert convert_values(ValueIntArrayRef, [1, '2', 3]) == [ValueInt(1), ValueInt(2), ValueInt(3)]
    pytest.raises(Exception, convert_values, ValueIntArrayRef, '1a')
    assert convert_values(ValueFloatArrayRef, [1, '2.0', 3]) == [ValueFloat(1.0), ValueFloat(2.0), ValueFloat(3.0)]
    pytest.raises(Exception, convert_values, ValueFloatArrayRef, '1a')
    pytest.raises(Exception, convert_values, ValueReference, [1, 2])
