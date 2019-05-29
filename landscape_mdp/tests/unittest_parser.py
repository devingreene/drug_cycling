import re
import tempfile,os,sys
from treatment import *
from optimizations import find_best_for_n_steps,\
        max_expected_length
from tests.landscapes import *
from argparse import ArgumentParser

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
                "\nWe got\n\n" \
                +str(treatments))
    except ParsingError as e:
        print(f"For file:\nLine no.\n{data:15s}\n"
                "\nWe got\n\n"
                ,*e.args)
    except InconsistentLandscapeError as e:
        print(f"For file:\nLine no.\n{data:15s}\n"
                "\nWe got\n\n"
                ,*e.args)
    finally:
        os.unlink(filename)

divide = "\n"+("*"*12).center(70)
def main():
    test_parse(l01)
    print(divide)
    test_parse(l02)
    print(divide)
    test_parse(l03)
    print(divide)
    print("\n(Bad file)")
    test_parse(l04)

main()
