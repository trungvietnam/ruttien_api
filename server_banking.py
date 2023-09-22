import datetime
import time
import re
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from datetime import datetime, timedelta
import socket
import logging
from io import BytesIO

from selenium.webdriver import Keys
from datetime import date

today = date.today()

logging.basicConfig(
    filename=f'G:/ruttien/logs/{today}_ruttien.log', encoding='utf-8', level=logging.DEBUG)


# import momo_api.momo_api as momo_api
# import config_ruttien

ma_giao_dich = None


def send_get_data_web(url, dt):
    import requests

    # sending get request and saving the response as response object
    r = requests.get(url, params=dt)

    # extracting data in json format
    #     data = r.json()
    return (r.text)


def wait_element(driver, element, seconds=50):
    try:
        element = WebDriverWait(driver, seconds).until(
            EC.presence_of_element_located((By.XPATH, element)))
        return element
    except:
        return None


# def thong_bao_toi_admin():


def setup():
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options

    option = webdriver.ChromeOptions()
    option.add_argument('user-data-dir=G:/tp_bank')

    driver = webdriver.Chrome(options=option)

    return driver


def xuly_data(data_request):
    # # function check data có đúng hay không
    # import pdb
    # pdb.set_trace()
    function_run = re.search('function=(.*?)&', data_request).group(1)
    if function_run == "check_server":
        return (" server OK")

    try:

        # sdt_vts_momo = re.search('sdt_vts_momo=(.*?)&', data_request).group(1)
        # quan = re.search('quan=(.*?)&', data_request).group(1)
        stk_ngan_hang = re.search(
            'stk_nguoi_nhan=(.*?)&', data_request).group(1)
        ten_NganHang = re.search('ngan_hang=(.*?)&', data_request).group(1)
        # ma_giao_dich_web = re.search('ma_giao_dich=(.*?)&', data_request).group(1)
        so_tien = re.search(r'so_tien=(\d+)', data_request).group(1)
        # giao_dich_moi = GiaoDich(ma_giao_dich_web, "", stk_ngan_hang, ten_NganHang, "")

        # quan_id = (quan_config)
        # driver_sv = setup(quan)
        #
        # if (not quan is None):
        #     logging.info( f"{quan_id[quan][0]}")
        #     login(driver_sv, quan_id[quan][0], quan_id[quan][1])

        if function_run == "app_check":
            # function check mã giao dịch ví trả sau từ app
            order_key = re.search('order_key=(.*?)&', data_request).group(1)
            # ketqua = check_giao_dich(driver_sv, ma_giao_dich)
            # sotien = ketqua[1]
            ketqua = check_MaGD_API(quan, ma_giao_dich)
            sotien = ketqua[1]
            chuyen_tien_momo(sdt_vts_momo, sotien, order_key)
            logging.info(
                f"sdt_vts_momo: {sdt_vts_momo} thanh toan so tien {sotien} voi order_key {order_key}")

        if function_run == "rut_tien":
            # rut tien tu website
            so_tien = int(so_tien) #5000
            so_tien_max = 3900 
            so_lan_CK = round(so_tien/so_tien_max) # 1000 là số tiền max để chuyển khoản
            so_tien_da_chuyen = []
            
            print(sum(so_tien_da_chuyen), " so lan chuyen khoan: ", so_lan_CK)
            while True:
                if so_tien <= so_tien_max:
                    so_tien_ck = so_tien
                    
                if sum(so_tien_da_chuyen) == 0 and so_tien >= so_tien_max:
                    so_tien_ck = so_tien_max 
                elif so_tien_ck <= so_tien_max:
                    so_tien_ck = so_tien - sum(so_tien_da_chuyen)
                if so_tien_ck > so_tien_max:
                    so_tien_ck = so_tien_ck - so_tien_max
                so_tien_da_chuyen.append(so_tien_ck)
                print (so_tien_ck,sum(so_tien_da_chuyen) )

                chuyen_tien_bank(ten_NganHang, stk_ngan_hang, so_tien_ck, "21688")
                if sum(so_tien_da_chuyen) == so_tien:
                    break
            
            return "{'status': 'Chuyển tiền thành công', 'detail':''}" 
            # try:
            #     so_tien = int(so_tien) #5000
            #     so_tien_max = 4000
            #     so_lan_CK = round(so_tien/so_tien_max) # 1000 là số tiền max để chuyển khoản
            #     i =0
            #     so_tien_ck = 0
            #     print("so lan chuyen khoan: ", so_tien_ck)
            #     while i < so_lan_CK:
            #         if so_tien_max >= so_tien:
            #             so_tien_ck = so_tien
            #         elif so_tien_ck != 0:
            #             so_tien_ck = so_tien -so_tien_ck


            #         chuyen_tien_bank(ten_NganHang, stk_ngan_hang, so_tien_ck, "21688")
            #         i = i+1
            #     return "{'status': 'Chuyển tiền thành công', 'detail':''}"
            # except:
            #     return "Loi giao dich"

    except Exception as e:
        print(f'Lỗi xử lý data {e}')
        send_telegram("có lỗi xữ lý. vui lòng check")


def setup_socket():
    s = socket.socket()
    host = ""
    port = 21688
    s.bind((host, port))
    s.listen(5)
    print('socket now listening')

    while True:
        c, addr = s.accept()
        print('kết nối mới....')

        data = c.recv(1024)

        data = data.decode("utf-8")
       

        if data:
            print(data)
            # dt = f"function=respon_check_gd&so_tien=20000&ma_giao_dich=1231312313&xacthuc_gd=True"
            try:
                dt = xuly_data(data)
                dt =  bytes(dt, 'utf-8')
                print(dt)

                s.sendall(dt)
            except:
                pass

        c.close()


def xuly_rutien(giao_dich_moi):
    ma_giao_dich_web = giao_dich_moi.ma_giao_dich
    so_tien = giao_dich_moi.so_tien
    # sdt_momo_nhan = re.search('sdt_momo_nhan=(.*?)&', data).group(1)
    # ma_giao_dich_momo = giao_dich_moi.ma_gd_momo
    # if ma_giao_dich_momo is None:
    #     logging.info(ma_giao_dich_web + " hinh anh khong hop le")
    #     dt = {
    #         'function': 'respon_check_gd',
    #         'xacthuc_gd': False,
    #         'ma_giao_dich_web': ma_giao_dich_web,
    #         'trang_thai': "qr_cheat"
    #     }
    #     send_get_data_web(api_link, dt)
    #     return

    # chen code so tien <100K
    if int(so_tien) < 100000:
        dt = {
            'function': 'respon_check_gd',
            'xacthuc_gd': False,
            'so_tien': so_tien,
            'trang_thai': "nho_hon_100k",
            'ma_giao_dich_web': ma_giao_dich_web,
            'ma_giao_dich_momo': ma_giao_dich,
        }
        (send_get_data_web(api_link, dt))
        return

    if so_tien:
        print("Momo nhan tien thanh cong")
        dt = {
            'function': 'respon_check_gd',
            'get_fee': 0,
            'so_tien': so_tien,
            'trang_thai': 'banking',
            'xacthuc_gd': True,
            'ma_giao_dich_momo': ma_giao_dich,
            'ma_giao_dich_web': ma_giao_dich_web,
        }

        fee = send_get_data_web(api_link, dt)
        if fee is None:
            fee = 0
        fee = float(fee)

        if fee > 0:
            so_tien = so_tien - (fee * 0.01 * so_tien)

        so_tien = int(so_tien)
        kq = chuyen_tien_bank(giao_dich_moi)

        if kq == "thanh_cong":
            dt = {
                'function': 'respon_check_gd',
                'trang_thai': "success",
                'xacthuc_gd': True,
                'phi_thu': fee,
                'so_tien': so_tien,
                'ma_giao_dich_momo': ma_giao_dich,
                'ma_giao_dich_web': ma_giao_dich_web
            }
            send_get_data_web(api_link, dt)
            dt = {
                "noidung": f"thanh cong!! Mã đơn: {ma_giao_dich_web}.",
                "trang_thai": "sucess"
            }
            send_get_data_web("https://eoz6ct38rxihtjw.m.pipedream.net", dt)
        if kq == "het_tien":
            send_get_data_web("https://eoz6ct38rxihtjw.m.pipedream.net",
                              {"noidung": "hết tiền rồi ba ơi, nạp vào thêm đi!!!!!", "trang_thai": "failed"})
            # data_res = {
    #     'function':'respon_check_gd',
    #     'so_tien':20000, 'xacthuc_gd':True,
    #     'ma_giao_dich':23423434,
    #     'sdt': "090506088"
    #     }
    # send_data_web(data_res)
    else:
        dt = {
            'function': 'respon_check_gd',
            'xacthuc_gd': False,
            'trang_thai': "failed_bank"
        }
        send_get_data_web(api_link, dt)


# def check_ma_gd_sdt(driver, sdt):
#     # try:
#     tg_hien_tai = datetime.now()
#
#     tg_hien_tai_2 = tg_hien_tai - timedelta(minutes=30)
#     ngay_hien_tai = tg_hien_tai.strftime('%d/%m/%Y')
#
#     # import pdb
#     # pdb.set_trace()
#     # tg_hien_tai_2 = tg_hien_tai_2.strftime("%H:%M:%S")
#
#     driver.get("https://business.momo.vn/sanpham/portal/transaction-history")
#     time.sleep(10)
#     find_element = wait_element(driver, '//div[text()="' + sdt + '"]').is_displayed()
#     if find_element is True:
#         ma_giao_dich = driver.find_element(By.XPATH, '//div[text()="' + sdt + '"]/../../..').get_attribute("data-id")
#         print(ma_giao_dich, "ma_giao_dich")
#         ngay_giao_dich = driver.find_element(By.XPATH, '//*[@data-id="' + ma_giao_dich + '"]/div/div/span[1]').text
#         gio_giao_dich = driver.find_element(By.XPATH, '//*[@data-id="' + ma_giao_dich + '"]/div/div').text
#         # xoá \n trong string gio_giao_dich
#         gio_giao_dich.replace('\\n', '')
#         gio_giao_dich = datetime.strptime(gio_giao_dich, '%d/%m/%Y %H:%M:%S')
#         so_tien = driver.find_element(By.XPATH, '//*[@data-id="' + ma_giao_dich + '"]/div[5]').text
#         stt_giao_dich = driver.find_element(By.XPATH, '//*[@data-id="' + ma_giao_dich + '"]/div[6]').text
#
#         if (ngay_hien_tai == ngay_giao_dich):
#             print("trung ngay")
#             if stt_giao_dich == "Thành công" and (tg_hien_tai > gio_giao_dich) & (tg_hien_tai_2 < gio_giao_dich):
#                 print("oki", tg_hien_tai, tg_hien_tai_2, gio_giao_dich)
#                 print("giao dich hop le")
#                 return [True, so_tien, ma_giao_dich]
#             else:
#                 print("giao dich khong hop le")
#         else:
#             return [False]
#     else:
#         return [False]

# except:
#     return [False]


# driver.quit()
def chuyen_tien_momo(nguoi_nhan, so_tien, ma_giao_dich):
    driver_ck = setup("trung")
    driver_ck.get("https://ruttien.thueapi.com/account/transfer")
    time.sleep(3)
    check_login_ = wait_element(driver_ck, '//*[text()="Đăng nhập"]', 10)

    if check_login_:
        driver_ck.find_element(
            By.XPATH, '//*[@name="email"]').send_keys("lpt.isocial@gmail.com")
        driver_ck.find_element(
            By.XPATH, '//*[@name="password"]').send_keys("Trung@30")
        time.sleep(2)
        driver_ck.find_element(By.XPATH, '//*[text()="Đăng nhập"]').click()
        time.sleep(2)

    driver_ck.get("https://ruttien.thueapi.com/account/transfer")

    time.sleep(2)
    driver_ck.find_element(By.XPATH, "//div[text()='0377382067']").click()
    # lấy số dư của ví Momo
    so_du_vi_momo = driver_ck.find_element(By.XPATH,
                                           '//*[@id="app"]/div/div[2]/div[2]/div/div[2]/div/div/div/span').text
    so_du_vi_momo = so_du_vi_momo.replace('.', '')
    if int(so_tien) > int(so_du_vi_momo):
        return ("het_tien")

    driver_ck.find_element(
        By.XPATH, '//input[@placeholder="Người nhận"]').send_keys(nguoi_nhan)
    time.sleep(1)
    driver_ck.find_element(
        By.XPATH, '//input[@placeholder="Số tiền muốn chuyển"]').clear()
    time.sleep(1)
    driver_ck.find_element(
        By.XPATH, '//input[@placeholder="Số tiền muốn chuyển"]').send_keys(so_tien)
    time.sleep(1)
    driver_ck.find_element(By.XPATH, '//input[@placeholder="Nội dung chuyển tiền"]').send_keys(
        "Trung DC thanh toan " + ma_giao_dich)
    time.sleep(1)
    driver_ck.find_element(
        By.XPATH, '//*[@id="app"]/div/div[2]/div[2]/div/div[7]/button').click()
    time.sleep(5)
    driver_ck.get('https://ruttien.thueapi.com/notification')
    time.sleep(2)
    thong_bao = wait_element(
        driver_ck, '//*[@class="w-10 bg-yellow-50"]/div/div/img/../../../../td[2]')
    if thong_bao is None:
        time.sleep(10)
    thong_bao = wait_element(
        driver_ck, '//*[@class="w-10 bg-yellow-50"]/div/div/img/../../../../td[2]')

    if thong_bao.text == "Tài khoản không đủ tiền":
        return ("het_tien")
    elif "Bạn vừa chuyển số tiền" in thong_bao.text:
        print("hop le")
        thong_bao.click()
        print("chuyen tien thanh cong")

        return ("thanh_cong")


def send_telegram(error):
    # print(error)
    send_get_data_web("https://eoz6ct38rxihtjw.m.pipedream.net",
                      {"noidung": error, "trang_thai": error})


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


# def check_giao_dich(driver, ma_giao_dich):  # giá trị trả về là True | số tiền or False|0
#     # check ma giao dich bang ma giao dich
#     try:
#         driver.get("https://business.momo.vn/sanpham/portal/report-center/transaction-report/PAYMENT-" + ma_giao_dich)
#         time.sleep(5)
#         ma_giao_dich_os = wait_element(driver,
#                                        "//*[@id='mainContent']/div/div/div[2]/div[1]/div/div/div[1]/div[1]/div[2]")
#         so_tien_gd = wait_element(driver,
#                                   "//*[@id='mainContent']/div/div/div[2]/div[1]/div/div/div[2]/div/div[2]/div[3]/div[2]").text
#
#         so_tien_gd = re.findall(r'\d+', so_tien_gd)
#         so_tien_gd = ("".join(so_tien_gd))
#         print("ma_giao_dich_os: ", ma_giao_dich_os.text, so_tien_gd)
#         if (ma_giao_dich_os.text == '—'):
#             print("Ma giao dich khong ton tai")
#             send_telegram(f" Mã giao dịch {ma_giao_dich} không tồn tại")
#
#             return [False, 0]
#         else:
#             return [True, so_tien_gd]
#     except:
#         send_telegram(" Lỗi Kiểm tra mã giao dịch")
#         return [False, 0]


# def check_log_gd_file():
def chuyen_tien_bank(ten_nganhang, stk_nganhang, so_tien, ma_giao_dich):
    ten_nganhang = ten_nganhang.upper()
    driver_ck = setup()
    driver_ck.get("https://ebank.tpb.vn/retail/vX/")
    time.sleep(2)
    try:
        login = driver_ck.find_element(
            By.XPATH, '//input[@placeholder="Tên đăng nhập"]')
        login.click()
        login.send_keys('0905060588')
    except:
        pass
    time.sleep(5)
    password = driver_ck.find_element(
        By.XPATH, '//input[@placeholder="Mật khẩu"]')
    password.click()
    password.send_keys('Trung@30')
    time.sleep(3)
    driver_ck.find_element(By.XPATH, '//*[text()="Đăng Nhập"]').click()
    time.sleep(5)
    # click chuyen khoan
    try:
        login_success = wait_element(
            driver_ck, '//*[@id="main-menu"]/app-menu/div[2]/div[2]/div/a[1]/div[2]', 30)
        driver_ck.find_element(
            By.XPATH, '//*[@id="instruction-5"]/app-home-list-card-link/div/div[1]/a').click()
        
            
        # click chuyen lien ngan hang
        driver_ck.find_element(By.XPATH,
                               '/html/body/app-root/main-component/div/div[2]/div/div/div[1]/div/app-transfer-home/app-list-card-link/div/div[2]/a/div[2]').click()
        time.sleep(3)
        driver_ck.find_element(
            By.XPATH, '//p[text()="Chọn ngân hàng"]').click()

        driver_ck.find_element(
            By.XPATH, '//input[@placeholder="Tìm kiếm"]').click()
        driver_ck.find_element(
            By.XPATH, '//input[@placeholder="Tìm kiếm"]').send_keys(ten_nganhang)
        ten_ngan_hang = driver_ck.find_element(
            By.XPATH, '//div[@class="selection-search-detail"]').text
        if ten_ngan_hang.find(ten_ngan_hang) == -1:
            return
        driver_ck.find_element(
            By.XPATH, '//div[@class="selection-search-detail"]').click()
        time.sleep(3)
        driver_ck.find_element(
            By.XPATH, '//input[@placeholder="Số tài khoản"]').send_keys(stk_nganhang)
    except:
        send_telegram(f"{stk_nganhang} - {ma_giao_dich} Thao tác bị lỗi")
    # thông báo sai tên người nhận
    try:
        check_stk = driver_ck.find_element(By.XPATH,
                                           '//p[text()="Bạn vui lòng thử lại hoặc tiếp tục Chuyển tiền thường."]')
        #         thong báo đến người nhận qua sđt
        send_telegram(
            f"{stk_nganhang} - {ma_giao_dich} bị sai thông tin. Liên hệ gấp")
        return {'status': 'error', 'content': 'Sai STK chuyển khoản'}
    except:
        pass
    time.sleep(3)
    nhap_tien = driver_ck.find_element(
        By.XPATH, '//input[@placeholder="Số tiền VND"]')
    nhap_tien.send_keys(so_tien)
    nhap_tien.send_keys(Keys.TAB)
    time.sleep(0.6)
    driver_ck.find_element(
        By.XPATH, '//app-interbank/div/div/div[4]/div[1]/textarea').clear()
    driver_ck.find_element(By.XPATH, '//app-interbank/div/div/div[4]/div[1]/textarea').send_keys(
        f"TrungD C thanh toan {ma_giao_dich}")
    time.sleep(1)
    driver_ck.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1)
    wait_element(driver_ck, '//*[text()=" Tiếp tục "]', 30).click()
    time.sleep(2)
    driver_ck.find_element(By.CLASS_NAME, 'app-switch').click()
    time.sleep(1)
    wait_element(driver_ck, '//*[text()="Xác Nhận Giao Dịch"]', 30).click()
    time.sleep(6)
    passcode = "160493"
    i = 1
    for p in passcode:
        driver_ck.find_element(By.XPATH,
                               f'//app-interbank/div[2]/app-otp/div/div/form/input-code/div/input[{i}]').send_keys(p)
        i = i + 1
        time.sleep(0.8)

    driver_ck.find_element(By.XPATH, '//*[text()="Xác thực"]').click()
    time.sleep(6)
    link_giao_dich = driver_ck.find_element(By.CLASS_NAME, "link").text
    f = open(f'nhat-ky-giao-dich.txt', 'a+')
    content = f" {link_giao_dich} - {ma_giao_dich} \n"
    f.write(content)
    f.close()

    from PIL import Image
    from io import BytesIO


    image = driver_ck.find_element(By.CLASS_NAME,'transfer-success').screenshot_as_png
    im = Image.open(BytesIO(image)) 

    im.save(f'/ruttien/{ma_giao_dich}.png')  # saves new cropped image

    return {'status': 'OK', 'content': {"ma_giao_dich": ma_giao_dich, 'link_giao_dich': link_giao_dich}}


def download_img(url):
    import urllib.request
    from urllib.parse import urlsplit

    # url = "https://example.com/file.txt"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    response = urllib.request.urlopen(req)
    filename = urlsplit(url)[2].split("/")[-1]

    luu_file = "D:/RUTTIEN/giao_dich/" + filename
    with open(luu_file, "wb") as f:
        f.write(response.read())
    return luu_file


if __name__ == "__main__":
    import json

    # quan = "banh_xeo_qngai"
    
    # momo_api.lay_doanh_thu_tu_api()
    # quan_id = (quan_config)
    #
    #
    setup_socket()
