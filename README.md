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

Example program
```
func rangesum ; return sum of numbers in range, upper bound included
arg int ; lower bound
arg int ; upper bound
var int ; current sum
var int ; increment
load 0
store 2
load 0
store 3
push 1
load 3
add
dup
load 1
if_cmpgt 7
dup
store 3
load 2
add
store 2
goto -11
load 2
return
```