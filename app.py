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
    df.columns = df.columns.str.strip()  # remove leading/trailing spaces in headers

    if "SeatNumber" in df.columns:
        # Normalize SeatNumber column
        df["SeatNumber"] = (
            df["SeatNumber"]
            .astype(str)
            .str.strip()  # remove spaces
            .str.upper()  # make uppercase
            .str.replace(r"\s+", "", regex=True)  # remove internal spaces
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

    # Normalize the input exactly like the Excel column
    seat_number_clean = seat_number.strip().upper().replace(" ", "")

    row = df[df["SeatNumber"] == seat_number_clean]

    if not row.empty:
        return {"status": "success", "data": row.iloc[0].to_dict()}
    else:
        # DEBUG MODE: print what seat numbers exist (first 10)
        sample_seats = df["SeatNumber"].head(10).tolist()
        return {
            "status": "error",
            "message": f"Seat number '{seat_number}' not found.",
            "debug_sample": f"Here are some seat numbers from Excel: {sample_seats}",
        }
