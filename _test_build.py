#! /usr/bin/python
import sys
import subprocess

if __name__ == '__main__':
    modules = ["nose"]
    if sys.version_info < (2, 7):
        modules.append("unittest2")
    subprocess.check_call(f'pip install --use-mirrors {" ".join(modules)}', shell=True)
    subprocess.check_call("python setup.py develop", shell=True)
    subprocess.check_call("nosetests -w tests", shell=True)
