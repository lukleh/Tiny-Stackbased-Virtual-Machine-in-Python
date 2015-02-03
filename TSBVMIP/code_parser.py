# -*- coding: utf-8  -*-
import yaml

from . import instructions
from . import value_containers
from .exceptions import ParserException
from .method import Method


def _process_func(method, func):
    if not func or not isinstance(func, dict):
        raise ParserException('"func" not defined')
    method.function_name = func['name']
    method.return_type = value_containers.types[func['type'].lower()]()
    _process_vars(method, func['args'], inc_arg_count=True)


def _add_label(method, label, index):
    if not isinstance(label, str):
        raise ParserException('label %s needs to be a string' % label)
    if label is None:
        raise ParserException('every local variable needs a label')
    if label in method.labels:
        raise ParserException('labels has to be unique: duplicate %s' % label)
    method.labels[label] = index


def _process_vars(method, args, inc_arg_count=False):
    for arg in args:
        t = arg['type'].lower()
        if inc_arg_count:
            method.argument_count += 1
        method.variables.append(value_containers.types[t]())
        l = arg.get('label', None)
        _add_label(method, l, len(method.variables) - 1)


def _process_ins(method, ins):
    # pass1: collect labels
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
            _add_label(method, label, offset)
        else:
            offset += 1
    else:
        if label:
            raise ParserException('label cannot be as last instruction %s' % i)

    # pass2: use labels and collect instructions
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
            method.code.append(inst())
        elif isinstance(i, dict):
            kw, value = i.popitem()
            inst = instructions.keywords[kw.lower()]
            if issubclass(inst, instructions.InsNoArgument):
                raise ParserException('instruction %s takes no argument' % i)
            if issubclass(inst, instructions.InsArgILabel):
                if isinstance(value, str):
                    try:
                        value = method.labels[value]
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

            method.code.append(inst(instructions.contain_value(inst, value)))
        else:
            raise ParserException('unknown instruction format %s' % i)


def process_yaml(structure):
    m = Method()
    _process_func(m, structure.get('func', {}))
    _process_vars(m, structure.get('lvars', []))
    _process_ins(m, structure.get('ins', []))
    return m


def parse_string(data):
    structure = yaml.safe_load(data)
    return process_yaml(structure)


def parse_file(fname):
    with open(fname, 'r') as f:
        return parse_string(f)
