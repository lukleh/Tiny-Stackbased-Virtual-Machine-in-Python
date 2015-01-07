# -*- coding: utf-8  -*-
import sys
if sys.version_info[0] != 3:
    raise Exception('need Python 3k to run')

import itertools
import logging as log

from . import value_containers
from .code_parser import parse_file, parse_string
from .exceptions import RuntimeException
from .analysis.verifier import Verifier
from .analysis.interpreter import BasicVerifier


log.basicConfig(format='%(levelname)s %(message)s', level=log.DEBUG)


class VM:

    def __init__(self, code=None):
        self.code = code
        self.variables = []
        self.stack = []
        self.pc = 0
        self.finished = False
        self.return_value = None

    def stack_push(self, v):
        self.stack.append(v)

    def stack_pop(self):
        try:
            return self.stack.pop()
        except IndexError:
            raise RuntimeException('stack is empty, cannot pop value')

    def verify(self):
        ver = Verifier(BasicVerifier())
        ver.verify(self.code)

    def load_file_code(self, fname):
        self.code = parse_file(fname)

    def load_string_code(self, data):
        self.code = parse_string(data)

    def check_arguments_count(self, args):
        if len(args) != self.code.argument_count:
            raise RuntimeException('number of function arguments (%s) does not match number of passed arguments (%s)' %
                                   (self.code.argument_count, len(args)))

    def assign_arguments(self, args):
        """
        assign values from argument received to actual variables inside VM
        """
        self.check_arguments_count(args)
        self.variables = []
        for arg_value, loc_var in itertools.zip_longest(args, self.code.variables):
            if loc_var is None:
                raise RuntimeException('more args than local vars')
            lv = loc_var.copy()
            lv.set_value(arg_value)
            self.variables.append(lv)

    def run(self, *args):
        """
        main run loop
        expects ready arguments as produced from VM.convert_args
        iterates the instruction list and executes instruction on index self.pc
        """
        log.info('{!s:<15}{}'.format('args', len(args)))
        log.info('{!s:<15}{}'.format('local vars', len(self.code.variables)))
        log.info(
            '{!s:<15}{}'.format('instructions', len(self.code.instructions)))
        self.verify()
        self.assign_arguments(args)
        while not self.finished:
            if self.pc < 0:
                raise RuntimeException('instruction pointer less than zero')
            if self.pc >= len(self.code.instructions):
                raise RuntimeException('instruction pointer longer than code')
            ins = self.code.instructions[self.pc]
            log.info(
                "pc {!s:<7}{!s:<28}stack {}".format(self.pc, ins, self.stack))
            ins.execute(self)
        return self.return_value

    @property
    def args_types(self):
        """
        yield arguments types as defined in code source

        """
        for i in range(self.code.argument_count):
            yield self.code.variables[i].vtype

    def convert_args(self, args):
        """
        covert argument values into form that can be accepted by Value* classes
        """
        self.check_arguments_count(args)
        cargs = []
        for i in range(self.code.argument_count):
            lv = self.code.variables[i]
            try:
                cargs.append(value_containers.convert_values(lv, args[i]))
            except ValueError:
                raise RuntimeException('cannot convert argument at possition {0} value:{1} to {2}'.format(i, args[i], lv.vtype))
        return cargs
