# -*- coding: utf-8  -*-

from collections import defaultdict

from ..instructions import InsBranch, InsGoto, InsReturn


class BasicBlock():

    def __init__(self, instruction_indexes=None, sucessors=None, predecessors=None):
        if not predecessors:
            predecessors = []
        if not sucessors:
            sucessors = []
        if not instruction_indexes:
            instruction_indexes = []
        self.instruction_indexes = instruction_indexes
        self.sucessors = sucessors
        self.predecessors = predecessors

    def __eq__(self, other):
        return self.instruction_indexes == other.instruction_indexes and \
            len(self.sucessors) == len(other.sucessors) and \
            len(self.predecessors) == len(other.predecessors)
        # one day we will need to compare also the connections

    def __str__(self):
        return "IDX%s, S%s, P%s" % (self.instruction_indexes, len(self.sucessors), len(self.predecessors))

    def __repr__(self):
        return self.__str__()

    def append(self, idx):
        self.instruction_indexes.append(idx)

    @property
    def is_empty(self):
        return len(self.instruction_indexes) == 0

    @property
    def end_inst_index(self):
        return self.instruction_indexes[-1]

    @property
    def start_inst_index(self):
        return self.instruction_indexes[0]


class ControlFlowAnalyzer():

    def __init__(self):
        self.basic_blocks = []
        self.jump_target = defaultdict(list)
        self.jump_source = defaultdict(list)

    def analyze(self, code):
        self.find_jump_points(code)
        self.scan_basic_blocks(code)
        self.connect_basic_blocks(code)
        return self.basic_blocks

    def find_jump_points(self, code):
        for i, ins in enumerate(code.instructions):
            if isinstance(ins, InsGoto) or isinstance(ins, InsBranch):
                self.jump_target[ins.argument.value].append(i)
                self.jump_source[i].append(ins.argument.value)
            if isinstance(ins, InsBranch):
                self.jump_target[i + 1].append(i)
                self.jump_source[i].append(i + 1)

    def scan_basic_blocks(self, code):
        bb = BasicBlock()
        for i, ins in enumerate(code.instructions):
            if i in self.jump_target:
                bb_prev = bb
                bb = BasicBlock()
                if not bb_prev.is_empty:
                    self.basic_blocks.append(bb_prev)
                    bb.predecessors.append(bb_prev)
                    bb_prev.sucessors.append(bb)
                bb.append(i)
            elif i in self.jump_source or isinstance(ins, InsReturn):
                bb.append(i)
                self.basic_blocks.append(bb)
                bb = BasicBlock()
            else:
                bb.append(i)

        if not bb.is_empty:
            self.basic_blocks.append(bb)

    def connect_basic_blocks(self, code):
        for bb in self.basic_blocks:
            if not isinstance(code.instructions[bb.end_inst_index], InsReturn):
                for source in self.jump_source[bb.end_inst_index]:
                    for bbb in self.basic_blocks:
                        if bbb.start_inst_index == source:
                            bb.sucessors.append(bbb)
            for target in self.jump_target[bb.start_inst_index]:
                for bbb in self.basic_blocks:
                    if bbb.end_inst_index == target:
                        bb.predecessors.append(bbb)
