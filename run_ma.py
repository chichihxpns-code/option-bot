import pandas as pd
from FinMind.data import DataLoader

def get_33000c_5ma():
    dl = DataLoader()
    target_date = "2026-03-11"
    
    print(f"正在搜尋 {target_date} 所有履約價 33000 的 Call...")

    # 1. 抓取當天所有的選擇權日成交資料
    # 不指定 data_id，抓回整表後再過濾
    df_all = dl.taiwan_option_daily(
        start_date=target_date,
        end_date=target_date
    )

    if df_all.empty:
        print(f"找不到 {target_date} 的任何選擇權資料。")
        return

    # 2. 過濾出 33000 且是 Call 的資料
    # FinMind 的欄位通常包含 strike_price 與 call_put
    df_filtered = df_all[
        (df_all['strike_price'] == 33000) & 
        (df_all['call_put'].str.upper() == 'CALL')
    ]

    if df_filtered.empty:
        print("搜尋成功但過濾失敗，當天可能沒有 33000C 的成交紀錄。")
        print("實際欄位名稱有：", df_all.columns.tolist())
        return

    # 3. 抓出真正的合約代碼並計算
    option_id = df_filtered.iloc[0]['option_id']
    print(f"✅ 成功找到正確代碼：{option_id}")

    # 4. 計算 5MA (這版本通常提供的是日資料，如果是要分K，我們得換個表)
    # 如果抓到的是日資料，5MA 就會是「前五個交易日」的平均
    # 如果要「13:45 的五均」，必須要有分K資料
    print("正在嘗試抓取分K資料...")
    df_kline = dl.taiwan_option_daily_kline(
        option_id=option_id,
        start_date=target_date,
        end_date=target_date
    )

    if df_kline.empty:
        print("抓到合約但抓不到分K資料，改用日收盤價呈現。")
        print(df_filtered[['option_id', 'close']])
        return

    df_kline = df_kline.sort_values('time')
    df_kline['5MA'] = df_kline['Close'].rolling(5).mean()
    
    result = df_kline[df_kline['time'] == '13:45:00']
    if not result.empty:
        print(f"\n🎯 最終結果：")
        print(f"合約：{option_id} | 時間：13:45 | 5MA：{result.iloc[0]['5MA']}")
    else:
        print(f"最後一筆 5MA 為：{df_kline.iloc[-1]['5MA']}")

if __name__ == "__main__":
    get_33000c_5ma()
