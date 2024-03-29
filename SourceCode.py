import re
ilist = []

class DatabaseAndRegex:
    keyworddict = {"DT":["num", "bool", "string"] , "arr":"arr" , "const":"const" , "TFN":["true","false","none"] , "if":"if" , "else":"else" , "for":"for" , "break":"break" , "return":"ret" , "AM":["public","private"] , "static":"static" , "class":"class" , "virtual":"virtual" , "override":"override" , "interface":"interface" , "abstract":"abstract" , "sealed" : "sealed" , "new":"new" , "void":"void"}
    operatordict = {"not":"!", "pm":["+","-"] , "mdm":["*","/","%"] , "inc_dec":["++","--"] , "lo":["&&","||"] , "ro":["<",">","<=",">=","!=","=="] , "=":"="}   
    operators = ["!","+","-","*","/","%","++","--","&&","||","<",">","<=",">=","!=","==","=","!"]
    punctuators = ["#" , ";" , "(" , ")" , "{" , "}" , "[" , "]" , "," , "." , '"', ":"]

class LexicalAnalyzer:
    flag = True
    flag1 = True
    flag2 = True
    global ilist

    def fileHandler(self):
        try: sfile = open('sourcefile.txt','r')
        except:
            sfile = open('sourcefile.txt','w')
            sfile.close()
        finally: sfile = open('sourcefile.txt','r')
        return sfile

    def wordBreaker(self):
        DBR = DatabaseAndRegex()
        sfile = self.fileHandler()
        sfile = sfile.read().splitlines()
        lineCounter = 0
        for line in sfile:
            i = 0
            lineCounter += 1
            while(i < len(line)):
                cword = line[i]
                if(line[i] == '"'):
                    if((i+1) == len(line)):self.tokenGenrator("invalid lexene",line[i],lineCounter)
                    else:
                        i += 1
                        while(line[i] != '"'):
                            if line[i] == '\\' and i+1 != len(line):
                                cword += line[i] + line[i+1]
                                i += 2
                            elif(i < len(line)):
                                cword += line[i]
                                i += 1
                            if(i == len(line)):break
                            elif(line[i] == '"'):cword = cword + line[i]
                        self.stringHandler(cword,lineCounter)
                elif(line[i] == " "): pass
                elif line[i] in DBR.operators:
                    if ((i+1) != len(line)) and line[i+1] in DBR.operators:
                        if((i+2) < len(line) and (line[i+1] == '+' or line[i+1] == '-') and re.match(r'[\d]',line[i+2])):
                            self.opratorHndler(cword,lineCounter)
                            i += 1
                            i = self.numberBreaker(line,i,line[i],lineCounter)
                        else:
                            i += 1
                            cword = cword + line[i]
                            self.opratorHndler(cword,lineCounter)
                    elif(i+1) != len(line) and re.match(r'[+|-]([\d]|[.])',line[i]+line[i+1]):
                        cword = line[i] + line[i+1]
                        i += 1
                        i = self.numberBreaker(line,i,cword,lineCounter)
                    else:
                        self.opratorHndler(cword,lineCounter)
                elif line[i] in DBR.punctuators:
                    if(line[i] == "#"):i = len(line)
                    elif(i+1) != len(line) and re.match(r'[.][\d]+',line[i]+line[i+1]):
                        cword = line[i] + line[i+1]
                        i += 1
                        i = self.numberBreaker(line,i,cword,lineCounter)
                    else:self.punctuatorHandler(line[i],lineCounter)
                elif re.match(r'([+|-]|[\d]|[.])+',cword):
                    i = self.numberBreaker(line,i,cword,lineCounter)
                elif re.match(r'^([a-z]|[A-Z]|[_])+',cword):
                    i += 1
                    while(i < len(line)):
                        if line[i]=='"' or line[i] == ' ' or line[i] in DBR.punctuators or line[i] in DBR.operators:
                            self.kwIdHandler(cword,lineCounter)
                            i-=1
                            cword = ""
                            break
                        else: cword += line[i]
                        i += 1       
                    if cword != "":
                        self.kwIdHandler(cword,lineCounter)
                else: 
                    cword = ''
                    while(i < len(line) and line[i] != ' '):
                        cword += line[i]
                        i += 1
                    self.tokenGenrator('Invalid Lexene',cword,lineCounter)
                i += 1

    def tokenGenrator(self,cp,cv,lc):
        ilist1 = [cp,cv,lc]
        if self.flag is True:
            self.ilist = [ilist1]
            self.flag = False
        else: self.ilist.append(ilist1)
        del ilist1

    def stringHandler(self,word,counter):       
        if re.match(r'^[\"]+([\w\s\S]*|[\b])[\"]+$',word):
            word = word[1:-1]
            self.tokenGenrator("str_const",word,counter)
        else: self.tokenGenrator("invalidlexene",word,counter)

    def punctuatorHandler(self,word,counter): 
        self.tokenGenrator(word,word,counter)

    def kwIdHandler(self,word,counter):
        self.flag1 = True
        if re.match(r'^[a-zA-Z_]([\w]*)$',word):
            for key,value in DatabaseAndRegex.keyworddict.items():
                if (type(value) == list and word in value) or (type(value) == str and word == value):
                    x = [key for key,value in DatabaseAndRegex.keyworddict.items() if word in value]
                    x = ('[]'.join(x))
                    self.tokenGenrator(x,word,counter)
                    self.flag1 = False
                    break
            if (self.flag1 == True): self.tokenGenrator("id",word,counter)
        else: self.tokenGenrator("invalid lexeme",word,counter)

    def opratorHndler(self,word,counter):
        if word in DatabaseAndRegex.operators: self.opr(word,counter)
        else:
            self.opr(word[0],counter)
            self.opr(word[1],counter)

    def opr(self,word,counter):
        for key,value in DatabaseAndRegex.operatordict.items():
            if str(word) in value:
                self.tokenGenrator(key,word,counter)
                break

    def num_constHandler(self,word,counter):
        if re.match(r'^[+|-]*([\d]*|[\d]*.[\d]+)$',word): self.tokenGenrator("num_const",word,counter)
        else: self.tokenGenrator("invalid lexene", word,counter)

    def numberBreaker(self,line,i,cword,lineCounter):
        i += 1
        self.flag2 = True
        while((i) < len(line) and line[i] != ' ' and line[i] != '"' and (line[i] not in DatabaseAndRegex.operators or line[i] == "+" or line[i] == "-" or line[i] == "*" or line[i] == "/") and (line[i] not in DatabaseAndRegex.punctuators or line[i] == '.')):
            if re.match(r'([+|-]*[\d]*[.][\d]*)',cword) and line[i] == '.':
                i -= 1
                self.flag2 = False
                self.num_constHandler(cword,lineCounter)
                break
            elif (line[i] == "+" or line[i] == "-" or line[i] == "*" or line[i] == "/") and (i+1) < len(line):
                    if re.match(r'[\d]',line[i+1]):
                        if(re.match(r'[+|-]*[\d]+',cword)):
                            self.num_constHandler(cword,lineCounter)
                        i = self.numberBreaker2(line,i,line[i],lineCounter)
                        self.flag2 = False
                        i += 1
                        break
                    elif line[i+1] in DatabaseAndRegex.operators:
                        if(re.match(r'[+|-]*[\d]+',cword)):
                            self.num_constHandler(cword,lineCounter)
                            cword = line[i] + line[i+1]
                            self.opratorHndler(cword,lineCounter)
                        self.flag2 = False
                        i += 1
                        break
            elif((line[i] == "+" or line[i] == "-" or line[i] == "*" or line[i] == "/") and (i+1) <= len(line)):
                        self.num_constHandler(cword,lineCounter)
                        self.flag2 = False
                        i -= 1
                        break
            else:
                cword += line[i]
                i += 1
        if i < len(line) and (line[i] == '"' or line[i] in DatabaseAndRegex.operators or line[i] in DatabaseAndRegex.punctuators):
            i -= 1           
        if (self.flag2): 
            self.num_constHandler(cword,lineCounter)
        return i

    def numberBreaker2(self,line,i,cword,lineCounter):
        if (line[i] == '+' or line[i] == '-' or line[i] == '*' or line[i] == '/') and re.match(r"[\d]",line[i-1]):
            if((i+1) < len(line) and (line[i+1] == '+')):
                return i
            else:
                self.opr(line[i],lineCounter)
                i += 1
                cword = line[i]
        i = self.numberBreaker(line,i,cword,lineCounter)
        return i

class Constants:
    def __init__(self):
        self.name = None
        self.type = None
        self.cat = None
        self.parent = None
        self.access_modifier = None
        self.const = None
        self.parameter_type = None
        self.temp_type = None
        self.ref = None
    def ResetValues(self):
        self.name = None
        self.type = None
        self.cat = None
        self.parent = None
        self.access_modifier = None
        self.const = None
        self.parameter_type = None
        self.ref = None

class SyntaxAnalyzer:
    i = 0
    def __init__(self,ilistm): 
        self.ilistm = ilistm
        self.flag = True
        self.flag_lookupCT = True
        self.objConstants = Constants()
        self.objSementics = SementicsHandler()   
    def superFunction(self):
        while(self.ilistm[self.i][0] != "$"):
            if (self.sst_main()):
                print("successfully process till line: ",self.ilistm[self.i-1][2],"now on char :",self.ilistm[self.i][0])
                continue
            elif self.flag is False:
                return print("Error: Redaclartion Occured at line: ",self.ilistm[self.i][2])
            elif self.flag_lookupCT is False:
                return print("Declartion required at line: ",self.ilistm[self.i][2])                
            else:
                print(self.ilistm[self.i][0])
                return print("Syntax error at line: ",self.ilistm[self.i][2])
    def sst_main(self):
        if(self.interface_st()):
            return True
        elif(self.abstract_class_st()):
            return True
        elif(self.static_class_st()):
            return True
        elif(self.sealed_class_st()):
            return True
        elif(self.class_st()):
            return True
        elif(self.ifelse_st()):
            return True
        elif(self.for_st()):
            return True
        elif(self.const_var()):
            return True
        elif(self.obj()):
            return True
        elif(self.init_arr()):
            return True
        elif(self.ilistm[self.i][0] == "void"):
            self.i += 1
            if(self.function_st()):
                return True
        elif(self.ilistm[self.i][0] == "id"):
            self.i += 1
            if(self.l2()):
                return True
        elif(self.ilistm[self.i][0] == "DT"):
            self.objConstants.type = self.ilistm[self.i][1]
            self.i += 1
            if(self.l3()):
                return True
        elif(self.ilistm[self.i][0] == "arr"):
            self.i += 1
            if(self.l4()):
                return True
        return False

    def interface_st(self):
        if(self.ilistm[self.i][0] == "interface"):
            self.objConstants.type = "interface"
            self.i += 1
            if(self.ilistm[self.i][0] == "id"):
                self.objConstants.name = self.ilistm[self.i][1]
                self.i += 1
                if(self.ilistm[self.i][0] == "("):
                    self.i += 1
                    if(self.ilistm[self.i][0] == ")"):
                        self.i += 1
                        self.flag = self.objSementics.insert(self.objConstants.name,self.objConstants.type,self.objConstants.cat,self.objConstants.parent)
                        if(self.ilistm[self.i][0] == "{" and self.flag == True):
                            self.i += 1
                            if(self.interface1()):
                                self.objSementics.insertCTintoCdataTable(self.objSementics.k)
                                if(self.ilistm[self.i][0] == "}"):
                                    self.i += 1
                                    return True
        return False

    def interface1(self):
        if(self.ilistm[self.i][0] == "}"):
            return True
        elif(self.ilistm[self.i][0] == "AM"):
            self.objConstants.access_modifier = self.ilistm[self.i][1]
            self.i += 1
            if(self.ilistm[self.i][0] == "DT" or self.ilistm[self.i][0] == "void"):
                self.objConstants.type = self.ilistm[self.i][1]
                self.i += 1
                if(self.ilistm[self.i][0] == "id"):
                    self.objConstants.name = self.ilistm[self.i][1]
                    self.i += 1
                    if(self.ilistm[self.i][0] == "("):
                        self.i += 1
                        if(self.params()):
                            self.objConstants.parameter_type = None
                            if(self.ilistm[self.i][0] == ")"):
                                self.i += 1
                                if(self.ilistm[self.i][0] == ";"):
                                    self.objSementics.insertCT(self.objConstants.name,self.objConstants.type,self.objConstants.access_modifier,self.objConstants.cat,self.objConstants.const,self.objConstants.ref)
                                    self.i += 1
                                    if(self.interface1()):
                                        return True
        return False

    def params(self):
        if(self.ilistm[self.i][0] == ")"):
            return True
        elif(self.params1()):
            self.objConstants.type += "=>" + self.objConstants.parameter_type
            return True
        return False

    def params1(self):
        if self.objConstants.parameter_type == None:
            self.objConstants.parameter_type = ""
        if(self.ilistm[self.i][0] == "DT"):
            self.objConstants.parameter_type += self.ilistm[self.i][1]
            self.i += 1
            if(self.ilistm[self.i][0] == "id"):
                self.i += 1
                if(self.params2()):
                    return True
        return False

    def params2(self):
        if(self.ilistm[self.i][0] == ")"):
            return True
        elif(self.params3()):
            return True
        elif(self.ilistm[self.i][0] == "["):
            self.objConstants.parameter_type += self.ilistm[self.i][0]
            self.i += 1
            if(self.ilistm[self.i][0] == "]"):
                self.objConstants.parameter_type += self.ilistm[self.i][0]
                self.i += 1
                if(self.params3()):
                    return True
        return False

    def params3(self):
        if(self.ilistm[self.i][0] == ")"):
            return True
        elif(self.ilistm[self.i][0] == ","):
            self.objConstants.parameter_type += self.ilistm[self.i][0]
            self.i += 1
            if(self.params1()):
                return True
        return False

    def args(self):
        if(self.ilistm[self.i][0] == ")"):
            return True
        elif(self.exp()):
            if(self.args1()):
                return True
        return False

    def args1(self):
        if(self.ilistm[self.i][0] == ")"):
            return True
        elif(self.ilistm[self.i][0] == ","):
            self.i += 1
            if(self.args()):
                return True
        return False

    def class_st(self):
        self.cat = None
        self.parent = None
        if(self.ilistm[self.i][0] == "class"):
            self.objConstants.type = self.ilistm[self.i][0]
            self.i += 1
            if(self.ilistm[self.i][0] == "id"):
                self.objConstants.name = self.ilistm[self.i][1]
                self.i += 1
                if(self.inheritence_st()):
                    self.flag = self.objSementics.insert(self.objConstants.name,self.objConstants.type,self.objConstants.cat,self.objConstants.parent)
                    if(self.ilistm[self.i][0] == "{" and self.flag == True):
                        self.i += 1
                        if(self.mst_class()):
                            self.flag = self.objSementics.insertCT(self.objConstants.name,self.objConstants.type,self.objConstants.access_modifier,self.objConstants.cat,self.objConstants.const,self.objConstants.ref)
                            if(self.ilistm[self.i][0] == "}" and self.flag == True):
                                self.i += 1
                                return True
        return False  

    def inheritence_st(self):
        if(self.ilistm[self.i][0] == "{"):
            return True
        self.objConstants.parent = ""
        if(self.ilistm[self.i][0] == ":"):
            self.i += 1
            if(self.ilistm[self.i][0] == "id"):
                if(self.objSementics.lookup(self.ilistm[self.i][1]) is not False):
                    self.objConstants.parent += self.ilistm[self.i][1]
                    self.i += 1
                    if(self.list6()):
                        return True
        return False

    def list6(self):
        if(self.ilistm[self.i][0] == "{"):
            return True
        if(self.ilistm[self.i][0] == ","):
            self.i += 1
            if(self.ilistm[self.i][0] == "id"):
                if(self.objSementics.lookup(self.ilistm[self.i][1]) is not False):
                # and self.objSementics.defs["type"].values is "interface"):
                    x = self.objSementics.defs["name"].index(self.ilistm[self.i][1])
                    if(self.objSementics.defs["type"][x] is "interface"):
                        self.objConstants.parent += "," + self.ilistm[self.i][1]
                        self.i += 1
                        if(self.list6()):
                            return True
        return False

    def mst_class(self):
        if(self.ilistm[self.i][0] == "}"):
            return True
        elif(self.sst_class()):
            if(self.mst_class()):
                return True
        return False

    def sst_class(self):
        if(self.ilistm[self.i][0] == "AM"):
            self.objConstants.access_modifier = self.ilistm[self.i][1]
            self.i += 1
            if(self.l5()):
                return True
        elif(self.ilistm[self.i][0] == "static"):
            self.objConstants.cat = self.ilistm[self.i][0]
            self.i += 1
            if(self.l1()):
                return True
        elif(self.ilistm[self.i][0] == "DT"):
            self.objConstants.type = self.ilistm[self.i][1]
            self.i += 1
            if(self.l3()):
                return True
        elif(self.ilistm[self.i][0] == "id"):
            self.objConstants.name = self.ilistm[self.i][1]
            self.i += 1
            self.objConstants.temp_type = self.objConstants.temp_type
            if self.ilistm[self.i][0] == "[" or self.ilistm[self.i][1] == "=":
                self.objSementics.insertCT(self.objConstants.name,self.objConstants.type,self.objConstants.access_modifier,self.objConstants.cat,self.objConstants.const,self.objConstants.ref)
            if(self.l6()):
                return True
        elif(self.ilistm[self.i][0] == "arr"):
            self.objConstants.type = self.ilistm[self.i][0]
            self.i += 1
            if(self.l4()):
                return True
        elif(self.init_arr()):
            return True
        elif(self.obj()):
            return True
        elif(self.const_var()):
            return True
        elif(self.v_function()):
            return True
        elif(self.o_function()):
            return True
        elif(self.class_st()):
            return True
        elif(self.abstract_class_st()):
            return True
        elif(self.sealed_class_st()):
            return True
        return False

    def stat(self):
        if(self.ilistm[self.i][0] == "static"):
            self.objConstants.cat = self.ilistm[self.i][1]
            self.i += 1
            return True
        elif(self.ilistm[self.i][0] == "DT" or self.ilistm[self.i][0] == "void" or self.ilistm[self.i][0] == "arr" or self.ilistm[self.i][0] == "id"):
            return True
        return False

    def l1(self):
        if(self.ilistm[self.i][0] == "class"):
            self.objConstants.type = self.ilistm[self.i][0]
            self.i += 1
            if(self.ilistm[self.i][0] == "id"):
                self.objConstants.name = self.ilistm[self.i][1]
                self.i += 1
                if(self.inheritence_st()):
                    self.flag = self.objSementics.insert(self.objConstants.name,self.objConstants.type,self.objConstants.cat,self.objConstants.parent)
                    if(self.ilistm[self.i][0] == "{" and self.flag == True):
                        self.i += 1
                        if(self.mst_static_class()):
                            if(self.ilistm[self.i][0] == "}"):
                                self.i += 1
                                return True
        elif(self.l7()):
            return True
        return False

    def R7(self):
        if(self.ilistm[self.i][0] == ";"):
            self.i +=1
            return True
        elif(self.ilistm[self.i-1][0] != ")"):
            if(self.init()):
                return True
        return False

    def l2(self):
        if(self.ilistm[self.i][0] == "["):
            self.i += 1
            if(self.E1()):
                if(self.ilistm[self.i][0] == "]"):
                    self.i += 1
                    if(self.R1()):
                        return True
        elif(self.calling1()):
            if(self.calling2()):
                if(self.R7()):
                    return True
        elif(self.ilistm[self.i][0] == "="):
            self.i += 1
            if(self.exp()):
                if(self.init2()):
                    return True
        elif(self.function_st()):
            return True
        return False

    def R1(self):
        if(self.ilistm[self.i][0] == "["):
            self.i += 1
            if(self.E1()):
                if(self.ilistm[self.i][0] == "]"):
                    self.i += 1
                    if(self.ilistm[self.i][0] == "="):
                        self.i += 1
                        if(self.exp()):
                            if(self.ilistm[self.i][0] == ";"):
                                self.i += 1
                                return True
        elif(self.ilistm[self.i][0] == "="):
            self.i += 1
            if(self.exp()):
                if(self.init2()):
                    return True
        elif(self.init2()):
            return True
        return False

    def l3(self):
        if(self.ilistm[self.i][0] == "id"):
            self.objConstants.name = self.ilistm[self.i][1]
            if(self.ilistm[self.i+1][0] == "=" or self.ilistm[self.i+1][0] == "," or self.ilistm[self.i+1][0] == ";"):
                self.objSementics.insertCT(self.objConstants.name,self.objConstants.type,self.objConstants.access_modifier,self.objConstants.cat,self.objConstants.const,self.objConstants.ref)
            self.i += 1
            if(self.R2()):
                return True
        return False

    def R2(self):
        if(self.assgn1()):
            if(self.assgn2()):
                return True
        elif(self.ilistm[self.i][0] == "("):
            self.i += 1
            if(self.params()):
                self.objConstants.parameter_type = None
                if(self.ilistm[self.i][0] == ")"):
                    self.objSementics.insertCT(self.objConstants.name,self.objConstants.type,self.objConstants.access_modifier,self.objConstants.cat,self.objConstants.const,self.objConstants.ref)
                    self.i += 1
                    if(self.body()):
                        return True
        return False

    def l4(self):
        if(self.arr_st()):
            return True
        elif(self.ilistm[self.i][0] == "id"):
            self.objConstants.name = self.ilistm[self.i][1]
            self.i += 1
            if self.ilistm[self.i][0] == "=":
                self.objSementics.insertCT(self.objConstants.name,self.objConstants.type,self.objConstants.access_modifier,self.objConstants.cat,self.objConstants.const,self.objConstants.ref)                
            if(self.R6()):
                return True
        return False    

    def R6(self):
        if(self.ilistm[self.i][0] == "("):
            self.i += 1
            if(self.params()):
                self.objConstants.parameter_type = None
                if(self.ilistm[self.i][0] == ")"):
                    self.objSementics.insertCT(self.objConstants.name,self.objConstants.type,self.objConstants.access_modifier,self.objConstants.cat,self.objConstants.const,self.objConstants.ref)
                    self.i += 1
                    if(self.body()):
                        return True
        elif(self.ilistm[self.i][0] == "="):
            self.i += 1
            if(self.ilistm[self.i][0] == "{"):
                self.i += 1
                if(self.values()):
                    if(self.ilistm[self.i][0] == "}"):
                        self.i += 1
                        if(self.ilistm[self.i][0] == ";"):
                            self.i += 1
                            return True
        return False

    def l5(self):
        if(self.stat()):
            if(self.l7()):
                return True
        elif(self.ilistm[self.i][0] == "id"):
            self.objConstants.name = self.ilistm[self.i][1]
            self.i += 1
            if(self.constructor_st()):
                return True
        return False

    def l6(self):
        if(self.ilistm[self.i][0] == "["):
            self.i += 1
            if(self.E1()):
                if(self.ilistm[self.i][0] == "]"):
                    self.i += 1
                    if(self.R1()):
                        return True
        elif(self.R3()):
                return True
        elif(self.ilistm[self.i][0] == "="):
            self.i += 1
            if(self.exp()):
                if(self.init2()):
                    return True
        elif(self.function_st()):
            return True
        elif(self.calling2()):
            if(self.R7()):
                return True
        return False

    def R3(self):
        if(self.ilistm[self.i][0] == "("):
            self.i += 1
            if(self.R4()):
                return True
        return False

    def R4(self):
        if(self.params()):
            self.objConstants.parameter_type = None
            if(self.ilistm[self.i][0] == ")"):
                self.i += 1
                self.objSementics.insertCT(self.objConstants.name,self.objConstants.type,self.objConstants.access_modifier,self.objConstants.cat,self.objConstants.const,self.objConstants.ref)
                if(self.ilistm[self.i][0] == "{"):
                    self.i += 1
                    if(self.c_body()):
                        if(self.ilistm[self.i][0] == "}"):
                            self.i += 1
                        return True
        elif(self.args()):
            if(self.ilistm[self.i][0] == ")"):
                self.i += 1
                if(self.objSementics.lookupCT(self.objConstants.name,self.objConstants.ref) != False):
                    if(self.calling2()):
                        if(self.R7()):
                            return True
                elif(self.objSementics.lookupCT(self.objConstants.name,self.objConstants.ref) == False):
                    self.flag_lookupCT = False
                    return False
        return False

    def l7(self):
        if(self.ilistm[self.i][0] == "DT"):
            self.objConstants.type = self.ilistm[self.i][1]
            self.i += 1
            if(self.l3()):
                return True
        elif(self.ilistm[self.i][0] == "void"):
            self.objConstants.type = self.ilistm[self.i][1]
            self.i += 1
            if(self.function_st()):
                return True
        elif(self.ilistm[self.i][0] == "arr"):
            self.objConstants.type = self.ilistm[self.i][0]
            self.i += 1
            if(self.l4()):
                return True
        elif(self.ilistm[self.i][0] == "id"):
            self.objConstants.name = self.ilistm[self.i][1]
            self.i += 1
            if(self.constructor_st()):
                return True
        return False

    def constructor_st(self):
        if(self.ilistm[self.i][0] == "("):
            self.i += 1
            if(self.params()):
                self.objConstants.parameter_type = None
                if(self.ilistm[self.i][0] == ")"):
                    self.objSementics.insertCT(self.objConstants.name,self.objConstants.type,self.objConstants.access_modifier,self.objConstants.cat,self.objConstants.const,self.objConstants.ref)
                    self.i += 1
                    if(self.ilistm[self.i][0] == "{"):
                        self.i += 1
                        if(self.c_body()):
                            if(self.ilistm[self.i][0] == "}"):
                                self.i += 1
                                return True
        return False

    def function_st(self):
        if(self.ilistm[self.i][0] == "id"):
            self.objConstants.name = self.ilistm[self.i][1]
            self.i += 1
            if(self.ilistm[self.i][0] == "("):
                self.i += 1
                if(self.params()):
                    self.objConstants.parameter_type = None
                    if(self.ilistm[self.i][0] == ")"):
                        self.objSementics.insertCT(self.objConstants.name,self.objConstants.type,self.objConstants.access_modifier,self.objConstants.cat,self.objConstants.const,self.objConstants.ref)
                        self.i += 1
                        if(self.body()):
                            return True
        return False

    def body(self):
        if(self.ilistm[self.i][0] == "{"):
            self.i += 1
            if(self.mst()):
                self.objSementics.insertCTintoCdataTable(self.objSementics.k)
                if(self.ilistm[self.i][0] == "}"):
                    self.i += 1
                    return True
        elif(self.sst()):
            return True
        return False

    def obj(self):
        if(self.ilistm[self.i][0] == "new"):
            self.i += 1
            if(self.ilistm[self.i][0] == "id"):
                self.i += 1
                if(self.ilistm[self.i][0] == "="):
                    self.i += 1
                    if(self.ilistm[self.i][0] == "new"):
                        self.i += 1
                        if(self.ilistm[self.i][0] == "id"):
                            self.i += 1
                            if(self.ilistm[self.i][0] == "("):
                                self.i += 1
                                if(self.args()):
                                    if(self.ilistm[self.i][0] == ")"):
                                        self.i += 1
                                        if(self.subc_call1()):
                                            if(self.ilistm[self.i][0] == ";"):
                                                self.i += 1
                                                return True
        return False

    def const_var(self):
        if(self.ilistm[self.i][0] == "const"):
            self.objConstants.const = True
            self.i += 1
            if(self.list0()):
                return True
        return False

    def list0(self):
        if(self.arr_st()):
            return True
        elif(self.dec_st()):
            return True
        return False

    def init_arr(self):
        if(self.ilistm[self.i][0] == "["):
            self.i += 1
            if(self.ilistm[self.i][0] == "]"):
                self.i += 1
                if(self.init_arr1()):
                    if(self.ilistm[self.i][0] == ";"):
                        self.i += 1
                        return True
        return False

    def init_arr1(self):
        if(self.ilistm[self.i][0] == "id"):
            if(self.objSementics.lookupCT(self.objConstants.name,self.objConstants.ref) != False):
                self.i += 1
                if(self.ilistm[self.i][0] == "="):
                    self.i += 1
                    if(self.ilistm[self.i][0] == "{"):
                        self.i += 1
                        if(self.values()):
                            if(self.ilistm[self.i][0] == "}"):
                                self.i += 1
                                return True
            elif(self.objSementics.lookupCT(self.objConstants.name,self.objConstants.ref) == False):
                self.flag_lookupCT = False
                return False
        elif(self.ilistm[self.i][0] == "["):
            self.i += 1
            if(self.ilistm[self.i][0] == "]"):
                self.i += 1
                if(self.ilistm[self.i][0] == "id"):
                    if(self.objSementics.lookupCT(self.objConstants.name,self.objConstants.ref) != False):
                        self.i += 1
                        if(self.ilistm[self.i][0] == "="):
                            self.i += 1
                            if(self.ilistm[self.i][0] == "{"):
                                self.i += 1
                                if(self.values()):
                                    if(self.ilistm[self.i][0] == "}"):
                                        self.i += 1
                                        return True
                    elif(self.objSementics.lookupCT(self.objConstants.name,self.objConstants.ref) == False):
                        self.flag_lookupCT = False
                        return False
        return False

    def v_function(self):
        if(self.ilistm[self.i][0] == "virtual"):
            self.objConstants.cat = self.ilistm[self.i][1]
            self.i += 1
            if(self.function_st()):
                return True
        return False

    def o_function(self):
        if(self.ilistm[self.i][0] == "override"):
            self.objConstants.cat = self.ilistm[self.i][1]
            self.i += 1
            if(self.function_st()):
                return True
        return False

    def assgn1(self):
        if(self.ilistm[self.i][0] == "," or self.ilistm[self.i][0] == ";"):
            return True
        elif(self.ilistm[self.i][0] == "="):
            self.i += 1
            if(self.exp()):
                return True
        return False

    def assgn2(self):
        if(self.ilistm[self.i][0] == ";"):
            self.i += 1
            return True
        elif(self.ilistm[self.i][0] == ","):
            self.i += 1
            if(self.ilistm[self.i][0] == "id"):
                self.i += 1
                if(self.assgn1()):
                    if(self.assgn2()):
                        return True
        return False

    def arr_st(self):
        if(self.ilistm[self.i][0] == "DT"):
            self.objConstants.type += ":" + self.ilistm[self.i][1]
            self.i += 1
            if(self.ilistm[self.i][0] == "id"):
                self.objConstants.name = self.ilistm[self.i][1]
                self.objSementics.insertCT(self.objConstants.name,self.objConstants.type,self.objConstants.access_modifier,self.objConstants.cat,self.objConstants.const,self.objConstants.ref)
                self.i += 1
                if(self.ilistm[self.i][0] == "="):
                    self.i += 1
                    if(self.ilistm[self.i][0] == "{"):
                        self.i += 1
                        if(self.values()):
                            if(self.ilistm[self.i][0] == "}"):
                                self.i += 1
                                if(self.ilistm[self.i][0] == ";"):
                                    self.i += 1
                                    return True
        return False

    def subc_call1(self):
        if(self.ilistm[self.i][0] == ";"):
            return True
        elif(self.ilistm[self.i][0] == "."):
            self.i += 1
            if(self.subc_call2()):
                return True
        return False

    def subc_call2(self):
        if(self.ilistm[self.i][0] == "id"):
            self.i += 1
            if(self.ilistm[self.i][0] == "("):
                self.i += 1
                if(self.args()):
                    if(self.ilistm[self.i][0] == ")"):
                        self.i += 1
                        if(self.subc_call1()):
                            return True
        return False

    def init(self):
        if(self.init1()):
            if(self.init2()):
                return True
        return False

    def init1(self):
        if(self.ilistm[self.i][0] == "="):
            self.i += 1
            if(self.exp()):
                return True
        elif(self.ilistm[self.i][0] == "["):
            self.i += 1
            if(self.E1()):
                if(self.ilistm[self.i][0] == "]"):
                    self.i += 1
                    if(self.ilistm[self.i][0] == "="):
                        self.i += 1
                        if(self.exp()):
                            return True
        return False

    def init2(self):
        if(self.ilistm[self.i][0] == ","):
            self.i += 1
            self.objConstants.type = self.objConstants.temp_type
            if(self.ilistm[self.i][0] == "id"):
                self.objConstants.name = self.ilistm[self.i][1]
                self.i += 1
                self.objSementics.insertCT(self.objConstants.name,self.objConstants.type,self.objConstants.access_modifier,self.objConstants.cat,self.objConstants.const,self.objConstants.ref)
                if(self.init()):
                    return True
        elif(self.ilistm[self.i][0] == ";"):
            self.objConstants.temp_type = None
            self.i += 1
            return True
        return False

    def calling1(self):
        if(self.ilistm[self.i][0] == "mdm" or self.ilistm[self.i][0] == "pm" or self.ilistm[self.i][0] == ")" or self.ilistm[self.i][0] == "]" or self.ilistm[self.i][0] == "ro" or self.ilistm[self.i][0] == "lo" or self.ilistm[self.i][0] == "," or self.ilistm[self.i][0] == ";" or self.ilistm[self.i][0] == "." or self.ilistm[self.i][0] == "="):
            return True
        elif(self.ilistm[self.i][0] == "("):
            self.i += 1
            if(self.args()):
                if(self.ilistm[self.i][0] == ")"):
                    self.i += 1
                    return True
        return False

    def calling2(self):
        if(self.ilistm[self.i][0] == ";" or self.ilistm[self.i][0] == "=" or self.ilistm[self.i][0] == ")" or self.ilistm[self.i][0] == "}" or self.ilistm[self.i][0] == ","):
            return True
        elif(self.ilistm[self.i][0] == "."):
            self.i += 1
            if(self.ilistm[self.i][0] == "id"):
                self.objConstants.name = self.ilistm[self.i][1]
                self.i += 1
                if(self.objSementics.lookupCT(self.objConstants.name,self.objConstants.ref) != False):
                    if(self.calling1()):
                        if(self.calling2()):
                            return True
                elif(self.objSementics.lookupCT(self.objConstants.name,self.objConstants.ref) == False):
                    self.flag_lookupCT = False
                    return False
        return False

    def values(self):
        if(self.ilistm[self.i][0] == "}"):
            return True
        elif(self.values3()):
            return True
        elif(self.values1()):
            return True
        return False

    def values1(self):
        if(self.ilistm[self.i][0] == "{"):
            self.i += 1
            if(self.values3()):
                if(self.ilistm[self.i][0] == "}"):
                    self.i += 1
                    if(self.values2()):
                        return True
        return False

    def values2(self):
        if(self.ilistm[self.i][0] == "}"):
            return True
        elif(self.ilistm[self.i][0] == ","):
            self.i += 1
            if(self.values1()):
                return True
        return False

    def values3(self):
        if(self.ilistm[self.i][0] == "}"):
            return True
        elif(self.values4()):
            return True
        return False

    def values4(self):
        if(self.exp()):
            if(self.values5()):
                return True
        return False

    def values5(self):
        if(self.ilistm[self.i][0] == "}"):
            return True
        elif(self.ilistm[self.i][0] == ","):
            self.i += 1
            if(self.values4()):
                return True
        return False

    def for_st(self):
        if(self.ilistm[self.i][0] == "for"):
            self.i += 1
            if(self.ilistm[self.i][0] == "("):
                self.i += 1
                if(self.c1()):
                    if(self.c2()):
                        if(self.ilistm[self.i][0] == ";"):
                            self.i += 1
                            if(self.c3()):
                                if(self.ilistm[self.i][0] == ")"):
                                    self.i += 1
                                    if(self.body_wt()):
                                        return True
        return False

    def c1(self):
        if(self.ilistm[self.i][0] == "DT"):
            self.i += 1
            if(self.ilistm[self.i][0] == "id"):
                self.i +=1
                if(self.init()):
                    return True
        elif(self.ilistm[self.i][0] == "id"):
            self.i += 1
            if(self.init()):
                return True
        elif(self.ilistm[self.i][0] == ";"):
            self.i += 1
            return True    
        return False

    def c2(self):
        if(self.ilistm[self.i][0] == ";"):
            return True
        elif(self.exp()):
            return True
        return False

    def c3(self):
        if(self.ilistm[self.i][0] == ")"):
            return True
        elif(self.ilistm[self.i][0] == "id"):
            self.i += 1
            if(self.ilistm[self.i][0] == "inc_dec"):
                self.i += 1
                return True
        elif(self.ilistm[self.i][0] == "inc_dec"):
            self.i += 1
            if(self.ilistm[self.i][0] == "id"):
                self.i += 1
                return True  
        return False

    def arr_ge_init(self):
        if(self.ilistm[self.i][0] == "["):
            self.i += 1
            if(self.E1()):
                if(self.ilistm[self.i][0] == "]"):
                    self.i += 1
                    if(self.arr_ge_init1()):
                        if(self.ilistm[self.i][0] == ";"):
                            self.i += 1
                            return True
        return False

    def arr_ge_init1(self):
        if(self.ilistm[self.i][0] == "["):
            self.i += 1
            if(self.E1()):
                if(self.ilistm[self.i][0] == "]"):
                    self.i += 1
                    if(self.ilistm[self.i][0] == "="):
                        self.i += 1
                        if(self.exp()):
                            return True
        elif(self.ilistm[self.i][0] == "="):
            self.i += 1
            if(self.exp()):
                return True
        return False

    def exp(self):
        if(self.AE()):
            if(self.OE()):
                return True
        return False

    def OE(self):
        if(self.ilistm[self.i][0] == "," or self.ilistm[self.i][0] == ";" or self.ilistm[self.i][0] == ")" or self.ilistm[self.i][0] == "}"):
            return True
        elif(self.ilistm[self.i][0] == "lo"):
            self.i += 1
            if(self.AE()):
                if(OE()):
                    return True
        return False

    def AE(self):
        if(self.RE()):
            if(self.AE_()):
                return True
        return False

    def AE_(self):
        if(self.ilistm[self.i][0] == "lo" or self.ilistm[self.i][0] == "," or self.ilistm[self.i][0] == ";" or self.ilistm[self.i][0] == ")" or self.ilistm[self.i][0] == "}"):
            return True
        elif(self.ilistm[self.i][0] == "lo"):
            self.i += 1
            if(self.RE()):
                if(self.AE_()):
                    return True
        return False

    def RE(self):
        if(self.E()):
            if(self.RE_()):
                return True
        return False

    def RE_(self):
        if(self.ilistm[self.i][0] == "lo" or self.ilistm[self.i][0] == "," or self.ilistm[self.i][0] == ";" or self.ilistm[self.i][0] == ")" or self.ilistm[self.i][0] == "}"):
            return True
        elif(self.ilistm[self.i][0] == "ro"):
            self.i += 1
            if(self.E()):
                if(self.RE_()):
                    return True
        return False

    def E(self):
        if(self.T()):
            if(self.E_()):
                return True
        return False

    def E_(self):
        if(self.ilistm[self.i][0] == "ro" or self.ilistm[self.i][0] == "lo" or self.ilistm[self.i][0] == "," or self.ilistm[self.i][0] == ";" or self.ilistm[self.i][0] == ")" or self.ilistm[self.i][0] == "}"):
            return True
        elif(self.ilistm[self.i][0] == "pm"):
            self.i += 1
            if(self.T()):
                if(self.E_()):
                    return True
        return False

    def T(self):
        if(self.F()):
            if(self.T_()):
                return True
        return False

    def T_(self):
        if(self.ilistm[self.i][0] == "pm" or self.ilistm[self.i][0] == "ro" or self.ilistm[self.i][0] == "lo" or self.ilistm[self.i][0] == "," or self.ilistm[self.i][0] == ";" or self.ilistm[self.i][0] == ")" or self.ilistm[self.i][0] == "}"):
            return True
        elif(self.ilistm[self.i][0] == "mdm"):
            self.i += 1
            if(self.F()):
                if(self.T_()):
                    return True
        return False

    def F(self):
        if(self.ilistm[self.i][0] == "id"):
            self.i += 1
            if(self.F_()):
                return True
        elif(self.ilistm[self.i][0] == "num_const"):
            self.i += 1
            return True
        elif(self.ilistm[self.i][0] == "str_const"):
            self.i += 1
            return True
        elif(self.ilistm[self.i][0] == "not"):
            self.i += 1
            if(self.F()):
                return True
        elif(self.ilistm[self.i][0] == "("):
            self.i += 1
            if(self.exp()):
                if(self.ilistm[self.i][0] == ")"):
                    self.i += 1
                    return True
        elif(self.ilistm[self.i][0] == "inc_dec"):
            self.i += 1
            if(self.ilistm[self.i][0] == "id"):
                self.i += 1
                return True
        return False

    def F_(self):
        if(self.ilistm[self.i][0] == "mdm" or self.ilistm[self.i][0] == "pm" or self.ilistm[self.i][0] == "ro" or self.ilistm[self.i][0] == "lo" or self.ilistm[self.i][0] == "," or self.ilistm[self.i][0] == ";" or self.ilistm[self.i][0] == ")" or self.ilistm[self.i][0] == "id" or self.ilistm[self.i][0] == "}"):
            return True
        elif(self.ilistm[self.i][0] == "inc_dec"):
            self.i += 1
            return True
        elif(self.ilistm[self.i][0] == "("):
            self.i += 1
            if(self.args()):
                if(self.ilistm[self.i][0] == ")"):
                    self.i += 1
                    if(self.calling2()):
                        return True
        elif(self.ilistm[self.i][0] == "."):
            self.i += 1
            if(self.ilistm[self.i][0] == "id"):
                self.i += 1
                if(self.calling1()):
                    if(self.calling2()):
                        return True
        elif(self.ilistm[self.i][0] == "["):
            self.i += 1
            if(self.E1()):
                if(self.ilistm[self.i][0] == "]"):
                    self.i += 1
                    return True
        return False

    def E1(self):
        if(self.T1()):
            if(self.E1_()):
                return True
        return False

    def E1_(self):
        if(self.ilistm[self.i][0] == "ro" or self.ilistm[self.i][0] == "lo" or self.ilistm[self.i][0] == "," or self.ilistm[self.i][0] == ";" or self.ilistm[self.i][0] == ")"):
            return True
        elif(self.ilistm[self.i][0] == "pm"):
            self.i += 1
            if(self.T1()):
                if(self.E1_()):
                    return True
        return False

    def T1(self):
        if(self.F1()):
            if(self.T1_()):
                return True
        return False

    def T1_(self):
        if(self.ilistm[self.i][0] == "pm" or self.ilistm[self.i][0] == "ro" or self.ilistm[self.i][0] == "lo" or self.ilistm[self.i][0] == "," or self.ilistm[self.i][0] == ";" or self.ilistm[self.i][0] == ")"):
            return True
        elif(self.ilistm[self.i][0] == "mdm"):
            self.i += 1
            if(self.F1()):
                if(self.T1_()):
                    return True
        return False

    def F1(self):
        if(self.ilistm[self.i][0] == "id"):
            self.i += 1
            if(self.F1_()):
                return True
        elif(self.ilistm[self.i][0] == "num_const"):
            self.i += 1
            return True
        elif(self.ilistm[self.i][0] == "not"):
            self.i += 1
            if(self.F1()):
                return True
        elif(self.ilistm[self.i][0] == "["):
            self.i += 1
            if(self.E1()):
                if(self.ilistm[self.i][0] == "]"):
                    self.i += 1
                    return True
        elif(self.ilistm[self.i][0] == "inc_dec"):
            self.i += 1
            if(self.ilistm[self.i][0] == "id"):
                self.i += 1
                return True
        return False

    def F1_(self):
        if(self.ilistm[self.i][0] == "mdm" or self.ilistm[self.i][0] == "pm" or self.ilistm[self.i][0] == "ro" or self.ilistm[self.i][0] == "lo" or self.ilistm[self.i][0] == "," or self.ilistm[self.i][0] == ";" or self.ilistm[self.i][0] == ")"):
            return True
        elif(self.ilistm[self.i][0] == "inc_dec"):
            self.i += 1
            return True
        elif(self.calling1()):
            if(self.calling2()):
                return True
        elif(self.ilistm[self.i][0] == "["):
            self.i += 1
            if(self.E1()):
                if(self.ilistm[self.i][0] == "]"):
                    self.i += 1
                    return True
        return False

    def ifelse_st(self):
        if(self.ilistm[self.i][0] == "if"):
            self.i += 1
            if(self.ilistm[self.i][0] == "("):
                self.i += 1
                if(self.exp()):
                    if(self.ilistm[self.i][0] == ")"):
                        self.i += 1
                        if(self.body_wt()):
                            if(self.else_st()):
                                return True
        return False

    def else_st(self):
        if(self.ilistm[self.i][0] == "abstract" or self.ilistm[self.i][0] == "sealed" or self.ilistm[self.i][0] == "class" or self.ilistm[self.i][0] == "static" or self.ilistm[self.i][0] == "am" or self.ilistm[self.i][0] == "void" or self.ilistm[self.i][0] == "id" or self.ilistm[self.i][0] == "}" or self.ilistm[self.i][0] == "const" or self.ilistm[self.i][0] == "DT" or self.ilistm[self.i][0] == "[" or self.ilistm[self.i][0] == "for" or self.ilistm[self.i][0] == "if" or self.ilistm[self.i][0] == "return" or self.ilistm[self.i][0] == "new" or self.ilistm[self.i][0] == "interface" or self.ilistm[self.i][0] == "arr" or self.ilistm[self.i][0] == "$"):
            return True
        if(self.ilistm[self.i][0] == "else"):
            self.i += 1
            if(self.body_wt()):
                return True
        return False

    def body_wt(self):
        if(self.ilistm[self.i][0] == ";"):
            self.i += 1
            return True
        elif(self.body()):
            return True
        return False

    def mst(self):
        if(self.ilistm[self.i][0] == "}"):
            return True
        elif (self.sst()):
            if(self.mst()):
                return True
        return False

    def sst(self):
        if(self.ilistm[self.i][0] == "arr"):
            self.i += 1
            if(self.l4()):
                return True
        elif(self.init_arr()):
            return True
        elif(self.for_st()):
            return True
        elif(self.ifelse_st()):
            return True
        elif(self.ret_st()):
            return True
        elif(self.obj()):
            return True
        elif(self.const_var()):
            return  True
        elif(self.list3_()):
            return True
        elif(self.ilistm[self.i][0] == "id"):
            self.i += 1
            if(self.list2()):
                return True
        return False

    def ret_st(self):
        if(self.ilistm[self.i][0] == "return"):
            self.i += 1
            if(self.exp()):
                if(self.ilistm[self.i][0] == ";"):
                    self.i += 1
                    return True
        return False
 
    def list1(self):
        if(self.ilistm[self.i][0] == "="):
            self.i += 1
            if(self.exp()):
                if(self.init2()):
                    return True
        elif(self.ilistm[self.i][0] == "["):
            self.i += 1
            if(self.E1()):
                if(self.ilistm[self.i][0] == "]"):
                    self.i += 1
                    if(self.ilistm[self.i][0] == "="):
                        self.i += 1
                        if(self.exp()):
                            if(self.list1_):
                                return True
        return False
 
    def list1_(self):
        if(self.ilistm[self.i][0] == ";"):
            self.i += 1
            return True
        elif(self.ilistm[self.i][0] == ","):
            self.i += 1
            if(self.init()):
                return True
        return False
 
    def list2(self):
        if(self.ilistm[self.i][0] == ";"):
            return True
        elif(self.list1()):
            return True
        elif(self.calling1()):
            if(self.calling2()):
                if(self.ilistm[self.i][0] == ";"):
                    self.i += 1
                    return True
        return False
 
    def list3_(self):
        if(self.ilistm[self.i][0] == "static"):
            self.i += 1
            if(self.list3()):
                return True
        elif(self.list3()):
            return True
        elif(self.ilistm[self.i][0] == "AM"):
            self.i += 1
            if(self.stat()):
                if(self.list3()):
                    return True
        return False
 
    def list3(self):
        if(self.ilistm[self.i][0] == "DT"):
            self.i += 1
            if(self.list4()):
                return True
        elif(self.ilistm[self.i][0] == "void"):
            self.i += 1
            if(self.ilistm[self.i][0] == "id"):
                self.i += 1
                if(self.ilistm[self.i][0] == "("):
                    self.i += 1
                    if(self.params()):
                        self.objConstants.parameter_type = None
                        if(self.ilistm[self.i][0] == ")"):
                            self.i += 1
                            if(self.body()):
                                return True
        return False
 
    def list4(self):
        if(self.ilistm[self.i][0] == "id"):
            self.i += 1
            if(self.list5()):
                return True
        return False
 
    def list5(self):
        if(self.assgn1()):
            if(self.assgn2()):
                return True
        elif(self.ilistm[self.i][0] == "("):
            self.i += 1
            if(self.params()):
                self.objConstants.parameter_type = None
                if(self.ilistm[self.i][0] == ")"):
                    self.i += 1
                    if(self.body()):
                        return True
        return False
 
    def c_body(self):
        if(self.ilistm[self.i][0] == "}"):
            return True
        elif(self.ilistm[self.i][0] == "id"):
            self.i += 1
            if(self.list1()):
                if(self.c_body()):
                    return True
        elif(self.init_arr()):
            if(self.c_body()):
                return True
        elif(self.const_var()):
            if(self.c_body()):
                return True
        return False
 
    def mst_sealed_class(self):
        if(self.ilistm[self.i][0] == "}"):
            return True
        elif(self.sst_sealed_class()):
            if(self.mst_sealed_class()):
               return True
        return False
 
    def sst_sealed_class(self):
        if(self.ilistm[self.i][0] == "am"):
            self.i += 1
            if(self.l5()):
                return True
        elif(self.ilistm[self.i][0] == "static"):
            self.i += 1
            if(self.l1()):
                return True
        elif(self.ilistm[self.i][0] == "DT"):
            self.i += 1
            if(self.l3()):
                return True
        elif(self.ilistm[self.i][0] == "id"):
            self.i += 1
            if(self.l6()):
                return True
        elif(self.ilistm[self.i][0] == "arr"):
            self.i += 1
            if(self.l4()):
                return True
        elif(self.init_arr()):
            return True
        elif(self.obj()):
            return True
        elif(self.const_var()):
            return True
        elif(self.class_st()):
            return True
        elif(self.sealed_class_st()):
            return True
        elif(self.abstract_class_st()):
            return True
        elif(self.ilistm[self.i][0] == "virtual"):
            self.i += 1
            if(self.ret_type()):
                if(self.function_st()):
                    return True
        elif(self.ilistm[self.i][0] == "override"):
            self.i += 1
            if(self.ret_type()):
                if(self.function_st()):
                    return True
        return False
 
    def ret_type(self):
        if(self.ilistm[self.i][0] == "void"):
            self.i += 1
            return True
        elif(self.ilistm[self.i][0] == "DT"):
            self.i += 1
            return True
        elif(self.ilistm[self.i][0] == "arr"):
            self.i += 1
            return True
        elif(self.ilistm[self.i][0] == "id"):
            self.i += 1
            return True
        return False

    def sealed_class_st(self):
        if(self.ilistm[self.i][0] == "sealed"):
            self.objConstants.cat = "sealed"
            self.i += 1
            if(self.ilistm[self.i][0] == "class"):
                self.objConstants.type = "class"
                self.i += 1
                if(self.ilistm[self.i][0] == "id"):
                    self.objConstants.name = self.ilistm[self.i][1]
                    self.i += 1
                    if(self.inheritence_st()):
                        self.flag = self.objSementics.insert(self.objConstants.name,self.objConstants.type,self.objConstants.cat,self.objConstants.parent)
                        if(self.ilistm[self.i][0] == "{" and self.flag == True):
                            self.i += 1
                            if(self.mst_sealed_class()):
                                self.flag = self.objSementics.insertCT(self.objConstants.name,self.objConstants.type,self.objConstants.access_modifier,self.objConstants.cat,self.objConstants.const,self.objConstants.ref)
                                if(self.ilistm[self.i][0] == "}" and self.flag == True):
                                    self.i += 1
                                    return True
        return False

    def static_class_st(self):
        if(self.ilistm[self.i][0] == "static"):
            self.objConstants.cat = "static"
            self.i +=  1
            if(self.ilistm[self.i][0] == "class"):
                self.objConstants.type = "class"
                self.i += 1
                if(self.ilistm[self.i][0] == "id"):
                    self.objConstants.name = self.ilistm[self.i][1]
                    self.i += 1
                    if(self.inheritence_st()):
                        self.flag = self.objSementics.insert(self.objConstants.name,self.objConstants.type,self.objConstants.cat,self.objConstants.parent)
                        if(self.ilistm[self.i][0] == "{" and self.flag == True):
                            self.i += 1
                            if(self.mst_static_class()):
                                self.flag = self.objSementics.insertCT(self.objConstants.name,self.objConstants.type,self.objConstants.access_modifier,self.objConstants.cat,self.objConstants.const,self.objConstants.ref)
                                if(self.ilistm[self.i][0] == "}" and self.flag == True):
                                    self.i += 1
                                    return True
        return False

    def mst_static_class(self):
        if(self.ilistm[self.i][0] == "}"):
            return True
        elif(self.sst_static_class()):
            if(self.mst_static_class()):
                return True
        return False

    def sst_static_class(self):
        if(self.ilistm[self.i][0] == "static"):
            self.objConstants.cat = self.ilistm[self.i][1]
            self.i += 1
            if(self.l1()):
                return True
        elif(self.class_st()):
            return True
        elif(self.sealed_class_st()):
            return True
        elif(self.abstract_class_st()):
            return True
        return False

    def abstract_class_st(self):
        if(self.ilistm[self.i][0] == "abstract"):
            self.objConstants.cat = "abstract"
            self.i += 1
            if(self.ilistm[self.i][0] == "class"):
                self.objConstants.type = "class"                
                self.i += 1
                if(self.ilistm[self.i][0] == "id"):
                    self.objConstants.name = self.ilistm[self.i][1]
                    self.i += 1
                    if(self.inheritence_st()):
                        self.flag = self.objSementics.insert(self.objConstants.name,self.objConstants.type,self.objConstants.cat,self.objConstants.parent)
                        if(self.ilistm[self.i][0] == "{" and self.flag == True):
                            self.i += 1
                            if(self.mst_abstract_class()):
                                self.objSementics.insertCTintoCdataTable(self.objSementics.k)
                                if(self.ilistm[self.i][0] == "}"):
                                    self.i += 1
                                    return True
        return False

    def mst_abstract_class(self):
        if(self.ilistm[self.i][0] == "}"):
            return True
        elif(self.sst_abstract_class()):
            if(self.mst_abstract_class()):
                return True
        return False
    
    def sst_abstract_class(self):
        if(self.ilistm[self.i][0] == "abstract"):
            self.i += 1
            if(self.R5()):
                return True
        elif(self.ilistm[self.i][0] == "AM"):
            self.objConstants.access_modifier = self.ilistm[self.i][1]
            self.i += 1
            if(self.l5()):
                return True
        elif(self.ilistm[self.i][0] == "static"):
            self.i += 1
            if(self.l1()):
                return True
        elif(self.ilistm[self.i][0] == "DT"):
            self.i += 1
            if(self.l3()):
                return True
        elif(self.ilistm[self.i][0] == "id"):
            self.i += 1
            if(self.l6()):
                return True
        elif(self.ilistm[self.i][0] == "arr"):
            self.i += 1
            if(self.l4()):
                return True
        elif(self.init_arr()):
            return True
        elif(self.obj()):
            return True
        elif(self.const_var()):
            return True
        elif(self.v_function()):
            return True
        elif(self.o_function()):
            return True
        elif(self.class_st()):
            return True
        elif(self.sealed_class_st()):
            return True
        return False

    def R5(self):
        if(self.ret_type()):
            if(self.function_st()):
                return True
        elif(self.ilistm[self.i][0] == "class"):
            self.i += 1
            if(self.ilistm[self.i][0] == "id"):
                self.i += 1
                if(self.inheritence_st()):
                    if(self.ilistm[self.i][0] == "{"):
                        self.i += 1
                        if(self.mst_abstract_class()):
                            if(self.ilistm[self.i][0] == "}"):
                                self.i += 1
                                return True
        return False


class SementicsHandler:
    def __init__(self):
        self.objConstants = Constants()
        self.j = 0
        self.k = 0
        self.defs = {
            "name" : [],
            "type" : [],
            "cat" : [],
            "parent" : [],
            "ref" : []
        }
        self.class_data = {
            "name" : [],
            "type" : [],
            "access_modifier" : [],
            "type_modifier" : [],
            "constant" : [],
            "ref" : []
        }
        self.class_data_table = {}
        self.function_data = {
        "name" : [],
        "type" : [],
        "scope" : [],
        "ref" : []
        }

    def lookup(self,name1):
        if name1 in self.defs["name"]:
            self.j = self.defs["name"].index(name1)
            return [self.defs["type"][self.j],self.defs["cat"][self.j],self.defs["parent"][self.j],self.defs["ref"][self.j]]
        else:
            return False

    def lookupCT(self,name1,ref1):
        if (name1 in self.class_data["name"] and ref1 == self.class_data["ref"][self.class_data["name"].index(name1)]):
            self.j = self.class_data["name"].index(name1)
            return [self.class_data["type"][self.j],self.class_data["am"][self.j],self.class_data["tm"][self.j],self.class_data["const"][self.j],self.class_data["ref"][self.j]]
        else:
            return False

    def lookupFT(self,name1,ref1):
        if (name1 in self.function_data["name"] and ref1 == self.function_data["ref"][self.function_data["name"].index(name1)]):
            i = self.function_data["name"].index(name1)
            return [self.function_data["type"][i],self.function_data["scope"][i],self.function_data["ref"][i]]
        else:
            return False  

    def insert(self,name1,type1,cat1,parent1):
        self.k = self.k + 1
        if self.lookup(name1) is False:
            self.defs["name"].append(name1)
            self.defs["type"].append(type1)
            self.defs["cat"].append(cat1)
            self.defs["parent"].append(parent1)
            self.defs["ref"].append(self.k)
            self.objConstants.ResetValues()
            return True
        elif self.lookup(name1) is not False :
            return False
        else : print("error in insert at : ",name1)

    def insertCT(self,name1,type1,am1,tm1,const1,ref1):
        if self.lookupCT(name1,ref1) is False:
            self.class_data["name"].append(name1)
            self.class_data["type"].append(type1)
            self.class_data["access_modifier"].append(am1)
            self.class_data["type_modifier"].append(tm1)
            self.class_data["constant"].append(const1)
            self.class_data["ref"].append(self.k)
            self.objConstants.ResetValues()
            return True
        elif self.lookupCT(name1,ref1) is not False :
            return False
        else : print("unexpected error in insertCT at : ",name1)

    def insertCTintoCdataTable(self,l):
        self.class_data_table.update({str(l):self.class_data})
        self.class_data = {
            "name" : [],
            "type" : [],
            "access_modifier" : [],
            "type_modifier" : [],
            "constant" : [],
            "ref" : []
        }

    def insertFT(self,name1,type1,scope1,ref1):
        if self.lookupFT(name1,ref1) is not False:
            self.defs["name"].append(name1)
            self.defs["type"].append(type1)
            self.defs["scope"].append(scope1)
            self.defs["ref"].append(ref1)
        elif self.lookupFT(name1,ref1) is False :
            print("Error: Redaclartion occured in class data table...")
        else : print("error in insert FT at : ",name1)

# Creating Lexemes
objl = LexicalAnalyzer()
objl.wordBreaker()

# adding end token to the lexeme
objl.ilist.append(["$", "$", str(objl.ilist[len(objl.ilist)-1][2])])

# writing tokens into the seprate file
with open('tokens.txt', 'w') as f:
    for x in objl.ilist:
        f.write("%s\n" %('['+x[0]+' , '+x[1]+' , '+str(x[2])+']'))
f.close()

# Analyzing syntax
syntaxAnalyzerObj = SyntaxAnalyzer(objl.ilist)
syntaxAnalyzerObj.superFunction()

# writing tables into the tables.txt
with open('tables.txt', 'w') as f:
    f.write("\t Refrence Table\n")
    for x,y in syntaxAnalyzerObj.objSementics.defs.items():
        f.write("%s\n" %(x+": "+str(y)))
    f.write("\n\n \t Class Data Tables\n")
    for x,y in syntaxAnalyzerObj.objSementics.class_data_table.items():
        f.write("%s\n" %(x+": "+str(y)))
f.close()