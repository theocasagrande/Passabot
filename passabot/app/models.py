from pydantic import BaseModel
from typing import List, Optional, Literal

class Passenger(BaseModel):
    full_name: str

class CheckinRequest(BaseModel):
    pnr: str
    origin: str
    destination: str
    departure_date: str
    return_date: Optional[str] = None
    airline: Literal["Gol", "Latam", "Azul"]
    passengers: List[Passenger]

class CheckinResponse(BaseModel):
    status: Literal["success", "error"]
    checked_in: bool = False
    boarding_pass: Optional[str] = None
    message: str
    detail: Optional[str] = None