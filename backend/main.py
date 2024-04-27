from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# import API routers
from api.generate_hypothesis import router as generate_hypothesis_router
from api.existing_response import router as response_router

# create FastAPI instance
app = FastAPI()

# define allowed origins for CORS to allow access from frontend
origins = [
    "http://localhost",
    "http://localhost:3000"
]

# add CORS middleware for access control
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# include API routers in the main FastAPI application instance
app.include_router(generate_hypothesis_router, prefix="/api")
app.include_router(response_router, prefix="/api")

if __name__ == "__main__":
    # run the FastAPI app using Uvicorn server
    uvicorn.run("main:app", host="0.0.0.0", port=8000)