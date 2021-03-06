from ppp_datamodel import Intersection, First, Last

superlativeNoun = {
    # associate relevant predicate to each uperlative
    'biggest'   : 'size',
    'smallest'  : 'size',
    'broadest'  : 'width',
    'coldest'   : 'temperature',
    'deepest'   : 'depth',
    'densest'   : 'density',
    'furthest'  : 'distance',
    'farthest'  : 'distance',
    'fattest'   : 'weight',
    'hardest'   : 'difficulty',
    'heaviest'  : 'weight',
    'highest'   : 'height',
    'hottest'   : 'temperature',
    'largest'   : 'width',
    'longest'   : 'length',
    'loudest'   : 'sound',
    'lowest'    : 'height',
    'noisiest'  : 'sound',
    'oldest'    : 'age',
    'eldest'    : 'age',
    'quickest'  : 'speed',
    'fastest'   : 'speed',
    'shortest'  : 'length',
    'slimmest'  : 'weight',
    'slowest'   : 'speed',
    'strongest' : 'strength',
    'thickest'  : 'thickness',
    'warmest'   : 'temperature',
    'wettest'   : 'humidity',
    'widest'    : 'width',
    'youngest'  : 'age',
    'cheapest'  : 'cost',
    'tallest'   : 'height',
    #
    'recent'    : 'date',
    'expensive' : 'cost',
    'popular'   : 'popularity',
}

superlativeOrder = {
    # associate sorting order to each uperlative
    'first'     : First,
    'last'      : Last,
    'biggest'   : Last,
    'smallest'  : Last,
    'broadest'  : Last,
    'coldest'   : First,
    'deepest'   : Last,
    'densest'   : Last,
    'furthest'  : Last,
    'farthest'  : Last,
    'fattest'   : Last,
    'hardest'   : Last,
    'heaviest'  : Last,
    'highest'   : Last,
    'hottest'   : Last,
    'largest'   : Last,
    'longest'   : Last,
    'loudest'   : Last,
    'lowest'    : First,
    'noisiest'  : Last,
    'oldest'    : Last,
    'eldest'    : Last,
    'quickest'  : Last,
    'fastest'   : Last,
    'shortest'  : First,
    'slimmest'  : First,
    'slowest'   : First,
    'strongest' : Last,
    'thickest'  : Last,
    'warmest'   : Last,
    'wettest'   : Last,
    'widest'    : Last,
    'youngest'  : First,
    'cheapest'  : First,
    'tallest'   : Last,
    #
    'most'      : Last,
    'least'     : First,
}
