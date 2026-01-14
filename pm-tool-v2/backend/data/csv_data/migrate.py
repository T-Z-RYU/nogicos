# -*- coding: utf-8 -*-
"""
数据迁移脚本
将现有JSON数据迁移到SQLite数据库
支持从旧的screen_type到新的三层分类(Stage/Module/Feature)的转换
"""

import os
import sys
import json
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.db_manager import DBManager, DB_PATH

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECTS_DIR = os.path.join(BASE_DIR, "projects")
CONFIG_DIR = os.path.join(BASE_DIR, "config")

# 加载同义词映射（用于screen_type到stage/module的转换）
def load_screen_type_mapping():
    """加载旧screen_type到新三层结构的映射"""
    synonyms_path = os.path.join(CONFIG_DIR, "synonyms.json")
    if os.path.exists(synonyms_path):
        with open(synonyms_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("screen_type_mapping", {})
    
    # 默认映射
    return {
        "Welcome": {"stage": "Onboarding", "module": "Welcome", "feature": None},
        "Onboarding_Intro": {"stage": "Onboarding", "module": "Welcome", "feature": "ValueProp"},
        "Onboarding_Profile": {"stage": "Onboarding", "module": "Profile", "feature": None},
        "Onboarding_Goal": {"stage": "Onboarding", "module": "Goal", "feature": None},
        "Onboarding_Personalization": {"stage": "Onboarding", "module": "Preference", "feature": None},
        "Onboarding_Permission": {"stage": "Onboarding", "module": "Permission", "feature": None},
        "Onboarding_Loading": {"stage": "Onboarding", "module": "Initialization", "feature": "Loading"},
        "Paywall": {"stage": "Onboarding", "module": "Paywall", "feature": None},
        "Subscription": {"stage": "Onboarding", "module": "Paywall", "feature": "PlanSelect"},
        "Registration": {"stage": "Onboarding", "module": "Registration", "feature": None},
        "Login": {"stage": "Onboarding", "module": "Registration", "feature": "MethodSelect"},
        "SignUp": {"stage": "Onboarding", "module": "Registration", "feature": None},
        "Home": {"stage": "Core", "module": "Dashboard", "feature": "Overview"},
        "Dashboard": {"stage": "Core", "module": "Dashboard", "feature": "Overview"},
        "Tracking": {"stage": "Core", "module": "Tracking", "feature": None},
        "Food_Log": {"stage": "Core", "module": "Tracking", "feature": "FoodLog"},
        "Food_Search": {"stage": "Core", "module": "Tracking", "feature": "FoodSearch"},
        "Progress": {"stage": "Core", "module": "Progress", "feature": None},
        "Analytics": {"stage": "Core", "module": "Progress", "feature": "TrendAnalysis"},
        "Profile": {"stage": "Core", "module": "Profile_Core", "feature": "AccountInfo"},
        "Settings": {"stage": "Core", "module": "Settings", "feature": None},
        "Social": {"stage": "Core", "module": "Social", "feature": None},
        "Content": {"stage": "Core", "module": "Content", "feature": None},
        "Feature": {"stage": "Core", "module": "Dashboard", "feature": None},
        "Permission": {"stage": "Onboarding", "module": "Permission", "feature": None},
        "Onboarding": {"stage": "Onboarding", "module": "Profile", "feature": None},
        "Launch": {"stage": "Onboarding", "module": "Welcome", "feature": "Splash"},
        "Other": {"stage": "Core", "module": "Dashboard", "feature": None},
    }


def convert_screen_type(screen_type, mapping):
    """将旧的screen_type转换为新的三层分类"""
    if not screen_type:
        return {"stage": None, "module": None, "feature": None}
    
    # 直接匹配
    if screen_type in mapping:
        return mapping[screen_type]
    
    # 模糊匹配
    screen_type_lower = screen_type.lower()
    for key, value in mapping.items():
        if key.lower() in screen_type_lower or screen_type_lower in key.lower():
            return value
    
    # 默认返回
    return {"stage": None, "module": None, "feature": None}


def migrate_project(db: DBManager, project_folder: str, mapping: dict) -> bool:
    """迁移单个项目"""
    project_path = os.path.join(PROJECTS_DIR, project_folder)
    
    # 读取ai_analysis.json
    analysis_file = os.path.join(project_path, "ai_analysis.json")
    if not os.path.exists(analysis_file):
        print(f"  [SKIP] No ai_analysis.json found")
        return False
    
    try:
        with open(analysis_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"  [ERROR] Failed to load ai_analysis.json: {e}")
        return False
    
    # 提取产品信息
    product_profile = data.get('product_profile', {})
    flow_structure = data.get('flow_structure', {})
    
    # 从文件夹名提取产品名
    product_name = project_folder.replace('_Analysis', '').replace('_', ' ')
    
    product_data = {
        'name': product_name,
        'folder_name': project_folder,
        'category': product_profile.get('app_category'),
        'sub_category': product_profile.get('sub_category'),
        'target_users': product_profile.get('target_users'),
        'core_value': product_profile.get('core_value'),
        'business_model': product_profile.get('business_model'),
        'visual_style': product_profile.get('visual_style'),
        'paywall_position': flow_structure.get('paywall_position'),
        'onboarding_length': flow_structure.get('onboarding_length'),
        'total_screenshots': data.get('total_screenshots', 0),
        'model': data.get('model')
    }
    
    # 保存产品
    product_id = db.save_product(product_data)
    print(f"  [OK] Product saved (ID: {product_id})")
    
    # 保存截图（含三层分类转换）
    results = data.get('results', {})
    screenshot_count = 0
    conversion_stats = {"converted": 0, "skipped": 0}
    
    for filename, screenshot_data in results.items():
        screenshot_data['filename'] = filename
        
        # 转换screen_type到新的三层分类
        screen_type = screenshot_data.get('screen_type')
        converted = convert_screen_type(screen_type, mapping)
        
        screenshot_data['stage'] = converted.get('stage')
        screenshot_data['module'] = converted.get('module')
        screenshot_data['feature'] = converted.get('feature')
        
        if converted.get('stage'):
            conversion_stats["converted"] += 1
        else:
            conversion_stats["skipped"] += 1
        
        db.save_screenshot(product_id, screenshot_data)
        screenshot_count += 1
    
    print(f"  [OK] {screenshot_count} screenshots saved (converted: {conversion_stats['converted']}, skipped: {conversion_stats['skipped']})")
    
    # 保存流程阶段
    stages = flow_structure.get('stages', [])
    if stages:
        db.save_flow_stages(product_id, stages)
        print(f"  [OK] {len(stages)} flow stages saved")
    
    return True


def migrate_all():
    """迁移所有项目"""
    print("=" * 60)
    print("  Data Migration to SQLite (with 3-Layer Classification)")
    print("=" * 60)
    
    # 加载映射
    mapping = load_screen_type_mapping()
    print(f"\n[INFO] Loaded screen_type mapping with {len(mapping)} entries")
    
    # 备份现有数据库（如果存在）
    if os.path.exists(DB_PATH):
        backup_path = DB_PATH + f".backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.rename(DB_PATH, backup_path)
        print(f"\n[BACKUP] Existing database backed up to {backup_path}")
    
    # 创建新数据库
    db = DBManager()
    print(f"[OK] Database created at {DB_PATH}")
    
    # 获取所有项目
    projects = [d for d in os.listdir(PROJECTS_DIR) 
                if os.path.isdir(os.path.join(PROJECTS_DIR, d)) 
                and d.endswith('_Analysis')]
    
    print(f"\n[INFO] Found {len(projects)} projects to migrate\n")
    
    success_count = 0
    fail_count = 0
    
    for project in projects:
        print(f"\n[{success_count + fail_count + 1}/{len(projects)}] Migrating: {project}")
        
        if migrate_project(db, project, mapping):
            success_count += 1
        else:
            fail_count += 1
    
    # 验证迁移结果
    print("\n" + "=" * 60)
    print("  Migration Summary")
    print("=" * 60)
    
    products = db.get_all_products()
    print(f"\nProducts in database: {len(products)}")
    for p in products:
        screenshots = db.get_screenshots(p['id'])
        print(f"  - {p['name']}: {len(screenshots)} screenshots")
    
    # 新的Stage/Module统计
    print("\n[STATS] Stage distribution:")
    stage_stats = db.get_stage_stats()
    for stage, count in stage_stats.items():
        print(f"  {stage or 'None'}: {count}")
    
    print("\n[STATS] Module distribution:")
    module_stats = db.get_module_stats()
    for module, count in list(module_stats.items())[:15]:
        print(f"  {module or 'None'}: {count}")
    
    # 旧的screen_type统计（用于对比）
    print("\n[STATS] Legacy screen_type distribution:")
    type_stats = db.get_screen_type_stats()
    for t, count in list(type_stats.items())[:10]:
        print(f"  {t}: {count}")
    
    print(f"\n[RESULT] Success: {success_count}, Failed: {fail_count}")
    print(f"[OK] Database saved to {DB_PATH}")


if __name__ == "__main__":
    migrate_all()
