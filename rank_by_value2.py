import yfinance as yf
import pandas as pd
import time

def rank_by_value(companies):
    """
    根據 PB、PE、殖利率進行排序，並計算總排名分數。
    分數越低表示估值越便宜。

    參數:
        companies (list of str): 股票代號列表。

    返回:
        DataFrame: 含 PB, PE, Dividend Yield, 各自排名與總排名分數。
    """
    results = []
    for stock_id in companies:
        suffix = ['TW', 'TWO']
        try:
            n_test=0
            while True:
                ticker_symbol = f"{stock_id}.{suffix[n_test]}"
                ticker = yf.Ticker(ticker_symbol)
                info = ticker.info
                pb = info.get("priceToBook")
                pe = info.get("trailingPE")
                dividend_yield = info.get("dividendYield")
                print(f"dividend_yield={dividend_yield}")
                if pb is None or pe is None or dividend_yield is None:
                    n_test+=1
                else:
                    break
                if n_test>=2:
                    print(f"❌ {stock_id}資料為空")
                    break
                    

            results.append({
                "stock_id": stock_id,
                "pb": pb,
                "pe": pe,
                "div_yield": dividend_yield
            })
        except Exception as e:
            print(f"{stock_id}: 取得估值資料錯誤: {e}")
        time.sleep(0.5)

    df = pd.DataFrame(results)

    # 分別計算排名（PB、PE 越小越好，殖利率越高越好）
    df["pb_rank"] = df["pb"].rank()
    df["pe_rank"] = df["pe"].rank()
    df["div_rank"] = df["div_yield"].rank(ascending=False)
    df["total_score"] = df["pb_rank"] + df["pe_rank"] + df["div_rank"]

    df.sort_values(by="total_score", inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df
