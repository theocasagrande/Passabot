
from fastapi import FastAPI, HTTPException
from app.models import CheckinRequest, CheckinResponse
from app.service import process_checkin

app = FastAPI(title="Passabot")

@app.post("/checkin", response_model=CheckinResponse)
async def checkin(payload: CheckinRequest):
    try:
        return await process_checkin(payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))