import re
import pandas as pd
import dgl
import torch
from sklearn.preprocessing import LabelEncoder

#sql文本文件

def parse_sql_inserts(file_path):
    data = []
    # 读取 SQL 文件
    with open(file_path, 'r', encoding='utf-8') as file:
        sql_file = file.read()
    
    # 正则表达式匹配 INSERT 语句
    # INSERT INTO `preprocess_Data` (`id`, `_ip`, `_port`, `_org`, `_service`, `_version`, `_banner`, `_url`, `_title`, `_keywords`, `_copyright`, `_os`, `_server`, `_isp`, `_rdns`, `_ip_c`) VALUES 
    pattern = re.compile(r"INSERT INTO `preprocess_Data` .+? VALUES \((.+?)\);", re.S)
    matches = pattern.findall(sql_file)
    
    for match in matches:
        # 提取单个 INSERT 语句中的数据
        values = match.split(',')
        # 检查是否有16个值，不符合的打印出来并跳过
        if len(values) != 16:
            print(f"Skipping record with incorrect number of fields: {values}")
            continue  # 跳过这条记录，不将其加入到data中
        # 假设第一列是 IP，第二列是端口，依此类推
        # 处理和转换 values 中的数据，例如去掉引号和转义字符
        cleaned_values = [v.strip().strip("'").replace("\\'", "'") for v in values]
        data.append(cleaned_values)
    
    return data

# 调用函数
data = parse_sql_inserts('xas_data.sql')
# 创建 DataFrame
columns = ['id','_ip', '_port', '_org', '_service', '_version', '_banner', '_url', '_title', '_keywords', '_copyright', '_os', '_server', '_isp', '_rdns', '_ip_c']
df = pd.DataFrame(data, columns=columns)

# 创建标签编码器实例，用于将分类标签转换为整数
encoders = {col: LabelEncoder() for col in df.columns}
for col in df.columns:
    df[col + '_id'] = encoders[col].fit_transform(df[col])

# 构建边
edges_data = {
    ('ip', 'connects', 'port'): (torch.tensor(df['_ip_id']), torch.tensor(df['_port_id']))
}

# 构建图
g = dgl.heterograph(edges_data)

