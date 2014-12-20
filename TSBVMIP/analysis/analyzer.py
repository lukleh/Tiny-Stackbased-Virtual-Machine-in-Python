# -*- coding: utf-8  -*-

from ..instructions import InsBranch, InsGoto


class Analyzer():

    def __init__(self):
        self.basic_blocks = []
        self.jump_target = set()

    def analyze_control(self, codeobj):
        for i, ins in enumerate(codeobj.instructions):
            if isinstance(ins, InsGoto) or isinstance(ins, InsBranch):
                self.jump_target.add(ins.argument.value)
        self.scan_basic_blocks(codeobj)

    def scan_basic_blocks(self, codeobj):
        bb = []
        for i, ins in enumerate(codeobj.instructions):
            if isinstance(ins, InsGoto) or isinstance(ins, InsBranch):
                bb.append(i)
                self.basic_blocks.append(bb)
                bb = []
            elif i in self.jump_target:
                if bb:
                    self.basic_blocks.append(bb)
                bb = [i]
            else:
                bb.append(i)

        if bb:
            self.basic_blocks.append(bb)
        return self.basic_blocks


