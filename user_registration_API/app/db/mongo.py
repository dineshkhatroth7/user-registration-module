from pymongo import MongoClient

client = MongoClient("mongodb+srv://dinunaik65:hjKj4di7aPjdirPX@user-data.yvlc9zz.mongodb.net/")
db = client["user_registration_model"]
users_collection = db["users"]