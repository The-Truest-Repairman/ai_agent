#Import get_files_info from the module functions in the same directory
from functions.get_files_info import get_files_info
print("Test 1:")
print(get_files_info("calculator", "."))

print("\nTest 2:")
print(get_files_info("calculator", "pkg"))
print("\nTest 3:")
print(get_files_info("calculator", "/bin"))
print("\nTest 4:")
print(get_files_info("calculator", "../"))