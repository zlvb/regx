#include <vector>
#include <map>

enum NodeType
{
    NT_ROOT,
    NT_REPEATED,
    NT_CHAR,
    NT_ANYCHAR,
    NT_BEGIN,
    NT_END,
};

struct EDGE
{
    NodeType type;
    char ch;
};

bool operator<(const EDGE &x, const EDGE &y)
{
    if (x.type < y.type)
        return true;
    return x.type == y.type && x.ch < y.ch;
}

typedef std::vector<int> NEXT;
typedef std::map<EDGE,  NEXT> STATE;
typedef std::map<int,  STATE> NFA;

bool CheckEdge(const EDGE &edge, char ch, int findIdx)
{
    switch (edge.type)
    {
    case NT_CHAR:
    case NT_REPEATED:    
        return edge.ch == ch;
    case NT_ANYCHAR:
        return ch != '\0';
    case NT_END:
        return ch == '\0';
    case NT_BEGIN:
        return findIdx == 0;
    default:
        return false;
    }
}

int Match(const char *p, const NFA &nfa, int terminal);
int Match(const char *p, const NFA &nfa, int terminal, int &current, int findIdx)
{
    if (current == terminal)
        return 0;

    auto nfa_it = nfa.find(current);
    if (nfa_it == nfa.end())
    {
        return -1;
    }

    const STATE &state = nfa_it->second;
    const char *op = p++;
    for (auto it = state.begin(); it != state.end(); ++it)
    {
        if (CheckEdge(it->first, *op, findIdx))
        {
            const char *nextp = it->first.type == NT_BEGIN?op:p;
            const NEXT &vec_next = it->second;
            for (size_t i = 0; i < vec_next.size(); i++)
            {        
                current = vec_next[i];
                if (Match(nextp, nfa, terminal, current, findIdx) == 0)
                    return 0;
            }
            
        }
    }    

    return -1;
}

int Match(const char *p, const NFA &nfa, int terminal)
{    
    int findIdx = 0;    
    do 
    {
        int current = 0;
        if (Match(p, nfa, terminal, current, findIdx) == 0)
            return findIdx; // 返回最终匹配的位置
        findIdx++;
    } while (*p++ != '\0');
    
    return -1;
}

struct Node
{
    Node(NodeType eType, char ch = '\0')
        :type(eType),c(ch) { }
    Node():type(NT_ROOT),c('\0'){}
    NodeType type;
    std::vector<Node> children;
    char c;
};

int Parse(const char *regx, size_t regLen, Node &parent)
{
    for (int i = 0; i < (int)regLen; i++)
    {
        char c = regx[i];
        switch (c)
        {
        case '*':{
            Node newNode(NT_REPEATED, '*');            
            Node &last = parent.children.back();
            newNode.children.push_back(last);
            parent.children.pop_back();
            parent.children.push_back(newNode);
        } break;
        case '.': {
            Node newNode(NT_ANYCHAR);
            parent.children.push_back(newNode);
        } break;
        case '^': {
            if (i != 0)
                return -i;
            Node newNode(NT_BEGIN);
            parent.children.push_back(newNode);
        } break;
        case '$': {
            if (i != regLen - 1)
                return -i;
            Node newNode(NT_END);
            parent.children.push_back(newNode);
        } break;
        default:{
            Node newNode(NT_CHAR, c);
            parent.children.push_back(newNode);
        }break;
        }
    }

    return 0;
}

int Parse(const char *regx, Node *pNode)
{
    size_t len = strlen(regx);
    return Parse(regx, len, *pNode);
}

void Tree2NFA(const Node &node, NFA *pNfa, int &current)
{
    NFA &nfa = *pNfa;
    if (node.type == NT_ROOT)
    {
        for (size_t i = 0; i < node.children.size(); i++)
        {
            Tree2NFA(node.children[i], pNfa, current);
        }
    }
    else if (node.type == NT_REPEATED)
    {
        EDGE edge = {node.type, node.children[0].c};
        nfa[current][edge].push_back(current);
    }
    else
    {
        EDGE edge = {node.type, node.c};
        nfa[current][edge].push_back(current+1);
        current++;
    }
}

int Tree2NFA(const Node &node, NFA *pNfa)
{
    int current = 0;    
    Tree2NFA(node, pNfa, current);
    return current;
}

int TestCase(const char *regx, const char *str)
{
    Node root;
    int ret = Parse(regx, &root);
    if (ret != 0)
        return ret;

    NFA nfa;
    int terminal = Tree2NFA(root, &nfa);

    return Match(str, nfa, terminal);
}

int main()
{
    int i = TestCase("^aa*.b$", "aaaab");
    i = TestCase("a*.b", "caab");
    i = TestCase("a*.b", "cccaab");
    i = TestCase("^a*.b", "cccaab");
    i = TestCase("a*.b", "cccaabbbbbbbbbbbbc");
    i = TestCase("a*.b$", "cccaabbbbbbbbbbbbc");
    return i;
}
