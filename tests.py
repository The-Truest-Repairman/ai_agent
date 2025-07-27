#Import the module functions in the same directory
from functions import *

#print("Test: 0")
#print(get_file_content("calculator", "lorem.txt"))

print("\nTest 1:")
print(run_python_file("calculator", "main.py"))

print("\nTest 2:")
print(run_python_file("calculator", "main.py", ["3 + 5"]))

print("\nTest 3:")
print(run_python_file("calculator", "tests.py"))

print("\nTest 4:")
print(run_python_file("calculator", "../main.py"))

print("\nTest 5:")
print(run_python_file("calculator", "nonexistent.py"))
