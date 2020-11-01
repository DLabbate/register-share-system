import pymongo
from pymongo import MongoClient
import dns
from private.connection import connectionString

class DBHandler:

    def __init__(self):
        self.connectinString = connectionString
        self.client = MongoClient(connectionString)
        self.db = self.client["register-share-system"]
        self.userCollection = self.db["users"]
    
    def addUser(self,name,IP,port):
        #user = {"name":name,"IP":IP,"port":port }

        try:
            user = {"_id":name,"IP":IP,"port":port }
            self.userCollection.insert_one(user)
            return True 
        except:
            print("USERNAME:" + str(name) + " ALREADY EXISTS!")
            return False

