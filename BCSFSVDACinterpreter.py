#Interpreter of my own programming language
#created 10/01/26 by queensnail3706
try:
    from time import sleep, perf_counter
    import os
    import pygame
    import colorsys
    import warnings
    import sys
    warnings.filterwarnings("ignore", category=UserWarning)
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
    ip = 0
    MEMptr = 0
    VIDptr = 0
    REGptr = 0
    loopAmount = 0
    activeLoops = []
    phrase = ""
    MEMTemp = 0
    REGTemp = 0
    JNZflags = 0
    operator = ""
    adrtype = ""
    secAddress = ""
    isFin = False
    VersionNumber = "1.0"
    last_key = 0
    functions = []
    funcExecuteIp = 0
    InstructionCounter = []
    #functions
    def render(): #Renders the whole videobuffer with pygame
        screen.fill((0, 0, 0))
        #Draw each pixel
        for i in range(width * height):
            x = (i % width) * pixelSize
            y = (i // width) * pixelSize
            v = int(VID[i])
            v = int(v)
            colour = Findcolour(v)
            pygame.draw.rect(screen, colour, (int(x), int(y), pixelSize, pixelSize))
        pygame.display.flip()
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
            character = code[ip]
            if character == "W":
                if code[ip:ip+3] == "WHL":
                    depth += 1
                    ip += 3
                    continue
            elif character == "F":
                # detect FIN
                if code[ip:ip+3] == "FIN":
                    depth -= 1
                    ip += 3
                    continue
            ip += 1

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
    if not os.path.exists(fileName):
        print(f"Program file '{fileName}' not found")
        code = []
    else:
        with open(fileName, "r") as f:
            code = [
                line.split("#")[0].rstrip()
                for line in f
                if line.strip() and not line.strip().startswith("#")
            ]
    code = "".join(code)
    print(f"Loaded program: {fileName}")
    print("Code:")
    code = str(code)
    code = code.replace(" ", "")
    print(code)
    #sleep(5)
    print("Running")
    start_time = perf_counter()
    try:
        while ip < len(code): #Running the code
            for event in pygame.event.get(): #Get any keypresses
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        exit()
                if event.type == pygame.KEYDOWN:
                    last_key = event.key
            phrase = code[ip:ip+3]
            ip += 3
            if phrase == "MEM": #MEM commands
                phrase = ""
                phrase = code[ip:ip+3]
                ip += 3
                if phrase == "PTR": #PTR command
                    phrase = ""
                    character = code[ip]
                    if character.isdigit(): #Direct assignment
                        while ip<len(code) and code[ip].isdigit():
                            phrase = phrase + code[ip]
                            ip += 1
                        MEMptr = int(phrase)
                        if MEMptr < 0:
                            raise Exception("MEMptr exeeded minimum lim")
                        if MEMptr >= mainMemSize:
                            raise Exception("MEMptr exeeded maximum lim")
                    else: #assignment through addresses
                        phrase = code[ip:ip+3]
                        ip += 3
                        if phrase == "MEM":
                            phrase = ""
                            character = code[ip]
                            while ip < len(code) and code[ip].isdigit():
                                phrase = phrase + code[ip]
                                ip += 1
                            phrase = int(phrase)
                            MEMptr = int(MEM[phrase])
                        elif phrase == "REG":
                            phrase = ""
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
                            phrase = ""
                            character = code[ip]
                            while ip < len(code) and code[ip].isdigit():
                                phrase = phrase + code[ip]
                                ip += 1
                            phrase = int(phrase)
                            MEMptr = int(VID[phrase])
                        
                elif phrase == "MOV": #Move command
                    phrase = ""
                    character = code[ip]
                    if character == "-": #move back
                        ip += 1
                        phrase = ""
                        while ip < len(code) and code[ip].isdigit():
                            phrase = phrase + code[ip]
                            ip += 1
                        MEMptr = MEMptr - int(phrase)
                        if MEMptr < 0:
                            raise Exception("MEMptr exeeded minimum lim")
                    else: #Move forwards
                        phrase = ""
                        while ip < len(code) and code[ip].isdigit():
                            phrase = phrase + code[ip]
                            ip += 1
                        MEMptr = MEMptr + int(phrase)
                        if MEMptr >= mainMemSize:
                            raise Exception("MEMptr exeeded maximum lim")
                elif phrase == "SET": #Set command
                    phrase = ""
                    character = code[ip]
                    if character.isdigit():# direct assignment
                        while ip<len(code) and code[ip].isdigit():
                            phrase = phrase + code[ip]
                            ip += 1
                        MEM[MEMptr] = int(phrase)
                    else: #assignment through address
                        phrase = code[ip:ip+3]
                        ip += 3
                        if phrase == "MEM":
                            phrase = ""
                            character = code[ip]
                            if character == "-":
                                ip +=1
                                character = code[ip]
                                while ip < len(code) and code[ip].isdigit(): #Relative address compatabilty
                                    phrase = phrase + code[ip]
                                    ip += 1
                                phrase = int(phrase)
                                MEM[MEMptr] = int(MEM[int(MEMptr)-int(phrase)])
                            else: #non relative assignment
                                while ip < len(code) and code[ip].isdigit():
                                    phrase = phrase + code[ip]
                                    ip += 1
                                phrase = int(phrase)
                                MEM[MEMptr] = MEM[phrase]
                        elif phrase == "REG": #same but for reg
                            phrase = ""
                            character = code[ip]
                            if character == "-":
                                ip +=1
                                character = code[ip]
                                while ip < len(code) and code[ip].isdigit():
                                    phrase = phrase + code[ip]
                                    ip += 1
                                phrase = int(phrase)
                                MEM[MEMptr] = int(REG[int(REGptr)-int(phrase)])
                            else:
                                while ip < len(code) and code[ip].isdigit():
                                    phrase = phrase + code[ip]
                                    ip += 1
                                phrase = int(phrase)
                                MEM[MEMptr] = REG[phrase]
                        elif phrase == "STK":
                            if len(STK) == 0:
                                raise Exception("Stack underflow")
                            MEM[MEMptr] = STK[-1]
                        elif phrase == "VID": #same but for vid
                            phrase = ""
                            character = code[ip]
                            if character == "-":
                                ip +=1
                                character = code[ip]
                                while ip < len(code) and code[ip].isdigit():
                                    phrase = phrase + code[ip]
                                    ip += 1
                                phrase = int(phrase)
                                MEM[MEMptr] = int(VID[int(VIDptr)-int(phrase)])
                            else:
                                while ip < len(code) and code[ip].isdigit():
                                    phrase = phrase + code[ip]
                                    ip += 1
                                phrase = int(phrase)
                                MEM[MEMptr] = VID[phrase]
                elif phrase == "ADD": #ADD command, All mathematical commands are virtually the same
                    phrase = ""
                    if code[ip].isdigit(): #direct addition
                        while ip < len(code) and code[ip].isdigit():
                            phrase += code[ip]
                            ip += 1
                        MEM[MEMptr] += int(phrase)
                    else: #addition through address
                        phrase = code[ip:ip+3]
                        ip += 3
                        if phrase == "MEM":
                            phrase = ""
                            if code[ip] == "-":
                                ip += 1
                                while ip < len(code) and code[ip].isdigit():
                                    phrase += code[ip]
                                    ip += 1
                                MEMTemp = MEM[MEMptr - int(phrase)]
                            else:
                                while ip < len(code) and code[ip].isdigit():
                                    phrase += code[ip]
                                    ip += 1
                                MEMTemp = MEM[int(phrase)]
                            MEM[MEMptr] += MEMTemp
                        elif phrase == "REG":
                            phrase = ""
                            if code[ip] == "-":
                                ip += 1
                                while ip < len(code) and code[ip].isdigit():
                                    phrase += code[ip]
                                    ip += 1
                                REGTemp = REG[REGptr - int(phrase)]
                            else:
                                while ip < len(code) and code[ip].isdigit():
                                    phrase += code[ip]
                                    ip += 1
                                REGTemp = REG[int(phrase)]
                            MEM[MEMptr] += REGTemp
                        elif phrase == "STK":
                            if len(STK) == 0:
                                raise Exception("Stack underflow")
                            MEM[MEMptr] += STK[-1]
                        elif phrase == "VID":
                            phrase = ""
                            if code[ip] == "-":
                                ip += 1
                                while ip < len(code) and code[ip].isdigit():
                                    phrase += code[ip]
                                    ip += 1
                                VIDTemp = VID[VIDptr - int(phrase)]
                            else:
                                while ip < len(code) and code[ip].isdigit():
                                    phrase += code[ip]
                                    ip += 1
                                VIDTemp = VID[int(phrase)]
                            MEM[MEMptr] += VIDTemp

                elif phrase == "SUB":
                    phrase = ""
                    if code[ip].isdigit():
                        while ip < len(code) and code[ip].isdigit():
                            phrase += code[ip]
                            ip += 1
                        MEM[MEMptr] -= int(phrase)
                    else:
                        phrase = code[ip:ip+3]
                        ip += 3
                        if phrase == "MEM":
                            phrase = ""
                            if code[ip] == "-":
                                ip += 1
                                while ip < len(code) and code[ip].isdigit():
                                    phrase += code[ip]
                                    ip += 1
                                MEMTemp = MEM[MEMptr - int(phrase)]
                            else:
                                while ip < len(code) and code[ip].isdigit():
                                    phrase += code[ip]
                                    ip += 1
                                MEMTemp = MEM[int(phrase)]
                            MEM[MEMptr] -= MEMTemp
                        elif phrase == "REG":
                            phrase = ""
                            if code[ip] == "-":
                                ip += 1
                                while ip < len(code) and code[ip].isdigit():
                                    phrase += code[ip]
                                    ip += 1
                                REGTemp = REG[REGptr - int(phrase)]
                            else:
                                while ip < len(code) and code[ip].isdigit():
                                    phrase += code[ip]
                                    ip += 1
                                REGTemp = REG[int(phrase)]
                            MEM[MEMptr] -= REGTemp
                        elif phrase == "STK":
                            if len(STK) == 0:
                                raise Exception("Stack underflow")
                            MEM[MEMptr] -= STK[-1]
                        elif phrase == "VID":
                            phrase = ""
                            if code[ip] == "-":
                                ip += 1
                                while ip < len(code) and code[ip].isdigit():
                                    phrase += code[ip]
                                    ip += 1
                                VIDTemp = VID[VIDptr - int(phrase)]
                            else:
                                while ip < len(code) and code[ip].isdigit():
                                    phrase += code[ip]
                                    ip += 1
                                VIDTemp = VID[int(phrase)]
                            MEM[MEMptr] -= VIDTemp

                elif phrase == "CLR":
                    MEM[MEMptr] = 0
                elif phrase == "MUL":
                    phrase = ""
                    if code[ip].isdigit():
                        while ip < len(code) and code[ip].isdigit():
                            phrase += code[ip]
                            ip += 1
                        MEM[MEMptr] *= int(phrase)
                    else:
                        phrase = code[ip:ip+3]
                        ip += 3
                        if phrase == "MEM":
                            phrase = ""
                            if code[ip] == "-":
                                ip += 1
                                while ip < len(code) and code[ip].isdigit():
                                    phrase += code[ip]
                                    ip += 1
                                MEMTemp = MEM[MEMptr - int(phrase)]
                            else:
                                while ip < len(code) and code[ip].isdigit():
                                    phrase += code[ip]
                                    ip += 1
                                MEMTemp = MEM[int(phrase)]
                            MEM[MEMptr] *= MEMTemp
                        elif phrase == "REG":
                            phrase = ""
                            if code[ip] == "-":
                                ip += 1
                                while ip < len(code) and code[ip].isdigit():
                                    phrase += code[ip]
                                    ip += 1
                                REGTemp = REG[REGptr - int(phrase)]
                            else:
                                while ip < len(code) and code[ip].isdigit():
                                    phrase += code[ip]
                                    ip += 1
                                REGTemp = REG[int(phrase)]
                            MEM[MEMptr] *= REGTemp
                        elif phrase == "STK":
                            if len(STK) == 0:
                                raise Exception("Stack underflow")
                            MEM[MEMptr] *= STK[-1]
                        elif phrase == "VID":
                            phrase = ""
                            if code[ip] == "-":
                                ip += 1
                                while ip < len(code) and code[ip].isdigit():
                                    phrase += code[ip]
                                    ip += 1
                                VIDTemp = VID[VIDptr - int(phrase)]
                            else:
                                while ip < len(code) and code[ip].isdigit():
                                    phrase += code[ip]
                                    ip += 1
                                VIDTemp = VID[int(phrase)]
                            MEM[MEMptr] *= VIDTemp
                elif phrase == "DIV":
                    phrase = ""
                    if code[ip].isdigit():
                        while ip < len(code) and code[ip].isdigit():
                            phrase += code[ip]
                            ip += 1
                        MEM[MEMptr] //= int(phrase)
                    else:
                        phrase = code[ip:ip+3]
                        ip += 3
                        if phrase == "MEM":
                            phrase = ""
                            if code[ip] == "-":
                                ip += 1
                                while ip < len(code) and code[ip].isdigit():
                                    phrase += code[ip]
                                    ip += 1
                                MEMTemp = MEM[MEMptr - int(phrase)]
                            else:
                                while ip < len(code) and code[ip].isdigit():
                                    phrase += code[ip]
                                    ip += 1
                                MEMTemp = MEM[int(phrase)]
                            MEM[MEMptr] //= MEMTemp
                        elif phrase == "REG":
                            phrase = ""
                            if code[ip] == "-":
                                ip += 1
                                while ip < len(code) and code[ip].isdigit():
                                    phrase += code[ip]
                                    ip += 1
                                REGTemp = REG[REGptr - int(phrase)]
                            else:
                                while ip < len(code) and code[ip].isdigit():
                                    phrase += code[ip]
                                    ip += 1
                                REGTemp = REG[int(phrase)]
                            MEM[MEMptr] //= REGTemp
                        elif phrase == "STK":
                            if len(STK) == 0:
                                raise Exception("Stack underflow")
                            MEM[MEMptr] //= STK[-1]
                        elif phrase == "VID":
                            phrase = ""
                            if code[ip] == "-":
                                ip += 1
                                while ip < len(code) and code[ip].isdigit():
                                    phrase += code[ip]
                                    ip += 1
                                VIDTemp = VID[VIDptr - int(phrase)]
                            else:
                                while ip < len(code) and code[ip].isdigit():
                                    phrase += code[ip]
                                    ip += 1
                                VIDTemp = VID[int(phrase)]
                            MEM[MEMptr] //= VIDTemp
                elif phrase == "MOD":
                    phrase = ""
                    if code[ip].isdigit():
                        while ip < len(code) and code[ip].isdigit():
                            phrase += code[ip]
                            ip += 1
                        MEM[MEMptr] %= int(phrase)
                    else:
                        phrase = code[ip:ip+3]
                        ip += 3
                        if phrase == "MEM":
                            phrase = ""
                            if code[ip] == "-":
                                ip += 1
                                while ip < len(code) and code[ip].isdigit():
                                    phrase += code[ip]
                                    ip += 1
                                MEMTemp = MEM[MEMptr - int(phrase)]
                            else:
                                while ip < len(code) and code[ip].isdigit():
                                    phrase += code[ip]
                                    ip += 1
                                MEMTemp = MEM[int(phrase)]
                            MEM[MEMptr] %= MEMTemp
                        elif phrase == "REG":
                            phrase = ""
                            if code[ip] == "-":
                                ip += 1
                                while ip < len(code) and code[ip].isdigit():
                                    phrase += code[ip]
                                    ip += 1
                                REGTemp = REG[REGptr - int(phrase)]
                            else:
                                while ip < len(code) and code[ip].isdigit():
                                    phrase += code[ip]
                                    ip += 1
                                REGTemp = REG[int(phrase)]
                            MEM[MEMptr] %= REGTemp
                        elif phrase == "STK":
                            if len(STK) == 0:
                                raise Exception("Stack underflow")
                            MEM[MEMptr] %= STK[-1]
                        elif phrase == "VID":
                            phrase = ""
                            if code[ip] == "-":
                                ip += 1
                                while ip < len(code) and code[ip].isdigit():
                                    phrase += code[ip]
                                    ip += 1
                                VIDTemp = VID[VIDptr - int(phrase)]
                            else:
                                while ip < len(code) and code[ip].isdigit():
                                    phrase += code[ip]
                                    ip += 1
                                VIDTemp = VID[int(phrase)]
                            MEM[MEMptr] %= VIDTemp

                elif phrase == "PWR":
                    phrase = ""
                    if code[ip].isdigit():
                        while ip < len(code) and code[ip].isdigit():
                            phrase += code[ip]
                            ip += 1
                        MEM[MEMptr] **= int(phrase)
                    else:
                        phrase = code[ip:ip+3]
                        ip += 3
                        if phrase == "MEM":
                            phrase = ""
                            if code[ip] == "-":
                                ip += 1
                                while ip < len(code) and code[ip].isdigit():
                                    phrase += code[ip]
                                    ip += 1
                                MEMTemp = MEM[MEMptr - int(phrase)]
                            else:
                                while ip < len(code) and code[ip].isdigit():
                                    phrase += code[ip]
                                    ip += 1
                                MEMTemp = MEM[int(phrase)]
                            MEM[MEMptr] **= MEMTemp
                        elif phrase == "REG":
                            phrase = ""
                            if code[ip] == "-":
                                ip += 1
                                while ip < len(code) and code[ip].isdigit():
                                    phrase += code[ip]
                                    ip += 1
                                REGTemp = REG[REGptr - int(phrase)]
                            else:
                                while ip < len(code) and code[ip].isdigit():
                                    phrase += code[ip]
                                    ip += 1
                                REGTemp = REG[int(phrase)]
                            MEM[MEMptr] **= REGTemp
                        elif phrase == "STK":
                            if len(STK) == 0:
                                raise Exception("Stack underflow")
                            MEM[MEMptr] **= STK[-1]
                        elif phrase == "VID":
                            phrase = ""
                            if code[ip] == "-":
                                ip += 1
                                while ip < len(code) and code[ip].isdigit():
                                    phrase += code[ip]
                                    ip += 1
                                VIDTemp = VID[VIDptr - int(phrase)]
                            else:
                                while ip < len(code) and code[ip].isdigit():
                                    phrase += code[ip]
                                    ip += 1
                                VIDTemp = VID[int(phrase)]
                            MEM[MEMptr] **= VIDTemp
                elif phrase == "SWP": #swap function
                    phrase = ""
                    phrase = code[ip:ip+3]
                    ip += 3
                    if phrase == "MEM":
                        phrase = ""
                        while ip < len(code) and code[ip].isdigit():
                            phrase = phrase + code[ip]
                            ip += 1
                        phrase = int(phrase)
                        MEMTemp = int(MEM[MEMptr]) #stores value temporarily
                        MEM[MEMptr] = int(MEM[phrase])
                        MEM[phrase] = int(MEMTemp)
                    elif phrase == "REG":
                        phrase = ""
                        while ip < len(code) and code[ip].isdigit():
                            phrase = phrase + code[ip]
                            ip += 1
                        phrase = int(phrase)
                        MEMTemp = int(MEM[MEMptr])
                        MEM[MEMptr] = int(REG[phrase])
                        REG[phrase] = int(MEMTemp)
                    elif phrase == "STK":
                        phrase = ""
                        while ip < len(code) and code[ip].isdigit():
                            phrase = phrase + code[ip]
                            ip += 1
                        phrase = int(phrase)
                        MEMTemp = int(MEM[MEMptr])
                        MEM[MEMptr] = int(STK[-1])
                        STK[-1] = int(MEMTemp)
                    elif phrase == "VID":
                        phrase = ""
                        while ip < len(code) and code[ip].isdigit():
                            phrase = phrase + code[ip]
                            ip += 1
                        phrase = int(phrase)
                        MEMTemp = int(MEM[MEMptr])
                        MEM[MEMptr] = int(VID[phrase])
                        VID[phrase] = int(MEMTemp)
                elif phrase == "JNZ":
                    if int(MEM[MEMptr]) != 0:
                        while ip < len(code):
                            character = code[ip]
                            if character == "E":
                                ip +=1
                                phrase = ""
                                phrase = phrase + character
                                for i in range(2):
                                    character = code[ip]
                                    phrase = phrase + character
                                    ip +=1
                                if phrase == "END" and JNZflags == 0 :
                                    break
                                elif phrase == "END" and JNZflags != 0:
                                    JNZflags -=1
                            elif character == "J":
                                phrase = ""
                                ip +=1
                                phrase = phrase + character
                                for i in range(2):
                                    character = code[ip]
                                    phrase = phrase + character
                                    ip +=1
                                if phrase == "JNZ":
                                    JNZflags += 1
                                if phrase == "JEZ":
                                    JNZflags += 1
                            else:
                                ip += 1
                elif phrase == "JEZ":
                    if int(MEM[MEMptr]) == 0:
                        while ip < len(code):
                            character = code[ip]
                            if character == "E":
                                ip +=1
                                phrase = ""
                                phrase = phrase + character
                                for i in range(2):
                                    character = code[ip]
                                    phrase = phrase + character
                                    ip +=1
                                if phrase == "END" and JNZflags == 0 :
                                    break
                                elif phrase == "END" and JNZflags != 0:
                                    JNZflags -=1
                            elif character == "J":
                                phrase = ""
                                ip +=1
                                phrase = phrase + character
                                for i in range(2):
                                    character = code[ip]
                                    phrase = phrase + character
                                    ip +=1
                                if phrase == "JNZ":
                                    JNZflags += 1
                                if phrase == "JEZ":
                                    JNZflags += 1
                            else:
                                ip +=1
                elif phrase == "OUT":
                    print("Current MEM value at ",MEMptr," is ",MEM[MEMptr])
                elif phrase == "INI":
                    MEMin = input("Enter value to save")
                    MEMin = int(MEMin)
                    MEM[MEMptr] = MEMin
                elif phrase == "ARY":
                    # Expecting something like ARY[1,0,2,38,1,0]
                    if code[ip] == "[": 
                        ip += 1
                        arr_str = ""
                        while code[ip] != "]":
                            arr_str += code[ip]
                            ip += 1
                        ip += 1  # skip the closing bracket
                        # Convert the string to a list of numbers
                        arr = [int(x.strip()) for x in arr_str.split(",")]
                        # Apply each value to MEM and move MEMptr along
                        for val in arr:
                            if MEMptr >= len(MEM):
                                raise Exception("MEMptr exceeded main memory")
                            MEM[MEMptr] = val
                            MEMptr += 1
                if MEMptr < 0:
                    raise Exception("MEMptr underflow")
                if MEMptr > mainMemSize:
                    raise Exception("MEMptr overflow")

            elif phrase == "REG":
                phrase = ""
                character = code[ip]
                while ip < len(code) and code[ip].isdigit():
                    phrase = phrase + code[ip]
                    ip += 1
                REGptr = int(phrase)
                phrase = code[ip:ip+3]
                ip +=3
                if phrase == "SET":
                    phrase = ""
                    character = code[ip]
                    if character.isdigit():
                        while ip < len(code) and code[ip].isdigit():
                            phrase= phrase + code[ip]
                            ip += 1
                        phrase = int(phrase)
                        REG[REGptr] = phrase
                        REG[REGptr] = int(REG[REGptr])
                    else:
                        phrase = code[ip:ip+3]
                        ip += 3
                        if phrase == "MEM":
                            phrase = ""
                            while ip < len(code) and code[ip].isdigit():
                                phrase = phrase + code[ip]
                                ip += 1
                            phrase = int(phrase)
                            REG[REGptr] = int(MEM[phrase])
                        elif phrase == "REG":
                            phrase = ""
                            while ip < len(code) and code[ip].isdigit():
                                phrase = phrase + code[ip]
                                ip += 1
                            phrase = int(phrase)
                            REG[REGptr] = int(REG[phrase])
                        elif phrase == "STK":
                            if len(STK) == 0:
                                raise Exception("Stack underflow")
                            REG[REGptr] = int(STK[-1])
                        elif phrase == "VID":
                            phrase = ""
                            while ip < len(code) and code[ip].isdigit():
                                phrase = phrase + code[ip]
                                ip += 1
                            phrase = int(phrase)
                            REG[REGptr] = int(VID[phrase])
                elif phrase == "CLR":
                    phrase = ""
                    character = code[ip]
                    if character.isdigit():
                        while ip < len(code) and code[ip].isdigit():
                            phrase = phrase + code[ip]
                            ip += 1
                        REG[int(phrase)] = 0
            elif phrase == "STK":
                phrase = ""
                phrase = code[ip:ip+3]
                ip += 3
                if phrase == "PSH":
                    phrase = ""
                    character = code[ip]
                    if character.isdigit():
                        while ip < len(code) and code[ip].isdigit():
                            phrase= phrase + code[ip]
                            ip += 1
                        STK.append(int(phrase))
                    else:
                        phrase = code[ip:ip+3]
                        ip += 3
                        if phrase == "MEM":
                            phrase = ""
                            while ip < len(code) and code[ip].isdigit():
                                phrase = phrase + code[ip]
                                ip += 1
                            phrase = int(phrase)
                            if len(STK) >= stackSize:
                                raise Exception("Stack overflow")
                            STK.append(int(MEM[phrase]))
                        elif phrase == "REG":
                            phrase = ""
                            while ip < len(code) and code[ip].isdigit():
                                phrase = phrase + code[ip]
                                ip += 1
                            phrase = int(phrase)
                            if len(STK) >= stackSize:
                                raise Exception("Stack overflow")
                            STK.append(int(REG[phrase]))
                        elif phrase == "VID":
                            phrase = ""
                            while ip < len(code) and code[ip].isdigit():
                                phrase = phrase + code[ip]
                                ip += 1
                            phrase = int(phrase)
                            if len(STK) >= stackSize:
                                raise Exception("Stack overflow")
                            STK.append(int(VID[phrase]))
                elif phrase == "POP":
                    if len(STK) == 0:
                        raise Exception("Stack underflow")
                    STK.pop()
                elif phrase == "CLR":
                    STK.clear()
            elif phrase == "VID":
                phrase = ""
                phrase = code[ip:ip+3]
                ip +=3
                if phrase == "PTR":
                    phrase = ""
                    character = code[ip]
                    if character.isdigit():
                        while ip<len(code) and code[ip].isdigit():
                            phrase = phrase + code[ip]
                            ip += 1
                        VIDptr = int(phrase)
                        if VIDptr < 0:
                            raise Exception("VIDptr exeeded minimum lim")
                        if VIDptr >= videoSize:
                            raise Exception("VIDptr exeeded maximum lim")
                    else:
                        phrase = code[ip:ip+3]
                        ip += 3
                        if phrase == "MEM":
                            phrase = ""
                            character = code[ip]
                            while ip < len(code) and code[ip].isdigit():
                                phrase = phrase + code[ip]
                                ip += 1
                            phrase = int(phrase)
                            VIDptr = int(MEM[phrase])
                        elif phrase == "REG":
                            phrase = ""
                            character = code[ip]
                            while ip < len(code) and code[ip].isdigit():
                                phrase = phrase + code[ip]
                                ip += 1
                            phrase = int(phrase)
                            VIDptr = int(REG[phrase])
                        elif phrase == "STK":
                            if len(STK) == 0:
                                raise Exception("Stack underflow")
                            VIDptr = int(STK[-1])
                        elif phrase == "VID":
                            phrase = ""
                            character = code[ip]
                            while ip < len(code) and code[ip].isdigit():
                                phrase = phrase + code[ip]
                                ip += 1
                            phrase = int(phrase)
                            VIDptr = int(VID[phrase])
                elif phrase == "MOV":
                    phrase = ""
                    character = code[ip]
                    if character == "-":
                        ip += 1
                        phrase = ""
                        while ip < len(code) and code[ip].isdigit():
                            phrase = phrase + code[ip]
                            ip += 1
                        VIDptr = VIDptr - int(phrase)
                        if VIDptr < 0:
                            raise Exception("VIDptr exeeded minimum lim")
                    else:
                        phrase = ""
                        while ip < len(code) and code[ip].isdigit():
                            phrase = phrase + code[ip]
                            ip += 1
                        VIDptr = VIDptr + int(phrase)
                        if VIDptr >= videoSize:
                            raise Exception("VIDptr exeeded maximum lim")
                elif phrase == "SET":
                    phrase = ""
                    character = code[ip]
                    if character.isdigit():
                        while ip<len(code) and code[ip].isdigit():
                            phrase = phrase + code[ip]
                            ip += 1
                        VID[VIDptr] = int(phrase)
                    else:
                        phrase = code[ip:ip+3]
                        ip += 3
                        if phrase == "MEM":
                            phrase = ""
                            character = code[ip]
                            while ip < len(code) and code[ip].isdigit():
                                phrase = phrase + code[ip]
                                ip += 1
                            phrase = int(phrase)
                            VID[VIDptr] = int(MEM[phrase])
                        elif phrase == "REG":
                            phrase = ""
                            character = code[ip]
                            while ip < len(code) and code[ip].isdigit():
                                phrase = phrase + code[ip]
                                ip += 1
                            phrase = int(phrase)
                            VID[VIDptr] = int(REG[phrase])
                        elif phrase == "STK":
                            if len(STK) == 0:
                                raise Exception("Stack underflow")
                            VID[VIDptr] = int(STK[-1])
                        elif phrase == "VID":
                            phrase = ""
                            character = code[ip]
                            while ip < len(code) and code[ip].isdigit():
                                phrase = phrase + code[ip]
                                ip += 1
                            phrase = int(phrase)
                            VID[VIDptr] = int(VID[phrase])
                elif phrase == "CLR":
                    for i in range(videoSize):
                        VID[i] = 0
                elif phrase == "ARY":
                    # Expecting something like ARY[1,0,2,38,1,0]
                    if code[ip] == "[": 
                        ip += 1
                        arr_str = ""
                        while code[ip] != "]":
                            arr_str += code[ip]
                            ip += 1
                        ip += 1  # skip the closing bracket
                        # Convert the string to a list of numbers
                        arr = [int(x.strip()) for x in arr_str.split(",")]
                        # Apply each value to VID and move VIDptr along
                        for val in arr:
                            if VIDptr >= len(VID):
                                raise Exception("VIDptr exceeded video buffer")
                            VID[VIDptr] = val
                            VIDptr += 1

            elif phrase == "WHL":
            # FUCK NESTED LOOPS
                phrase = ""
                phrase = code[ip:ip+3]
                ip += 3
                source = phrase #collects info about loop
                if phrase == "MEM" or phrase == "REG" or phrase == "VID":
                    phrase = ""
                    while ip < len(code) and code[ip].isdigit():
                        phrase = phrase + code[ip]
                        ip += 1
                    address = int(phrase)
                elif phrase == "STK":
                    address = int(-1)
                    phrase = ""
                phrase = code[ip:ip+3]
                ip += 3
                operator = phrase
                character = code[ip]
                if character.isdigit():
                    adrtype = "DIR"
                    phrase = ""
                    while ip < len(code) and code[ip].isdigit():
                        phrase = phrase + code[ip]
                        ip += 1
                    secAddress = int(phrase)
                else:
                    phrase = ""
                    phrase = code[ip:ip+3]
                    ip +=3
                    adrtype = phrase
                    phrase = ""
                    while ip < len(code) and code[ip].isdigit():
                        phrase = phrase + code[ip]
                        ip += 1
                    secAddress = int(phrase)
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
                compare(activeLoops[-1],False)
                
            elif phrase == "FIN":
                if activeLoops:
                    loopInfo = activeLoops[-1]
                    #ip = loopInfo["loopIp"] #added this line to fin
                    compare(loopInfo,True)
                else:
                    # FIN outside loop — ignore or error
                    pass

            elif phrase == "FRZ":
                phrase = ""
                while ip<len(code) and code[ip].isdigit():
                    phrase = phrase + code[ip]
                    ip += 1
                phrase = int(phrase)
                sleep(phrase/1000)
            elif phrase == "REN":
                render()
            elif phrase == "KEY":
                phrase = ""
                phrase = code[ip:ip+3]
                ip += 3
                if phrase == "MEM":
                    phrase = ""
                    while ip<len(code) and code[ip].isdigit():
                        phrase = phrase + code[ip]
                        ip += 1
                    MEM[int(phrase)] = last_key
                elif phrase == "REG":
                    phrase = ""
                    while ip<len(code) and code[ip].isdigit():
                        phrase = phrase + code[ip]
                        ip += 1
                    REG[int(phrase)] = last_key
                elif phrase == "STK":
                    STK[-1] = last_key
                elif phrase == "VID":
                    phrase = ""
                    while ip < len(code) and code[ip].isdigit():
                        phrase = phrase + code[ip]
                        ip += 1
                    VID[int(phrase)] = last_key
                last_key = 0
            elif phrase == "DEF":
                phrase = ""
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
            phrase = ""
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
    except Exception as e:
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
except Exception as e:
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
