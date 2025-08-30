from fastapi import FastAPI
from fastapi.responses import FileResponse
import pandas as pd

app = FastAPI()

# Serve HTML file
@app.get("/")
def home():
    return FileResponse("index.html")  # keep index.html in same folder

# Load Excel
df = pd.read_excel("seating.xlsx")

@app.get("/get-seat")
def get_seat(seat_number: int):
    row = df[df["SeatNumber"] == seat_number]
    if not row.empty:
        return {"status": "success", "data": row.iloc[0].to_dict()}
    else:
        return {"status": "error", "message": "Seat number not found"}