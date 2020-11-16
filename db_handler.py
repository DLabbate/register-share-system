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
        self.messages_collection = self.db["messages"]
    
    def add_user(self,name,ip,port):
        #user = {"name":name,"IP":IP,"port":port }

        try:
            user = {"_id":name,"IP":ip,"port":port }
            self.user_collection.insert_one(user)
            return True 

        except:

            print("USERNAME:" + str(name) + " ALREADY EXISTS!")
            return False

    #Assuming unique name IDs for each user
    def remove_user(self,name):

        try:
            user_query = {"_id":name}
            self.user_collection.delete_one(user_query)
            return True 

        except:

            print("USERNAME:" + str(name) + "DOES NOT EXIST!")
            return False

    def update_socket(self,name,ip,port):

        try:
            user_query = {"_id":name}
            user_newvalues = { "$set": {"IP": ip,"port": port}}
            self.user_collection.update_one(user_query, user_newvalues)
            return True 
        
        except:
            print("USERNAME:" + str(name) + "DOES NOT EXIST!")
            return False 

    #Takes input array of subjects
    def update_subjects(self,name,subjects):

        try: 

            user_query = {"_id":name}
            user_newvalues = {"$set": {"subjects": subjects}}
            self.user_collection.update_one(user_query,user_newvalues)
            
            return True 
        
        except:
            print("USERNAME:" + str(name) + "DOES NOT EXIST!")
            return False 
    
    def publish_message (self, name, subject, text):

        try:

            #user_query = {"_id":name}

            if (self.user_collection.count_documents({"_id":name}) != 0):

                print("name exists")
                
                if(self.user_collection.find({"_id":name, "subjects": subject}).count() != 0):

                    print("subject exits")
                
                    message = {"name":name,"subject":subject,"text":text}
                    self.messages_collection.insert_one(message)
                    return True

                else:
                    print("SUBJECT:" + str(subject) + " NOT FOUND IN SUBJECT LIST")
                    return False

            else:

                print("USERNAME:" + str(name) + " DOES NOT EXIST!")
                return False

        except:

            print("MESSAGE NOT PUBLISHED FROM USERNAME:" + str(name))
            return False



        






