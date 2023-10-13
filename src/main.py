from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
	return {"message": "Posts microsevice"}

#
#    posts routes
#
#app.get("/users")(users.get_users)
#app.post("/users")(users.create_users)


