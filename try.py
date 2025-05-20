from fastapi import FastAPI
import time
import asyncio

app = FastAPI()

# Synchronous endpoint (blocks while sleeping)
@app.get("/sync")
def sync_endpoint():
    time.sleep(3)  # Simulate a blocking I/O task (3 seconds)
    return {"message": "Synchronous response after 3 seconds"}

# Asynchronous endpoint (does NOT block, uses await)
@app.get("/async")
async def async_endpoint():
    await asyncio.sleep(3)  # Simulate a non-blocking async task (3 seconds)
    return {"message": "Asynchronous response after 3 seconds"}
