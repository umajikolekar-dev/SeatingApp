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
    df.columns = df.columns.str.strip()  # remove extra spaces in headers

    if "SeatNumber" in df.columns:
        df["SeatNumber"] = (
            df["SeatNumber"]
            .astype(str)
            .str.strip()
            .str.upper()
            .str.replace(r"\s+", "", regex=True)
        )
    else:
        print("⚠️ Column 'SeatNumber' not found in Excel.")
except Exception as e:
    print("❌ Error loading Excel:", e)
    df = pd.DataFrame()

@app.get("/get-seat")
def get_seat(seat_number: str):
    if df.empty:
        return {"status": "error", "message": "Excel file not loaded or empty"}

    if "SeatNumber" not in df.columns:
        return {"status": "error", "message": "Column 'SeatNumber' not found in Excel"}

    seat_number_clean = seat_number.strip().upper().replace(" ", "")
    row = df[df["SeatNumber"] == seat_number_clean]

    if not row.empty:
        data = row.iloc[0].to_dict()
        # Rename column key if it’s “RoomNumber” → show as “Room number”
        formatted_data = {}
        for key, value in data.items():
            if key.lower() == "roomnumber":
                formatted_data["Room number"] = value
            else:
                formatted_data[key] = value

        return {"status": "success", "data": formatted_data}

    else:
        return {
            "status": "error",
            "message": f"Seat number '{seat_number}' not found. Please contact CONTROL ROOM (Room Number - 127) immediately.",
        }
