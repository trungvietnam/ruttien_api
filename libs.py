import momo_api
import config_ruttien
import urllib.request
from urllib.parse import urlsplit
import json
import requests
from datetime import date
import aiofiles
import asyncio
today = date.today()
import logging
FORMAT  = "%(asctime)-15s%(message)s"
logging.basicConfig(filemode = "w", filename=f'log_ruttien.log', format = FORMAT, level=logging.DEBUG)

def socket_client(param):


    # momo_api.lay_doanh_thu_tu_api()
    # print(libs.lay_doanh_thu_cua_hang_tu_file())
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            s.sendall(param.encode("utf-8"))
            data = s.recv(1024)
            import pdb
            pdb.set_trace()
            print(b"Received " + data)

    except Exception as e:
        print(e)
        send_telegram("server disconnect")

    
def client_received(s):
    encodedAckText = s.recv(1024)
    ackText = encodedAckText.decode('utf-8')

    # log if acknowledgment was successful
    print('error: server has sent back ' + ackText)

  
    return

def kiem_tra_ma_giao_dich(data,phi_giao_dich):
    id_web = data['id']
    bang_chung_img = data['bang_chung_img']
    ma_cuahang = data['ma_cuahang']
    sdt_momo_pay = data['sdt_momo_pay']

    ma_giao_dich_momo = BarcodeReader(download_img(bang_chung_img))
    check_ma_gd_cu = find_string_file ("ma_giao_dich_momo.txt",ma_giao_dich_momo)
    print(ma_giao_dich_momo,check_ma_gd_cu)
    # kiểm tra có phát hiện mã barcode không?
    if (ma_giao_dich_momo is None) or check_ma_gd_cu:

        logging.debug(str(id_web) + "mã giao dịch không hợp lệ")

        data_return = {
            "trang_thai": "cheat_image_duplicate",
            "so_tien": 0,
            "ma_giao_dich": ma_giao_dich_momo+ "_Duplicate",
            "phi_thu": 0
        }
        return [id_web, False, data_return]
    else:

        ketqua = check_MaGD_API(ma_cuahang, ma_giao_dich_momo)
        logging.debug(ketqua)

        if ketqua[0]:
            ten_kh = ketqua[1]
            sdt_kh = ketqua[2]
            so_tien = ketqua[3]
            sdt_kh_che = f"****{sdt_momo_pay[-4:]}"

            if (sdt_kh_che != sdt_kh):
                # Khách hàng gian lận, phí 10%
                phi_thu = 10
                logging.debug(f" {id_web} Khách nhập sai sđt khi so sánh với MoMo. Bị phạt 10%")
            elif phi_giao_dich == 0 and so_tien == 100000:
                phi_thu = 0
            elif (so_tien < 1000000):
                phi_thu = 6
            elif 1000000 < so_tien < 12000000:
                phi_thu = 5
            elif so_tien >= 12000000:
                phi_thu = 4
            
            data_query = {
                "trang_thai": "banking",
                "so_tien": so_tien,
                "ma_giao_dich": ma_giao_dich_momo,
                "phi_thu": phi_thu,
                "ten_kh":ten_kh,
                "sdt_kh":sdt_kh,
            }
            return [id_web, True, ketqua, data_query]
        else:
            send_telegram("Có mã giao dịch không tồn tại")


def send_server(id_web, payload, method):

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
        sdt_kh = check_kq['data']['customerPhoneNumber']
        return [True, ten_kh, sdt_kh, so_tien]
    except:
        logging.debug("Mã giao dịch có vấn đề")
    
    return [False, "Mã giao dịch không tồn tại"]


def BarcodeReader(image):
    import cv2
    from pyzbar.pyzbar import decode
    img = cv2.imread(image)

    # Decode the barcode image
    detectedBarcodes = decode(img)

    # If not detected then print the message
    if not detectedBarcodes:
        logging.debug(" Lỗi quét qrcode " + image)
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

    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    response = urllib.request.urlopen(req)
    filename = urlsplit(url)[2].split("/")[-1]

    luu_file = "giao_dich/" + filename

    import os
    if not os.path.exists("giao_dich"):
        os.makedirs("giao_dich")

    with open(luu_file, "wb") as f:
        f.write(response.read())
    return luu_file


def send_telegram(error):
    # print(error)
    send_get_data_web("https://eoz6ct38rxihtjw.m.pipedream.net",
                      {"noidung": error, "trang_thai": error})


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
        filtered_data = [item for item in data_list if 0 <
                         item['doanh_thu'] < 5000000]
    if filtered_data is None:
        filtered_data = [item for item in data_list if 5000000 <
                         item['doanh_thu'] < 8000000]

    random_shop = random.choice(filtered_data)

    return (random_shop)




def write_file(FILENAME,data):
    with open(FILENAME, "w+") as f:
        data = f"{data}\n"
        f.write(data)


def find_string_file(filename, find_string):
    with open(filename, 'r') as f:
        for index, line in enumerate(f):
            if find_string in line:
                return True		
            break

        return False

# xoá tiếng việt có dấu. vd: LÊ PHƯỚC TRUNG -> LE PHUOC TRUNG
def xoa_dau(txt: str) -> str:
    import unicodedata

    BANG_XOA_DAU = str.maketrans(
        "ÁÀẢÃẠĂẮẰẲẴẶÂẤẦẨẪẬĐÈÉẺẼẸÊẾỀỂỄỆÍÌỈĨỊÓÒỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÚÙỦŨỤƯỨỪỬỮỰÝỲỶỸỴáàảãạăắằẳẵặâấầẩẫậđèéẻẽẹêếềểễệíìỉĩịóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữựýỳỷỹỵ",
        "A"*17 + "D" + "E"*11 + "I"*5 + "O"*17 + "U"*11 + "Y"*5 + "a"*17 + "d" + "e"*11 + "i"*5 + "o"*17 + "u"*11 + "y"*5
    )
    if not unicodedata.is_normalized("NFC", txt):
        txt = unicodedata.normalize("NFC", txt)
    return txt.translate(BANG_XOA_DAU).upper()