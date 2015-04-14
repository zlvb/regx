'''
((abc){4})
[1-5]{5}
5+
5*
5?
'''
EQUL = 1
COUNT = 2
ANY = 3
TREE = 4

class Node    
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

    def parseany(self, regstr):
        
    def parseregx(self, regstr, idx = 0):
        regstr_len = len(regstr)
        while True:
            if regstr[idx] == '[':
                newnode = Node(ANY, self.curnode)
                self.tokens.append(newnode)
                idx = self.parseany(regstr, idx)
            elif regstr[idx] == '{':
                newnode = Node(COUNT, self.curnode)
                self.tokens.insert(-1, newnode)
                idx+=1
            elif regstr[idx] == '(':
                newnode = Node(TREE, self.curnode)
                self.curnode = newnode
                self.tokens = newnode.children
                parseregx(regstr, idx)
            elif regstr[idx] == ')':
                self.curnode = self.curnode.parent
                self.tokens = self.curnode.children
                idx+=1
            elif regstr[idx] == '?':
                newnode = Node(COUNT, self.curnode)
                newnode.c = regstr[idx]
                self.tokens.insert(-1, newnode)
                idx+=1
            elif regstr[idx] == '+':
                newnode = Node(COUNT, self.curnode)
                newnode.c = regstr[idx]
                self.tokens.insert(-1, newnode)
                idx+=1
            elif regstr[idx] == '*':
                newnode = Node(COUNT, self.curnode)
                newnode.c = regstr[idx]
                self.tokens.insert(-1, newnode)
                idx+=1
            elif regstr[idx] == '.':                
                pass
            elif:
                pass