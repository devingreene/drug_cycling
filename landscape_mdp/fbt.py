from optimizations import find_best_for_n_steps, \
        max_expected_length, collect_genotypes
from treatment import load_treatments_from_file
from argparse import ArgumentParser
import sys

def bitstringconverter(l):
    'Returns function for converting ints to '\
            'zero padded bitstrings'
    len = max(x.bit_length() for x in l)

    def tobitstr(n):
        return format(n,f'0{len}b')

    return tobitstr

parser = ArgumentParser()
parser.add_argument('file')
parser.add_argument('pathlength',nargs='?')
parser.add_argument('-d',dest='d',type=float,metavar="discount",
        help="Discount Factor")
parser.add_argument('--discount',dest='d',type=float,metavar="discount",
        help="Discount Factor")
parser.add_argument('-e','--expected',dest='e',action='store_true',
        help="expected reward flag")
args = parser.parse_args()
file,length = args.file,args.pathlength

tl = load_treatments_from_file(file)

genotypes = collect_genotypes(tl)
tobs = bitstringconverter(genotypes)

if args.e:
    if args.d is None:
        discount = 0.9
    else:
        discount = args.d
    if args.pathlength is not None:
        print("Warning: Path length ignored with this option",
                file = sys.stderr)
    res = max_expected_length(tl,discount)
    print('To maximize expected reward:')
    print('Genotype','Treatment','Reward')
    for g,(t,p) in res.items():
        print(f'{tobs(g):>8}',\
                f'{t!s:>9}',\
                f'{p:>11.5f}')

if not args.e:
    if args.d is not None:
        print("Cannot have discount factor for n-step "\
            "calculation",file=sys.stderr)
        sys.exit(1)
    if args.pathlength is None:
        print("Must have path length for this option",
                file=sys.stderr)
        sys.exit(1)
    res = find_best_for_n_steps(tl,length)
    print('To maximize probability of >= '+\
            str(args.pathlength)+' steps:')
    print('Genotype','Treatment','Probability')
    for g in genotypes:
        if g in res:
            treat = res[g][0].name
            prob  = res[g][1]
        if g not in res:
            treat = 'None'
            prob = 0
        print(f'{tobs(g):>8}',\
                f'{treat:>9}',\
                f'{prob:>11.5f}')
