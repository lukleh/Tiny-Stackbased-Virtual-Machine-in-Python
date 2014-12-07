# -*- coding: utf-8  -*-

import fixtures
import TSBVMIP.instructions as ins
from TSBVMIP import yparser as parser
from TSBVMIP.values import ValueFloat, ValueInt


def test_code():
    c = parser.Code(func={'name': 'n',
                          'args': [
                              {'type': 'int'},
                              {'type': 'float'}
                          ]},
                    lvars=[
                        {'type': 'int'},
                        {'type': 'float'}
                    ])
    assert c.var_count == 4


def test_func():
    p = parser.parse_string(fixtures.load('func.code'))
    assert p.function_name == 'multiple word name'
    assert p.var_count == 2
    assert p.argument_count == 2
    assert p.labels == {'a': 0}
    assert p.local_vars == [ValueInt(), ValueFloat()]


def test_variables():
    p = parser.parse_string(fixtures.load('variables.code'))
    assert p.var_count == 4
    assert p.argument_count == 1
    assert p.labels == {'x': 1, 'y': 3}
    assert p.local_vars == [ValueInt(), ValueInt(), ValueInt(), ValueFloat()]


def test_instructions():
    p = parser.parse_string(fixtures.load('instructions.code'))
    assert p.ins_count == 6
    assert p.instructions == [ins.InsIPush(ValueInt(10)),
                              ins.InsIPush(ValueInt(11)),
                              ins.InsIAdd(),
                              ins.InsIStore(ValueInt(0)),
                              ins.InsILoad(ValueInt(1)),
                              ins.InsIReturn()]

def test_whole():
    p = parser.parse_string(fixtures.load('parse_ok.code'))
    assert p