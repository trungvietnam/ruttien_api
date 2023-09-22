def socket_server(param):
    HOST = "42.96.33.21"
    PORT = 21688
    import socket
    # momo_api.lay_doanh_thu_tu_api()
    # print(libs.lay_doanh_thu_cua_hang_tu_file())
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            s.sendall(param.encode())
            data = s.recv(1024).decode()

        print(f"Received {data!r}")
    except Exception as e:
        # pass
        print(f"Loix "+e)
        s.close()
        # send_telegram("server disconnect")




if __name__ == "__main__":
    import json
    import socket
    import libs
    # quan = "banh_xeo_qngai"
    # chuyen_tien_bank("vietcombank", "trungdc", 1000, 2222)
    # momo_api.lay_doanh_thu_tu_api()
    # quan_id = (quan_config)
    #
    #
    # import libs
    # import socket

    param = "function=rut_tien&stk_nguoi_nhan=trungdc&ngan_hang=vcb&so_tien=1100"

    
    
        libs.client_received(s)
    



    # so_tien = 9100 #5000
    # so_tien_max = 3900 
    # so_lan_CK = round(so_tien/so_tien_max) # 1000 là số tiền max để chuyển khoản
    # i =0
    # so_tien_da_chuyen = []
    
    # print(sum(so_tien_da_chuyen), " so lan chuyen khoan: ", so_lan_CK)
    # while True:
    #     if so_tien <= so_tien_max:
    #         so_tien_ck = so_tien
    #         break
    #     if sum(so_tien_da_chuyen) == 0 and so_tien >= so_tien_max:
    #         so_tien_ck = so_tien_max 
    #     elif so_tien_ck <= so_tien_max:
    #         so_tien_ck = so_tien - sum(so_tien_da_chuyen)
    #     if so_tien_ck > so_tien_max:
    #         so_tien_ck = so_tien_ck - so_tien_max
    #     so_tien_da_chuyen.append(so_tien_ck)

    #     print (i, so_tien_ck,sum(so_tien_da_chuyen) )
    #     if sum(so_tien_da_chuyen) == so_tien:
    #         break
    #     print("2222")
    # print("xong")