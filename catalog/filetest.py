import os
import pickle

def filetest():
  parent_dir = os.path.split(os.getcwd())[0]

  with open(os.path.join(parent_dir, "type_dict.pickle")) as f:
    type_dict = pickle.load(f)
    print(type_dict[skin_type])


filetest()
