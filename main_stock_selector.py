import yfinance as yf
import pandas as pd
import os
from filter_high_fcf_return import filter_high_fcf_return
from get_3yr_fcf_return import get_3yr_fcf_return
from rank_by_value2 import rank_by_value

def get_top300_from_yahoo(filename):
    """
    從 Yahoo 股市排行頁面擷取市值前 300 名的股票清單（使用預先整理的清單或第三方 CSV 資料）。
    可手動準備一份含股票代號的 csv 檔。
    
    返回:
        DataFrame: 包含 stock_id, company_name
    """
    try:
        df = pd.read_csv(filename)  # 請準備此檔案，內含 stock_id 與公司名稱欄位
        df = df.dropna(subset=["stock_id"])
        df["stock_id"] = df["stock_id"].astype(str).str.zfill(4)
        return df[["stock_id", "company_name"]]
    except Exception as e:
        print(f"讀取 {filename} 失敗: ", e)
        return pd.DataFrame([])
    

def convert_raw_market_csv(input_path, output_path):
    # 讀取原始檔案（編碼需符合原檔格式，常見為 utf-8 或 big5）
    df = pd.read_csv(input_path, encoding="utf-8")

    # 清理代號格式（去除 Excel = 公式格式，轉成字串並補零）
    df["代號"] = df["代號"].astype(str).str.replace("=", "").str.replace("\"", "").str.zfill(4)
    df = df.rename(columns={"代號": "stock_id", "名稱": "company_name"})

    # 篩選前 300 名（假設已依市值排好）
    df_top300 = df[["stock_id", "company_name"]].head(300)

    df_top300.to_csv(output_path, index=False)
    print(f"已儲存轉換後的檔案至 {output_path}")


def main(output_csv):
    input_csv = "top300.csv"
    # output_csv = 
    if not os.path.exists(output_csv):
        convert_raw_market_csv(input_csv, output_csv)
    print(f"[1]讀取{output_csv}公司（Goodinfo）...")
    df_top300 = get_top300_from_yahoo(output_csv)
    if df_top300.empty:
        print(f"找不到 {output_csv}，請確認檔案存在且格式正確。")
        return


    stock_ids = df_top300['stock_id'].tolist()
    # yf_symbols = [f"{sid}.{suffix}" for sid, suffix, _ in company_list]
    # name_dict = {sid: name for sid, _, name in company_list}

    print("[2] 擷取三年 FCF 資料...")
    fcf_data_dict = get_3yr_fcf_return(stock_ids)
    print("符合三年資料條件公司數：", len(fcf_data_dict))
    # print(list(fcf_data_dict.items())[5])
    print("[3] 篩選三年平均 FCF 高的公司...")
    df_fcf_high = filter_high_fcf_return(fcf_data_dict)
    # print(df_fcf_high.head())

    fcf_candidates = df_fcf_high['stock_id'].tolist()

    print("[4] 根據估值指標進行綜合排名...")
    df_value = rank_by_value(fcf_candidates)
    
    name_dict = dict(zip(df_top300['stock_id'], df_top300['company_name']))
    df_value.insert(1, 'company_name', df_value['stock_id'].map(name_dict))
    result_name = input_csv.split('.')[0] + '_result.csv'
    # print(df_value.head())
    print(f"[完成] 儲存選股結果 {result_name}")
    df_value.to_csv(result_name, index=False)

if __name__ == "__main__":
    main("top300_list.csv")
    # main("301_600_list.csv")
    # main("601_900_list.csv")
    # main("901_1200_list.csv")
