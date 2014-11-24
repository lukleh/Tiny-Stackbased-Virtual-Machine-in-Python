# -*- coding: utf-8  -*-
import pytest

import fixtures
from vm import parser
from vm import instructions
from vm import values
from vm.exceptions import ParserException, InstructionException


def test_skip_no_code():
    assert len(list(parser.tokenize_string(""))) == 0
    assert len(list(parser.tokenize_string(fixtures.load("tokenizer_blank_lines.code")))) == 0
    assert len(list(parser.tokenize_string(fixtures.load("tokenizer_comments.code")))) == 0
    assert len(list(parser.tokenize_string(fixtures.load("tokenizer_blank_lines_comments.code")))) == 0
    assert len(list(parser.tokenize_string(fixtures.load("tokenizer_blank_not_trivial.code")))) == 0


def test_args():
    for name, ins in instructions.keywords.items():
        if issubclass(ins, instructions.InsArgument):
            pytest.raises(InstructionException, ins)
            if issubclass(ins, instructions.InsArgNumber):
                assert ins(values.ValueInt(1)) is not None
                pytest.raises(InstructionException, ins, 'int')
                pytest.raises(InstructionException, ins, values.ValueInt())
            elif issubclass(ins, instructions.InsArgString):
                assert ins(values.ValueString('int')) is not None
                pytest.raises(InstructionException, ins, 1)
                pytest.raises(InstructionException, ins, values.ValueString())
        else:
            assert ins() is not None


def test_complete():
    tokens = parser.tokenize_string(fixtures.load("parse_ok.code"))
    assert len(list(tokens)) == 7


def test_code_local_var():
    c = parser.Code()
    c.add_local_var(instructions.InsVar(values.ValueString('int')))
    assert isinstance(c.get_var(0), values.ValueInt)
    c.add_local_var(instructions.InsVar(values.ValueString('float')))
    assert isinstance(c.get_var(1), values.ValueFloat)
    c.add_local_var(instructions.InsVar(values.ValueString('int')))
    c.add_local_var(instructions.InsVar(values.ValueString('int')))
    assert c.var_count == 4


def test_add_instruction():
    c = parser.Code()
    c.add_ins(instructions.keywords['ipush'](values.ValueInt(1)))
    assert isinstance(c.instructions[0], instructions.keywords['ipush'])
    assert c.instructions[0].argument.value == 1


def test_parse():
    tokens = parser.tokenize_string(fixtures.load("parse_ok.code"))
    code = parser.parse(tokens)
    assert isinstance(code, parser.Code)