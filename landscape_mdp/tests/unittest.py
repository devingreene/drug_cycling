import re
import tempfile,os,sys
from treatment import *
from optimizations import find_best_for_n_steps,\
        max_expected_length
from tests.landscapes import *

def lninsrt(s):
    ran = iter(range(1,s.count('\n')+1))
    return '\n'.join([ f'{next(ran):02d} '+l for l in s.split('\n')[:-1]])

def test_parse(data):
    fd,filename = tempfile.mkstemp()
    with open(fd,'w') as f:
        f.write(data)
    data = lninsrt(data)
    try:
        treatments = load_treatments_from_file(filename)
        print(f"For file:\nLine no.\n{data}\n"
                "\nWe got\n" \
                +str(treatments))
    except ParsingError as e:
        print(f"For file:\nLine no.\n{data:15s}\n"
                "\nWe got\n"
                ,*e.args)
    except InconsistentLandscapeError as e:
        print(f"For file:\nLine no.\n{data:15s}\n"
                "\nWe got\n"
                ,*e.args)
    finally:
        os.unlink(filename)

def main():
    n = sys.argv[-1]
    try:
        if n not in ['inf','oo']:
            n = int(n)
            if n <= 0:
                raise ValueError
    except Exception as e:
        print('Please provide a postive number'
                ' for the path length.'
                ,file=sys.stderr)
        sys.exit(1)

    test_parse(l01)
    test_parse(l02)
    test_parse(l03)
    test_parse(l04)

    #Test optimizer
    print('\n'+'*'*60)
    print('\nOptimal treatment options: \n'
    )
    fd,fn = tempfile.mkstemp()
    try:
        with open(fd,'w') as f:
            f.write(check_paths)

        treatments = load_treatments_from_file(fn)

        print("\nWith this landscape:\n")
        print(check_paths+"\n")

        print(find_best_for_n_steps(treatments,n))

        print("\nMax expected length:\n")
        print(max_expected_length(treatments))

    finally:
        os.unlink(fn)


main()
