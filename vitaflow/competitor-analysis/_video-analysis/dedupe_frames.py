# -*- coding: utf-8 -*-
"""
视频帧去重脚本
- 比较相邻帧的相似度
- 删除相似度>阈值的重复帧
- 保留关键帧（页面切换点）
"""

import os
import sys
from PIL import Image
import imagehash
from pathlib import Path
import shutil

# 配置
FRAMES_DIR = Path("calai_frames")
OUTPUT_DIR = Path("calai_keyframes")
SIMILARITY_THRESHOLD = 8  # 汉明距离阈值，越小越严格

def get_image_hash(filepath):
    """计算图片的感知哈希"""
    try:
        img = Image.open(filepath)
        return imagehash.phash(img)
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return None

def main():
    print("=" * 60)
    print("  VIDEO FRAME DEDUPLICATION")
    print("=" * 60)
    
    # 创建输出目录
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    # 获取所有帧
    frames = sorted(FRAMES_DIR.glob("*.jpg"))
    total = len(frames)
    print(f"\nTotal frames: {total}")
    
    if total == 0:
        print("No frames found!")
        return
    
    # 去重
    keyframes = []
    prev_hash = None
    
    for i, frame in enumerate(frames):
        curr_hash = get_image_hash(frame)
        
        if curr_hash is None:
            continue
        
        # 第一帧或与前一帧差异大于阈值
        if prev_hash is None or (curr_hash - prev_hash) > SIMILARITY_THRESHOLD:
            keyframes.append(frame)
            prev_hash = curr_hash
        
        # 进度
        if (i + 1) % 100 == 0:
            print(f"Processed {i + 1}/{total} frames, kept {len(keyframes)} keyframes")
    
    print(f"\nDeduplication complete!")
    print(f"Original: {total} frames")
    print(f"Keyframes: {len(keyframes)} frames")
    print(f"Reduction: {100 * (1 - len(keyframes) / total):.1f}%")
    
    # 复制关键帧到输出目录
    print(f"\nCopying keyframes to {OUTPUT_DIR}...")
    for i, frame in enumerate(keyframes):
        # 重命名为顺序编号
        new_name = f"key_{i + 1:04d}.jpg"
        shutil.copy(frame, OUTPUT_DIR / new_name)
    
    print(f"Done! Keyframes saved to: {OUTPUT_DIR.absolute()}")
    
    # 输出统计
    print("\n" + "=" * 60)
    print(f"  RESULT: {len(keyframes)} keyframes extracted")
    print("=" * 60)

if __name__ == "__main__":
    main()


"""
视频帧去重脚本
- 比较相邻帧的相似度
- 删除相似度>阈值的重复帧
- 保留关键帧（页面切换点）
"""

import os
import sys
from PIL import Image
import imagehash
from pathlib import Path
import shutil

# 配置
FRAMES_DIR = Path("calai_frames")
OUTPUT_DIR = Path("calai_keyframes")
SIMILARITY_THRESHOLD = 8  # 汉明距离阈值，越小越严格

def get_image_hash(filepath):
    """计算图片的感知哈希"""
    try:
        img = Image.open(filepath)
        return imagehash.phash(img)
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return None

def main():
    print("=" * 60)
    print("  VIDEO FRAME DEDUPLICATION")
    print("=" * 60)
    
    # 创建输出目录
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    # 获取所有帧
    frames = sorted(FRAMES_DIR.glob("*.jpg"))
    total = len(frames)
    print(f"\nTotal frames: {total}")
    
    if total == 0:
        print("No frames found!")
        return
    
    # 去重
    keyframes = []
    prev_hash = None
    
    for i, frame in enumerate(frames):
        curr_hash = get_image_hash(frame)
        
        if curr_hash is None:
            continue
        
        # 第一帧或与前一帧差异大于阈值
        if prev_hash is None or (curr_hash - prev_hash) > SIMILARITY_THRESHOLD:
            keyframes.append(frame)
            prev_hash = curr_hash
        
        # 进度
        if (i + 1) % 100 == 0:
            print(f"Processed {i + 1}/{total} frames, kept {len(keyframes)} keyframes")
    
    print(f"\nDeduplication complete!")
    print(f"Original: {total} frames")
    print(f"Keyframes: {len(keyframes)} frames")
    print(f"Reduction: {100 * (1 - len(keyframes) / total):.1f}%")
    
    # 复制关键帧到输出目录
    print(f"\nCopying keyframes to {OUTPUT_DIR}...")
    for i, frame in enumerate(keyframes):
        # 重命名为顺序编号
        new_name = f"key_{i + 1:04d}.jpg"
        shutil.copy(frame, OUTPUT_DIR / new_name)
    
    print(f"Done! Keyframes saved to: {OUTPUT_DIR.absolute()}")
    
    # 输出统计
    print("\n" + "=" * 60)
    print(f"  RESULT: {len(keyframes)} keyframes extracted")
    print("=" * 60)

if __name__ == "__main__":
    main()


"""
视频帧去重脚本
- 比较相邻帧的相似度
- 删除相似度>阈值的重复帧
- 保留关键帧（页面切换点）
"""

import os
import sys
from PIL import Image
import imagehash
from pathlib import Path
import shutil

# 配置
FRAMES_DIR = Path("calai_frames")
OUTPUT_DIR = Path("calai_keyframes")
SIMILARITY_THRESHOLD = 8  # 汉明距离阈值，越小越严格

def get_image_hash(filepath):
    """计算图片的感知哈希"""
    try:
        img = Image.open(filepath)
        return imagehash.phash(img)
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return None

def main():
    print("=" * 60)
    print("  VIDEO FRAME DEDUPLICATION")
    print("=" * 60)
    
    # 创建输出目录
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    # 获取所有帧
    frames = sorted(FRAMES_DIR.glob("*.jpg"))
    total = len(frames)
    print(f"\nTotal frames: {total}")
    
    if total == 0:
        print("No frames found!")
        return
    
    # 去重
    keyframes = []
    prev_hash = None
    
    for i, frame in enumerate(frames):
        curr_hash = get_image_hash(frame)
        
        if curr_hash is None:
            continue
        
        # 第一帧或与前一帧差异大于阈值
        if prev_hash is None or (curr_hash - prev_hash) > SIMILARITY_THRESHOLD:
            keyframes.append(frame)
            prev_hash = curr_hash
        
        # 进度
        if (i + 1) % 100 == 0:
            print(f"Processed {i + 1}/{total} frames, kept {len(keyframes)} keyframes")
    
    print(f"\nDeduplication complete!")
    print(f"Original: {total} frames")
    print(f"Keyframes: {len(keyframes)} frames")
    print(f"Reduction: {100 * (1 - len(keyframes) / total):.1f}%")
    
    # 复制关键帧到输出目录
    print(f"\nCopying keyframes to {OUTPUT_DIR}...")
    for i, frame in enumerate(keyframes):
        # 重命名为顺序编号
        new_name = f"key_{i + 1:04d}.jpg"
        shutil.copy(frame, OUTPUT_DIR / new_name)
    
    print(f"Done! Keyframes saved to: {OUTPUT_DIR.absolute()}")
    
    # 输出统计
    print("\n" + "=" * 60)
    print(f"  RESULT: {len(keyframes)} keyframes extracted")
    print("=" * 60)

if __name__ == "__main__":
    main()


"""
视频帧去重脚本
- 比较相邻帧的相似度
- 删除相似度>阈值的重复帧
- 保留关键帧（页面切换点）
"""

import os
import sys
from PIL import Image
import imagehash
from pathlib import Path
import shutil

# 配置
FRAMES_DIR = Path("calai_frames")
OUTPUT_DIR = Path("calai_keyframes")
SIMILARITY_THRESHOLD = 8  # 汉明距离阈值，越小越严格

def get_image_hash(filepath):
    """计算图片的感知哈希"""
    try:
        img = Image.open(filepath)
        return imagehash.phash(img)
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return None

def main():
    print("=" * 60)
    print("  VIDEO FRAME DEDUPLICATION")
    print("=" * 60)
    
    # 创建输出目录
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    # 获取所有帧
    frames = sorted(FRAMES_DIR.glob("*.jpg"))
    total = len(frames)
    print(f"\nTotal frames: {total}")
    
    if total == 0:
        print("No frames found!")
        return
    
    # 去重
    keyframes = []
    prev_hash = None
    
    for i, frame in enumerate(frames):
        curr_hash = get_image_hash(frame)
        
        if curr_hash is None:
            continue
        
        # 第一帧或与前一帧差异大于阈值
        if prev_hash is None or (curr_hash - prev_hash) > SIMILARITY_THRESHOLD:
            keyframes.append(frame)
            prev_hash = curr_hash
        
        # 进度
        if (i + 1) % 100 == 0:
            print(f"Processed {i + 1}/{total} frames, kept {len(keyframes)} keyframes")
    
    print(f"\nDeduplication complete!")
    print(f"Original: {total} frames")
    print(f"Keyframes: {len(keyframes)} frames")
    print(f"Reduction: {100 * (1 - len(keyframes) / total):.1f}%")
    
    # 复制关键帧到输出目录
    print(f"\nCopying keyframes to {OUTPUT_DIR}...")
    for i, frame in enumerate(keyframes):
        # 重命名为顺序编号
        new_name = f"key_{i + 1:04d}.jpg"
        shutil.copy(frame, OUTPUT_DIR / new_name)
    
    print(f"Done! Keyframes saved to: {OUTPUT_DIR.absolute()}")
    
    # 输出统计
    print("\n" + "=" * 60)
    print(f"  RESULT: {len(keyframes)} keyframes extracted")
    print("=" * 60)

if __name__ == "__main__":
    main()



"""
视频帧去重脚本
- 比较相邻帧的相似度
- 删除相似度>阈值的重复帧
- 保留关键帧（页面切换点）
"""

import os
import sys
from PIL import Image
import imagehash
from pathlib import Path
import shutil

# 配置
FRAMES_DIR = Path("calai_frames")
OUTPUT_DIR = Path("calai_keyframes")
SIMILARITY_THRESHOLD = 8  # 汉明距离阈值，越小越严格

def get_image_hash(filepath):
    """计算图片的感知哈希"""
    try:
        img = Image.open(filepath)
        return imagehash.phash(img)
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return None

def main():
    print("=" * 60)
    print("  VIDEO FRAME DEDUPLICATION")
    print("=" * 60)
    
    # 创建输出目录
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    # 获取所有帧
    frames = sorted(FRAMES_DIR.glob("*.jpg"))
    total = len(frames)
    print(f"\nTotal frames: {total}")
    
    if total == 0:
        print("No frames found!")
        return
    
    # 去重
    keyframes = []
    prev_hash = None
    
    for i, frame in enumerate(frames):
        curr_hash = get_image_hash(frame)
        
        if curr_hash is None:
            continue
        
        # 第一帧或与前一帧差异大于阈值
        if prev_hash is None or (curr_hash - prev_hash) > SIMILARITY_THRESHOLD:
            keyframes.append(frame)
            prev_hash = curr_hash
        
        # 进度
        if (i + 1) % 100 == 0:
            print(f"Processed {i + 1}/{total} frames, kept {len(keyframes)} keyframes")
    
    print(f"\nDeduplication complete!")
    print(f"Original: {total} frames")
    print(f"Keyframes: {len(keyframes)} frames")
    print(f"Reduction: {100 * (1 - len(keyframes) / total):.1f}%")
    
    # 复制关键帧到输出目录
    print(f"\nCopying keyframes to {OUTPUT_DIR}...")
    for i, frame in enumerate(keyframes):
        # 重命名为顺序编号
        new_name = f"key_{i + 1:04d}.jpg"
        shutil.copy(frame, OUTPUT_DIR / new_name)
    
    print(f"Done! Keyframes saved to: {OUTPUT_DIR.absolute()}")
    
    # 输出统计
    print("\n" + "=" * 60)
    print(f"  RESULT: {len(keyframes)} keyframes extracted")
    print("=" * 60)

if __name__ == "__main__":
    main()


"""
视频帧去重脚本
- 比较相邻帧的相似度
- 删除相似度>阈值的重复帧
- 保留关键帧（页面切换点）
"""

import os
import sys
from PIL import Image
import imagehash
from pathlib import Path
import shutil

# 配置
FRAMES_DIR = Path("calai_frames")
OUTPUT_DIR = Path("calai_keyframes")
SIMILARITY_THRESHOLD = 8  # 汉明距离阈值，越小越严格

def get_image_hash(filepath):
    """计算图片的感知哈希"""
    try:
        img = Image.open(filepath)
        return imagehash.phash(img)
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return None

def main():
    print("=" * 60)
    print("  VIDEO FRAME DEDUPLICATION")
    print("=" * 60)
    
    # 创建输出目录
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    # 获取所有帧
    frames = sorted(FRAMES_DIR.glob("*.jpg"))
    total = len(frames)
    print(f"\nTotal frames: {total}")
    
    if total == 0:
        print("No frames found!")
        return
    
    # 去重
    keyframes = []
    prev_hash = None
    
    for i, frame in enumerate(frames):
        curr_hash = get_image_hash(frame)
        
        if curr_hash is None:
            continue
        
        # 第一帧或与前一帧差异大于阈值
        if prev_hash is None or (curr_hash - prev_hash) > SIMILARITY_THRESHOLD:
            keyframes.append(frame)
            prev_hash = curr_hash
        
        # 进度
        if (i + 1) % 100 == 0:
            print(f"Processed {i + 1}/{total} frames, kept {len(keyframes)} keyframes")
    
    print(f"\nDeduplication complete!")
    print(f"Original: {total} frames")
    print(f"Keyframes: {len(keyframes)} frames")
    print(f"Reduction: {100 * (1 - len(keyframes) / total):.1f}%")
    
    # 复制关键帧到输出目录
    print(f"\nCopying keyframes to {OUTPUT_DIR}...")
    for i, frame in enumerate(keyframes):
        # 重命名为顺序编号
        new_name = f"key_{i + 1:04d}.jpg"
        shutil.copy(frame, OUTPUT_DIR / new_name)
    
    print(f"Done! Keyframes saved to: {OUTPUT_DIR.absolute()}")
    
    # 输出统计
    print("\n" + "=" * 60)
    print(f"  RESULT: {len(keyframes)} keyframes extracted")
    print("=" * 60)

if __name__ == "__main__":
    main()






































































