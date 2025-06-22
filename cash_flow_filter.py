import yfinance as yf
import pandas as pd
import time

def cash_flow_filter(stock_id_list, fcf_return_threshold=0.0):
    """
    使用 Yahoo Finance 計算多檔股票的自由現金流報酬率，並返回符合條件的公司列表。

    自由現金流報酬率 = (營業現金流 - 資本支出) / 總資本

    參數:
        stock_id_list (list of str): 股票代號列表，例如 ['2330', '2317']
        fcf_return_threshold (float): 自由現金流報酬率下限，篩選出大於此值的公司。

    返回:
        DataFrame: 包含 stock_id, fcf, capital, fcf_return 等欄位，僅保留符合條件的公司。
    """
    results = []

    for stock_id in stock_id_list:
        ticker_symbol = f"{stock_id}.TW"
        try:
            ticker = yf.Ticker(ticker_symbol)
            cashflow = ticker.cashflow
            
            if 'Total Cash From Operating Activities' in cashflow.index:
                ocf = cashflow.loc['Total Cash From Operating Activities'][0]
            elif 'Operating Cash Flow' in cashflow.index:
                ocf = cashflow.loc['Operating Cash Flow'][0]
            else:
                print(f"{stock_id}: 無營業現金流資料")
                continue

            if 'Capital Expenditures' in cashflow.index:
                capex = cashflow.loc['Capital Expenditures'][0]
            else:
                print(f"{stock_id}: 無資本支出資料")
                continue

            fcf = ocf + capex

            bs = ticker.balance_sheet
            if 'Total Assets' in bs.index:
                capital = bs.loc['Total Assets'][0]
            else:
                print(f"{stock_id}: 無總資產資料")
                continue

            if capital == 0 or pd.isna(capital):
                print(f"{stock_id}: 資本為 0 或缺失")
                continue

            fcf_return = fcf / capital
            results.append({
                "stock_id": stock_id,
                "fcf": fcf,
                "capital": capital,
                "fcf_return": fcf_return
            })

        except Exception as e:
            print(f"{stock_id}: 發生錯誤 - {e}")
        
        time.sleep(0.5)

    df = pd.DataFrame(results)
    df_filtered = df[df['fcf_return'] > fcf_return_threshold].copy()
    df_filtered.sort_values(by='fcf_return', ascending=False, inplace=True)
    df_filtered.reset_index(drop=True, inplace=True)
    return df_filtered
