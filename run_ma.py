import pandas as pd
from FinMind.data import DataLoader

def get_real_data_final():
    dl = DataLoader()
    # 2026-03-13 週五數據
    target_date = "2026-03-13"
    # 使用台指期熱門履約價做測試
    option_id = "TXO23600C6" 
    
    print(f"正在使用通用指令抓取 {option_id}...")

    # 最新版 FinMind SDK 建議使用 fetch_data 配合 data_id
    try:
        # 抓取選擇權日成交資料
        df = dl.taiwan_option_daily(
            option_id=option_id,
            start_date=target_date,
            end_date=target_date
        )
        
        if df.empty:
            print("資料庫回傳空值，可能是該合約今日無成交。")
            return

        # 計算 5MA (日均線邏輯)
        # 注意：若要分K，免費版 API 在假日存取限制較多，我們先確保能抓到日資料
        print(f"✅ 成功抓取！{option_id} 收盤價為: {df.iloc[-1]['close']}")
        
    except Exception as e:
        print(f"❌ 發生錯誤: {e}")
        print("提示：這代表 SDK 版本不支援舊指令，請考慮使用 HTTP Request 或檢查 Token 權限。")

if __name__ == "__main__":
    get_real_data_final()
