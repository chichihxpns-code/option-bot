import pandas as pd
from FinMind.data import DataLoader
from datetime import datetime, timedelta

def get_33000c_5ma():
    dl = DataLoader()
    
    # 自動抓取「昨天」或「今天」的日期 (因為 13:45 執行時，當天資料已產生)
    # 若在非交易日執行，建議手動改為最近的週三
    target_date = datetime.now().strftime("%Y-%m-%d")
    
    print(f"執行時間: {datetime.now()}")
    print(f"正在查詢 {target_date} 的 33000C 合約...")

    # 1. 搜尋代碼
    opt_info = dl.taiwan_option_info()
    target_contracts = opt_info[
        (opt_info['strike_price'] == 33000) & 
        (opt_info['call_put'] == 'call')
    ]
    
    if target_contracts.empty:
        print("找不到 33000C 合約")
        return

    option_id = target_contracts.iloc[0]['option_id']
    print(f"找到代碼: {option_id}")

    # 2. 抓取分 K
    df = dl.taiwan_option_daily_kline(
        option_id=option_id,
        start_date=target_date,
        end_date=target_date
    )

    if df.empty:
        print("今日無成交資料")
        return

    # 3. 計算 5MA (包含補值邏輯)
    df['Timestamp'] = pd.to_datetime(df['date'] + ' ' + df['time'])
    df = df.sort_values('Timestamp')
    
    # 建立完整時間軸避免缺值
    full_times = pd.date_range(
        start=f"{target_date} 08:46:00", 
        end=f"{target_date} 13:45:00", 
        freq='1min'
    )
    df_full = pd.DataFrame({'Timestamp': full_times})
    df_merged = pd.merge(df_full, df, on='Timestamp', how='left').fillna(method='ffill')
    
    df_merged['5MA'] = df_merged['Close'].rolling(5).mean()

    # 4. 輸出結果
    result = df_merged[df_merged['Timestamp'] == f"{target_date} 13:45:00"]
    if not result.empty:
        print(f"【結果】{option_id} 13:45 的 5MA 為: {result.iloc[0]['5MA']}")
    else:
        print("找不到 13:45 的數據")

if __name__ == "__main__":
    get_33000c_5ma()
