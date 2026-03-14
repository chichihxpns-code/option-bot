import pandas as pd
from FinMind.data import DataLoader

def get_33000c_vip():
    dl = DataLoader()
    
    # 1. 拿出你的 VIP 通行證
    my_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJkYXRlIjoiMjAyNi0wMS0zMCAwODoxNToxMSIsInVzZXJfaWQiOiJkZW5uaXNsaW45OTk5IiwiZW1haWwiOiJkZW5uaXNsaW45OTk5QGdtYWlsLmNvbSIsImlwIjoiNjAuMjQ4LjE4LjIxMCJ9.XlLccdGIeJRr2hM23_B3yolW2I-hszdGEwcBffYxMA8" 
    dl.login_by_token(api_token=my_token)
    
    target_date = "2026-03-13"
    print(f"🔑 Token 登入成功！正在搜尋 {target_date} 的 33000C...")

    # 2. 抓取當天所有選擇權，自動找出 33000C 代碼
    df_all = dl.taiwan_option_daily(
        start_date=target_date,
        end_date=target_date
    )
    
    if df_all.empty:
        print("❌ 找不到資料，請確認 Token 是否填寫正確。")
        return
        
    target = df_all[(df_all['strike_price'] == 33000) & (df_all['call_put'].str.upper() == 'CALL')]
    
    if target.empty:
        print("❌ 當天沒有 33000C 的資料。")
        return
        
    option_id = target.iloc[0]['option_id']
    print(f"✅ 找到熱門合約代碼：{option_id}，正在調閱 13:45 的分 K 資料...")

    # 3. 抓取分 K 資料來算 5MA
    df_kline = dl.taiwan_option_daily_kline(
        option_id=option_id,
        start_date=target_date,
        end_date=target_date
    )

    if df_kline.empty:
        print("無法抓取分K資料，可能該合約當天無成交。")
        return

    # 4. 計算 5MA
    df_kline = df_kline.sort_values('time')
    df_kline['5MA'] = df_kline['Close'].rolling(window=5).mean()
    
    # 5. 輸出結果
    result = df_kline[df_kline['time'] == '13:45:00']
    
    if not result.empty:
        print(f"\n🎯 恭喜！破關成功！")
        print(f"合約：{option_id}")
        print(f"13:45 的 5MA 價格為：{result.iloc[0]['5MA']}")
    else:
        print(f"13:45 無成交，最後一筆 5MA 為：{df_kline.iloc[-1]['5MA']}")

if __name__ == "__main__":
    get_33000c_vip()
