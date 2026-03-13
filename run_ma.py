import pandas as pd
from FinMind.data import DataLoader
import datetime

def get_33000c_5ma():
    dl = DataLoader()
    
    # 強制設定為上週三，確保一定有資料
    target_date = "2026-03-11"
    
    print(f"正在查詢 {target_date} 的 33000C 合約...")

    # 1. 修正後的搜尋代碼方式 (使用 taiwan_option_static 資料表)
    try:
        opt_info = dl.taiwan_option_static()
    except:
        # 如果上面的不行，嘗試另一個常用指令
        opt_info = dl.taiwan_option_info()
    
    # 篩選 33000 Call
    target_contracts = opt_info[
        (opt_info['strike_price'] == 33000) & 
        (opt_info['call_put'].str.lower() == 'call')
    ]
    
    if target_contracts.empty:
        print("找不到 33000C 合約，請檢查履約價是否正確。")
        return

    # 取得第一個合約 ID (通常是當週週選)
    option_id = target_contracts.iloc[0]['option_id']
    print(f"找到代碼: {option_id}")

    # 2. 抓取分 K 資料 (修正參數名稱)
    df = dl.taiwan_option_daily_kline(
        option_id=option_id,
        start_date=target_date,
        end_date=target_date
    )

    if df.empty:
        print(f"合約 {option_id} 在 {target_date} 無成交資料。")
        return

    # 3. 整理資料並計算 5MA
    df['date_time'] = pd.to_datetime(df['date'] + ' ' + df['time'])
    df = df.sort_values('date_time')
    
    # 計算收盤價的 5 根 K 棒移動平均
    df['5MA'] = df['Close'].rolling(window=5).mean()

    # 4. 篩選 13:45 的數據
    result = df[df['time'] == '13:45:00']
    
    if not result.empty:
        val = result.iloc[0]['5MA']
        print(f"✅ 計算成功！")
        print(f"合約: {option_id}")
        print(f"時間: 13:45")
        print(f"5MA 價格: {val}")
    else:
        print("找不到 13:45 的數據，可能該分鐘無成交。")

if __name__ == "__main__":
    get_33000c_5ma()
