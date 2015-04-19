#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
((abc){4})
[1-5]{5}
5+
5*
5?
ord(last_c), ord(getescape(regstr, idx+1])+1)
'''

CHAR = 1
REPEAT = 2
ANY = 3
CATCH = 4
RANGE = 5
META = 6
OR = 7
NOTANY = 8

class Node:
    def __init__(self, ntype, parent = None):
        self.type = ntype
        self.c = None
        self.children = []
        self.parent = parent

class RegeX:
    def __init__(self, regstr):
        self.curnode = Node(CATCH)
        self.tokens = self.curnode.children
        self.parsemap = {'[':(ANY, self.parseany), '{':(REPEAT, self.parsecount), '(':(CATCH, self.parseregx)}
        self.escape = {'t':'\t','n':'\n','a':'\a','r':'\r','f':'\f','v':'\v'}
        self.parseregx(regstr)

    def getescape(self, regstr, idx):
        me = regstr[idx]
        if me == '\\':
            idx += 1
            me = regstr[idx]
            if me in 'sdb':
                newnode = Node(META, self.curnode)
            else:
                newnode = Node(CHAR, self.curnode)
                me = self.escape[me] if me in 'tnafrv' else me
        elif me in '.^$':
            newnode = Node(META, self.curnode)
        else:
            newnode = Node(CHAR, self.curnode)
        newnode.c = me
        idx += 1
        return newnode, idx

    def addnode(self, ntype):
        newnode = Node(ntype, self.curnode)
        if ntype != REPEAT:
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
                upbound, idx = self.getescape(regstr, idx)
                newnode.children.append(upbound)
                self.tokens.append(newnode)
            else:
                newnode, idx = self.getescape(regstr, idx)
                self.tokens.append(newnode)
        return idx

    def parsecount(self, regstr, idx):
        regstr_len = len(regstr)
        self.curnode.c = []
        while idx < regstr_len:
            c = regstr[idx]
            if c in ',}':
                if len(self.tokens) > 0:
                    self.curnode.c.append(int(''.join(self.tokens)))
                    self.tokens[:] = []
                idx += 1
                if c == '}':
                    break
            else:
                self.tokens.append(c)
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
                newnode = self.addnode(REPEAT)
                newnode.c = regstr[idx]
                idx+=1
            elif regstr[idx] == '|':
                op = self.curnode.parent
                newnode = Node(OR, op)
                newnode.children.append(self.curnode)
                self.curnode.parent = newnode
                self.curnode = newnode
                self.tokens = newnode.children
                if op:
                    op.children.pop()
                    op.children.append(newnode)
                idx += 1
            else:
                newnode, idx = self.getescape(regstr, idx)
                self.tokens.append(newnode)
        return idx

    def matchnode(self, node, source, idx):
        if node.type == CHAR:
            if source[idx] == node.c:
                return True, idx + 1
        elif node.type == ANY:
            for n in node.children:
                ret, idx = self.matchnode(n, source, idx)
                if ret:
                    return True, idx
        elif node.type == RANGE:
            for aii in range(ord(node.children[0].c), ord(node.children[1].c)+1):
                if chr(aii) == source[idx]:
                    return True, idx + 1
        elif node.type == CATCH:
            for n in node.children:
                ret, idx = self.matchnode(n, source, idx)
                if not ret:
                    return False, idx
            return True, idx

        return False, idx

    def match(self, source):
        return self.matchnode(self.curnode, source, 0)


##################################################
# TEST
##################################################
def displaynode(node,tab=''):
    ast = []
    if node.type == CHAR:
        return '%s[%d] %s\n' % (tab, node.type, node.c)
    elif node.type == REPEAT:
        return '%s[%d] %s\n' % (tab, node.type, str(node.c))
    elif node.type == RANGE:
        return '%s[%d]\n%s%s%s%s\n' % (tab, node.type, tab+' ', displaynode(node.children[0]), tab+' ', displaynode(node.children[1]))
    elif node.type == META:
        return '%s[%d] %s\n' % (tab, node.type, node.c)
    elif node.type == OR:
        ast.append('%s[%d]\n' % (tab, node.type))

    nexttab = tab if node.type == CATCH else tab + ' '
    lasttype = None
    for n in node.children:
        nexttab2 = nexttab if lasttype != REPEAT else nexttab + ' '
        ast.append(displaynode(n, nexttab2))
        lasttype = n.type

    return ''.join(ast)

import sys
r = RegeX('([123a-z]{4,5}){99,}(fuck)*\s*|(1|2)')
sys.stdout.write(displaynode(r.curnode))
print '-----------------------------------'
r = RegeX('(31|2{3})')
sys.stdout.write(displaynode(r.curnode))
print '-----------------------------------'
r = RegeX('44(1[2-3][2-3])[6789](45)[789]')
sys.stdout.write(displaynode(r.curnode))
print r.match('441236457')
