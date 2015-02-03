# -*- coding: utf8 -*-


class Frame:

    def __init__(self, _method, _arguments):
        self.method = _method
        self.instructions = _method.code
        self.variables = _arguments
        self.stack = []
        self.pc = 0
        self.finished = False
        self.return_value = None
