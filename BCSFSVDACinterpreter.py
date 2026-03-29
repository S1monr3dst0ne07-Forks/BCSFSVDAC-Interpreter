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
    print("press enter to quit")
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    break



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
#Find config file
configFile = "config.txt"
#If no configs exist create the file
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
clock = pygame.time.Clock()

#variables
MEMptr = 0
VIDptr = 0
REGptr = 0
loopAmount = 0
activeLoops = []
JNZflags = 0
isFin = False
VersionNumber = "1.0"
last_key = 0
functions = []
funcExecuteIp = 0
InstructionCounter = []


#functions
VID_OLD = [0] * videoSize
def render(): 
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

def compare(loopInfo,fromFin):
    global ip

    # resolve LEFT
    if loopInfo["source"] == "MEM":
        left = MEM[loopInfo["address"]]
    elif loopInfo["source"] == "REG":
        left = REG[loopInfo["address"]]
    elif loopInfo["source"] == "VID":
        left = VID[loopInfo["address"]]
    elif loopInfo["source"] == "STK":
        left = STK[-1]

    # resolve RIGHT
    if loopInfo["adrtype"] == "DIR":
        right = loopInfo["secAddress"]
    elif loopInfo["adrtype"] == "MEM":
        right = MEM[loopInfo["secAddress"]]
    elif loopInfo["adrtype"] == "REG":
        right = REG[loopInfo["secAddress"]]
    elif loopInfo["adrtype"] == "VID":
        right = VID[loopInfo["secAddress"]]
    elif loopInfo["adrtype"] == "STK":
        right = STK[-1]

    # evaluate condition
    if loopInfo["operator"] == "GTR":
        cond = left > right
    elif loopInfo["operator"] == "LES":
        cond = left < right
    elif loopInfo["operator"] == "EQU":
        cond = left == right
    elif loopInfo["operator"] == "NEQ":
        cond = left != right
    else:
        cond = False

    if not fromFin:
        # called from WHL
        if not cond:
            skiptoFin()
            activeLoops.pop()
        # if cond == True → do nothing, run loop body

    else:
        # called from FIN
        if cond:
            ip = loopInfo["loopIp"]
        else:
            activeLoops.pop()
            # continue forward normally

def skiptoFin():
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
    global PALETTE
    global width
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
print("\n \n \n")



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
    sys.exit(1)

def check_memptr():
    if MEMptr < 0:
        error("MEMptr exeeded minimum lim")
    if MEMptr >= mainMemSize:
        error("MEMptr exeeded maximum lim")

def check_vidptr():
    if VIDptr < 0:
        raise Exception("VIDptr exeeded minimum lim")
    if VIDptr >= videoSize:
        raise Exception("VIDptr exeeded maximum lim")

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
        global ip, code
        p = code[ip]
        ip += 1
        return p

    phrase = word()
    if phrase == "MEM": #MEM commands
        phrase = word()
        if phrase == "PTR": #PTR command
            character = code[ip]
            if character.isdigit(): #Direct assignment
                MEMptr = int(word())
            else: #assignment through addresses
                phrase = word()

                if phrase == "MEM":
                    character = code[ip]
                    while ip < len(code) and code[ip].isdigit():
                        phrase = phrase + code[ip]
                        ip += 1
                    phrase = int(phrase)
                    MEMptr = int(MEM[phrase])
                elif phrase == "REG":
                    character = code[ip]
                    while ip < len(code) and code[ip].isdigit():
                        phrase = phrase + code[ip]
                        ip += 1
                    phrase = int(phrase)
                    MEMptr = int(REG[phrase])
                elif phrase == "STK":
                    if len(STK) == 0:
                        raise Exception("Stack underflow")
                    MEMptr = int(STK[-1])
                elif phrase == "VID":
                    character = code[ip]
                    while ip < len(code) and code[ip].isdigit():
                        phrase = phrase + code[ip]
                        ip += 1
                    phrase = int(phrase)
                    MEMptr = int(VID[phrase])
                
        elif phrase == "MOV": #Move command
            offset = int(word())
            MEMptr += offset
            check_memptr()

        elif phrase == "SET": #Set command
            phrase = code[ip]
            if phrase.isdigit():# direct assignment
                MEM[MEMptr] = int(phrase)

            else: #assignment through address
                phrase = word()
                if phrase == "MEM":
                    character = code[ip]
                    if character == "-":
                        phrase = int(word())
                        MEM[MEMptr] = int(MEM[int(MEMptr)-int(phrase)])
                    else: #non relative assignment
                        phrase = int(word())
                        MEM[MEMptr] = MEM[phrase]
                elif phrase == "REG": #same but for reg
                    character = code[ip]
                    if character == "-":
                        phrase = int(word())
                        MEM[MEMptr] = int(REG[int(REGptr)-int(phrase)])
                    else:
                        phrase = int(word())
                        MEM[MEMptr] = REG[phrase]
                elif phrase == "STK":
                    check_stack()
                    MEM[MEMptr] = STK[-1]
                elif phrase == "VID": #same but for vid
                    character = code[ip]
                    if character == "-":
                        phrase = int(word())
                        MEM[MEMptr] = int(VID[int(VIDptr)-int(phrase)])
                    else:
                        phrase = int(word())
                        MEM[MEMptr] = VID[phrase]
        elif phrase == "ADD": #ADD command, All mathematical commands are virtually the same
            if code[ip].isdigit(): #direct addition
                MEM[MEMptr] += int(word())
            else: #addition through address
                phrase = word()
                if phrase == "MEM":
                    if code[ip] == "-":
                        MEMTemp = MEM[MEMptr - int(word())]
                    else:
                        MEMTemp = MEM[int(word())]
                    MEM[MEMptr] += MEMTemp

                elif phrase == "REG":
                    if code[ip] == "-":
                        REGTemp = REG[REGptr - int(word())]
                    else:
                        REGTemp = REG[int(word())]
                    MEM[MEMptr] += REGTemp
                elif phrase == "STK":
                    check_stack()
                    MEM[MEMptr] += STK[-1]
                elif phrase == "VID":
                    if code[ip] == "-":
                        VIDTemp = VID[VIDptr - int(word())]
                    else:
                        VIDTemp = VID[int(word())]
                    MEM[MEMptr] += VIDTemp

        elif phrase == "SUB":
            if code[ip].isdigit():
                MEM[MEMptr] -= int(word())
            else:
                phrase = word()
                if phrase == "MEM":
                    if code[ip] == "-":
                        MEMTemp = MEM[MEMptr - int(word())]
                    else:
                        MEMTemp = MEM[int(word())]
                    MEM[MEMptr] -= MEMTemp

                elif phrase == "REG":
                    if code[ip] == "-":
                        REGTemp = REG[REGptr - int(word())]
                    else:
                        REGTemp = REG[int(word())]
                    MEM[MEMptr] -= REGTemp
                elif phrase == "STK":
                    check_stack()
                    MEM[MEMptr] -= STK[-1]
                elif phrase == "VID":
                    if code[ip] == "-":
                        VIDTemp = VID[VIDptr - int(word())]
                    else:
                        VIDTemp = VID[int(word())]
                    MEM[MEMptr] -= VIDTemp

        elif phrase == "CLR":
            MEM[MEMptr] = 0

        elif phrase == "MUL":
            if code[ip].isdigit():
                MEM[MEMptr] *= int(word())
            else:
                phrase = word()
                if phrase == "MEM":
                    if code[ip] == "-":
                        MEMTemp = MEM[MEMptr - int(word())]
                    else:
                        MEMTemp = MEM[int(word())]
                    MEM[MEMptr] *= MEMTemp

                elif phrase == "REG":
                    if code[ip] == "-":
                        REGTemp = REG[REGptr - int(word())]
                    else:
                        REGTemp = REG[int(word())]
                    MEM[MEMptr] *= REGTemp

                elif phrase == "STK":
                    check_stack()
                    MEM[MEMptr] *= STK[-1]
                elif phrase == "VID":
                    if code[ip] == "-":
                        VIDTemp = VID[VIDptr - int(word())]
                    else:
                        VIDTemp = VID[int(word())]
                    MEM[MEMptr] *= VIDTemp

        elif phrase == "DIV":
            if code[ip].isdigit():
                MEM[MEMptr] //= int(word())
            else:
                phrase = word()
                if phrase == "MEM":
                    if code[ip] == "-":
                        MEMTemp = MEM[MEMptr - int(word())]
                    else:
                        MEMTemp = MEM[int(word())]
                    MEM[MEMptr] //= MEMTemp
                elif phrase == "REG":
                    if code[ip] == "-":
                        REGTemp = REG[REGptr - int(word())]
                    else:
                        REGTemp = REG[int(word())]
                    MEM[MEMptr] //= REGTemp
                elif phrase == "STK":
                    check_stack()
                    MEM[MEMptr] //= STK[-1]
                elif phrase == "VID":
                    if code[ip] == "-":
                        VIDTemp = VID[VIDptr - int(word())]
                    else:
                        VIDTemp = VID[int(word())]
                    MEM[MEMptr] //= VIDTemp

        elif phrase == "MOD":
            if code[ip].isdigit():
                MEM[MEMptr] %= int(word())
            else:
                phrase = word()
                if phrase == "MEM":
                    if code[ip] == "-":
                        MEMTemp = MEM[MEMptr - int(word())]
                    else:
                        MEMTemp = MEM[int(word())]
                    MEM[MEMptr] %= MEMTemp
                elif phrase == "REG":
                    if code[ip] == "-":
                        REGTemp = REG[REGptr - int(word())]
                    else:
                        REGTemp = REG[int(word())]
                    MEM[MEMptr] %= REGTemp
                elif phrase == "STK":
                    check_stack()
                    MEM[MEMptr] %= STK[-1]
                elif phrase == "VID":
                    if code[ip] == "-":
                        VIDTemp = VID[VIDptr - int(word())]
                    else:
                        VIDTemp = VID[int(wordD())]
                    MEM[MEMptr] %= VIDTemp

        elif phrase == "PWR":
            if code[ip].isdigit():
                MEM[MEMptr] **= int(word())
            else:
                phrase = word()
                if phrase == "MEM":
                    if code[ip] == "-":
                        MEMTemp = MEM[MEMptr - int(word())]
                    else:
                        MEMTemp = MEM[int(word())]
                    MEM[MEMptr] **= MEMTemp
                elif phrase == "REG":
                    if code[ip] == "-":
                        REGTemp = REG[REGptr - int(word())]
                    else:
                        REGTemp = REG[int(word())]
                    MEM[MEMptr] **= REGTemp
                elif phrase == "STK":
                    check_stack()
                    MEM[MEMptr] **= STK[-1]
                elif phrase == "VID":
                    if code[ip] == "-":
                        VIDTemp = VID[VIDptr - int(word())]
                    else:
                        VIDTemp = VID[int(word())]
                    MEM[MEMptr] **= VIDTemp

        elif phrase == "SWP": #swap function
            phrase = word()
            if phrase == "MEM":
                phrase = int(word())
                MEMTemp = int(MEM[MEMptr]) #stores value temporarily
                MEM[MEMptr] = int(MEM[phrase])
                MEM[phrase] = int(MEMTemp)

            elif phrase == "REG":
                phrase = int(word())
                MEMTemp = int(MEM[MEMptr])
                MEM[MEMptr] = int(REG[phrase])
                REG[phrase] = int(MEMTemp)
            elif phrase == "STK":
                phrase = int(word())
                MEMTemp = int(MEM[MEMptr])
                MEM[MEMptr] = int(STK[-1])
                STK[-1] = int(MEMTemp)
            elif phrase == "VID":
                phrase = int(word())
                MEMTemp = int(MEM[MEMptr])
                MEM[MEMptr] = int(VID[phrase])
                VID[phrase] = int(MEMTemp)

        elif phrase == "JNZ":
            if int(MEM[MEMptr]) != 0:
                while ip < len(code):
                    phrase = word()
                    if phrase == "END":
                        if JNZflags == 0: break
                        if JNZflags != 0: JNZflags -= 1

                    elif phrase == "JNZ":
                        JNZflags += 1
                    elif phrase == "JEZ":
                        JNZflags += 1

        elif phrase == "JEZ":
            if int(MEM[MEMptr]) == 0:
                while ip < len(code):
                    phrase = word()
                    if phrase == "END":
                        if JNZflags == 0: break
                        if JNZflags != 0: JNZflags -= 1
                    elif phrase == "JNZ":
                        JNZflags += 1
                    elif phrase == "JEZ":
                        JNZflags += 1

        elif phrase == "OUT":
            print(f"Current MEM value at {MEMptr} is {MEM[MEMptr]}")

        elif phrase == "INI":
            MEMin = int(input("Enter value to save"))
            MEM[MEMptr] = MEMin

        elif phrase == "ARY":
            # Expecting something like `ARY [1,0,2,38,1,0]`
            content = word().strip('[]')

            for value in map(int, content.split(',')):
                check_memptr()
                MEM[MEMptr] = value
                MEMptr += 1

        check_memptr()

    elif phrase == "REG":
        REGptr = int(word())
        phrase = word()

        if phrase == "SET":
            character = code[ip]
            if character.isdigit():
                REG[REGptr] = int(word())
            else:
                phrase = word()
                if phrase == "MEM":
                    phrase = int(word())
                    REG[REGptr] = int(MEM[phrase])
                elif phrase == "REG":
                    phrase = int(word())
                    REG[REGptr] = int(REG[phrase])
                elif phrase == "STK":
                    check_stack()
                    REG[REGptr] = int(STK[-1])
                elif phrase == "VID":
                    phrase = int(word())
                    REG[REGptr] = int(VID[phrase])
        elif phrase == "CLR":
            if code[ip].isdigit():
                REG[int(word())] = 0

    elif phrase == "STK":
        phrase = word()
        if phrase == "PSH":
            if code[ip].isdigit():
                STK.append(int(word()))
            else:
                phrase = word()
                if phrase == "MEM":
                    phrase = int(word())
                    STK.append(int(MEM[phrase]))
                    check_stack()
                elif phrase == "REG":
                    phrase = int(word())
                    STK.append(int(REG[phrase]))
                    check_stack()
                elif phrase == "VID":
                    phrase = int(word())
                    check_stack()
                    STK.append(int(VID[phrase]))

        elif phrase == "POP":
            check_stack()
            STK.pop()
        elif phrase == "CLR":
            STK.clear()

    elif phrase == "VID":
        phrase = word()
        if phrase == "PTR":
            if code[ip].isdigit():
                VIDptr = int(word())
                check_vidptr()
            else:
                phrase = word()
                if phrase == "MEM":
                    phrase = int(word())
                    VIDptr = int(MEM[phrase])
                elif phrase == "REG":
                    phrase = int(word())
                    VIDptr = int(REG[phrase])
                elif phrase == "STK":
                    check_stack()
                    VIDptr = int(STK[-1])
                elif phrase == "VID":
                    phrase = int(word())
                    VIDptr = int(VID[phrase])

        elif phrase == "MOV":
            VIDptr += int(word())
            check_vidptr()

        elif phrase == "SET":
            if code[ip].isdigit():
                VID[VIDptr] = int(word())
            else:
                phrase = word()
                if phrase == "MEM":
                    phrase = int(word())
                    VID[VIDptr] = int(MEM[phrase])
                elif phrase == "REG":
                    phrase = int(word())
                    VID[VIDptr] = int(REG[phrase])
                elif phrase == "STK":
                    check_stack()
                    VID[VIDptr] = int(STK[-1])
                elif phrase == "VID":
                    phrase = int(word())
                    VID[VIDptr] = int(VID[phrase])

        elif phrase == "CLR":
            for i in range(videoSize):
                VID[i] = 0

        elif phrase == "ARY":
            # Expecting something like `ARY [1,0,2,38,1,0]`
            content = word().strip('[]')

            for value in map(int, content.split(',')):
                check_vidptr()
                VID[VIDptr] = value
                VIDptr += 1

    elif phrase == "WHL":
        # FUCK NESTED LOOPS

        source = word() #collects info about loop
        if source in ('MEM', 'REG', 'VID'):
            address = int(word())
        elif source == "STK":
            address = int(-1)

        operator = word()
        if code[ip].isdigit():
            adrtype = "DIR"
            secAddress = int(word())
        else:
            adrtype = word()
            secAddress = int(word())

        loopIp = ip
        loopInfo = { #compiles info about loop
            "loopIp":loopIp,
            "source":source,
            "address":address,
            "operator":operator,
            "adrtype":adrtype,
            "secAddress":secAddress,
            "loopAmount":loopAmount
        }

        loopAmount += 1
        activeLoops.append(loopInfo)
        compare(activeLoops[-1], False)
        
    elif phrase == "FIN":
        if activeLoops:
            loopInfo = activeLoops[-1]
            #ip = loopInfo["loopIp"] #added this line to fin
            compare(loopInfo,True)
        else:
            # FIN outside loop — ignore or error
            pass

    elif phrase == "FRZ":
        phrase = int(word())
        sleep(phrase/1000)

    elif phrase == "REN":
        render()

    elif phrase == "KEY":
        phrase = word()
        if phrase == "MEM":
            MEM[int(word())] = last_key
        elif phrase == "REG":
            REG[int(word())] = last_key
        elif phrase == "STK":
            STK[-1] = last_key
        elif phrase == "VID":
            VID[int(word())] = last_key
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
print("Execution took ",milliseconds,"ms")
waiting = True
print("press enter to quit")
while waiting:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                waiting = False 

    pygame.display.flip()
    clock.tick(60)


def runtime_error():
    print("\n \n \n")
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
    print("Current phrase:", phrase)
    print("InstructionCounter length:", len(InstructionCounter))
    print("VM version:", VersionNumber)
    print("Error message:", e)
    print("================================")
    print("\n \n \n")
    raise Exception("An error has occurred")
    
pygame.quit()
print("Done")
print("Ending pointer value: ",MEM[MEMptr])
print("Ending pointer: ",MEMptr)
print("Ending memory: ",MEM)
#print("Ending VID: ", VID)


wait_for_quit()

