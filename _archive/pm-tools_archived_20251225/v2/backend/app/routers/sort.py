"""
截图排序相关 API
- 保存排序
- 应用排序（重命名文件）
- 删除截图
- 恢复截图
"""
import os
import json
import shutil
from datetime import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from ..config import settings

router = APIRouter()


class SortItem(BaseModel):
    """排序项"""
    original_file: str
    new_index: int


class SaveSortRequest(BaseModel):
    """保存排序请求"""
    project: str
    order: List[SortItem]


class DeleteScreensRequest(BaseModel):
    """删除截图请求"""
    project: str
    files: List[str]


class RestoreScreensRequest(BaseModel):
    """恢复截图请求"""
    project: str
    batch: str  # 删除批次时间戳


def get_project_path(project_name: str) -> str:
    """获取项目路径"""
    if project_name.startswith("downloads_2024/"):
        return os.path.join(settings.downloads_2024_dir, project_name.replace("downloads_2024/", ""))
    return os.path.join(settings.projects_dir, project_name)


def get_screens_dir(project_name: str, project_path: str) -> str:
    """获取截图目录"""
    is_downloads_2024 = project_name.startswith("downloads_2024/")
    
    if is_downloads_2024:
        return project_path
    else:
        screens_dir = os.path.join(project_path, "screens")
        if not os.path.exists(screens_dir):
            screens_dir = os.path.join(project_path, "Screens")
        return screens_dir


@router.post("/save-sort-order")
async def save_sort_order(data: SaveSortRequest):
    """保存排序结果（不重命名文件）"""
    project_path = get_project_path(data.project)
    
    if not os.path.exists(project_path):
        raise HTTPException(status_code=404, detail=f"项目不存在: {data.project}")
    
    # #region agent log
    import json as _json
    screens_dir = get_screens_dir(data.project, project_path)
    actual_files = sorted([f for f in os.listdir(screens_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]) if os.path.exists(screens_dir) else []
    with open(r"c:\Users\WIN\Desktop\Cursor Project\.cursor\debug.log", "a", encoding="utf-8") as _f:
        _f.write(_json.dumps({"location":"sort.py:save_sort_order","message":"SAVE_REQUEST","data":{"project":data.project,"order_count":len(data.order),"first5_order":[item.original_file for item in data.order[:5]],"last3_order":[item.original_file for item in data.order[-3:]],"actual_file_count":len(actual_files),"first5_actual":actual_files[:5],"last3_actual":actual_files[-3:]},"timestamp":__import__("time").time()*1000,"hypothesisId":"A"}) + "\n")
    # #endregion
    
    sort_file = os.path.join(project_path, "sort_order.json")
    backup_dir = os.path.join(project_path, "backups")
    
    try:
        # 1. 如果旧文件存在，先备份
        if os.path.exists(sort_file):
            os.makedirs(backup_dir, exist_ok=True)
            backup_file = os.path.join(
                backup_dir, 
                f"sort_order_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            shutil.copy(sort_file, backup_file)
            
            # 只保留最近 10 个备份
            backups = sorted([
                f for f in os.listdir(backup_dir) 
                if f.startswith("sort_order_")
            ], reverse=True)
            for old_backup in backups[10:]:
                os.remove(os.path.join(backup_dir, old_backup))
        
        # 2. 保存新数据
        sort_data = {
            "project": data.project,
            "saved_at": datetime.now().isoformat(),
            "order": [item.model_dump() for item in data.order]
        }
        with open(sort_file, "w", encoding="utf-8") as f:
            json.dump(sort_data, f, ensure_ascii=False, indent=2)
        
        return {"success": True, "message": f"排序已保存"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sort-order/{project_name:path}")
async def get_sort_order(project_name: str):
    """获取已保存的排序"""
    project_path = get_project_path(project_name)
    sort_file = os.path.join(project_path, "sort_order.json")
    
    if os.path.exists(sort_file):
        with open(sort_file, "r", encoding="utf-8") as f:
            return json.load(f)
    
    return {"project": project_name, "order": []}


@router.post("/apply-sort-order")
async def apply_sort_order(data: SaveSortRequest):
    """
    应用排序并重命名文件
    
    安全措施：
    1. 验证数据一致性
    2. 使用两阶段重命名避免冲突
    3. 保留完整备份
    """
    project_path = get_project_path(data.project)
    
    if not os.path.exists(project_path):
        raise HTTPException(status_code=404, detail=f"项目不存在: {data.project}")
    
    is_downloads_2024 = data.project.startswith("downloads_2024/")
    screens_dir = get_screens_dir(data.project, project_path)
    
    if not os.path.exists(screens_dir):
        raise HTTPException(status_code=404, detail="截图目录不存在")
    
    try:
        # ========== 1. 收集实际存在的图片文件 ==========
        actual_files = set()
        image_extensions = ('.png', '.jpg', '.jpeg', '.webp')
        
        # 根目录文件
        for f in os.listdir(screens_dir):
            if f.lower().endswith(image_extensions) and os.path.isfile(os.path.join(screens_dir, f)):
                actual_files.add(f)
        
        # screenshots 子目录文件
        screenshots_subdir = os.path.join(screens_dir, "screenshots")
        if os.path.exists(screenshots_subdir):
            for f in os.listdir(screenshots_subdir):
                if f.lower().endswith(image_extensions):
                    actual_files.add(f"screenshots/{f}")
        
        # ========== 2. 验证排序数据 ==========
        order_files = set(item.original_file for item in data.order)
        
        # 检查是否有文件缺失
        missing_in_order = actual_files - order_files
        missing_on_disk = order_files - actual_files
        
        if missing_on_disk:
            # 过滤掉不存在的文件，只处理存在的文件
            data.order = [item for item in data.order if item.original_file in actual_files]
        
        if len(data.order) == 0:
            raise HTTPException(status_code=400, detail="没有可处理的文件")
        
        # 重新分配索引（确保连续）
        for i, item in enumerate(data.order):
            item.new_index = i + 1
        
        # ========== 3. 创建备份 ==========
        backup_base = os.path.dirname(project_path)
        folder_name = os.path.basename(project_path)
        backup_dir = os.path.join(backup_base, f"{folder_name}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        shutil.copytree(screens_dir, backup_dir)
        
        # ========== 4. 两阶段安全重命名 ==========
        # 阶段一：所有文件先重命名为临时名称（避免冲突）
        temp_mapping = {}  # original_path -> temp_path
        
        for item in data.order:
            old_name = item.original_file
            
            # 确定源文件路径
            if "/" in old_name or "\\" in old_name:
                old_path = os.path.join(screens_dir, old_name.replace("/", os.sep).replace("\\", os.sep))
            else:
                old_path = os.path.join(screens_dir, old_name)
            
            if os.path.exists(old_path):
                # 临时文件名使用 UUID 避免冲突
                temp_name = f"_temp_{item.new_index:04d}_{os.path.basename(old_name)}"
                temp_path = os.path.join(screens_dir, temp_name)
                shutil.move(old_path, temp_path)
                temp_mapping[temp_path] = item
        
        # 删除 screenshots 子目录（如果存在且已清空）
        if os.path.exists(screenshots_subdir):
            try:
                os.rmdir(screenshots_subdir)
            except:
                pass
        
        # 阶段二：将临时文件重命名为最终名称
        for temp_path, item in temp_mapping.items():
            # 获取原始扩展名
            original_ext = os.path.splitext(item.original_file)[1]
            # 如果是子目录文件，只取文件名部分的扩展名
            if "/" in item.original_file or "\\" in item.original_file:
                original_ext = os.path.splitext(os.path.basename(item.original_file))[1]
            
            new_name = f"{item.new_index:04d}{original_ext}"
            new_path = os.path.join(screens_dir, new_name)
            
            if os.path.exists(temp_path):
                shutil.move(temp_path, new_path)
        
        # ========== 5. 清理缩略图缓存 ==========
        for thumb_dir_name in ['thumbs_small', 'thumbs_medium', 'thumbs_large']:
            thumb_dir = os.path.join(screens_dir, thumb_dir_name)
            if os.path.exists(thumb_dir):
                shutil.rmtree(thumb_dir, ignore_errors=True)
        
        # ========== 6. 保存应用记录 ==========
        sort_file = os.path.join(project_path, "sort_order_applied.json")
        final_files = sorted([f for f in os.listdir(screens_dir) if f.lower().endswith(image_extensions)])
        
        with open(sort_file, "w", encoding="utf-8") as f:
            json.dump({
                "project": data.project,
                "applied_at": datetime.now().isoformat(),
                "backup_dir": backup_dir,
                "final_count": len(final_files),
                "order": [item.model_dump() for item in data.order]
            }, f, ensure_ascii=False, indent=2)
        
        return {
            "success": True,
            "message": f"已重命名 {len(temp_mapping)} 张截图",
            "backup_dir": backup_dir,
            "final_count": len(final_files)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"重命名失败: {str(e)}")


@router.post("/delete-screens")
async def delete_screens(data: DeleteScreensRequest):
    """删除选中的截图（移动到 deleted 文件夹备份）"""
    project_path = get_project_path(data.project)
    
    if not os.path.exists(project_path):
        raise HTTPException(status_code=404, detail=f"项目不存在: {data.project}")
    
    screens_dir = get_screens_dir(data.project, project_path)
    
    if not os.path.exists(screens_dir):
        raise HTTPException(status_code=404, detail="截图目录不存在")
    
    try:
        # 创建 deleted 备份目录
        deleted_dir = os.path.join(project_path, "deleted")
        os.makedirs(deleted_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        batch_deleted_dir = os.path.join(deleted_dir, timestamp)
        os.makedirs(batch_deleted_dir, exist_ok=True)
        
        deleted_count = 0
        deleted_files = []
        
        for filename in data.files:
            file_path = os.path.join(screens_dir, filename)
            if os.path.exists(file_path):
                shutil.move(file_path, os.path.join(batch_deleted_dir, filename))
                deleted_count += 1
                deleted_files.append(filename)
        
        # 保存删除记录
        manifest_file = os.path.join(batch_deleted_dir, "manifest.json")
        with open(manifest_file, "w", encoding="utf-8") as f:
            json.dump({
                "project": data.project,
                "deleted_at": datetime.now().isoformat(),
                "files": deleted_files
            }, f, ensure_ascii=False, indent=2)
        
        return {
            "success": True,
            "deleted_count": deleted_count,
            "batch": timestamp,
            "message": f"已删除 {deleted_count} 张截图"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/deleted-screens/{project_name:path}")
async def get_deleted_screens(project_name: str):
    """获取项目已删除的截图列表"""
    project_path = get_project_path(project_name)
    deleted_dir = os.path.join(project_path, "deleted")
    
    result = {
        "total": 0,
        "batches": []
    }
    
    if not os.path.exists(deleted_dir):
        return result
    
    for batch_name in sorted(os.listdir(deleted_dir), reverse=True):
        batch_path = os.path.join(deleted_dir, batch_name)
        if not os.path.isdir(batch_path):
            continue
        
        manifest_file = os.path.join(batch_path, "manifest.json")
        files = []
        deleted_at = None
        
        if os.path.exists(manifest_file):
            with open(manifest_file, "r", encoding="utf-8") as f:
                manifest = json.load(f)
                files = manifest.get("files", [])
                deleted_at = manifest.get("deleted_at")
        else:
            files = [f for f in os.listdir(batch_path) 
                    if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
        
        if files:
            result["batches"].append({
                "timestamp": batch_name,
                "deleted_at": deleted_at,
                "files": files,
                "count": len(files)
            })
            result["total"] += len(files)
    
    return result


@router.post("/restore-screens")
async def restore_screens(data: RestoreScreensRequest):
    """恢复已删除的截图"""
    project_path = get_project_path(data.project)
    screens_dir = get_screens_dir(data.project, project_path)
    
    deleted_dir = os.path.join(project_path, "deleted", data.batch)
    
    if not os.path.exists(deleted_dir):
        raise HTTPException(status_code=404, detail=f"备份批次不存在: {data.batch}")
    
    try:
        restored_count = 0
        
        for filename in os.listdir(deleted_dir):
            if filename == "manifest.json":
                continue
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                src_path = os.path.join(deleted_dir, filename)
                dst_path = os.path.join(screens_dir, filename)
                shutil.move(src_path, dst_path)
                restored_count += 1
        
        # 删除空的备份目录
        shutil.rmtree(deleted_dir)
        
        return {
            "success": True,
            "restored_count": restored_count,
            "message": f"已恢复 {restored_count} 张截图"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))






