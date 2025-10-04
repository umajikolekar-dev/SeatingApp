from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import os

app = FastAPI(title="Seating Arrangement API")

# ✅ Enable CORS (important for frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # you can restrict this later to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    file_path = "index.html"
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return JSONResponse({"status": "error", "message": "index.html not found"}, status_code=404)

# ✅ Load Excel safely
excel_path = "seating.xlsx"

if not os.path.exists(excel_path):
    print(f"❌ Excel file not found at: {excel_path}")
    df = pd.DataFrame()
else:
    try:
        df = pd.read_excel(excel_path)
        df.columns = df.columns.str.strip()  # remove extra spaces in headers
        df = df.fillna("")  # ✅ Replace NaN with empty strings globally

        if "SeatNumber" in df.columns:
            # Normalize SeatNumber column
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

    # Normalize input exactly like Excel column
    seat_number_clean = seat_number.strip().upper().replace(" ", "")

    row = df[df["SeatNumber"] == seat_number_clean]

    if not row.empty:
        # ✅ Replace any NaN or invalid values before converting to dict
        clean_data = row.iloc[0].fillna("").to_dict()
        return {"status": "success", "data": clean_data}

    else:
        # For debugging — show first 10 seat numbers
        sample_seats = df["SeatNumber"].head(10).tolist()
        return {
            "status": "error",
            "message": f"Seat number '{seat_number}' not found.",
            "debug_sample": f"Sample seats from Excel: {sample_seats}",
        }
