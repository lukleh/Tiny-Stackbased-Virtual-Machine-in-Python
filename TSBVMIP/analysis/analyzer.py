# -*- coding: utf-8  -*-

from collections import defaultdict

from ..instructions import InsJump, InsReturn


class FlowGraph():
    def __init__(self):
        self.v_out = defaultdict(list)
        self.v_in = defaultdict(list)
        self.basic_blocks = []
        self.ins_count = 0

    def add_connection(self, e1, e2):
        self.ins_count = max(self.ins_count, e2)
        self.v_out[e1].append(e2)
        self.v_in[e2].append(e1)

    def scan_basic_blocks(self):
        self.ins_count += 1
        bb = []
        for e1 in range(self.ins_count):
            if len(self.v_out[e1]) == 1:
                if len(self.v_in[e1]) < 2:
                    bb.append(e1)
                else:
                    if bb:
                        self.basic_blocks.append(bb)
                    bb = [e1]
            elif len(self.v_out[e1]) != 1:
                bb.append(e1)
                self.basic_blocks.append(bb)
                bb = []
        return self.basic_blocks


class Analyzer():

    def __init__(self):
        self.control_graph = FlowGraph()

    def analyze_control(self, codeobj):
        for i, ins in enumerate(codeobj.instructions):
            if isinstance(ins, InsJump):
                self.new_control_flow_edge(i, i + 1)
                self.new_control_flow_edge(i, ins.argument.value)
            elif not isinstance(ins, InsReturn):
                self.new_control_flow_edge(i, i + 1)
            else:
                # graph end, return instruction
                pass

    def new_control_flow_edge(self, ins_from, ins_to):
        self.control_graph.add_connection(ins_from, ins_to)