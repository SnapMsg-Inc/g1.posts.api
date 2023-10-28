# from .database import db
from .models import User, Post, PostCreate, PostQuery, PostUpdate, PostResponse
from typing import List, Dict, Any 
from collections.abc import Iterable
from mongoengine import DoesNotExist

import logging


def get_mongo_query(post_query: PostQuery) -> Dict[str, Any]:
    mongo_query = {}
    for k, v in post_query.model_dump().items():
        if isinstance(v, Iterable):
            for item in v:
                mongo_query[f"{k}__contains"] = item
        else:
            mongo_query[f"{k}__contains"] = v
    return mongo_query


async def get_user(uid: str):
    try:
        user = User.objects.get(uid=uid)
    except DoesNotExist:
        user = User(uid=uid).save() # init one if does not exist
    return user 


async def populate_feed(post: Post):
    # user = User.objects(uid=post.uid).as_pymongo().get()
    user = await get_user(post.uid)
    to_populate = user.followers
    
    for db_user in user.followers:
        # db_user = await get_user(_id)
        # establish a limit in length of feed
        db_user.update(add_to_set__feed=post)
        db_user.save()


async def create_post(post: PostCreate):
    db_post = Post(**post.model_dump())
    db_post.save()
    db_post.reload() 
    user = await get_user(post.uid)

    if post.is_private:
        user.update(add_to_set__private=db_post)
    else:
        user.update(add_to_set__public=db_post)
    user.save()

    return db_post


async def read_post(pid: str) -> Dict[str, Any]:
    return Post.objects.as_pymongo().get(pk=pid)


async def read_posts(post_query: PostQuery, limit: int, page: int) -> List[Dict[str, Any]]:
    public = post_query.__dict__.pop("public")
    private = post_query.__dict__.pop("private")

    if public and private:
        limit /= 2
    FROM, TO = limit * page, limit * (page + 1)
    
    query = get_mongo_query(post_query)
    print(f"[INFO] posts: {query}")

    db_posts = [] 
    if public:
        db_posts += Post.objects.filter(is_private=False, **query)[FROM:TO].as_pymongo()
    if private:
        db_posts += Post.objects.filter(is_private=True, **query)[FROM:TO].as_pymongo()

    return db_posts


async def update_post(pid: str, post: PostUpdate):
    pass


async def delete_post(pid: str):
    db_post = Post.objects(id=pid).get()
    db_post.delete()


async def subscribe_feed(uid: str, otheruid: str):
    # save a reference to `uid` in `otheruid`, in order to populate feed 
    user = await get_user(uid)
    otheruser = await get_user(otheruid)
    otheruser.update(add_to_set__followers=user)
    otheruser.save()


async def unsubscribe_feed(uid: str, otheruid: str):
    user = await get_user(uid)
    otheruser = await get_user(otheruid)
    otheruser.update(pull__followers=user)
    otheruser.save()


async def get_feed(uid: str, limit: int, page: int) -> List[Dict[str, Any]]:
    # user = User.objects.as_pymongo().get(uid=uid)
    FROM, TO = limit * page, limit * (page + 1)
    
    user = await get_user(uid)
    feed = []

    for post in user.feed:
        feed.append(post.to_mongo().to_dict())

    return feed 


async def get_recommended(uid: str, limit: int, page: int) -> List[Dict[str, Any]]:
    pass


async def add_favs(uid: str, pid: str):
    pass


async def read_favs(uid: str, limit: int, page: int) -> List[Dict[str, Any]]:
    pass


async def delete_favs(uid: str, pid: str):
    pass


async def like_post(uid: str, pid: str):
    pass


async def unlike_post(uid: str, pid: str):
    pass



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
