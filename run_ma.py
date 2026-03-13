import pandas as pd
import numpy as np

def get_33000c_5ma():
    print("正在執行 33000C 5MA 自動化計算...")
    
    # 這裡我們手動模擬 13:41 - 13:45 的數據，確保程式一定能跑完
    # 等到開盤日，你可以再換回 dl.taiwan_option_daily_kline
    data = {
        'time': ['13:41:00', '13:42:00', '13:43:00', '13:44:00', '13:45:00'],
        'Close': [100.0, 102.0, 105.0, 103.0, 110.0]
    }
    
    df = pd.DataFrame(data)
    
    # 計算 5MA
    df['5MA'] = df['Close'].rolling(window=5).mean()
    
    # 取得 13:45 的結果
    result = df[df['time'] == '13:45:00']
    
    if not result.empty:
        val = result.iloc[0]['5MA']
        print(f"\n✅ 自動化流程測試成功！")
        print(f"模擬合約：TXO33000C6")
        print(f"時間：13:45")
        print(f"計算得出的 5MA 為：{val}")
        print("\n(提示：目前為模擬數據，週一開盤後可接入真實 API)")
    else:
        print("計算失敗。")

if __name__ == "__main__":
    get_33000c_5ma()
