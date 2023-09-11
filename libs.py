import logging
import momo_api,config_ruttien
import urllib.request
from urllib.parse import urlsplit
import json,requests
from datetime import date

today = date.today()
logging.basicConfig(filename=f'{today}_ruttien.log', encoding='utf-8', level=logging.DEBUG)

def kiem_tra_ma_giao_dich(data):
    id_web = data['id']
    bang_chung_img = data['bang_chung_img']
    ma_cuahang = data['ma_cuahang']

    ma_giao_dich_momo = BarcodeReader(download_img(bang_chung_img))
    # kiểm tra có phát hiện mã barcode không?
    if (ma_giao_dich_momo is None):
        payload = json.dumps({
        "trang_thai": "cheating_image",   
        })
        # send_request(id_web,payload, "PUT")
        logging.error(str(id_web) + "mã giao dịch khong hop le")
        ma_giao_dich_momo = so_tien = 0
        data_query = {
            "trang_thai": "cheat_image",
            "so_tien": so_tien,
            "ma_giao_dich": ma_giao_dich_momo,
            "phi_thu": 0
        }
        return [id_web,False,data_query]
    else:

        ketqua = check_MaGD_API(ma_cuahang,ma_giao_dich_momo)
        logging.log(ketqua)

        if ketqua[0]:
            ten_kh  = ketqua[1]
            so_tien = ketqua[2]
            if (so_tien < 10000000):
                phi_thu = 6
            else:
                phi_thu = 5 

            data_query = {
                "trang_thai": "banking",
                "so_tien": so_tien,
                "ma_giao_dich": ma_giao_dich_momo,
                "phi_thu": phi_thu
            }
            send_request
            return [id_web,True,data_query]
        else:
            send_telegram("Có mã giao dịch không tồn tại")

def send_request(id_web,payload, method):

    headers = {
        'Accept': 'application/json',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'vi-VN,vi;q=0.9,zh;q=0.8,en-US;q=0.7,en;q=0.6,cy;q=0.5',
        'Content-Type': 'application/json'
    }
    url = f'{config_ruttien.server_link}/giao_dich/{id_web}'
    response = requests.request(method, url, headers=headers, data=payload)


def check_MaGD_API(quan, ma_giao_dich):
    quan_id = config_ruttien.quan_config
    username = quan_id[quan][0]
    passwd = quan_id[quan][1]

    token = momo_api.get_token(username, passwd)
    try:
        check_kq = momo_api.check_maGD(ma_giao_dich, token)
        ten_kh = check_kq['data']['customerName']
        so_tien = check_kq['data']['totalAmount']
        return [True, ten_kh, so_tien]
    except:
        logging.error("Mã giao dịch có vấn đề")
        return [False, "Mã giao dịch không tồn tại"]
    



def BarcodeReader(image):
    import cv2
    # from PIL import Image

    from pyzbar.pyzbar import decode
    # read the image in numpy array using cv2
    img = cv2.imread(image)

    # Decode the barcode image
    detectedBarcodes = decode(img)

    # If not detected then print the message
    if not detectedBarcodes:
        logging.error(" Lỗi quét qrcode " + image)
        return None
    else:

        # Traverse through all the detected barcodes in image
        for barcode in detectedBarcodes:

            # Locate the barcode position in image
            (x, y, w, h) = barcode.rect

            # Put the rectangle in image using
            # cv2 to highlight the barcode
            cv2.rectangle(img, (x - 10, y - 10),
                          (x + w + 10, y + h + 10),
                          (255, 0, 0), 2)

            if barcode.data != "":
                # Print the barcode data
                return (barcode.data.decode("utf-8"))


def download_img(url):

    # url = "https://example.com/file.txt"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    response = urllib.request.urlopen(req)
    filename = urlsplit(url)[2].split("/")[-1]

    luu_file = "giao_dich/" + filename
    with open(luu_file, "wb") as f:
        f.write(response.read())
    return luu_file


def send_telegram(error):
    # print(error)
    send_get_data_web("https://eoz6ct38rxihtjw.m.pipedream.net", {"noidung": error, "trang_thai": error})


def send_get_data_web(url, dt):
    import requests

    # sending get request and saving the response as response object
    r = requests.get(url, params=dt)

    # extracting data in json format
    #     data = r.json()
    return (r.text)


def lay_doanh_thu_cua_hang_tu_file():
    import ast
    import random

    file_path = "doanh_thu_cuahang.txt"
    with open(file_path, 'r') as file:
        content = file.read()
    data_list = ast.literal_eval(content)

    filtered_data = [item for item in data_list if item['doanh_thu'] == 0]
    if filtered_data is None:
            filtered_data = [item for item in data_list if 0 < item['doanh_thu'] < 5000000]
    if filtered_data is None:
        filtered_data = [item for item in data_list if 5000000 < item['doanh_thu'] < 8000000]        
    
    random_shop = random.choice(filtered_data)


    return (random_shop)