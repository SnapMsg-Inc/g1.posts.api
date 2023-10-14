from pydantic import BaseModel, Field
from typing import List, Dict


''' Design del domingo '''
class Post(BaseModel):
    # pid: str = Field(default=None, alias="_id")
    hashtags: List[str] = Field(default=[])
    text: str = Field(..., max_length=300)
    mediaURI: List[str] = Field(default=[])
    likes: int = 0
    # public: bool = False
    class Config:
        from_attributes=True

class User(BaseModel):
    uid: str = Field(..., alias="_id")
    public: Dict[int, Post] = Field(default={})
    private: Dict[int, Post] = Field(default={})
    favs: Dict[int, Post] = Field(default={})
    lastpid: int = -1 # check if its necessary

''' End design del domingo '''

class PostCreate(BaseModel):
    hashtags: List[str] = Field(default=[])
    text: str = Field(..., max_length=300)
    mediaURI: List[str] = Field(default=[])
    is_public: bool


    # class Config:
        # allow_population_by_field_name = True
        # arbitrary_types_allowed = True
        # json_encoders = {ObjectId: str}
        # schema_extra = {
        #     "example": {
        #         "name": "Jane Doe",
        #         "email": "jdoe@example.com",
        #         "course": "Experiments, Science, and Fashion in Nanophotonics",
        #         "gpa": "3.0",
        #     }
        # }