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
from .frame import Frame


log.basicConfig(format='%(levelname)s %(message)s', level=log.DEBUG)


class VM:

    def __init__(self):
        self.method = None
        self.frame = None

    def verify(self):
        ver = Verifier(BasicVerifier())
        ver.verify(self.method)

    def load_file_code(self, fname):
        self.method = parse_file(fname)

    def load_string_code(self, data):
        self.method = parse_string(data)

    def contain_arguments(self, args):
        """
        assign values from argument received to actual variables inside VM
        """
        self.check_arguments_count(args)
        variables = []
        for arg_value, loc_var in itertools.zip_longest(args, self.method.variables):
            if loc_var is None:
                raise RuntimeException('more args than local vars')
            lv = loc_var.copy()
            lv.set_value(arg_value)
            variables.append(lv)
        return variables

    def run(self, *args):
        """
        main run loop
        expects ready arguments as produced from VM.convert_args
        iterates the instruction list and executes instruction on index self.pc
        """
        log.info('{!s:<15}{}'.format('args', len(args)))
        log.info('{!s:<15}{}'.format('local vars', len(self.method.variables)))
        log.info(
            '{!s:<15}{}'.format('instructions', len(self.method.code)))
        self.verify()
        arguments = self.contain_arguments(args)
        self.frame = Frame(self.method, arguments)
        while not self.frame.finished:
            ins = self.frame.instructions[self.frame.pc]
            log.info(
                "pc {!s:<7}{!s:<28}stack {}".format(self.frame.pc, ins, self.frame.stack))
            self.exec_frame(self.frame, ins)
        return self.frame.return_value

    @classmethod
    def exec_frame(cls, frame, ins):
        ins.execute(frame)
        frame.pc += 1

    def run_cmd(self, cmd_args):
        pargs = []
        for i, _ in enumerate(self.args_types):
            name = 'arg%d' % i
            pargs.append(getattr(cmd_args, name))
        cargs = self.convert_args(pargs)
        return self.run(*cargs)

    @property
    def args_types(self):
        """
        yield arguments types as defined in code source

        """
        for i in range(self.method.argument_count):
            yield self.method.variables[i].vtype

    def check_arguments_count(self, args):
        if len(args) != self.method.argument_count:
            raise RuntimeException('number of function arguments (%s) does not match number of passed arguments (%s)' %
                                   (self.method.argument_count, len(args)))

    def convert_args(self, args):
        """
        covert argument values into form that can be accepted by Value* classes
        """
        self.check_arguments_count(args)
        cargs = []
        for i in range(self.method.argument_count):
            lv = self.method.variables[i]
            print(i, lv)
            try:
                cargs.append(value_containers.convert_values(lv, args[i]))
            except ValueError:
                raise RuntimeException('cannot convert argument at possition {0} value:{1} to {2}'.format(i, args[i], lv.vtype))
        return cargs
