import os
import subprocess
import sys

repo = r'C:\Users\badit\dynamo-5056bd0-data-science-and-reporting'
os.chdir(repo)
subprocess.run([sys.executable, 'task/solution/solve.py'], check=True)
subprocess.run([sys.executable, '-m', 'pytest', '-q', 'task/tests'], check=True)
