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
        return {"message": "Excel file not loaded or empty."}

    if "SeatNumber" not in df.columns:
        return {"message": "Column 'SeatNumber' not found in Excel."}

    seat_number_clean = seat_number.strip().upper().replace(" ", "")
    row = df[df["SeatNumber"] == seat_number_clean]

    if not row.empty:
        data = row.iloc[0].to_dict()
        # Find the correct column name for room number (case-insensitive)
        room_key = next((k for k in data.keys() if k.lower() == "roomnumber"), None)
        room_number = data.get(room_key, "N/A") if room_key else "N/A"

        return {"message": f"Room Number - {room_number}"}
    else:
        return {"message": "Seat Number not found, Contact Control ROOM No - 127"}
