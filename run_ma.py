import pandas as pd
from FinMind.data import DataLoader

def get_33000c_5ma():
    dl = DataLoader()
    
    # 1. 直接指定日期與代碼 (3月W2結算日為 03-11)
    target_date = "2026-03-11"
    option_id = "TXO33000C6" 
    
    print(f"正在抓取 {target_date} 合約 {option_id} 的行情...")

    # 2. 直接抓取日分 K 資料
    try:
        df = dl.taiwan_option_daily_kline(
            option_id=option_id,
            start_date=target_date,
            end_date=target_date
        )
    except Exception as e:
        print(f"API 抓取失敗: {e}")
        return

    if df.empty:
        print(f"找不到資料！請確認代碼 {option_id} 是否正確，或日期 {target_date} 是否有交易。")
        return

    # 3. 計算 5MA
    df = df.sort_values('time')
    df['5MA'] = df['Close'].rolling(window=5).mean()

    # 4. 尋找 13:45 的數據
    result = df[df['time'] == '13:45:00']
    
    if not result.empty:
        val = result.iloc[0]['5MA']
        print(f"\n✅ 計算成功！")
        print(f"合約：{option_id}")
        print(f"13:45 的 5MA 價格為：{val}")
    else:
        # 如果剛好沒成交，顯示最後一筆
        last_val = df.tail(1)['5MA'].values[0]
        print(f"13:45 無成交，最後一筆 5MA 為：{last_val}")

if __name__ == "__main__":
    get_33000c_5ma()
