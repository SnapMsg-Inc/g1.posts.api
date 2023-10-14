from fastapi import FastAPI, HTTPException
from typing import Optional 
from .database import db
from .models import PostCreate
from . import crud


app = FastAPI()


# @app.on_event("startup")
# async def startup_db_client():
#     app.mongodb_client = AsyncIOMotorClient("mongodb://snapmsg:snapmsg@posts-db:27017/postsdb?retryWrites=true&w=majority")
#     app.mongodb = app.mongodb_client.posts-db


# @app.on_event("shutdown")
# async def shutdown_db_client():
#     app.mongodb_client.close()


@app.get("/")
async def root():
	# print(dirdb))
	# posts_collection = db.get_collection("posts")
	# posts_collection.insert()
	return {"message": "Posts microsevice"}



@app.post("/posts/{uid}")
async def create_post(uid: str, post: PostCreate):
	await crud.create_post(uid, post)
	return "post created"


@app.get("/posts/{uid}")
async def get_private_posts(uid: str, public: Optional[bool] = True, private: Optional[bool] = True):
	try:
		return await crud.get_posts(uid, public=public, private=private)
	except:
		raise HTTPException(status_code=500, detail="internal server error")
	