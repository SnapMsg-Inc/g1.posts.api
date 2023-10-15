from fastapi import FastAPI, HTTPException
from .models import *
from .crud import *
import mongoengine 
from bson import ObjectId
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

app = FastAPI()

# Convertir ObjectId a string y objetos a diccionarios
def jsonable_encoder_custom(obj):
    if isinstance(obj, ObjectId):
        return str(obj)
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, list):
        return [jsonable_encoder_custom(e) for e in obj]
    if isinstance(obj, dict):
        return {key: jsonable_encoder_custom(value) for key, value in obj.items()}
    return obj

@app.on_event("startup")
async def startup_db_client():
	mongoengine.connect(db='snapmsg', host='localhost', port=27017)

@app.on_event("shutdown")
async def shutdown_db_client():
	mongoengine.disconnect()

@app.get("/")
async def root():
	return {"message": "Posts microsevice"}


@app.post("/posts")
async def create_post_endpoint(post_in: PostIn):
	# Convertir el modelo Pydantic a un modelo MongoEngine
	
	post = Post(**post_in.dict())
	post.save()  # Guardar el post en la base de datos
	if post.id is None:
		raise HTTPException(status_code=400, detail="Post could not be created")
	return JSONResponse(content=jsonable_encoder_custom(post))

@app.get("/posts")
async def read_posts():
    mongo_posts = Post.objects.all()  # Obtener todos los posts
    pydantic_posts = [PydanticPost.from_mongo(post) for post in mongo_posts]
    return pydantic_posts  # FastAPI manejará la serialización a JSON