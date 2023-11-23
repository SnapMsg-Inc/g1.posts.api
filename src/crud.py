# from .database import db
from .models import (
    User, 
    BasePost, 
    Post, 
    SnapShare,
    PostCreate, 
    PostQuery, 
    PostUpdate, 
    PostResponse,
    TrendingTopic,
    TopicMention,
)
from typing import List, Dict, Any 
from collections.abc import Iterable
from mongoengine.queryset.visitor import Q
from mongoengine import DoesNotExist

from datetime import datetime, timedelta

import logging


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


async def get_trending_topic(topic: str):
    try:
        trending = TrendingTopic.objects.get(topic=topic)
    except DoesNotExist:
        print("[DEBUG] trending doesnt exists")
        trending = TrendingTopic(topic=topic).save() # init one if does not exist
    return trending 


async def update_trending_topics(post: PostQuery):
    # try:
    for topic in post.hashtags:
        print("HERE")
        mention = TopicMention()
        mention.save()
        trending_topic = await get_trending_topic(topic)
        trending_topic.mentions.append(mention)
        trending_topic.last_mentioned = datetime.utcnow
        trending_topic.save()
    # except Exception as e:
        # logging.error(f"error updating trending topic: {e}")


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

    FROM, TO = limit * page, limit * (page + 1)

    query = get_mongo_query(post_query)
    db_posts = [] 

    if public and private:
        db_posts = BasePost.objects.filter(query)[FROM:TO].order_by("-timestamp").as_pymongo()
    elif public:
        # only posts that are public
        db_posts = Post.objects.filter(query, is_private=False)[FROM:TO].order_by("-timestamp").as_pymongo()
    elif private:
        db_posts = BasePost.objects.filter(query, is_private=True)[FROM:TO].order_by("-timestamp").as_pymongo()

    return db_posts


async def update_post(pid: str, post: PostUpdate):
    try:
        Post.objects(id=pid).get().update(**post.model_dump())
    except DoesNotExist:
        raise CRUDException("post doesnt exist")


async def delete_post(pid: str):
    try:
        post = Post.objects(id=pid).get()
    except DoesNotExist:
        raise CRUDException("post does not exist")
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
        raise CRUDException("like does not exist")

    post.likes -= 1
    user.liked.remove(post)
    post.save()
    user.save()


async def is_author(uid: str, pid: str):
    try: 
        post = Post.objects(id=pid).get()
        if post.uid == uid:
            return True
    except DoesNotExist:
        raise CRUDException("post does not exist")
    return False


async def is_liked(uid: str, pid: str):
    user = await get_user(uid)
    post = Post.objects(id=pid).get()
    if post in user.liked:
        return True
    return False


async def delete_user(uid: str):
    try:
        user = User.objects(uid=uid).get()
    except DoesNotExist:
        raise CRUDException("user does not exist")
    # delete all posts with user as author 
    post = Post.objects(uid=uid).delete()
    user.delete()


async def create_snapshare(uid: str, pid: str):
    user = await get_user(uid)
    
    try:
        post = Post.objects.get(id=pid)
    except DoesNotExist:
        raise CRUDException("post does not exist")

    snapshare = SnapShare(uid=uid, post=post).save()
    user.snapshare.append(snapshare)
    user.save()


async def read_snapshares(uid: str, limit: int, page: int):
    user = await get_user(uid)
    FROM, TO = limit * page, limit * (page + 1)
    snapshares = []

    for db_snapshare in user.snapshare[FROM:TO]:
        post = db_snapshare.post.to_mongo()
        snapshare = db_snapshare.to_mongo()
        snapshare['post'] = post
        snapshares.append(snapshare.to_dict())
    return snapshares


async def is_snapshared(uid: str, pid: str):
    user = await get_user(uid)
    try:
        snapshare = SnapShare.objects(uid=uid, post=post)
    except DoesNotExist:
        return False
    return True


async def delete_snapshare(pid: str):
    try:
        snapshare = SnapShare.objects(id=pid).get()
    except DoesNotExist:
        raise CRUDException("snapshare does not exist")
    snapshare.delete()

    
async def get_trending_topics(limit: int, page: int):
    FROM, TO = limit * page, limit * (page + 1)
    topics = TrendingTopic.objects()[FROM:TO].order_by('-mentions')
    return [{"topic": topic.topic, "mention_count": len(topic.mentions)} for topic in topics]

