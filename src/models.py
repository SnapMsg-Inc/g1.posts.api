from mongoengine import ReferenceField, ListField
from pydantic import BaseModel, Field, validator
from datetime import datetime
from mongoengine import Document, StringField, DateTimeField, IntField, BooleanField
from typing import List


# Modelo Pydantic para la entrada de datos
class PostIn(BaseModel):
    uid: str  # ID del creador
    content: str  # Contenido del post
    hashtags: List[str] = Field(default=[])  # Lista de hashtags
    is_private: bool = Field(default=False)  # Indica si el post es privado

    @validator('content')
    def validate_content(cls, value):
        if len(value) > 280:  # Ejemplo: limitar el contenido a 280 caracteres
            raise ValueError("El contenido es demasiado largo")
        return value

    @validator('hashtags', pre=True)
    def validate_hashtags(cls, value):
        if not all(isinstance(item, str) and item.startswith('#') for item in value):
            raise ValueError("Todos los hashtags deben ser cadenas que comienzan con '#'")
        return value

class Post(Document):
    uid = StringField(required=True)  # ID del creador
    timestamp = DateTimeField(default=datetime.utcnow)  # Fecha y hora del post
    content = StringField(required=True)  # Contenido del post
    hashtags = ListField(StringField(), default=list)  # Lista de hashtags
    is_private = BooleanField(default=False)  # Indica si el post es privado
    likes = IntField(default=0)  # Contador de likes
    liked_by = ListField(StringField(), default=list)  # IDs de usuarios que dieron "like"

    meta = {
        'indexes': [
            {
                'fields': [('uid', 1), ('timestamp', -1)],  # Índice compuesto en uid (ascendente) y timestamp (descendente)
            },
        ]
    }

# Modelo Pydantic para la salida JSON
class PostOut(BaseModel):
    uid: str
    timestamp: datetime
    content: str
    hashtags: List[str]
    is_private: bool
    likes: int
    liked_by: List[str]

# Función para convertir un modelo Pydantic a un modelo MongoEngine
def convert_postin_to_post(post_in: PostIn) -> Post:
    return Post(
        uid=post_in.uid,
        content=post_in.content,
        hashtags=post_in.hashtags,
        is_private=post_in.is_private
    )

def convert_post_to_postout(post: Post) -> PostOut:
    return PostOut(
        uid=post.uid,
        timestamp=post.timestamp,
        content=post.content,
        hashtags=post.hashtags,
        is_private=post.is_private,
        likes=post.likes,
        liked_by=post.liked_by
    )

class UserProfile(Document):
    uid = StringField(required=True, unique = True)  # ID del usuario
    public = ListField(ReferenceField(Post), default=list())  # Lista de referencias a posts públicos
    private = ListField(ReferenceField(Post), default=list())  # Lista de referencias a posts privados
    favs = ListField(ReferenceField(Post), default=list()) 

