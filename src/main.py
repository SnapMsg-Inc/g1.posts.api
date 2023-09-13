from fastapi import FastAPI
import psycopg2


app = FastAPI()

@app.get("/")
async def root():
	return {"message": "Posts microsevice"}

con = psycopg2.connect(
	database="postsdb",
	user="snapmsg",
	password="1234",
	host="posts-db",
	port= '5432'
)
#
#    posts routes
#
#app.get("/users")(users.get_users)
#app.post("/users")(users.create_users)


