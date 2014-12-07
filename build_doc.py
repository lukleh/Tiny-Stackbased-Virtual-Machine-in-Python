# -*- coding: utf8 -*-

#
#
#  python3 build_doc.py > doc/instructions.md
#
#


from TSBVMIP import instructions as ins


header = """
#instructions list

"""

print(header)
print(len(ins.keywords), 'in total')


def prepare_desc(docstring):
    prep = [l for l in docstring.split('\n') if l]
    prep = [l[4:] for l in prep]
    return "\n".join(prep)


def prep_stack(st_in, st_out, order=[]):
    vnames = []
    vtypes = {}
    for i, t in enumerate(st_in + st_out):
        if order:
            j = order[i]
        else:
            j = i
        j += 1
        name = 'value%s' % j
        vnames.append(name)
        if name in vtypes:
            if vtypes[name] != t:
                raise Exception('inconsistent sack type order')
        else:
            vtypes[name] = t
    vnames.insert(len(st_in), '->')

    vnt = []
    for i, nt in enumerate(vtypes):
        name = 'value%s' % (i + 1)
        vtype = vtypes[name]
        vnt.append('%s: %s' % (name, vtype.doc_name))

    return ['```', ' '.join(vnames), '\n'.join(vnt), '```']


for name, iclass in ins.keywords.items():
    md = []
    dstr = iclass.__doc__
    md.append('## %s' % name)

    md.append(dstr.strip())
    md.append('####argument')
    if issubclass(iclass, ins.InsArgILabel):
        md.append('integer or label')
    elif issubclass(iclass, ins.InsArgInteger):
        md.append('integer')
    elif issubclass(iclass, ins.InsArgFloat):
        md.append('float')
    else:
        md.append('no arguments')

    md.append('####operation stack')
    md.extend(prep_stack(iclass.stack_input_arguments, iclass.stack_output_arguments, iclass.stack_order))
    print('\n'.join(md))
    print()