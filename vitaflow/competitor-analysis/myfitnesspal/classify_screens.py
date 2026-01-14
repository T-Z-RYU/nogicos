# -*- coding: utf-8 -*-
"""
MyFitnessPal 截图分类工具
按产品流程逻辑进行分类，Onboarding 模块细颗粒度分类
"""

import os
import shutil

# ============ 配置区域 ============
SOURCE_FOLDER = "MFP_Screens_Downloaded"
OUTPUT_FOLDER = "MFP_Screens_Classified"
# =================================

# 分类结构定义（基于产品流程逻辑）
CLASSIFICATION = {
    # ==================== 1. 启动与欢迎 ====================
    "01_Launch": {
        "screens": [(1, 1)],
        "description": "启动页/Splash Screen - 品牌展示"
    },
    
    "02_Welcome_Carousel": {
        "screens": [(2, 4)],
        "description": "欢迎轮播页 - 产品核心价值介绍（追踪、影响、习惯）"
    },
    
    "03_SignUp_Entry": {
        "screens": [(5, 5)],
        "description": "注册入口 - 注册方式选择（Email/Google/Apple）"
    },
    
    # ==================== 2. Onboarding 核心流程 ====================
    "04_Onboarding": {
        "sub_folders": {
            "04-01_Name_Input": {
                "screens": [(6, 6)],
                "description": "姓名输入 - 个性化称呼收集，建立亲切感"
            },
            "04-02_Goals_Selection": {
                "screens": [(7, 7)],
                "description": "目标选择 - 选择最多3个健身目标（减重/保持/增重/增肌/饮食/计划/压力/运动）"
            },
            "04-03_Goals_Motivation": {
                "screens": [(8, 8)],
                "description": "目标激励页 - 承认减重不易，承诺陪伴支持，展示预期曲线"
            },
            "04-04_Barriers_Survey": {
                "screens": [(9, 9)],
                "description": "障碍调研 - 过去减重失败原因（时间/难度/食物/选择/社交/渴望/进度）"
            },
            "04-05_Barriers_Empathy": {
                "screens": [(10, 10)],
                "description": "共情页面 - 理解用户困难，强调帮助数百万用户的经验"
            },
            "04-06_Habits_Selection": {
                "screens": [(11, 11)],
                "description": "习惯选择 - 选择重要的健康习惯（推荐+更多习惯两组）"
            },
            "04-07_Habits_Motivation": {
                "screens": [(12, 12)],
                "description": "习惯激励页 - 小习惯=大改变，帮助积累小胜利"
            },
            "04-08_Meal_Planning_Frequency": {
                "screens": [(13, 13)],
                "description": "饮食规划频率 - 提前规划饮食的频率（从不/很少/偶尔/经常/总是）"
            },
            "04-09_Meal_Planning_Motivation": {
                "screens": [(14, 14)],
                "description": "规划激励页 - 一点计划，大量生活便利"
            },
            "04-10_Weekly_Meal_Plan_Interest": {
                "screens": [(15, 15)],
                "description": "周餐计划意愿 - 是否需要帮助制定周餐计划（积极/开放/拒绝）"
            },
            "04-11_Activity_Level": {
                "screens": [(16, 16)],
                "description": "活动水平 - 基础活动水平选择（不活跃/轻度/中度/非常活跃）"
            },
            "04-12_Personal_Info": {
                "screens": [(17, 18)],
                "description": "个人信息 - 性别/年龄/地区/邮编（含地区选择弹窗）"
            },
            "04-13_Body_Metrics": {
                "screens": [(19, 19)],
                "description": "身体数据 - 身高/当前体重/目标体重"
            },
            "04-14_Weekly_Goal": {
                "screens": [(20, 20)],
                "description": "每周目标 - 选择每周减重速度（0.2/0.5/0.8/1kg）"
            },
            "04-15_Account_Creation": {
                "screens": [(21, 21)],
                "description": "账户创建 - 邮箱和密码设置，同意条款"
            },
            "04-16_Attribution_Survey": {
                "screens": [(22, 22)],
                "description": "来源调研 - 从哪里了解到App（Facebook/TikTok/Instagram/AppStore等）"
            },
            "04-17_Calorie_Goal_Result": {
                "screens": [(23, 23)],
                "description": "卡路里目标结果 - 显示计算出的每日卡路里目标、预期达成日期、开启提醒"
            }
        }
    },
    
    # ==================== 3. Paywall 付费墙 ====================
    "05_Paywall": {
        "sub_folders": {
            "05-01_Permission_Notification": {
                "screens": [(24, 24)],
                "description": "通知权限请求 - 请求推送通知权限"
            },
            "05-02_Permission_Motion": {
                "screens": [(25, 25)],
                "description": "运动权限请求 - 请求访问运动与健身数据"
            },
            "05-03_Premium_Intro": {
                "screens": [(26, 26)],
                "description": "Premium介绍 - Premium功能列表、价格、免费试用"
            },
            "05-04_Plans_Comparison": {
                "screens": [(27, 27)],
                "description": "套餐对比 - Premium vs Premium+ 功能对比表"
            },
            "05-05_Premium_Plus_Intro": {
                "screens": [(28, 28)],
                "description": "Premium+介绍 - Premium+专属功能、价格"
            },
            "05-06_Purchase_Process": {
                "screens": [(29, 30)],
                "description": "购买流程 - 购买确认、购买成功弹窗"
            }
        }
    },
    
    # ==================== 4. Premium+ 餐计划引导 ====================
    "06_MealPlan_Onboarding": {
        "sub_folders": {
            "06-01_Premium_Welcome": {
                "screens": [(31, 31)],
                "description": "Premium+欢迎 - Welcome to Premium+"
            },
            "06-02_MealPlanner_Intro": {
                "screens": [(32, 32)],
                "description": "餐计划器介绍 - Dig in to Meal Planner"
            },
            "06-03_MealPlan_Goals": {
                "screens": [(33, 33)],
                "description": "餐计划目标 - 选择餐计划目标（减重/宏量/健康/增重/省时/省钱等）"
            },
            "06-04_Motivation_Level": {
                "screens": [(34, 34)],
                "description": "动机程度 - 愿意做多大改变（大改变/中等/小步骤/还没准备好）"
            },
            "06-05_Eating_Challenge": {
                "screens": [(35, 35)],
                "description": "饮食挑战 - 健康饮食最大挑战（份量/零食/渴望/压力/外食/时间）"
            },
            "06-06_Change_Pace": {
                "screens": [(36, 36)],
                "description": "改变节奏 - 选择改变速度，展示体重曲线预览"
            },
            "06-07_Diet_Type": {
                "screens": [(37, 37)],
                "description": "饮食类型 - 选择饮食计划（均衡/海鲜/弹性/素食/低碳/生酮/地中海/高蛋白等）"
            },
            "06-08_Diet_Detail": {
                "screens": [(38, 38)],
                "description": "饮食详情 - 显示选择的饮食计划详情（卡路里、宏量比例、特点）"
            },
            "06-09_Meals_Frequency": {
                "screens": [(39, 39)],
                "description": "餐食频率 - 每周计划多少餐（部分晚餐/大部分午晚餐/每餐/自定义）"
            },
            "06-10_Macronutrient": {
                "screens": [(40, 40)],
                "description": "营养素优先级 - 最重要的宏量营养素（碳水/蛋白质/脂肪/均等）"
            },
            "06-11_Allergies": {
                "screens": [(41, 41)],
                "description": "过敏源 - 选择食物过敏（花生/坚果/鱼/贝类/大豆/蛋/乳制品/芝麻）"
            },
            "06-12_Dislikes": {
                "screens": [(42, 44)],
                "description": "食物偏好 - 不喜欢的食材选择"
            },
            "06-13_Cooking_Skills": {
                "screens": [(45, 45)],
                "description": "烹饪技能 - 烹饪水平（新手/基础/中级/高级）"
            },
            "06-14_Cooking_Time": {
                "screens": [(46, 48)],
                "description": "烹饪时间 - 愿意花多少时间做饭"
            },
            "06-15_Leftover_Preference": {
                "screens": [(49, 50)],
                "description": "剩菜偏好 - 吃剩菜的频率（经常/有时/不常）"
            },
            "06-16_Kitchen_Equipment": {
                "screens": [(51, 52)],
                "description": "厨房设备 - 拥有的烹饪设备"
            },
            "06-17_Ingredient_Preferences": {
                "screens": [(53, 58)],
                "description": "食材偏好 - 喜欢的蔬菜、蛋白质、谷物等"
            },
            "06-18_Calculating": {
                "screens": [(59, 60)],
                "description": "计算加载 - 正在计算个性化方案"
            },
            "06-19_Plan_Summary": {
                "screens": [(61, 64)],
                "description": "计划摘要 - 展示个性化餐计划概要"
            },
            "06-20_Start_Date": {
                "screens": [(65, 66)],
                "description": "开始日期 - 选择餐计划开始日期"
            },
            "06-21_Meal_Plan_Review": {
                "screens": [(67, 72)],
                "description": "餐计划审核 - 审核每天的早午晚餐和零食"
            },
            "06-22_Recipe_Swap": {
                "screens": [(73, 77)],
                "description": "食谱替换 - 替换不喜欢的食谱"
            },
            "06-23_Snacks_Review": {
                "screens": [(78, 80)],
                "description": "零食审核 - 审核推荐的零食"
            },
            "06-24_Plan_Created": {
                "screens": [(81, 82)],
                "description": "计划创建完成 - 餐计划创建成功确认"
            }
        }
    },
    
    # ==================== 5. 应用内教程 ====================
    "07_App_Tutorials": {
        "sub_folders": {
            "07-01_Dashboard_Tutorial": {
                "screens": [(95, 96)],
                "description": "Dashboard教程 - Logging Progress功能介绍"
            },
            "07-02_Feature_Tips": {
                "screens": [(97, 98)],
                "description": "功能提示 - 各种功能的使用提示"
            }
        }
    },
    
    # ==================== 6. 主应用界面 ====================
    "08_Main_App": {
        "sub_folders": {
            "08-01_Dashboard": {
                "screens": [(110, 111), (140, 141)],
                "description": "Dashboard主页 - 卡路里/宏量营养素/习惯/步数/运动/体重概览"
            },
            "08-02_Diary": {
                "screens": [(83, 86)],
                "description": "Diary日记 - 每日食物/运动/水分记录"
            },
            "08-03_Plan_MealPlanner": {
                "screens": [(87, 89)],
                "description": "Plan餐计划 - 查看和管理周餐计划"
            },
            "08-04_Plan_Groceries": {
                "screens": [(90, 92)],
                "description": "Plan购物清单 - 购物列表管理"
            },
            "08-05_More_Menu": {
                "screens": [(93, 94)],
                "description": "More菜单 - 更多功能入口"
            }
        }
    },
    
    # ==================== 7. 食物记录流程 ====================
    "09_Food_Logging": {
        "sub_folders": {
            "09-01_Food_Search": {
                "screens": [(105, 107)],
                "description": "食物搜索 - 搜索食物数据库"
            },
            "09-02_Add_Food_Detail": {
                "screens": [(125, 130)],
                "description": "添加食物详情 - 份量/营养素/时间戳/多日添加"
            },
            "09-03_Barcode_Scan": {
                "screens": [(131, 133)],
                "description": "条码扫描 - 扫描食品条码快速添加"
            },
            "09-04_Meal_Scan": {
                "screens": [(170, 172)],
                "description": "餐食扫描 - AI识别整餐食物并记录"
            },
            "09-05_Quick_Add": {
                "screens": [(134, 135)],
                "description": "快速添加 - 直接输入卡路里"
            }
        }
    },
    
    # ==================== 8. 食谱与营养 ====================
    "10_Recipes_Nutrition": {
        "sub_folders": {
            "10-01_Recipe_Detail": {
                "screens": [(160, 162)],
                "description": "食谱详情 - 食谱图片/营养信息/食材/步骤"
            },
            "10-02_Nutrition_Overview": {
                "screens": [(100, 102)],
                "description": "营养概览 - 营养素详细追踪（蛋白质/碳水/脂肪/纤维等）"
            },
            "10-03_Calorie_Breakdown": {
                "screens": [(103, 104)],
                "description": "卡路里分解 - 每餐卡路里分布"
            }
        }
    },
    
    # ==================== 9. 运动与健身 ====================
    "11_Exercise": {
        "sub_folders": {
            "11-01_Exercise_Log": {
                "screens": [(145, 147)],
                "description": "运动记录 - 记录运动类型和消耗"
            },
            "11-02_Workout_Videos": {
                "screens": [(150, 152)],
                "description": "运动视频 - 健身视频指导"
            },
            "11-03_Steps_Tracking": {
                "screens": [(148, 149)],
                "description": "步数追踪 - 每日步数统计"
            }
        }
    },
    
    # ==================== 10. 健康追踪 ====================
    "12_Health_Tracking": {
        "sub_folders": {
            "12-01_Weight_Progress": {
                "screens": [(118, 119)],
                "description": "体重进度 - 体重变化趋势图"
            },
            "12-02_Body_Measurements": {
                "screens": [(120, 122)],
                "description": "身体测量 - 腰围/臀围等数据记录"
            },
            "12-03_Sleep": {
                "screens": [(190, 191)],
                "description": "睡眠追踪 - 睡眠时长和质量分析"
            },
            "12-04_Fasting": {
                "screens": [(185, 187)],
                "description": "轻断食 - 间歇性断食追踪设置"
            },
            "12-05_Water": {
                "screens": [(136, 137)],
                "description": "饮水追踪 - 每日饮水记录"
            }
        }
    },
    
    # ==================== 11. 习惯与目标 ====================
    "13_Habits_Goals": {
        "sub_folders": {
            "13-01_Habits_Setup": {
                "screens": [(112, 116)],
                "description": "习惯设置 - 创建和管理健康习惯"
            },
            "13-02_Goals_Customization": {
                "screens": [(195, 196)],
                "description": "目标自定义 - 自定义每日卡路里和宏量目标"
            },
            "13-03_Streaks": {
                "screens": [(117, 117)],
                "description": "连续记录 - 记录连续天数统计"
            }
        }
    },
    
    # ==================== 12. 设置与账户 ====================
    "14_Settings": {
        "sub_folders": {
            "14-01_Premium_Management": {
                "screens": [(180, 182)],
                "description": "Premium管理 - 订阅状态和功能管理"
            },
            "14-02_Export_Data": {
                "screens": [(200, 200)],
                "description": "数据导出 - 导出进度报告和历史数据"
            },
            "14-03_Profile": {
                "screens": [(198, 199)],
                "description": "个人资料 - 账户信息管理"
            },
            "14-04_Notifications": {
                "screens": [(183, 184)],
                "description": "通知设置 - 提醒和通知配置"
            }
        }
    }
}


def create_folder_structure():
    """创建文件夹结构"""
    base_path = OUTPUT_FOLDER
    if os.path.exists(base_path):
        shutil.rmtree(base_path)
    os.makedirs(base_path, exist_ok=True)
    
    for folder_name, config in CLASSIFICATION.items():
        folder_path = os.path.join(base_path, folder_name)
        os.makedirs(folder_path, exist_ok=True)
        
        if "sub_folders" in config:
            for sub_name in config["sub_folders"].keys():
                sub_path = os.path.join(folder_path, sub_name)
                os.makedirs(sub_path, exist_ok=True)
    
    # 创建未分类文件夹
    os.makedirs(os.path.join(base_path, "99_Uncategorized"), exist_ok=True)
    
    print("[OK] 文件夹结构创建完成")


def get_screen_path(screen_num):
    """获取截图文件路径"""
    filename = f"Screen_{screen_num:03d}.png"
    return os.path.join(SOURCE_FOLDER, filename)


def copy_screen(screen_num, dest_folder):
    """复制截图到目标文件夹"""
    src_path = get_screen_path(screen_num)
    if os.path.exists(src_path):
        filename = f"Screen_{screen_num:03d}.png"
        dest_path = os.path.join(dest_folder, filename)
        shutil.copy2(src_path, dest_path)
        return True
    return False


def classify_screens():
    """执行截图分类"""
    base_path = OUTPUT_FOLDER
    classified_count = 0
    classified_nums = set()
    
    for folder_name, config in CLASSIFICATION.items():
        folder_path = os.path.join(base_path, folder_name)
        
        if "sub_folders" in config:
            for sub_name, sub_config in config["sub_folders"].items():
                sub_path = os.path.join(folder_path, sub_name)
                for start, end in sub_config.get("screens", []):
                    for num in range(start, end + 1):
                        if copy_screen(num, sub_path):
                            classified_count += 1
                            classified_nums.add(num)
        elif "screens" in config:
            for start, end in config.get("screens", []):
                for num in range(start, end + 1):
                    if copy_screen(num, folder_path):
                        classified_count += 1
                        classified_nums.add(num)
    
    print(f"[OK] 已分类 {classified_count} 张截图")
    return classified_nums


def copy_remaining_screens(classified_nums):
    """将未分类的截图复制到 99_Uncategorized 文件夹"""
    uncategorized_path = os.path.join(OUTPUT_FOLDER, "99_Uncategorized")
    uncategorized_count = 0
    
    for i in range(1, 201):
        if i not in classified_nums:
            if copy_screen(i, uncategorized_path):
                uncategorized_count += 1
    
    print(f"[OK] {uncategorized_count} 张待进一步分类的截图已复制到 99_Uncategorized")
    return uncategorized_count


def generate_chapters_md():
    """生成 _Chapters.md 文档"""
    lines = ["# MyFitnessPal 产品截图分类\n\n"]
    lines.append("> 按产品流程逻辑分类 | 专为产品经理设计\n\n")
    lines.append("---\n\n")
    
    lines.append("## 目录\n\n")
    for folder_name in CLASSIFICATION.keys():
        display_name = folder_name.replace("_", " ")
        lines.append(f"- [{display_name}](#{folder_name.lower()})\n")
    lines.append("\n---\n\n")
    
    lines.append("## 产品流程结构\n\n")
    
    for folder_name, config in CLASSIFICATION.items():
        display_name = folder_name.replace("_", " ")
        lines.append(f"### {display_name}\n\n")
        
        if "description" in config:
            lines.append(f"**概述**: {config['description']}\n\n")
        
        if "sub_folders" in config:
            lines.append("| 序号 | 模块 | 描述 | 截图 |\n")
            lines.append("|------|------|------|------|\n")
            for sub_name, sub_config in config["sub_folders"].items():
                sub_display = sub_name.split("_", 1)[1].replace("_", " ") if "_" in sub_name else sub_name
                desc = sub_config.get("description", "")
                screens = sub_config.get("screens", [])
                screen_str = ", ".join([f"{s}-{e}" if s != e else str(s) for s, e in screens])
                lines.append(f"| {sub_name.split('_')[0]} | {sub_display} | {desc} | {screen_str} |\n")
            lines.append("\n")
        elif "screens" in config:
            screens = config.get("screens", [])
            screen_str = ", ".join([f"{s}-{e}" if s != e else str(s) for s, e in screens])
            lines.append(f"**截图范围**: {screen_str}\n\n")
    
    # Onboarding 详细分析
    lines.append("---\n\n")
    lines.append("## Onboarding 设计分析\n\n")
    lines.append("### 流程特点\n\n")
    lines.append("MyFitnessPal 的 Onboarding 流程设计亮点：\n\n")
    lines.append("1. **渐进式信息收集** - 从简单问题（姓名）开始，逐步深入到复杂决策\n")
    lines.append("2. **激励穿插设计** - 每收集2-3个信息后插入激励页面，降低用户疲劳感\n")
    lines.append("3. **共情文案策略** - 承认困难、理解痛点，建立情感连接\n")
    lines.append("4. **个性化承诺** - 展示计算结果和预期达成日期，给用户明确目标\n")
    lines.append("5. **价值先行** - 在 Paywall 前已完成核心价值体验（目标设定）\n\n")
    
    lines.append("### 页面类型统计\n\n")
    lines.append("| 类型 | 数量 | 作用 |\n")
    lines.append("|------|------|------|\n")
    lines.append("| 信息收集页 | 12 | 收集用户数据用于个性化 |\n")
    lines.append("| 激励/共情页 | 4 | 保持用户动力，降低流失 |\n")
    lines.append("| 结果展示页 | 1 | 展示个性化计算结果 |\n\n")
    
    lines.append("### Meal Plan Onboarding 特点\n\n")
    lines.append("Premium+ 餐计划引导是一个深度个性化流程：\n\n")
    lines.append("1. **目标明确化** - 再次确认餐计划相关目标\n")
    lines.append("2. **限制条件收集** - 过敏源、不喜欢的食材、烹饪水平\n")
    lines.append("3. **生活方式适配** - 烹饪时间、厨房设备、剩菜习惯\n")
    lines.append("4. **可视化预览** - 展示体重曲线预测\n")
    lines.append("5. **用户控制权** - 允许审核和替换不喜欢的食谱\n\n")
    
    output_path = os.path.join(OUTPUT_FOLDER, "_Chapters.md")
    with open(output_path, "w", encoding="utf-8") as f:
        f.writelines(lines)
    
    print(f"[OK] 已生成 _Chapters.md")


def generate_screen_list_csv():
    """生成 _ScreenList.csv 截图清单"""
    lines = ["Screen,Category,SubCategory,Description\n"]
    
    for folder_name, config in CLASSIFICATION.items():
        category = folder_name
        
        if "sub_folders" in config:
            for sub_name, sub_config in config["sub_folders"].items():
                desc = sub_config.get("description", "").replace(",", ";")
                for start, end in sub_config.get("screens", []):
                    for num in range(start, end + 1):
                        lines.append(f"Screen_{num:03d}.png,{category},{sub_name},{desc}\n")
        elif "screens" in config:
            desc = config.get("description", "").replace(",", ";")
            for start, end in config.get("screens", []):
                for num in range(start, end + 1):
                    lines.append(f"Screen_{num:03d}.png,{category},,{desc}\n")
    
    output_path = os.path.join(OUTPUT_FOLDER, "_ScreenList.csv")
    with open(output_path, "w", encoding="utf-8-sig") as f:
        f.writelines(lines)
    
    print(f"[OK] 已生成 _ScreenList.csv")


def generate_onboarding_detail_md():
    """生成 Onboarding 详细分析文档"""
    lines = ["# Onboarding 流程详细分析\n\n"]
    lines.append("> MyFitnessPal Onboarding 流程拆解\n\n")
    
    # 只处理 Onboarding 相关的分类
    onboarding_keys = ["04_Onboarding", "06_MealPlan_Onboarding"]
    
    for key in onboarding_keys:
        if key in CLASSIFICATION:
            config = CLASSIFICATION[key]
            display_name = key.replace("_", " ")
            lines.append(f"## {display_name}\n\n")
            
            if "sub_folders" in config:
                for sub_name, sub_config in config["sub_folders"].items():
                    sub_display = sub_name.replace("_", " ")
                    desc = sub_config.get("description", "")
                    screens = sub_config.get("screens", [])
                    
                    lines.append(f"### {sub_display}\n\n")
                    lines.append(f"**描述**: {desc}\n\n")
                    
                    screen_str = ", ".join([f"Screen_{s:03d}-{e:03d}" if s != e else f"Screen_{s:03d}" for s, e in screens])
                    lines.append(f"**截图**: {screen_str}\n\n")
                    
                    # 提取分析要点
                    if "目标" in desc:
                        lines.append("**设计要点**: 目标设定是用户参与度的关键驱动力\n\n")
                    elif "激励" in desc or "共情" in desc:
                        lines.append("**设计要点**: 情感连接页面，减少用户流失\n\n")
                    elif "选择" in desc or "偏好" in desc:
                        lines.append("**设计要点**: 个性化数据收集，提升推荐准确度\n\n")
                    
                    lines.append("---\n\n")
    
    output_path = os.path.join(OUTPUT_FOLDER, "_Onboarding_Analysis.md")
    with open(output_path, "w", encoding="utf-8") as f:
        f.writelines(lines)
    
    print(f"[OK] 已生成 _Onboarding_Analysis.md")


def main():
    print("=" * 60)
    print("MyFitnessPal 截图分类工具")
    print("按产品流程逻辑分类 | Onboarding 细颗粒度分析")
    print("=" * 60)
    print()
    
    if not os.path.exists(SOURCE_FOLDER):
        print(f"[X] 源文件夹不存在: {SOURCE_FOLDER}")
        return
    
    print("步骤 1/5: 创建文件夹结构...")
    create_folder_structure()
    
    print("\n步骤 2/5: 分类截图...")
    classified_nums = classify_screens()
    
    print("\n步骤 3/5: 处理待分类截图...")
    uncategorized = copy_remaining_screens(classified_nums)
    
    print("\n步骤 4/5: 生成分类文档...")
    generate_chapters_md()
    generate_screen_list_csv()
    
    print("\n步骤 5/5: 生成 Onboarding 分析文档...")
    generate_onboarding_detail_md()
    
    print("\n" + "=" * 60)
    print("分类完成!")
    print(f"  - 已分类: {len(classified_nums)} 张")
    print(f"  - 待进一步分类: {uncategorized} 张")
    print(f"  - 输出目录: {OUTPUT_FOLDER}")
    print(f"  - 生成文档: _Chapters.md, _ScreenList.csv, _Onboarding_Analysis.md")
    print("=" * 60)


if __name__ == "__main__":
    main()
