
import json as JSON

def json_unicode_to_str(obj):
    # replace all unicode strings in a JSON object with str objects
    new = {}
    for k,v in obj.items():
        new_k = str(k) if isinstance(k,unicode) else k
        if isinstance(v,unicode):
            new_v = str(v)
        elif isinstance(v,dict):
            new_v = json_unicode_to_str(v)
        else:
            new_v = v
        new[new_k] = new_v
    return new

def parse_json_file(filename,unicode_to_str=True):
    obj = JSON.load(open(filename))
    if unicode_to_str:
        obj = json_unicode_to_str(obj)
    return obj
