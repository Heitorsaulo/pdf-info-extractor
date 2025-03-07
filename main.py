from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from extractor import extract_text_from_pdf, get_relevant_info_from_openai, create_excel_from_analysis
import os
import json

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("static", StaticFiles(directory="static"), name="static")

@app.post("/extract_pdf")
async def extract_info(file: UploadFile = File(...)):
    pdf_bytes = await file.read()
    text = extract_text_from_pdf(pdf_bytes)

    if not text:
        return {"error": "Não foi possível extrair texto do PDF."}

    extracted_info_json = get_relevant_info_from_openai(text)
    excel_data = create_excel_from_analysis(extracted_info_json)

    # Salvar o arquivo Excel
    output_path = "static/output.xlsx"
    with open(output_path, "wb") as f:
        f.write(excel_data)

    extracted_info = json.loads(extracted_info_json)
    summary = extracted_info.get("summary", "")
    key_points = extracted_info.get("key_points", [])

    return {
        "summary": summary,
        "key_points": key_points,
        "excel_file": "static/output.xlsx"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)