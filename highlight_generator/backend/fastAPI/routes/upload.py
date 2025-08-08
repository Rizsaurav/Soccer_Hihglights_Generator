from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import FileResponse, JSONResponse
import uuid
import os
import psutil
from backend.fastAPI.services.pipeline import run_highlight_pipeline

router = APIRouter()

# Get the PID of the first process to prevent duplicated runs
parent_pid = os.getpid()
parent_process = psutil.Process(parent_pid)

@router.post("/upload")
async def upload_video(video: UploadFile = File(...)):
    # Skip if this is a child reload process
    if any("watchgod" in child.name() for child in parent_process.children(recursive=True)):
        return JSONResponse(status_code=200, content={"message": "⚠️ Dev reload duplicate. Skipped execution."})

    input_filename = f"temp_input_{uuid.uuid4().hex}.mp4"
    output_filename = f"highlight_{uuid.uuid4().hex}.mp4"
    output_path = os.path.abspath(output_filename)

    try:
        with open(input_filename, "wb") as f:
            f.write(await video.read())

        print(f"[🎬] 🔁 Running highlight pipeline")
        final_output = run_highlight_pipeline(input_filename, output_path)

        if not os.path.exists(final_output):
            raise HTTPException(status_code=404, detail="❌ No highlights generated.")

        return FileResponse(final_output, media_type="video/mp4", filename="highlights.mp4")

    except Exception as e:
        print("[❌ ERROR]", str(e))
        return JSONResponse(status_code=500, content={"error": "Internal Server Error."})

    finally:
        if os.path.exists(input_filename):
            os.remove(input_filename)
