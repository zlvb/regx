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
RANGE = 5
META = 6

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
        self.parsemap = {'[':(ANY, self.parseany), '{':(COUNT, self.parsecount), '(':(TREE, self.parseregx)}
        self.parseregx(regstr)

    def gettrans(self, regstr, idx):
        me = regstr[idx]
        if me == '\\':
            idx += 1
            me = regstr[idx]
            if me in 'sdb':
                newnode = Node(META, self.curnode)
            else:
                newnode = Node(EQUL, self.curnode)
        elif me in '.^$':
            newnode = Node(META, self.curnode)
        else:
            newnode = Node(EQUL, self.curnode)
        newnode.c = me

        idx += 1
        return newnode, idx

    def addnode(self, ntype):
        newnode = Node(ntype, self.curnode)
        if ntype != COUNT:
            self.tokens.append(newnode)
        else:
            self.tokens.insert(-1, newnode)
        return newnode

    def parseany(self, regstr, idx):
        regstr_len = len(regstr)
        while idx < regstr_len:
            if regstr[idx] == ']':
                idx += 1
                break
            elif regstr[idx] == '-':
                idx += 1
                newnode = Node(RANGE, self.curnode)
                newnode.children.append(self.tokens.pop())
                upbound, idx = self.gettrans(regstr, idx)
                newnode.children.append(upbound)
                self.tokens.append(newnode)
            else:
                newnode, idx = self.gettrans(regstr, idx)
                self.tokens.append(newnode)
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

    def levelin(self, ntype, func, regstr, idx):
        newnode = self.addnode(ntype)
        self.curnode = newnode
        self.tokens = newnode.children
        idx+=1
        idx = func(regstr, idx)
        self.curnode = self.curnode.parent
        self.tokens = self.curnode.children
        return idx

    def parseregx(self, regstr, idx = 0):
        regstr_len = len(regstr)
        while idx < regstr_len:
            if regstr[idx] in '[{(':
                args = self.parsemap[regstr[idx]]
                idx = self.levelin(args[0], args[1], regstr, idx)
            elif regstr[idx] == ')':
                idx+=1
                break
            elif regstr[idx] in '?*+':
                newnode = self.addnode(COUNT)
                newnode.c = regstr[idx]
                idx+=1
            else:
                newnode, idx = self.gettrans(regstr, idx)
                self.tokens.append(newnode)
        return idx

##################################################
# TEST
##################################################
def displaynode(node,tab=''):
    if node.type == EQUL:
        return '%s[%d] %s\n' % (tab, node.type, node.c)
    elif node.type == COUNT:
        return '%s[%d] %s\n' % (tab, node.type, str(node.c))
    elif node.type == RANGE:
        return '%s[%d]\n%s%s%s-\n%s%s\n' % (tab, node.type, tab+'\t', displaynode(node.children[0]), tab+'\t', tab+'\t', displaynode(node.children[1]))
    elif node.type == META:
        return '%s[%d] %s\n' % (tab, node.type, node.c)

    ast = []
    for n in node.children:
        ast.append(displaynode(n,tab+'\t'))

    return ''.join(ast)

import sys
r = RegX('([123a-z]{4}){99}(fuck)*\s*')
for n in r.tokens:
    sys.stdout.write(displaynode(n))
