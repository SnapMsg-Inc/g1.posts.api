# from .database import db
from .models import *
import bson
from typing import List, Union
import httpx, json
from fastapi import HTTPException
from mongoengine import DoesNotExist

async def check_follow_status(requesting_uid: str, target_uid: str) -> bool:
    url = f"https://users-ms-marioax.cloud.okteto.net/users/{requesting_uid}/follows/{target_uid}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
    # Retornar True si el follow existe, False en caso contrario
    return response.status_code == 200

def create_post(post: Post) -> Post:
    try:
        post.save()
        
        post.reload()  # Recargar el post para obtener el ID
    except Exception as e:
        return (f"Error al guardar el post: {e}")
        

    # Crear la referencia del post en el UserProfile correspondiente
    try:
        # Intentar obtener el UserProfile existente
        user_profile = UserProfile.objects.get(uid=post.uid)
    
    except DoesNotExist:
        # Crear uno nuevo si no existe
        user_profile = UserProfile(uid=post.uid).save()
    
    # Agregar la referencia del post en la lista correspondiente y guardar
    if post.is_private:
        user_profile.update(add_to_set__private=post.id)  # Usar post.id en lugar de post
    else:
        user_profile.update(add_to_set__public=post.id)  # Usar post.id en lugar de post
    
    user_profile.save()

    return {"message": "Post creado exitosamente", "post_id": str(post.id)}


def read_posts_by_user_id(uid: str, public: bool, private: bool = False) -> Union[List[PostOut], dict]:
    
    try:
        
        # Obtener el UserProfile asociado con el UID
        user_profile = UserProfile.objects.get(uid=uid)
        
    except DoesNotExist:
        return {"error": "Usuario no encontrado"}

    posts = []
    if public:
        posts.extend(user_profile.public)
    
    # Si private es True, agregar los posts privados a la lista de posts
    if private:
        posts.extend(user_profile.private)

    sorted(posts, key=lambda post: post.timestamp, reverse=True)  # Ordenar por timestamp descendente

    # Convertir los posts a PostOut y devolverlos
    return [convert_post_to_postout(post).dict() for post in posts]

def delete_post(post_id: str):
    try:
        post = Post.objects.get(id=post_id)
    except DoesNotExist:
        return {"error": "Post no encontrado"}
    
    
    post.delete()
    
    return {"message": "Post eliminado exitosamente"}