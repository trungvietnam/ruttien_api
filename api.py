from datetime import datetime
from typing import Union
import uuid as uuid_pkg

from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError

from fastapi import Depends, FastAPI, HTTPException, status

import database, model
from sqlalchemy.orm import Session, sessionmaker
import cua_hang

app = FastAPI()


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


# model.Base.metadata.create_all()
from typing import Annotated
import pydantic


class GiaoDichUpdate(BaseModel):
    trang_thai: str
    so_tien: int
    ma_giao_dich: str
    phi_thu: float

class TrangThaiGDUpdate(BaseModel):
    trang_thai: str


class GiaoDichBase(BaseModel):
    id: int
    phi_thu: float = 6.0
    sdt_momo_pay: str
    # ma_giao_dich: str
    ngay_gd: datetime
    stk_ngan_hang: str
    ma_cuahang: str
    bang_chung_img: str
    trang_thai: str


@app.get("/")
async def read_root(db: Session = Depends(get_db)):
    # crud.get_items()
    return {"Hello": "world"}


@app.get("/update_doanhthu")
async def update_doanhthu_cuahang():
    #     chỉ chạy 1 lần trong ngày

    return None


@app.get("/get_qrcode")
async def get_qrcode(db: Annotated[Session, Depends(get_db)]):
    from sqlalchemy import func, select, not_, exists, text

    query = """
select FLOOR(390 + RAND() * 9999999) AS ma_gd FROM `giaodich` WHERE giaodich.id  IN (SELECT id FROM giaodich WHERE id IS NOT NULL) LIMIT 1;
        """

    result = db.execute(text(query)).fetchone()
    if result:
        ma_gd = int(result[0])

        print("Mã giao dịch mới:", ma_gd)
    else:
        ma_gd = 6868
    # cua_hang.tong_doanh_thu()
    return {'ma_giao_dich': ma_gd}


@app.put("/giao_dich/{ma_giao_dich}")
async def update_giaodich(ma_giao_dich: str, update_giaodich: GiaoDichUpdate, db: Session = Depends(get_db)):
    print(ma_giao_dich)
    try:
        giao_dich = db.query(model.GiaoDich).filter(model.GiaoDich.id == ma_giao_dich).first()
        if giao_dich is None:
            return {'status_code': 404, 'status': "Không tìm thấy giao dịch"}

        for attr, value in update_giaodich.model_dump().items():
            setattr(giao_dich, attr, value)
        db.commit()
        db.refresh(giao_dich)
        return {'status_code': 200, "status": "Cập nhật thành công"}
    except Exception as e:
        # raise Exception(e)
        return {'status_code': 404, 'status': 'Không tìm thấy giao dịch'}


# hàm lấy trạng thái của mã giao dịch
@app.get("/giao_dich/{ma_giao_dich}")
async def read_item(ma_giao_dich: str, db: Annotated[Session, Depends(get_db)]):
    giao_dich = db.query(model.GiaoDich).filter(model.GiaoDich.id == ma_giao_dich).first()
    if giao_dich is None:
        raise HTTPException(status_code=404, detail=f"{ma_giao_dich} khong ton tai")

    return {"ma_giao_dich": giao_dich}


# hàm tạo giao dịch mới

@app.post("/giaodich/", status_code=status.HTTP_201_CREATED)
async def create_giao_dich(giaodich: GiaoDichBase, db: Annotated[Session, Depends(get_db)]):
    try:
        new_giaodich = model.GiaoDich(**giaodich.dict())
        db.add(new_giaodich)
        db.commit()
        db.refresh(new_giaodich)
        return new_giaodich
    except SQLAlchemyError as e:
        error = str(e.orig)
        print(error)
        db.rollback()  # Quay lại trạng thái trước khi commit
        raise HTTPException(status_code=500, detail="Có lỗi trong câu lệnh MySQL")  # Xử lý lỗi

