import sys


class DependenciesTree:
    """
        One node of the parse tree.
        It is a group of words of same NamedEntityTag (e.g. George Washington).
    """
    def __init__(self, word, namedentitytag='undef', dependency='undef', child=None):
        self.wordList = [(word[:word.rindex('-')],int(word[word.rindex('-')+1:]))]
        self.namedEntityTag = namedentitytag
        self.dependency = dependency
        self.child = child or []
        self.text = "" # only relevant for the root node
        # parent attribute will also be available after computation of the tree

    def string(self):
        # Concatenation of the words of the root
        w = ' '.join(x[0] for x in self.wordList)
        s=''
        # Adding the definition of the root (dot format)
        t=''
        if(self.namedEntityTag != 'O' and self.namedEntityTag != 'undef'):
            t+= " [{0}]".format(self.namedEntityTag)
        s+="\t\"{0}\"[label=\"{1}{2}\",shape=box];\n".format(self.wordList[0][0]+str(self.wordList[0][1]),w,t)
        # Adding definitions of the edges
        for n in self.child:
            s+="\t\"{0}\" -> \"{1}\"[label=\"{2}\"];\n".format(self.wordList[0][0]+str(self.wordList[0][1]),n.wordList[0][0]+str(n.wordList[0][1]),n.dependency)
        # Recursive calls
        for n in self.child:
            s+=n.string()+'\n'
        return s

    def __str__(self):
        return "digraph relations {"+"\n{0}\tlabelloc=\"t\"\tlabel=\"{1}\";\n".format(self.string(),self.text)+"}\n"
        
    def merge(self,other):
        """
            Merge the root of the two given trees into one single node.
            The result is stored in node 'self'.
        """
        self.child += other.child
        self.wordList = other.wordList + self.wordList
        self.wordList.sort(key = lambda x: x[1])
        other.parent.child.remove(other)
        other.wordList = ["should not be used"]

def compute_edges(r,name_to_nodes):
    """
        Compute the edges of the dependence tree.
        Take in input a piece of the result produced by StanfordNLP, and the
        map from names to nodes.
    """
    for edge in r['indexeddependencies']:
        try:
            n1 = name_to_nodes[edge[1]]
        except KeyError:
            n1 = DependenciesTree(edge[1])
            name_to_nodes[edge[1]] = n1
        try:
            n2 = name_to_nodes[edge[2]]
        except KeyError:
            n2 = DependenciesTree(edge[2])
            name_to_nodes[edge[2]] = n2
        # n1 is the parent of n2
        n1.child = n1.child+[n2]
        n2.parent = n1
        n2.dependency = edge[0]

def compute_tags(r,name_to_nodes):
    """
        Compute the tags of the dependence tree nodes.
        Take in input a piece of the result produced by StanfordNLP, and the
        map from names to nodes.
    """
    index=1
    # Computation of the tags of the nodes
    for word in r['words']:
        if word[0].isalnum() or word[0] == '$' or  word[0] == '%':
            w=word[0]+'-'+str(index) # key in the name_to_nodes map
            index+=1
            try:
                n = name_to_nodes[w]
                if word[1]['NamedEntityTag'] != 'O':
                    n.namedEntityTag = word[1]['NamedEntityTag']
            except KeyError:        # this node does not exists (e.g. 'of' preposition)
                pass

def compute_tree(r):
    """
        Compute the dependence tree.
        Take in input a piece of the result produced by StanfordNLP.
        If foo is this result, then r = foo['sentences'][0]
        Return the root of the tree (word 'ROOT-0').
    """
    name_to_nodes = {} # map from the original string to the node
    compute_edges(r,name_to_nodes)
    compute_tags(r,name_to_nodes)
    name_to_nodes['ROOT-0'].text = r['text']
    return name_to_nodes['ROOT-0']

def remove_det(t):
    """
        Remove all nodes with 'det' dependency.
    """
    for c in t.child:
        remove_det(c)
    if t.dependency == 'det':
        for c in t.child:
            c.parent = t.parent
        t.parent.child += t.child
        t.parent.child.remove(t)

def mergeNamedEntityTagChildParent(t):
    """
        Merge all nodes n1,n2 such that:
            * n1 is parent of n2
            * n1 and n2 have a same namedEntityTag
    """
    for c in t.child:
        mergeNamedEntityTagChildParent(c)
    same_tag_child = set()
    if t.namedEntityTag != 'undef':
        for c in t.child:
            if c.namedEntityTag == t.namedEntityTag:
                same_tag_child.add(c)
        for c in same_tag_child:
            t.merge(c)

def mergeNamedEntityTagSisterBrother(t):
    """
        Merge all nodes n1,n2 such that:
            * n1 and n2 have a same parent
            * n1 and n2 have a same namedEntityTag
            * n1 and n2 have a same dependency
    """
    for c in t.child:
        mergeNamedEntityTagSisterBrother(c)
    tagToNodes = {}
    for c in t.child:
        if c.namedEntityTag != 'undef':
            try:
                tagToNodes[c.namedEntityTag+c.dependency].add(c)
            except KeyError:
                tagToNodes[c.namedEntityTag+c.dependency] = set([c])
    for sameTag in tagToNodes.values():
        x = sameTag.pop()
        for other in sameTag:
            x.merge(other)

def simplify(t):
    remove_det(t)
    mergeNamedEntityTagChildParent(t)
    mergeNamedEntityTagSisterBrother(t)
