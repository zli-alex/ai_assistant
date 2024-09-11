import json 
def file_reader(file_name):
    """Read file as a whole string

    Args:
        file_name (str): path to file (txt)

    Returns:
        str: a very long string of file content
    """
    with open(file_name, encoding='utf-8') as data_file:   
        content = data_file.read()
    return content

def file_reader_json(file_name):
    """Read file as a json

    Args:
        file_name (str): path to file (txt)

    Returns:
        dict: json data
    """
    with open(file_name, encoding='utf-8') as data_file:    
        data = json.load(data_file)
    return data