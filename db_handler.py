import pymongo
from pymongo import MongoClient
import dns

class DBHandler:

    def __init__(self,connection_string,db_name):
        self.client = MongoClient(connection_string)
        self.db = self.client[db_name]
        self.user_collection = self.db["users"]
        self.messages_collection = self.db["messages"]
    
    def add_user(self,name,ip,port):
        
        try:
            
            if (name):
            
                if (self.user_collection.count_documents({"_id":name}) == 0):
            
                    user = {"_id":name,"IP":ip,"port":port }
                    self.user_collection.insert_one(user)
                    return 0
            
                else:

                    print("USERNAME:" + str(name) + " ALREADY EXISTS!")
                    return 1

            else:
                
                print("NOT A VALID USERNAME!")
                return 2

        except:

            print("USERNAME NOT ADDED! DATABASE CONNECTION ERROR")
            return 3

    # Assuming unique name IDs for each user
    def remove_user(self,name):

        try:

            if (self.user_collection.count_documents({"_id":name}) != 0):
                
                user_query = {"_id":name}
                self.user_collection.delete_one(user_query)
                return True 
            
            else:

                print("USERNAME:" + str(name) + " DOES NOT EXIST!")
                return False

        except:

            print("USERNAME:" + str(name) + "DOES NOT EXIST!")
            return False

    def update_socket(self,name,ip,port):

        try:

            if (self.user_collection.count_documents({"_id":name}) != 0):

                user_query = {"_id":name}
                user_newvalues = { "$set": {"IP": ip,"port": port}}
                self.user_collection.update_one(user_query, user_newvalues)
                return True 
            
            else:

                print("USERNAME:" + str(name) + " DOES NOT EXIST!")
                return False
        
        except:
            print("USERNAME:" + str(name) + "DOES NOT EXIST!")
            return False 

    # Takes input array of subjects
    def update_subjects(self,name,subjects):

        try: 

            if (self.user_collection.count_documents({"_id":name}) != 0):

                user_query = {"_id":name}
                user_newvalues = {"$set": {"subjects": subjects}}
                self.user_collection.update_one(user_query,user_newvalues)
                return True 
            
            else:

                print("USERNAME:" + str(name) + " DOES NOT EXIST!")
                return False

        
        except:
            print("USERNAME:" + str(name) + "DOES NOT EXIST!")
            return False 
    
    def publish_message (self, name, subject, text):

        try:

            if (self.user_collection.count_documents({"_id":name}) != 0):

                print("name exists")
                
                if(self.user_collection.find({"_id":name, "subjects": subject}).count() != 0):

                    print("subject exits")
                
                    message = {"name":name,"subject":subject,"text":text,"clients_received":[]}
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

    def retrieve_texts (self, name):

        try:

            if (self.user_collection.count_documents({"_id":name}) != 0):
            
                user_cursor = self.user_collection.find_one({"_id":{"$eq":name}})

                user_subjects = user_cursor["subjects"]
        

                message_query = {"$and":[{"subject":{"$in":user_subjects}},{"clients_received":{"$nin":[name]}}]}
                message_cursor = self.messages_collection.find(message_query)
                
                message_newClients = {"$push": {"clients_received":name}}
                
                msg_list = []

                
                for document in message_cursor:

                    msg = {"NAME":document["name"],"SUBJECT":document["subject"],"TEXT":document["text"]}
                    msg_list.append(msg)  
            
                self.messages_collection.update_many(message_query,message_newClients)
                
                return msg_list
            
            else:

                print("USERNAME:" + str(name) + " DOES NOT EXIST!")
                return 
        
        except:

            print("TEXTS COULD NOT BE RETRIEVED FOR USERNAME:" + str(name))
            return






        






