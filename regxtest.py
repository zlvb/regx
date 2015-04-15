#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
((abc){4})
[1-5]{5}
5+
5*
5?
ord(last_c), ord(gettrans(regstr, idx+1])+1)
'''

EQUL = 1
COUNT = 2
ANY = 3
TREE = 4
DOT = 5
RANGE = 6

class Node:
    def __init__(self, ntype, parent = None):
        self.type = ntype
        self.c = None
        self.children = []
        self.parent = parent


class RegX:
    def __init__(self, regstr):
        self.curnode = Node(TREE)
        self.tokens = self.curnode.children
        self.parseregx(regstr)

    def gettrans(self, regstr, idx, parent):
        newnode = Node(EQUL, self.curnode)
        newnode.c = regstr[idx]
        idx += 1
        return newnode, idx

    def addnode(self, ntype, pos=0):
        newnode = Node(ntype, self.curnode)
        if pos == 0:
            self.tokens.append(newnode)
        else:
            self.tokens.insert(pos, newnode)
        return newnode

    def parseany(self, regstr, idx):
        regstr_len = len(regstr)
        while idx < regstr_len:
            if regstr[idx] == '\\':
                newnode, idx = self.gettrans(regstr, idx, self.curnode)
                self.tokens.append(newnode)
            elif regstr[idx] == ']':
                idx += 1
                break
            elif regstr[idx] == '-':
                idx += 1
                newnode = Node(RANGE, self.curnode)
                newnode.children.append(self.tokens.pop())
                upbound, idx = self.gettrans(regstr, idx, self.curnode)
                newnode.children.append(upbound)
                self.tokens.append(newnode)
            else:
                newnode = self.addnode(EQUL)
                newnode.c = regstr[idx]
                idx += 1
        return idx

    def parsecount(self, regstr, idx):
        regstr_len = len(regstr)
        while idx < regstr_len:
            if regstr[idx] == '}':
                self.curnode.c = int(''.join(self.tokens))
                idx += 1
                break
            else:
                self.tokens.append(regstr[idx])
                idx += 1
        return idx

    def parseregx(self, regstr, idx = 0):
        regstr_len = len(regstr)
        while idx < regstr_len:
            if regstr[idx] == '[':
                newnode = self.addnode(ANY)
                self.curnode = newnode
                self.tokens = newnode.children
                idx+=1
                idx = self.parseany(regstr, idx)
                self.curnode = self.curnode.parent
                self.tokens = self.curnode.children
            elif regstr[idx] == '{':
                newnode = self.addnode(COUNT, -1)
                self.curnode = newnode
                self.tokens = newnode.children
                idx+=1
                idx = self.parsecount(regstr, idx)
                self.curnode = self.curnode.parent
                self.tokens = self.curnode.children
            elif regstr[idx] == '(':
                newnode = self.addnode(TREE)
                self.curnode = newnode
                self.tokens = newnode.children
                idx+=1
                idx = self.parseregx(regstr, idx)
                self.curnode = self.curnode.parent
                self.tokens = self.curnode.children
            elif regstr[idx] == ')':
                idx+=1
                break
            elif regstr[idx] in '?*+':
                newnode = self.addnode(COUNT, -1)
                newnode.c = regstr[idx]
                idx+=1
            elif regstr[idx] == '.':
                idx+=1
            elif regstr[idx] == '\\':
                newnode, idx = self.gettrans(regstr, idx, self.curnode)
            else:
                newnode = self.addnode(EQUL)
                newnode.c = regstr[idx]
                idx+=1
        return idx

##################################################
# TEST

def displaynode(node,tab=''):
    if node.type == EQUL:
        return '%s[%d] %s\n' % (tab, node.type, node.c)
    elif node.type == COUNT:
        return '%s[%d] %s\n' % (tab, node.type, str(node.c))
    elif node.type == RANGE:
        return '%s[%d]\n%s%s%s-\n%s%s\n' % (tab, node.type, tab+'\t', displaynode(node.children[0]), tab+'\t', tab+'\t', displaynode(node.children[1]))
    elif node.type == DOT:
        return '%s[%d] %s\n' % (node.type, '.')

    ast = []
    for n in node.children:
        ast.append(displaynode(n,tab+'\t'))

    return ''.join(ast)

import sys
r = RegX('([123a-z]{4}){99}(fuck)*')
for n in r.tokens:
    sys.stdout.write(displaynode(n))
