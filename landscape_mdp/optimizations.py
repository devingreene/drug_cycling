from treatment import Treatment
import sys
from collections import deque,OrderedDict

class ConvergenceFailure(Exception):
    pass

cache = {}

def find_best_for_n_steps(treats:list,n)->dict:
    'Find the treatment for maximizing the probability of lasting '\
    '>= n steps'

    cache.clear()
    if n in [ 'oo', 'inf' ]:
        win = deque([None]*10)
        for i in range(10,1000):
            win.append(_find_best_for_n_steps(treats,i))
            win.popleft()
            # Drop probabilities
            win_sans_probs = \
                    [ { a:b[0] for a,b in w.items() } \
                    if w is not None else None \
                    for w in win ]
                    
            if [win_sans_probs[0]]*10 == \
                    list(win_sans_probs):
                return win.pop()
        else:
            raise ConvergenceFailure(
                    "Sequence failed to converge")

    else:
        try:
            n = int(n)
            if n <= 0:
                raise ValueError
        except ValueError:
            raise ValueError("Path length must be "\
                    "a positive integer")

    return _find_best_for_n_steps(treats,n)

# Let the cache ``catch up''
def _find_best_for_n_steps(treats,n):

    k = n
    while True:
        try: 
            out = __find_best_for_n_steps(treats,k)
            if n == k:
                return out
        except RecursionError:
            if k == n:
                sys.setrecursionlimit(
                        2*sys.getrecursionlimit())
            k //= 2
        else:
            break
    for j in range(1,n//k+1):
        if n >= 100000 and j % 10 == 0:
            print(f'Finding `cache[{j*k}]\'',file=sys.stderr)
        __find_best_for_n_steps(treats,j*k)
    return __find_best_for_n_steps(treats,n)


def __find_best_for_n_steps(treats,n):
    if n <= 0:
        raise ValueError("Only positive integers allowed")

    ans = cache.get(n)
    if ans is not None:
        return ans

    genotypes = collect_genotypes(treats)
    opttreats = {}

    if n == 1:
        for g in genotypes:
            for t in treats:
                gadj = t.adj.get(g)
                # It's not a trap in this treatment
                if gadj is not None:
                    opttreats[g] = (t,1)
                    break
            else:
                opttreats[g] = (None,0)

    else:
        opttreatsm1 = __find_best_for_n_steps(treats,n-1)
        for g in genotypes:
            opts = dict.fromkeys(treats,0)
            for t in treats:
                gadj = t.adj.get(g)
                if gadj is not None:
                    for ag,p in gadj.items():
                        opts[t] += p * opttreatsm1.get(ag,[0,0])[1]
            if not any(opts.values()):
                opttreats[g] = (None,0)
            else:
                opttreats[g] = max(opts.items(),
                    key=lambda x:x[1],default=(None,0))

    cache[n] = opttreats
    return opttreats

def max_expected_length(treats:list,discount = 0.9,\
        maxiter = 1000,eps=0.33e-3):
    genotypes = collect_genotypes(treats)
    if discount >= 1 or discount <= 0:
        raise ValueError("`discount' must be < 1 and positive")
    win = deque(4*[None])
    state = OrderedDict.fromkeys(genotypes,(None,1)) 
    win.append(state)
    for i in range(maxiter):
        newstate = OrderedDict.fromkeys(genotypes,(None,1))
        for g in genotypes:
            rewards = [(None,0)]
            for t in treats:
                if g not in t.adj:
                    continue
                acc = 0
                for ag,p in t.adj[g].items():
                    acc += p*(1 + discount*state[ag][1])
                rewards += [(t.name,acc)]
            newstate[g] = max(rewards,key=lambda x:x[1])
        win.append(newstate)
        state = newstate
        if win.popleft() is not None and i > 19:
            treatments = [ [x[0] for x in s.values() ] \
                    for s in win ]
            rewards    = [ [ x[1] for x in s.values() ] \
                    for s in win ]
            if sum( _sqdiffs(x,y) for x,y in \
                    zip(rewards[1:],rewards[:-1])) \
                    < eps and all(t==treatments[0] \
                    for t in treatments[1:]):
                return win.pop()
    else:
        print("It didn't converge")
        return {}

def collect_genotypes(treats:list):
    "Gathers all genotypes from a list of treatments"

    genotypes = set()
    for t in treats:
        genotypes.update(t.adj.keys())
        for a in t.adj.values():
            genotypes.update([g for g,p in a.items() if p != 0])
    return genotypes

def _sqdiffs(x,y):
    return sum((x-y)**2 for x,y in zip(x,y))
