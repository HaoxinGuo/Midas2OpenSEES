# -*- coding: utf-8 -*-
"""
Created on Tue May  7 18:56:57 2019

@author: 12101
"""

import os

def getNodeEleSec(datas):
    '''
    函数getNodeEleSec(datas) 定义得到节点 单元 截面信息 输入文件为datas 即去掉，号的mct文件
    输出文件： 
    nodes 节点信息 node 
    'node',int(node[0]), float(node[1]), float(node[2]), float(node[3])
    节点标识号 节点号 X Y Z    
    elements 单元信息
    ('element',Ele[1], int(Ele[0]), int(Ele[4]), int(Ele[5]),int(Ele[3]))
    单元标识号 单元类型 单元号  Inode Jnode 单元截面标号 
    SecValue 截面信息
    A面积 抗扭J 抗弯Ix 抗弯Iy
    Secnum 截面标号 #Midas截面标号
    重要变量：
    *NODE    ; Nodes 节点关键字
    *ELEMENT    ; Elements 单元关键字
    *MATERIAL    ; Material 材料关键字
    nodestart/end  节点起始位置结束位置数据
    Elestart/end  单元起始位置结束位置数据
    SecNum 截面数据及截面标号 
     BEAM  识别梁的类型
    '''
    nodes = []
    SecNum ={}
    nodestart = 0
    nodeend =0
    Elestart = 0
    Eleend = 0
    fixstart= 0
    fixend = 0
    fix = []
    a = -1;
    for data in datas:
        a = a + 1;    
        if '*NODE    ; Nodes' in data[0]:
            #print(datas[a])
            nodestart = a + 2
        if '*ELEMENT    ; Elements' in data[0]:
            #print(datas[a])
            Elestart = a + 6
            nodeend = a - 2
        if '*MATERIAL    ; Material' in data[0]:
            Eleend = a - 2
        
        if data[0][:5] == ' SECT':
            SecNum[str(data[0][6:])] = a+1
        
        if data[0][:10] == '*CONSTRAIN':
           # print(data[0][:10])
            fixstart = a +2
        if data[0][:12] == '*ELASTICLINK':
            fixend = a - 2
            print(fixend)
            
    for i in range(nodestart,nodeend):
        node = datas[i]
        nodes.append(('node',int(node[0]), float(node[1]), float(node[2]), float(node[3])))
    
    elements = []
    for i in range(Elestart,Eleend):
        Ele = datas[i]
        if Ele[1] == ' BEAM  ':
            Ele[1] = 'elasticBeamColumn'
            elements.append(('element',Ele[1], int(Ele[0]), int(Ele[4]), int(Ele[5]),int(Ele[3])))
    
    SecValue = []
    Secnum = []
    for value in SecNum.values():
        #print(value)
        #print(key)
        sec = datas[value]
        SecValue.append(sec)
        #print(sec)
    for key in SecNum:
        Secnum.append(key)
        #print(key)
    if fixstart == fixend:
        for value in range(fixstart,fixend+1):
            fix.append((str(datas[fixstart][0]).split(),datas[fixstart][1].split()))
    else:
        for value in range(fixstart,fixend):
             fix.append((str(datas[fixstart][0]).split(),datas[fixstart][1].split()))
    #print(str(datas[fixstart][0]).split())
    return nodes,elements,SecValue,Secnum,fix

def WriteFunc(nodes,elements,SecValue,Secnum,fix):
    '''
    输入文件：
            nodes: 节点数据
            elements: 单元数据
            SecValue: 截面值数据
            Secnum: 截面编号数据
    输出文件：
            node.tcl 节点
            Element.tcl 单元
            Section.tcl 截面    
    '''

# 写节点文件
    with  open('node.tcl', 'w') as f_out:
        f_out.write('model BasicBuilder -ndm 3 -ndf 6;' + '\n')
        for lin in nodes:        
            lin2 = list(lin)
            f_out.write(lin2[0] + '\t' + str(lin2[1]) +  '\t' + str(lin2[2]) + '\t' + str(lin2[3]) + '\t' + str(lin2[4]) + '\n')
        for lin in fix:
            lin2 = list(lin)
            print(len(lin2[0]))
            if lin2[1] == ['111111']:
                for j in range(len(lin2[0])):
                    f_out.write('fix ' + lin2[0][j] + ' 1 1 1 1 1 1' + '\n') 
    
# 写截面文件    
    with  open('Section.tcl', 'w') as f_out:
        f_out.write('set ' + 'E1' + ' = ' + str(E1) + '\n')
        f_out.write('set ' + 'G1' + ' = ' + str(G1) + '\n')
        for lin,i in zip(SecValue,Secnum):        
            lin2 = list(lin)
            f_out.write('set ' + 'A'+i.lstrip() + ' = ' + str(lin2[0]).lstrip()+ '\n') 
            f_out.write('set ' + 'J'+i.lstrip() + ' = ' + str(lin2[3]).lstrip() + '\n')
            f_out.write('set ' + 'Iy'+i.lstrip() + ' = ' + str(lin2[5]).lstrip())
            f_out.write('set ' + 'Iz'+i.lstrip() + ' = ' + str(lin2[4]).lstrip() + '\n\n')
    
# 写单元文件    
    with  open('Element.tcl', 'w') as f_out:
        for lin in elements:        
            lin2 = list(lin)
            f_out.write(lin2[0] + '\t' + str(lin2[1]) +  '\t' + str(lin2[2]) + '\t' + str(lin2[3]) + '\t' + str(lin2[4])  + '\t' 
                        + '$A'+str(lin2[5]) + '\t' + '$E1' + '\t' + '$G1' + '\t' + '$J'+str(lin2[5])  + '\t' + '$Iy'+str(lin2[5])+ '\t'  + '$Iz'+str(lin2[5]) + '\t'
                        + '\n' )  
            
# 输入文件即mct文件
# tclfiles = ('11.tcl',)

# 自输入材料值
poisson = 0.20
E1 = 34.5e9  
G1 = E1/(2*(1 + poisson))

# 文件处理
# print('Please Enter the file name')
tclfile = input("输入文件名:")
#with open(tclfile) as f_in:
    
# tclfile, ndm = flatten_tcl(tclfiles)

ndm = 3

datas = []

with open(tclfile) as f:
    for line in f:
        datas.append(line.split(','))

nodes,elements,SecValue,Secnum,fix = getNodeEleSec(datas)  
WriteFunc(nodes,elements,SecValue,Secnum,fix)

  







