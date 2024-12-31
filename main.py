from fastapi import FastAPI,UploadFile,Form,Response
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.staticfiles import StaticFiles
from typing import Annotated
import sqlite3

con = sqlite3.connect('db.db', check_same_thread=False)
cur = con.cursor()

# 만약 배포를 하게 되면 백엔드 서버에서 테이블을 생성해줘야하는데 테이블이 없으면 데이터를 넣을 곳이 없음
# 따라서 백엔드코드에서 자동으로 생성 할 수 있도록 테이블을 넣어준거임
# 테이블이 있는 상태에서 들어가면 테이블이 존재한다는 애러를 발생하기 때문에 
# IF NOT EXIST라는 조건문을 넣으면, 테이블이 없을 때만 생성하게되는 SQL문이 생성됨
cur.execute(f"""
            CREATE TABLE IF NOT EXISTS items (
	            id INTEGER PRIMARY KEY,
	            title TEXT NOT NULL,
	            image BLOB,
	            price INTEGER NOT NULL,
	            description TEXT,
	            place TEXT NOT NULL,
	            insertAt INTEGER
            );
            """)

app = FastAPI()

@app.post('/items')
async def creat_items(image:UploadFile, 
                title:Annotated[str,Form()], 
                price:Annotated[int,Form()], 
                description:Annotated[str,Form()], 
                place:Annotated[str,Form()],
                insertAt:Annotated[int,Form()] 
                ):
    image_bytes = await image.read()
    cur.execute(f"""
                INSERT INTO 
                items(title, image, price, description, place, insertAt)
                VALUES ('{title}','{image_bytes.hex()}',{price},'{description}','{place}',{insertAt})
                """)
    con.commit()
    return '200'

@app.get('/items')
async def get_items():
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    rows = cur.execute(f"""
                       SELECT * from items;
                       """).fetchall()
    return JSONResponse( jsonable_encoder(
        dict(row) for row in rows
    ))

@app.get('/images/{item_id}')
async def get_image(item_id):
    cur = con.cursor()
    image_bytes = cur.execute(f"""
                              SELECT image from items WHERE id={item_id}
                              """).fetchone()[0]
    
    return Response(content=bytes.fromhex(image_bytes), media_type='image/*')

app.mount("/", StaticFiles(directory='frontend', html=True), name='frontend')