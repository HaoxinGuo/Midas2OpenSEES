# -*- coding: utf-8 -*-
"""
Created on Fri May 10 14:43:06 2019

@author: 12101
"""
import os


def getKeyWords(datas):
    keyword = {}
    modelkey = []
    modelvalue = []
    a = -1
    for data in datas:
        a = a + 1
        if datas[a][0][0] == '*':
            #print(datas[a][0][0])
            keyword[str(datas[a])] = a
    sorted(keyword.items(),key = lambda item:item[1])
    for key in keyword:
        modelkey.append(key)
    for value in keyword.values():
        modelvalue.append(value)
    return modelkey,modelvalue
                
         
def GetNode(datas,modelkey,modelvalue):
    Node = []
    nodestart = 0
    nodeend = 0
    a = -1
    for temp in modelkey:
        a = a + 1
        if temp == '[\'*NODE    ; Nodes\\n\']':
            #print(modelkey[a])
            nodestart = modelvalue[a] + 2
            nodeend = modelvalue[a+1] - 1
    for i in range(nodestart,nodeend):
        node = datas[i]
        Node.append(('node',int(node[0]), float(node[1]), float(node[2]), float(node[3])))    
    with  open('node.tcl', 'w') as f_out:
        f_out.write('model BasicBuilder -ndm 3 -ndf 6;' + '\n')
        for lin in Node:        
            lin2 = list(lin)
            f_out.write(lin2[0] + '\t' + str(lin2[1]) +  '\t' + str(lin2[2]) + '\t' + str(lin2[3]) + '\t' + str(lin2[4]) + '\n')       
    print('node.tcl Finish')

def GetSec(datas,Matl,Elements):
    poisson = 0.20
    matlnum = [];
    matlvalue = [];
    for key in Matl:
        matlnum.append(key.split())
    for value in Matl.values():
        matlvalue.append(value.split())
    Elst = {}
    for i in range(len(matlnum)):
        Elst[str(matlnum[i][0])]= str(matlvalue[i][0])
    # print(Elst)
    a = -1; 
    SecNum ={}
    for data in datas:
        a = a + 1; 
        if data[0][:5] == ' SECT':
            SecNum[str(data[0][6:])] = a + 1
    SecValue = []
    Secnum = []
    for value in SecNum.values():
        sec = datas[value]
        SecValue.append(sec)
        #print(sec)
    for key in SecNum:
        Secnum.append(key)
    with  open('Section.tcl', 'w') as f_out:
        for lin,i,Ele in zip(SecValue,Secnum,Elements):        
            lin2 = list(lin)
            f_out.write('set ' + 'A'+i.lstrip() + ' = ' + str(lin2[0]).lstrip()+ '\n')
            f_out.write('set ' + 'E'+ str(Ele[6]) + ' = ' + str(Elst[str(Ele[6])])+ '\n')
            f_out.write('set ' + 'G'+ str(Ele[6]) + ' = ' + '[' + 'expr ' +  '$' + 'E'  +str( Ele[6]) + '/ (2+ 2 * poisson)'  + ']'+ '\n')
            f_out.write('set ' + 'J'+i.lstrip() + ' = ' + str(lin2[3]).lstrip() + '\n')
            
            f_out.write('set ' + 'Iy'+i.lstrip() + ' = ' + str(lin2[5]).lstrip())
            f_out.write('set ' + 'Iz'+i.lstrip() + ' = ' + str(lin2[4]).lstrip() + '\n\n')
    print('Section.tcl Finish')

def GetEle(datas,modelkey,modelvalue):
    Elements = []
    Elestart = 0
    Eleend = 0
    a = -1
    for temp in modelkey:
        a = a + 1
        if temp == '[\'*ELEMENT    ; Elements\\n\']':
            #print(modelkey[a])
            Elestart = modelvalue[a] + 6
            Eleend =   modelvalue[a+1] - 1
            #print(Eleend)
    for i in range(Elestart,Eleend):
        Ele = datas[i]
        if Ele[1] == ' BEAM  ':
            Ele[1] = 'elasticBeamColumn'
            Elements.append(('element',Ele[1], int(Ele[0]), int(Ele[4]), int(Ele[5]),int(Ele[3]),int(Ele[2])))
        elif Ele[1] == ' TRUSS ':
            Ele[1] = 'Truss'
            Elements.append(('element',Ele[1], int(Ele[0]), int(Ele[4]), int(Ele[5]),int(Ele[3]),int(Ele[2])))
        else:
            Elements.append(('element',Ele[1], int(Ele[0]), int(Ele[4]), int(Ele[5]),int(Ele[3]),int(Ele[2])))
    with  open('Element.tcl', 'w') as f_out:
        for lin in Elements:        
            lin2 = list(lin)
            f_out.write(lin2[0] + '\t' + str(lin2[1]) +  '\t' + str(lin2[2]) + '\t' + str(lin2[3]) + '\t' + str(lin2[4])  + '\t' 
                        + '$A'+str(lin2[5]) + '\t' + '$E'+ str(lin2[6]) + '\t' + '$G'+ str(lin2[6]) + '\t' + '$J'+str(lin2[5])  + '\t' + '$Iy'+str(lin2[5])+ '\t'  + '$Iz'+str(lin2[5]) + '\t'
                        + '\n' )
    print('Element.tcl Finish')
    return Elements

def GetFix(datas,modelkey,modelvalue):
    Fix = []
    Fixdata = []
    Fixstart = 0
    Fixend = 0
    a = -1
    Fix1 =[]
    Fix2 = []
    for temp in modelkey:
        a = a + 1
        if temp == '[\'*CONSTRAINT    ; Supports\\n\']':
            #print(modelkey[a])
            Fixstart = modelvalue[a] + 2
            Fixend =   modelvalue[a+1] - 1
            break
    if Fixstart == Fixend:
        Fixend = Fixend + 1
    Fixdata=datas[Fixstart:Fixend]
    #print(Fixdata)
    for temp in Fixdata:
        a = temp[0].split()
        #print(a)
        for value in a:
            Fix.append(value)
    #print(Fix)
    for index in range(len(Fix)):
        #print(Fix[index].find('to'))
        if Fix[index].find('to') == -1:
            Fix1.append(Fix[index])
        else:
            value1 =  int(Fix[index].find('to'))
           #print(value1)           
            if Fix[index].find('by') != -1:
               value2 =  int(Fix[index].find('by'))
               a = int(Fix[index][0:value1])
               b = int(Fix[index][value1+2:(value2)])
               c = int(Fix[index][(value2+2):])
               for d in range(a,b+c,c):              
                   Fix2.append(d)
            else:
                value2 = value1 + 2
                a = int(Fix[index][0:value1])
                b = int(Fix[index][value2:])
                c = 1
                for d in range(a,b+c,c): 
                    Fix2.append(d)
    Fix = Fix1 + Fix2
    with  open('Fix.tcl', 'w') as f_out:
        for value in Fix:
            f_out.write('fix ' + str(value) + ' 1 1 1 1 1 1' + '\n')
    return Fix
  
def GetMatl(datas,modelkey,modelvalue):
    Matl = {}
    a = -1
    for temp in modelkey:
        a = a + 1
        if temp == '[\'*DGN-MATL    ; Modify Steel(Concrete) Material\\n\']':
            #print(modelkey[a])
            Matlstart = modelvalue[a] + 14
            Matlend =   modelvalue[a+1] - 1
            break
    maxnum = 0;
    for i in range(Matlstart,Matlend):
        maxnum = max(int(datas[i][0]),maxnum)
    for i in range(0,maxnum+1):
        Matl[str(i)] = str(0)
    for i in range(Matlstart,Matlend):
        if datas[i][1] == ' CONC ':
            Matl[datas[i][0]] = datas[i][14]
            #print(type(datas[i][0].split()))
            #print(type(datas[i][0]))
        else:
            Matl[datas[i][0]] = str(0)
    return Matl


def Transtoby(Tran):
    length = 0
    Fix1 = []
    Fix2 =[]
    Fix =[]
    #Fixx = []
    Atran ={}
    for key,value in zip(Tran,Tran.values()):
        Fixx = []
        Fix1 = []
        Fix2 =[]
        Fix =[]
        length = len(value.split())
        Fix = value.split()
        #print(Fix)
        #print(Fix[0])
        for index in range(0,length):            
            if Fix[index].find('to') == -1:
                Fix1.append(Fix[index])
            else:
                value1 =  int(Fix[index].find('to'))
           #print(value1)           
                if Fix[index].find('by') != -1:
                   value2 =  int(Fix[index].find('by'))
                   a = int(Fix[index][0:value1])
                   b = int(Fix[index][value1+2:(value2)])
                   c = int(Fix[index][(value2+2):])
                   for d in range(a,b+c,c):              
                       Fix2.append(d)
                   #print(Fix2)
                else:
                    value2 = value1 + 2
                    a = int(Fix[index][0:value1])
                    b = int(Fix[index][value2:])
                    c = 1
                    for d in range(a,b+c,c): 
                        Fix2.append(d)
                    #print(Fix2)
            Fixx = Fix1 + Fix2
            Atran[key] = Fixx
    return Atran
            
def GetRigidLink(datas,modelkey,modelvalue):
    Rigid = {}
    a = -1
    rigidstart = 0
    rigidend =0
    for temp in modelkey:
        a = a + 1
        if temp == '[\'*RIGIDLINK    ; Rigid Link\\n\']':
            rigidstart = modelvalue[a] + 2
            rigidend = modelvalue[a+1] - 1
    for i in range(rigidstart,rigidend):
        Rigid[(datas[i][0].split()[0])] = datas[i][2]
    Rtran = Transtoby(Rigid)
    with  open('equalDOF.tcl', 'w') as f_out:
        for key,value in zip(Rtran,Rtran.values()):        
            for i in range(0,len(value)):
                f_out.write('equalDOF ' + str(key) + ' ' + str(value[i]) +  ' 1 2 3 4 5 6' + '\n')
    print('EqualDOF Finish!')


# 自输入材料值


# 文件处理
# print('Please Enter the file name')
# tclfile = input("Please Enter the file name of Midas: ")
#with open(tclfile) as f_in:
    
# tclfile, ndm = flatten_tcl(tclfiles)
tclfile = 'SongpuBridge.tcl'
#tclfile = '11.tcl'
ndm = 3

datas = []

with open(tclfile) as f:
    for line in f:
        datas.append(line.split(','))
#for data in datas:
#    print(data[0][0])
#print(datas[5][0][0])
modelkey,modelvalue = getKeyWords(datas)
GetNode(datas,modelkey,modelvalue)

Fix = GetFix(datas,modelkey,modelvalue)
Matl = GetMatl(datas,modelkey,modelvalue)
Elements = GetEle(datas,modelkey,modelvalue)
GetSec(datas,Matl,Elements)
GetRigidLink(datas,modelkey,modelvalue)

