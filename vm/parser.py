# -*- coding: utf-8  -*-
import re
import io

from vm import instructions
from vm import values
from vm.exceptions import ParserException


class Code():
    def __init__(self):
        self.local_vars = []
        self.instructions = []
        self.function_name = None
        self.argument_count = 0

    def add_function(self, ins):
        self.function_name = ins.argument.value

    def add_local_var(self, ins):
        self.local_vars.append(ins.argument)

    def add_argument(self, ins):
        self.argument_count += 1
        self.add_local_var(ins)

    def get_var(self, idx):
        return self.local_vars[idx]

    @property
    def var_count(self):
        return len(self.local_vars)

    def add_ins(self, ins):
        self.instructions.append(ins)


class Token():
    def __init__(self, line_number=None, line=None, instruction=None):
        self.line_number = line_number
        self.line = line
        self.instruction = instruction


def g_lines(data):
    for line_number, line in enumerate(data):
        yield Token(line_number=line_number, line=line.rstrip('\n'))
    if isinstance(data, io.IOBase):
        data.close()


def g_skip_no_data(data):
    for token in data:
        if re.match('^\s*$', token.line):
            continue
        elif re.match('^\s*;.*$', token.line):
            continue
        else:
            yield token
            
            
def format_error(msg, token):
    return "%s\nline %d %s" % (msg, token.line_number, token.line)


def g_tokenize(data):
    for token in data:
        m = re.match('\s*(\w+)', token.line)
        if not m:
            raise ParserException(format_error('could not recognize word', token))
        kw = m.group(1).lower()
        if kw not in instructions.keywords.keys():
            raise ParserException(format_error('"%s" not known keyword' % kw, token))
        ins_obj = instructions.keywords[kw]
        if issubclass(ins_obj, instructions.InsArgString):
            m = re.match('\s+(\w+)', token.line[m.end(1):])
            if not m:
                raise ParserException(format_error('expected string after %s' % kw, token))
            token.instruction = ins_obj(values.ValueString(m.group(1)))
        elif issubclass(ins_obj, instructions.InsArgNumber):
            m = re.match('\s+(\-?\d+)', token.line[m.end(1):])
            if not m:
                raise ParserException(format_error('expected number after %s' % kw, token))
            token.instruction = ins_obj(values.ValueInt(int(m.group(1))))
        elif issubclass(ins_obj, instructions.Instruction):
            token.instruction = ins_obj()
        else:
            raise ParserException(format_error('this should not happen', token))
        yield token


def get_tokens(imput):
    lines = g_lines(imput)
    no_empty = g_skip_no_data(lines)
    tokens = g_tokenize(no_empty)
    return tokens


def tokenize_string(data):
    return get_tokens(data.split('\n'))


def tokenize_file(fname):
    f = open(fname, 'r')
    return get_tokens(f)


def parse(tokens):
    code = Code()
    for i, t in enumerate(tokens):
        ins = t.instruction
        if ins.__class__ == instructions.InsFunc:
            if i != 0:
                raise ParserException(format_error('function must be as first instruction', t))
            code.add_function(ins)
        elif ins.__class__ == instructions.InsArg:
            code.add_argument(ins)
        elif ins.__class__ == instructions.InsVar:
            code.add_local_var(ins)
        else:
            code.add_ins(ins)
    return code