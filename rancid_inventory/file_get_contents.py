import os.path

def file_get_contents( filename, ignore_comments = True ):
    if os.path.exists( filename ) == False:
        raise FileNotFoundError

    contents = []
 
    with open( filename, "r") as file_handle:
        line = file_handle.readline()
        while line:
            if line.startswith("#") == False:
                contents.append( line.replace("\n","" ))

            line = file_handle.readline()
   
    return contents
