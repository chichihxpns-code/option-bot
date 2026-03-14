import pandas as pd
import requests

def get_33000c_direct():
    print("正在直接連線 API，抓取 2026-03-13 的 33000C 資料...")
    
    url = "https://api.finmindtrade.com/api/v4/data"
    params = {
        "dataset": "TaiwanOptionDaily",
        "start_date": "2026-03-13",
        "end_date": "2026-03-13"
    }
    
    try:
        # 直接發送網路請求
        res = requests.get(url, params=params)
        data = res.json() # 將結果轉為 JSON 格式
        
        # 檢查 API 是不是回傳了錯誤訊息（例如請求太頻繁）
        if "data" not in data:
            print("❌ FinMind 拒絕了請求，伺服器回傳的真實原因如下：")
            print(data)
            return
            
        # 如果成功拿到資料，將其轉換為表格
        df = pd.DataFrame(data["data"])
        
        if df.empty:
            print("回傳成功，但資料表是空的！")
            return
            
        # 篩選出 33000 的 Call
        df_target = df[(df['strike_price'] == 33000) & (df['call_put'].str.upper() == 'CALL')]
        
        if df_target.empty:
            print("在當天所有合約中，找不到 33000C，請確認 FinMind 是否漏檔。")
        else:
            print("\n🎉 成功抓到了！33000C 的合約資訊如下：")
            # 只顯示重要的幾個欄位
            result = df_target[['option_id', 'strike_price', 'trading_volume', 'close']]
            result.columns = ['合約代碼', '履約價', '成交量', '收盤價']
            print(result.to_string(index=False))
            print("\n(只要拿到上面這個『合約代碼』，我們就能精準算出 5MA 了！)")
            
    except Exception as e:
        print(f"程式執行發生嚴重錯誤: {e}")

if __name__ == "__main__":
    get_33000c_direct()
