# from .database import db
from .models import User, Post, PostCreate, PostQuery, PostUpdate, PostResponse
from typing import List, Dict, Any 
from collections.abc import Iterable
from mongoengine.queryset.visitor import Q
from mongoengine import DoesNotExist


import logging

MAX_FEED = 250

class CRUDException(Exception):
    message: str = "API error: "

    def __init__(self, message):
        self.message += message

    def __str__(self):
        return self.message



def get_mongo_query(post_query: PostQuery) -> Dict[str, Any]:
    query = Q() 
    for k, v in post_query.model_dump().items():
        if isinstance(v, str):
            query &= Q(**{f"{k}__contains" : v})
        elif isinstance(v, list):
            expr = map(lambda item: f"Q({k}__contains='{item}')", v)
            print(f"[INFO] expr: {expr}")
            query &= (eval(" | ".join(expr)))
        else:
            # ignore other type than list or str
            pass

    return query 


async def get_user(uid: str):
    try:
        user = User.objects.get(uid=uid)
    except DoesNotExist:
        print("[DEBUG] user doesnt exists")
        user = User(uid=uid).save() # init one if does not exist
    return user 


async def create_post(post_create: PostCreate):
    post = Post(**post_create.model_dump())
    post.save()
    post.reload() 
    user = await get_user(post.uid)

    if post.is_private:
        user.private.append(post)
    else:
        user.public.append(post)
    user.save()
    return post


async def read_post(pid: str) -> Dict[str, Any]:
    return Post.objects.as_pymongo().get(pk=pid)


async def read_posts(post_query: PostQuery, limit: int, page: int) -> List[Dict[str, Any]]:
    print(f"[INFO] posts: {post_query.__dict__}")
    public = post_query.__dict__.pop("public")
    private = post_query.__dict__.pop("private")

    if public and private:
        limit /= 2
    FROM, TO = limit * page, limit * (page + 1)
    
    query = get_mongo_query(post_query)
    db_posts = [] 

    if public:
        db_posts += Post.objects.filter(query, is_private=False)[FROM:TO].as_pymongo()
    if private:
        db_posts += Post.objects.filter(query, is_private=True)[FROM:TO].as_pymongo()

    print(f"[INFO] posts: {db_posts}")
    return db_posts


async def update_post(pid: str, post: PostUpdate):
    try:
        # post = Post.objects(id=pid).get()
        Post.objects(id=pid).get().update(**post.model_dump())
    except DoesNotExist:
        raise CRUDException("post doesnt exist")


async def delete_post(pid: str):
    post = Post.objects(id=pid).get()
    post.delete()


async def get_recommended(uid: str, limit: int, page: int) -> List[Dict[str, Any]]:
    return [] 


async def add_favs(uid: str, pid: str):
    user = await get_user(uid)
    post = Post.objects(id=pid).get()
    if post in user.favs:
        raise CRUDException("post already in favs")
    user.favs.append(post)
    user.save()
    print(user.to_mongo())


async def read_favs(uid: str, limit: int, page: int) -> List[Dict[str, Any]]:
    FROM, TO = limit * page, limit * (page + 1)
    user = await get_user(uid)
    favs = []
    print(user.to_mongo())
    for post in user.favs[FROM:TO]:
        favs.append(post.to_mongo().to_dict())
    return favs


async def delete_favs(uid: str, pid: str):
    user = await get_user(uid)
    post = Post.objects(id=pid).get()
    if post not in user.favs:
        raise CRUDException("post not in favs")
    user.favs.remove(post)
    user.save()


async def like_post(uid: str, pid: str):
    user = await get_user(uid)
    post = Post.objects(id=pid).get()
    if post in user.liked:
        raise CRUDException("like already exist")
    
    post.likes += 1
    user.liked.append(post)
    post.save()
    user.save()


async def unlike_post(uid: str, pid: str):
    user = await get_user(uid)
    post = Post.objects(id=pid).get()
    if post not in user.liked:
        raise CRUDException("like doesnt exist")

    post.likes -= 1
    user.liked.remove(post)
    post.save()
    user.save()

async def is_author(uid: str, pid: str):
    try: 
        post = Post.objects(id=pid).get()

        if post.uid == uid:
            return True

        return False
    except DoesNotExist:
        raise CRUDException("post doesnt exist")

async def is_liked(uid: str, pid: str):
    user = await get_user(uid)
    post = Post.objects(id=pid).get()
    if post in user.liked:
        return True
    return False

