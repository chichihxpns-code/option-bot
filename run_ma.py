import pandas as pd
import requests

def get_33000c_ultimate():
    # 1. 放入你的 Token
    token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJkYXRlIjoiMjAyNi0wMS0zMCAwODoxNToxMSIsInVzZXJfaWQiOiJkZW5uaXNsaW45OTk5IiwiZW1haWwiOiJkZW5uaXNsaW45OTk5QGdtYWlsLmNvbSIsImlwIjoiNjAuMjQ4LjE4LjIxMCJ9.XlLccdGIeJRr2hM23_B3yolW2I-hszdGEwcBffYxMA8"
    target_date = "2026-03-13"
    
    # 3月13日是第二週週五，接下來要結算的是「第三週(月選) TXO」或「第四週 TX4」
    # 我們讓程式自動去撞門，哪個有資料就抓哪個！
    possible_ids = ["TXO33000C6", "TX433000C6", "TX233000C6", "TX133000C6"]
    
    url = "https://api.finmindtrade.com/api/v4/data"
    print(f"🚀 啟動直連模式！帶著 Token 尋找 {target_date} 的 33000C...\n")

    success_df = None
    target_id = ""

    # 2. 開始逐一測試代碼
    for opt_id in possible_ids:
        print(f"嘗試調閱代碼: {opt_id} ...")
        params = {
            "dataset": "TaiwanOptionTick", # 直接抓最詳細的逐筆成交
            "data_id": opt_id,
            "start_date": target_date,
            "end_date": target_date,
            "token": token
        }
        
        try:
            res = requests.get(url, params=params)
            data = res.json()
            
            # 如果成功且有資料
            if data.get("msg") == "success" and len(data.get("data", [])) > 0:
                success_df = pd.DataFrame(data["data"])
                target_id = opt_id
                print(f"✅ 命中目標！正確代碼為: {opt_id}\n")
                break
            elif data.get("status") != 200:
                print(f"  ❌ 伺服器拒絕: {data.get('msg')}")
            else:
                print("  無成交資料。")
        except Exception as e:
            print(f"  網路請求失敗: {e}")

    # 3. 檢查是否抓到資料
    if success_df is None or success_df.empty:
        print("\n💥 所有代碼都測試失敗。請確認 Token 是否正確，或當日該履約價無人交易。")
        return

    # 4. 開始計算 5MA
    print("正在計算 13:45 的 5MA...")
    # 統一將欄位名稱轉小寫，避免大小寫出錯
    success_df.columns = success_df.columns.str.lower() 
    
    if 'time' not in success_df.columns or 'price' not in success_df.columns:
        print("資料欄位異常，無法計算。")
        return

    # 排序並計算 5 筆移動平均
    success_df = success_df.sort_values('time')
    success_df['5MA'] = success_df['price'].rolling(window=5).mean()

    # 尋找 13:45:00 以前的最後一筆成交
    df_1345 = success_df[success_df['time'] <= '13:45:00'].tail(1)

    if not df_1345.empty:
        final_time = df_1345.iloc[0]['time']
        final_price = df_1345.iloc[0]['price']
        final_ma = df_1345.iloc[0]['5MA']
        
        print(f"\n🎯 任務圓滿達成！")
        print(f"==============================")
        print(f"合約代碼：{target_id}")
        print(f"結算時間：{final_time}")
        print(f"當下成交價：{final_price}")
        print(f"當下 5MA：{final_ma}")
        print(f"==============================")
    else:
        print("找不到 13:45 以前的成交紀錄。")

if __name__ == "__main__":
    get_33000c_ultimate()
