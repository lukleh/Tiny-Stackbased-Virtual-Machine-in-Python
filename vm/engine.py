# -*- coding: utf-8  -*-
import itertools
import logging as log

import vm.parser as parse
from vm.exceptions import RuntimeException


log.basicConfig(format='%(levelname)s %(message)s', level=log.DEBUG)


class VM:
    def __init__(self, code=None):
        self.code = code
        self.local_vars = []
        self.stack = []
        self.pc = 0
        self.finished = False
        self.return_value = None

    def stack_push(self, v):
        self.stack.append(v)

    def stack_pop(self):
        return self.stack.pop()

    def load_file_code(self, fname):
        tokens = parse.tokenize_file(fname)
        self.code = parse.parse(tokens)

    def load_string_code(self, fname):
        tokens = parse.tokenize_string(fname)
        self.code = parse.parse(tokens)

    def check_arguments_count(self, args):
        if len(args) != self.code.argument_count:
            raise RuntimeException('number of function arguments (%s) does not match number of passed arguments (%s)' %
                                   (self.code.argument_count, len(args)))

    def assign_arguments(self, args):
        self.check_arguments_count(args)
        self.local_vars = []
        for arg_value, loc_var in itertools.zip_longest(args, self.code.local_vars):
            if loc_var is None:
                raise RuntimeException('more args than local vars')
            if arg_value is not None:
                if not loc_var.validatevalue(arg_value):
                    raise RuntimeException(
                        'argument %s does not match type %s' % (arg_value.__class__, loc_var.__class__))
                self.local_vars.append(loc_var.__class__(arg_value))
            else:
                self.local_vars.append(loc_var.__class__())

    def run(self, *args):
        log.info('{!s:<15}{}'.format('args', len(args)))
        log.info('{!s:<15}{}'.format('local vars', len(self.code.local_vars)))
        log.info('{!s:<15}{}'.format('instructions', len(self.code.instructions)))
        self.assign_arguments(args)
        while not self.finished:
            if self.pc < 0:
                raise RuntimeException('instruction pointer less than zero')
            if self.pc >= len(self.code.instructions):
                raise RuntimeException('instruction pointer more than code')
            ins = self.code.instructions[self.pc]
            log.info("{!s:<7}{!s:<28}{}".format(self.pc, ins, self.stack))
            self.execute_instruction(ins)
        return self.return_value

    def convert_args(self, args):
        self.check_arguments_count(args)
        cargs = []
        for i in range(self.code.argument_count):
            lv = self.code.local_vars[i]
            try:
                cargs.append(lv.convertvalue(args[i]))
            except ValueError:
                raise RuntimeException(
                    'cannot convert argument at possition {0} value:{1} to {2}'.format(i, args[i], lv.vtype))
        return cargs

    def execute_instruction(self, ins):
        ins.execute(self)