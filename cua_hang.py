#
# def tong_doanh_thu():
#    import datetime
#
#     now = datetime.datetime.now()
#     year = now.year
#
#     month = now.month
#     total_revenue = db.query(model.GiaoDich.ma_cuahang, func.sum(model.GiaoDich.so_tien)).filter(
#         func.extract('year', model.GiaoDich.ngay_gd) == year,
#         func.extract('month', model.GiaoDich.ngay_gd) == month,
#         # model.GiaoDich.trang_thai == "success"
#     ).group_by(model.GiaoDich.ma_cuahang).all()
#
#     # print(total_revenue)
#     doanh_thu_temp = []
#     for ma_cuahang, so_tien in total_revenue:
#         doanh_thu_temp.append({ma_cuahang: so_tien})
#     # return {"ma_giao_dich": total_revenue}

# # lưu thông tin tạm thời trong 1 ngày của cửa hàng
# def cache_info_cuahang(token):
#
# # hàm kiểm tra phí thu cho các SĐT.
# # Các điều kiện sẽ được cập nhật ở đây
# def fee_thu(sdt):
#     return sdt
#
#
#
# def kiem_tra_ma_giao_dich(bang_chung_img):
#
#
#     return None
#
