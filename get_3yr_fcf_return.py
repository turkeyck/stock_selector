import yfinance as yf
import pandas as pd
import time

def get_3yr_fcf_return(stock_ids):
    fcf_data = {}
    target_years = ['2024', '2023', '2022']

    for stock_id in stock_ids:
        suffix = ['TW', 'TWO']
        try:
            n_test=0
            while True:
                ticker_symbol = f"{stock_id}.{suffix[n_test]}"
                print(f"\n🔍 處理 {ticker_symbol}...")
                ticker = yf.Ticker(ticker_symbol)
                cf = ticker.cashflow
                bs = ticker.balance_sheet

                if cf.empty or bs.empty:
                    n_test+=1
                else:
                    break
                if n_test>=2:
                    print(f"❌ {stock_id}資料為空")
                    continue

            fcf_returns = {}

            # 將 datetime64 欄位轉為字串
            cf_year_map = {str(col.year): col for col in cf.columns}
            bs_year_map = {str(col.year): col for col in bs.columns}

            for year in target_years:
                try:
                    if year not in cf_year_map or year not in bs_year_map:
                        print(f" - ✖ {year} 沒有對應資料")
                        continue

                    ocf = cf.at['Operating Cash Flow', cf_year_map[year]]
                    capex = cf.at['Capital Expenditure', cf_year_map[year]]
                    total_assets = bs.at['Total Assets', bs_year_map[year]]
                    print(f"ocf={ocf}")
                    print(f"capex={capex}")
                    print(f"total_asset={total_assets}")
                    if pd.isna(ocf) or pd.isna(capex) or pd.isna(total_assets) or total_assets == 0:
                        print(f" - ⚠ {year} 欠缺有效資料")
                        continue

                    fcf = ocf + capex  # 注意 capex 通常是負值
                    fcf_return = fcf / total_assets
                    fcf_returns[f"fcf_return_{year}"] = fcf_return
                    print(f"✅ {year} FCF Return = {fcf_return:.4%}")

                except KeyError as e:
                    print(f" - ❗ 欄位錯誤：{e}")
                except Exception as e:
                    print(f" - ❗ 其他錯誤：{e}")

            if len(fcf_returns) == 3:
                fcf_data[stock_id] = fcf_returns
                print(f"🎯 收錄 {stock_id}")
            else:
                print(f"⛔ 資料不足，跳過 {stock_id}")

        except Exception as e:
            print(f"❌ 外層錯誤 {stock_id}: {e}")
        time.sleep(0.5)

    return fcf_data



