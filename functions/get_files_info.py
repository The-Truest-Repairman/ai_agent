import os

def get_files_info(working_directory, directory="."):
    """
    Returns string info about files/directories within `directory`, relative to `working_directory`.
    Guards against directory traversal and non-directories.
    """    
    absolute_working_dir = os.path.abspath(working_directory)
    full_path = os.path.abspath(os.path.join(absolute_working_dir, directory))
    
    #First check for proper directory inputs 
    if not full_path.startswith(absolute_working_dir):
        return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'
    if not os.path.isdir(full_path): #Check that the path is a directory
        return f'Error: "{directory}" is not a directory'
    
        
    
    #Try building output string and catch any exceptions thrown 
    try:
        #Build and return a string to represent contents of directory
        files = sorted(os.listdir(full_path))
        files_info = []
        for file in files:
            file_path = os.path.join(full_path, file)
            files_info.append(f"- {file}: file_size={os.path.getsize(file_path)} bytes, is_dir={os.path.isdir(file_path)}")
        return "\n".join(files_info)
    except Exception as e:
        return(f"Error listing files: {str(e)}")
   
