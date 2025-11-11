import uvicorn
from fastapi import FastAPI
from backend.endpoints.user_endpoint import router as user_rt
from backend.endpoints.resume_endpoint import router as resume_rt

app = FastAPI()

app.include_router(router=user_rt, prefix="/api/v1/users", tags=['users'])
app.include_router(router=resume_rt, prefix="/api/v1/resume", tags=['resume'])

@app.get("/")
async def root():
    print(user_rt.prefix)
    return {"message": "Hello World"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0")