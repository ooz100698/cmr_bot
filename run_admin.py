"""
Starts the admin dashboard on http://localhost:8000/admin
Run this in a SEPARATE terminal from run_bot.py
"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
