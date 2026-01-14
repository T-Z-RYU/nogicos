# -*- coding: utf-8 -*-
"""
截图重命名脚本 - 扁平化结构，方便导入Figma
"""

import os
import shutil

SOURCE_FOLDER = "MFP_Screens_Downloaded"
OUTPUT_FOLDER = "Screens"

# 截图命名映射：原始编号 -> 新文件名
RENAME_MAP = {
    # 01_Launch - 启动
    1: "01_Launch_01_SplashScreen",
    
    # 02_Welcome - 欢迎轮播
    2: "02_Welcome_01_ValueProp_Tracking",
    3: "02_Welcome_02_ValueProp_Impact",
    4: "02_Welcome_03_ValueProp_Habits",
    
    # 03_SignUp - 注册入口
    5: "03_SignUp_01_MethodSelection",
    
    # 04_Onboard - 核心引导流程
    6: "04_Onboard_01_NameInput",
    7: "04_Onboard_02_GoalsSelection",
    8: "04_Onboard_03_GoalsMotivation",
    9: "04_Onboard_04_BarriersSurvey",
    10: "04_Onboard_05_BarriersEmpathy",
    11: "04_Onboard_06_HabitsSelection",
    12: "04_Onboard_07_HabitsMotivation",
    13: "04_Onboard_08_MealPlanFrequency",
    14: "04_Onboard_09_MealPlanMotivation",
    15: "04_Onboard_10_WeeklyPlanInterest",
    16: "04_Onboard_11_ActivityLevel",
    17: "04_Onboard_12_PersonalInfo",
    18: "04_Onboard_13_PersonalInfoFilled",
    19: "04_Onboard_14_BodyMetrics",
    20: "04_Onboard_15_WeeklyGoal",
    21: "04_Onboard_16_AccountCreation",
    22: "04_Onboard_17_AttributionSurvey",
    23: "04_Onboard_18_CalorieGoalResult",
    
    # 05_Paywall - 付费墙
    24: "05_Paywall_01_NotificationPermission",
    25: "05_Paywall_02_MotionPermission",
    26: "05_Paywall_03_PremiumIntro",
    27: "05_Paywall_04_PlansComparison",
    28: "05_Paywall_05_PremiumPlusIntro",
    29: "05_Paywall_06_PurchaseConfirm",
    30: "05_Paywall_07_PurchaseSuccess",
    
    # 06_MealPlan - 餐计划引导
    31: "06_MealPlan_01_PremiumWelcome",
    32: "06_MealPlan_02_MealPlannerIntro",
    33: "06_MealPlan_03_GoalsSelection",
    34: "06_MealPlan_04_MotivationLevel",
    35: "06_MealPlan_05_EatingChallenge",
    36: "06_MealPlan_06_ChangePace",
    37: "06_MealPlan_07_DietType",
    38: "06_MealPlan_08_DietDetail",
    39: "06_MealPlan_09_MealsFrequency",
    40: "06_MealPlan_10_Macronutrient",
    41: "06_MealPlan_11_Allergies",
    42: "06_MealPlan_12_Dislikes_1",
    43: "06_MealPlan_13_Dislikes_2",
    44: "06_MealPlan_14_Dislikes_3",
    45: "06_MealPlan_15_CookingSkills",
    46: "06_MealPlan_16_CookingTime_1",
    47: "06_MealPlan_17_CookingTime_2",
    48: "06_MealPlan_18_CookingTime_3",
    49: "06_MealPlan_19_LeftoverPref_1",
    50: "06_MealPlan_20_LeftoverPref_2",
    51: "06_MealPlan_21_KitchenEquip_1",
    52: "06_MealPlan_22_KitchenEquip_2",
    53: "06_MealPlan_23_IngredientPref_1",
    54: "06_MealPlan_24_IngredientPref_2",
    55: "06_MealPlan_25_IngredientPref_3",
    56: "06_MealPlan_26_IngredientPref_4",
    57: "06_MealPlan_27_IngredientPref_5",
    58: "06_MealPlan_28_IngredientPref_6",
    59: "06_MealPlan_29_Calculating_1",
    60: "06_MealPlan_30_Calculating_2",
    61: "06_MealPlan_31_PlanSummary_1",
    62: "06_MealPlan_32_PlanSummary_2",
    63: "06_MealPlan_33_PlanSummary_3",
    64: "06_MealPlan_34_PlanSummary_4",
    65: "06_MealPlan_35_StartDate_1",
    66: "06_MealPlan_36_StartDate_2",
    67: "06_MealPlan_37_MealReview_1",
    68: "06_MealPlan_38_MealReview_2",
    69: "06_MealPlan_39_MealReview_3",
    70: "06_MealPlan_40_MealReview_4",
    71: "06_MealPlan_41_MealReview_5",
    72: "06_MealPlan_42_MealReview_6",
    73: "06_MealPlan_43_RecipeSwap_1",
    74: "06_MealPlan_44_RecipeSwap_2",
    75: "06_MealPlan_45_RecipeSwap_3",
    76: "06_MealPlan_46_RecipeSwap_4",
    77: "06_MealPlan_47_RecipeSwap_5",
    78: "06_MealPlan_48_SnacksReview_1",
    79: "06_MealPlan_49_SnacksReview_2",
    80: "06_MealPlan_50_SnacksReview_3",
    81: "06_MealPlan_51_PlanCreated_1",
    82: "06_MealPlan_52_PlanCreated_2",
    
    # 07_Tutorial - 应用教程
    83: "08_Main_01_Diary_1",
    84: "08_Main_02_Diary_2",
    85: "08_Main_03_Diary_3",
    86: "08_Main_04_Diary_4",
    87: "08_Main_05_Plan_Meal_1",
    88: "08_Main_06_Plan_Meal_2",
    89: "08_Main_07_Plan_Meal_3",
    90: "08_Main_08_Plan_Groceries_1",
    91: "08_Main_09_Plan_Groceries_2",
    92: "08_Main_10_Plan_Groceries_3",
    93: "08_Main_11_More_1",
    94: "08_Main_12_More_2",
    95: "07_Tutorial_01_LoggingProgress",
    96: "07_Tutorial_02_CelebrateChoices",
    97: "07_Tutorial_03_FeatureTip_1",
    98: "07_Tutorial_04_FeatureTip_2",
    99: "08_Main_13_Dashboard_1",
    100: "10_Recipe_01_NutritionOverview_1",
    101: "10_Recipe_02_NutritionOverview_2",
    102: "10_Recipe_03_NutritionOverview_3",
    103: "10_Recipe_04_CalorieBreakdown_1",
    104: "10_Recipe_05_CalorieBreakdown_2",
    105: "09_FoodLog_01_Search_1",
    106: "09_FoodLog_02_Search_2",
    107: "09_FoodLog_03_Search_3",
    108: "08_Main_14_Dashboard_2",
    109: "08_Main_15_Dashboard_3",
    110: "08_Main_16_Dashboard_4",
    111: "08_Main_17_Dashboard_5",
    112: "13_Habits_01_Setup_1",
    113: "13_Habits_02_Setup_2",
    114: "13_Habits_03_Setup_3",
    115: "13_Habits_04_Setup_4",
    116: "13_Habits_05_Setup_5",
    117: "13_Habits_06_Streaks",
    118: "12_Health_01_WeightProgress_1",
    119: "12_Health_02_WeightProgress_2",
    120: "12_Health_03_BodyMeasure_1",
    121: "12_Health_04_BodyMeasure_2",
    122: "12_Health_05_BodyMeasure_3",
    123: "09_FoodLog_04_AddDetail_1",
    124: "09_FoodLog_05_AddDetail_2",
    125: "09_FoodLog_06_AddDetail_3",
    126: "09_FoodLog_07_AddDetail_4",
    127: "09_FoodLog_08_AddDetail_5",
    128: "09_FoodLog_09_AddDetail_6",
    129: "09_FoodLog_10_AddDetail_7",
    130: "09_FoodLog_11_AddDetail_8",
    131: "09_FoodLog_12_BarcodeScan_1",
    132: "09_FoodLog_13_BarcodeScan_2",
    133: "09_FoodLog_14_BarcodeScan_3",
    134: "09_FoodLog_15_QuickAdd_1",
    135: "09_FoodLog_16_QuickAdd_2",
    136: "12_Health_06_Water_1",
    137: "12_Health_07_Water_2",
    138: "08_Main_18_Dashboard_6",
    139: "08_Main_19_Dashboard_7",
    140: "08_Main_20_Dashboard_8",
    141: "08_Main_21_Dashboard_9",
    142: "11_Exercise_01_Log_1",
    143: "11_Exercise_02_Log_2",
    144: "11_Exercise_03_Log_3",
    145: "11_Exercise_04_Log_4",
    146: "11_Exercise_05_Log_5",
    147: "11_Exercise_06_Log_6",
    148: "11_Exercise_07_Steps_1",
    149: "11_Exercise_08_Steps_2",
    150: "11_Exercise_09_Video_1",
    151: "11_Exercise_10_Video_2",
    152: "11_Exercise_11_Video_3",
    153: "11_Exercise_12_Workout_1",
    154: "11_Exercise_13_Workout_2",
    155: "11_Exercise_14_Workout_3",
    156: "11_Exercise_15_Workout_4",
    157: "11_Exercise_16_Workout_5",
    158: "11_Exercise_17_Workout_6",
    159: "11_Exercise_18_Workout_7",
    160: "10_Recipe_06_RecipeDetail_1",
    161: "10_Recipe_07_RecipeDetail_2",
    162: "10_Recipe_08_RecipeDetail_3",
    163: "10_Recipe_09_RecipeDetail_4",
    164: "10_Recipe_10_RecipeDetail_5",
    165: "10_Recipe_11_RecipeList_1",
    166: "10_Recipe_12_RecipeList_2",
    167: "10_Recipe_13_RecipeList_3",
    168: "09_FoodLog_17_MealScan_1",
    169: "09_FoodLog_18_MealScan_2",
    170: "09_FoodLog_19_MealScan_3",
    171: "09_FoodLog_20_MealScan_4",
    172: "09_FoodLog_21_MealScan_5",
    173: "09_FoodLog_22_History_1",
    174: "09_FoodLog_23_History_2",
    175: "09_FoodLog_24_History_3",
    176: "14_Settings_01_Profile_1",
    177: "14_Settings_02_Profile_2",
    178: "14_Settings_03_Profile_3",
    179: "14_Settings_04_Premium_1",
    180: "14_Settings_05_Premium_2",
    181: "14_Settings_06_Premium_3",
    182: "14_Settings_07_Premium_4",
    183: "14_Settings_08_Notifications_1",
    184: "14_Settings_09_Notifications_2",
    185: "12_Health_08_Fasting_1",
    186: "12_Health_09_Fasting_2",
    187: "12_Health_10_Fasting_3",
    188: "12_Health_11_Fasting_4",
    189: "12_Health_12_Fasting_5",
    190: "12_Health_13_Sleep_1",
    191: "12_Health_14_Sleep_2",
    192: "12_Health_15_Sleep_3",
    193: "13_Habits_07_Goals_1",
    194: "13_Habits_08_Goals_2",
    195: "13_Habits_09_Goals_3",
    196: "13_Habits_10_Goals_4",
    197: "14_Settings_10_Account_1",
    198: "14_Settings_11_Account_2",
    199: "14_Settings_12_Account_3",
    200: "14_Settings_13_ExportData",
}


def main():
    print("=" * 50)
    print("截图重命名 - 扁平化结构")
    print("=" * 50)
    
    # 创建输出文件夹
    if os.path.exists(OUTPUT_FOLDER):
        shutil.rmtree(OUTPUT_FOLDER)
    os.makedirs(OUTPUT_FOLDER)
    
    # 重命名并复制
    success_count = 0
    for old_num, new_name in RENAME_MAP.items():
        old_path = os.path.join(SOURCE_FOLDER, f"Screen_{old_num:03d}.png")
        new_path = os.path.join(OUTPUT_FOLDER, f"{new_name}.png")
        
        if os.path.exists(old_path):
            shutil.copy2(old_path, new_path)
            success_count += 1
            print(f"  Screen_{old_num:03d}.png -> {new_name}.png")
    
    print()
    print(f"[OK] 完成！已重命名 {success_count} 张截图")
    print(f"[OK] 输出目录: {OUTPUT_FOLDER}")


if __name__ == "__main__":
    main()









"""
截图重命名脚本 - 扁平化结构，方便导入Figma
"""

import os
import shutil

SOURCE_FOLDER = "MFP_Screens_Downloaded"
OUTPUT_FOLDER = "Screens"

# 截图命名映射：原始编号 -> 新文件名
RENAME_MAP = {
    # 01_Launch - 启动
    1: "01_Launch_01_SplashScreen",
    
    # 02_Welcome - 欢迎轮播
    2: "02_Welcome_01_ValueProp_Tracking",
    3: "02_Welcome_02_ValueProp_Impact",
    4: "02_Welcome_03_ValueProp_Habits",
    
    # 03_SignUp - 注册入口
    5: "03_SignUp_01_MethodSelection",
    
    # 04_Onboard - 核心引导流程
    6: "04_Onboard_01_NameInput",
    7: "04_Onboard_02_GoalsSelection",
    8: "04_Onboard_03_GoalsMotivation",
    9: "04_Onboard_04_BarriersSurvey",
    10: "04_Onboard_05_BarriersEmpathy",
    11: "04_Onboard_06_HabitsSelection",
    12: "04_Onboard_07_HabitsMotivation",
    13: "04_Onboard_08_MealPlanFrequency",
    14: "04_Onboard_09_MealPlanMotivation",
    15: "04_Onboard_10_WeeklyPlanInterest",
    16: "04_Onboard_11_ActivityLevel",
    17: "04_Onboard_12_PersonalInfo",
    18: "04_Onboard_13_PersonalInfoFilled",
    19: "04_Onboard_14_BodyMetrics",
    20: "04_Onboard_15_WeeklyGoal",
    21: "04_Onboard_16_AccountCreation",
    22: "04_Onboard_17_AttributionSurvey",
    23: "04_Onboard_18_CalorieGoalResult",
    
    # 05_Paywall - 付费墙
    24: "05_Paywall_01_NotificationPermission",
    25: "05_Paywall_02_MotionPermission",
    26: "05_Paywall_03_PremiumIntro",
    27: "05_Paywall_04_PlansComparison",
    28: "05_Paywall_05_PremiumPlusIntro",
    29: "05_Paywall_06_PurchaseConfirm",
    30: "05_Paywall_07_PurchaseSuccess",
    
    # 06_MealPlan - 餐计划引导
    31: "06_MealPlan_01_PremiumWelcome",
    32: "06_MealPlan_02_MealPlannerIntro",
    33: "06_MealPlan_03_GoalsSelection",
    34: "06_MealPlan_04_MotivationLevel",
    35: "06_MealPlan_05_EatingChallenge",
    36: "06_MealPlan_06_ChangePace",
    37: "06_MealPlan_07_DietType",
    38: "06_MealPlan_08_DietDetail",
    39: "06_MealPlan_09_MealsFrequency",
    40: "06_MealPlan_10_Macronutrient",
    41: "06_MealPlan_11_Allergies",
    42: "06_MealPlan_12_Dislikes_1",
    43: "06_MealPlan_13_Dislikes_2",
    44: "06_MealPlan_14_Dislikes_3",
    45: "06_MealPlan_15_CookingSkills",
    46: "06_MealPlan_16_CookingTime_1",
    47: "06_MealPlan_17_CookingTime_2",
    48: "06_MealPlan_18_CookingTime_3",
    49: "06_MealPlan_19_LeftoverPref_1",
    50: "06_MealPlan_20_LeftoverPref_2",
    51: "06_MealPlan_21_KitchenEquip_1",
    52: "06_MealPlan_22_KitchenEquip_2",
    53: "06_MealPlan_23_IngredientPref_1",
    54: "06_MealPlan_24_IngredientPref_2",
    55: "06_MealPlan_25_IngredientPref_3",
    56: "06_MealPlan_26_IngredientPref_4",
    57: "06_MealPlan_27_IngredientPref_5",
    58: "06_MealPlan_28_IngredientPref_6",
    59: "06_MealPlan_29_Calculating_1",
    60: "06_MealPlan_30_Calculating_2",
    61: "06_MealPlan_31_PlanSummary_1",
    62: "06_MealPlan_32_PlanSummary_2",
    63: "06_MealPlan_33_PlanSummary_3",
    64: "06_MealPlan_34_PlanSummary_4",
    65: "06_MealPlan_35_StartDate_1",
    66: "06_MealPlan_36_StartDate_2",
    67: "06_MealPlan_37_MealReview_1",
    68: "06_MealPlan_38_MealReview_2",
    69: "06_MealPlan_39_MealReview_3",
    70: "06_MealPlan_40_MealReview_4",
    71: "06_MealPlan_41_MealReview_5",
    72: "06_MealPlan_42_MealReview_6",
    73: "06_MealPlan_43_RecipeSwap_1",
    74: "06_MealPlan_44_RecipeSwap_2",
    75: "06_MealPlan_45_RecipeSwap_3",
    76: "06_MealPlan_46_RecipeSwap_4",
    77: "06_MealPlan_47_RecipeSwap_5",
    78: "06_MealPlan_48_SnacksReview_1",
    79: "06_MealPlan_49_SnacksReview_2",
    80: "06_MealPlan_50_SnacksReview_3",
    81: "06_MealPlan_51_PlanCreated_1",
    82: "06_MealPlan_52_PlanCreated_2",
    
    # 07_Tutorial - 应用教程
    83: "08_Main_01_Diary_1",
    84: "08_Main_02_Diary_2",
    85: "08_Main_03_Diary_3",
    86: "08_Main_04_Diary_4",
    87: "08_Main_05_Plan_Meal_1",
    88: "08_Main_06_Plan_Meal_2",
    89: "08_Main_07_Plan_Meal_3",
    90: "08_Main_08_Plan_Groceries_1",
    91: "08_Main_09_Plan_Groceries_2",
    92: "08_Main_10_Plan_Groceries_3",
    93: "08_Main_11_More_1",
    94: "08_Main_12_More_2",
    95: "07_Tutorial_01_LoggingProgress",
    96: "07_Tutorial_02_CelebrateChoices",
    97: "07_Tutorial_03_FeatureTip_1",
    98: "07_Tutorial_04_FeatureTip_2",
    99: "08_Main_13_Dashboard_1",
    100: "10_Recipe_01_NutritionOverview_1",
    101: "10_Recipe_02_NutritionOverview_2",
    102: "10_Recipe_03_NutritionOverview_3",
    103: "10_Recipe_04_CalorieBreakdown_1",
    104: "10_Recipe_05_CalorieBreakdown_2",
    105: "09_FoodLog_01_Search_1",
    106: "09_FoodLog_02_Search_2",
    107: "09_FoodLog_03_Search_3",
    108: "08_Main_14_Dashboard_2",
    109: "08_Main_15_Dashboard_3",
    110: "08_Main_16_Dashboard_4",
    111: "08_Main_17_Dashboard_5",
    112: "13_Habits_01_Setup_1",
    113: "13_Habits_02_Setup_2",
    114: "13_Habits_03_Setup_3",
    115: "13_Habits_04_Setup_4",
    116: "13_Habits_05_Setup_5",
    117: "13_Habits_06_Streaks",
    118: "12_Health_01_WeightProgress_1",
    119: "12_Health_02_WeightProgress_2",
    120: "12_Health_03_BodyMeasure_1",
    121: "12_Health_04_BodyMeasure_2",
    122: "12_Health_05_BodyMeasure_3",
    123: "09_FoodLog_04_AddDetail_1",
    124: "09_FoodLog_05_AddDetail_2",
    125: "09_FoodLog_06_AddDetail_3",
    126: "09_FoodLog_07_AddDetail_4",
    127: "09_FoodLog_08_AddDetail_5",
    128: "09_FoodLog_09_AddDetail_6",
    129: "09_FoodLog_10_AddDetail_7",
    130: "09_FoodLog_11_AddDetail_8",
    131: "09_FoodLog_12_BarcodeScan_1",
    132: "09_FoodLog_13_BarcodeScan_2",
    133: "09_FoodLog_14_BarcodeScan_3",
    134: "09_FoodLog_15_QuickAdd_1",
    135: "09_FoodLog_16_QuickAdd_2",
    136: "12_Health_06_Water_1",
    137: "12_Health_07_Water_2",
    138: "08_Main_18_Dashboard_6",
    139: "08_Main_19_Dashboard_7",
    140: "08_Main_20_Dashboard_8",
    141: "08_Main_21_Dashboard_9",
    142: "11_Exercise_01_Log_1",
    143: "11_Exercise_02_Log_2",
    144: "11_Exercise_03_Log_3",
    145: "11_Exercise_04_Log_4",
    146: "11_Exercise_05_Log_5",
    147: "11_Exercise_06_Log_6",
    148: "11_Exercise_07_Steps_1",
    149: "11_Exercise_08_Steps_2",
    150: "11_Exercise_09_Video_1",
    151: "11_Exercise_10_Video_2",
    152: "11_Exercise_11_Video_3",
    153: "11_Exercise_12_Workout_1",
    154: "11_Exercise_13_Workout_2",
    155: "11_Exercise_14_Workout_3",
    156: "11_Exercise_15_Workout_4",
    157: "11_Exercise_16_Workout_5",
    158: "11_Exercise_17_Workout_6",
    159: "11_Exercise_18_Workout_7",
    160: "10_Recipe_06_RecipeDetail_1",
    161: "10_Recipe_07_RecipeDetail_2",
    162: "10_Recipe_08_RecipeDetail_3",
    163: "10_Recipe_09_RecipeDetail_4",
    164: "10_Recipe_10_RecipeDetail_5",
    165: "10_Recipe_11_RecipeList_1",
    166: "10_Recipe_12_RecipeList_2",
    167: "10_Recipe_13_RecipeList_3",
    168: "09_FoodLog_17_MealScan_1",
    169: "09_FoodLog_18_MealScan_2",
    170: "09_FoodLog_19_MealScan_3",
    171: "09_FoodLog_20_MealScan_4",
    172: "09_FoodLog_21_MealScan_5",
    173: "09_FoodLog_22_History_1",
    174: "09_FoodLog_23_History_2",
    175: "09_FoodLog_24_History_3",
    176: "14_Settings_01_Profile_1",
    177: "14_Settings_02_Profile_2",
    178: "14_Settings_03_Profile_3",
    179: "14_Settings_04_Premium_1",
    180: "14_Settings_05_Premium_2",
    181: "14_Settings_06_Premium_3",
    182: "14_Settings_07_Premium_4",
    183: "14_Settings_08_Notifications_1",
    184: "14_Settings_09_Notifications_2",
    185: "12_Health_08_Fasting_1",
    186: "12_Health_09_Fasting_2",
    187: "12_Health_10_Fasting_3",
    188: "12_Health_11_Fasting_4",
    189: "12_Health_12_Fasting_5",
    190: "12_Health_13_Sleep_1",
    191: "12_Health_14_Sleep_2",
    192: "12_Health_15_Sleep_3",
    193: "13_Habits_07_Goals_1",
    194: "13_Habits_08_Goals_2",
    195: "13_Habits_09_Goals_3",
    196: "13_Habits_10_Goals_4",
    197: "14_Settings_10_Account_1",
    198: "14_Settings_11_Account_2",
    199: "14_Settings_12_Account_3",
    200: "14_Settings_13_ExportData",
}


def main():
    print("=" * 50)
    print("截图重命名 - 扁平化结构")
    print("=" * 50)
    
    # 创建输出文件夹
    if os.path.exists(OUTPUT_FOLDER):
        shutil.rmtree(OUTPUT_FOLDER)
    os.makedirs(OUTPUT_FOLDER)
    
    # 重命名并复制
    success_count = 0
    for old_num, new_name in RENAME_MAP.items():
        old_path = os.path.join(SOURCE_FOLDER, f"Screen_{old_num:03d}.png")
        new_path = os.path.join(OUTPUT_FOLDER, f"{new_name}.png")
        
        if os.path.exists(old_path):
            shutil.copy2(old_path, new_path)
            success_count += 1
            print(f"  Screen_{old_num:03d}.png -> {new_name}.png")
    
    print()
    print(f"[OK] 完成！已重命名 {success_count} 张截图")
    print(f"[OK] 输出目录: {OUTPUT_FOLDER}")


if __name__ == "__main__":
    main()









"""
截图重命名脚本 - 扁平化结构，方便导入Figma
"""

import os
import shutil

SOURCE_FOLDER = "MFP_Screens_Downloaded"
OUTPUT_FOLDER = "Screens"

# 截图命名映射：原始编号 -> 新文件名
RENAME_MAP = {
    # 01_Launch - 启动
    1: "01_Launch_01_SplashScreen",
    
    # 02_Welcome - 欢迎轮播
    2: "02_Welcome_01_ValueProp_Tracking",
    3: "02_Welcome_02_ValueProp_Impact",
    4: "02_Welcome_03_ValueProp_Habits",
    
    # 03_SignUp - 注册入口
    5: "03_SignUp_01_MethodSelection",
    
    # 04_Onboard - 核心引导流程
    6: "04_Onboard_01_NameInput",
    7: "04_Onboard_02_GoalsSelection",
    8: "04_Onboard_03_GoalsMotivation",
    9: "04_Onboard_04_BarriersSurvey",
    10: "04_Onboard_05_BarriersEmpathy",
    11: "04_Onboard_06_HabitsSelection",
    12: "04_Onboard_07_HabitsMotivation",
    13: "04_Onboard_08_MealPlanFrequency",
    14: "04_Onboard_09_MealPlanMotivation",
    15: "04_Onboard_10_WeeklyPlanInterest",
    16: "04_Onboard_11_ActivityLevel",
    17: "04_Onboard_12_PersonalInfo",
    18: "04_Onboard_13_PersonalInfoFilled",
    19: "04_Onboard_14_BodyMetrics",
    20: "04_Onboard_15_WeeklyGoal",
    21: "04_Onboard_16_AccountCreation",
    22: "04_Onboard_17_AttributionSurvey",
    23: "04_Onboard_18_CalorieGoalResult",
    
    # 05_Paywall - 付费墙
    24: "05_Paywall_01_NotificationPermission",
    25: "05_Paywall_02_MotionPermission",
    26: "05_Paywall_03_PremiumIntro",
    27: "05_Paywall_04_PlansComparison",
    28: "05_Paywall_05_PremiumPlusIntro",
    29: "05_Paywall_06_PurchaseConfirm",
    30: "05_Paywall_07_PurchaseSuccess",
    
    # 06_MealPlan - 餐计划引导
    31: "06_MealPlan_01_PremiumWelcome",
    32: "06_MealPlan_02_MealPlannerIntro",
    33: "06_MealPlan_03_GoalsSelection",
    34: "06_MealPlan_04_MotivationLevel",
    35: "06_MealPlan_05_EatingChallenge",
    36: "06_MealPlan_06_ChangePace",
    37: "06_MealPlan_07_DietType",
    38: "06_MealPlan_08_DietDetail",
    39: "06_MealPlan_09_MealsFrequency",
    40: "06_MealPlan_10_Macronutrient",
    41: "06_MealPlan_11_Allergies",
    42: "06_MealPlan_12_Dislikes_1",
    43: "06_MealPlan_13_Dislikes_2",
    44: "06_MealPlan_14_Dislikes_3",
    45: "06_MealPlan_15_CookingSkills",
    46: "06_MealPlan_16_CookingTime_1",
    47: "06_MealPlan_17_CookingTime_2",
    48: "06_MealPlan_18_CookingTime_3",
    49: "06_MealPlan_19_LeftoverPref_1",
    50: "06_MealPlan_20_LeftoverPref_2",
    51: "06_MealPlan_21_KitchenEquip_1",
    52: "06_MealPlan_22_KitchenEquip_2",
    53: "06_MealPlan_23_IngredientPref_1",
    54: "06_MealPlan_24_IngredientPref_2",
    55: "06_MealPlan_25_IngredientPref_3",
    56: "06_MealPlan_26_IngredientPref_4",
    57: "06_MealPlan_27_IngredientPref_5",
    58: "06_MealPlan_28_IngredientPref_6",
    59: "06_MealPlan_29_Calculating_1",
    60: "06_MealPlan_30_Calculating_2",
    61: "06_MealPlan_31_PlanSummary_1",
    62: "06_MealPlan_32_PlanSummary_2",
    63: "06_MealPlan_33_PlanSummary_3",
    64: "06_MealPlan_34_PlanSummary_4",
    65: "06_MealPlan_35_StartDate_1",
    66: "06_MealPlan_36_StartDate_2",
    67: "06_MealPlan_37_MealReview_1",
    68: "06_MealPlan_38_MealReview_2",
    69: "06_MealPlan_39_MealReview_3",
    70: "06_MealPlan_40_MealReview_4",
    71: "06_MealPlan_41_MealReview_5",
    72: "06_MealPlan_42_MealReview_6",
    73: "06_MealPlan_43_RecipeSwap_1",
    74: "06_MealPlan_44_RecipeSwap_2",
    75: "06_MealPlan_45_RecipeSwap_3",
    76: "06_MealPlan_46_RecipeSwap_4",
    77: "06_MealPlan_47_RecipeSwap_5",
    78: "06_MealPlan_48_SnacksReview_1",
    79: "06_MealPlan_49_SnacksReview_2",
    80: "06_MealPlan_50_SnacksReview_3",
    81: "06_MealPlan_51_PlanCreated_1",
    82: "06_MealPlan_52_PlanCreated_2",
    
    # 07_Tutorial - 应用教程
    83: "08_Main_01_Diary_1",
    84: "08_Main_02_Diary_2",
    85: "08_Main_03_Diary_3",
    86: "08_Main_04_Diary_4",
    87: "08_Main_05_Plan_Meal_1",
    88: "08_Main_06_Plan_Meal_2",
    89: "08_Main_07_Plan_Meal_3",
    90: "08_Main_08_Plan_Groceries_1",
    91: "08_Main_09_Plan_Groceries_2",
    92: "08_Main_10_Plan_Groceries_3",
    93: "08_Main_11_More_1",
    94: "08_Main_12_More_2",
    95: "07_Tutorial_01_LoggingProgress",
    96: "07_Tutorial_02_CelebrateChoices",
    97: "07_Tutorial_03_FeatureTip_1",
    98: "07_Tutorial_04_FeatureTip_2",
    99: "08_Main_13_Dashboard_1",
    100: "10_Recipe_01_NutritionOverview_1",
    101: "10_Recipe_02_NutritionOverview_2",
    102: "10_Recipe_03_NutritionOverview_3",
    103: "10_Recipe_04_CalorieBreakdown_1",
    104: "10_Recipe_05_CalorieBreakdown_2",
    105: "09_FoodLog_01_Search_1",
    106: "09_FoodLog_02_Search_2",
    107: "09_FoodLog_03_Search_3",
    108: "08_Main_14_Dashboard_2",
    109: "08_Main_15_Dashboard_3",
    110: "08_Main_16_Dashboard_4",
    111: "08_Main_17_Dashboard_5",
    112: "13_Habits_01_Setup_1",
    113: "13_Habits_02_Setup_2",
    114: "13_Habits_03_Setup_3",
    115: "13_Habits_04_Setup_4",
    116: "13_Habits_05_Setup_5",
    117: "13_Habits_06_Streaks",
    118: "12_Health_01_WeightProgress_1",
    119: "12_Health_02_WeightProgress_2",
    120: "12_Health_03_BodyMeasure_1",
    121: "12_Health_04_BodyMeasure_2",
    122: "12_Health_05_BodyMeasure_3",
    123: "09_FoodLog_04_AddDetail_1",
    124: "09_FoodLog_05_AddDetail_2",
    125: "09_FoodLog_06_AddDetail_3",
    126: "09_FoodLog_07_AddDetail_4",
    127: "09_FoodLog_08_AddDetail_5",
    128: "09_FoodLog_09_AddDetail_6",
    129: "09_FoodLog_10_AddDetail_7",
    130: "09_FoodLog_11_AddDetail_8",
    131: "09_FoodLog_12_BarcodeScan_1",
    132: "09_FoodLog_13_BarcodeScan_2",
    133: "09_FoodLog_14_BarcodeScan_3",
    134: "09_FoodLog_15_QuickAdd_1",
    135: "09_FoodLog_16_QuickAdd_2",
    136: "12_Health_06_Water_1",
    137: "12_Health_07_Water_2",
    138: "08_Main_18_Dashboard_6",
    139: "08_Main_19_Dashboard_7",
    140: "08_Main_20_Dashboard_8",
    141: "08_Main_21_Dashboard_9",
    142: "11_Exercise_01_Log_1",
    143: "11_Exercise_02_Log_2",
    144: "11_Exercise_03_Log_3",
    145: "11_Exercise_04_Log_4",
    146: "11_Exercise_05_Log_5",
    147: "11_Exercise_06_Log_6",
    148: "11_Exercise_07_Steps_1",
    149: "11_Exercise_08_Steps_2",
    150: "11_Exercise_09_Video_1",
    151: "11_Exercise_10_Video_2",
    152: "11_Exercise_11_Video_3",
    153: "11_Exercise_12_Workout_1",
    154: "11_Exercise_13_Workout_2",
    155: "11_Exercise_14_Workout_3",
    156: "11_Exercise_15_Workout_4",
    157: "11_Exercise_16_Workout_5",
    158: "11_Exercise_17_Workout_6",
    159: "11_Exercise_18_Workout_7",
    160: "10_Recipe_06_RecipeDetail_1",
    161: "10_Recipe_07_RecipeDetail_2",
    162: "10_Recipe_08_RecipeDetail_3",
    163: "10_Recipe_09_RecipeDetail_4",
    164: "10_Recipe_10_RecipeDetail_5",
    165: "10_Recipe_11_RecipeList_1",
    166: "10_Recipe_12_RecipeList_2",
    167: "10_Recipe_13_RecipeList_3",
    168: "09_FoodLog_17_MealScan_1",
    169: "09_FoodLog_18_MealScan_2",
    170: "09_FoodLog_19_MealScan_3",
    171: "09_FoodLog_20_MealScan_4",
    172: "09_FoodLog_21_MealScan_5",
    173: "09_FoodLog_22_History_1",
    174: "09_FoodLog_23_History_2",
    175: "09_FoodLog_24_History_3",
    176: "14_Settings_01_Profile_1",
    177: "14_Settings_02_Profile_2",
    178: "14_Settings_03_Profile_3",
    179: "14_Settings_04_Premium_1",
    180: "14_Settings_05_Premium_2",
    181: "14_Settings_06_Premium_3",
    182: "14_Settings_07_Premium_4",
    183: "14_Settings_08_Notifications_1",
    184: "14_Settings_09_Notifications_2",
    185: "12_Health_08_Fasting_1",
    186: "12_Health_09_Fasting_2",
    187: "12_Health_10_Fasting_3",
    188: "12_Health_11_Fasting_4",
    189: "12_Health_12_Fasting_5",
    190: "12_Health_13_Sleep_1",
    191: "12_Health_14_Sleep_2",
    192: "12_Health_15_Sleep_3",
    193: "13_Habits_07_Goals_1",
    194: "13_Habits_08_Goals_2",
    195: "13_Habits_09_Goals_3",
    196: "13_Habits_10_Goals_4",
    197: "14_Settings_10_Account_1",
    198: "14_Settings_11_Account_2",
    199: "14_Settings_12_Account_3",
    200: "14_Settings_13_ExportData",
}


def main():
    print("=" * 50)
    print("截图重命名 - 扁平化结构")
    print("=" * 50)
    
    # 创建输出文件夹
    if os.path.exists(OUTPUT_FOLDER):
        shutil.rmtree(OUTPUT_FOLDER)
    os.makedirs(OUTPUT_FOLDER)
    
    # 重命名并复制
    success_count = 0
    for old_num, new_name in RENAME_MAP.items():
        old_path = os.path.join(SOURCE_FOLDER, f"Screen_{old_num:03d}.png")
        new_path = os.path.join(OUTPUT_FOLDER, f"{new_name}.png")
        
        if os.path.exists(old_path):
            shutil.copy2(old_path, new_path)
            success_count += 1
            print(f"  Screen_{old_num:03d}.png -> {new_name}.png")
    
    print()
    print(f"[OK] 完成！已重命名 {success_count} 张截图")
    print(f"[OK] 输出目录: {OUTPUT_FOLDER}")


if __name__ == "__main__":
    main()









"""
截图重命名脚本 - 扁平化结构，方便导入Figma
"""

import os
import shutil

SOURCE_FOLDER = "MFP_Screens_Downloaded"
OUTPUT_FOLDER = "Screens"

# 截图命名映射：原始编号 -> 新文件名
RENAME_MAP = {
    # 01_Launch - 启动
    1: "01_Launch_01_SplashScreen",
    
    # 02_Welcome - 欢迎轮播
    2: "02_Welcome_01_ValueProp_Tracking",
    3: "02_Welcome_02_ValueProp_Impact",
    4: "02_Welcome_03_ValueProp_Habits",
    
    # 03_SignUp - 注册入口
    5: "03_SignUp_01_MethodSelection",
    
    # 04_Onboard - 核心引导流程
    6: "04_Onboard_01_NameInput",
    7: "04_Onboard_02_GoalsSelection",
    8: "04_Onboard_03_GoalsMotivation",
    9: "04_Onboard_04_BarriersSurvey",
    10: "04_Onboard_05_BarriersEmpathy",
    11: "04_Onboard_06_HabitsSelection",
    12: "04_Onboard_07_HabitsMotivation",
    13: "04_Onboard_08_MealPlanFrequency",
    14: "04_Onboard_09_MealPlanMotivation",
    15: "04_Onboard_10_WeeklyPlanInterest",
    16: "04_Onboard_11_ActivityLevel",
    17: "04_Onboard_12_PersonalInfo",
    18: "04_Onboard_13_PersonalInfoFilled",
    19: "04_Onboard_14_BodyMetrics",
    20: "04_Onboard_15_WeeklyGoal",
    21: "04_Onboard_16_AccountCreation",
    22: "04_Onboard_17_AttributionSurvey",
    23: "04_Onboard_18_CalorieGoalResult",
    
    # 05_Paywall - 付费墙
    24: "05_Paywall_01_NotificationPermission",
    25: "05_Paywall_02_MotionPermission",
    26: "05_Paywall_03_PremiumIntro",
    27: "05_Paywall_04_PlansComparison",
    28: "05_Paywall_05_PremiumPlusIntro",
    29: "05_Paywall_06_PurchaseConfirm",
    30: "05_Paywall_07_PurchaseSuccess",
    
    # 06_MealPlan - 餐计划引导
    31: "06_MealPlan_01_PremiumWelcome",
    32: "06_MealPlan_02_MealPlannerIntro",
    33: "06_MealPlan_03_GoalsSelection",
    34: "06_MealPlan_04_MotivationLevel",
    35: "06_MealPlan_05_EatingChallenge",
    36: "06_MealPlan_06_ChangePace",
    37: "06_MealPlan_07_DietType",
    38: "06_MealPlan_08_DietDetail",
    39: "06_MealPlan_09_MealsFrequency",
    40: "06_MealPlan_10_Macronutrient",
    41: "06_MealPlan_11_Allergies",
    42: "06_MealPlan_12_Dislikes_1",
    43: "06_MealPlan_13_Dislikes_2",
    44: "06_MealPlan_14_Dislikes_3",
    45: "06_MealPlan_15_CookingSkills",
    46: "06_MealPlan_16_CookingTime_1",
    47: "06_MealPlan_17_CookingTime_2",
    48: "06_MealPlan_18_CookingTime_3",
    49: "06_MealPlan_19_LeftoverPref_1",
    50: "06_MealPlan_20_LeftoverPref_2",
    51: "06_MealPlan_21_KitchenEquip_1",
    52: "06_MealPlan_22_KitchenEquip_2",
    53: "06_MealPlan_23_IngredientPref_1",
    54: "06_MealPlan_24_IngredientPref_2",
    55: "06_MealPlan_25_IngredientPref_3",
    56: "06_MealPlan_26_IngredientPref_4",
    57: "06_MealPlan_27_IngredientPref_5",
    58: "06_MealPlan_28_IngredientPref_6",
    59: "06_MealPlan_29_Calculating_1",
    60: "06_MealPlan_30_Calculating_2",
    61: "06_MealPlan_31_PlanSummary_1",
    62: "06_MealPlan_32_PlanSummary_2",
    63: "06_MealPlan_33_PlanSummary_3",
    64: "06_MealPlan_34_PlanSummary_4",
    65: "06_MealPlan_35_StartDate_1",
    66: "06_MealPlan_36_StartDate_2",
    67: "06_MealPlan_37_MealReview_1",
    68: "06_MealPlan_38_MealReview_2",
    69: "06_MealPlan_39_MealReview_3",
    70: "06_MealPlan_40_MealReview_4",
    71: "06_MealPlan_41_MealReview_5",
    72: "06_MealPlan_42_MealReview_6",
    73: "06_MealPlan_43_RecipeSwap_1",
    74: "06_MealPlan_44_RecipeSwap_2",
    75: "06_MealPlan_45_RecipeSwap_3",
    76: "06_MealPlan_46_RecipeSwap_4",
    77: "06_MealPlan_47_RecipeSwap_5",
    78: "06_MealPlan_48_SnacksReview_1",
    79: "06_MealPlan_49_SnacksReview_2",
    80: "06_MealPlan_50_SnacksReview_3",
    81: "06_MealPlan_51_PlanCreated_1",
    82: "06_MealPlan_52_PlanCreated_2",
    
    # 07_Tutorial - 应用教程
    83: "08_Main_01_Diary_1",
    84: "08_Main_02_Diary_2",
    85: "08_Main_03_Diary_3",
    86: "08_Main_04_Diary_4",
    87: "08_Main_05_Plan_Meal_1",
    88: "08_Main_06_Plan_Meal_2",
    89: "08_Main_07_Plan_Meal_3",
    90: "08_Main_08_Plan_Groceries_1",
    91: "08_Main_09_Plan_Groceries_2",
    92: "08_Main_10_Plan_Groceries_3",
    93: "08_Main_11_More_1",
    94: "08_Main_12_More_2",
    95: "07_Tutorial_01_LoggingProgress",
    96: "07_Tutorial_02_CelebrateChoices",
    97: "07_Tutorial_03_FeatureTip_1",
    98: "07_Tutorial_04_FeatureTip_2",
    99: "08_Main_13_Dashboard_1",
    100: "10_Recipe_01_NutritionOverview_1",
    101: "10_Recipe_02_NutritionOverview_2",
    102: "10_Recipe_03_NutritionOverview_3",
    103: "10_Recipe_04_CalorieBreakdown_1",
    104: "10_Recipe_05_CalorieBreakdown_2",
    105: "09_FoodLog_01_Search_1",
    106: "09_FoodLog_02_Search_2",
    107: "09_FoodLog_03_Search_3",
    108: "08_Main_14_Dashboard_2",
    109: "08_Main_15_Dashboard_3",
    110: "08_Main_16_Dashboard_4",
    111: "08_Main_17_Dashboard_5",
    112: "13_Habits_01_Setup_1",
    113: "13_Habits_02_Setup_2",
    114: "13_Habits_03_Setup_3",
    115: "13_Habits_04_Setup_4",
    116: "13_Habits_05_Setup_5",
    117: "13_Habits_06_Streaks",
    118: "12_Health_01_WeightProgress_1",
    119: "12_Health_02_WeightProgress_2",
    120: "12_Health_03_BodyMeasure_1",
    121: "12_Health_04_BodyMeasure_2",
    122: "12_Health_05_BodyMeasure_3",
    123: "09_FoodLog_04_AddDetail_1",
    124: "09_FoodLog_05_AddDetail_2",
    125: "09_FoodLog_06_AddDetail_3",
    126: "09_FoodLog_07_AddDetail_4",
    127: "09_FoodLog_08_AddDetail_5",
    128: "09_FoodLog_09_AddDetail_6",
    129: "09_FoodLog_10_AddDetail_7",
    130: "09_FoodLog_11_AddDetail_8",
    131: "09_FoodLog_12_BarcodeScan_1",
    132: "09_FoodLog_13_BarcodeScan_2",
    133: "09_FoodLog_14_BarcodeScan_3",
    134: "09_FoodLog_15_QuickAdd_1",
    135: "09_FoodLog_16_QuickAdd_2",
    136: "12_Health_06_Water_1",
    137: "12_Health_07_Water_2",
    138: "08_Main_18_Dashboard_6",
    139: "08_Main_19_Dashboard_7",
    140: "08_Main_20_Dashboard_8",
    141: "08_Main_21_Dashboard_9",
    142: "11_Exercise_01_Log_1",
    143: "11_Exercise_02_Log_2",
    144: "11_Exercise_03_Log_3",
    145: "11_Exercise_04_Log_4",
    146: "11_Exercise_05_Log_5",
    147: "11_Exercise_06_Log_6",
    148: "11_Exercise_07_Steps_1",
    149: "11_Exercise_08_Steps_2",
    150: "11_Exercise_09_Video_1",
    151: "11_Exercise_10_Video_2",
    152: "11_Exercise_11_Video_3",
    153: "11_Exercise_12_Workout_1",
    154: "11_Exercise_13_Workout_2",
    155: "11_Exercise_14_Workout_3",
    156: "11_Exercise_15_Workout_4",
    157: "11_Exercise_16_Workout_5",
    158: "11_Exercise_17_Workout_6",
    159: "11_Exercise_18_Workout_7",
    160: "10_Recipe_06_RecipeDetail_1",
    161: "10_Recipe_07_RecipeDetail_2",
    162: "10_Recipe_08_RecipeDetail_3",
    163: "10_Recipe_09_RecipeDetail_4",
    164: "10_Recipe_10_RecipeDetail_5",
    165: "10_Recipe_11_RecipeList_1",
    166: "10_Recipe_12_RecipeList_2",
    167: "10_Recipe_13_RecipeList_3",
    168: "09_FoodLog_17_MealScan_1",
    169: "09_FoodLog_18_MealScan_2",
    170: "09_FoodLog_19_MealScan_3",
    171: "09_FoodLog_20_MealScan_4",
    172: "09_FoodLog_21_MealScan_5",
    173: "09_FoodLog_22_History_1",
    174: "09_FoodLog_23_History_2",
    175: "09_FoodLog_24_History_3",
    176: "14_Settings_01_Profile_1",
    177: "14_Settings_02_Profile_2",
    178: "14_Settings_03_Profile_3",
    179: "14_Settings_04_Premium_1",
    180: "14_Settings_05_Premium_2",
    181: "14_Settings_06_Premium_3",
    182: "14_Settings_07_Premium_4",
    183: "14_Settings_08_Notifications_1",
    184: "14_Settings_09_Notifications_2",
    185: "12_Health_08_Fasting_1",
    186: "12_Health_09_Fasting_2",
    187: "12_Health_10_Fasting_3",
    188: "12_Health_11_Fasting_4",
    189: "12_Health_12_Fasting_5",
    190: "12_Health_13_Sleep_1",
    191: "12_Health_14_Sleep_2",
    192: "12_Health_15_Sleep_3",
    193: "13_Habits_07_Goals_1",
    194: "13_Habits_08_Goals_2",
    195: "13_Habits_09_Goals_3",
    196: "13_Habits_10_Goals_4",
    197: "14_Settings_10_Account_1",
    198: "14_Settings_11_Account_2",
    199: "14_Settings_12_Account_3",
    200: "14_Settings_13_ExportData",
}


def main():
    print("=" * 50)
    print("截图重命名 - 扁平化结构")
    print("=" * 50)
    
    # 创建输出文件夹
    if os.path.exists(OUTPUT_FOLDER):
        shutil.rmtree(OUTPUT_FOLDER)
    os.makedirs(OUTPUT_FOLDER)
    
    # 重命名并复制
    success_count = 0
    for old_num, new_name in RENAME_MAP.items():
        old_path = os.path.join(SOURCE_FOLDER, f"Screen_{old_num:03d}.png")
        new_path = os.path.join(OUTPUT_FOLDER, f"{new_name}.png")
        
        if os.path.exists(old_path):
            shutil.copy2(old_path, new_path)
            success_count += 1
            print(f"  Screen_{old_num:03d}.png -> {new_name}.png")
    
    print()
    print(f"[OK] 完成！已重命名 {success_count} 张截图")
    print(f"[OK] 输出目录: {OUTPUT_FOLDER}")


if __name__ == "__main__":
    main()










"""
截图重命名脚本 - 扁平化结构，方便导入Figma
"""

import os
import shutil

SOURCE_FOLDER = "MFP_Screens_Downloaded"
OUTPUT_FOLDER = "Screens"

# 截图命名映射：原始编号 -> 新文件名
RENAME_MAP = {
    # 01_Launch - 启动
    1: "01_Launch_01_SplashScreen",
    
    # 02_Welcome - 欢迎轮播
    2: "02_Welcome_01_ValueProp_Tracking",
    3: "02_Welcome_02_ValueProp_Impact",
    4: "02_Welcome_03_ValueProp_Habits",
    
    # 03_SignUp - 注册入口
    5: "03_SignUp_01_MethodSelection",
    
    # 04_Onboard - 核心引导流程
    6: "04_Onboard_01_NameInput",
    7: "04_Onboard_02_GoalsSelection",
    8: "04_Onboard_03_GoalsMotivation",
    9: "04_Onboard_04_BarriersSurvey",
    10: "04_Onboard_05_BarriersEmpathy",
    11: "04_Onboard_06_HabitsSelection",
    12: "04_Onboard_07_HabitsMotivation",
    13: "04_Onboard_08_MealPlanFrequency",
    14: "04_Onboard_09_MealPlanMotivation",
    15: "04_Onboard_10_WeeklyPlanInterest",
    16: "04_Onboard_11_ActivityLevel",
    17: "04_Onboard_12_PersonalInfo",
    18: "04_Onboard_13_PersonalInfoFilled",
    19: "04_Onboard_14_BodyMetrics",
    20: "04_Onboard_15_WeeklyGoal",
    21: "04_Onboard_16_AccountCreation",
    22: "04_Onboard_17_AttributionSurvey",
    23: "04_Onboard_18_CalorieGoalResult",
    
    # 05_Paywall - 付费墙
    24: "05_Paywall_01_NotificationPermission",
    25: "05_Paywall_02_MotionPermission",
    26: "05_Paywall_03_PremiumIntro",
    27: "05_Paywall_04_PlansComparison",
    28: "05_Paywall_05_PremiumPlusIntro",
    29: "05_Paywall_06_PurchaseConfirm",
    30: "05_Paywall_07_PurchaseSuccess",
    
    # 06_MealPlan - 餐计划引导
    31: "06_MealPlan_01_PremiumWelcome",
    32: "06_MealPlan_02_MealPlannerIntro",
    33: "06_MealPlan_03_GoalsSelection",
    34: "06_MealPlan_04_MotivationLevel",
    35: "06_MealPlan_05_EatingChallenge",
    36: "06_MealPlan_06_ChangePace",
    37: "06_MealPlan_07_DietType",
    38: "06_MealPlan_08_DietDetail",
    39: "06_MealPlan_09_MealsFrequency",
    40: "06_MealPlan_10_Macronutrient",
    41: "06_MealPlan_11_Allergies",
    42: "06_MealPlan_12_Dislikes_1",
    43: "06_MealPlan_13_Dislikes_2",
    44: "06_MealPlan_14_Dislikes_3",
    45: "06_MealPlan_15_CookingSkills",
    46: "06_MealPlan_16_CookingTime_1",
    47: "06_MealPlan_17_CookingTime_2",
    48: "06_MealPlan_18_CookingTime_3",
    49: "06_MealPlan_19_LeftoverPref_1",
    50: "06_MealPlan_20_LeftoverPref_2",
    51: "06_MealPlan_21_KitchenEquip_1",
    52: "06_MealPlan_22_KitchenEquip_2",
    53: "06_MealPlan_23_IngredientPref_1",
    54: "06_MealPlan_24_IngredientPref_2",
    55: "06_MealPlan_25_IngredientPref_3",
    56: "06_MealPlan_26_IngredientPref_4",
    57: "06_MealPlan_27_IngredientPref_5",
    58: "06_MealPlan_28_IngredientPref_6",
    59: "06_MealPlan_29_Calculating_1",
    60: "06_MealPlan_30_Calculating_2",
    61: "06_MealPlan_31_PlanSummary_1",
    62: "06_MealPlan_32_PlanSummary_2",
    63: "06_MealPlan_33_PlanSummary_3",
    64: "06_MealPlan_34_PlanSummary_4",
    65: "06_MealPlan_35_StartDate_1",
    66: "06_MealPlan_36_StartDate_2",
    67: "06_MealPlan_37_MealReview_1",
    68: "06_MealPlan_38_MealReview_2",
    69: "06_MealPlan_39_MealReview_3",
    70: "06_MealPlan_40_MealReview_4",
    71: "06_MealPlan_41_MealReview_5",
    72: "06_MealPlan_42_MealReview_6",
    73: "06_MealPlan_43_RecipeSwap_1",
    74: "06_MealPlan_44_RecipeSwap_2",
    75: "06_MealPlan_45_RecipeSwap_3",
    76: "06_MealPlan_46_RecipeSwap_4",
    77: "06_MealPlan_47_RecipeSwap_5",
    78: "06_MealPlan_48_SnacksReview_1",
    79: "06_MealPlan_49_SnacksReview_2",
    80: "06_MealPlan_50_SnacksReview_3",
    81: "06_MealPlan_51_PlanCreated_1",
    82: "06_MealPlan_52_PlanCreated_2",
    
    # 07_Tutorial - 应用教程
    83: "08_Main_01_Diary_1",
    84: "08_Main_02_Diary_2",
    85: "08_Main_03_Diary_3",
    86: "08_Main_04_Diary_4",
    87: "08_Main_05_Plan_Meal_1",
    88: "08_Main_06_Plan_Meal_2",
    89: "08_Main_07_Plan_Meal_3",
    90: "08_Main_08_Plan_Groceries_1",
    91: "08_Main_09_Plan_Groceries_2",
    92: "08_Main_10_Plan_Groceries_3",
    93: "08_Main_11_More_1",
    94: "08_Main_12_More_2",
    95: "07_Tutorial_01_LoggingProgress",
    96: "07_Tutorial_02_CelebrateChoices",
    97: "07_Tutorial_03_FeatureTip_1",
    98: "07_Tutorial_04_FeatureTip_2",
    99: "08_Main_13_Dashboard_1",
    100: "10_Recipe_01_NutritionOverview_1",
    101: "10_Recipe_02_NutritionOverview_2",
    102: "10_Recipe_03_NutritionOverview_3",
    103: "10_Recipe_04_CalorieBreakdown_1",
    104: "10_Recipe_05_CalorieBreakdown_2",
    105: "09_FoodLog_01_Search_1",
    106: "09_FoodLog_02_Search_2",
    107: "09_FoodLog_03_Search_3",
    108: "08_Main_14_Dashboard_2",
    109: "08_Main_15_Dashboard_3",
    110: "08_Main_16_Dashboard_4",
    111: "08_Main_17_Dashboard_5",
    112: "13_Habits_01_Setup_1",
    113: "13_Habits_02_Setup_2",
    114: "13_Habits_03_Setup_3",
    115: "13_Habits_04_Setup_4",
    116: "13_Habits_05_Setup_5",
    117: "13_Habits_06_Streaks",
    118: "12_Health_01_WeightProgress_1",
    119: "12_Health_02_WeightProgress_2",
    120: "12_Health_03_BodyMeasure_1",
    121: "12_Health_04_BodyMeasure_2",
    122: "12_Health_05_BodyMeasure_3",
    123: "09_FoodLog_04_AddDetail_1",
    124: "09_FoodLog_05_AddDetail_2",
    125: "09_FoodLog_06_AddDetail_3",
    126: "09_FoodLog_07_AddDetail_4",
    127: "09_FoodLog_08_AddDetail_5",
    128: "09_FoodLog_09_AddDetail_6",
    129: "09_FoodLog_10_AddDetail_7",
    130: "09_FoodLog_11_AddDetail_8",
    131: "09_FoodLog_12_BarcodeScan_1",
    132: "09_FoodLog_13_BarcodeScan_2",
    133: "09_FoodLog_14_BarcodeScan_3",
    134: "09_FoodLog_15_QuickAdd_1",
    135: "09_FoodLog_16_QuickAdd_2",
    136: "12_Health_06_Water_1",
    137: "12_Health_07_Water_2",
    138: "08_Main_18_Dashboard_6",
    139: "08_Main_19_Dashboard_7",
    140: "08_Main_20_Dashboard_8",
    141: "08_Main_21_Dashboard_9",
    142: "11_Exercise_01_Log_1",
    143: "11_Exercise_02_Log_2",
    144: "11_Exercise_03_Log_3",
    145: "11_Exercise_04_Log_4",
    146: "11_Exercise_05_Log_5",
    147: "11_Exercise_06_Log_6",
    148: "11_Exercise_07_Steps_1",
    149: "11_Exercise_08_Steps_2",
    150: "11_Exercise_09_Video_1",
    151: "11_Exercise_10_Video_2",
    152: "11_Exercise_11_Video_3",
    153: "11_Exercise_12_Workout_1",
    154: "11_Exercise_13_Workout_2",
    155: "11_Exercise_14_Workout_3",
    156: "11_Exercise_15_Workout_4",
    157: "11_Exercise_16_Workout_5",
    158: "11_Exercise_17_Workout_6",
    159: "11_Exercise_18_Workout_7",
    160: "10_Recipe_06_RecipeDetail_1",
    161: "10_Recipe_07_RecipeDetail_2",
    162: "10_Recipe_08_RecipeDetail_3",
    163: "10_Recipe_09_RecipeDetail_4",
    164: "10_Recipe_10_RecipeDetail_5",
    165: "10_Recipe_11_RecipeList_1",
    166: "10_Recipe_12_RecipeList_2",
    167: "10_Recipe_13_RecipeList_3",
    168: "09_FoodLog_17_MealScan_1",
    169: "09_FoodLog_18_MealScan_2",
    170: "09_FoodLog_19_MealScan_3",
    171: "09_FoodLog_20_MealScan_4",
    172: "09_FoodLog_21_MealScan_5",
    173: "09_FoodLog_22_History_1",
    174: "09_FoodLog_23_History_2",
    175: "09_FoodLog_24_History_3",
    176: "14_Settings_01_Profile_1",
    177: "14_Settings_02_Profile_2",
    178: "14_Settings_03_Profile_3",
    179: "14_Settings_04_Premium_1",
    180: "14_Settings_05_Premium_2",
    181: "14_Settings_06_Premium_3",
    182: "14_Settings_07_Premium_4",
    183: "14_Settings_08_Notifications_1",
    184: "14_Settings_09_Notifications_2",
    185: "12_Health_08_Fasting_1",
    186: "12_Health_09_Fasting_2",
    187: "12_Health_10_Fasting_3",
    188: "12_Health_11_Fasting_4",
    189: "12_Health_12_Fasting_5",
    190: "12_Health_13_Sleep_1",
    191: "12_Health_14_Sleep_2",
    192: "12_Health_15_Sleep_3",
    193: "13_Habits_07_Goals_1",
    194: "13_Habits_08_Goals_2",
    195: "13_Habits_09_Goals_3",
    196: "13_Habits_10_Goals_4",
    197: "14_Settings_10_Account_1",
    198: "14_Settings_11_Account_2",
    199: "14_Settings_12_Account_3",
    200: "14_Settings_13_ExportData",
}


def main():
    print("=" * 50)
    print("截图重命名 - 扁平化结构")
    print("=" * 50)
    
    # 创建输出文件夹
    if os.path.exists(OUTPUT_FOLDER):
        shutil.rmtree(OUTPUT_FOLDER)
    os.makedirs(OUTPUT_FOLDER)
    
    # 重命名并复制
    success_count = 0
    for old_num, new_name in RENAME_MAP.items():
        old_path = os.path.join(SOURCE_FOLDER, f"Screen_{old_num:03d}.png")
        new_path = os.path.join(OUTPUT_FOLDER, f"{new_name}.png")
        
        if os.path.exists(old_path):
            shutil.copy2(old_path, new_path)
            success_count += 1
            print(f"  Screen_{old_num:03d}.png -> {new_name}.png")
    
    print()
    print(f"[OK] 完成！已重命名 {success_count} 张截图")
    print(f"[OK] 输出目录: {OUTPUT_FOLDER}")


if __name__ == "__main__":
    main()









"""
截图重命名脚本 - 扁平化结构，方便导入Figma
"""

import os
import shutil

SOURCE_FOLDER = "MFP_Screens_Downloaded"
OUTPUT_FOLDER = "Screens"

# 截图命名映射：原始编号 -> 新文件名
RENAME_MAP = {
    # 01_Launch - 启动
    1: "01_Launch_01_SplashScreen",
    
    # 02_Welcome - 欢迎轮播
    2: "02_Welcome_01_ValueProp_Tracking",
    3: "02_Welcome_02_ValueProp_Impact",
    4: "02_Welcome_03_ValueProp_Habits",
    
    # 03_SignUp - 注册入口
    5: "03_SignUp_01_MethodSelection",
    
    # 04_Onboard - 核心引导流程
    6: "04_Onboard_01_NameInput",
    7: "04_Onboard_02_GoalsSelection",
    8: "04_Onboard_03_GoalsMotivation",
    9: "04_Onboard_04_BarriersSurvey",
    10: "04_Onboard_05_BarriersEmpathy",
    11: "04_Onboard_06_HabitsSelection",
    12: "04_Onboard_07_HabitsMotivation",
    13: "04_Onboard_08_MealPlanFrequency",
    14: "04_Onboard_09_MealPlanMotivation",
    15: "04_Onboard_10_WeeklyPlanInterest",
    16: "04_Onboard_11_ActivityLevel",
    17: "04_Onboard_12_PersonalInfo",
    18: "04_Onboard_13_PersonalInfoFilled",
    19: "04_Onboard_14_BodyMetrics",
    20: "04_Onboard_15_WeeklyGoal",
    21: "04_Onboard_16_AccountCreation",
    22: "04_Onboard_17_AttributionSurvey",
    23: "04_Onboard_18_CalorieGoalResult",
    
    # 05_Paywall - 付费墙
    24: "05_Paywall_01_NotificationPermission",
    25: "05_Paywall_02_MotionPermission",
    26: "05_Paywall_03_PremiumIntro",
    27: "05_Paywall_04_PlansComparison",
    28: "05_Paywall_05_PremiumPlusIntro",
    29: "05_Paywall_06_PurchaseConfirm",
    30: "05_Paywall_07_PurchaseSuccess",
    
    # 06_MealPlan - 餐计划引导
    31: "06_MealPlan_01_PremiumWelcome",
    32: "06_MealPlan_02_MealPlannerIntro",
    33: "06_MealPlan_03_GoalsSelection",
    34: "06_MealPlan_04_MotivationLevel",
    35: "06_MealPlan_05_EatingChallenge",
    36: "06_MealPlan_06_ChangePace",
    37: "06_MealPlan_07_DietType",
    38: "06_MealPlan_08_DietDetail",
    39: "06_MealPlan_09_MealsFrequency",
    40: "06_MealPlan_10_Macronutrient",
    41: "06_MealPlan_11_Allergies",
    42: "06_MealPlan_12_Dislikes_1",
    43: "06_MealPlan_13_Dislikes_2",
    44: "06_MealPlan_14_Dislikes_3",
    45: "06_MealPlan_15_CookingSkills",
    46: "06_MealPlan_16_CookingTime_1",
    47: "06_MealPlan_17_CookingTime_2",
    48: "06_MealPlan_18_CookingTime_3",
    49: "06_MealPlan_19_LeftoverPref_1",
    50: "06_MealPlan_20_LeftoverPref_2",
    51: "06_MealPlan_21_KitchenEquip_1",
    52: "06_MealPlan_22_KitchenEquip_2",
    53: "06_MealPlan_23_IngredientPref_1",
    54: "06_MealPlan_24_IngredientPref_2",
    55: "06_MealPlan_25_IngredientPref_3",
    56: "06_MealPlan_26_IngredientPref_4",
    57: "06_MealPlan_27_IngredientPref_5",
    58: "06_MealPlan_28_IngredientPref_6",
    59: "06_MealPlan_29_Calculating_1",
    60: "06_MealPlan_30_Calculating_2",
    61: "06_MealPlan_31_PlanSummary_1",
    62: "06_MealPlan_32_PlanSummary_2",
    63: "06_MealPlan_33_PlanSummary_3",
    64: "06_MealPlan_34_PlanSummary_4",
    65: "06_MealPlan_35_StartDate_1",
    66: "06_MealPlan_36_StartDate_2",
    67: "06_MealPlan_37_MealReview_1",
    68: "06_MealPlan_38_MealReview_2",
    69: "06_MealPlan_39_MealReview_3",
    70: "06_MealPlan_40_MealReview_4",
    71: "06_MealPlan_41_MealReview_5",
    72: "06_MealPlan_42_MealReview_6",
    73: "06_MealPlan_43_RecipeSwap_1",
    74: "06_MealPlan_44_RecipeSwap_2",
    75: "06_MealPlan_45_RecipeSwap_3",
    76: "06_MealPlan_46_RecipeSwap_4",
    77: "06_MealPlan_47_RecipeSwap_5",
    78: "06_MealPlan_48_SnacksReview_1",
    79: "06_MealPlan_49_SnacksReview_2",
    80: "06_MealPlan_50_SnacksReview_3",
    81: "06_MealPlan_51_PlanCreated_1",
    82: "06_MealPlan_52_PlanCreated_2",
    
    # 07_Tutorial - 应用教程
    83: "08_Main_01_Diary_1",
    84: "08_Main_02_Diary_2",
    85: "08_Main_03_Diary_3",
    86: "08_Main_04_Diary_4",
    87: "08_Main_05_Plan_Meal_1",
    88: "08_Main_06_Plan_Meal_2",
    89: "08_Main_07_Plan_Meal_3",
    90: "08_Main_08_Plan_Groceries_1",
    91: "08_Main_09_Plan_Groceries_2",
    92: "08_Main_10_Plan_Groceries_3",
    93: "08_Main_11_More_1",
    94: "08_Main_12_More_2",
    95: "07_Tutorial_01_LoggingProgress",
    96: "07_Tutorial_02_CelebrateChoices",
    97: "07_Tutorial_03_FeatureTip_1",
    98: "07_Tutorial_04_FeatureTip_2",
    99: "08_Main_13_Dashboard_1",
    100: "10_Recipe_01_NutritionOverview_1",
    101: "10_Recipe_02_NutritionOverview_2",
    102: "10_Recipe_03_NutritionOverview_3",
    103: "10_Recipe_04_CalorieBreakdown_1",
    104: "10_Recipe_05_CalorieBreakdown_2",
    105: "09_FoodLog_01_Search_1",
    106: "09_FoodLog_02_Search_2",
    107: "09_FoodLog_03_Search_3",
    108: "08_Main_14_Dashboard_2",
    109: "08_Main_15_Dashboard_3",
    110: "08_Main_16_Dashboard_4",
    111: "08_Main_17_Dashboard_5",
    112: "13_Habits_01_Setup_1",
    113: "13_Habits_02_Setup_2",
    114: "13_Habits_03_Setup_3",
    115: "13_Habits_04_Setup_4",
    116: "13_Habits_05_Setup_5",
    117: "13_Habits_06_Streaks",
    118: "12_Health_01_WeightProgress_1",
    119: "12_Health_02_WeightProgress_2",
    120: "12_Health_03_BodyMeasure_1",
    121: "12_Health_04_BodyMeasure_2",
    122: "12_Health_05_BodyMeasure_3",
    123: "09_FoodLog_04_AddDetail_1",
    124: "09_FoodLog_05_AddDetail_2",
    125: "09_FoodLog_06_AddDetail_3",
    126: "09_FoodLog_07_AddDetail_4",
    127: "09_FoodLog_08_AddDetail_5",
    128: "09_FoodLog_09_AddDetail_6",
    129: "09_FoodLog_10_AddDetail_7",
    130: "09_FoodLog_11_AddDetail_8",
    131: "09_FoodLog_12_BarcodeScan_1",
    132: "09_FoodLog_13_BarcodeScan_2",
    133: "09_FoodLog_14_BarcodeScan_3",
    134: "09_FoodLog_15_QuickAdd_1",
    135: "09_FoodLog_16_QuickAdd_2",
    136: "12_Health_06_Water_1",
    137: "12_Health_07_Water_2",
    138: "08_Main_18_Dashboard_6",
    139: "08_Main_19_Dashboard_7",
    140: "08_Main_20_Dashboard_8",
    141: "08_Main_21_Dashboard_9",
    142: "11_Exercise_01_Log_1",
    143: "11_Exercise_02_Log_2",
    144: "11_Exercise_03_Log_3",
    145: "11_Exercise_04_Log_4",
    146: "11_Exercise_05_Log_5",
    147: "11_Exercise_06_Log_6",
    148: "11_Exercise_07_Steps_1",
    149: "11_Exercise_08_Steps_2",
    150: "11_Exercise_09_Video_1",
    151: "11_Exercise_10_Video_2",
    152: "11_Exercise_11_Video_3",
    153: "11_Exercise_12_Workout_1",
    154: "11_Exercise_13_Workout_2",
    155: "11_Exercise_14_Workout_3",
    156: "11_Exercise_15_Workout_4",
    157: "11_Exercise_16_Workout_5",
    158: "11_Exercise_17_Workout_6",
    159: "11_Exercise_18_Workout_7",
    160: "10_Recipe_06_RecipeDetail_1",
    161: "10_Recipe_07_RecipeDetail_2",
    162: "10_Recipe_08_RecipeDetail_3",
    163: "10_Recipe_09_RecipeDetail_4",
    164: "10_Recipe_10_RecipeDetail_5",
    165: "10_Recipe_11_RecipeList_1",
    166: "10_Recipe_12_RecipeList_2",
    167: "10_Recipe_13_RecipeList_3",
    168: "09_FoodLog_17_MealScan_1",
    169: "09_FoodLog_18_MealScan_2",
    170: "09_FoodLog_19_MealScan_3",
    171: "09_FoodLog_20_MealScan_4",
    172: "09_FoodLog_21_MealScan_5",
    173: "09_FoodLog_22_History_1",
    174: "09_FoodLog_23_History_2",
    175: "09_FoodLog_24_History_3",
    176: "14_Settings_01_Profile_1",
    177: "14_Settings_02_Profile_2",
    178: "14_Settings_03_Profile_3",
    179: "14_Settings_04_Premium_1",
    180: "14_Settings_05_Premium_2",
    181: "14_Settings_06_Premium_3",
    182: "14_Settings_07_Premium_4",
    183: "14_Settings_08_Notifications_1",
    184: "14_Settings_09_Notifications_2",
    185: "12_Health_08_Fasting_1",
    186: "12_Health_09_Fasting_2",
    187: "12_Health_10_Fasting_3",
    188: "12_Health_11_Fasting_4",
    189: "12_Health_12_Fasting_5",
    190: "12_Health_13_Sleep_1",
    191: "12_Health_14_Sleep_2",
    192: "12_Health_15_Sleep_3",
    193: "13_Habits_07_Goals_1",
    194: "13_Habits_08_Goals_2",
    195: "13_Habits_09_Goals_3",
    196: "13_Habits_10_Goals_4",
    197: "14_Settings_10_Account_1",
    198: "14_Settings_11_Account_2",
    199: "14_Settings_12_Account_3",
    200: "14_Settings_13_ExportData",
}


def main():
    print("=" * 50)
    print("截图重命名 - 扁平化结构")
    print("=" * 50)
    
    # 创建输出文件夹
    if os.path.exists(OUTPUT_FOLDER):
        shutil.rmtree(OUTPUT_FOLDER)
    os.makedirs(OUTPUT_FOLDER)
    
    # 重命名并复制
    success_count = 0
    for old_num, new_name in RENAME_MAP.items():
        old_path = os.path.join(SOURCE_FOLDER, f"Screen_{old_num:03d}.png")
        new_path = os.path.join(OUTPUT_FOLDER, f"{new_name}.png")
        
        if os.path.exists(old_path):
            shutil.copy2(old_path, new_path)
            success_count += 1
            print(f"  Screen_{old_num:03d}.png -> {new_name}.png")
    
    print()
    print(f"[OK] 完成！已重命名 {success_count} 张截图")
    print(f"[OK] 输出目录: {OUTPUT_FOLDER}")


if __name__ == "__main__":
    main()













































































