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
    df.columns = df.columns.str.strip()  # remove leading/trailing spaces
    df.columns = df.columns.str.replace(r"\s+", "", regex=True)  # remove spaces inside column names
    df.columns = df.columns.str.upper()  # make all uppercase for matching

    print("✅ Columns loaded from Excel:", df.columns.tolist())

    if "SEATNUMBER" in df.columns:
        df["SEATNUMBER"] = (
            df["SEATNUMBER"]
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

    if "SEATNUMBER" not in df.columns:
        return {"message": "Column 'SeatNumber' not found in Excel."}

    seat_number_clean = seat_number.strip().upper().replace(" ", "")
    row = df[df["SEATNUMBER"] == seat_number_clean]

    if not row.empty:
        data = row.iloc[0].to_dict()

        # Automatically detect the room column (any of these variations)
        possible_room_columns = ["ROOMNUMBER", "ROOMNO", "ROOM", "ROOM_NO"]
        room_number = None
        for key in data.keys():
            if key.replace(" ", "").upper() in possible_room_columns:
                room_number = data[key]
                break

        if not room_number:
            room_number = "N/A"

        return {"message": f"Room Number - {room_number}"}

    else:
        return {"message": "Seat Number not found, Contact Control ROOM No - 127"}
