#Import get_files_info from the module functions in the same directory
from functions.get_file_content import get_file_content
#print("Test: 0")
#print(get_file_content("calculator", "lorem.txt"))

print("\nTest 1:")
print(get_file_content("calculator", "main.py"))

print("\nTest 2:")
print(get_file_content("calculator", "pkg/calculator.py"))
print("\nTest 3:")
print(get_file_content("calculator", "/bin/cat"))
print("\nTest 4:")
print(get_file_content("calculator", "pkg/does_not_exist.py"))