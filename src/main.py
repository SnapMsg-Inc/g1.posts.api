from fastapi import FastAPI

import datadog 
from ddtrace.runtime import RuntimeMetrics

RuntimeMetrics.enable()

app = FastAPI()

@app.get("/")
async def root():
	return {"message": "Posts microsevice"}

#
#    posts routes
#
#app.get("/users")(users.get_users)
#app.post("/users")(users.create_users)


