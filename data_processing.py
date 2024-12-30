import pandas as pd
import os
import re

def process_excel(file_path, csv_dir):
    try:
        df = pd.read_excel(file_path, header=3, engine='xlrd')
    except Exception as e:
        print(f"無法讀取文件 {file_path}: {str(e)}")
        return None

    # 從檔案名稱提取年份
    file_name = os.path.basename(file_path)
    year_match = re.search(r'(\d{3})年', file_name)
    if year_match:
        year = int(year_match.group(1)) + 1911  # 轉換民國年為西元年
    else:
        print(f"無法從檔案名稱 {file_name} 提取年份")
        return None

    # 創建 CSV 檔案路徑
    csv_filename = os.path.basename(file_path).replace('.xls', '.csv')
    csv_path = os.path.join(csv_dir, csv_filename)
    
    # 確保 csv_dir 存在
    os.makedirs(csv_dir, exist_ok=True)
    
    # 將 DataFrame 轉換為 CSV
    df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    print(f"CSV 文件已保存至: {csv_path}")

    city_column = df.columns[0]
    total_pop_column = df.columns[1]
    elderly_pop_column = df.columns[-4]  # 65歲以上總計列

    result = []
    for _, row in df.iterrows():
        city = row[city_column]
        if isinstance(city, str) and ('縣' in city or '市' in city):
            total_pop = row[total_pop_column]
            elderly_pop = row[elderly_pop_column]
            if pd.notna(total_pop) and pd.notna(elderly_pop):
                total_pop = int(float(str(total_pop).replace(',', '')))
                elderly_pop = int(float(str(elderly_pop).replace(',', '')))
                result.append({
                    '年份': year,
                    '縣市': city,
                    '總計人口': total_pop,
                    '65歲以上人口': elderly_pop,
                    '高齡化比例': round(elderly_pop / total_pop * 100, 2),
                })

    return pd.DataFrame(result)

def process_all_files(raw_data_dir):
    csv_dir = os.path.join(os.path.dirname(raw_data_dir), 'csv_data')
    processed_data_dir = os.path.join(os.path.dirname(raw_data_dir), 'processed_data')
    
    all_results = []
    for filename in os.listdir(raw_data_dir):
        if filename.endswith('.xls'):
            file_path = os.path.join(raw_data_dir, filename)
            result = process_excel(file_path, csv_dir)
            if result is not None:
                all_results.append(result)
    
    if all_results:
        combined_results = pd.concat(all_results, ignore_index=True)
        result_csv_path = os.path.join(processed_data_dir, 'combined_population_data.csv')
        os.makedirs(processed_data_dir, exist_ok=True)
        combined_results.to_csv(result_csv_path, index=False, encoding='utf-8-sig')
        print(f"\n所有處理後的數據已合併並保存至: {result_csv_path}")
    else:
        print("沒有成功處理任何文件")

# 使用函數
raw_data_dir = 'raw_data'  # 請確保這個路徑正確
process_all_files(raw_data_dir)