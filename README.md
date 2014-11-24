#Tiny Stackbased Virtual Machine in Python

Custom stack based virtual machine for experimentation.
Single file code for execution, single return value.

##Features
* requires Python3
* 24+ instructions
* currently integer values only
* instructions described in vm/instructions.py docstrings
* roughly inspired by the JVM

##Execution
```
python run.py <code.file> arg1 arg2 argN
```

Example program: python run.py data/sum.vm 1 5
```
func rangesum ; return sum of numbers in range, upper bound included
arg int ; lower bound
arg int ; upper bound
var int ; current sum
var int ; increment
iload 0
istore 2
iload 0
istore 3
ipush 1
iload 3
iadd
dup
iload 1
if_icmpgt 7
dup
istore 3
iload 2
iadd
istore 2
goto -11
iload 2
ireturn
```