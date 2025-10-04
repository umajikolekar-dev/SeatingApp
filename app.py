from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
import pandas as pd
import os

app = FastAPI(title="Seating Arrangement API")

# Serve HTML file
@app.get("/")
def home():
    file_path = "index.html"
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return JSONResponse({"status": "error", "message": "index.html not found"}, status_code=404)

# Load Excel once at startup (safe)
try:
    df = pd.read_excel("seating.xlsx")
except FileNotFoundError:
    df = pd.DataFrame()  # empty DataFrame fallback

@app.get("/get-seat")
def get_seat(seat_number: int):
    if df.empty:
        return {"status": "error", "message": "Excel file not loaded or empty"}

    # Convert seat number to match Excel data type if needed
    if "SeatNumber" not in df.columns:
        return {"status": "error", "message": "Column 'SeatNumber' not found in Excel"}

    row = df[df["SeatNumber"] == seat_number]
    if not row.empty:
        return {"status": "success", "data": row.iloc[0].to_dict()}
    else:
        return {"status": "error", "message": f"Seat number {seat_number} not found"}
