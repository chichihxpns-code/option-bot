from FinMind.data import DataLoader

def search_option_id():
    dl = DataLoader()
    # 查詢週五當天所有選擇權合約
    df = dl.taiwan_option_daily(
        start_date="2026-03-13",
        end_date="2026-03-13"
    )
    
    if not df.empty:
        # 只看 33000 附近的 Call
        result = df[(df['strike_price'] >= 32000) & (df['call_put'] == 'call')]
        print("--- 找到的合約代碼清單 ---")
        print(result[['option_id', 'strike_price', 'close']])
    else:
        print("抓不到資料，請檢查 API 狀態。")

if __name__ == "__main__":
    search_option_id()
