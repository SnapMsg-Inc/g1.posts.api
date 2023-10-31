from fastapi import FastAPI, Query, Depends, Request, HTTPException
from fastapi.responses import JSONResponse
from typing import List, Annotated, Optional
from .models import Post, PostCreate, PostQuery, PostUpdate, PostResponse
from . import crud 

import mongoengine

from ddtrace.runtime import RuntimeMetrics
import datadog 

RuntimeMetrics.enable()

app = FastAPI()


@app.exception_handler(Exception)
async def error_handler(req: Request, exc):
    detail = "internal server error"
    if isinstance(exc, crud.CRUDException):
        detail = str(exc)
    return JSONResponse(status_code=400, content={"detail" : detail})
            

#@app.on_event("startup")
#def init_db_client():
config = {
    "db" : "postsdb",
    "host" : "posts-db-mongodb",
    "port" : 27017,
    "username" : "root",
    "password" : "snapmsg",
    "authentication_source" : "admin",
    "connectTimeoutMS" : 2000,
    "serverSelectionTimeoutMS" : 2000
}
url = "mongodb://snapmsg:snapmsg@posts-db-mongodb:27017/postsdb"
mongoengine.connect(**config)

@app.on_event("shutdown")
def shutdown_db_client():
    mongoengine.disconnect()


@app.get("/")
async def root():
    return {"message": "posts microsevice"}


@app.post("/posts", status_code=201)
async def create_post(*, post: PostCreate):
    db_post = await crud.create_post(post)
    return {"message" : "post created"}


@app.get("/posts", response_model=List[PostResponse])
async def get_posts(*,
                    post: PostQuery = Depends(), 
                    limit: int = Query(default=100, ge=0, le=100), 
                    page: int = Query(default=0, ge=0)):
    return await crud.read_posts(post, limit, page) 


@app.get("/posts/{pid}", response_model=PostResponse)
async def get_post(*, pid: str):
    return await crud.read_post(pid) # returns a dict, pydantic does the rest


@app.patch("/posts/{pid}")
async def update_post(*, pid: str, post: Optional[PostUpdate] = None):
    if not post:
        return {"message", "nothing to update"}
    await crud.update_post(pid, post)
    return {"message" : "post updated"}


@app.delete("/posts/{pid}")
async def delete_post(*, pid: str):
    await crud.delete_post(pid)
    return {"message" : "post deleted"}


@app.get("/posts/{uid}/recommended", response_model=List[PostResponse])
async def get_recommended(*,
                          uid: str, 
                          limit: int = Query(default=100, ge=0, le=100), 
                          page: int = Query(default=0, ge=0)):
    return await crud.get_recommended(uid, limit, page)


@app.post("/posts/{uid}/favs/{pid}")
async def add_favs(*, uid: str, pid: str):
    await crud.add_favs(uid, pid)
    return {"message" : "post added to favs"}


@app.get("/posts/{uid}/favs", response_model=List[PostResponse])
async def get_favs(*,
                   uid: str,
                   limit: int = Query(default=100, ge=0, le=100), 
                   page: int = Query(default=0, ge=0)):
    return await crud.read_favs(uid, limit, page)


@app.delete("/posts/{uid}/favs/{pid}")
async def delete_favs(*, uid: str, pid: str):
    await crud.delete_favs(uid, pid)
    return {"message" : "post deleted from favs"}


@app.post("/posts/{uid}/likes/{pid}")
async def like_post(*, uid: str, pid: str):
    await crud.like_post(uid, pid)
    return {"message" : "post liked"}

@app.get("/posts/{uid}/likes/{pid}")
async def is_liked(*, uid: str, pid: str):
    is_liked = await crud.is_liked(uid, pid)
    if not is_liked:
        raise HTTPException(status_code=404, detail="not liked")
    return {"message": "the post is liked"}


@app.delete("/posts/{uid}/likes/{pid}")
async def unlike_post(*, uid: str, pid: str):
    await crud.unlike_post(uid, pid)
    return {"message" : "post unliked"}


@app.get("/posts/{uid}/author/{pid}", response_model=bool)
async def is_author(*, uid: str, pid: str):
    is_author = await crud.is_author(uid, pid)
    if not is_author:
        raise HTTPException(status_code=404, detail="not author")
    return {"message": "the user is the author"}    




