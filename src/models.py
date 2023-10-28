from mongoengine import (
    Document, 
    IntField, 
    ListField, 
    StringField, 
    BooleanField,
    DateTimeField, 
    ReferenceField,
    EmbeddedDocumentField,
    CASCADE 
)
from fastapi import Query, Depends
from typing_extensions import Annotated
from pydantic import Field, BeforeValidator, AfterValidator, model_validator
import pydantic
from datetime import datetime
from typing import List, Dict, Any, Optional, Generic, TypeVar
from collections.abc import Iterable


'''
    database models
'''

class Post(Document):
    #pid: str = Field(required=True, alias="_id") 
    uid: str = StringField(required=True)  # author uid
    text: str = StringField(required=True)
    media_uri: List[str] = ListField(StringField(), default=[])
    hashtags: List[str] = ListField(StringField(), default=[])
    is_private: bool = BooleanField(default=True)
    timestamp: datetime = DateTimeField(default=datetime.utcnow)
    likes: List[str] = ListField(StringField(), default=[])

    meta = {
        'indexes': [
            {
                'fields': [('uid', 1), ('timestamp', -1)],  # compound index 
            },
        ]
    }
    __auto_convert = True
        

# `ReferenceField` will be automatically dereferenced on access (consider efficency)
# https://docs.mongoengine.org/apireference.html#mongoengine.fields.ReferenceField
PostReference = ReferenceField(Post, reverse_delete_rule=CASCADE)
UserReference = ReferenceField('User', reverse_delete_rule=CASCADE)
#PostListReference = ReferenceField('PostList', reverse_delete=CASCADE)

#class PostList(Document):
#    posts: ListField(PostReference, default=[])


class User(Document):
    uid: str = StringField(required=True, unique=True)
    public = ListField(PostReference, default=[]) 
    private = ListField(PostReference, default=[]) 
    favs = ListField(PostReference, default=[]) 
    feed = ListField(PostReference, default=[])  # subscriptions to different user posts
    followers = ListField(UserReference, default=[])


'''
    API models
'''
class BaseModel(pydantic.BaseModel): # BaseModel wrapper
    @model_validator(mode="after")
    def exclude_unset(cls, values: Any) -> Any:
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
Hashtag = Annotated[str, AfterValidator(hashtag_validator)]
PID = Annotated[str, BeforeValidator(lambda pid: str(pid))]

class PostCreate(BaseModel):
    uid: str     # author's uid
    text: Text
    media_uri: List[str] = []
    hashtags: List[Hashtag] = []
    is_private: bool = True


class PostUpdate(BaseModel):
    text: Optional[Text] = None
    media_uri: Optional[str] = None
    hashtags: Optional[List[Hashtag]] = None
    is_private: Optional[bool] = None


class PostQuery(BaseModel):
#    pid: Optional[str] = None
    uid: Optional[str] = None  # author's uid
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


