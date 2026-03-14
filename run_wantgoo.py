import pandas as pd
import requests
import io

def fetch_taifex_oi():
    target_date = "2026/03/13"
    print(f"🚀 直接連線【台灣期交所】官方主機，下載 {target_date} 籌碼資料...\n")

    url = "https://www.taifex.com.tw/cht/3/optDataDown"
    
    payload = {
        "down_type": "1",
        "commodity_id": "TXO",
        "queryStartDate": target_date,
        "queryEndDate": target_date
    }

    try:
        # 1. 發送請求下載資料
        res = requests.post(url, data=payload)
        res.raise_for_status()

        # 2. 轉成 Pandas 表格
        csv_data = res.content.decode('big5', errors='replace')
        df = pd.read_csv(io.StringIO(csv_data))

        if df.empty or len(df) < 5:
            print("❌ 抓不到期交所資料，可能是該日期為假日。")
            return

        print("✅ 成功從期交所下載原始數據！正在進行 AI 分析...")

        df.columns = df.columns.str.strip() 
        
        # 📌 關鍵修正：自動尋找期交所的「未沖銷契約量」欄位
        oi_col = next((c for c in df.columns if '未沖銷' in c or '未平倉' in c), None)
        
        if not oi_col:
            print(f"❌ 找不到未平倉欄位！目前的欄位有：{df.columns.tolist()}")
            return

        # 3. 資料清洗與整理
        if '交易時段' in df.columns:
            df = df[df['交易時段'] == '一般']

        contracts = df['到期月份(週別)'].unique()
        contracts = sorted([str(c).strip() for c in contracts if str(c).strip() != ''])
        target_contract = contracts[0]
        print(f"📌 自動鎖定近期結算合約：{target_contract}")

        df = df[df['到期月份(週別)'].str.strip() == target_contract]

        # 轉換數字格式
        df['履約價'] = pd.to_numeric(df['履約價'], errors='coerce')
        df[oi_col] = pd.to_numeric(df[oi_col], errors='coerce').fillna(0)
        df['買賣權'] = df['買賣權'].str.strip()

        # 分離買權與賣權
        calls = df[df['買賣權'] == 'Call']
        puts = df[df['買賣權'] == 'Put']

        # 加總相同履約價的未平倉量
        calls_oi = calls.groupby('履約價')[oi_col].sum().reset_index()
        puts_oi = puts.groupby('履約價')[oi_col].sum().reset_index()

        # 合併成「支撐壓力表」
        sr_table = pd.merge(calls_oi, puts_oi, on='履約價', how='outer', suffixes=('_call', '_put')).fillna(0)
        sr_table = sr_table.sort_values('履約價')

        # 4. 尋找最大支撐與壓力
        max_call_idx = sr_table[f'{oi_col}_call'].idxmax()
        max_put_idx = sr_table[f'{oi_col}_put'].idxmax()

        resistance_strike = sr_table.loc[max_call_idx, '履約價']
        resistance_vol = sr_table.loc[max_call_idx, f'{oi_col}_call']

        support_strike = sr_table.loc[max_put_idx, '履約價']
        support_vol = sr_table.loc[max_put_idx, f'{oi_col}_put']

        # 5. 印出漂亮的分析報告
        print("\n📊 【官方選擇權支撐壓力表 (節錄)】")
        print("==================================================")
        print(f"{'買權OI (壓力)':>12} | {'履約價':>8} | {'賣權OI (支撐)':>12}")
        print("-" * 50)

        display_df = sr_table[(sr_table[f'{oi_col}_call'] > 2000) | (sr_table[f'{oi_col}_put'] > 2000)]
        for _, row in display_df.iterrows():
            print(f"{int(row[f'{oi_col}_call']):>14} | {int(row['履約價']):>8} | {int(row[f'{oi_col}_put']):>14}")
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
