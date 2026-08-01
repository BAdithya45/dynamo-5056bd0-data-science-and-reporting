import os
import subprocess
import sys

root = os.getcwd()
print(root)
subprocess.run([sys.executable, os.path.join(root, 'task', 'solution', 'solve.py')], check=True)
subprocess.run([sys.executable, '-m', 'pytest', '-q', os.path.join(root, 'task', 'tests')], check=True)
