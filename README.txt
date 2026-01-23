README
===========INTRO===============
BCSFSVDAC
Basic coding system for simple video display and calculations
file extension
.bcvf

===========CONTEST=============
Anyone that can create a better .exe icon will be credited in readme and initialization (even if your icon doesn't get used)
contact at -Ryviel on reddit

===========DESCRIPTION==========
BCSFSVDAC is a minimal interpreted programming language focused on memory manipulation, simple calculations, and basic video output.

===========RUNNING FILES========
You will need to define BCSFSVDAC (1.0).exe as default program to run .bcvf files
Run BCSFSVDAC.exe and pass a .bcvf file by double-clicking or via command line.
If no file is provided, either defaultfile in config is used or the user will be prompted by default.


### Cant wait to see what everyone creates :3 ####

===========Known issues========
INS and IPN can often break catastrophically if misused this is (mostly) intentional, my honest advice: don't
The config file is required to be in the same location as the .bcvf file or else it will create a new one with defaults

===========SUPPORT AND CONTANT=====
If you have any issues or questions contact u/-ryviel on reddit

===========TUTORIAL=========
-----MEM commands-----
- PTR
sets pointer to value specified after command
Pointer cannot exceed the maximum limit or be lower than 0
pointer can be set by another address
Examples
MEM PTR 30
MEM PTR 482
MEM PTR MEM 4


- MOV 
moves pointer +/- value specified 
Pointer cannot exceed the maximum limit or be lower than 0
Does not take addresses
Examples
MEM MOV 20
MEM MOV -130


- SET
sets the value of current ptr to value specified, the value can also be another address
If using STK no address is needed, providing an address will give an error
SET also takes negative address values to dynamically access adresses
Examples
MEM SET 20
MEM SET MEM 30
MEM SET REG 20


- ADD
Adds a value to the current value of the current address
Value can be another address
If using STK no address is needed, providing an address will give an error
ADD also takes negative address values to dynamically access adresses
Examples
MEM ADD 30
MEM ADD MEM 10
MEM ADD VID 2
MEM ADD MEM -3


- SUB
Same as ADD but for subtraction
Examples
MEM SUB 3
MEM SUB MEM 6
MEM SUB REG 4


- MUL
Same as ADD but for multiplication
Examples
MEM MUL 4
MEM MUL MEM 5


- DIV
Same as ADD but for division
will always return a full int
Examples
MEM DIV 5
MEM DIV MEM 19


- MOD
modulus function
Examples
MEM MOD 5
MEM MOD MEM 10


- PWR
power function
Examples
MEM PWR 10
MEM PWR MEM 2


- SWP
Swaps two values
if swapping stack no address is needed, providing an address will give an error
Examples
MEM SWP MEM 5
MEM SWP REG 2
MEM SWP STK


- JNZ 
jumps to an END tag if current cell is not 0
Examples
MEM JNZ.........END
MEM JNZ....JNZ.....END......END


- JEZ
jumps to an END tag if current cell is 0
Examples
MEM JEZ......END
MEM JEZ .....JNZ....END.....END


- OUT
prints out the current value of MEM at MEMptr
Example
MEM OUT


- INI
Takes in an integer value and saves it to MEM at MEMptr
Example
MEM INI



-----REG commands-----
- SET
Sets a specified register address to a specified number or address
Example
REG 4 SET MEM 5
REG 4 SET 10
REG 3 SET STK


- CLR
clears a specified register address
Example
REG 5 CLR


-----STK commands-----
- PSH
Adds a number or address  to top of stack
Example
STK PSH 20
STK PSH MEM 4


- POP
Removes the top of the list
Example
STK POP


- CLR
Clears the whole stack
Example
STK CLR



-----VID commands-----
- PTR
Sets the VID pointer to a specified number, can be specified through address
Example
VID PTR 10
VID PTR MEM 6
VID PTR STK


- MOV
Moves the VID pointer a certain amount, can take an address
Example
VID MOV 5
VID MOV -6
VID MOV MEM 5


- SET
Sets the current value at VIDptr to an amount, can be specified through address
Example
VID SET 7
VID SET MEM 8


- CLR
Clears all of VID
Example
VID CLR


- REN
Renders VID, the VID prefix is not needed
Example
REN



-----LOOP commands-----
-WHL
Repeats a section of code as long as the condition is met
the section is defined as the WHL command to the FIN command
if the condition is false the section inside the loop will be skipped
the conditions that WHL takes are: GTR (greater than) LES (less than) EQU (equal to) NEQ (not equal to)
Examples
WHL MEM 5 GTR 4 (while MEM 5 is greater than 4) ....... FIN
WHL REG 2 LES 8 (while REG 2 is less than 8) ..... FIN


-----Functions-----
Functions are laid out in the format DEF [Function name in square brackets] function contents, you must end the function with a RET tag
Calling a function is FNC [NAME of function in square brackets]
DEF [ThisIsAfunction]
{function contents}
RET

FNC [ThisIsAfunction]



-----Misc-----
Use # for comments


- FRZ
pause for a period of time in milliseconds
Examples
FRZ 1000
FRZ 500


- KEY
get the last key pressed as an int and store it as an address
Examples
KEY MEM 4
KEY REG 10

- IPS
sets the ip to a specified number
!! warning this can break very easily !!
Examples
IPS 3
IPS 9


- IPN
sets the ip to any previous instruction executed
Example
MEM SET 10
MEM MOV 2
MEM SET 11
IPN 2 #will skip back to MEM MOV 2

========FUTURE ROADMAP SNEAK PEEK ====
v2.0 - User made library support!
v3.0 - Named variables
If you wish to see something added, refer to contact details mentioned earlier
Other additions that might be added by popular request (tell me if you want this):
The ablity to save height and width at an address