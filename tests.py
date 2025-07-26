#Import the module functions in the same directory
from functions import *

#print("Test: 0")
#print(get_file_content("calculator", "lorem.txt"))

print("\nTest 1:")
print(write_file("calculator", "lorem.txt", "wait, this isn't lorem ipsum"))

print("\nTest 2:")
print(write_file("calculator", "pkg/morelorem.txt", "lorem ipsum dolor sit amet"))

print("\nTest 3:")
print(write_file("calculator", "/tmp/temp.txt", "this should not be allowed"))
