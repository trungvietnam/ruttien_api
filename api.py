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
    ngan_hang: str
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
   return momo_api.lay_doanh_thu_tu_api()


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
    phi_giao_dich = 0

    try:
        # import pdb
        # pdb.set_trace()

        giao_dich_moi = giaodich.dict()

        # kiểm tra sđt khách đã từng giao dịch chưa?
        sdt_khach =giaodich.dict()['sdt_momo_pay']
        check_sdt_khach = db.query(model.GiaoDich).filter(
            model.GiaoDich.sdt_momo_pay == sdt_khach).count()
        
        # Nếu khách giao dịch rồi, không free rút 100K nữa, sẽ tính phí 6%
        if check_sdt_khach != 0 :
            phi_giao_dich = 0
        else:
            phi_giao_dich = 6
        # tạo giao dịch trên Database
        new_giaodich = model.GiaoDich(**giaodich.dict())
        db.add(new_giaodich)
        db.commit()
        db.refresh(new_giaodich)

        # đề phòng trường hợp có xử cố bất ngờ, cho nên sẽ tạo DB trực tiếp cho từng giao dịch rồi update giao dịch đó
        ketqua_xuly = libs.kiem_tra_ma_giao_dich(giao_dich_moi,phi_giao_dich)

        


        if ketqua_xuly[1] is False:
            data_return = ketqua_xuly[2]
            update_data(ketqua_xuly[0],data_return,db)
            return_data  = {"status": "image_cheating", "detail":data_return}
        elif ketqua_xuly[1] is True:
            data_return = ketqua_xuly[3]
            so_tien = data_return['so_tien']
            update_data(ketqua_xuly[0],data_return,db)
            ma_giao_dich_momo= data_return['ma_giao_dich']
            return_data  = {"status": "qr_ok", "detail":data_return}
            # yêu cầu banking cho
            try:
                # send_server(id_web, data_query, "POST")
                param = f"function=rut_tien&stk_nguoi_nhan={giao_dich_moi['stk_ngan_hang']}&ngan_hang={giao_dich_moi['ngan_hang']}&so_tien={so_tien}"
                libs.socket_client(param)

                libs.write_file("ma_giao_dich_momo.txt",ma_giao_dich_momo)
            except:
                libs.send_telegram(f"\n SERVER CHUYỂN TIỀN KHÔNG HOẠT ĐỘNG\n Mã giao dịch đang tạm treo: {ketqua_xuly[0]}")

        
        return return_data
    
    except SQLAlchemyError as e:

        error = str(e.orig)
        print(error)
        db.rollback()  # Quay lại trạng thái trước khi commit
        raise HTTPException(
            status_code=500, detail="Có lỗi trong câu lệnh MySQL")  # Xử lý lỗi




# if __name__ == "__main__":
    # import uvicorn

    # uvicorn.run(app, host="0.0.0.0", port=1993, log_level="info")

#     # lay_doanh_thu_tu_api()