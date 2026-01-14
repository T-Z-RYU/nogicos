# -*- coding: utf-8 -*-
"""
关键帧分析脚本 - 三层分类体系 (Stage / Module / Feature)
- 用AI识别每个关键帧的页面类型
- 检测页面切换点
- 推断跳转关系
"""

import os
import sys
import json
import base64
from pathlib import Path
from anthropic import Anthropic

# 配置
KEYFRAMES_DIR = Path("calai_keyframes")
OUTPUT_FILE = Path("calai_analysis.json")
BATCH_SIZE = 20  # 每批分析的帧数

# 加载API密钥
def load_api_key():
    config_path = Path("C:/Users/WIN/Desktop/Cursor Project/PM_Screenshot_Tool/config/api_keys.json")
    
    if config_path.exists():
        with open(config_path, 'r') as f:
            config = json.load(f)
            return config.get("ANTHROPIC_API_KEY")
    
    return os.environ.get("ANTHROPIC_API_KEY")

# 加载标准词表
def load_taxonomy():
    taxonomy_path = Path("C:/Users/WIN/Desktop/Cursor Project/PM_Screenshot_Tool/config/taxonomy.json")
    if taxonomy_path.exists():
        with open(taxonomy_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

# 新的三层分类 Prompt
ANALYSIS_PROMPT = """你是一位资深产品经理，正在分析App的视频帧序列。

我会给你一组连续的App截图帧，请使用三层分类体系进行分析：

## 三层分类体系 (Stage / Module / Feature)

### 第一层 - Stage（阶段）
- **Onboarding**: 从启动到首次使用核心功能前的所有页面
- **Core**: 核心功能使用阶段

### 第二层 - Module（模块）

**Onboarding阶段的Module：**
- Welcome: 启动页、欢迎页、价值主张
- Profile: 身份信息收集（性别、年龄、身高体重）
- Goal: 目标设定（方向、数值、时间线）
- Preference: 偏好收集（饮食、健身习惯）
- Permission: 权限请求（通知、位置、追踪、健康）
- Growth: 增长运营（归因调研、推荐码）
- Initialization: 初始化加载
- Paywall: 付费墙（套餐选择、价格展示、试用优惠）
- Registration: 账号注册（登录方式、邮箱、密码、OAuth）

**Core阶段的Module：**
- Dashboard: 首页/概览
- Tracking: 数据记录（食物搜索、记录、扫描）
- Progress: 进度统计（图表、趋势、历史）
- Content: 内容展示（文章、教程）
- Social: 社交功能（好友、动态）
- Profile_Core: 个人中心
- Settings: 设置

### 第三层 - Feature（功能）
使用PascalCase命名，常见的Feature包括：
- Onboarding: Splash, ValueProp, GenderSelect, AgeInput, HeightInput, WeightInput, DirectionSelect, TargetInput, NotificationAsk, HealthAsk, PlanSelect, PriceDisplay, EmailInput, OAuthApple
- Core: Overview, Summary, FoodSearch, FoodLog, PhotoScan, WeeklyChart, TrendAnalysis, AccountInfo, Subscription

### 页面角色 (Role)
- Entry: 入口页面
- Browse: 浏览列表
- Detail: 详情页
- Action: 操作页面
- Result: 结果页
- Modal: 弹窗/底部弹出

### 转场类型 (Transition)
- push: 前进到新页面
- pop: 返回上一页
- modal: 弹窗/底部弹出
- tab: Tab切换
- replace: 页面替换

## 输出格式

```json
{
  "frames": [
    {
      "index": 1,
      "stage": "Onboarding",
      "module": "Welcome",
      "feature": "Splash",
      "role": "Entry",
      "description": "启动页，显示Cal AI Logo",
      "is_new_page": true,
      "transition_from_prev": null
    },
    {
      "index": 2,
      "stage": "Onboarding",
      "module": "Welcome",
      "feature": "Splash",
      "role": "Entry",
      "description": "启动页，与上一帧相同",
      "is_new_page": false,
      "transition_from_prev": null
    },
    {
      "index": 3,
      "stage": "Onboarding",
      "module": "Profile",
      "feature": "GenderSelect",
      "role": "Action",
      "description": "性别选择页",
      "is_new_page": true,
      "transition_from_prev": "push"
    }
  ],
  "summary": {
    "total_pages": 10,
    "stages": {"Onboarding": 8, "Core": 2},
    "modules": {"Welcome": 2, "Profile": 3, "Goal": 2, ...}
  }
}
```

## 重要规则
1. Stage只有两个值：Onboarding 或 Core
2. Module必须与Stage匹配（参考上面的列表）
3. Feature使用PascalCase，如果没有匹配的Feature，使用"Other"
4. 如果页面没有变化，is_new_page = false，保持与上一帧相同的分类
5. 保持流程顺序的一致性：Onboarding阶段应该在Core之前

请分析以下帧序列，只输出JSON："""


def encode_image(filepath):
    """将图片编码为base64"""
    with open(filepath, "rb") as f:
        return base64.standard_b64encode(f.read()).decode("utf-8")


def analyze_batch(client, frames, start_idx):
    """分析一批帧"""
    print(f"\n  Analyzing frames {start_idx + 1} - {start_idx + len(frames)}...")
    
    # 构建消息
    content = [{"type": "text", "text": ANALYSIS_PROMPT}]
    
    for i, frame in enumerate(frames):
        # 添加帧编号
        content.append({
            "type": "text",
            "text": f"\n--- Frame {start_idx + i + 1} ---"
        })
        # 添加图片
        content.append({
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": "image/jpeg",
                "data": encode_image(frame)
            }
        })
    
    # 调用API
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=8192,
        messages=[{"role": "user", "content": content}]
    )
    
    # 解析结果
    result_text = response.content[0].text
    
    # 尝试提取JSON
    try:
        if "```json" in result_text:
            result_text = result_text.split("```json")[1].split("```")[0]
        elif "```" in result_text:
            result_text = result_text.split("```")[1].split("```")[0]
        return json.loads(result_text)
    except:
        print(f"  Warning: Could not parse JSON response")
        return {"raw": result_text}


def main():
    print("=" * 60)
    print("  KEYFRAME ANALYSIS (3-Layer Classification)")
    print("=" * 60)
    
    # 初始化
    api_key = load_api_key()
    if not api_key:
        print("Error: No API key found!")
        return
    
    client = Anthropic(api_key=api_key)
    
    # 加载词表（可选，用于验证）
    taxonomy = load_taxonomy()
    if taxonomy:
        print(f"\n[INFO] Loaded taxonomy v{taxonomy.get('version', '?')}")
    
    # 获取所有关键帧
    frames = sorted(KEYFRAMES_DIR.glob("*.jpg"))
    total = len(frames)
    print(f"\nTotal keyframes: {total}")
    
    if total == 0:
        print("No keyframes found!")
        return
    
    # 分析所有帧
    sample_size = total
    print(f"Analyzing all {sample_size} frames...")
    
    # 分批分析
    all_results = []
    for i in range(0, sample_size, BATCH_SIZE):
        batch = frames[i:i + BATCH_SIZE]
        result = analyze_batch(client, batch, i)
        if "frames" in result:
            all_results.extend(result["frames"])
        else:
            all_results.append(result)
    
    # 保存结果
    output = {
        "product": "Cal AI",
        "total_keyframes": total,
        "analyzed": sample_size,
        "classification_version": "3-layer",
        "frames": all_results
    }
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\nAnalysis saved to: {OUTPUT_FILE}")
    
    # 统计
    print("\n" + "=" * 60)
    print("  ANALYSIS SUMMARY")
    print("=" * 60)
    
    if all_results and isinstance(all_results[0], dict) and "stage" in all_results[0]:
        stages = {}
        modules = {}
        features = {}
        roles = {}
        transitions = {}
        page_changes = 0
        
        for frame in all_results:
            stage = frame.get("stage", "Unknown")
            module = frame.get("module", "Unknown")
            feature = frame.get("feature", "Unknown")
            role = frame.get("role", "Unknown")
            transition = frame.get("transition_from_prev")
            
            stages[stage] = stages.get(stage, 0) + 1
            modules[module] = modules.get(module, 0) + 1
            features[feature] = features.get(feature, 0) + 1
            roles[role] = roles.get(role, 0) + 1
            if transition:
                transitions[transition] = transitions.get(transition, 0) + 1
            if frame.get("is_new_page"):
                page_changes += 1
        
        print(f"\nPage changes detected: {page_changes}")
        
        print(f"\nStages:")
        for stage, count in sorted(stages.items(), key=lambda x: -x[1]):
            print(f"  {stage}: {count}")
        
        print(f"\nModules:")
        for module, count in sorted(modules.items(), key=lambda x: -x[1])[:15]:
            print(f"  {module}: {count}")
        
        print(f"\nFeatures (top 10):")
        for feature, count in sorted(features.items(), key=lambda x: -x[1])[:10]:
            print(f"  {feature}: {count}")
        
        print(f"\nRoles:")
        for role, count in sorted(roles.items(), key=lambda x: -x[1]):
            print(f"  {role}: {count}")
        
        print(f"\nTransitions:")
        for transition, count in sorted(transitions.items(), key=lambda x: -x[1]):
            print(f"  {transition}: {count}")


if __name__ == "__main__":
    main()
