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

def displaynode(node):
    if node.type == EQUL:
        return '[%d] %s\n' % (node.type, node.c)
    elif node.type == COUNT:
        return '[%d] %s\n' % (node.type, str(node.c))
    elif node.type == RANGE:
        return '[%d] %s-%s\n' % (node.type, node.children[0], node.children[1])
    elif node.type == DOT:
        return '[%d] %s\n' % (node.type, '.')

    ast = []
    for n in node.children:
        ast.append(displaynode(n))

    return ''.join(ast)


class RegX:
    def __init__(self, regstr):
        self.curnode = Node(TREE)
        self.tokens = self.curnode.children
        self.parseregx(regstr)

    def gettrans(self, regstr, idx):
        return regstr[idx]

    def parseany(self, regstr, idx):
        regstr_len = len(regstr)
        last_c = None
        while idx < regstr_len:
            if regstr[idx] == '\\':
                last_c = gettrans(regstr,idx+1)
                newnode = Node(EQUL, self.curnode)
                newnode.c = last_c
                self.tokens.append(newnode)
                idx += 2
            elif regstr[idx] == ']':
                idx += 1
                break
            elif regstr[idx] == '-':
                newnode = Node(RANGE, self.curnode)
                newnode.children.append(last_c)
                newnode.children.append(self.gettrans(regstr, idx+1))
                self.tokens.append(newnode)
                idx+=2
            else:
                last_c = regstr[idx]
                newnode = Node(EQUL, self.curnode)
                newnode.c = last_c
                self.tokens.append(newnode)
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
                newnode = Node(ANY, self.curnode)
                self.tokens.append(newnode)
                self.curnode = newnode
                self.tokens = newnode.children
                idx+=1
                idx = self.parseany(regstr, idx)
                self.curnode = self.curnode.parent
                self.tokens = self.curnode.children
            elif regstr[idx] == '{':
                newnode = Node(COUNT, self.curnode)
                self.tokens.insert(-1, newnode)
                self.curnode = newnode
                self.tokens = newnode.children
                idx+=1
                idx = self.parsecount(regstr, idx)
                self.curnode = self.curnode.parent
                self.tokens = self.curnode.children
            elif regstr[idx] == '(':
                newnode = Node(TREE, self.curnode)
                self.tokens.append(newnode)
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
                newnode = Node(COUNT, self.curnode)
                newnode.c = regstr[idx]
                self.tokens.insert(-1, newnode)
                idx+=1
            elif regstr[idx] == '.':
                pass
            elif regstr[idx] == '\\':
                pass
            else:
                newnode = Node(EQUL, self.curnode)
                newnode.c = regstr[idx]
                self.tokens.append(newnode)
                idx+=1
        return idx

import sys
r = RegX('([123a-z]{4}){99}')
for n in r.tokens:
    sys.stdout.write(displaynode(n))
