from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
import pandas as pd
import os

app = FastAPI(title="Seating Arrangement API")

@app.get("/")
def home():
    file_path = "index.html"
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return JSONResponse({"status": "error", "message": "index.html not found"}, status_code=404)

# Load Excel safely
try:
    df = pd.read_excel("seating.xlsx")
    # Clean and normalize data
    df.columns = df.columns.str.strip()  # Remove spaces in headers
    if "SeatNumber" in df.columns:
        # Convert everything to string and trim spaces
        df["SeatNumber"] = df["SeatNumber"].astype(str).str.strip()
except Exception as e:
    print("Error loading Excel:", e)
    df = pd.DataFrame()

@app.get("/get-seat")
def get_seat(seat_number: str):  # Accept as string
    if df.empty:
        return {"status": "error", "message": "Excel file not loaded or empty"}

    if "SeatNumber" not in df.columns:
        return {"status": "error", "message": "Column 'SeatNumber' not found in Excel"}

    # Compare as string (case-insensitive)
    seat_number = seat_number.strip()
    row = df[df["SeatNumber"].str.upper() == seat_number.upper()]

    if not row.empty:
        return {"status": "success", "data": row.iloc[0].to_dict()}
    else:
        return {
            "status": "error",
            "message": f"Seat number '{seat_number}' not found. "
                       "Please check if it matches exactly as in Excel.",
        }
