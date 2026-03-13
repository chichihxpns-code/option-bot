import pandas as pd
from FinMind.data import DataLoader

def get_friday_5ma():
    dl = DataLoader()
    target_date = "2026-03-13"
    # 這是週五 33000C 的標準代碼格式
    option_id = "TXO33000C6" 
    
    print(f"正在強制抓取 {target_date} 合約 {option_id} 的原始成交明細...")

    try:
        # 使用 Tick API，這通常比日 K 線 API 更穩定
        df = dl.taiwan_option_tick(
            option_id=option_id,
            date=target_date
        )
    except Exception as e:
        print(f"❌ 抓取失敗: {e}")
        return

    if df.empty:
        print(f"❌ 找不到資料！可能是代碼有誤，或是當天該合約完全沒有成交。")
        return

    # 1. 整理時間與價格 (Tick 資料欄位為 price 和 time)
    df = df[['time', 'price']].copy()
    df = df.sort_values('time')

    # 2. 計算 5 筆成交移動平均 (5MA)
    # 在 Tick 資料中，5MA 代表「最後五筆成交的平均價」
    df['5MA'] = df['price'].rolling(window=5).mean()

    # 3. 找出最接近 13:45:00 的那筆資料
    # 我們找 13:45 之前的最後一筆紀錄
    df_1345 = df[df['time'] <= '13:45:00'].tail(1)
    
    if not df_1345.empty:
        final_price = df_1345.iloc[0]['price']
        final_ma = df_1345.iloc[0]['5MA']
        print(f"\n✅ 查詢成功！")
        print(f"合約：{option_id}")
        print(f"13:45 當時成交價為：{final_price}")
        print(f"13:45 當時的 5MA 為：{final_ma}")
    else:
        print("找不到 13:45 之前的成交紀錄。")

if __name__ == "__main__":
    get_friday_5ma()
