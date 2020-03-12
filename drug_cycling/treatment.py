import copy
import re
import sys
from fractions import Fraction
from numbers import Number

eps = 1.33*sys.float_info.epsilon
    
class ParsingError(Exception):
    def __init__(self,msg,lineno):
        super().__init__(msg+str(lineno))

class InconsistentLandscapeError(Exception):
    def __init__(self,landscape):
        msg = 'Fitness landscape '+\
                landscape.name+' has '\
                'an inconsistency.'
        super().__init__(msg)

# Structure of Treatment:
# ( g,d | g is genotype, d is dictionary of adjacent genotypes with
# probabilities
class Treatment:
    def __init__(self,adj:dict,name:str=None):
        self.name = name
        # Caller is responsible for making sum(probs) over common 
        # treatment and source \approx 1 or empty dict
        self.adj = copy.deepcopy(adj)

    def __repr__(self):
        bc = max([k.bit_length() for v in self.adj.values()
                for k in v.keys()] \
                        + [k.bit_length() for k in self.adj.keys()] \
                        ,default=0)
        s = '\n'+self.name+'\n'
        for i,a in self.adj.items():
            s += f'{i:0{bc}b}: {{'\
                    +', '.join(f'{a:0{bc}b}:{b}' for a,b in a.items())+'}\n'
        return s

    def check_consistency(self):
        pairs = []
        for g,adj in self.adj.items():
            thisp = 0
            for ag,p in adj.items():
                if not isinstance(p,Number) or \
                        p < 0:
                    return False
                if g != ag and p != 0:
                    pairs += [sorted((g,ag))]
                    thisp += p
            if thisp >= 1 + eps or thisp <= 1 - eps:
                return False
        pairs.sort()
        if any(x==y for x,y in zip(pairs[1:],pairs[:-1])):
            return False
        return True


def load_treatments_from_file(filename)->list:
    '''File should be blocks of lines each consisting of a three
    white space separated fields:
        - A source genotype
        - A destination genotype
        - (Optional:) The probability of src->dest
    In the case where there are no probabilities, a probability of 1/k
    if assigned to a genotype with k destinations.  
    
    The method reads data into a list of treatments.'''

    treatments = []
    adj = []
    probs = []
    lineno = 0
    with open(filename) as f:
        name = None
        for line in f:
            lineno += 1
            # Blank line after content signals end of data
            if line.strip() == '':
                if name is not None:
                    tr = Treatment(adj,name)
                    _assign_probs(tr,lineno)
                    if not tr.check_consistency():
                        raise InconsistentLandscapeError(
                                tr)
                    treatments.append(tr)
                name = None
                continue
            fields = line.split()
            if len(fields) == 1:
                if name is None:
                    name = fields[0].strip()
                    adj = {}
                # Ensure name not after name
                else:
                    raise ParsingError(
                            'Name must be following by data or blank ' 
                            'line',lineno)
            elif len(fields) in [2,3]:
                if name is None:
                    raise ParsingError(
                            "Data doesn't have name",lineno)
                if len(fields) == 2:
                    fields += [None]
                src,dst,prob = convert_to_numbers(*fields,lineno)
                if adj.get(src) is not None:
                    adj[src].update({dst:prob})
                else:
                    adj[src] = {dst:prob}
            else:
                raise ParsingError(
                        'Lines must have 0 to 3 fields:',
                        lineno)
        else:
            if name is not None:
                tr = Treatment(adj,name)
                _assign_probs(tr,lineno)
                if not tr.check_consistency():
                    raise InconsistentLandscapeError(
                        tr)
                treatments.append(tr)

    return treatments

def _assign_probs(tr,lineno):
    for g,a in tr.adj.items():
       if all(x is None for x in a.values()):
           a.update(dict.fromkeys(a.keys(),1/len(a)))
       if any(x is None for x in a.values()):
           raise ParsingError(
                   'You can\'t mix default probabilities with '\
                           'assgined probabilities in a single '\
                           'source genotype.',lineno)

def convert_to_numbers(src,dst,prob,lineno):
    try:
        src,dst = int(src,2),int(dst,2)
    except ValueError:
        raise ParsingError('Could not convert strings to '\
                'numbers at line ',lineno)


    if prob is not None:
        try:
            prob = float(Fraction(prob))
        except:
            raise ParsingError(
                    'Could not convert third field to float ' 
                    'in line ',lineno)
    return src,dst,prob
