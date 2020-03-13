import sys
import subprocess
import itertools

tests = ( list(itertools.product(
                    ["unittest_optimizer"],
                    [1,2,4,15,50])) + 
        [ ("unittest_parser","") ] )

first = True
success = True
for a,b in tests:
    if not first:
        print("\n\n",flush=True)
    first = False
    args = ["python3","-m","landscape_mdp.tests."+a,
            str(b)]
    sargs = " ".join(args)
    print("*"*(len(sargs)+5),flush=True)
    print("With",sargs,flush=True)
    print("*"*(len(sargs)+5),flush=True)
    print("\n\n",flush=True)
    res = subprocess.run(args).returncode
    if res != 0:
        print("Failed at {} {}".format(a,b),
                file=sys.stderr)
        success = False

if success:
    print("\n\nEverything went well")
else:
    print("\n\nSomething went wrong")
