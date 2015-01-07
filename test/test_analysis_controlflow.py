# -*- coding: utf-8  -*-

import fixtures

from TSBVMIP import instructions
from TSBVMIP import value_containers
from TSBVMIP.code_parser import parse_string
from TSBVMIP.code import Code
from TSBVMIP.analysis import controlflow
from TSBVMIP.analysis.controlflow import BasicBlock


def test_flow_instructions():
    # make sure no instruction fall through
    for name, i in instructions.keywords.items():
        c = Code()
        anz = controlflow.ControlFlowAnalyzer()
        if issubclass(i, instructions.InsGoto):
            c.instructions.append(i(value_containers.ValueInt(3)))
            c.instructions.append(instructions.InsNop())
            c.instructions.append(instructions.InsNop())
            c.instructions.append(instructions.InsNop())
            anz.analyze(c)
            assert anz.basic_blocks == [BasicBlock(instruction_indexes=[0], sucessors=[None]),
                                        BasicBlock(instruction_indexes=[1, 2], sucessors=[None]),
                                        BasicBlock(instruction_indexes=[3], predecessors=[None, None])]
        elif issubclass(i, instructions.InsBranch):
            c.instructions.append(instructions.InsNop())
            c.instructions.append(i(value_containers.ValueInt(0)))
            anz.analyze(c)
            assert anz.basic_blocks == [BasicBlock(instruction_indexes=[0, 1], sucessors=[None], predecessors=[None])]
        elif not issubclass(i, instructions.InsReturn):
            if issubclass(i, instructions.InsNoArgument):
                c.instructions.append(i())
            elif issubclass(i, instructions.InsArgInteger):
                c.instructions.append(i(value_containers.ValueInt(1)))
            elif issubclass(i, instructions.InsArgFloat):
                c.instructions.append(i(value_containers.ValueFloat(5.0)))
            else:
                assert False
            anz.analyze(c)
            assert anz.basic_blocks == [BasicBlock(instruction_indexes=[0])]
        elif issubclass(i, instructions.InsReturn):
            c.instructions.append(i())
            anz.analyze(c)
            assert anz.basic_blocks == [BasicBlock(instruction_indexes=[0])]
        else:
            assert False


def test_basic_block_simple():
    c = Code()
    c.instructions = [
        instructions.InsIPush(value_containers.ValueInt(1)),
        instructions.InsIReturn()
    ]
    anz = controlflow.ControlFlowAnalyzer()
    anz.analyze(c)
    assert len(anz.basic_blocks) == 1
    assert anz.basic_blocks == [BasicBlock(instruction_indexes=[0, 1])]


def test_basic_block_complex():
    c = parse_string(fixtures.load('sum.code'))
    anz = controlflow.ControlFlowAnalyzer()
    anz.analyze(c)
    assert len(anz.basic_blocks) == 4
    assert [bb.instruction_indexes for bb in anz.basic_blocks] == [
        [0, 1, 2, 3], [4, 5, 6, 7, 8, 9], [10, 11, 12, 13, 14, 15], [16, 17]]

    c = parse_string(fixtures.load('bubblesort.code'))
    anz = controlflow.ControlFlowAnalyzer()
    anz.analyze(c)
    assert len(anz.basic_blocks) == 7
    assert [bb.instruction_indexes for bb in anz.basic_blocks] == [[0, 1, 2],
                                                                   [3, 4, 5, 6],
                                                                   [7, 8, 9, 10, 11, 12, 13],
                                                                   [14, 15, 16, 17, 18, 19, 20, 21, 22],
                                                                   [23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35,
                                                                    36, 37, 38, 39, 40, 41,
                                                                    42, 43],
                                                                   [44, 45, 46],
                                                                   [47, 48]]


def test_basic_block_oneblock():
    c = Code()
    anz = controlflow.ControlFlowAnalyzer()
    c.instructions.append(instructions.InsNop())
    c.instructions.append(instructions.InsNop())
    c.instructions.append(instructions.InsNop())
    anz.analyze(c)
    assert anz.basic_blocks == [BasicBlock(instruction_indexes=[0, 1, 2])]


def test_basic_block_onejumpback():
    c = Code()
    anz = controlflow.ControlFlowAnalyzer()
    c.instructions.append(instructions.InsNop())
    c.instructions.append(instructions.InsNop())
    c.instructions.append(instructions.InsNop())
    c.instructions.append(instructions.InsGoto(value_containers.ValueInt(0)))
    c.instructions.append(instructions.InsNop())
    anz.analyze(c)
    assert anz.basic_blocks == [BasicBlock(instruction_indexes=[0, 1, 2, 3], sucessors=[None], predecessors=[None]),
                                BasicBlock(instruction_indexes=[4])]


def test_basic_block_onejumpforward():
    c = Code()
    anz = controlflow.ControlFlowAnalyzer()
    c.instructions.append(instructions.InsGoto(value_containers.ValueInt(3)))
    c.instructions.append(instructions.InsNop())
    c.instructions.append(instructions.InsNop())
    c.instructions.append(instructions.InsNop())
    c.instructions.append(instructions.InsNop())
    anz.analyze(c)
    assert anz.basic_blocks == [BasicBlock(instruction_indexes=[0], sucessors=[None]),
                                BasicBlock(instruction_indexes=[1, 2], sucessors=[None]),
                                BasicBlock(instruction_indexes=[3, 4], predecessors=[None, None])]
