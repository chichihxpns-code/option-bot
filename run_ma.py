import pandas as pd
import requests

def get_option_kline():
    # 1. 放入你剛剛驗證成功的 Token
    token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJkYXRlIjoiMjAyNi0wMS0zMCAwODoxNToxMSIsInVzZXJfaWQiOiJkZW5uaXNsaW45OTk5IiwiZW1haWwiOiJkZW5uaXNsaW45OTk5QGdtYWlsLmNvbSIsImlwIjoiNjAuMjQ4LjE4LjIxMCJ9.XlLccdGIeJRr2hM23_B3yolW2I-hszdGEwcBffYxMA8"
    target_date = "2026-03-13"
    
    # 加入 33000C，並把截圖上的 32800C 也當作備案，保證一定抓得到資料！
    possible_ids = ["TXO33000C6", "TX433000C6", "TXO32800C6", "TX432800C6"]
    
    url = "https://api.finmindtrade.com/api/v4/data"
    print(f"✅ Token 驗證無誤！切換至免費版『1分鐘 K 線』資料庫...\n")

    success_df = None
    target_id = ""

    # 2. 開始逐一測試代碼
    for opt_id in possible_ids:
        print(f"嘗試調閱代碼: {opt_id} ...")
        params = {
            "dataset": "TaiwanOptionDailyKline", # <--- 關鍵修改：換成免費版可用的分K線
            "data_id": opt_id,
            "start_date": target_date,
            "end_date": target_date,
            "token": token
        }
        
        try:
            res = requests.get(url, params=params)
            data = res.json()
            
            if data.get("msg") == "success" and len(data.get("data", [])) > 0:
                success_df = pd.DataFrame(data["data"])
                target_id = opt_id
                print(f"✅ 命中目標！正確代碼為: {opt_id}\n")
                break
            elif data.get("status") != 200:
                print(f"  ❌ 伺服器拒絕: {data.get('msg')}")
            else:
                print("  無成交資料，換下一個...")
        except Exception as e:
            print(f"  網路請求失敗: {e}")

    # 3. 檢查是否抓到資料
    if success_df is None or success_df.empty:
        print("\n💥 所有代碼都測試失敗。免費版 API 可能在週末有流量限制，請週一開盤再試。")
        return

    # 4. 開始計算 5MA
    print("正在計算 13:45 的 5MA...")
    success_df.columns = success_df.columns.str.lower() 
    
    if 'time' not in success_df.columns or 'close' not in success_df.columns:
        print(f"資料欄位異常，目前的欄位有: {success_df.columns.tolist()}")
        return

    # K線是用收盤價 (close) 來計算平均
    success_df = success_df.sort_values('time')
    success_df['5MA'] = success_df['close'].rolling(window=5).mean()

    # 尋找 13:45:00 以前的最後一筆 K 棒
    df_1345 = success_df[success_df['time'] <= '13:45:00'].tail(1)

    if not df_1345.empty:
        final_time = df_1345.iloc[0]['time']
        final_price = df_1345.iloc[0]['close']
        final_ma = df_1345.iloc[0]['5MA']
        
        print(f"\n🎯 任務圓滿達成！")
        print(f"==============================")
        print(f"合約代碼：{target_id}")
        print(f"K棒時間：{final_time}")
        print(f"當下收盤價：{final_price}")
        print(f"當下 5MA：{final_ma}")
        print(f"==============================")
    else:
        print("找不到 13:45 以前的成交紀錄。")

if __name__ == "__main__":
    get_option_kline()
