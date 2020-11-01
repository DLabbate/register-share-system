import pickle
import ast

def serialize(msg):
    return pickle.dumps(msg)

def deserialize(msg):
    return pickle.loads(msg)

def convert_to_dict(msg):
    try:
        msg_dict = ast.literal_eval(str(msg))
        return msg_dict
    except:
        print("ERROR CONVERTING MESSAGE TO DICTIONARY")
