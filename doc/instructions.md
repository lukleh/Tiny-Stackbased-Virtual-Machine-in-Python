
#instructions list


46 in total
## ipush
push integer value onto the stack
####argument
integer
####operation stack
```
-> value1
value1: integer
```

## fpush
push float value onto the stack
####argument
float
####operation stack
```
-> value1
value1: float
```

## iload
load integer value from local variable at index
####argument
integer or label
####operation stack
```
-> value1
value1: integer
```

## fload
load float value from local variable at index
####argument
integer or label
####operation stack
```
-> value1
value1: float
```

## istore
store integer value to local variable at index
####argument
integer or label
####operation stack
```
value1 ->
value1: integer
```

## fstore
store float value to local variable at index
####argument
integer or label
####operation stack
```
value1 ->
value1: float
```

## goto
move pointer to position
####argument
integer or label
####operation stack
```
->

```

## ireturn
pops value from stack and set it as return value of the code and finishes execution
####argument
no arguments
####operation stack
```
value1 ->
value1: integer
```

## freturn
pops value from stack and set it as return value of the code and finishes execution
####argument
no arguments
####operation stack
```
value1 ->
value1: float
```

## nop
no effect, no operation
####argument
no arguments
####operation stack
```
->

```

## pop
pops value from stack and discards it
####argument
no arguments
####operation stack
```
value1 ->
value1: any value
```

## dup
duplicates value on the stack
####argument
no arguments
####operation stack
```
value1 -> value1 value1
value1: any value
```

## swap
swaps values on the stack
####argument
no arguments
####operation stack
```
value1 value2 -> value2 value1
value1: any value
value2: any value
```

## if_icmpeq
if two values are equal, move pointer to <var>
####argument
integer or label
####operation stack
```
value1 value2 ->
value1: integer
value2: integer
```

## if_icmpne
if two values are not equal, move pointer to <var>
####argument
integer or label
####operation stack
```
value1 value2 ->
value1: integer
value2: integer
```

## if_icmpge
if value1 is greater or equal to value2, move pointer to <var>
####argument
integer or label
####operation stack
```
value1 value2 ->
value1: integer
value2: integer
```

## if_icmpgt
if value1 is greater than value2, move pointer to <var>
####argument
integer or label
####operation stack
```
value1 value2 ->
value1: integer
value2: integer
```

## if_icmple
if value1 is lower or equal than value2, move pointer to <var>
####argument
integer or label
####operation stack
```
value1 value2 ->
value1: integer
value2: integer
```

## if_icmplt
if value1 is lower than value2, move pointer to <var>
####argument
integer or label
####operation stack
```
value1 value2 ->
value1: integer
value2: integer
```

## if_fcmpeq
if two values are equal, move pointer to <var>
####argument
integer or label
####operation stack
```
value1 value2 ->
value1: float
value2: float
```

## if_fcmpne
if two values are not equal, move pointer to <var>
####argument
integer or label
####operation stack
```
value1 value2 ->
value1: float
value2: float
```

## if_fcmpge
if value1 is greater or equal to value2, move pointer to <var>
####argument
integer or label
####operation stack
```
value1 value2 ->
value1: float
value2: float
```

## if_fcmpgt
if value1 is greater than value2, move pointer to <var>
####argument
integer or label
####operation stack
```
value1 value2 ->
value1: float
value2: float
```

## if_fcmple
if value1 is lower or equal than value2, move pointer to <var>
####argument
integer or label
####operation stack
```
value1 value2 ->
value1: float
value2: float
```

## if_fcmplt
if value1 is lower than value2, move pointer to <var>
####argument
integer or label
####operation stack
```
value1 value2 ->
value1: float
value2: float
```

## ifnonnull
if value is not null, move pointer to <var>
####argument
integer or label
####operation stack
```
value1 ->
value1: any value
```

## ifnull
if value is null, move pointer to <var>
####argument
integer or label
####operation stack
```
value1 ->
value1: any value
```

## iadd
add two integers, push result to stack
####argument
no arguments
####operation stack
```
value1 value2 -> value3
value1: integer
value2: integer
value3: integer
```

## isub
subsctract two integers, push result to stack
####argument
no arguments
####operation stack
```
value1 value2 -> value3
value1: integer
value2: integer
value3: integer
```

## imul
multiply two integers, push result to stack
####argument
no arguments
####operation stack
```
value1 value2 -> value3
value1: integer
value2: integer
value3: integer
```

## idiv
divide two integers, push result to stack
####argument
no arguments
####operation stack
```
value1 value2 -> value3
value1: integer
value2: integer
value3: integer
```

## fadd
add two floats, push result to stack
####argument
no arguments
####operation stack
```
value1 value2 -> value3
value1: float
value2: float
value3: float
```

## fsub
subsctract two floats, push result to stack
####argument
no arguments
####operation stack
```
value1 value2 -> value3
value1: float
value2: float
value3: float
```

## fmul
multiply two floats, push result to stack
####argument
no arguments
####operation stack
```
value1 value2 -> value3
value1: float
value2: float
value3: float
```

## fdiv
divide two floats, push result to stack
####argument
no arguments
####operation stack
```
value1 value2 -> value3
value1: float
value2: float
value3: float
```

## f2i
converts float to int
####argument
no arguments
####operation stack
```
value1 -> value2
value1: float
value2: integer
```

## i2f
converts int to float
####argument
no arguments
####operation stack
```
value1 -> value2
value1: integer
value2: float
```

## newarray
makes an array of size value1 with type <var>
####argument
integer
####operation stack
```
value1 -> value2
value1: integer
value2: generic array
```

## aload
load array reference from local variable <var>
####argument
integer or label
####operation stack
```
-> value1
value1: generic array
```

## astore
store array reference to local variable <var>
####argument
integer or label
####operation stack
```
value1 ->
value1: generic array
```

## iaload
load an int from an array
####argument
no arguments
####operation stack
```
value1 value2 -> value3
value1: array of components integer
value2: integer
value3: integer
```

## faload
load an float from an array
####argument
no arguments
####operation stack
```
value1 value2 -> value3
value1: array of components float
value2: integer
value3: float
```

## iastore
store an int to array index
####argument
no arguments
####operation stack
```
value1 value2 value3 ->
value1: array of components integer
value2: integer
value3: integer
```

## fastore
store an float to array index
####argument
no arguments
####operation stack
```
value1 value2 value3 ->
value1: array of components float
value2: integer
value3: float
```

## arraylength
returns length of an array
####argument
no arguments
####operation stack
```
value1 -> value2
value1: generic array
value2: integer
```

## areturn
pops value from stack and set it as return value of the code and finishes execution
####argument
no arguments
####operation stack
```
value1 ->
value1: generic array
```

