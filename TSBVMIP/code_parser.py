# -*- coding: utf-8  -*-
import yaml

from . import instructions
from . import value_containers
from .exceptions import ParserException
from .code import Code


def _process_func(code, func):
    if not func or not isinstance(func, dict):
        raise ParserException('"func" not defined')
    code.function_name = func['name']
    code.return_type = value_containers.types[func['type'].lower()]()
    _process_vars(code, func['args'], inc_arg_count=True)


def _process_vars(code, args, inc_arg_count=False):
    for arg in args:
        t = arg['type'].lower()
        if inc_arg_count:
            code.argument_count += 1
        code.variables.append(value_containers.types[t]())
        l = arg.get('label', None)
        code.add_label(l, code.var_count - 1)


def _process_ins(code, ins):
    # pass1
    offset = 0
    label = None
    label_current = None
    for i in ins:
        if isinstance(i, dict):
            if not len(i) == 1:
                raise ParserException('bad syntax for data %s' % i)
            label_current = i.get('label', None)
            if label and label_current:
                raise ParserException('label cannot follow label: %s, %s' % (label, label_current))
            label = label_current
        else:
            label = None
            label_current = None
        if label:
            code.add_label(label, offset)
        else:
            offset += 1
    else:
        if label:
            raise ParserException('label cannot be as last instruction %s' % i)

    # pass2
    offset = 0
    for i in ins:
        if isinstance(i, dict) and i.get('label', None):
            continue
        else:
            offset += 1
        if isinstance(i, str):
            inst = instructions.keywords[i.lower()]
            if not issubclass(inst, instructions.InsNoArgument):
                raise ParserException('instruction %s requires argument' % i)
            code.add_ins(inst())
        elif isinstance(i, dict):
            kw, value = i.popitem()
            inst = instructions.keywords[kw.lower()]
            if issubclass(inst, instructions.InsNoArgument):
                raise ParserException('instruction %s takes no argument' % i)
            if issubclass(inst, instructions.InsArgILabel):
                if isinstance(value, str):
                    try:
                        value = code.labels[value]
                    except KeyError:
                        raise ParserException('label %s is not defined' % value)
                else:
                    raise ParserException('instruction %s requires label as argument' % i)
            elif issubclass(inst, instructions.InsArgInteger):
                if value != int(value):
                    raise ParserException('instruction %s requires integer argument' % i)
            elif issubclass(inst, instructions.InsArgFloat):
                if value != float(value):
                    raise ParserException('instruction %s requires float argument' % i)

            code.add_ins(inst(instructions.contain_value(inst, value)))
        else:
            raise ParserException('unknown instruction format %s' % i)


def process_yaml(structure):
    c = Code()
    _process_func(c, structure.get('func', {}))
    _process_vars(c, structure.get('lvars', []))
    _process_ins(c, structure.get('ins', []))
    return c


def parse_string(data):
    structure = yaml.safe_load(data)
    return process_yaml(structure)


def parse_file(fname):
    with open(fname, 'r') as f:
        return parse_string(f)
