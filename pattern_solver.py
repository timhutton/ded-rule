# Solver for Patterns, by Simon Tatham

# entry: 0=white, 1=black, 2=unknown
# clues: lengths of the black runs in that row/column

def get_possibilities(N,clues,curr=[]):
    '''Generates run-lengths of alternating white and black.'''
    if len(clues)==0:
        yield curr+[N]
    else:
        n_white = N-sum(clues)
        min_white = 1 if curr else 0
        max_white = n_white-max(0,len(clues)-2)
        for i in range(min_white,max_white+1):
            for p in get_possibilities(N-(i+clues[0]),clues[1:],curr+[i,clues[0]]):
                yield p

def rle_to_string(rle):
    return ''.join( '01'[i%2]*n for i,n in enumerate(rle) )

def intersect(entries,possibilities):
    print entries,'-->',
    k = union(p for p in possibilities if matches(entries,p))
    return k if k else 'Error'

def union(strs):
    '''Given a set of strings of 0,1, return a string with '.' if disagreement, else the 0 or 1.'''
    t = map(list,zip(*strs)) # by entry
    return ''.join('0' if all(e=='0' for e in te) else '1' if all(e=='1' for e in te) else '.' for te in t)

def matches(entries,seq):
    '''e.g. "...1." matches with "00111" but not with "00101".'''
    return all(e=='.' or e==s for e,s in zip(entries,seq))

poss=[]
N = 13
clues = [4,1,4]
print N,clues
poss = map(rle_to_string, get_possibilities(N,clues))
print poss
print intersect('.............',poss)
print intersect('1............',poss)
print intersect('1...........1',poss)
print intersect('10..........1',poss)
