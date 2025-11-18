from fastapi import FastAPI
import uvicorn
from api.v1.auth_router import auth_router
from api.v1.wallet_router import wallet_router
from models_db.init_db import init_models
import asyncio


#app = FastAPI()

#if __name__ == "__main__":
 #   uvicorn.run(app="main:app", host="0.0.0.0", port=8000)


app = FastAPI()

app.include_router(auth_router)
app.include_router(wallet_router)

if __name__ == "__main__":
    if False:
        asyncio.run(init_models())
    
    uvicorn.run(app="main:app", host="0.0.0.0", port=8000)


