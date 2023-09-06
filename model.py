from sqlalchemy import Column, Integer,Float, String, DateTime
from pydantic import BaseModel
from database import Base


class GiaoDich(Base):
    __tablename__ = "giaodich"
    id = Column(Integer, primary_key=True, index=True)
    phi_thu = Column(Float)
    sdt_momo_pay =Column(String(length=10))
    so_tien = Column(Integer)
    ma_giao_dich = Column(String(length=255))
    ngay_gd =Column(DateTime)
    stk_ngan_hang =Column(String(length=255))
    ngan_hang =Column(String(length=50))

    ma_cuahang = Column(String(length=255))
    bang_chung_img = Column(String(length=255))
    trang_thai =Column(String(length=10))
    class Config:
        orm_mode = True
    # year = Column(Integer)
