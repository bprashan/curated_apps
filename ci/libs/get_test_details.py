import subprocess
import sys

result = subprocess.run("python3 -m pytest --collect-only", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, encoding="utf-8").stdout.split("\n")

def test_cmd(test):
    package = ''
    module = ''
    cmd = ''
    for line in result:
        line = line.replace("<", "").replace(">", "")
        if "Package" in line:
            package = line.strip().split(" ")[1]
        if "Module" in line:
            module = line.strip().split(" ")[1]
        if test in line:
            cmd = package + "/" + module + "::TestClass::" + test
            return cmd

if __name__ == '__main__':
    test = sys.argv[1]
    print(test_cmd(test))