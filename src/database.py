import motor.motor_asyncio
import pymongo
# POSTS_DB = "mongodb://snapmsg:snapmsg@posts-db-mongodb:27017/postsdb?retryWrites=true&w=majority"
POSTS_DB = "mongodb://snapmsg:snapmsg@posts-db-mongodb:27017/postsdb"

client = motor.motor_asyncio.AsyncIOMotorClient(POSTS_DB)
# client = pymongo.MongoClient("mongodb://snapmsg:snapmsg@posts-db-mongodb/postsdb", 27017)
db = client.postsdb