from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import uvicorn
from dotenv import load_dotenv
from .api import master_router
from .database import setup_database, populate_database, drop_all_tables

# Load environment variables from .env
load_dotenv()

app = FastAPI()

## API VERSION: 1
app.include_router(master_router, tags=["API Router"])


# Add CORS middleware to allow specific origins or all
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # This will later be changed to the actual allowed origin from which requests can be made
    allow_credentials=True,
    allow_methods=["*"],  # specific methods like GET, POST etc. or use ["*"] for all methods
    allow_headers=["*"],  # specific headers like ["Content-Type", "Authorization"] or use ["*"] for all headers
)


@app.on_event("startup")
async def startup_event():
    await drop_all_tables()
    await setup_database()
    await populate_database()

# Testing Endpoint
@app.get('/')
async def index():
    return {"message": "Hello, World!"}


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=int(os.getenv('SERVER_PORT', 5200)))
