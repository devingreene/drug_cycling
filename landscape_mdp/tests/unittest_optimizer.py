import tempfile,os,sys
from ..treatment import *
from ..optimizations import find_best_for_n_steps,\
        max_expected_length
from .landscapes import *
from argparse import ArgumentParser

divide = "\n"+("*"*12).center(70)

#Test optimizer
def main():
    parser = ArgumentParser()
    parser.add_argument('pathlength')
    args = parser.parse_args()
    n = args.pathlength
    print('Optimal treatment options: \n'
    )
    fd,fn = tempfile.mkstemp()
    try:
        with open(fd,'w') as f:
            f.write(for_optimization_test)

        try:
            treatments = load_treatments_from_file(fn)
        except ParsingError:
            print("Oops, the file didn't parse",file=sys.stderr)
            sys.exit(1)

        print("With this landscape:\n")
        print(for_optimization_test+"\n")
        try:
            print(find_best_for_n_steps(treatments,n))
        except ValueError as e:
            print(e)

        print("\nMax expected length:\n")
        print(max_expected_length(treatments))

    finally:
        os.unlink(fn)

main()
