import requests
import pandas as pd
from io import StringIO

def analyze_options_oi():
    # 你指定的玩股網網址
    url = "https://www.wantgoo.com/option/support-resistance?date=2026-03-13&contract=202603"
    
    # 偽裝成正常的瀏覽器，避免被玩股網阻擋
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    print("🌐 正在連線玩股網，抓取選擇權未平倉籌碼...")
    
    try:
        res = requests.get(url, headers=headers)
        res.raise_for_status() # 檢查連線狀態
        
        # 使用 pandas 尋找網頁中的所有 HTML 表格
        dfs = pd.read_html(StringIO(res.text))
        
        if not dfs:
            print("❌ 找不到表格，網頁結構可能改變，或資料是由 JavaScript 動態載入。")
            return
            
        # 玩股網的支撐壓力表通常是頁面上的第一個主要表格
        df = dfs[0]
        
        # 為了避免多重表頭問題，我們將欄位名稱轉化為字串，並清理空值
        df.columns = ['_'.join(str(c) for c in col).strip() if isinstance(col, tuple) else str(col) for col in df.columns]
        df = df.dropna(how='all') # 移除全空的列
        
        # --- 尋找關鍵欄位 ---
        # 玩股網的欄位通常包含：買權成交量, 買權未平倉, 履約價, 賣權未平倉, 賣權成交量
        # 我們用關鍵字來鎖定正確的欄位名稱 (避免網頁改版導致欄位名微調)
        call_oi_col = next((c for c in df.columns if '買權' in c and '未平倉' in c), None)
        put_oi_col = next((c for c in df.columns if '賣權' in c and '未平倉' in c), None)
        strike_col = next((c for c in df.columns if '履約價' in c), None)
        
        if not (call_oi_col and put_oi_col and strike_col):
            print(f"❌ 無法辨識欄位名稱。目前抓到的欄位有：{df.columns.tolist()}")
            return

        # 將資料轉為數字格式以便計算
        df[call_oi_col] = pd.to_numeric(df[call_oi_col].astype(str).str.replace(',', ''), errors='coerce')
        df[put_oi_col] = pd.to_numeric(df[put_oi_col].astype(str).str.replace(',', ''), errors='coerce')
        df[strike_col] = pd.to_numeric(df[strike_col].astype(str).str.replace(',', ''), errors='coerce')
        df = df.dropna(subset=[call_oi_col, put_oi_col, strike_col])

        # --- 列印原始表格 ---
        print("\n📊 【選擇權支撐壓力表 (節錄)】")
        print("==================================================")
        # 只挑選履約價附近的重要數據顯示 (避免印出太長)
        # 我們取 買權 或 賣權 未平倉量大於 1000 口的履約價來顯示
        significant_df = df[(df[call_oi_col] > 1000) | (df[put_oi_col] > 1000)]
        display_df = significant_df[[call_oi_col, strike_col, put_oi_col]].copy()
        display_df.columns = ['買權OI (壓力)', '履約價', '賣權OI (支撐)']
        print(display_df.to_string(index=False))
        print("==================================================")

        # --- 自動盤勢分析邏輯 ---
        # 買權未平倉 (Call OI) 最大值 = 莊家認為漲不過去的地方 = 最大壓力
        # 賣權未平倉 (Put OI) 最大值 = 莊家認為跌不下去的地方 = 最大支撐
        max_call_idx = df[call_oi_col].idxmax()
        max_put_idx = df[put_oi_col].idxmax()
        
        resistance_strike = df.loc[max_call_idx, strike_col]
        resistance_vol = df.loc[max_call_idx, call_oi_col]
        
        support_strike = df.loc[max_put_idx, strike_col]
        support_vol = df.loc[max_put_idx, put_oi_col]

        print("\n🤖 【AI 盤勢籌碼重點分析】")
        print(f"📈 最大壓力區：{int(resistance_strike)} 點 (防守口數：{int(resistance_vol)} 口)")
        print(f"📉 最大支撐區：{int(support_strike)} 點 (防守口數：{int(support_vol)} 口)")
        
        print("\n💡 【操作解讀】")
        print(f"1. 莊家結算防守區間落於 【{int(support_strike)} ~ {int(resistance_strike)}】 之間。")
        if resistance_strike - support_strike <= 400:
            print("2. 支撐與壓力區間較窄，暗示近期盤勢可能為「狹幅震盪」，適合高出低進的區間策略。")
        else:
            print("2. 支撐與壓力區間較寬，大盤震盪劇烈，需注意單邊突破的風險。")
            
        print(f"3. 警戒線：若指數強勢突破 {int(resistance_strike)} 點，可能會引發買權莊家的停損買盤（軋空行情）；")
        print(f"   反之，若跌破 {int(support_strike)} 點，則需防範賣權莊家停損造成的踩踏效應（殺多行情）。")

    except Exception as e:
        print(f"❌ 爬蟲執行發生錯誤：{e}")
        print("可能是網站有防爬蟲機制，或是資料尚未更新。")

if __name__ == "__main__":
    analyze_options_oi()
