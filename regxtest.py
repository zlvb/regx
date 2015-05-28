#!/usr/bin/env python
# -*- coding: utf-8 -*-

CHAR = 1
REPEAT = 2
ANY = 3
CATCH = 4
RANGE = 5
META = 6
OR = 7
NOTANY = 8

EOF = -1

class SafeString:
    def __init__(self, source):
        self.source = source
        self.len = len(source)

    def __len__(self):
        return self.len

    def __getitem__(self, idx):
        if idx >= self.len:
            return EOF
        return self.source[idx]

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
            if me in 'sdbSDwWB':
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
            elif regstr[idx] == '^':
                self.curnode.type = NOTANY
                idx += 1
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
                else:
                    self.curnode.c.append(sys.maxint if c=='}' else 0)
                idx += 1
                if c == '}':
                    self.curnode.c.append(0)
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
            rc = regstr[idx]
            if rc in '[({':
                args = self.parsemap[regstr[idx]]
                idx = self.levelin(args[0], args[1], regstr, idx)
                if rc == '{':
                    repnode = self.tokens[-2]
                    nextnode = self.tokens.pop()
                    nextnode.parent = repnode
                    repnode.children.append(nextnode)
            elif rc == ')':
                idx+=1
                break
            elif rc in '?*+':
                newnode = self.addnode(REPEAT)
                newnode.c = regstr[idx]
                repnode = self.tokens[-2]
                nextnode = self.tokens.pop()
                nextnode.parent = repnode
                repnode.children.append(nextnode)
                idx+=1
            elif rc == '|':
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

    def addrowcol(self, node, nextstate):
        pass

    def tree2nfa(self, curstate, node, nextstate = None):
        if node.type in (CHAR, RANGE, META):
            return self.addrowcol(curstate, node, nextstate)

        if node.type == OR:
            for n in node.children:
                self.tree2nfa(curstate, n)
        elif node.type == REPEAT:
            beginstate = curstate
            for idx, n in enumerate(node.children):
                if idx == len(node.children) - 1:
                    curstate = self.tree2nfa(curstate, n, beginstate)
                else:
                    curstate = self.tree2nfa(curstate, n)
        elif node.type == CATCH:
            for n in node.children:
                curstate = self.tree2nfa(curstate, n)

    def matchchildren(self, node, source, idx):
        for n in node.children:
            ret, idx = self.matchnode(n, source, idx)
            if not ret:
                return False, idx
        return True, idx

    def isdigit(self, c):
        return c >= '0' and c <= '9'

    def ischar(self, c):
        return (c >= 'a' and c <= 'z') or (c >= 'A' and c <= 'Z')

    def matchnode(self, node, source, idx):
        if source[idx] == EOF:
            return False, idx
        if node.type == CHAR:
            if source[idx] == node.c:
                return True, idx + 1
        elif node.type == META:
            if node.c == '.':
                if source[idx] != '\n':
                    return True, idx + 1
                return False, idx
            elif node.c == 's':
                if source[idx] in ' \n\r\t':
                    return True, idx + 1
                return False, idx
            elif node.c == 'S':
                if not source[idx] in ' \n\r\t':
                    return True, idx + 1
                return False, idx
            elif node.c == 'd':
                if self.isdigit(source[idx]):
                    return True, idx + 1
                return False, idx
            elif node.c == 'D':
                if not self.isdigit(source[idx]):
                    return True, idx + 1
                return False, idx
            elif node.c == 'w':
                c = source[idx]
                if self.ischar(c) or self.isdigit(c) or c == '_':
                    return True, idx + 1
                return False, idx
            elif node.c == 'W':
                c = source[idx]
                if not self.ischar(c) and not self.isdigit(c):
                    return True, idx + 1
                return False, idx
        elif node.type == ANY:
            for n in node.children:
                ret, idx = self.matchnode(n, source, idx)
                if ret:
                    return True, idx
        elif node.type == NOTANY:
            for n in node.children:
                ret, idx = self.matchnode(n, source, idx)
                if ret:
                    return False, idx
            return True, idx + 1
        elif node.type == RANGE:
            for aii in xrange(ord(node.children[0].c), ord(node.children[1].c)+1):
                if aii == ord(source[idx]):
                    return True, idx + 1
        elif node.type == CATCH:
            return self.matchchildren(node, source, idx)
        elif node.type == REPEAT:
            if node.c == '*':
                lb = 0
                ub = sys.maxint
            elif node.c == '+':
                lb = 1
                ub = sys.maxint
            elif node.c == '?':
                lb = 0
                ub = 1
            elif isinstance(node.c, list):
                lb = node.c[0]
                ub = node.c[1]
            return self.matchrepeate(node, source, idx, lb, ub)


        return False, idx

    def matchrepeate(self, node, source, idx, lb, ub):
        for it in xrange(lb):
            oldidx = idx
            ret, idx = self.matchchildren(node, source, idx)
            if not ret:
                return False, oldidx
        t = ub - lb
        for it in xrange(t):
            oldidx = idx
            ret, idx = self.matchchildren(node, source, idx)
            if not ret:
                return True, oldidx
        return True, idx

    def match(self, source):
        source = SafeString(source)
        ret, idx = self.matchnode(self.curnode, source, 0)
        return ret and source[idx] == EOF, idx


##################################################
# TEST
##################################################
def displaynode(node,tab=''):
    ast = []
    if node.type == CHAR:
        return '%s[%d] %s\n' % (tab, node.type, node.c)
    elif node.type == RANGE:
        return '%s[%d]\n%s%s%s%s\n' % (tab, node.type, tab+'>', displaynode(node.children[0]), tab+'>', displaynode(node.children[1]))
    elif node.type == META:
        return '%s[%d] %s\n' % (tab, node.type, node.c)
    elif node.type == OR:
        ast.append('%s[%d]\n' % (tab, node.type))
    elif node.type == REPEAT:
        ast.append('%s[%d] %s\n' % (tab, node.type, str(node.c)))

    for n in node.children:
        ast.append(displaynode(n, tab+'>'))

    return ''.join(ast)

import sys
#r = RegeX('([123a-z]{4,5}){99,}(fuck)*\s*|(1|2)')
#sys.stdout.write(displaynode(r.curnode))
#print '-----------------------------------'
#r = RegeX('(31|2{3})')
#sys.stdout.write(displaynode(r.curnode))
#print '-----------------------------------'
#r = RegeX('44(1[2-3][2-3])[6789](45)[789]')
#sys.stdout.write(displaynode(r.curnode))
#print r.match('441236457')
r = RegeX(r'<\w*>\d*</\w*>')
sys.stdout.write(displaynode(r.curnode))
print r.match('<head>123</head>')

r = RegeX(r'a(bb)+c')
sys.stdout.write(displaynode(r.curnode))
print r.match('abbbc')

'''
(abc|abd)|(eee|eec)

or   0
  or 0
  	 0 a 1 b 2 c 3
	 0 a 1 b 2 d 4
  or
  	eee
	eec

   0   1   2   3   4   5   6   7   8
0      a               e

1          b

2              c   d

3

4

5                          e

6                              e   c

7

8

(abc)*

r 0
  0 a 1 b 2 c 3 a   0
                EOF 4

   0   1
0


'''
