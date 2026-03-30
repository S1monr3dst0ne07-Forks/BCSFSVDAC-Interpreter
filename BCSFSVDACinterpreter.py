#Interpreter of my own programming language
#created 10/01/26 by queensnail3706
from time import sleep, perf_counter
import os
import pygame
import colorsys
import warnings
import sys
#warnings.filterwarnings("ignore", category=UserWarning)


def wait_for_quit():
    clock = pygame.time.Clock()

    print("Press enter to quit.")
    while True:
        event = pygame.event.poll()
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit(0)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                break

        pygame.display.flip()
        clock.tick(60)



#Setup config
#set defaults
Defaults = {
    "width": 100,
    "height": 100,
    "mainMemSize": 255,
    "registerSize": 255,
    "stackSize": 255,
    "winSize":600,
    "DefaultFile":""
}

configFile = "config.txt"
if not os.path.exists(configFile):
    with open(configFile, "w") as f:
        for name, value in Defaults.items():
            f.write(f"{name} = {value}  # default value\n")
    print("config.txt not found, created a new one with defaults")

#Load the config
config = Defaults.copy()
with open(configFile, "r") as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "#" in line:
            line = line.split("#", 1)[0].strip()
        if "=" in line:
            name, value = line.split("=", 1)
            name = name.strip()
            value = value.strip()
            # check if value is a number
            if value.isdigit():
                config[name] = int(value)
            else:
                # keep as string
                config[name] = value

for name, value in config.items():
    globals()[name] = value

videoSize = width * height
fileName = DefaultFile
pixelSize = winSize // max(width, height)

print("---- Loaded configuration: ----")
print("stackSize =", stackSize)
print("mainMemSize   =", mainMemSize)
print("registerSize   =", registerSize)
print("Vid Width  =", width)
print("Vid Height =", height)
print("videoSize =", videoSize)
print("pixelSize =", pixelSize)
print("--------------------------------")

#Setup memories
MEM = [0] * mainMemSize
REG = [0] * registerSize
STK = [] 
VID = [0] * videoSize

#pygame setup
pygame.init()
screen = pygame.display.set_mode(
    (width * pixelSize, height * pixelSize)
)
pygame.display.set_caption("Video display BCSFSVDAC V1.0")

#variables
MEMptr = 0
VIDptr = 0
REGptr = 0

loop_addrs = []

VersionNumber = "1.0"
last_key = 0

functions = []
funcExecuteIp = 0
InstructionCounter = []


#functions
VID_OLD = [0] * videoSize
def render(): 
    global VID_OLD
    #Renders parts of video buffer which have changed

    rects = []
    for i in range(width * height):
        if VID_OLD[i] == VID[i]: continue
        VID_OLD[i] = VID[i]

        x = (i % width) * pixelSize
        y = (i // width) * pixelSize
        v = int(VID[i])
        colour = Findcolour(v)
        rect = pygame.Rect(x, y, pixelSize, pixelSize)
        rects.append(rect)
        pygame.draw.rect(screen, colour, rect)

    pygame.display.update(rects)


def skip_to_fin():
    global ip
    depth = 1  # we are already inside one WHL

    while ip < len(code) and depth > 0:
        phrase = word()
        if phrase == "WHL": depth += 1
        if phrase == "FIN": depth -= 1

    # when depth reaches 0, we are AFTER the matching FIN

def make_palette(size=width): #Makes the colour palette based on width
    palette = [
        (0, 0, 0),
        (255, 255, 255),
    ]

    for i in range(size - 2):
        h = i / (size - 2)
        r, g, b = colorsys.hsv_to_rgb(h, 1, 1)
        palette.append((
            int(r * 255),
            int(g * 255),
            int(b * 255)
        ))
    return palette

PALETTE = make_palette(width) #Loads the palette
def Findcolour(Num): #Finding colours of pixels
    if Num < 0:
        return (0, 0, 0)
    if Num >= len(PALETTE):
        Num = Num % len(PALETTE)
    return PALETTE[Num]

#load the code
print("\n")
print("-------------------------------------------------------------------")
print("-- Welcome to version ",VersionNumber," of the python BCSFSVDAC interpreter ---")
print("-------------- Check the readme for a simple tutorial -------------")
print("-- Dm u/-Ryviel for complaints and suggestions for future updates -")
print("------------------- Donation support coming soon ------------------")
print("-------------------------------------------------------------------")
print("\n\n\n")



if len(sys.argv) > 1 and sys.argv[1].strip():
    fileName = sys.argv[1]
else:
    fileName = DefaultFile

if not fileName:
    fileName = input("Enter your .bcvf or .txt file\n").strip()


def tokenize(path):
    tokens = []
    with open(path, 'r') as f:
        for line in map(str.strip, f.read().split('\n')):
            if not line: continue
            if line.startswith('#'): continue

            for word in line.split(' '):
                if not word: continue
                tokens.append(word)

    return tokens

        

if not os.path.exists(fileName):
    print(f"Program file '{fileName}' not found")
    sys.exit(1)
else:
    code = tokenize(fileName)

print(f"Loaded program: {fileName}")
print(f"Code: {code}")

print("Running")
start_time = perf_counter()

def error(msg):
    print(msg)
    runtime_error()
    sys.exit(1)

def runtime_error():
    print("\n\n\n")
    print("===============================")
    print("=== BCSFSVDAC RUNTIME ERROR ===")
    print("=  A FATAL ERROR HAS OCCURRED =")
    print("Current MEMptr:", MEMptr)
    print("MEM snapshot:", MEM[max(0, MEMptr-5):MEMptr+60])
    print("Current REGptr:", REGptr)
    print("REG snapshot:", REG[max(0, REGptr-5):REGptr+60])
    print("Current STK: ", STK)
    print("Current VIDptr:", VIDptr)
    print("VID snapshot:", VID[max(0, VIDptr-5):VIDptr+60])
    print("Current ip: ")
    print("Recent code parsed: ",code[-40:])
    print("InstructionCounter length:", len(InstructionCounter))
    print("VM version:", VersionNumber)
    print("================================")
    print("\n\n\n")

def check_memptr():
    if MEMptr < 0:
        error("MEMptr exeeded minimum lim")
    if MEMptr >= mainMemSize:
        error("MEMptr exeeded maximum lim")

def check_vidptr():
    if VIDptr < 0:
        error("VIDptr exeeded minimum lim")
    if VIDptr >= videoSize:
        error("VIDptr exeeded maximum lim")

def check_stack():
    if len(STK) >= stackSize:
        error("Stack overflow")
    if len(STK) == 0:
        error("Stack underflow")



ip = 0
while ip < len(code): #Running the code
    for event in pygame.event.get(): #Get any keypresses
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            pygame.quit()
            exit()
        if event.type == pygame.KEYDOWN:
            last_key = event.key

    def word():
        global ip
        p = code[ip]
        ip += 1
        return p

    def number():
        return int(word())

    def address(ptr):
        n = number()
        return n if n >= 0 else ptr - n

    def evaluate():
        match word():
            case x if x.isdigit():
                return int(x)
            case 'STK':
                check_stack()
                return STK[-1]
            case 'MEM':
                return MEM[address(MEMptr)]
            case 'REG':
                return REG[address(REGptr)]
            case 'VID':
                return VID[address(VIDptr)]



    last_ip = ip
    phrase = word()
    if phrase == "MEM": #MEM commands
        phrase = word()
        if phrase == "PTR": #PTR command
            MEMptr = evaluate()
            check_memptr()
                
        elif phrase == "MOV": #Move command
            MEMptr += number()
            check_memptr()

        elif phrase == "SET": #Set command
            MEM[MEMptr] = evaluate()

        elif phrase == "ADD": #ADD command, All mathematical commands are virtually the same
            MEM[MEMptr] += evaluate()

        elif phrase == "SUB":
            MEM[MEMptr] -= evaluate()

        elif phrase == "CLR":
            MEM[MEMptr] = 0

        elif phrase == "MUL":
            MEM[MEMptr] *= evaluate()

        elif phrase == "DIV":
            MEM[MEMptr] //= evaluate()

        elif phrase == "MOD":
            MEM[MEMptr] %= evaluate()

        elif phrase == "PWR":
            MEM[MEMptr] **= evaluate()

        elif phrase == "SWP": #swap function
            match word():
                case 'MEM': 
                    other = MEM
                    address = number()
                case 'REG': 
                    other = REG
                    address = number()
                case 'STK':
                    other = STK
                    address = -1
                case 'VID':
                    other = VID
                    address = number()



            temp = MEM[MEMptr]
            MEM[MEMptr] = other[address]
            other[address] = temp

        elif phrase == "JNZ" and int(MEM[MEMptr]) != 0:
            depth = 0
            while ip < len(code) and depth != 0:
                match word():
                    case 'END'        : depth -= 1
                    case 'JNZ' | 'JEZ': depth += 1

        elif phrase == "JEZ" and int(MEM[MEMptr]) == 0:
            depth = 0
            while ip < len(code) and depth != 0:
                match word():
                    case 'END'        : depth -= 1
                    case 'JNZ' | 'JEZ': depth += 1

        elif phrase == "OUT":
            print(f"Current MEM value at {MEMptr} is {MEM[MEMptr]}")

        elif phrase == "INI":
            MEM[MEMptr] = int(input("Enter value to save"))

        elif phrase == "ARY":
            # Expecting something like `ARY [1,0,2,38,1,0]`
            content = word().strip('[]')

            for value in map(int, content.split(',')):
                check_memptr()
                MEM[MEMptr] = value
                MEMptr += 1

        check_memptr()

    elif phrase == "REG":
        REGptr = number()

        match word():
            case 'SET': REG[REGptr] = evaluate()
            case 'CLR': REG[REGptr] = 0

    elif phrase == "STK":
        match word():
            case 'PSH': STK.append(evaluate())
            case 'POP': STK.pop()
            case 'CLR': STK.clear()

        check_stack()

    elif phrase == "VID":
        check_vidptr()
        match word():
            case 'PTR': VIDptr = evaluate()
            case 'MOV': VIDptr += number()
            case 'SET': VID[VIDptr] = evaluate()
            case 'CLR':
                for i in range(videoSize):
                    VID[i] = 0
            case 'ARY':
                # Expecting something like `ARY [1,0,2,38,1,0]`
                content = word().strip('[]')

                for value in map(int, content.split(',')):
                    VID[VIDptr] = value
                    VIDptr += 1


    elif phrase == "WHL":
        # "FUCK NESTED LOOPS" - queensnail3706
        # "BE NOT AFRAID" - S1monr3dst0ne07

        # the loop condition is evaluated at the start of the loop.
        # then the end jumps back to the start which makes
        # the condition checks re-execute.

        lhs = evaluate()
        operator = word()
        rhs = evaluate()

        match operator:
            case 'GTR': cond = lhs > rhs
            case 'LES': cond = lhs < rhs
            case 'EQU': cond = lhs == rhs
            case 'NEQ': cond = lhs != rhs
            case _    : cond = False

        if not cond: 
            skip_to_fin()

        else:
            # place the address of the current instruction
            # onto the loop stack, such that the condition
            # checks will re-execute.
            loop_addrs.append(last_ip)
        
    elif phrase == "FIN":
        if not loop_addrs:
            error("Error: `FIN` outside of loop.")

        # *boom* see how simple that is?
        ip = loop_addrs.pop()

    elif phrase == "FRZ":
        sleep(number()/1000)

    elif phrase == "REN":
        render()

    elif phrase == "KEY":
        match word():
            case 'MEM': MEM[number()] = last_key
            case 'REG': REG[number()] = last_key
            case 'STK': STK[-1]       = last_key
            case 'VID': VID[number()] = last_key
        last_key = 0

    """commented out for now, as no example exist to test 
    elif phrase == "DEF":
        character = code[ip]
        if character == "[":
            ip += 1
            while character != "]":
                phrase = phrase + code[ip]
                ip += 1
                character = code[ip]
            ip +=1
            funcName = phrase
            funcIp = ip
            funcInfo = {
                "funcName":funcName,
                "funcIp":ip
                }
            depth = 1
            while depth > 0 and ip < len(code):
                if code[ip:ip+3] == "RET":
                    depth -= 1
                    ip += 3
                else:
                    ip += 1
            functions.append(funcInfo)
    elif phrase == "FNC":
        phrase = ""
        character = code[ip]
        if character == "[":
            ip +=1
            while character != "]":
                phrase = phrase + code[ip]
                ip +=1
                character = code[ip]
            ip += 1
        funcExecuteIp = ip
        found = False
        for func in functions:
            if func["funcName"] == phrase:
                ip = func["funcIp"]
                found = True
                break
        if not found:
            raise Exception(f"Function '{phrase}' not defined")

    elif phrase == "RET":
        ip = funcExecuteIp
    elif phrase == "IPS":
        phrase = ""
        while ip < len(code) and code[ip].isdigit():
            phrase = phrase + code[ip]
            ip += 1
        ip = int(phrase)
    elif phrase == "INS":
        phrase = ""
        while ip < len(code) and code[ip].isdigit():
            phrase = phrase + code[ip]
            ip += 1
        ip = int(InstructionCounter[int(phrase)])
    """

    pygame.event.pump()
    if len(InstructionCounter) < 10000:
        InstructionCounter.append(ip)

end_time = perf_counter()
elapsed = end_time - start_time
milliseconds = elapsed * 1000
print(f"Execution took {milliseconds}ms")
wait_for_quit()
    
pygame.quit()
print("Done")
#print("Ending pointer value: ",MEM[MEMptr])
#print("Ending pointer: ",MEMptr)
#print("Ending memory: ",MEM)
#print("Ending VID: ", VID)



