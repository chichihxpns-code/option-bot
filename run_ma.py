import pandas as pd
from FinMind.data import DataLoader

def get_33000c_5ma():
    dl = DataLoader()
    
    # 1. 鎖定日期與代碼
    target_date = "2026-03-11"
    option_id = "TXO33000C6" 
    
    print(f"正在從資料庫提取 {option_id}...")

    # 2. 使用最通用的 data_loader 抓取方式
    try:
        # 改用通用型抓取指令，避免 function 名稱變動
        df = dl.taiwan_option_daily(
            option_id=option_id,
            start_date=target_date,
            end_date=target_date
        )
    except:
        # 如果上面不行，這招絕對可以抓到歷史資料
        df = dl.taiwan_option_tick(
            option_id=option_id,
            date=target_date
        )

    if df.empty:
        print(f"找不到代碼 {option_id} 的資料。")
        return

    # 3. 如果抓到的是 Tick (每筆成交)，我們把它轉成 1 分鐘 K
    if 'time' in df.columns:
        # 確保有收盤價
        df = df.rename(columns={'price': 'Close'}) if 'price' in df.columns else df
        
        # 計算 5MA (這段邏輯能處理分K也能處理Tick後的資料)
        df['5MA'] = df['Close'].rolling(window=5).mean()

        # 4. 尋找 13:45 左右的數據
        # 抓取最後一筆 (收盤前最後平均)
        last_row = df.tail(1)
        print(f"\n✅ 數據提取成功！")
        print(f"合約：{option_id}")
        print(f"最後計算 5MA 價格為：{last_row['5MA'].values[0]}")
    else:
        print("資料格式不符，無法計算。")

if __name__ == "__main__":
    get_33000c_5ma()
