from mongoengine import (
    Document, 
    IntField, 
    ListField, 
    StringField, 
    BooleanField,
    DateTimeField, 
    ReferenceField,
    EmbeddedDocument,
    EmbeddedDocumentField,
    CASCADE, 
    PULL 
)
from fastapi import Query, Depends
from typing_extensions import Annotated
from pydantic import BaseModel, Field, BeforeValidator, AfterValidator, model_validator
from datetime import datetime
from typing import List, Dict, Any, Optional, Generic, TypeVar
from collections.abc import Iterable


'''
    database models
'''
class BasePost(Document): 
    uid: str = StringField(required=True)  # author uid
    is_private: bool = BooleanField(default=True)
    timestamp = DateTimeField(default=datetime.utcnow)

    meta = {
        'indexes': [
            {
                'fields': [('uid', 1), ('timestamp', -1)],  # compound index 
            }
        ],
        'allow_inheritance': True,
    }


class Post(BasePost):
    text: str = StringField(required=True)
    media_uri: List[str] = ListField(StringField(), default=[])
    hashtags: List[str] = ListField(StringField(), default=[])
    likes: int = IntField(default=0, min_value=0)
    
        
class SnapShare(BasePost):
    post = ReferenceField(Post, reverse_delete_rule=CASCADE) # delete document when referenced is deleted

# `ReferenceField` will be automatically dereferenced on access (consider efficency)
# https://docs.mongoengine.org/apireference.html#mongoengine.fields.ReferenceField
PostReference = ReferenceField(Post, reverse_delete_rule=PULL)
SnapShareReference = ReferenceField(SnapShare, reverse_delete_rule=PULL)


class User(Document):
    uid: str = StringField(required=True, unique=True)
    public = ListField(PostReference, default=[]) 
    private = ListField(PostReference, default=[]) 
    favs = ListField(PostReference, default=[]) 
    liked = ListField(PostReference, default=[])
    snapshare = ListField(SnapShareReference, default=[])


class TopicMention(Document):
    timestamp = DateTimeField(default=datetime.utcnow)
    meta = {
        'indexes': [
            {
                'fields': ['timestamp'], 'expireAfterSeconds': (60 * 60 * 24) # ttl index
            }
        ]
    }

TopicMentionReference = ReferenceField(TopicMention, reverse_delete_rule=PULL)

class TrendingTopic(Document):
    topic = StringField(required=True, unique=True)
    mentions = ListField(TopicMentionReference, default=[])
    last_mentioned = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'indexes': [
            {
                'fields': ['last_mentioned'], 'expireAfterSeconds': (60 * 60 * 24) # ttl index
            }
        ]
    }
    

'''
    API models
'''
class BaseModelOptional(BaseModel): # BaseModel wrapper
    @model_validator(mode="after")
    def exclude_unset(cls, values: Any) -> Any:
        # remove unset attributes
        print(values)
        items = values.dict().items()
        for k, v in items:
            if v is None or (isinstance(v, Iterable) and not v):
                delattr(values, k)
        return values   

def pid_validator(pid):
    print(f"PID VALIDATOR: {str(pid)}")
    return str(pid)

def text_validator(t):
    assert len(t) <= 300, "text is larger than 300 chars"
    return t

def hashtag_validator(h):
    assert h.startswith('#') or '-' in h, "invalid hashtag format"
    return h


Text = Annotated[str, AfterValidator(text_validator)] 
PID = Annotated[str, BeforeValidator(lambda pid: str(pid))]
Hashtag = Annotated[str, AfterValidator(hashtag_validator)]

class PostCreate(BaseModel):
    uid: str     # author's uid
    text: Text
    media_uri: Optional[List[str]] = []
    hashtags: Optional[List[Hashtag]] = []
    is_private: bool = True


class PostUpdate(BaseModelOptional):
    text: Optional[Text] = None
    media_uri: Optional[List[str]] = []
    hashtags: Optional[List[Hashtag]] = None
    is_private: Optional[bool] = None


class PostQuery(BaseModelOptional):
    uid: List[str] = Field(Query([])) # author's uid
    text: Optional[Text] = None
    hashtags: List[Hashtag] = Field(Query([]))
    private: bool = False
    public: bool = True # show the publics by default
   
 
class PostResponse(PostCreate):
    pid: PID = Field(validation_alias="_id")
    likes: int = 0
    timestamp: datetime
    
    class Config:
        allow_population_by_field_name = True


class SnapShareResponse(BaseModel):
    pid: PID = Field(validation_alias="_id")
    uid: str 
    post: PostResponse
    is_private: bool
    timestamp: datetime
    
    class Config:
        allow_population_by_field_name = True
