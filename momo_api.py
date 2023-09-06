import requests
import json

import config_ruttien


def check_maGD(maGD, token):
    url = f"https://business.momo.vn/api/transaction/v2/transactions/PAYMENT-{maGD}?language=vi"
    payload = {}
    headers = {
        'Authorization': f'Bearer {token}'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    data = json.loads(response.text)
    return data


def get_token(username, password):
    url = "https://business.momo.vn/api/authentication/login?language=vi"
    payload = json.dumps({
        "username": username,
        "password": password
    })
    headers = {
        'Accept': 'application/json',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'vi-VN,vi;q=0.9,zh;q=0.8,en-US;q=0.7,en;q=0.6,cy;q=0.5',
        'Connection': 'keep-alive',
        'Content-Length': '47',
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)

    data = json.loads(response.text)
    # print(data)
    return data['data']['token']


def tong_doanh_thu(token, merchantId):
    from datetime import datetime
    thang = datetime.now().month
    try:
        toDate = datetime(2023, thang, 31, 23, 59, 00, 0)
    except ValueError:
        toDate = datetime(2023, thang, 30, 23, 59, 00, 0)

    fromDate = datetime(2023, thang, 1, 00, 00, 00, 0)
    fromDate = fromDate.isoformat()
    toDate = toDate.isoformat()
    url = "https://business.momo.vn/api/transaction/v2/transactions/statistics?merchantId=" + merchantId + "" \
                                                                                                           f"&fromDate={fromDate}&toDate={toDate}&status=ALL&paymentMethod=ALL&language=vi"
    # url ="https://business.momo.vn/api/transaction/v2/transactions/statistics?fromDate=2023-08-01T00%3A00%3A00.00&toDate=2023-08-19T23%3A59%3A59.00&status=ALL&paymentMethod=ALL&merchantId=1129949&language=vi"
    payload = {}
    headers = {
        'MerchantId': merchantId,
        'Authorization': 'Bearer ' + token
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    doanh_thu = json.loads(response.text)
    # import pdb
    # pdb.set_trace()
    # doanh_thu['data']
    return doanh_thu['data']


def check_giao_dich(token, ma_giao_dich):
    url = f"https://business.momo.vn/api/transaction/v2/transactions/PAYMENT-{ma_giao_dich}?language=vi"
    payload = {}
    headers = {
        'Authorization': 'Bearer ' + token
    }
    response = requests.request("GET", url, headers=headers, data=payload)

    return response.text


# hàm này chạy theo ngày, lấy doanh thu từ MoMo
def lay_doanh_thu_tu_api():
    doanh_thu_cuahang = []
    quan_id = config_ruttien.quan_config
    for quan in quan_id:
        # check_MaGD_API("tap_hoa_phuong_pham", "44100614455")
        username = quan_id[quan][0]
        passwd = quan_id[quan][1]
        merchan_id = quan_id[quan][2]
        token = get_token(username, passwd)
        doanh_thu = tong_doanh_thu(token, merchan_id)
        doanh_thu = doanh_thu['totalSuccessAmount']
        doanh_thu_cuahang.append({'cua_hang': quan_id[quan][0], 'doanh_thu': doanh_thu})
    # ketqua = momo_api.momo_api.get_token()
    print(doanh_thu_cuahang)
    with open('doanh_thu_cuahang.txt', 'w') as file:
        file.write(str(doanh_thu_cuahang))
