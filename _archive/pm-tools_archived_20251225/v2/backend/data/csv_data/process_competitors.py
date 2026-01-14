# -*- coding: utf-8 -*-
"""
竞品数据处理脚本
从Sensor Tower CSV文件中提取、清洗、分析数据
生成精选的"必研究竞品清单"
"""

import pandas as pd
import json
import os
from pathlib import Path

# 配置
INPUT_DIR = Path(r"C:\Users\WIN\Downloads\1")
OUTPUT_DIR = Path(__file__).parent

# CSV文件路径
FILES = {
    "total_revenue": INPUT_DIR / "App Store 应用排行榜 收入  (Nov 11, 2025 - Dec 10, 2025, US, AU, CA, FR, DE + 2 其他), 详细.csv",
    "nutrition_revenue": INPUT_DIR / "App Store 应用排行榜 收入  (Nov 11, 2025 - Dec 10, 2025, US, AU, CA, FR, DE + 2 其他), 详细 (1).csv",
    "total_growth": INPUT_DIR / "App Store 应用排行榜 收入 PoP 增长 (Nov 11, 2025 - Dec 10, 2025, US, AU, CA, FR, DE + 2 其他), 详细.csv",
    "nutrition_growth": INPUT_DIR / "App Store 应用排行榜 收入 PoP 增长 (Nov 11, 2025 - Dec 10, 2025, US, AU, CA, FR, DE + 2 其他), 详细 (1).csv",
}

def load_csv(filepath):
    """加载CSV文件"""
    print(f"  Loading: {filepath.name}")
    # 尝试不同的编码
    encodings = ['utf-16', 'utf-16-le', 'utf-8-sig', 'utf-8', 'gbk', 'latin1']
    for enc in encodings:
        try:
            df = pd.read_csv(filepath, sep='\t', encoding=enc)
            print(f"    -> {len(df)} rows (encoding: {enc})")
            return df
        except (UnicodeDecodeError, UnicodeError):
            continue
    raise ValueError(f"Could not decode file: {filepath}")

def aggregate_by_app(df):
    """按App汇总数据（原始数据是每日记录）"""
    # 汇总字段
    agg_dict = {
        'Unified Name': 'first',
        'Unified Publisher Name': 'first',
        'Category': 'first',
        'Downloads (Absolute)': 'sum',
        'Downloads (PoP Growth)': 'sum',
        'Revenue (Absolute)': 'sum',
        'Revenue (PoP Growth)': 'sum',
        'DAU (Absolute)': 'mean',  # DAU取平均值
    }
    
    # 按App ID分组汇总
    grouped = df.groupby('App ID').agg(agg_dict).reset_index()
    return grouped

def calculate_metrics(df):
    """计算关键指标"""
    # ARPU = 收入 / 下载
    df['ARPU'] = df['Revenue (Absolute)'] / df['Downloads (Absolute)'].replace(0, 1)
    
    # 收入增长率
    base_revenue = df['Revenue (Absolute)'] - df['Revenue (PoP Growth)']
    df['Growth Rate'] = df['Revenue (PoP Growth)'] / base_revenue.replace(0, 1)
    
    # 清理异常值 - 使用更合理的上限
    df['ARPU'] = df['ARPU'].clip(0, 50)  # ARPU上限50（合理范围）
    df['Growth Rate'] = df['Growth Rate'].clip(-1, 2)  # 增长率上限200%
    
    return df

def calculate_score(df):
    """计算综合评分 - 优化版本，强调商业规模"""
    import numpy as np
    
    # 收入门槛：$100,000（月收入10万美元以上才有研究价值）
    MIN_REVENUE = 100000
    df['Valid'] = df['Revenue (Absolute)'] >= MIN_REVENUE
    
    # 归一化函数
    def normalize(series):
        min_val = series.min()
        max_val = series.max()
        if max_val == min_val:
            return pd.Series([50] * len(series), index=series.index)
        return (series - min_val) / (max_val - min_val) * 100
    
    # 收入评分 (40%) - 使用对数变换，强调商业规模
    log_revenue = np.log10(df['Revenue (Absolute)'].clip(lower=1))
    revenue_score = normalize(log_revenue) * 0.40
    
    # ARPU评分 (25%) - 转化效率
    arpu_score = normalize(df['ARPU']) * 0.25
    
    # 增长率评分 (15%) - 市场验证
    growth_score = normalize(df['Growth Rate']) * 0.15
    
    # DAU评分 (20%) - 用户活跃度（说明产品有粘性）
    log_dau = np.log10(df['DAU (Absolute)'].fillna(1).clip(lower=1))
    dau_score = normalize(log_dau) * 0.20
    
    df['Score'] = revenue_score + arpu_score + growth_score + dau_score
    
    # 对收入低于门槛的产品大幅降权（这些产品参考价值有限）
    df.loc[~df['Valid'], 'Score'] = df.loc[~df['Valid'], 'Score'] * 0.2
    
    return df

def assign_priority(score):
    """根据评分分配优先级"""
    if score >= 70:
        return "P0"
    elif score >= 50:
        return "P1"
    else:
        return "P2"

def process_data():
    """主处理流程"""
    print("\n" + "="*60)
    print("  竞品数据处理")
    print("="*60)
    
    # Step 1: 加载数据
    print("\n[Step 1] 加载CSV文件...")
    dfs = {}
    for key, filepath in FILES.items():
        if filepath.exists():
            dfs[key] = load_csv(filepath)
        else:
            print(f"  Warning: {filepath} not found")
    
    # Step 2: 处理Nutrition分榜数据
    print("\n[Step 2] 处理 Nutrition 分榜...")
    if 'nutrition_revenue' in dfs:
        nutrition_df = dfs['nutrition_revenue'].copy()
        nutrition_df = aggregate_by_app(nutrition_df)
        nutrition_df = calculate_metrics(nutrition_df)
        nutrition_df = calculate_score(nutrition_df)
        nutrition_df['Priority'] = nutrition_df['Score'].apply(assign_priority)
        nutrition_df = nutrition_df.sort_values('Score', ascending=False)
        print(f"    -> {len(nutrition_df)} unique apps")
    
    # Step 3: 处理总榜数据（只取Health & Fitness）
    print("\n[Step 3] 处理总榜 (Health & Fitness)...")
    if 'total_revenue' in dfs:
        total_df = dfs['total_revenue'].copy()
        # 筛选Health & Fitness
        health_df = total_df[total_df['Category'] == 'Health & Fitness'].copy()
        health_df = aggregate_by_app(health_df)
        health_df = calculate_metrics(health_df)
        health_df = calculate_score(health_df)
        health_df['Priority'] = health_df['Score'].apply(assign_priority)
        health_df = health_df.sort_values('Score', ascending=False)
        print(f"    -> {len(health_df)} unique Health & Fitness apps")
    
    # Step 4: 生成Top 30清单
    print("\n[Step 4] 生成 Top 30 必研究清单...")
    
    # 策略：确保头部产品（收入Top 10）+ 高效率产品（ARPU高）+ 高增长产品
    
    # 从Nutrition分榜取：
    # - 收入Top 10
    nutrition_by_revenue = nutrition_df.nlargest(10, 'Revenue (Absolute)').copy()
    # - 评分Top 15（去重）
    nutrition_by_score = nutrition_df[~nutrition_df['App ID'].isin(nutrition_by_revenue['App ID'])].head(10).copy()
    nutrition_combined = pd.concat([nutrition_by_revenue, nutrition_by_score])
    nutrition_combined['Source'] = 'Nutrition'
    
    # 从总榜补充跨赛道标杆（如Calm, Strava, Flo等）
    nutrition_app_ids = set(nutrition_combined['App ID'].tolist())
    # 先按收入排序，取收入Top 10的非Nutrition产品
    health_by_revenue = health_df[~health_df['App ID'].isin(nutrition_app_ids)].nlargest(10, 'Revenue (Absolute)').copy()
    health_by_revenue['Source'] = 'Health_Total'
    
    # 合并
    top30_df = pd.concat([nutrition_combined, health_by_revenue], ignore_index=True)
    top30_df = top30_df.sort_values('Score', ascending=False).head(30)
    top30_df['Rank'] = range(1, len(top30_df) + 1)
    
    # Step 5: 整理输出字段
    print("\n[Step 5] 整理输出...")
    
    output_columns = [
        'Rank', 'Unified Name', 'Unified Publisher Name', 'Category',
        'Revenue (Absolute)', 'Downloads (Absolute)', 'ARPU',
        'Growth Rate', 'DAU (Absolute)', 'Score', 'Priority', 'Source'
    ]
    
    top30_output = top30_df[output_columns].copy()
    top30_output.columns = [
        'rank', 'app_name', 'publisher', 'category',
        'revenue', 'downloads', 'arpu',
        'growth_rate', 'dau', 'score', 'priority', 'source'
    ]
    
    # 格式化数字
    top30_output['revenue'] = top30_output['revenue'].round(0).astype(int)
    top30_output['downloads'] = top30_output['downloads'].round(0).astype(int)
    top30_output['arpu'] = top30_output['arpu'].round(2)
    top30_output['growth_rate'] = (top30_output['growth_rate'] * 100).round(1)  # 转为百分比
    top30_output['dau'] = top30_output['dau'].fillna(0).round(0).astype(int)
    top30_output['score'] = top30_output['score'].round(1)
    
    # Step 6: 保存文件
    print("\n[Step 6] 保存输出文件...")
    
    # 确保输出目录存在
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # 保存Top 30 CSV
    top30_csv = OUTPUT_DIR / "top30_must_study.csv"
    top30_output.to_csv(top30_csv, index=False, encoding='utf-8-sig')
    print(f"  -> {top30_csv}")
    
    # 保存完整Nutrition分榜
    nutrition_csv = OUTPUT_DIR / "nutrition_competitors.csv"
    nutrition_cols = [
        'Unified Name', 'Unified Publisher Name', 'Category',
        'Revenue (Absolute)', 'Downloads (Absolute)', 'ARPU',
        'Growth Rate', 'DAU (Absolute)', 'Score', 'Priority'
    ]
    nutrition_output = nutrition_df[nutrition_cols].copy()
    nutrition_output.columns = [
        'app_name', 'publisher', 'category',
        'revenue', 'downloads', 'arpu',
        'growth_rate', 'dau', 'score', 'priority'
    ]
    nutrition_output['source'] = 'Nutrition'
    nutrition_output.to_csv(nutrition_csv, index=False, encoding='utf-8-sig')
    print(f"  -> {nutrition_csv}")
    
    # 保存JSON数据库
    competitors_json = OUTPUT_DIR / "competitors.json"
    
    # 合并所有数据
    all_data = {
        "metadata": {
            "source": "Sensor Tower",
            "date_range": "Nov 11, 2025 - Dec 10, 2025",
            "regions": ["US", "AU", "CA", "FR", "DE", "+2 others"],
            "total_nutrition_apps": len(nutrition_df),
            "total_health_apps": len(health_df),
        },
        "top30": top30_output.to_dict(orient='records'),
        "nutrition_all": nutrition_df[[
            'App ID', 'Unified Name', 'Revenue (Absolute)', 
            'Downloads (Absolute)', 'ARPU', 'Growth Rate', 'Score', 'Priority'
        ]].head(50).to_dict(orient='records'),
    }
    
    with open(competitors_json, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    print(f"  -> {competitors_json}")
    
    # Step 7: 打印摘要
    print("\n" + "="*60)
    print("  Done!")
    print("="*60)
    
    print("\n[Top 30 Must Study List]")
    print("-" * 90)
    print(f"{'Rank':<5} {'App Name':<35} {'Revenue':>12} {'ARPU':>8} {'Growth':>8} {'Priority':<8}")
    print("-" * 90)
    
    for _, row in top30_output.iterrows():
        name = row['app_name'][:33] if len(str(row['app_name'])) > 33 else row['app_name']
        revenue = f"${row['revenue']:,}"
        arpu = f"${row['arpu']:.2f}"
        growth = f"{row['growth_rate']:+.1f}%"
        print(f"{row['rank']:<5} {name:<35} {revenue:>12} {arpu:>8} {growth:>8} {row['priority']:<8}")
    
    print("-" * 90)
    p0_count = len(top30_output[top30_output['priority']=='P0'])
    p1_count = len(top30_output[top30_output['priority']=='P1'])
    p2_count = len(top30_output[top30_output['priority']=='P2'])
    print(f"\nP0 (High Priority): {p0_count}")
    print(f"P1 (Medium Priority): {p1_count}")
    print(f"P2 (Low Priority): {p2_count}")
    
    return top30_output

if __name__ == "__main__":
    process_data()


竞品数据处理脚本
从Sensor Tower CSV文件中提取、清洗、分析数据
生成精选的"必研究竞品清单"
"""

import pandas as pd
import json
import os
from pathlib import Path

# 配置
INPUT_DIR = Path(r"C:\Users\WIN\Downloads\1")
OUTPUT_DIR = Path(__file__).parent

# CSV文件路径
FILES = {
    "total_revenue": INPUT_DIR / "App Store 应用排行榜 收入  (Nov 11, 2025 - Dec 10, 2025, US, AU, CA, FR, DE + 2 其他), 详细.csv",
    "nutrition_revenue": INPUT_DIR / "App Store 应用排行榜 收入  (Nov 11, 2025 - Dec 10, 2025, US, AU, CA, FR, DE + 2 其他), 详细 (1).csv",
    "total_growth": INPUT_DIR / "App Store 应用排行榜 收入 PoP 增长 (Nov 11, 2025 - Dec 10, 2025, US, AU, CA, FR, DE + 2 其他), 详细.csv",
    "nutrition_growth": INPUT_DIR / "App Store 应用排行榜 收入 PoP 增长 (Nov 11, 2025 - Dec 10, 2025, US, AU, CA, FR, DE + 2 其他), 详细 (1).csv",
}

def load_csv(filepath):
    """加载CSV文件"""
    print(f"  Loading: {filepath.name}")
    # 尝试不同的编码
    encodings = ['utf-16', 'utf-16-le', 'utf-8-sig', 'utf-8', 'gbk', 'latin1']
    for enc in encodings:
        try:
            df = pd.read_csv(filepath, sep='\t', encoding=enc)
            print(f"    -> {len(df)} rows (encoding: {enc})")
            return df
        except (UnicodeDecodeError, UnicodeError):
            continue
    raise ValueError(f"Could not decode file: {filepath}")

def aggregate_by_app(df):
    """按App汇总数据（原始数据是每日记录）"""
    # 汇总字段
    agg_dict = {
        'Unified Name': 'first',
        'Unified Publisher Name': 'first',
        'Category': 'first',
        'Downloads (Absolute)': 'sum',
        'Downloads (PoP Growth)': 'sum',
        'Revenue (Absolute)': 'sum',
        'Revenue (PoP Growth)': 'sum',
        'DAU (Absolute)': 'mean',  # DAU取平均值
    }
    
    # 按App ID分组汇总
    grouped = df.groupby('App ID').agg(agg_dict).reset_index()
    return grouped

def calculate_metrics(df):
    """计算关键指标"""
    # ARPU = 收入 / 下载
    df['ARPU'] = df['Revenue (Absolute)'] / df['Downloads (Absolute)'].replace(0, 1)
    
    # 收入增长率
    base_revenue = df['Revenue (Absolute)'] - df['Revenue (PoP Growth)']
    df['Growth Rate'] = df['Revenue (PoP Growth)'] / base_revenue.replace(0, 1)
    
    # 清理异常值 - 使用更合理的上限
    df['ARPU'] = df['ARPU'].clip(0, 50)  # ARPU上限50（合理范围）
    df['Growth Rate'] = df['Growth Rate'].clip(-1, 2)  # 增长率上限200%
    
    return df

def calculate_score(df):
    """计算综合评分 - 优化版本，强调商业规模"""
    import numpy as np
    
    # 收入门槛：$100,000（月收入10万美元以上才有研究价值）
    MIN_REVENUE = 100000
    df['Valid'] = df['Revenue (Absolute)'] >= MIN_REVENUE
    
    # 归一化函数
    def normalize(series):
        min_val = series.min()
        max_val = series.max()
        if max_val == min_val:
            return pd.Series([50] * len(series), index=series.index)
        return (series - min_val) / (max_val - min_val) * 100
    
    # 收入评分 (40%) - 使用对数变换，强调商业规模
    log_revenue = np.log10(df['Revenue (Absolute)'].clip(lower=1))
    revenue_score = normalize(log_revenue) * 0.40
    
    # ARPU评分 (25%) - 转化效率
    arpu_score = normalize(df['ARPU']) * 0.25
    
    # 增长率评分 (15%) - 市场验证
    growth_score = normalize(df['Growth Rate']) * 0.15
    
    # DAU评分 (20%) - 用户活跃度（说明产品有粘性）
    log_dau = np.log10(df['DAU (Absolute)'].fillna(1).clip(lower=1))
    dau_score = normalize(log_dau) * 0.20
    
    df['Score'] = revenue_score + arpu_score + growth_score + dau_score
    
    # 对收入低于门槛的产品大幅降权（这些产品参考价值有限）
    df.loc[~df['Valid'], 'Score'] = df.loc[~df['Valid'], 'Score'] * 0.2
    
    return df

def assign_priority(score):
    """根据评分分配优先级"""
    if score >= 70:
        return "P0"
    elif score >= 50:
        return "P1"
    else:
        return "P2"

def process_data():
    """主处理流程"""
    print("\n" + "="*60)
    print("  竞品数据处理")
    print("="*60)
    
    # Step 1: 加载数据
    print("\n[Step 1] 加载CSV文件...")
    dfs = {}
    for key, filepath in FILES.items():
        if filepath.exists():
            dfs[key] = load_csv(filepath)
        else:
            print(f"  Warning: {filepath} not found")
    
    # Step 2: 处理Nutrition分榜数据
    print("\n[Step 2] 处理 Nutrition 分榜...")
    if 'nutrition_revenue' in dfs:
        nutrition_df = dfs['nutrition_revenue'].copy()
        nutrition_df = aggregate_by_app(nutrition_df)
        nutrition_df = calculate_metrics(nutrition_df)
        nutrition_df = calculate_score(nutrition_df)
        nutrition_df['Priority'] = nutrition_df['Score'].apply(assign_priority)
        nutrition_df = nutrition_df.sort_values('Score', ascending=False)
        print(f"    -> {len(nutrition_df)} unique apps")
    
    # Step 3: 处理总榜数据（只取Health & Fitness）
    print("\n[Step 3] 处理总榜 (Health & Fitness)...")
    if 'total_revenue' in dfs:
        total_df = dfs['total_revenue'].copy()
        # 筛选Health & Fitness
        health_df = total_df[total_df['Category'] == 'Health & Fitness'].copy()
        health_df = aggregate_by_app(health_df)
        health_df = calculate_metrics(health_df)
        health_df = calculate_score(health_df)
        health_df['Priority'] = health_df['Score'].apply(assign_priority)
        health_df = health_df.sort_values('Score', ascending=False)
        print(f"    -> {len(health_df)} unique Health & Fitness apps")
    
    # Step 4: 生成Top 30清单
    print("\n[Step 4] 生成 Top 30 必研究清单...")
    
    # 策略：确保头部产品（收入Top 10）+ 高效率产品（ARPU高）+ 高增长产品
    
    # 从Nutrition分榜取：
    # - 收入Top 10
    nutrition_by_revenue = nutrition_df.nlargest(10, 'Revenue (Absolute)').copy()
    # - 评分Top 15（去重）
    nutrition_by_score = nutrition_df[~nutrition_df['App ID'].isin(nutrition_by_revenue['App ID'])].head(10).copy()
    nutrition_combined = pd.concat([nutrition_by_revenue, nutrition_by_score])
    nutrition_combined['Source'] = 'Nutrition'
    
    # 从总榜补充跨赛道标杆（如Calm, Strava, Flo等）
    nutrition_app_ids = set(nutrition_combined['App ID'].tolist())
    # 先按收入排序，取收入Top 10的非Nutrition产品
    health_by_revenue = health_df[~health_df['App ID'].isin(nutrition_app_ids)].nlargest(10, 'Revenue (Absolute)').copy()
    health_by_revenue['Source'] = 'Health_Total'
    
    # 合并
    top30_df = pd.concat([nutrition_combined, health_by_revenue], ignore_index=True)
    top30_df = top30_df.sort_values('Score', ascending=False).head(30)
    top30_df['Rank'] = range(1, len(top30_df) + 1)
    
    # Step 5: 整理输出字段
    print("\n[Step 5] 整理输出...")
    
    output_columns = [
        'Rank', 'Unified Name', 'Unified Publisher Name', 'Category',
        'Revenue (Absolute)', 'Downloads (Absolute)', 'ARPU',
        'Growth Rate', 'DAU (Absolute)', 'Score', 'Priority', 'Source'
    ]
    
    top30_output = top30_df[output_columns].copy()
    top30_output.columns = [
        'rank', 'app_name', 'publisher', 'category',
        'revenue', 'downloads', 'arpu',
        'growth_rate', 'dau', 'score', 'priority', 'source'
    ]
    
    # 格式化数字
    top30_output['revenue'] = top30_output['revenue'].round(0).astype(int)
    top30_output['downloads'] = top30_output['downloads'].round(0).astype(int)
    top30_output['arpu'] = top30_output['arpu'].round(2)
    top30_output['growth_rate'] = (top30_output['growth_rate'] * 100).round(1)  # 转为百分比
    top30_output['dau'] = top30_output['dau'].fillna(0).round(0).astype(int)
    top30_output['score'] = top30_output['score'].round(1)
    
    # Step 6: 保存文件
    print("\n[Step 6] 保存输出文件...")
    
    # 确保输出目录存在
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # 保存Top 30 CSV
    top30_csv = OUTPUT_DIR / "top30_must_study.csv"
    top30_output.to_csv(top30_csv, index=False, encoding='utf-8-sig')
    print(f"  -> {top30_csv}")
    
    # 保存完整Nutrition分榜
    nutrition_csv = OUTPUT_DIR / "nutrition_competitors.csv"
    nutrition_cols = [
        'Unified Name', 'Unified Publisher Name', 'Category',
        'Revenue (Absolute)', 'Downloads (Absolute)', 'ARPU',
        'Growth Rate', 'DAU (Absolute)', 'Score', 'Priority'
    ]
    nutrition_output = nutrition_df[nutrition_cols].copy()
    nutrition_output.columns = [
        'app_name', 'publisher', 'category',
        'revenue', 'downloads', 'arpu',
        'growth_rate', 'dau', 'score', 'priority'
    ]
    nutrition_output['source'] = 'Nutrition'
    nutrition_output.to_csv(nutrition_csv, index=False, encoding='utf-8-sig')
    print(f"  -> {nutrition_csv}")
    
    # 保存JSON数据库
    competitors_json = OUTPUT_DIR / "competitors.json"
    
    # 合并所有数据
    all_data = {
        "metadata": {
            "source": "Sensor Tower",
            "date_range": "Nov 11, 2025 - Dec 10, 2025",
            "regions": ["US", "AU", "CA", "FR", "DE", "+2 others"],
            "total_nutrition_apps": len(nutrition_df),
            "total_health_apps": len(health_df),
        },
        "top30": top30_output.to_dict(orient='records'),
        "nutrition_all": nutrition_df[[
            'App ID', 'Unified Name', 'Revenue (Absolute)', 
            'Downloads (Absolute)', 'ARPU', 'Growth Rate', 'Score', 'Priority'
        ]].head(50).to_dict(orient='records'),
    }
    
    with open(competitors_json, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    print(f"  -> {competitors_json}")
    
    # Step 7: 打印摘要
    print("\n" + "="*60)
    print("  Done!")
    print("="*60)
    
    print("\n[Top 30 Must Study List]")
    print("-" * 90)
    print(f"{'Rank':<5} {'App Name':<35} {'Revenue':>12} {'ARPU':>8} {'Growth':>8} {'Priority':<8}")
    print("-" * 90)
    
    for _, row in top30_output.iterrows():
        name = row['app_name'][:33] if len(str(row['app_name'])) > 33 else row['app_name']
        revenue = f"${row['revenue']:,}"
        arpu = f"${row['arpu']:.2f}"
        growth = f"{row['growth_rate']:+.1f}%"
        print(f"{row['rank']:<5} {name:<35} {revenue:>12} {arpu:>8} {growth:>8} {row['priority']:<8}")
    
    print("-" * 90)
    p0_count = len(top30_output[top30_output['priority']=='P0'])
    p1_count = len(top30_output[top30_output['priority']=='P1'])
    p2_count = len(top30_output[top30_output['priority']=='P2'])
    print(f"\nP0 (High Priority): {p0_count}")
    print(f"P1 (Medium Priority): {p1_count}")
    print(f"P2 (Low Priority): {p2_count}")
    
    return top30_output

if __name__ == "__main__":
    process_data()


竞品数据处理脚本
从Sensor Tower CSV文件中提取、清洗、分析数据
生成精选的"必研究竞品清单"
"""

import pandas as pd
import json
import os
from pathlib import Path

# 配置
INPUT_DIR = Path(r"C:\Users\WIN\Downloads\1")
OUTPUT_DIR = Path(__file__).parent

# CSV文件路径
FILES = {
    "total_revenue": INPUT_DIR / "App Store 应用排行榜 收入  (Nov 11, 2025 - Dec 10, 2025, US, AU, CA, FR, DE + 2 其他), 详细.csv",
    "nutrition_revenue": INPUT_DIR / "App Store 应用排行榜 收入  (Nov 11, 2025 - Dec 10, 2025, US, AU, CA, FR, DE + 2 其他), 详细 (1).csv",
    "total_growth": INPUT_DIR / "App Store 应用排行榜 收入 PoP 增长 (Nov 11, 2025 - Dec 10, 2025, US, AU, CA, FR, DE + 2 其他), 详细.csv",
    "nutrition_growth": INPUT_DIR / "App Store 应用排行榜 收入 PoP 增长 (Nov 11, 2025 - Dec 10, 2025, US, AU, CA, FR, DE + 2 其他), 详细 (1).csv",
}

def load_csv(filepath):
    """加载CSV文件"""
    print(f"  Loading: {filepath.name}")
    # 尝试不同的编码
    encodings = ['utf-16', 'utf-16-le', 'utf-8-sig', 'utf-8', 'gbk', 'latin1']
    for enc in encodings:
        try:
            df = pd.read_csv(filepath, sep='\t', encoding=enc)
            print(f"    -> {len(df)} rows (encoding: {enc})")
            return df
        except (UnicodeDecodeError, UnicodeError):
            continue
    raise ValueError(f"Could not decode file: {filepath}")

def aggregate_by_app(df):
    """按App汇总数据（原始数据是每日记录）"""
    # 汇总字段
    agg_dict = {
        'Unified Name': 'first',
        'Unified Publisher Name': 'first',
        'Category': 'first',
        'Downloads (Absolute)': 'sum',
        'Downloads (PoP Growth)': 'sum',
        'Revenue (Absolute)': 'sum',
        'Revenue (PoP Growth)': 'sum',
        'DAU (Absolute)': 'mean',  # DAU取平均值
    }
    
    # 按App ID分组汇总
    grouped = df.groupby('App ID').agg(agg_dict).reset_index()
    return grouped

def calculate_metrics(df):
    """计算关键指标"""
    # ARPU = 收入 / 下载
    df['ARPU'] = df['Revenue (Absolute)'] / df['Downloads (Absolute)'].replace(0, 1)
    
    # 收入增长率
    base_revenue = df['Revenue (Absolute)'] - df['Revenue (PoP Growth)']
    df['Growth Rate'] = df['Revenue (PoP Growth)'] / base_revenue.replace(0, 1)
    
    # 清理异常值 - 使用更合理的上限
    df['ARPU'] = df['ARPU'].clip(0, 50)  # ARPU上限50（合理范围）
    df['Growth Rate'] = df['Growth Rate'].clip(-1, 2)  # 增长率上限200%
    
    return df

def calculate_score(df):
    """计算综合评分 - 优化版本，强调商业规模"""
    import numpy as np
    
    # 收入门槛：$100,000（月收入10万美元以上才有研究价值）
    MIN_REVENUE = 100000
    df['Valid'] = df['Revenue (Absolute)'] >= MIN_REVENUE
    
    # 归一化函数
    def normalize(series):
        min_val = series.min()
        max_val = series.max()
        if max_val == min_val:
            return pd.Series([50] * len(series), index=series.index)
        return (series - min_val) / (max_val - min_val) * 100
    
    # 收入评分 (40%) - 使用对数变换，强调商业规模
    log_revenue = np.log10(df['Revenue (Absolute)'].clip(lower=1))
    revenue_score = normalize(log_revenue) * 0.40
    
    # ARPU评分 (25%) - 转化效率
    arpu_score = normalize(df['ARPU']) * 0.25
    
    # 增长率评分 (15%) - 市场验证
    growth_score = normalize(df['Growth Rate']) * 0.15
    
    # DAU评分 (20%) - 用户活跃度（说明产品有粘性）
    log_dau = np.log10(df['DAU (Absolute)'].fillna(1).clip(lower=1))
    dau_score = normalize(log_dau) * 0.20
    
    df['Score'] = revenue_score + arpu_score + growth_score + dau_score
    
    # 对收入低于门槛的产品大幅降权（这些产品参考价值有限）
    df.loc[~df['Valid'], 'Score'] = df.loc[~df['Valid'], 'Score'] * 0.2
    
    return df

def assign_priority(score):
    """根据评分分配优先级"""
    if score >= 70:
        return "P0"
    elif score >= 50:
        return "P1"
    else:
        return "P2"

def process_data():
    """主处理流程"""
    print("\n" + "="*60)
    print("  竞品数据处理")
    print("="*60)
    
    # Step 1: 加载数据
    print("\n[Step 1] 加载CSV文件...")
    dfs = {}
    for key, filepath in FILES.items():
        if filepath.exists():
            dfs[key] = load_csv(filepath)
        else:
            print(f"  Warning: {filepath} not found")
    
    # Step 2: 处理Nutrition分榜数据
    print("\n[Step 2] 处理 Nutrition 分榜...")
    if 'nutrition_revenue' in dfs:
        nutrition_df = dfs['nutrition_revenue'].copy()
        nutrition_df = aggregate_by_app(nutrition_df)
        nutrition_df = calculate_metrics(nutrition_df)
        nutrition_df = calculate_score(nutrition_df)
        nutrition_df['Priority'] = nutrition_df['Score'].apply(assign_priority)
        nutrition_df = nutrition_df.sort_values('Score', ascending=False)
        print(f"    -> {len(nutrition_df)} unique apps")
    
    # Step 3: 处理总榜数据（只取Health & Fitness）
    print("\n[Step 3] 处理总榜 (Health & Fitness)...")
    if 'total_revenue' in dfs:
        total_df = dfs['total_revenue'].copy()
        # 筛选Health & Fitness
        health_df = total_df[total_df['Category'] == 'Health & Fitness'].copy()
        health_df = aggregate_by_app(health_df)
        health_df = calculate_metrics(health_df)
        health_df = calculate_score(health_df)
        health_df['Priority'] = health_df['Score'].apply(assign_priority)
        health_df = health_df.sort_values('Score', ascending=False)
        print(f"    -> {len(health_df)} unique Health & Fitness apps")
    
    # Step 4: 生成Top 30清单
    print("\n[Step 4] 生成 Top 30 必研究清单...")
    
    # 策略：确保头部产品（收入Top 10）+ 高效率产品（ARPU高）+ 高增长产品
    
    # 从Nutrition分榜取：
    # - 收入Top 10
    nutrition_by_revenue = nutrition_df.nlargest(10, 'Revenue (Absolute)').copy()
    # - 评分Top 15（去重）
    nutrition_by_score = nutrition_df[~nutrition_df['App ID'].isin(nutrition_by_revenue['App ID'])].head(10).copy()
    nutrition_combined = pd.concat([nutrition_by_revenue, nutrition_by_score])
    nutrition_combined['Source'] = 'Nutrition'
    
    # 从总榜补充跨赛道标杆（如Calm, Strava, Flo等）
    nutrition_app_ids = set(nutrition_combined['App ID'].tolist())
    # 先按收入排序，取收入Top 10的非Nutrition产品
    health_by_revenue = health_df[~health_df['App ID'].isin(nutrition_app_ids)].nlargest(10, 'Revenue (Absolute)').copy()
    health_by_revenue['Source'] = 'Health_Total'
    
    # 合并
    top30_df = pd.concat([nutrition_combined, health_by_revenue], ignore_index=True)
    top30_df = top30_df.sort_values('Score', ascending=False).head(30)
    top30_df['Rank'] = range(1, len(top30_df) + 1)
    
    # Step 5: 整理输出字段
    print("\n[Step 5] 整理输出...")
    
    output_columns = [
        'Rank', 'Unified Name', 'Unified Publisher Name', 'Category',
        'Revenue (Absolute)', 'Downloads (Absolute)', 'ARPU',
        'Growth Rate', 'DAU (Absolute)', 'Score', 'Priority', 'Source'
    ]
    
    top30_output = top30_df[output_columns].copy()
    top30_output.columns = [
        'rank', 'app_name', 'publisher', 'category',
        'revenue', 'downloads', 'arpu',
        'growth_rate', 'dau', 'score', 'priority', 'source'
    ]
    
    # 格式化数字
    top30_output['revenue'] = top30_output['revenue'].round(0).astype(int)
    top30_output['downloads'] = top30_output['downloads'].round(0).astype(int)
    top30_output['arpu'] = top30_output['arpu'].round(2)
    top30_output['growth_rate'] = (top30_output['growth_rate'] * 100).round(1)  # 转为百分比
    top30_output['dau'] = top30_output['dau'].fillna(0).round(0).astype(int)
    top30_output['score'] = top30_output['score'].round(1)
    
    # Step 6: 保存文件
    print("\n[Step 6] 保存输出文件...")
    
    # 确保输出目录存在
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # 保存Top 30 CSV
    top30_csv = OUTPUT_DIR / "top30_must_study.csv"
    top30_output.to_csv(top30_csv, index=False, encoding='utf-8-sig')
    print(f"  -> {top30_csv}")
    
    # 保存完整Nutrition分榜
    nutrition_csv = OUTPUT_DIR / "nutrition_competitors.csv"
    nutrition_cols = [
        'Unified Name', 'Unified Publisher Name', 'Category',
        'Revenue (Absolute)', 'Downloads (Absolute)', 'ARPU',
        'Growth Rate', 'DAU (Absolute)', 'Score', 'Priority'
    ]
    nutrition_output = nutrition_df[nutrition_cols].copy()
    nutrition_output.columns = [
        'app_name', 'publisher', 'category',
        'revenue', 'downloads', 'arpu',
        'growth_rate', 'dau', 'score', 'priority'
    ]
    nutrition_output['source'] = 'Nutrition'
    nutrition_output.to_csv(nutrition_csv, index=False, encoding='utf-8-sig')
    print(f"  -> {nutrition_csv}")
    
    # 保存JSON数据库
    competitors_json = OUTPUT_DIR / "competitors.json"
    
    # 合并所有数据
    all_data = {
        "metadata": {
            "source": "Sensor Tower",
            "date_range": "Nov 11, 2025 - Dec 10, 2025",
            "regions": ["US", "AU", "CA", "FR", "DE", "+2 others"],
            "total_nutrition_apps": len(nutrition_df),
            "total_health_apps": len(health_df),
        },
        "top30": top30_output.to_dict(orient='records'),
        "nutrition_all": nutrition_df[[
            'App ID', 'Unified Name', 'Revenue (Absolute)', 
            'Downloads (Absolute)', 'ARPU', 'Growth Rate', 'Score', 'Priority'
        ]].head(50).to_dict(orient='records'),
    }
    
    with open(competitors_json, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    print(f"  -> {competitors_json}")
    
    # Step 7: 打印摘要
    print("\n" + "="*60)
    print("  Done!")
    print("="*60)
    
    print("\n[Top 30 Must Study List]")
    print("-" * 90)
    print(f"{'Rank':<5} {'App Name':<35} {'Revenue':>12} {'ARPU':>8} {'Growth':>8} {'Priority':<8}")
    print("-" * 90)
    
    for _, row in top30_output.iterrows():
        name = row['app_name'][:33] if len(str(row['app_name'])) > 33 else row['app_name']
        revenue = f"${row['revenue']:,}"
        arpu = f"${row['arpu']:.2f}"
        growth = f"{row['growth_rate']:+.1f}%"
        print(f"{row['rank']:<5} {name:<35} {revenue:>12} {arpu:>8} {growth:>8} {row['priority']:<8}")
    
    print("-" * 90)
    p0_count = len(top30_output[top30_output['priority']=='P0'])
    p1_count = len(top30_output[top30_output['priority']=='P1'])
    p2_count = len(top30_output[top30_output['priority']=='P2'])
    print(f"\nP0 (High Priority): {p0_count}")
    print(f"P1 (Medium Priority): {p1_count}")
    print(f"P2 (Low Priority): {p2_count}")
    
    return top30_output

if __name__ == "__main__":
    process_data()


竞品数据处理脚本
从Sensor Tower CSV文件中提取、清洗、分析数据
生成精选的"必研究竞品清单"
"""

import pandas as pd
import json
import os
from pathlib import Path

# 配置
INPUT_DIR = Path(r"C:\Users\WIN\Downloads\1")
OUTPUT_DIR = Path(__file__).parent

# CSV文件路径
FILES = {
    "total_revenue": INPUT_DIR / "App Store 应用排行榜 收入  (Nov 11, 2025 - Dec 10, 2025, US, AU, CA, FR, DE + 2 其他), 详细.csv",
    "nutrition_revenue": INPUT_DIR / "App Store 应用排行榜 收入  (Nov 11, 2025 - Dec 10, 2025, US, AU, CA, FR, DE + 2 其他), 详细 (1).csv",
    "total_growth": INPUT_DIR / "App Store 应用排行榜 收入 PoP 增长 (Nov 11, 2025 - Dec 10, 2025, US, AU, CA, FR, DE + 2 其他), 详细.csv",
    "nutrition_growth": INPUT_DIR / "App Store 应用排行榜 收入 PoP 增长 (Nov 11, 2025 - Dec 10, 2025, US, AU, CA, FR, DE + 2 其他), 详细 (1).csv",
}

def load_csv(filepath):
    """加载CSV文件"""
    print(f"  Loading: {filepath.name}")
    # 尝试不同的编码
    encodings = ['utf-16', 'utf-16-le', 'utf-8-sig', 'utf-8', 'gbk', 'latin1']
    for enc in encodings:
        try:
            df = pd.read_csv(filepath, sep='\t', encoding=enc)
            print(f"    -> {len(df)} rows (encoding: {enc})")
            return df
        except (UnicodeDecodeError, UnicodeError):
            continue
    raise ValueError(f"Could not decode file: {filepath}")

def aggregate_by_app(df):
    """按App汇总数据（原始数据是每日记录）"""
    # 汇总字段
    agg_dict = {
        'Unified Name': 'first',
        'Unified Publisher Name': 'first',
        'Category': 'first',
        'Downloads (Absolute)': 'sum',
        'Downloads (PoP Growth)': 'sum',
        'Revenue (Absolute)': 'sum',
        'Revenue (PoP Growth)': 'sum',
        'DAU (Absolute)': 'mean',  # DAU取平均值
    }
    
    # 按App ID分组汇总
    grouped = df.groupby('App ID').agg(agg_dict).reset_index()
    return grouped

def calculate_metrics(df):
    """计算关键指标"""
    # ARPU = 收入 / 下载
    df['ARPU'] = df['Revenue (Absolute)'] / df['Downloads (Absolute)'].replace(0, 1)
    
    # 收入增长率
    base_revenue = df['Revenue (Absolute)'] - df['Revenue (PoP Growth)']
    df['Growth Rate'] = df['Revenue (PoP Growth)'] / base_revenue.replace(0, 1)
    
    # 清理异常值 - 使用更合理的上限
    df['ARPU'] = df['ARPU'].clip(0, 50)  # ARPU上限50（合理范围）
    df['Growth Rate'] = df['Growth Rate'].clip(-1, 2)  # 增长率上限200%
    
    return df

def calculate_score(df):
    """计算综合评分 - 优化版本，强调商业规模"""
    import numpy as np
    
    # 收入门槛：$100,000（月收入10万美元以上才有研究价值）
    MIN_REVENUE = 100000
    df['Valid'] = df['Revenue (Absolute)'] >= MIN_REVENUE
    
    # 归一化函数
    def normalize(series):
        min_val = series.min()
        max_val = series.max()
        if max_val == min_val:
            return pd.Series([50] * len(series), index=series.index)
        return (series - min_val) / (max_val - min_val) * 100
    
    # 收入评分 (40%) - 使用对数变换，强调商业规模
    log_revenue = np.log10(df['Revenue (Absolute)'].clip(lower=1))
    revenue_score = normalize(log_revenue) * 0.40
    
    # ARPU评分 (25%) - 转化效率
    arpu_score = normalize(df['ARPU']) * 0.25
    
    # 增长率评分 (15%) - 市场验证
    growth_score = normalize(df['Growth Rate']) * 0.15
    
    # DAU评分 (20%) - 用户活跃度（说明产品有粘性）
    log_dau = np.log10(df['DAU (Absolute)'].fillna(1).clip(lower=1))
    dau_score = normalize(log_dau) * 0.20
    
    df['Score'] = revenue_score + arpu_score + growth_score + dau_score
    
    # 对收入低于门槛的产品大幅降权（这些产品参考价值有限）
    df.loc[~df['Valid'], 'Score'] = df.loc[~df['Valid'], 'Score'] * 0.2
    
    return df

def assign_priority(score):
    """根据评分分配优先级"""
    if score >= 70:
        return "P0"
    elif score >= 50:
        return "P1"
    else:
        return "P2"

def process_data():
    """主处理流程"""
    print("\n" + "="*60)
    print("  竞品数据处理")
    print("="*60)
    
    # Step 1: 加载数据
    print("\n[Step 1] 加载CSV文件...")
    dfs = {}
    for key, filepath in FILES.items():
        if filepath.exists():
            dfs[key] = load_csv(filepath)
        else:
            print(f"  Warning: {filepath} not found")
    
    # Step 2: 处理Nutrition分榜数据
    print("\n[Step 2] 处理 Nutrition 分榜...")
    if 'nutrition_revenue' in dfs:
        nutrition_df = dfs['nutrition_revenue'].copy()
        nutrition_df = aggregate_by_app(nutrition_df)
        nutrition_df = calculate_metrics(nutrition_df)
        nutrition_df = calculate_score(nutrition_df)
        nutrition_df['Priority'] = nutrition_df['Score'].apply(assign_priority)
        nutrition_df = nutrition_df.sort_values('Score', ascending=False)
        print(f"    -> {len(nutrition_df)} unique apps")
    
    # Step 3: 处理总榜数据（只取Health & Fitness）
    print("\n[Step 3] 处理总榜 (Health & Fitness)...")
    if 'total_revenue' in dfs:
        total_df = dfs['total_revenue'].copy()
        # 筛选Health & Fitness
        health_df = total_df[total_df['Category'] == 'Health & Fitness'].copy()
        health_df = aggregate_by_app(health_df)
        health_df = calculate_metrics(health_df)
        health_df = calculate_score(health_df)
        health_df['Priority'] = health_df['Score'].apply(assign_priority)
        health_df = health_df.sort_values('Score', ascending=False)
        print(f"    -> {len(health_df)} unique Health & Fitness apps")
    
    # Step 4: 生成Top 30清单
    print("\n[Step 4] 生成 Top 30 必研究清单...")
    
    # 策略：确保头部产品（收入Top 10）+ 高效率产品（ARPU高）+ 高增长产品
    
    # 从Nutrition分榜取：
    # - 收入Top 10
    nutrition_by_revenue = nutrition_df.nlargest(10, 'Revenue (Absolute)').copy()
    # - 评分Top 15（去重）
    nutrition_by_score = nutrition_df[~nutrition_df['App ID'].isin(nutrition_by_revenue['App ID'])].head(10).copy()
    nutrition_combined = pd.concat([nutrition_by_revenue, nutrition_by_score])
    nutrition_combined['Source'] = 'Nutrition'
    
    # 从总榜补充跨赛道标杆（如Calm, Strava, Flo等）
    nutrition_app_ids = set(nutrition_combined['App ID'].tolist())
    # 先按收入排序，取收入Top 10的非Nutrition产品
    health_by_revenue = health_df[~health_df['App ID'].isin(nutrition_app_ids)].nlargest(10, 'Revenue (Absolute)').copy()
    health_by_revenue['Source'] = 'Health_Total'
    
    # 合并
    top30_df = pd.concat([nutrition_combined, health_by_revenue], ignore_index=True)
    top30_df = top30_df.sort_values('Score', ascending=False).head(30)
    top30_df['Rank'] = range(1, len(top30_df) + 1)
    
    # Step 5: 整理输出字段
    print("\n[Step 5] 整理输出...")
    
    output_columns = [
        'Rank', 'Unified Name', 'Unified Publisher Name', 'Category',
        'Revenue (Absolute)', 'Downloads (Absolute)', 'ARPU',
        'Growth Rate', 'DAU (Absolute)', 'Score', 'Priority', 'Source'
    ]
    
    top30_output = top30_df[output_columns].copy()
    top30_output.columns = [
        'rank', 'app_name', 'publisher', 'category',
        'revenue', 'downloads', 'arpu',
        'growth_rate', 'dau', 'score', 'priority', 'source'
    ]
    
    # 格式化数字
    top30_output['revenue'] = top30_output['revenue'].round(0).astype(int)
    top30_output['downloads'] = top30_output['downloads'].round(0).astype(int)
    top30_output['arpu'] = top30_output['arpu'].round(2)
    top30_output['growth_rate'] = (top30_output['growth_rate'] * 100).round(1)  # 转为百分比
    top30_output['dau'] = top30_output['dau'].fillna(0).round(0).astype(int)
    top30_output['score'] = top30_output['score'].round(1)
    
    # Step 6: 保存文件
    print("\n[Step 6] 保存输出文件...")
    
    # 确保输出目录存在
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # 保存Top 30 CSV
    top30_csv = OUTPUT_DIR / "top30_must_study.csv"
    top30_output.to_csv(top30_csv, index=False, encoding='utf-8-sig')
    print(f"  -> {top30_csv}")
    
    # 保存完整Nutrition分榜
    nutrition_csv = OUTPUT_DIR / "nutrition_competitors.csv"
    nutrition_cols = [
        'Unified Name', 'Unified Publisher Name', 'Category',
        'Revenue (Absolute)', 'Downloads (Absolute)', 'ARPU',
        'Growth Rate', 'DAU (Absolute)', 'Score', 'Priority'
    ]
    nutrition_output = nutrition_df[nutrition_cols].copy()
    nutrition_output.columns = [
        'app_name', 'publisher', 'category',
        'revenue', 'downloads', 'arpu',
        'growth_rate', 'dau', 'score', 'priority'
    ]
    nutrition_output['source'] = 'Nutrition'
    nutrition_output.to_csv(nutrition_csv, index=False, encoding='utf-8-sig')
    print(f"  -> {nutrition_csv}")
    
    # 保存JSON数据库
    competitors_json = OUTPUT_DIR / "competitors.json"
    
    # 合并所有数据
    all_data = {
        "metadata": {
            "source": "Sensor Tower",
            "date_range": "Nov 11, 2025 - Dec 10, 2025",
            "regions": ["US", "AU", "CA", "FR", "DE", "+2 others"],
            "total_nutrition_apps": len(nutrition_df),
            "total_health_apps": len(health_df),
        },
        "top30": top30_output.to_dict(orient='records'),
        "nutrition_all": nutrition_df[[
            'App ID', 'Unified Name', 'Revenue (Absolute)', 
            'Downloads (Absolute)', 'ARPU', 'Growth Rate', 'Score', 'Priority'
        ]].head(50).to_dict(orient='records'),
    }
    
    with open(competitors_json, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    print(f"  -> {competitors_json}")
    
    # Step 7: 打印摘要
    print("\n" + "="*60)
    print("  Done!")
    print("="*60)
    
    print("\n[Top 30 Must Study List]")
    print("-" * 90)
    print(f"{'Rank':<5} {'App Name':<35} {'Revenue':>12} {'ARPU':>8} {'Growth':>8} {'Priority':<8}")
    print("-" * 90)
    
    for _, row in top30_output.iterrows():
        name = row['app_name'][:33] if len(str(row['app_name'])) > 33 else row['app_name']
        revenue = f"${row['revenue']:,}"
        arpu = f"${row['arpu']:.2f}"
        growth = f"{row['growth_rate']:+.1f}%"
        print(f"{row['rank']:<5} {name:<35} {revenue:>12} {arpu:>8} {growth:>8} {row['priority']:<8}")
    
    print("-" * 90)
    p0_count = len(top30_output[top30_output['priority']=='P0'])
    p1_count = len(top30_output[top30_output['priority']=='P1'])
    p2_count = len(top30_output[top30_output['priority']=='P2'])
    print(f"\nP0 (High Priority): {p0_count}")
    print(f"P1 (Medium Priority): {p1_count}")
    print(f"P2 (Low Priority): {p2_count}")
    
    return top30_output

if __name__ == "__main__":
    process_data()


竞品数据处理脚本
从Sensor Tower CSV文件中提取、清洗、分析数据
生成精选的"必研究竞品清单"
"""

import pandas as pd
import json
import os
from pathlib import Path

# 配置
INPUT_DIR = Path(r"C:\Users\WIN\Downloads\1")
OUTPUT_DIR = Path(__file__).parent

# CSV文件路径
FILES = {
    "total_revenue": INPUT_DIR / "App Store 应用排行榜 收入  (Nov 11, 2025 - Dec 10, 2025, US, AU, CA, FR, DE + 2 其他), 详细.csv",
    "nutrition_revenue": INPUT_DIR / "App Store 应用排行榜 收入  (Nov 11, 2025 - Dec 10, 2025, US, AU, CA, FR, DE + 2 其他), 详细 (1).csv",
    "total_growth": INPUT_DIR / "App Store 应用排行榜 收入 PoP 增长 (Nov 11, 2025 - Dec 10, 2025, US, AU, CA, FR, DE + 2 其他), 详细.csv",
    "nutrition_growth": INPUT_DIR / "App Store 应用排行榜 收入 PoP 增长 (Nov 11, 2025 - Dec 10, 2025, US, AU, CA, FR, DE + 2 其他), 详细 (1).csv",
}

def load_csv(filepath):
    """加载CSV文件"""
    print(f"  Loading: {filepath.name}")
    # 尝试不同的编码
    encodings = ['utf-16', 'utf-16-le', 'utf-8-sig', 'utf-8', 'gbk', 'latin1']
    for enc in encodings:
        try:
            df = pd.read_csv(filepath, sep='\t', encoding=enc)
            print(f"    -> {len(df)} rows (encoding: {enc})")
            return df
        except (UnicodeDecodeError, UnicodeError):
            continue
    raise ValueError(f"Could not decode file: {filepath}")

def aggregate_by_app(df):
    """按App汇总数据（原始数据是每日记录）"""
    # 汇总字段
    agg_dict = {
        'Unified Name': 'first',
        'Unified Publisher Name': 'first',
        'Category': 'first',
        'Downloads (Absolute)': 'sum',
        'Downloads (PoP Growth)': 'sum',
        'Revenue (Absolute)': 'sum',
        'Revenue (PoP Growth)': 'sum',
        'DAU (Absolute)': 'mean',  # DAU取平均值
    }
    
    # 按App ID分组汇总
    grouped = df.groupby('App ID').agg(agg_dict).reset_index()
    return grouped

def calculate_metrics(df):
    """计算关键指标"""
    # ARPU = 收入 / 下载
    df['ARPU'] = df['Revenue (Absolute)'] / df['Downloads (Absolute)'].replace(0, 1)
    
    # 收入增长率
    base_revenue = df['Revenue (Absolute)'] - df['Revenue (PoP Growth)']
    df['Growth Rate'] = df['Revenue (PoP Growth)'] / base_revenue.replace(0, 1)
    
    # 清理异常值 - 使用更合理的上限
    df['ARPU'] = df['ARPU'].clip(0, 50)  # ARPU上限50（合理范围）
    df['Growth Rate'] = df['Growth Rate'].clip(-1, 2)  # 增长率上限200%
    
    return df

def calculate_score(df):
    """计算综合评分 - 优化版本，强调商业规模"""
    import numpy as np
    
    # 收入门槛：$100,000（月收入10万美元以上才有研究价值）
    MIN_REVENUE = 100000
    df['Valid'] = df['Revenue (Absolute)'] >= MIN_REVENUE
    
    # 归一化函数
    def normalize(series):
        min_val = series.min()
        max_val = series.max()
        if max_val == min_val:
            return pd.Series([50] * len(series), index=series.index)
        return (series - min_val) / (max_val - min_val) * 100
    
    # 收入评分 (40%) - 使用对数变换，强调商业规模
    log_revenue = np.log10(df['Revenue (Absolute)'].clip(lower=1))
    revenue_score = normalize(log_revenue) * 0.40
    
    # ARPU评分 (25%) - 转化效率
    arpu_score = normalize(df['ARPU']) * 0.25
    
    # 增长率评分 (15%) - 市场验证
    growth_score = normalize(df['Growth Rate']) * 0.15
    
    # DAU评分 (20%) - 用户活跃度（说明产品有粘性）
    log_dau = np.log10(df['DAU (Absolute)'].fillna(1).clip(lower=1))
    dau_score = normalize(log_dau) * 0.20
    
    df['Score'] = revenue_score + arpu_score + growth_score + dau_score
    
    # 对收入低于门槛的产品大幅降权（这些产品参考价值有限）
    df.loc[~df['Valid'], 'Score'] = df.loc[~df['Valid'], 'Score'] * 0.2
    
    return df

def assign_priority(score):
    """根据评分分配优先级"""
    if score >= 70:
        return "P0"
    elif score >= 50:
        return "P1"
    else:
        return "P2"

def process_data():
    """主处理流程"""
    print("\n" + "="*60)
    print("  竞品数据处理")
    print("="*60)
    
    # Step 1: 加载数据
    print("\n[Step 1] 加载CSV文件...")
    dfs = {}
    for key, filepath in FILES.items():
        if filepath.exists():
            dfs[key] = load_csv(filepath)
        else:
            print(f"  Warning: {filepath} not found")
    
    # Step 2: 处理Nutrition分榜数据
    print("\n[Step 2] 处理 Nutrition 分榜...")
    if 'nutrition_revenue' in dfs:
        nutrition_df = dfs['nutrition_revenue'].copy()
        nutrition_df = aggregate_by_app(nutrition_df)
        nutrition_df = calculate_metrics(nutrition_df)
        nutrition_df = calculate_score(nutrition_df)
        nutrition_df['Priority'] = nutrition_df['Score'].apply(assign_priority)
        nutrition_df = nutrition_df.sort_values('Score', ascending=False)
        print(f"    -> {len(nutrition_df)} unique apps")
    
    # Step 3: 处理总榜数据（只取Health & Fitness）
    print("\n[Step 3] 处理总榜 (Health & Fitness)...")
    if 'total_revenue' in dfs:
        total_df = dfs['total_revenue'].copy()
        # 筛选Health & Fitness
        health_df = total_df[total_df['Category'] == 'Health & Fitness'].copy()
        health_df = aggregate_by_app(health_df)
        health_df = calculate_metrics(health_df)
        health_df = calculate_score(health_df)
        health_df['Priority'] = health_df['Score'].apply(assign_priority)
        health_df = health_df.sort_values('Score', ascending=False)
        print(f"    -> {len(health_df)} unique Health & Fitness apps")
    
    # Step 4: 生成Top 30清单
    print("\n[Step 4] 生成 Top 30 必研究清单...")
    
    # 策略：确保头部产品（收入Top 10）+ 高效率产品（ARPU高）+ 高增长产品
    
    # 从Nutrition分榜取：
    # - 收入Top 10
    nutrition_by_revenue = nutrition_df.nlargest(10, 'Revenue (Absolute)').copy()
    # - 评分Top 15（去重）
    nutrition_by_score = nutrition_df[~nutrition_df['App ID'].isin(nutrition_by_revenue['App ID'])].head(10).copy()
    nutrition_combined = pd.concat([nutrition_by_revenue, nutrition_by_score])
    nutrition_combined['Source'] = 'Nutrition'
    
    # 从总榜补充跨赛道标杆（如Calm, Strava, Flo等）
    nutrition_app_ids = set(nutrition_combined['App ID'].tolist())
    # 先按收入排序，取收入Top 10的非Nutrition产品
    health_by_revenue = health_df[~health_df['App ID'].isin(nutrition_app_ids)].nlargest(10, 'Revenue (Absolute)').copy()
    health_by_revenue['Source'] = 'Health_Total'
    
    # 合并
    top30_df = pd.concat([nutrition_combined, health_by_revenue], ignore_index=True)
    top30_df = top30_df.sort_values('Score', ascending=False).head(30)
    top30_df['Rank'] = range(1, len(top30_df) + 1)
    
    # Step 5: 整理输出字段
    print("\n[Step 5] 整理输出...")
    
    output_columns = [
        'Rank', 'Unified Name', 'Unified Publisher Name', 'Category',
        'Revenue (Absolute)', 'Downloads (Absolute)', 'ARPU',
        'Growth Rate', 'DAU (Absolute)', 'Score', 'Priority', 'Source'
    ]
    
    top30_output = top30_df[output_columns].copy()
    top30_output.columns = [
        'rank', 'app_name', 'publisher', 'category',
        'revenue', 'downloads', 'arpu',
        'growth_rate', 'dau', 'score', 'priority', 'source'
    ]
    
    # 格式化数字
    top30_output['revenue'] = top30_output['revenue'].round(0).astype(int)
    top30_output['downloads'] = top30_output['downloads'].round(0).astype(int)
    top30_output['arpu'] = top30_output['arpu'].round(2)
    top30_output['growth_rate'] = (top30_output['growth_rate'] * 100).round(1)  # 转为百分比
    top30_output['dau'] = top30_output['dau'].fillna(0).round(0).astype(int)
    top30_output['score'] = top30_output['score'].round(1)
    
    # Step 6: 保存文件
    print("\n[Step 6] 保存输出文件...")
    
    # 确保输出目录存在
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # 保存Top 30 CSV
    top30_csv = OUTPUT_DIR / "top30_must_study.csv"
    top30_output.to_csv(top30_csv, index=False, encoding='utf-8-sig')
    print(f"  -> {top30_csv}")
    
    # 保存完整Nutrition分榜
    nutrition_csv = OUTPUT_DIR / "nutrition_competitors.csv"
    nutrition_cols = [
        'Unified Name', 'Unified Publisher Name', 'Category',
        'Revenue (Absolute)', 'Downloads (Absolute)', 'ARPU',
        'Growth Rate', 'DAU (Absolute)', 'Score', 'Priority'
    ]
    nutrition_output = nutrition_df[nutrition_cols].copy()
    nutrition_output.columns = [
        'app_name', 'publisher', 'category',
        'revenue', 'downloads', 'arpu',
        'growth_rate', 'dau', 'score', 'priority'
    ]
    nutrition_output['source'] = 'Nutrition'
    nutrition_output.to_csv(nutrition_csv, index=False, encoding='utf-8-sig')
    print(f"  -> {nutrition_csv}")
    
    # 保存JSON数据库
    competitors_json = OUTPUT_DIR / "competitors.json"
    
    # 合并所有数据
    all_data = {
        "metadata": {
            "source": "Sensor Tower",
            "date_range": "Nov 11, 2025 - Dec 10, 2025",
            "regions": ["US", "AU", "CA", "FR", "DE", "+2 others"],
            "total_nutrition_apps": len(nutrition_df),
            "total_health_apps": len(health_df),
        },
        "top30": top30_output.to_dict(orient='records'),
        "nutrition_all": nutrition_df[[
            'App ID', 'Unified Name', 'Revenue (Absolute)', 
            'Downloads (Absolute)', 'ARPU', 'Growth Rate', 'Score', 'Priority'
        ]].head(50).to_dict(orient='records'),
    }
    
    with open(competitors_json, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    print(f"  -> {competitors_json}")
    
    # Step 7: 打印摘要
    print("\n" + "="*60)
    print("  Done!")
    print("="*60)
    
    print("\n[Top 30 Must Study List]")
    print("-" * 90)
    print(f"{'Rank':<5} {'App Name':<35} {'Revenue':>12} {'ARPU':>8} {'Growth':>8} {'Priority':<8}")
    print("-" * 90)
    
    for _, row in top30_output.iterrows():
        name = row['app_name'][:33] if len(str(row['app_name'])) > 33 else row['app_name']
        revenue = f"${row['revenue']:,}"
        arpu = f"${row['arpu']:.2f}"
        growth = f"{row['growth_rate']:+.1f}%"
        print(f"{row['rank']:<5} {name:<35} {revenue:>12} {arpu:>8} {growth:>8} {row['priority']:<8}")
    
    print("-" * 90)
    p0_count = len(top30_output[top30_output['priority']=='P0'])
    p1_count = len(top30_output[top30_output['priority']=='P1'])
    p2_count = len(top30_output[top30_output['priority']=='P2'])
    print(f"\nP0 (High Priority): {p0_count}")
    print(f"P1 (Medium Priority): {p1_count}")
    print(f"P2 (Low Priority): {p2_count}")
    
    return top30_output

if __name__ == "__main__":
    process_data()


竞品数据处理脚本
从Sensor Tower CSV文件中提取、清洗、分析数据
生成精选的"必研究竞品清单"
"""

import pandas as pd
import json
import os
from pathlib import Path

# 配置
INPUT_DIR = Path(r"C:\Users\WIN\Downloads\1")
OUTPUT_DIR = Path(__file__).parent

# CSV文件路径
FILES = {
    "total_revenue": INPUT_DIR / "App Store 应用排行榜 收入  (Nov 11, 2025 - Dec 10, 2025, US, AU, CA, FR, DE + 2 其他), 详细.csv",
    "nutrition_revenue": INPUT_DIR / "App Store 应用排行榜 收入  (Nov 11, 2025 - Dec 10, 2025, US, AU, CA, FR, DE + 2 其他), 详细 (1).csv",
    "total_growth": INPUT_DIR / "App Store 应用排行榜 收入 PoP 增长 (Nov 11, 2025 - Dec 10, 2025, US, AU, CA, FR, DE + 2 其他), 详细.csv",
    "nutrition_growth": INPUT_DIR / "App Store 应用排行榜 收入 PoP 增长 (Nov 11, 2025 - Dec 10, 2025, US, AU, CA, FR, DE + 2 其他), 详细 (1).csv",
}

def load_csv(filepath):
    """加载CSV文件"""
    print(f"  Loading: {filepath.name}")
    # 尝试不同的编码
    encodings = ['utf-16', 'utf-16-le', 'utf-8-sig', 'utf-8', 'gbk', 'latin1']
    for enc in encodings:
        try:
            df = pd.read_csv(filepath, sep='\t', encoding=enc)
            print(f"    -> {len(df)} rows (encoding: {enc})")
            return df
        except (UnicodeDecodeError, UnicodeError):
            continue
    raise ValueError(f"Could not decode file: {filepath}")

def aggregate_by_app(df):
    """按App汇总数据（原始数据是每日记录）"""
    # 汇总字段
    agg_dict = {
        'Unified Name': 'first',
        'Unified Publisher Name': 'first',
        'Category': 'first',
        'Downloads (Absolute)': 'sum',
        'Downloads (PoP Growth)': 'sum',
        'Revenue (Absolute)': 'sum',
        'Revenue (PoP Growth)': 'sum',
        'DAU (Absolute)': 'mean',  # DAU取平均值
    }
    
    # 按App ID分组汇总
    grouped = df.groupby('App ID').agg(agg_dict).reset_index()
    return grouped

def calculate_metrics(df):
    """计算关键指标"""
    # ARPU = 收入 / 下载
    df['ARPU'] = df['Revenue (Absolute)'] / df['Downloads (Absolute)'].replace(0, 1)
    
    # 收入增长率
    base_revenue = df['Revenue (Absolute)'] - df['Revenue (PoP Growth)']
    df['Growth Rate'] = df['Revenue (PoP Growth)'] / base_revenue.replace(0, 1)
    
    # 清理异常值 - 使用更合理的上限
    df['ARPU'] = df['ARPU'].clip(0, 50)  # ARPU上限50（合理范围）
    df['Growth Rate'] = df['Growth Rate'].clip(-1, 2)  # 增长率上限200%
    
    return df

def calculate_score(df):
    """计算综合评分 - 优化版本，强调商业规模"""
    import numpy as np
    
    # 收入门槛：$100,000（月收入10万美元以上才有研究价值）
    MIN_REVENUE = 100000
    df['Valid'] = df['Revenue (Absolute)'] >= MIN_REVENUE
    
    # 归一化函数
    def normalize(series):
        min_val = series.min()
        max_val = series.max()
        if max_val == min_val:
            return pd.Series([50] * len(series), index=series.index)
        return (series - min_val) / (max_val - min_val) * 100
    
    # 收入评分 (40%) - 使用对数变换，强调商业规模
    log_revenue = np.log10(df['Revenue (Absolute)'].clip(lower=1))
    revenue_score = normalize(log_revenue) * 0.40
    
    # ARPU评分 (25%) - 转化效率
    arpu_score = normalize(df['ARPU']) * 0.25
    
    # 增长率评分 (15%) - 市场验证
    growth_score = normalize(df['Growth Rate']) * 0.15
    
    # DAU评分 (20%) - 用户活跃度（说明产品有粘性）
    log_dau = np.log10(df['DAU (Absolute)'].fillna(1).clip(lower=1))
    dau_score = normalize(log_dau) * 0.20
    
    df['Score'] = revenue_score + arpu_score + growth_score + dau_score
    
    # 对收入低于门槛的产品大幅降权（这些产品参考价值有限）
    df.loc[~df['Valid'], 'Score'] = df.loc[~df['Valid'], 'Score'] * 0.2
    
    return df

def assign_priority(score):
    """根据评分分配优先级"""
    if score >= 70:
        return "P0"
    elif score >= 50:
        return "P1"
    else:
        return "P2"

def process_data():
    """主处理流程"""
    print("\n" + "="*60)
    print("  竞品数据处理")
    print("="*60)
    
    # Step 1: 加载数据
    print("\n[Step 1] 加载CSV文件...")
    dfs = {}
    for key, filepath in FILES.items():
        if filepath.exists():
            dfs[key] = load_csv(filepath)
        else:
            print(f"  Warning: {filepath} not found")
    
    # Step 2: 处理Nutrition分榜数据
    print("\n[Step 2] 处理 Nutrition 分榜...")
    if 'nutrition_revenue' in dfs:
        nutrition_df = dfs['nutrition_revenue'].copy()
        nutrition_df = aggregate_by_app(nutrition_df)
        nutrition_df = calculate_metrics(nutrition_df)
        nutrition_df = calculate_score(nutrition_df)
        nutrition_df['Priority'] = nutrition_df['Score'].apply(assign_priority)
        nutrition_df = nutrition_df.sort_values('Score', ascending=False)
        print(f"    -> {len(nutrition_df)} unique apps")
    
    # Step 3: 处理总榜数据（只取Health & Fitness）
    print("\n[Step 3] 处理总榜 (Health & Fitness)...")
    if 'total_revenue' in dfs:
        total_df = dfs['total_revenue'].copy()
        # 筛选Health & Fitness
        health_df = total_df[total_df['Category'] == 'Health & Fitness'].copy()
        health_df = aggregate_by_app(health_df)
        health_df = calculate_metrics(health_df)
        health_df = calculate_score(health_df)
        health_df['Priority'] = health_df['Score'].apply(assign_priority)
        health_df = health_df.sort_values('Score', ascending=False)
        print(f"    -> {len(health_df)} unique Health & Fitness apps")
    
    # Step 4: 生成Top 30清单
    print("\n[Step 4] 生成 Top 30 必研究清单...")
    
    # 策略：确保头部产品（收入Top 10）+ 高效率产品（ARPU高）+ 高增长产品
    
    # 从Nutrition分榜取：
    # - 收入Top 10
    nutrition_by_revenue = nutrition_df.nlargest(10, 'Revenue (Absolute)').copy()
    # - 评分Top 15（去重）
    nutrition_by_score = nutrition_df[~nutrition_df['App ID'].isin(nutrition_by_revenue['App ID'])].head(10).copy()
    nutrition_combined = pd.concat([nutrition_by_revenue, nutrition_by_score])
    nutrition_combined['Source'] = 'Nutrition'
    
    # 从总榜补充跨赛道标杆（如Calm, Strava, Flo等）
    nutrition_app_ids = set(nutrition_combined['App ID'].tolist())
    # 先按收入排序，取收入Top 10的非Nutrition产品
    health_by_revenue = health_df[~health_df['App ID'].isin(nutrition_app_ids)].nlargest(10, 'Revenue (Absolute)').copy()
    health_by_revenue['Source'] = 'Health_Total'
    
    # 合并
    top30_df = pd.concat([nutrition_combined, health_by_revenue], ignore_index=True)
    top30_df = top30_df.sort_values('Score', ascending=False).head(30)
    top30_df['Rank'] = range(1, len(top30_df) + 1)
    
    # Step 5: 整理输出字段
    print("\n[Step 5] 整理输出...")
    
    output_columns = [
        'Rank', 'Unified Name', 'Unified Publisher Name', 'Category',
        'Revenue (Absolute)', 'Downloads (Absolute)', 'ARPU',
        'Growth Rate', 'DAU (Absolute)', 'Score', 'Priority', 'Source'
    ]
    
    top30_output = top30_df[output_columns].copy()
    top30_output.columns = [
        'rank', 'app_name', 'publisher', 'category',
        'revenue', 'downloads', 'arpu',
        'growth_rate', 'dau', 'score', 'priority', 'source'
    ]
    
    # 格式化数字
    top30_output['revenue'] = top30_output['revenue'].round(0).astype(int)
    top30_output['downloads'] = top30_output['downloads'].round(0).astype(int)
    top30_output['arpu'] = top30_output['arpu'].round(2)
    top30_output['growth_rate'] = (top30_output['growth_rate'] * 100).round(1)  # 转为百分比
    top30_output['dau'] = top30_output['dau'].fillna(0).round(0).astype(int)
    top30_output['score'] = top30_output['score'].round(1)
    
    # Step 6: 保存文件
    print("\n[Step 6] 保存输出文件...")
    
    # 确保输出目录存在
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # 保存Top 30 CSV
    top30_csv = OUTPUT_DIR / "top30_must_study.csv"
    top30_output.to_csv(top30_csv, index=False, encoding='utf-8-sig')
    print(f"  -> {top30_csv}")
    
    # 保存完整Nutrition分榜
    nutrition_csv = OUTPUT_DIR / "nutrition_competitors.csv"
    nutrition_cols = [
        'Unified Name', 'Unified Publisher Name', 'Category',
        'Revenue (Absolute)', 'Downloads (Absolute)', 'ARPU',
        'Growth Rate', 'DAU (Absolute)', 'Score', 'Priority'
    ]
    nutrition_output = nutrition_df[nutrition_cols].copy()
    nutrition_output.columns = [
        'app_name', 'publisher', 'category',
        'revenue', 'downloads', 'arpu',
        'growth_rate', 'dau', 'score', 'priority'
    ]
    nutrition_output['source'] = 'Nutrition'
    nutrition_output.to_csv(nutrition_csv, index=False, encoding='utf-8-sig')
    print(f"  -> {nutrition_csv}")
    
    # 保存JSON数据库
    competitors_json = OUTPUT_DIR / "competitors.json"
    
    # 合并所有数据
    all_data = {
        "metadata": {
            "source": "Sensor Tower",
            "date_range": "Nov 11, 2025 - Dec 10, 2025",
            "regions": ["US", "AU", "CA", "FR", "DE", "+2 others"],
            "total_nutrition_apps": len(nutrition_df),
            "total_health_apps": len(health_df),
        },
        "top30": top30_output.to_dict(orient='records'),
        "nutrition_all": nutrition_df[[
            'App ID', 'Unified Name', 'Revenue (Absolute)', 
            'Downloads (Absolute)', 'ARPU', 'Growth Rate', 'Score', 'Priority'
        ]].head(50).to_dict(orient='records'),
    }
    
    with open(competitors_json, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    print(f"  -> {competitors_json}")
    
    # Step 7: 打印摘要
    print("\n" + "="*60)
    print("  Done!")
    print("="*60)
    
    print("\n[Top 30 Must Study List]")
    print("-" * 90)
    print(f"{'Rank':<5} {'App Name':<35} {'Revenue':>12} {'ARPU':>8} {'Growth':>8} {'Priority':<8}")
    print("-" * 90)
    
    for _, row in top30_output.iterrows():
        name = row['app_name'][:33] if len(str(row['app_name'])) > 33 else row['app_name']
        revenue = f"${row['revenue']:,}"
        arpu = f"${row['arpu']:.2f}"
        growth = f"{row['growth_rate']:+.1f}%"
        print(f"{row['rank']:<5} {name:<35} {revenue:>12} {arpu:>8} {growth:>8} {row['priority']:<8}")
    
    print("-" * 90)
    p0_count = len(top30_output[top30_output['priority']=='P0'])
    p1_count = len(top30_output[top30_output['priority']=='P1'])
    p2_count = len(top30_output[top30_output['priority']=='P2'])
    print(f"\nP0 (High Priority): {p0_count}")
    print(f"P1 (Medium Priority): {p1_count}")
    print(f"P2 (Low Priority): {p2_count}")
    
    return top30_output

if __name__ == "__main__":
    process_data()

