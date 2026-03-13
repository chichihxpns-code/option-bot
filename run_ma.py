import pandas as pd
from FinMind.data import DataLoader

def get_33000c_real_data():
    dl = DataLoader()
    # 設定目標日期為上週五
    target_date = "2026-03-13"
    
    print(f"正在搜尋 {target_date} 的 33000C 真實數據...")

    # 1. 取得當天所有選擇權報價，用來找出正確的 option_id
    df_all = dl.taiwan_option_daily(
        start_date=target_date,
        end_date=target_date
    )

    if df_all.empty:
        print(f"❌ 找不到 {target_date} 的任何資料，請確認日期是否為交易日。")
        return

    # 2. 篩選履約價 33000 的 Call
    # 這裡過濾 strike_price 和 call_put
    target = df_all[(df_all['strike_price'] == 33000) & (df_all['call_put'].str.upper() == 'CALL')]

    if target.empty:
        print("❌ 找不到 33000C 合約，當天可能沒有這個履約價的成交。")
        return

    # 3. 拿到正確的 ID (例如 TXO33000C6)
    option_id = target.iloc[0]['option_id']
    print(f"✅ 找到合約代碼：{option_id}")

    # 4. 抓取分 K 資料來計算 5MA
    df_kline = dl.taiwan_option_daily_kline(
        option_id=option_id,
        start_date=target_date,
        end_date=target_date
    )

    if df_kline.empty:
        print(f"⚠ 抓到合約但無分K資料，顯示日收盤價：{target.iloc[0]['close']}")
        return

    # 5. 計算 5MA (以收盤價 Close 計算)
    df_kline = df_kline.sort_values('time')
    df_kline['5MA'] = df_kline['Close'].rolling(window=5).mean()

    # 6. 輸出 13:45 的結果
    result = df_kline[df_kline['time'] == '13:45:00']
    
    if not result.empty:
        final_ma = result.iloc[0]['5MA']
        print(f"\n🎯 查詢成功！")
        print(f"日期：{target_date} | 合約：{option_id}")
        print(f"13:45 的 5MA 價格為：{final_ma}")
    else:
        # 如果 13:45 剛好沒成交，就抓最後一筆
        last_ma = df_kline.iloc[-1]['5MA']
        print(f"13:45 無成交，最後一筆 (13:44 或收盤) 的 5MA 為：{last_ma}")

if __name__ == "__main__":
    get_33000c_real_data()
