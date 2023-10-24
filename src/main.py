from fastapi import FastAPI, Query, HTTPException
from .models import *
from .crud import *
import mongoengine 
from mongoengine import get_db
import httpx

import datadog 
from ddtrace.runtime import RuntimeMetrics

RuntimeMetrics.enable()


app = FastAPI()

@app.on_event("startup")
async def startup_db_client():
    mongoengine.connect(db='snapmsg', host='localhost', port=27017)
    # db = get_db()
    # for collection in db.list_collection_names():
    #     db.drop_collection(collection)
    

@app.on_event("shutdown")
async def shutdown_db_client():
	mongoengine.disconnect()


@app.get("/")
async def root():
	return {"message": "Posts microsevice"}


@app.get("/posts", status_code=200)
async def get_all_posts():
    
    posts = Post.objects().all()  # Recupera todos los posts de la base de datos
    
    return [convert_post_to_postout(post).dict() for post in posts]


@app.get("/posts/{uid}", response_model=List[PostOut])
async def read_posts_by_user_id_endpoint(
    requesting_uid: str,  # Asumiendo que tienes el uid del usuario que hace la solicitud
    target_uid: str,
    public: bool = Query(True, alias="public"),
    private: bool = Query(False, alias="private")
):
    is_following = await check_follow_status(requesting_uid, target_uid)
    
    # Si no está siguiendo, solo puede ver los posts públicos
    if not is_following:
        private = False

    posts_or_error = read_posts_by_user_id(target_uid, public, private)

    if isinstance(posts_or_error, dict) and "error" in posts_or_error:
        raise HTTPException(status_code=404, detail=posts_or_error["error"])

    return posts_or_error
     

@app.get("/posts/{uid}/{pid}")
async def get_post_by_id_endpoint(uid: str, pid: str):
    
    try:
    
        post = Post.objects.get(id=pid)
    
    except DoesNotExist:
    
        return {"error": "El post fue eliminado o no existe"}
    
    
    return convert_post_to_postout(post).dict()


@app.post("/posts", status_code=201)
async def create_post_endpoint(post_in: PostIn):
    
    post_or_error = create_post(convert_postin_to_post(post_in))

    if isinstance(post_or_error, dict) and "error" in post_or_error:
        raise HTTPException(status_code=404, detail=post_or_error["error"])
    
    return post_or_error
    

@app.delete("/posts/{pid}")
async def delete_post_endpoint(pid: str):
    
    result = delete_post(pid)
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result
