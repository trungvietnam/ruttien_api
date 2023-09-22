from typing import Annotated
from datetime import datetime

from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError

from fastapi import Depends, FastAPI, HTTPException, status
import momo_api
import libs

import database
import model
from sqlalchemy.orm import Session

app = FastAPI()


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


# model.Base.metadata.create_all()


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
    trang_thai: str = "pending"


@app.get("/")
async def read_root(db: Session = Depends(get_db)):
    # crud.get_items()
    return {"Hello": "world"}


@app.get("/tonghop_doanhthu")
async def update_doanhthu_cuahang():
    #     chỉ chạy 1 lần trong ngày
    momo_api.lay_doanh_thu_tu_api()


@app.get("/get_qrcode")
async def get_qrcode(db: Annotated[Session, Depends(get_db)]):
    from sqlalchemy import func, select, not_, exists, text

    query = """
select FLOOR(390 + RAND() * 9999999) AS ma_gd FROM `giaodich` WHERE giaodich.id  IN (SELECT id FROM giaodich WHERE id IS NOT NULL) LIMIT 1;
        """

    result = db.execute(text(query)).fetchone()
    if result:
        ma_gd = int(result[0])
    else:
        ma_gd = 6868

    info_qrcode = libs.lay_doanh_thu_cua_hang_tu_file()
    temp_dt = {'cua_hang': info_qrcode['cua_hang'],
               'qr_code_img': info_qrcode['qr_code_img'], 'ma_giao_dich': ma_gd}
    print("Mã giao dịch mới:", ma_gd)
    # cua_hang.tong_doanh_thu()
    return temp_dt


# # hàm check giao dịch bằng SĐT
# @app.get("/giao_dich/{sdt_khach}")
# async def read_item(sdt_khach: str, db: Annotated[Session, Depends(get_db)]):
#     giao_dich = db.query(model.GiaoDich).filter(
#         model.GiaoDich.sdt_momo_pay == sdt_khach).first()
#     if giao_dich is None:
#         raise HTTPException(
#             status_code=404, detail=f"{sdt_khach} chưa giao dịch lần nào")

    return giao_dich

# hàm lấy trạng thái của mã giao dịch
@app.get("/giao_dich/{ma_giao_dich}")
async def read_item(ma_giao_dich: str, db: Annotated[Session, Depends(get_db)]):
    giao_dich = db.query(model.GiaoDich).filter(
        model.GiaoDich.id == ma_giao_dich).first()
    if giao_dich is None:
        raise HTTPException(
            status_code=404, detail=f"{ma_giao_dich} khong ton tai")

    return giao_dich


def update_data(ma_giao_dich: int, data_update, db: Session):


    try:
        giao_dich = db.query(model.GiaoDich).filter(
            model.GiaoDich.id == ma_giao_dich).first()
        if giao_dich is None:
            return {'status_code': 404, 'status': "Không tìm thấy giao dịch"}

        for attr, value in data_update.items():
            setattr(giao_dich, attr, value)

        db.commit()
        db.refresh(giao_dich)
        return {'status_code': 200, "status": "Cập nhật thành công"}
    except SQLAlchemyError as e:
        error = str(e.orig)
        print(error)
        return {'status_code': 500, 'status': 'Mã giao dịch không tồn tại'}
    
# hàm tạo giao dịch mới
@app.post("/giaodich/", status_code=status.HTTP_201_CREATED)
async def create_giao_dich(giaodich: GiaoDichBase, db: Annotated[Session, Depends(get_db)]):
    try:
        # tạo giao dịch trên Database

        new_giaodich = model.GiaoDich(**giaodich.dict())
        db.add(new_giaodich)
        db.commit()
        db.refresh(new_giaodich)

        ketqua_xuly = libs.kiem_tra_ma_giao_dich(giaodich.dict())
        data_update = ketqua_xuly[2]
        if ketqua_xuly[1] is False:
            update_data(ketqua_xuly[0],data_update,db)
            
        return new_giaodich
    
    except SQLAlchemyError as e:

        error = str(e.orig)
        print(error)
        db.rollback()  # Quay lại trạng thái trước khi commit
        raise HTTPException(
            status_code=500, detail="Có lỗi trong câu lệnh MySQL")  # Xử lý lỗi




if __name__ == "__main__":
    # lay_doanh_thu_tu_api()

    momo_api.lay_doanh_thu_tu_api()
    print(libs.lay_doanh_thu_cua_hang_tu_file())
