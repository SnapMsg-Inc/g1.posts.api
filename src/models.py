from mongoengine import (
    DynamicDocument, 
    Document, 
    IntField, 
    ListField, 
    StringField, 
    BooleanField,
    DateTimeField, 
    ReferenceField,
    CASCADE 
)
from fastapi import Query, Depends
from typing_extensions import Annotated
from pydantic import Field, BeforeValidator, model_validator, root_validator
import pydantic
from datetime import datetime
from typing import List, Dict, Any, Optional, Generic, TypeVar



'''
    database models
'''

class Post(Document):
    pid: str = StringField(required=True, alias="_id") 
    uid: str = StringField(required=True)  # author uid
    text: str = StringField(required=True)
    media_uri: List[str] = ListField(StringField(), default=[])
    hashtags: List[str] = ListField(StringField(), default=[])
    is_private: bool = BooleanField(default=True)
    likes: int = IntField(default=0)
    timestamp: datetime = DateTimeField(default=datetime.utcnow)

    meta = {
        'indexes': [
            {
                'fields': [('uid', 1), ('timestamp', -1)],  # compound index 
            },
        ]
    }

# `ReferenceField` will be automatically dereferenced on access (consider efficency)
# https://docs.mongoengine.org/apireference.html#mongoengine.fields.ReferenceField
PostReference = ReferenceField(Post, reverse_delete_rule=CASCADE)

class User(Document):
    uid: str = StringField(required=True, unique=True)
    public = ListField(PostReference, default=[])
    private = ListField(PostReference, default=[])
    favs = ListField(PostReference, default=[])
    feed = ListField(PostReference, default=[])


'''
    API models
'''
class BaseModel(pydantic.BaseModel): # BaseModel wrapper
    @model_validator(mode="after")
    def exclude_none(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        for k, v in values.dict().items():
            if v is None:
                delattr(values, k)
        return values   

def text_validator(t):
    assert len(t) <= 300, "text is larger than 300 chars"
    return t

def hashtag_validator(h):
    assert h.startswith('#') or '-' in h, "invalid hashtag format"
    return h


Text = Annotated[str, BeforeValidator(text_validator)] 
Hashtag = Annotated[str, BeforeValidator(hashtag_validator)]

class PostCreate(BaseModel):
    uid: str     # author's uid
    text: Text
    media_uri: List[str]
    hashtags: List[Hashtag]
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
    hashtag: List[Hashtag] = Field(Query([]))
    private: bool = False
    public: bool = True # show the publics by default
   
 
class PostResponse(PostCreate):
    pid: str
    likes: int = 0
    timestamp: datetime


