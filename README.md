#Tiny Stackbased Virtual Machine in Python

Custom stack based virtual machine for experimentation.
Single file code for execution, single return value.

##Features
* YAML input code format
* ~35 instructions
* Integer and Float values only
* instructions described in vm/instructions.py docstrings
* roughly inspired by the JVM
* requires Python3

##Execution
```
python run.py <code.file> arg1 arg2 argN
```

Example program in data/sum.yaml
```
func:
    name: range sum #return sum of numbers in range, upper bound included
    args:
        - label: a
          type: int
        - label: b
          type: int
lvars:
    - label: sum
      type: int
    - label: increment
      type: int

ins:
    - iload: a
    - istore: sum
    - iload: a
    - istore: increment
    - ipush: 1
      label: L1
    - iload: increment
    - iadd
    - dup
    - iload: b
    - if_icmpgt: L2
    - dup
    - istore: increment
    - iload: sum
    - iadd
    - istore: sum
    - goto: L1
    - iload: sum
      label: L2
    - ireturn
```
run with
```
python run.py data/sum.yaml 1 5
```
