
import os, platform, subprocess

has_error = [False]

def make_error(msg):
    print "   *** ERROR ***", msg
    has_error[0] = True

def run_quietly(*cmd):
    try:
        with open(os.devnull,"w") as fnull:
            return subprocess.call(cmd, stdout=fnull, stderr=fnull)
    except OSError:
        return 999

def get_output(*cmd):
    # returns (stderr,stdout)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return p.communicate()

def test_metdraw():
    print "Platform information:"
    print "   Operating System:", platform.system()
    print "   Operating Platform:", platform.platform()

    print ""
    print "Python information:"
    print "   Version:", platform.python_version()
    major,minor,patch = [int(x) for x in platform.python_version_tuple()]
    if not (major == 2 and minor >= 7):
        make_error("Python 2.7 is required.")

    print ""
    print "Path setup"
    print "   Looking for metdraw.py"
    if run_quietly("python", "metdraw.py", "--test", "-") != 0:
        make_error("Your path does not include metdraw.py")
    print "   Looking for metcolor.py"
    if run_quietly("python", "metcolor.py", "--test", "-", "-") != 0:
        make_error("Your path does not include metcolor.py")

    print ""
    print "Graphviz"
    dot_cmd = ['dot','-V']
    if run_quietly(*dot_cmd) == 0:
        print "   Graphviz is installed."
        print "   Checking Graphviz version:"
        stderr,stdout = get_output('dot', '-V')
        if 'version 2.28' in stdout:
            print "      Your version [{0}] is compatible with MetDraw.".format(stdout.rstrip())
        else:
            make_error("MetDraw requires Graphviz version 2.28.")
    else:
        make_error("Graphviz is not installed on your path.")



if __name__ == '__main__':
    print ""
    test_metdraw()

    print ""
    if has_error[0]:
        print "*** This installation contained errors. ***"
    else:
        print "MetDraw is installed properly."
    print ""

