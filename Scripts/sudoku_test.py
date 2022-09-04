""" The is a example of how to compare two files .txt
    and check if they are the same.
"""

import filecmp
from importlib.resources import path
import os

# Path of the files to compare
path1 = os.path.join(os.path.dirname(__file__), "Text1.txt")
path2 = os.path.join(os.path.dirname(__file__), "text2.txt")

# Compare the files
if filecmp.cmp(path1, path2):
    print("The files are the same")
else:
    print("The files are different")
