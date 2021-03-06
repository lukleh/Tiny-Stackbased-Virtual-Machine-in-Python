#Tiny Stackbased Virtual Machine in Python

Custom stack based virtual machine for experimentation.
Single file code for execution, single return value.

##Features
* YAML input code format
* 46 instructions
* Integer and Float values, array of integers and floats
* instructions described in [instructions.md](doc/instructions.md)
* roughly inspired by the JVM
* requires Python3

Example programs in [data](data)

* sum of numbers in range [sum.yaml](data/sum.yaml)
* bubble sort [bubblesort.yaml](data/bubblesort.yaml)

##Execution
help in empty command 

```
python run.py -h
```

choose the codefile to run, that gives you code parameters needed

```
python run.py data/sum.yaml
```

and final command

```
python run.py data/sum.yaml --arg0 1 --arg1 5
```

array argument

```
python run.py data/bubblesort.yaml --arg0 5 10 4 3 7 10 10 0
```