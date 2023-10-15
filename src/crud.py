# from .database import db
from .models import *
import bson

def create_post(post: Post) -> Post:
    post.save()  # Guardar el post en la base de datos
    return post  # Retornar el post guardado



# async def create_post(uid: str, post_create: PostCreate):
#     posts_collection = db.get_collection("posts")
    
#     # post = User()

#     # check if user `uid` has posted before
#     # print(posts_collection.find_one({"_id": uid}))
#     if not await posts_collection.find_one({"uid": uid}):
#         await posts_collection.insert_one(User(_id=uid).__dict__)
#         print("adding user")
        
#     user = await posts_collection.find_one({"uid": uid})
#     is_public = post_create.is_public
#     delattr(post_create, "is_public")
#     post = Post.from_orm(post_create)

#     field = "public" if is_public else "private"
#     # pid = user["lastpid"] + 1
#     print(user)
    
#     # add new post to the dict of posts
#     await posts_collection.update_one(
#         {"uid": uid},
#         {"$set": {
#                 f"{field}.{bson.objectid.ObjectId()}": post.__dict__
#             }
#         })
#     return True

# async def get_posts(uid: str, public: bool = True, private: bool = False):
#     posts_collection = db.get_collection("posts")
#     user = await posts_collection.find_one({"uid": uid})
#     posts = {}

#     if public:
#         posts.update(user["public"])
#     if private:
#         posts.update(user["private"])

#     return posts