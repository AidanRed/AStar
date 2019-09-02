"""
Convenience script to run the tests specified on the assignment page.
"""

import subprocess

subprocess.call(["python", "robotplanner.py", "testgrid_large.txt", "0", "1", "4", "14"])
subprocess.call(["python", "robotplanner.py", "testgrid_large.txt", "0", "8", "9", "14"])
subprocess.call(["python", "robotplanner.py", "testgrid_large.txt", "10", "3", "5", "0"])
subprocess.call(["python", "robotplanner.py", "testgrid_large.txt", "5", "14", "2", "0"])
subprocess.call(["python", "robotplanner.py", "testgrid_large.txt", "0", "13", "0", "0"])
