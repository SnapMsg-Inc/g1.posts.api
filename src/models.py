from mongoengine import Document, StringField, DateTimeField, ListField, BooleanField, IntField
from datetime import datetime
from typing import List
from pydantic import BaseModel, Field
from bson import ObjectId

class PostIn(BaseModel):
    uid: str  # ID del creador
    content: str  # Contenido del post
    hashtags: List[str] = Field(default=[])  # Lista de hashtags
    is_private: bool = Field(default=False)  # Indica si el post es privado
    # Asumiendo que los campos likes y liked_by serán manejados por la aplicación,
    # por lo que no necesitan estar en el modelo de entrada.

class PydanticPost(BaseModel):
    id: str
    uid: str
    timestamp: datetime
    content: str
    hashtags: List[str] = Field(default=[])
    is_private: bool = Field(default=False)
    likes: int = Field(default=0)
    liked_by: List[str] = Field(default=[])

    class Config:
        json_encoders = {ObjectId: str, datetime: lambda dt: dt.isoformat()}

    @classmethod
    def from_mongo(cls, mongo_post):
        return cls(
            id=str(mongo_post.id),
            uid=mongo_post.uid,
            timestamp=mongo_post.timestamp,
            content=mongo_post.content,
            hashtags=mongo_post.hashtags,
            is_private=mongo_post.is_private,
            likes=mongo_post.likes,
            liked_by=mongo_post.liked_by
        )

# Los campos timestamp, likes y liked_by se manejarán automáticamente en el modelo MongoEngine,
# por lo que no necesitan estar en el modelo de entrada.

class Post(Document):
    uid = StringField(required=True)  # ID del creador
    timestamp = DateTimeField(default=datetime.utcnow)  # Fecha y hora del post
    content = StringField(required=True)  # Contenido del post
    hashtags = ListField(StringField(), default=list)  # Lista de hashtags
    is_private = BooleanField(default=False)  # Indica si el post es privado
    likes = IntField(default=0)  # Contador de likes
    liked_by = ListField(StringField(), default=list)  # IDs de usuarios que dieron "like"
    # otros campos relevantes

class UserProfile(Document):
    public = ListField(StringField(), default=list)  # IDs de posts públicos
    private = ListField(StringField(), default=list)  # IDs de posts privados
    favs = ListField(StringField(), default=list)  # IDs de posts favoritos
    # otros campos relevantes

class TrendingTopic(Document):
    hashtag = StringField(required=True)  # Hashtag
    count = IntField(required=True)  # Frecuencia de ocurrencia
    last_updated = DateTimeField(default=datetime.utcnow)  # Fecha y hora de la última actualización
    # otros campos relevantes
