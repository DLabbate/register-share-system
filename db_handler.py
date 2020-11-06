import pymongo
from pymongo import MongoClient
import dns
from private.connection import connection_string

class DBHandler:

    def __init__(self):
        self.connection_string = connection_string
        self.client = MongoClient(connection_string)
        self.db = self.client["register-share-system"]
        self.user_collection = self.db["users"]
    
    def add_user(self,name,ip,port):
        #user = {"name":name,"IP":IP,"port":port }

        try:
            user = {"_id":name,"IP":ip,"port":port }
            self.user_collection.insert_one(user)
            return True 
        except:
            print("USERNAME:" + str(name) + " ALREADY EXISTS!")
            return False

