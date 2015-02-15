import sys
from .questionWordProcessing import identifyQuestionWord, questionWordDependencyTree
from .dependencyTree import Word, DependenciesTree, computeTree
from .preprocessingMerge import preprocessingMerge
from copy import deepcopy
from .data.exceptions import GrammaticalError
from .data.questionWord import strongQuestionWord

##############################
# General analysis functions #
##############################

def remove(t,qw):
    t.parent.child.remove(t)

def impossible(t,qw):
    raise GrammaticalError(t.dependency,"unexpected dependency")

def ignore(t,qw):
    pass

def merge(t,qw):
    t.parent.merge(t,True)

##############################
# Special analysis functions #
##############################

def amodRule(t,qw):
    if t.wordList[0].pos == 'JJ':
        if len(t.child) > 0 and t.child[0].wordList[0].pos == 'RBS':
            assert len(t.child) == 1 and len(t.child[0].child) == 0
            merge(t.child[0],qw)
            t.dependency = 'connectorUp'
            return
    if t.namedEntityTag != 'ORDINAL' and t.wordList[0].pos != 'JJS': # [0] : must be improved? (search in the whole list?)
        assert t.parent is not None
        merge(t,qw)
    else:
        t.dependency = 'connectorUp'

def nnRule(t,qw):
    if t.namedEntityTag != t.parent.namedEntityTag and t.namedEntityTag != 'undef':
        t.dependency = 'R5'
    else:
        merge(t,qw)

def prepRule(t,qw):
    if t.parent.wordList[0].pos[0] == 'V':
        t.dependency = 'R3'
    else:
        t.dependency = 'R5'

##########################
# General analysis rules #
##########################

dependenciesMap1 = {
    'undef'     : 'R0',
    'root'      : 'R0',
    'inst_of'   : 'R6', # <<
    'dep'       : 'R1',
        'aux'       : remove,
            'auxpass'   : remove,
            'cop'       : impossible,
        'arg'       : impossible,
            'agent'     : 'R5', # <<
            'comp'      : 'R3',
                'acomp'     : 'R3',
                'ccomp'     : 'R5',
                'xcomp'     : 'R5',
                'pcomp'     : 'R3',
                'obj'       : impossible,
                    'dobj'      : 'R3',
                    'iobj'      : 'R3',
                    'pobj'      : 'R3',
            'subj'      : impossible,
                'nsubj'     : 'R5', # <<
                    'nsubjpass'    : 'R3',# <<
                'csubj'     : impossible,
                    'csubjpass'    : impossible,
        'cc'        : impossible,
        'conj'      : 'R0',
            'conj_and'  : ignore,
            'conj_or'   : ignore,
            'conj_negcc': ignore,
        'expl'      : remove,
        'mod'       : impossible,
            'amod'      : amodRule,
            'appos'     : 'R0', # <<
            'advcl'     : 'R5',
            'det'       : remove,
            'predet'    : remove,
            'preconj'   : remove,
            'vmod'      : 'R3',
            'mwe'       : merge,
                'mark'      : remove,
            'advmod'    : 'R5',
                'neg'       : 'connectorUp', # need a NOT node
            'rcmod'     : 'R5',
                'quantmod'  : remove,
            'nn'        : nnRule,
            'npadvmod'  : 'R5',
                'tmod'      : 'R3',
            'num'       : merge,
            'number'    : merge,
            'prep'      : prepRule, # <<
            'poss'      : 'R5',
            'possessive': impossible,
            'prt'       : merge,
        'parataxis' : remove,
        'punct'     : impossible,
        'ref'       : impossible,
        'sdep'      : impossible,
            'xsubj'     : 'R3',
        'goeswith'  : merge,
        'discourse' : remove
}

def propagateType(t,qw):
    """
        Propagate locally the type of the subtree
    """
    if t.parent != None:
        if t.parent.subtreeType == 'undef':
            t.parent.subtreeType = t.subtreeType
        assert t.subtreeType == 'undef' or t.subtreeType == t.parent.subtreeType
        t.subtreeType = t.parent.subtreeType

dependenciesMap2 = {         # how to handle a -b-> c
    'R0'        : propagateType,  # normalize(c)
    'R1'        : propagateType,  # !c
    'R2'        : propagateType,  # if c is a leaf: (normalize(c),!a,?), otherwise: normalize(c)
    'R3'        : ignore,         # (?,!a,normalize(c))
    'R4'        : ignore,         # (?,normalize(c),!a)
    'R5'        : ignore,         # (normalize(c),!a,?)
    'R6'        : propagateType,  # (?,instance of,c)
    'R7'        : ignore,         # (!a,normalize(c),?)
    'Rspl'      : propagateType,  # superlative
    'RconjT'    : propagateType,  # top of a conjunction relation
    'RconjB'    : propagateType,  # bottom of a conjunction relation
    'Rexist'    : propagateType
}

def collapseMap(t,depMap,qw,down=True):
    """
        Apply the rules of depMap to t
        If down = false, collapse from top to down, otherwise collapse from down to top
    """
    temp = list(t.child) # copy, because t.child is changed while iterating
    if down:
        for c in temp:
            collapseMap(c,depMap,qw,down)
    try:
        if isinstance(depMap[t.dependency], str):
            t.dependency = depMap[t.dependency]
        else:
            depMap[t.dependency](t,qw)
    except KeyError:
        raise GrammaticalError(t.dependency,"unknown dependency")
    if not down:
        for c in temp:
            collapseMap(c,depMap,qw,down)

def collapsePrep(t):
    """
        Replace prep(c)_x by prep
    """
    temp = list(t.child) # copy, because t.child is changed while iterating
    for c in temp:
        collapsePrep(c)
    if t.dependency.startswith('prep'): # prep_x or prepc_x (others?)
        prep = ' '.join(t.dependency.split('_')[1:]) # type of the prep (of, in, ...)
        if t.parent.wordList[0].pos[0] == 'V':
            t.parent.wordList[0].word += ' ' + prep
        t.dependency = 'prep'

def connectorUp(t):
    """
        Move amod connectors (superlative: first, biggest...)
    """
    if t.dependency == 'connectorUp':
        assert t.parent is not None and t.child == []
        t.dependency = t.parent.dependency
        t.parent.dependency = 'Rspl'
        t.parent.child.remove(t)
        t.child = [t.parent]
        t.parent.parent.child.remove(t.parent)
        t.parent.parent.child.append(t)
        parentTemp = t.parent.parent
        t.parent.parent = t
        t.parent = parentTemp
    else:
        temp = list(t.child) # copy, because t.child is changed while iterating
        for c in temp:
            connectorUp(c)

def conjConnectorsUp(t):
    """
        Move conjonction connectors (and, or, neg...)
    """
    if not t.dependency.startswith('conj'):
        temp = list(t.child) # copy, because t.child is changed while iterating
        for c in temp:
            conjConnectorsUp(c)
    else:
        assert t.parent is not None
        depSave = t.dependency[t.dependency.index('_')+1:]
        parentTemp = None
        dupl = None
        newTree = None
        if len(t.parent.child) == 1:
            parentTemp = t.parent.parent
            t.dependency = t.parent.dependency
            t.parent.child.remove(t)
            dupl = deepcopy(parentTemp)
            parentTemp.child.remove(t.parent)
            parentTemp.child.append(t)
            t.parent = parentTemp
            newTree = DependenciesTree(depSave, dependency=parentTemp.dependency, child=[dupl,parentTemp], parent=parentTemp.parent)
            parentTemp.dependency = 'RconjB'
            parentTemp.parent = newTree
        else:
            parentTemp = t.parent
            parentTemp.child.remove(t)
            dupl = deepcopy(parentTemp)
            t.child += t.parent.child
            for n in t.child:
                n.parent = t
            newTree = DependenciesTree(depSave, dependency=parentTemp.dependency, child=[dupl,t], parent=parentTemp.parent)
            t.dependency = 'RconjB'
            t.parent = newTree
        newTree.parent.child.remove(parentTemp)
        newTree.parent.child.append(newTree)
        dupl.dependency = 'RconjT'
        dupl.parent = newTree
        temp = list(newTree.child) # copy, because t.child is changed while iterating
        for c in temp:
            conjConnectorsUp(c)

###################
# Global function #
###################

def simplify(t):
    """
        identify and remove question word
        collapse dependencies of tree t
    """
    qw = identifyQuestionWord(t)             # identify and remove question word
    collapsePrep(t)                          # replace prep(c)_x by prep(c)
    collapseMap(t,dependenciesMap1,qw)       # collapse the tree according to dependenciesMap1
    conjConnectorsUp(t)                      # remove conjonction connectors
    connectorUp(t)                           # remove remaining amod connectors
    questionWordDependencyTree(t,qw)         # change the tree depending on the qw
    collapseMap(t,dependenciesMap2,qw)       # propagate types from bottom to top
    collapseMap(t,dependenciesMap2,qw,False) # propagate types from top to bottom
    return qw
