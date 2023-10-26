# from .database import db
from .models import PostCreate, PostQuery, PostUpdate, Post, User
from typing import List, Dict, Any 
from mongoengine import DoesNotExist


async def create_post(post: PostCreate):
    db_post = Post(**post.dict())
    db_post.save()
    db_post.reload() 

    # retrieve user (create one if does not exist)
    try:
        user = User.objects.get(uid=post.uid)
    except DoesNotExist:
        user = User(uid=post.uid).save()

    if post.is_private:
        user.update(add_to_set__private=db_post)
    else:
        user.update(add_to_set__public=db_post)
    user.save()


async def read_post(pid: str):
    return Post.objects.get(pid=pid) 


async def read_posts(post: PostQuery, limit: int, page: int):
    if public and private:
        limit /= 2
    FROM, TO = limit * page, limit * (page + 1)

    public = post.__dict__.pop("public")
    private = post.__dict__.pop("private")
    db_posts = []
    if public:
        db_posts += Post.objects(is_private=False, **post.dict())[FROM:TO]
    if private:
        db_posts += Post.objects(is_private=True, **post.dict())[FROM:TO]
    logging.info(f"[INFO] posts: {db_posts}")
    return db_posts


'''


def read_posts_by_user_id(uid: str,
                          public: bool,
                          private: bool = False) -> Union[List[PostOut], dict]:

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

    sorted(posts, key=lambda post: post.timestamp,
           reverse=True)  # Ordenar por timestamp descendente

    # Convertir los posts a PostOut y devolverlos
    return [convert_post_to_postout(post).dict() for post in posts]


def delete_post(post_id: str):
    try:
        post = Post.objects.get(id=post_id)
    except DoesNotExist:
        return {"error": "Post no encontrado"}

    post.delete()

    return {"message": "Post eliminado exitosamente"}
'''
