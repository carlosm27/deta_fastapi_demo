from fastapi import FastAPI, File, UploadFile, HTTPException, status
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
from PIL import Image
from dotenv import load_dotenv

from deta import Deta
from io import BytesIO
import os
import logging


app = FastAPI()

load_dotenv()

PROJECT_KEY = os.environ.get('PROJECT_KEY')
deta = Deta(PROJECT_KEY)

drive = deta.Drive("webp_images")



@app.get("/", response_class=HTMLResponse)
def render():
    return """
    <form action="/upload" enctype="multipart/form-data" method="post">
        <input name="file" type="file">
        <input type="submit">
    </form>

    """

@app.post("/upload")
def upload_image(file: UploadFile = File(...)):
    

    if not file.filename.endswith(".webp") or not file:
        raise HTTPException(status_code=400 , detail = "Select a '.webp' file")

    webp_name = file.filename
    image = file.file

    try:

        img = webp_to_png(image)
        png_name = webp_name.replace(".webp", ".png")
        res = drive.put(png_name, img)   
        return JSONResponse(status_code =status.HTTP_201_CREATED, content={"message": f"Image: '{res}' successfully uploaded."})  
    except:
        return JSONResponse(status_code=500, content="There was an error converting or uploading the file")
                
    


@app.get("/convert/{name}")
def converter(name: str):

    res = drive.get(name)

    if res is None:
        raise HTTPException(status_code=404, detail="Image not found")
     
    return  StreamingResponse(res.iter_chunks(1024), media_type="image/png")


def webp_to_png(image):

    try:
        img = Image.open(image)
        img_io = BytesIO()
        img.save(img_io , 'PNG')
        img_io.seek(0)
    except OSError:
        print("Cannot convert") 
         
    finally:
        img.close()
    return img_io