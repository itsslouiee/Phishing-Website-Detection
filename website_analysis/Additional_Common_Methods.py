#this file wasnt included with the files that came with dataset
def read_file_to_array(path):
    """Read a text file and return its lines as a clean list.
    - strips spaces and line endings (including Windows \\r\\n)
    - skips empty lines
    """
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]
