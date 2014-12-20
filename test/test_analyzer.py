# -*- coding: utf-8  -*-

import fixtures

from TSBVMIP import instructions
from TSBVMIP import values
from TSBVMIP.yparser import Code, parse_string
from TSBVMIP.analysis import analyzer


class TControlGraph():
    def add_connection(self, e1, e2):
        pass


def test_flow_instructions():
    # make sure no instruction fall through
    for name, i in instructions.keywords.items():
        c = Code()
        anz = analyzer.Analyzer()
        if issubclass(i, instructions.InsGoto):
            c.instructions.append(i(values.ValueInt(3)))
            c.instructions.append(instructions.InsNop())
            c.instructions.append(instructions.InsNop())
            c.instructions.append(instructions.InsNop())
            anz.analyze_control(c)
            assert anz.basic_blocks == [[0], [1, 2], [3]]
        elif issubclass(i, instructions.InsBranch):
            c.instructions.append(instructions.InsNop())
            c.instructions.append(i(values.ValueInt(0)))
            anz.analyze_control(c)
            assert anz.basic_blocks == [[0, 1]]
        elif not issubclass(i, instructions.InsReturn):
            if issubclass(i, instructions.InsNoArgument):
                c.instructions.append(i())
            elif issubclass(i, instructions.InsArgInteger):
                c.instructions.append(i(values.ValueInt(1)))
            elif issubclass(i, instructions.InsArgFloat):
                c.instructions.append(i(values.ValueFloat(5.0)))
            else:
                assert False
            anz.analyze_control(c)
            assert anz.basic_blocks == [[0]]
        elif issubclass(i, instructions.InsReturn):
            c.instructions.append(i())
            anz.analyze_control(c)
            assert anz.basic_blocks == [[0]]
        else:
            assert False


def test_basic_block_simple():
    c = Code()
    c.instructions = [
        instructions.InsIPush(values.ValueInt(1)),
        instructions.InsIReturn()
    ]
    anz = analyzer.Analyzer()
    anz.analyze_control(c)
    assert len(anz.basic_blocks) == 1
    assert anz.basic_blocks == [[0, 1]]


def test_basic_block_complex():
    c = parse_string(fixtures.load('sum.code'))
    anz = analyzer.Analyzer()
    anz.analyze_control(c)
    assert len(anz.basic_blocks) == 4
    assert anz.basic_blocks == [[0, 1, 2, 3], [4, 5, 6, 7, 8, 9], [10, 11, 12, 13, 14, 15], [16, 17]]

    c = parse_string(fixtures.load('bubblesort.code'))
    anz = analyzer.Analyzer()
    anz.analyze_control(c)
    assert len(anz.basic_blocks) == 7
    assert anz.basic_blocks == [[0, 1, 2],
                                [3, 4, 5, 6],
                                [7, 8, 9, 10, 11, 12],
                                [13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23],
                                [24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41,
                                 42, 43, 44, 45, 46],
                                [47, 48, 49],
                                [50, 51]]


def test_basic_block_oneblock():
    c = Code()
    anz = analyzer.Analyzer()
    c.instructions.append(instructions.InsNop())
    c.instructions.append(instructions.InsNop())
    c.instructions.append(instructions.InsNop())
    anz.analyze_control(c)
    assert anz.basic_blocks == [[0, 1, 2]]


def test_basic_block_onejumpback():
    c = Code()
    anz = analyzer.Analyzer()
    c.instructions.append(instructions.InsNop())
    c.instructions.append(instructions.InsNop())
    c.instructions.append(instructions.InsNop())
    c.instructions.append(instructions.InsGoto(values.ValueInt(0)))
    c.instructions.append(instructions.InsNop())
    anz.analyze_control(c)
    assert anz.basic_blocks == [[0, 1, 2, 3], [4]]


def test_basic_block_onejumpforward():
    c = Code()
    anz = analyzer.Analyzer()
    c.instructions.append(instructions.InsGoto(values.ValueInt(3)))
    c.instructions.append(instructions.InsNop())
    c.instructions.append(instructions.InsNop())
    c.instructions.append(instructions.InsNop())
    c.instructions.append(instructions.InsNop())
    anz.analyze_control(c)
    assert anz.basic_blocks == [[0], [1, 2], [3, 4]]