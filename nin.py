import socket
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

ma_giao_dich = None
quan_config = {
    "2": ["anvatmrx", "Anhoianhoi13579"],
    "1": ["0905060588", "12345678"]

}
url_web = "https://ruttien.net/data/"

def send_get_data_web(url, dt):
    import requests

    # sending get request and saving the response as response object
    r = requests.get(url, params=dt)

    # extracting data in json format
    #     data = r.json()

    print(r.text)


def wait_element(driver, element):
    try:
        element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, element)))
        return element
    except:
        print("khong tim thay")


# def thong_bao_toi_admin():


def setup(quan):
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    userdatadir = "C:/profile_momo/" + quan
    options = Options()
    # options.headless = True
    options.add_argument(f"--user-data-dir={userdatadir}")
    options.add_argument("--window-size=1920,1200")
    ma_giao_dich_kh = ""
    driver = webdriver.Chrome(options=options)
    return driver


def login(driver, username, password):
    try:

        driver.get("https://business.momo.vn/sanpham/")
        time.sleep(5)
        driver.find_element(By.XPATH, "//input[@name='username']").send_keys(username)
        driver.find_element(By.XPATH, "//input[@name='password']").send_keys(password)
        time.sleep(5)
        driver.find_element(By.XPATH, "//*[@id='root']/div/section/main/div/div/div/div[1]/div/form/button").click()
        time.sleep(5)
    except:
        return driver

    # print(driver.page_source)
    # driver.quit()


def setup_socket():
    s = socket.socket()
    host = ""
    port = 22688
    s.bind((host, port))
    s.listen(5)
    while True:
        c, addr = s.accept()
        data = c.recv(1024)
        data = data.decode("utf-8")

        # driver_sv = setup("trung")
        # login(driver_sv)

        if data:
            print(data)
            # dt = f"function=respon_check_gd&so_tien=20000&ma_giao_dich=1231312313&xacthuc_gd=True"
            print(data)
            xuly_dulieu(data)

            # url = "http://localhost/momo/admin_/api.php"
            # send_get_data_web(url, data)
        c.close()




# Make one method to decode the barcode
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
        print("Barcode Not Detected or your barcode is blank/corrupted!")
    else:

        # Traverse through all the detected barcodes in image
        for barcode in detectedBarcodes:

            # Locate the barcode position in image
            (x, y, w, h) = barcode.rect

            # Put the rectangle in image using
            # cv2 to highlight the barcode
            cv2.rectangle(img, (x-10, y-10),
                        (x + w+10, y + h+10),
                        (255, 0, 0), 2)

            if barcode.data!="":

            # Print the barcode data
                print(barcode.data)



def xuly_dulieu(data):
    from furl import furl
    import urllib.request
    from urllib.parse import urlsplit
    f = furl(data)
    quan = (f.args['quan'])
    momo_vts = (f.args['sdt_momo'])
    sdt_momo_nhan =  (f.args['sdt_momo_nhan'])
    # so_tien_res = (f.args['sotien'])
    sdt_che = momo_vts[:4] + "***" + momo_vts[7:]
    quan_id = quan_config
    print(quan, momo_vts)
    banking_info = (f.args['banking'])
    url = f.args['anh_giao_dich']
    import urllib.request
    from urllib.parse import urlsplit

# url = "https://example.com/file.txt"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    response = urllib.request.urlopen(req)
    filename = urlsplit(url)[2].split("/")[-1]
    with open("data/"+filename, "wb") as f:
    # f.write(response.read())
    link_img = r"C:\trung\giao_dich\\" + filename
    ma_giao_dich = BarcodeReader(link_img)
    print(ma_giao_dich)

def check_ma_gd_sdt(driver, sdt):
    # try:
    from datetime import datetime, timedelta
    tg_hien_tai = datetime.now()

    tg_hien_tai_2 = tg_hien_tai - timedelta(minutes=30)
    ngay_hien_tai = tg_hien_tai.strftime('%d/%m/%Y')

    # import pdb
    # pdb.set_trace()
    # tg_hien_tai_2 = tg_hien_tai_2.strftime("%H:%M:%S")

    driver.get("https://business.momo.vn/sanpham/portal/transaction-history")
    time.sleep(10)
    find_element = wait_element(driver, '//div[text()="' + sdt + '"]').is_displayed()
    if find_element is True:
        ma_giao_dich = driver.find_element(By.XPATH, '//div[text()="' + sdt + '"]/../../..').get_attribute("data-id")
        print(ma_giao_dich, "ma_giao_dich")
        ngay_giao_dich = driver.find_element(By.XPATH, '//*[@data-id="' + ma_giao_dich + '"]/div/div/span[1]').text
        gio_giao_dich = driver.find_element(By.XPATH, '//*[@data-id="' + ma_giao_dich + '"]/div/div').text
        # xoá \n trong string gio_giao_dich
        gio_giao_dich.replace('\\n', '')
        gio_giao_dich = datetime.strptime(gio_giao_dich, '%d/%m/%Y %H:%M:%S')
        so_tien = driver.find_element(By.XPATH, '//*[@data-id="' + ma_giao_dich + '"]/div[5]').text
        stt_giao_dich = driver.find_element(By.XPATH, '//*[@data-id="' + ma_giao_dich + '"]/div[6]').text

        if (ngay_hien_tai == ngay_giao_dich):
            print("trung ngay")
            if stt_giao_dich == "Thành công" and (tg_hien_tai > gio_giao_dich) & (tg_hien_tai_2 < gio_giao_dich):
                print("oki", tg_hien_tai, tg_hien_tai_2, gio_giao_dich)
                print("giao dich hop le")
                return [True, so_tien, ma_giao_dich]
            else:
                print("giao dich khong hop le")
        else:
            return [False]
    else:
        return [False]

    # except:
    #     return [False]


# driver.quit()
def chuyen_tien(nguoi_nhan, so_tien):
    driver_ck = setup("trung")
    driver_ck.get("https://ruttien.thueapi.com/account/transfer")
    try:
        driver_ck.find_element(By.XPATH, '//*[@name="email"]').send_keys("lpt.isocial@gmail.com")
        driver_ck.find_element(By.XPATH, '//*[@name="password"]').send_keys("Trung@30")
        time.sleep(2)
        driver_ck.find_element(By.XPATH, '//*[text()="Đăng nhập"]').click()
        time.sleep(2)
        driver_ck.get("https://ruttien.thueapi.com/account/transfer")
        time.sleep(2)
        driver_ck.find_element(By.XPATH, "//div[text()='0905060588']").click()
        driver_ck.find_element(By.XPATH, '//input[@placeholder="Người nhận"]').send_keys(nguoi_nhan)
        time.sleep(1)
        driver_ck.find_element(By.XPATH, '//input[@placeholder="Số tiền muốn chuyển"]').send_keys(so_tien)
        time.sleep(1)
        driver_ck.find_element(By.XPATH, '//input[@placeholder="Nội dung chuyển tiền"]').send_keys(
            "ruttien.net thanh toan")
        time.sleep(1)
        driver_ck.find_element(By.XPATH, '//*[@id="app"]/div/div[2]/div[2]/div/div[7]/button').click()



    except:
        import pdb
        pdb.set_trace()


def send_maiL():
    pass


if __name__ == "__main__":

    try:
        print("bat dau chay")
        setup_socket()

    except Exception as e:
        print(e)
        send_maiL()

    # data_res = {
    #     'function':'respon_check_gd',
    #     'so_tien':20000, 'xacthuc_gd':True,
    #     'ma_giao_dich':23423434,
    #     'sdt': "090506088"
    #     }
    # send_data_web(data_res)
    # driver_sv = setup("trung")
    # xu_ly(driver_sv)
    #

    #
    # sdt = (f.args['sdt'])
    # # quan =""
    # # ma_giao_dich= ""
    # # ketqua = check_giao_dich(quan,ma_giao_dich)
    #
    # q = (quan_config)
    #
    # driver_sv = setup(quan)
    # login(driver_sv, q[quan][0], q[quan][1])
    # try:
    #     check_login_ = driver_sv.find_element(By.XPATH, "//h2[contains(text(),'Đăng nhập')]").is_displayed()
    #     if check_login_:
    #         #     nếu chưa đăng nhập thì đăng nhập
    #         driver_sv.find_element(By.XPATH, "//input[@name='username']").send_keys(q[quan][0])
    #         driver_sv.find_element(By.XPATH, "//input[@name='password']").send_keys(q[quan][1])
    #         time.sleep(5)
    #         driver_sv.find_element(By.XPATH,
    #                                "//*[@id='root']/div/section/main/div/div/div/div[1]/div/form/button").click()
    #         time.sleep(5)
    # except:
    #     pass
    #
    # sdt = '0982***592'
    # if (check_ma_gd_sdt(driver_sv, sdt)):
    #         print(ma_giao_dich)
    #         chuyen_tien("","")
    # # check_giao_dich(driver_sv,"35054601596")
    # # sotien = driver_sv.find_element(By.XPATH,'//*[@id="mainContent"]/div[1]/div/div[2]/div[1]/div/div/div[2]/div/div[2]/div[2]/p[2]')
    # # driver_sv.quit()
    # # chuyen_tien()
    #
    # # print(q[quan][0])
    #
    # # xong
    # # chuyen_tien("0764978225",1000)
