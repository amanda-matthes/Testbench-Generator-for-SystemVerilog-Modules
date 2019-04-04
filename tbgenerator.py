'''
Funktioniert zur Zeit nur für Module ohne Parameter
'''

def readFile(filename):
    f = open(filename, "r")
    content = f.read()
    f.close()
    return content

def writeFile(filename, content):
    f = open(filename, "w")
    f.write(content)
    f.close()
    return

def removeComments(text): # Removes Comments (/**/ and //) in and before the portlist and whitespace at the beginning
    result = ""
    insideMultilineComment = False
    insideOneLineComment = False
    for i in range (0, len(text)):
        charPair = text[i:i+2]
        lastCharPair = text[i-1:i+1]
        if (insideMultilineComment):
           result += '' #"\n INSIDE MULTILINE COMMENT \n"
        if (insideOneLineComment):
           result += '' #"\n INSIDE ONELINE COMMENT \n"
        if (charPair == "/*"):
            insideMultilineComment = True
        if (charPair == "//"):
            insideOneLineComment = True 
        if ((not insideMultilineComment) and (not insideOneLineComment)):
            result += text[i]
        if (lastCharPair == "*/"):
            insideMultilineComment = False
        if (text[i] == '\n'):
            insideOneLineComment = False
        if (text[i] == ";"): # we only need the part up to the portlist
            break
    # now remove whitespace at beginning
    start = result.find('m') # find 'module'
    result = result[start:]
    return result


def removeLengthSpecifiers(input):
    output = []
    stop = False
    temp = ""
    for element in input:
        for char in element:
            if (char == '['):
                stop = True
            if (stop == False and char != ' '):
                temp += char
            if (char == ']'):
                stop = False
        output.append(temp)
        temp = ""
    return output


def getInputsAndOutputs (portlist):
    portlist = portlist + ','
    inputs = []                 # array of strings
    outputs = []                # array of strings
    temp = ""
    inputTag = True             # boolean True = input False = output
    for char in portlist:
        if (temp == "inputwire"):
            inputTag = True
            temp = ""
        if (temp == "outputreg"):
            inputTag = False
            temp = ""
        if (char == ','):
            if (inputTag == True):
                inputs.append(temp)
                temp = ""
            if (inputTag == False):
                outputs.append(temp)
                temp = ""
        if ((char != ' ') and (char != '\n') and (char != '\t') and (char != ',')):
            temp = temp + char
        if (char == ']'):
            temp = temp + " "

    return [inputs, outputs]

def createInstantiation(modulename, portlist):
    inputs = getInputsAndOutputs(portlist)[0]
    outputs = getInputsAndOutputs(portlist)[1]
    result = ""

    # Remove lenght specifiers (z.B.: [63:0])
    inputs = removeLengthSpecifiers(inputs)
    outputs = removeLengthSpecifiers(outputs)

    # Instantiate module
    result += "\n" + modulename + " " + modulename + "_I (\n"
    for input in inputs:
        result += "." + input + "(" + input + "),\n"
    for output in outputs:
        result += "." + output + "(" + output + "),\n"
    result = result[:-2]
    result += ");"
    return result

def getModuleName(file):
    temp = ""
    for char in file:
        if (temp == "module "):
            temp = ""
        if (char == ' ' and temp != "module"):
            return temp
        temp += char


def getPortlist (file):
    portlist = ""
    stop = True
    for char in file:
        if (char == ")"):
            stop = True 
        if (stop == False):
            portlist += char
        if (char == "("):
            stop = False
        if (char == ";"):
            break
    return portlist

def createInitialiseTask(inputs):
    inputs = removeLengthSpecifiers(inputs)
    result = ""
    result += "task initialise; \n"
    result += "    begin\n"

    for input in inputs:
        if (input == "clk"):
            continue
        if (input[-2:] == "_n"):
            result += "        " + input + " <= 1;\n"
        else:
            result += "        " + input + " <= 0;\n"

    result += "        #PERIOD\n"                 
    result += "        reset;\n" 
    result += "    end\n"  
    result += "endtask\n \n" 
    return result          

def createResetTask():
    result = "task reset;\n"
    result += "    begin\n"
    result += "        @(negedge clk) res_n <= 0;\n"
    result += "        #PERIOD\n"
    result += "        @(negedge clk) res_n <= 1;\n"
    result += "    end\n"
    result += "endtask\n \n"

    return result

def createClockInstance():
    result = "parameter PERIOD = 20;\n"
    result += "clock #(.PERIOD(PERIOD)) clk_I (clk);\n"
    return result

def createTb (filename):
    file = readFile(filename)
    file = removeComments(file)

    modulename = getModuleName(file)
    portlist = getPortlist(file)

    inputs = getInputsAndOutputs(portlist)[0]
    outputs = getInputsAndOutputs(portlist)[1]
    result = ""

    result += "module " + modulename + "_tb;\n \n"

    # Declare inputs and outputs
    for input in inputs:
        result += "reg " + input + "; \n"
    for output in outputs:
        result += "wire " + output + "; \n"

    # Instantiate clock and module
    result += createClockInstance()
    result += createInstantiation(modulename, portlist)
     
    
    # Create tasks
    result += "\n \n"
    result += createInitialiseTask(inputs)
    result += createResetTask()

    result += "\n \n" + "endmodule"

    return result 



filename = "file.txt"
tbfilename = "file_tb.txt"
print("Reading " + filename + " and creating testbench...")
writeFile(tbfilename, (createTb(filename)))
print("Testbench skeleton saved as " + tbfilename)
