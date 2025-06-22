import pandas as pd
import numpy as np

def filter_high_fcf_return(fcf_data_dict, top_pct=0.2):
    """
    根據輸入的歷年自由現金流資料，計算三年幾何平均自由現金流報酬率，挑出排名前 top_pct 的公司。

    參數:
        fcf_data_dict (dict): 
            結構如下 {
                'stock_id': {
                    'fcf_return_2021': float,
                    'fcf_return_2022': float,
                    'fcf_return_2023': float
                },
                ...
            }
        top_pct (float): 保留排名前 top_pct 的公司（例如 0.2 表示前 20%）

    返回:
        DataFrame: 包含 stock_id, geo_fcf_return 等欄位的前 top_pct 公司。
    """
    records = []
    for stock_id, fcf_returns in fcf_data_dict.items():
        try:
            r1 = fcf_returns['fcf_return_2022']
            r2 = fcf_returns['fcf_return_2023']
            r3 = fcf_returns['fcf_return_2024']
            if r1 <= 0 or r2 <= 0 or r3 <= 0:
                continue  # 幾何平均不能有負數
            geo_avg = np.exp((np.log(r1) + np.log(r2) + np.log(r3)) / 3)
            records.append({"stock_id": stock_id, "geo_fcf_return": geo_avg})
        except Exception:
            continue

    df = pd.DataFrame(records)
    if df.empty:
        return df

    threshold = df['geo_fcf_return'].quantile(1 - top_pct)
    df_filtered = df[df['geo_fcf_return'] >= threshold].sort_values(by='geo_fcf_return', ascending=False)
    df_filtered.reset_index(drop=True, inplace=True)
    return df_filtered
