from fastapi import FastAPI, Query, Depends, Request, HTTPException
from fastapi.responses import JSONResponse
from typing import List, Annotated, Optional
from .models import PostCreate, PostQuery, PostUpdate, PostResponse
from . import crud 

import mongoengine
'''
import datadog
from ddtrace.runtime import RuntimeMetrics

RuntimeMetrics.enable()
'''
app = FastAPI()


@app.exception_handler(Exception)
async def error_handler(req: Request, exc):
    print("error")
    detail = "internal server error"
    if req.method == "POST":
        detail = "couldnt create resource"
    elif req.method == "DELETE":
        detail = "couldnt delete resource"
    elif req.method == "PATCH":
        detail = "couldnt update resource"
    return JSONResponse(status_code=400, content={"detail" : detail})
            

@app.on_event("startup")
def init_db_client():
    config = {
        "db" : "postsdb",
        "host" : "posts-db",
        "port" : 27017,
        "username" : "snapmsg",
        "password" : "snapmsg",
        "connectTimeoutMS" : 2000,
        "serverSelectionTimeoutMS" : 2000
    }
    mongoengine.connect(**config)

@app.on_event("shutdown")
def shutdown_db_client():
    mongoengine.disconnect()


@app.get("/")
async def root():
    return {"message": "posts microsevice"}


@app.post("/posts", status_code=201)
async def create_post(*, post: PostCreate):
    await crud.create_post(post)
    return {"message" : "post created"}


@app.get("/posts", response_model=List[PostResponse])
async def get_posts(*,
                    post: PostQuery = Depends(), 
                    limit: int = Query(default=100, ge=0, le=100), 
                    page: int = Query(default=0, ge=0)):
    return await crud.read_posts(post, limit, page)

@app.get("/posts/{pid}", response_model=PostResponse)
async def get_post(*, pid: str):
    return await crud.read_post(pid)


@app.patch("/posts/{pid}")
async def update_post(*, pid: str, post: Optional[PostUpdate] = None):
    if not post:
        return {"message", "nothing to update"}
    #await crud.update_post(uid, pid, post)
    print(post)
    return {"message" : "post updated"}


@app.delete("/posts/{pid}")
async def delete_post(*, pid: str):
    #await crud.delete_post(pid)
    return {"message" : "post deleted"}


@app.get("/posts/{uid}/recommended")#, response_model=List[Post])
async def get_recommended(*,
                          uid: str, 
                          limit: int = Query(default=100, ge=0, le=100), 
                          page: int = Query(default=0, ge=0)):
    #return await crud.get_recommended(uid, limit, page)
    pass


@app.post("/posts/{uid}/fav/{pid}")
async def add_fav(*, uid: str, otheruid: str, pid: str):
    #await crud.add_fav(uid, otheruid, pid)
    return {"message" : "fav added"}


@app.get("/posts/{uid}/fav")#, response_model=List[Post])
async def get_favs(*,
                   uid: str,
                   limit: int = Query(default=100, ge=0, le=100), 
                   page: int = Query(default=0, ge=0)):

    #return await crud.get_favs(uid, limit, page)
    pass


#@app.post("/posts/{uid}/fav/{otheruid}/{pid}")

