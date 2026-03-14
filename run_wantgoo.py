import pandas as pd
import requests
import io

def fetch_taifex_oi():
    # 注意：期交所的日期格式必須是 YYYY/MM/DD
    target_date = "2026/03/13"
    print(f"🚀 直接連線【台灣期交所】官方主機，下載 {target_date} 籌碼資料...\n")

    # 期交所隱藏的 CSV 下載 API 網址
    url = "https://www.taifex.com.tw/cht/3/optDataDown"
    
    # 告訴期交所我們要下載什麼：down_type=1 (每日行情), commodity_id=TXO (台指選擇權)
    payload = {
        "down_type": "1",
        "commodity_id": "TXO",
        "queryStartDate": target_date,
        "queryEndDate": target_date
    }

    try:
        # 1. 發送 POST 請求直接下載資料
        res = requests.post(url, data=payload)
        res.raise_for_status()

        # 2. 期交所的編碼通常是 Big5，我們將它解碼並轉成 Pandas 表格
        csv_data = res.content.decode('big5', errors='replace')
        df = pd.read_csv(io.StringIO(csv_data))

        if df.empty or len(df) < 5:
            print("❌ 抓不到期交所資料，可能是該日期為假日。")
            return

        print("✅ 成功從期交所下載原始數據！正在進行 AI 分析...")

        # 3. 資料清洗與整理
        df.columns = df.columns.str.strip() # 清除欄位名稱的空白
        
        # 只看「一般」交易時段 (日盤結算後的未平倉量才是最準的)
        if '交易時段' in df.columns:
            df = df[df['交易時段'] == '一般']

        # 找出最近的結算月份 (排除遠月合約的雜訊，就像玩股網那樣)
        contracts = df['到期月份(週別)'].unique()
        contracts = sorted([str(c).strip() for c in contracts if str(c).strip() != ''])
        target_contract = contracts[0]
        print(f"📌 自動鎖定近期結算合約：{target_contract}")

        df = df[df['到期月份(週別)'].str.strip() == target_contract]

        # 轉換數字格式
        df['履約價'] = pd.to_numeric(df['履約價'], errors='coerce')
        df['未平倉合約數'] = pd.to_numeric(df['未平倉合約數'], errors='coerce').fillna(0)
        df['買賣權'] = df['買賣權'].str.strip()

        # 分離買權 (Call) 和賣權 (Put)
        calls = df[df['買賣權'] == 'Call']
        puts = df[df['買賣權'] == 'Put']

        # 加總相同履約價的未平倉量
        calls_oi = calls.groupby('履約價')['未平倉合約數'].sum().reset_index()
        puts_oi = puts.groupby('履約價')['未平倉合約數'].sum().reset_index()

        # 合併成左右對稱的「支撐壓力表」
        sr_table = pd.merge(calls_oi, puts_oi, on='履約價', how='outer', suffixes=('_call', '_put')).fillna(0)
        sr_table = sr_table.sort_values('履約價')

        # 4. 尋找最大支撐與壓力
        max_call_idx = sr_table['未平倉合約數_call'].idxmax()
        max_put_idx = sr_table['未平倉合約數_put'].idxmax()

        resistance_strike = sr_table.loc[max_call_idx, '履約價']
        resistance_vol = sr_table.loc[max_call_idx, '未平倉合約數_call']

        support_strike = sr_table.loc[max_put_idx, '履約價']
        support_vol = sr_table.loc[max_put_idx, '未平倉合約數_put']

        # 5. 印出漂亮的分析報告
        print("\n📊 【官方選擇權支撐壓力表 (節錄)】")
        print("==================================================")
        print(f"{'買權OI (壓力)':>12} | {'履約價':>8} | {'賣權OI (支撐)':>12}")
        print("-" * 50)

        # 只顯示防守口數大於 2000 口的關鍵區域
        display_df = sr_table[(sr_table['未平倉合約數_call'] > 2000) | (sr_table['未平倉合約數_put'] > 2000)]
        for _, row in display_df.iterrows():
            print(f"{int(row['未平倉合約數_call']):>14} | {int(row['履約價']):>8} | {int(row['未平倉合約數_put']):>14}")
        print("==================================================")

        print("\n🤖 【AI 盤勢籌碼重點分析】")
        print(f"📈 最大壓力區：{int(resistance_strike)} 點 (防守口數：{int(resistance_vol)} 口)")
        print(f"📉 最大支撐區：{int(support_strike)} 點 (防守口數：{int(support_vol)} 口)")

        print("\n💡 【操作解讀】")
        print(f"1. 莊家結算防守區間落於 【{int(support_strike)} ~ {int(resistance_strike)}】 之間。")
        if resistance_strike - support_strike <= 400:
            print("2. 支撐與壓力區間較窄，暗示近期盤勢可能為「狹幅震盪」，適合高賣低買的區間策略。")
        else:
            print("2. 支撐與壓力區間較寬，大盤震盪劇烈，需注意單邊突破的風險。")

        print(f"3. 警戒線：若指數強勢突破 {int(resistance_strike)} 點，將引發買權莊家的停損買盤（軋空行情）；")
        print(f"   反之，若跌破 {int(support_strike)} 點，則需防範賣權莊家停損造成的踩踏效應（殺多行情）。")

    except Exception as e:
        print(f"❌ 程式執行發生錯誤: {e}")

if __name__ == "__main__":
    fetch_taifex_oi()
