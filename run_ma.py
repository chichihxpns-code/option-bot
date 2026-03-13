import pandas as pd
from FinMind.data import DataLoader

def test_real_market_data():
    dl = DataLoader()
    target_date = "2026-03-13"
    # 我們改用一個當天絕對有交易的合約來測試 (23600C)
    option_id = "TXO23600C6" 
    
    print(f"測試抓取熱門合約 {option_id} 的數據...")

    try:
        # 抓取日 K 線
        df = dl.taiwan_option_daily_kline(
            option_id=option_id,
            start_date=target_date,
            end_date=target_date
        )
    except Exception as e:
        print(f"❌ API 連線異常: {e}")
        return

    if df.empty:
        print(f"❌ 依然找不到資料。這代表 FinMind 免費版目前限制了該日期的存取。")
        return

    # 計算 5MA
    df = df.sort_values('time')
    df['5MA'] = df['Close'].rolling(window=5).mean()

    # 輸出
    last_row = df.tail(1)
    print(f"\n✅ 終於成功抓到市場真實數據！")
    print(f"合約：{option_id}")
    print(f"最後成交時間：{last_row['time'].values[0]}")
    print(f"最後成交價：{last_row['Close'].values[0]}")
    print(f"最後 5MA：{last_row['5MA'].values[0]}")

if __name__ == "__main__":
    test_real_market_data()
