import pandas as pd
import requests

def analyze_support_resistance():
    # 1. 拿出你剛剛申請的 VIP 通行證
    token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJkYXRlIjoiMjAyNi0wMS0zMCAwODoxNToxMSIsInVzZXJfaWQiOiJkZW5uaXNsaW45OTk5IiwiZW1haWwiOiJkZW5uaXNsaW45OTk5QGdtYWlsLmNvbSIsImlwIjoiNjAuMjQ4LjE4LjIxMCJ9.XlLccdGIeJRr2hM23_B3yolW2I-hszdGEwcBffYxMA8"
    target_date = "2026-03-13"

    print(f"🚀 繞過網頁防火牆！使用 Token 直連資料庫，分析 {target_date} 籌碼...\n")

    url = "https://api.finmindtrade.com/api/v4/data"
    params = {
        "dataset": "TaiwanOptionDaily", # 免費版可用的日結算資料
        "start_date": target_date,
        "end_date": target_date,
        "token": token
    }

    try:
        res = requests.get(url, params=params)
        data = res.json()

        if "data" not in data or not data["data"]:
            print("❌ 找不到資料，請確認 Token 或日期。")
            return

        # 將原始資料轉換成表格
        df = pd.DataFrame(data["data"])
        df.columns = df.columns.str.lower()

        # 篩選出 TXO (台指選擇權)
        df = df[df['option_id'].str.startswith('TXO')]

        if df.empty:
            print("❌ 找不到 TXO 台指選擇權的資料。")
            return

        # 確保未平倉量 (open_interest) 和履約價是數字格式
        df['open_interest'] = pd.to_numeric(df['open_interest'], errors='coerce').fillna(0)
        df['strike_price'] = pd.to_numeric(df['strike_price'], errors='coerce')

        # 分離買權 (Call) 與賣權 (Put)
        calls = df[df['call_put'].str.upper() == 'CALL']
        puts = df[df['call_put'].str.upper() == 'PUT']

        # 加總每個履約價的未平倉量
        calls_oi = calls.groupby('strike_price')['open_interest'].sum().reset_index()
        puts_oi = puts.groupby('strike_price')['open_interest'].sum().reset_index()

        # 合併成一張「支撐壓力表」
        sr_table = pd.merge(calls_oi, puts_oi, on='strike_price', how='outer', suffixes=('_call', '_put')).fillna(0)
        sr_table = sr_table.sort_values('strike_price')

        # --- 尋找最大支撐與壓力 ---
        max_call_idx = sr_table['open_interest_call'].idxmax()
        max_put_idx = sr_table['open_interest_put'].idxmax()

        resistance_strike = sr_table.loc[max_call_idx, 'strike_price']
        resistance_vol = sr_table.loc[max_call_idx, 'open_interest_call']

        support_strike = sr_table.loc[max_put_idx, 'strike_price']
        support_vol = sr_table.loc[max_put_idx, 'open_interest_put']

        # --- 印出超專業分析報告 ---
        print("📊 【選擇權支撐壓力表 (節錄)】")
        print("==================================================")
        print(f"{'買權OI (壓力)':>12} | {'履約價':>8} | {'賣權OI (支撐)':>12}")
        print("-" * 50)
        
        # 為了版面乾淨，只印出有一定口數 (例如 > 2000口) 的重要防守區
        display_df = sr_table[(sr_table['open_interest_call'] > 2000) | (sr_table['open_interest_put'] > 2000)]
        for _, row in display_df.iterrows():
            print(f"{int(row['open_interest_call']):>14} | {int(row['strike_price']):>8} | {int(row['open_interest_put']):>14}")
        print("==================================================")

        print("\n🤖 【AI 盤勢籌碼重點分析】")
        print(f"📈 最大壓力區：{int(resistance_strike)} 點 (防守口數：{int(resistance_vol)} 口)")
        print(f"📉 最大支撐區：{int(support_strike)} 點 (防守口數：{int(support_vol)} 口)")

        print("\n💡 【操作解讀】")
        print(f"1. 莊家結算防守區間落於 【{int(support_strike)} ~ {int(resistance_strike)}】 之間。")
        if resistance_strike - support_strike <= 400:
            print("2. 支撐與壓力區間較窄，暗示近期盤勢可能為「狹幅震盪」，適合高出低進的區間策略。")
        else:
            print("2. 支撐與壓力區間較寬，大盤震盪劇烈，需注意單邊突破的風險。")

        print(f"3. 警戒線：若指數強勢突破 {int(resistance_strike)} 點，將引發買權莊家的停損買盤（軋空行情）；")
        print(f"   反之，若跌破 {int(support_strike)} 點，則需防範賣權莊家停損造成的踩踏效應（殺多行情）。")

    except Exception as e:
        print(f"程式執行發生錯誤: {e}")

if __name__ == "__main__":
    analyze_support_resistance()
