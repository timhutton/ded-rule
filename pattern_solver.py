# Solver for Pattern/Nonograms

def get_possibilities(N,clues,curr=[]):
    '''Generates run-lengths of alternating white and black.'''
    if len(clues)==0:
        yield curr+[N]
    else:
        n_white = N-sum(clues)
        min_white = 1 if curr else 0
        max_white = n_white-max(0,len(clues)-2)
        for i in range(min_white,max_white+1):
            for p in get_possibilities( N-(i+clues[0]), clues[1:], curr+[i,clues[0]] ):
                yield p

def rle_to_string(rle):
    return ''.join( '01'[i%2]*n for i,n in enumerate(rle) )

def intersect(entries,possibilities):
    k = intersection(p for p in possibilities if matches(entries,p))
    if not k:
        raise ValueError('Input entries not consistent with the clues!')
    return k

def intersection(strs):
    '''Given a list of strings, return a string with '.' where they disagree.'''
    return ''.join( te[0] if len(set(te))==1 else '.' for te in zip(*strs) )

def matches(entries,seq):
    '''e.g. "...1." matches with "00111" but not with "00101".'''
    return all( e=='.' or e==s for e,s in zip(entries,seq) )

def row(grid,i_row):
    return ''.join(grid[i_row])
def col(grid,i_col):
    return ''.join(zip(*grid)[i_col])
def print_grid(grid):
    for row in grid:
        print ' '.join(row)
    print

'''
# Generated by Simon Tatham's Portable Puzzle Collection:
X = 10
Y = 10
x_clues = [[1,1,2],[1,4],[7],[3,4],[4,2],[4],[4],[7],[1,1,1],[1,1,1]]
y_clues = [[3,6],[1,4],[1,6],[6],[3,1],[3,3],[4,1],[1,1],[2],[2,2]]
'''

# Generated by Simon Tatham's Portable Puzzle Collection:
X = 30
Y = 30
x_clues = [[3,6],[3,1,1,2,1],[3,3,1,3],[1,1,1,4,2,1],[1,1,1,7,5],[1,2,1,7,1,4],[7,13,4],[7,1,1,6],[7,4,1,1,1],[2,3,2,4,1],[2,1,5,1,4],[3,5,1,1,5],[10,3,3],[4,1,7,2],[5,5,2,7],[5,2,1,4,3],[1,3,8],[15,1,1],[1,13,4],[1,3,13],[4,2,3,7,2],[9,1,9,5],[4,4,1,1,3,3,5],[1,2,2,3],[3,4,1,5],[3,4,1,3],[5,2,3,3,5],[1,3,2,5,1],[1,4,4,6,3],[1,6,3,6,1,1]]
y_clues = [[3,1,3,3],[3,3,1,7],[3,3,1,5,6],[9,1,3,1],[3,1,1,4],[6,2,3,3],[2,11,3,3,3],[1,6,6,2],[3,5,6,1],[1,1,4,2,2],[8,1,1,3,1,5],[2,1,3,4,5],[1,2,2,10,2],[1,5,4,3,1],[10,2,4,1],[17,1,1],[7,1,7,1],[5,1,8,1],[4,7,3],[9,4,3,6],[5,1,12,4],[1,1,5,5,4],[1,2,6,5,3],[2,2,1,2],[6],[1,8,9],[3,5,1,7,1],[3,4,1,1,7,2],[3,1,1,2,1,1],[4,1,1,1,2,1,1]]

grid = [['.' for x in range(X)] for y in range(Y)]
found_new_entry = True
while found_new_entry:
    found_new_entry = False
    for i_col in range(X):
        clues = x_clues[i_col]
        poss = map(rle_to_string, get_possibilities(X,clues))
        entries = col(grid,i_col)
        new_entries = intersect(entries,poss)
        for i,(e,c) in enumerate(zip(entries,new_entries)):
            if e=='.' and not c=='.':
                grid[i][i_col] = c
                found_new_entry = True
    for i_row in range(Y):
        clues = y_clues[i_row]
        poss = map(rle_to_string, get_possibilities(Y,clues))
        entries = row(grid,i_row)
        new_entries = intersect(entries,poss)
        for i,(e,c) in enumerate(zip(entries,new_entries)):
            if e=='.' and not c=='.':
                grid[i_row][i] = c
                found_new_entry = True
print_grid(grid)
