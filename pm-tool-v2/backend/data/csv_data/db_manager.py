# -*- coding: utf-8 -*-
"""
SQLite数据库管理器
支持产品分析数据的存储和跨产品查询
支持三层分类体系 (Stage/Module/Feature)
"""

import os
import json
import sqlite3
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from contextlib import contextmanager

# 数据库路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "pm_tool.db")


class DBManager:
    """数据库管理器"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or DB_PATH
        self._init_db()
    
    @contextmanager
    def get_connection(self):
        """获取数据库连接（上下文管理器）"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # 返回字典式结果
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def _init_db(self):
        """初始化数据库表结构"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 产品表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    folder_name TEXT,
                    publisher TEXT,
                    category TEXT,
                    sub_category TEXT,
                    target_users TEXT,
                    core_value TEXT,
                    business_model TEXT,
                    visual_style TEXT,
                    paywall_position TEXT,
                    onboarding_length TEXT,
                    total_screenshots INTEGER DEFAULT 0,
                    model TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    analyzed_at DATETIME
                )
            """)
            
            # 截图表 - 支持三层分类 (Stage/Module/Feature)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS screenshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER NOT NULL,
                    idx INTEGER,
                    filename TEXT NOT NULL,
                    screen_type TEXT,
                    sub_type TEXT,
                    stage TEXT,
                    module TEXT,
                    feature TEXT,
                    role TEXT,
                    naming_cn TEXT,
                    naming_en TEXT,
                    core_function_cn TEXT,
                    core_function_en TEXT,
                    product_insight_cn TEXT,
                    product_insight_en TEXT,
                    confidence REAL,
                    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
                )
            """)
            
            # 设计亮点表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS design_highlights (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    screenshot_id INTEGER NOT NULL,
                    category TEXT,
                    content_cn TEXT,
                    content_en TEXT,
                    FOREIGN KEY (screenshot_id) REFERENCES screenshots(id) ON DELETE CASCADE
                )
            """)
            
            # 标签表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tags (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    screenshot_id INTEGER NOT NULL,
                    tag_cn TEXT,
                    tag_en TEXT,
                    FOREIGN KEY (screenshot_id) REFERENCES screenshots(id) ON DELETE CASCADE
                )
            """)
            
            # 流程阶段表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS flow_stages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER NOT NULL,
                    order_num INTEGER,
                    stage_name TEXT,
                    start_idx INTEGER,
                    end_idx INTEGER,
                    description TEXT,
                    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
                )
            """)
            
            # 视频帧表 (新增)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS video_frames (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER NOT NULL,
                    idx INTEGER,
                    filename TEXT NOT NULL,
                    timestamp_ms INTEGER,
                    stage TEXT,
                    module TEXT,
                    feature TEXT,
                    role TEXT,
                    description TEXT,
                    is_new_page INTEGER DEFAULT 0,
                    transition_type TEXT,
                    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
                )
            """)
            
            # 视频帧与截图对齐表 (新增)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS alignments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER NOT NULL,
                    video_frame_id INTEGER NOT NULL,
                    screenshot_id INTEGER,
                    confidence REAL,
                    match_method TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
                    FOREIGN KEY (video_frame_id) REFERENCES video_frames(id) ON DELETE CASCADE,
                    FOREIGN KEY (screenshot_id) REFERENCES screenshots(id) ON DELETE SET NULL
                )
            """)
            
            # 创建索引
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_screenshots_product ON screenshots(product_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_screenshots_type ON screenshots(screen_type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_screenshots_stage ON screenshots(stage)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_screenshots_module ON screenshots(module)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_highlights_screenshot ON design_highlights(screenshot_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tags_screenshot ON tags(screenshot_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_video_frames_product ON video_frames(product_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_alignments_product ON alignments(product_id)")
            
            # 添加新列到已存在的表（安全迁移）
            self._migrate_screenshots_table(cursor)
    
    def _migrate_screenshots_table(self, cursor):
        """为已存在的screenshots表添加新列"""
        # 检查并添加新列
        cursor.execute("PRAGMA table_info(screenshots)")
        existing_columns = {row[1] for row in cursor.fetchall()}
        
        new_columns = [
            ("stage", "TEXT"),
            ("module", "TEXT"),
            ("feature", "TEXT"),
            ("role", "TEXT"),
        ]
        
        for col_name, col_type in new_columns:
            if col_name not in existing_columns:
                try:
                    cursor.execute(f"ALTER TABLE screenshots ADD COLUMN {col_name} {col_type}")
                except sqlite3.OperationalError:
                    pass  # 列已存在
    
    # ==================== 写入操作 ====================
    
    def save_product(self, product_data: Dict) -> int:
        """
        保存或更新产品信息
        
        Args:
            product_data: 产品数据字典
            
        Returns:
            产品ID
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 检查是否已存在
            cursor.execute("SELECT id FROM products WHERE name = ?", (product_data.get('name'),))
            existing = cursor.fetchone()
            
            if existing:
                # 更新
                product_id = existing['id']
                cursor.execute("""
                    UPDATE products SET
                        folder_name = ?,
                        publisher = ?,
                        category = ?,
                        sub_category = ?,
                        target_users = ?,
                        core_value = ?,
                        business_model = ?,
                        visual_style = ?,
                        paywall_position = ?,
                        onboarding_length = ?,
                        total_screenshots = ?,
                        model = ?,
                        analyzed_at = ?
                    WHERE id = ?
                """, (
                    product_data.get('folder_name'),
                    product_data.get('publisher'),
                    product_data.get('category'),
                    product_data.get('sub_category'),
                    product_data.get('target_users'),
                    product_data.get('core_value'),
                    product_data.get('business_model'),
                    product_data.get('visual_style'),
                    product_data.get('paywall_position'),
                    product_data.get('onboarding_length'),
                    product_data.get('total_screenshots', 0),
                    product_data.get('model'),
                    datetime.now().isoformat(),
                    product_id
                ))
                
                # 删除旧的截图数据（级联删除会处理关联表）
                cursor.execute("DELETE FROM screenshots WHERE product_id = ?", (product_id,))
                cursor.execute("DELETE FROM flow_stages WHERE product_id = ?", (product_id,))
            else:
                # 插入新产品
                cursor.execute("""
                    INSERT INTO products (
                        name, folder_name, publisher, category, sub_category,
                        target_users, core_value, business_model, visual_style,
                        paywall_position, onboarding_length, total_screenshots, model, analyzed_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    product_data.get('name'),
                    product_data.get('folder_name'),
                    product_data.get('publisher'),
                    product_data.get('category'),
                    product_data.get('sub_category'),
                    product_data.get('target_users'),
                    product_data.get('core_value'),
                    product_data.get('business_model'),
                    product_data.get('visual_style'),
                    product_data.get('paywall_position'),
                    product_data.get('onboarding_length'),
                    product_data.get('total_screenshots', 0),
                    product_data.get('model'),
                    datetime.now().isoformat()
                ))
                product_id = cursor.lastrowid
            
            return product_id
    
    def save_screenshot(self, product_id: int, screenshot_data: Dict) -> int:
        """保存截图分析结果（支持三层分类）"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO screenshots (
                    product_id, idx, filename, screen_type, sub_type,
                    stage, module, feature, role,
                    naming_cn, naming_en, core_function_cn, core_function_en,
                    product_insight_cn, product_insight_en, confidence
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                product_id,
                screenshot_data.get('index', screenshot_data.get('idx')),
                screenshot_data.get('filename'),
                screenshot_data.get('screen_type'),
                screenshot_data.get('sub_type'),
                screenshot_data.get('stage'),
                screenshot_data.get('module'),
                screenshot_data.get('feature'),
                screenshot_data.get('role'),
                screenshot_data.get('naming', {}).get('cn') if isinstance(screenshot_data.get('naming'), dict) else screenshot_data.get('naming_cn'),
                screenshot_data.get('naming', {}).get('en') if isinstance(screenshot_data.get('naming'), dict) else screenshot_data.get('naming_en'),
                screenshot_data.get('core_function', {}).get('cn') if isinstance(screenshot_data.get('core_function'), dict) else screenshot_data.get('core_function_cn'),
                screenshot_data.get('core_function', {}).get('en') if isinstance(screenshot_data.get('core_function'), dict) else screenshot_data.get('core_function_en'),
                screenshot_data.get('product_insight', {}).get('cn') if isinstance(screenshot_data.get('product_insight'), dict) else screenshot_data.get('product_insight_cn'),
                screenshot_data.get('product_insight', {}).get('en') if isinstance(screenshot_data.get('product_insight'), dict) else screenshot_data.get('product_insight_en'),
                screenshot_data.get('confidence', 0.0)
            ))
            
            screenshot_id = cursor.lastrowid
            
            # 保存设计亮点
            highlights = screenshot_data.get('design_highlights', [])
            for h in highlights:
                cursor.execute("""
                    INSERT INTO design_highlights (screenshot_id, category, content_cn, content_en)
                    VALUES (?, ?, ?, ?)
                """, (
                    screenshot_id,
                    h.get('category'),
                    h.get('cn'),
                    h.get('en')
                ))
            
            # 保存标签
            tags = screenshot_data.get('tags', [])
            for t in tags:
                if isinstance(t, dict):
                    cursor.execute("""
                        INSERT INTO tags (screenshot_id, tag_cn, tag_en)
                        VALUES (?, ?, ?)
                    """, (screenshot_id, t.get('cn'), t.get('en')))
                else:
                    cursor.execute("""
                        INSERT INTO tags (screenshot_id, tag_cn, tag_en)
                        VALUES (?, ?, ?)
                    """, (screenshot_id, str(t), str(t)))
            
            return screenshot_id
    
    def save_video_frame(self, product_id: int, frame_data: Dict) -> int:
        """保存视频帧分析结果"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO video_frames (
                    product_id, idx, filename, timestamp_ms,
                    stage, module, feature, role,
                    description, is_new_page, transition_type
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                product_id,
                frame_data.get('index', frame_data.get('idx')),
                frame_data.get('filename'),
                frame_data.get('timestamp_ms'),
                frame_data.get('stage'),
                frame_data.get('module'),
                frame_data.get('feature'),
                frame_data.get('role'),
                frame_data.get('description'),
                1 if frame_data.get('is_new_page') else 0,
                frame_data.get('transition_type', frame_data.get('transition_from_prev'))
            ))
            
            return cursor.lastrowid
    
    def save_alignment(self, product_id: int, video_frame_id: int, 
                       screenshot_id: int, confidence: float, method: str = "ai") -> int:
        """保存视频帧与截图的对齐关系"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO alignments (
                    product_id, video_frame_id, screenshot_id, confidence, match_method
                ) VALUES (?, ?, ?, ?, ?)
            """, (product_id, video_frame_id, screenshot_id, confidence, method))
            
            return cursor.lastrowid
    
    def save_flow_stages(self, product_id: int, stages: List[Dict]):
        """保存流程阶段"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            for i, stage in enumerate(stages):
                if isinstance(stage, str):
                    # 简单字符串格式
                    cursor.execute("""
                        INSERT INTO flow_stages (product_id, order_num, stage_name)
                        VALUES (?, ?, ?)
                    """, (product_id, i, stage))
                else:
                    # 字典格式
                    cursor.execute("""
                        INSERT INTO flow_stages (product_id, order_num, stage_name, start_idx, end_idx, description)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        product_id,
                        stage.get('order', i),
                        stage.get('name', stage.get('stage_name')),
                        stage.get('start_idx', stage.get('start')),
                        stage.get('end_idx', stage.get('end')),
                        stage.get('description')
                    ))
    
    # ==================== 查询操作 ====================
    
    def get_product(self, name: str) -> Optional[Dict]:
        """获取产品信息"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM products WHERE name = ? OR folder_name = ?", (name, name))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_product_by_folder(self, folder_name: str) -> Optional[Dict]:
        """通过文件夹名获取产品"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM products WHERE folder_name = ?", (folder_name,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_all_products(self) -> List[Dict]:
        """获取所有产品"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM products ORDER BY analyzed_at DESC")
            return [dict(row) for row in cursor.fetchall()]
    
    def get_screenshots(self, product_id: int) -> List[Dict]:
        """获取产品的所有截图"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM screenshots WHERE product_id = ? ORDER BY idx
            """, (product_id,))
            
            screenshots = []
            for row in cursor.fetchall():
                screenshot = dict(row)
                screenshot_id = screenshot['id']
                
                # 获取设计亮点
                cursor.execute("""
                    SELECT category, content_cn, content_en FROM design_highlights
                    WHERE screenshot_id = ?
                """, (screenshot_id,))
                screenshot['design_highlights'] = [
                    {'category': r['category'], 'cn': r['content_cn'], 'en': r['content_en']}
                    for r in cursor.fetchall()
                ]
                
                # 获取标签
                cursor.execute("""
                    SELECT tag_cn, tag_en FROM tags WHERE screenshot_id = ?
                """, (screenshot_id,))
                screenshot['tags'] = [
                    {'cn': r['tag_cn'], 'en': r['tag_en']}
                    for r in cursor.fetchall()
                ]
                
                screenshots.append(screenshot)
            
            return screenshots
    
    def get_video_frames(self, product_id: int) -> List[Dict]:
        """获取产品的所有视频帧"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM video_frames WHERE product_id = ? ORDER BY idx
            """, (product_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_alignments(self, product_id: int) -> List[Dict]:
        """获取产品的所有对齐关系"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT a.*, vf.filename as frame_filename, s.filename as screenshot_filename
                FROM alignments a
                LEFT JOIN video_frames vf ON a.video_frame_id = vf.id
                LEFT JOIN screenshots s ON a.screenshot_id = s.id
                WHERE a.product_id = ?
                ORDER BY vf.idx
            """, (product_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_flow_stages(self, product_id: int) -> List[Dict]:
        """获取产品的流程阶段"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM flow_stages WHERE product_id = ? ORDER BY order_num
            """, (product_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_product_with_screenshots(self, name: str) -> Optional[Dict]:
        """获取产品及其所有截图（完整数据）"""
        product = self.get_product(name)
        if not product:
            return None
        
        product['screenshots'] = self.get_screenshots(product['id'])
        product['flow_stages'] = self.get_flow_stages(product['id'])
        product['video_frames'] = self.get_video_frames(product['id'])
        product['alignments'] = self.get_alignments(product['id'])
        return product
    
    # ==================== 跨产品查询 ====================
    
    def find_by_screen_type(self, screen_type: str) -> List[Dict]:
        """按截图类型查询"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT s.*, p.name as product_name, p.folder_name
                FROM screenshots s
                JOIN products p ON s.product_id = p.id
                WHERE s.screen_type = ?
                ORDER BY p.name, s.idx
            """, (screen_type,))
            return [dict(row) for row in cursor.fetchall()]
    
    def find_by_stage(self, stage: str) -> List[Dict]:
        """按Stage查询"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT s.*, p.name as product_name, p.folder_name
                FROM screenshots s
                JOIN products p ON s.product_id = p.id
                WHERE s.stage = ?
                ORDER BY p.name, s.idx
            """, (stage,))
            return [dict(row) for row in cursor.fetchall()]
    
    def find_by_module(self, module: str) -> List[Dict]:
        """按Module查询"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT s.*, p.name as product_name, p.folder_name
                FROM screenshots s
                JOIN products p ON s.product_id = p.id
                WHERE s.module = ?
                ORDER BY p.name, s.idx
            """, (module,))
            return [dict(row) for row in cursor.fetchall()]
    
    def find_by_paywall_position(self, position: str) -> List[Dict]:
        """按Paywall位置查询产品"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM products WHERE paywall_position = ?
            """, (position,))
            return [dict(row) for row in cursor.fetchall()]
    
    def find_by_onboarding_length(self, length: str) -> List[Dict]:
        """按Onboarding长度查询产品"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM products WHERE onboarding_length = ?
            """, (length,))
            return [dict(row) for row in cursor.fetchall()]
    
    # ==================== 聚合统计 ====================
    
    def get_screen_type_stats(self) -> Dict[str, int]:
        """获取截图类型统计"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT screen_type, COUNT(*) as count
                FROM screenshots
                GROUP BY screen_type
                ORDER BY count DESC
            """)
            return {row['screen_type']: row['count'] for row in cursor.fetchall()}
    
    def get_stage_stats(self) -> Dict[str, int]:
        """获取Stage统计"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT stage, COUNT(*) as count
                FROM screenshots
                WHERE stage IS NOT NULL
                GROUP BY stage
                ORDER BY count DESC
            """)
            return {row['stage']: row['count'] for row in cursor.fetchall()}
    
    def get_module_stats(self) -> Dict[str, int]:
        """获取Module统计"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT module, COUNT(*) as count
                FROM screenshots
                WHERE module IS NOT NULL
                GROUP BY module
                ORDER BY count DESC
            """)
            return {row['module']: row['count'] for row in cursor.fetchall()}
    
    def get_onboarding_stats(self) -> Dict:
        """获取Onboarding统计"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 各产品Onboarding截图数（使用新的stage字段）
            cursor.execute("""
                SELECT p.name, COUNT(s.id) as onboarding_count
                FROM products p
                LEFT JOIN screenshots s ON p.id = s.product_id AND s.stage = 'Onboarding'
                GROUP BY p.id
                ORDER BY onboarding_count DESC
            """)
            by_product = {row['name']: row['onboarding_count'] for row in cursor.fetchall()}
            
            # Onboarding长度分布
            cursor.execute("""
                SELECT onboarding_length, COUNT(*) as count
                FROM products
                WHERE onboarding_length IS NOT NULL
                GROUP BY onboarding_length
            """)
            length_dist = {row['onboarding_length']: row['count'] for row in cursor.fetchall()}
            
            # Module分布
            cursor.execute("""
                SELECT module, COUNT(*) as count
                FROM screenshots
                WHERE stage = 'Onboarding' AND module IS NOT NULL
                GROUP BY module
                ORDER BY count DESC
            """)
            module_dist = {row['module']: row['count'] for row in cursor.fetchall()}
            
            return {
                'by_product': by_product,
                'length_distribution': length_dist,
                'module_distribution': module_dist
            }
    
    def get_paywall_stats(self) -> Dict:
        """获取Paywall统计"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Paywall位置分布
            cursor.execute("""
                SELECT paywall_position, COUNT(*) as count
                FROM products
                WHERE paywall_position IS NOT NULL
                GROUP BY paywall_position
            """)
            position_dist = {row['paywall_position']: row['count'] for row in cursor.fetchall()}
            
            # 各产品Paywall截图数（使用module字段）
            cursor.execute("""
                SELECT p.name, COUNT(s.id) as paywall_count
                FROM products p
                LEFT JOIN screenshots s ON p.id = s.product_id AND s.module = 'Paywall'
                GROUP BY p.id
                ORDER BY paywall_count DESC
            """)
            by_product = {row['name']: row['paywall_count'] for row in cursor.fetchall()}
            
            return {
                'position_distribution': position_dist,
                'by_product': by_product
            }
    
    def get_design_patterns(self, limit: int = 20) -> List[Dict]:
        """获取设计亮点出现频率"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT content_cn, category, COUNT(*) as count
                FROM design_highlights
                GROUP BY content_cn
                ORDER BY count DESC
                LIMIT ?
            """, (limit,))
            return [dict(row) for row in cursor.fetchall()]
    
    # ==================== 兼容性方法（供app.py使用） ====================
    
    def get_structured_descriptions(self, folder_name: str) -> Dict:
        """
        获取结构化描述（兼容原JSON格式）
        返回格式与原 ai_analysis.json 的 results 字段兼容
        """
        product = self.get_product_by_folder(folder_name) or self.get_product(folder_name)
        if not product:
            return {}
        
        screenshots = self.get_screenshots(product['id'])
        
        result = {}
        for s in screenshots:
            result[s['filename']] = {
                'filename': s['filename'],
                'index': s['idx'],
                'screen_type': s['screen_type'],
                'sub_type': s['sub_type'],
                'stage': s.get('stage'),
                'module': s.get('module'),
                'feature': s.get('feature'),
                'role': s.get('role'),
                'naming': {
                    'cn': s['naming_cn'],
                    'en': s['naming_en']
                },
                'core_function': {
                    'cn': s['core_function_cn'],
                    'en': s['core_function_en']
                },
                'product_insight': {
                    'cn': s['product_insight_cn'],
                    'en': s['product_insight_en']
                },
                'design_highlights': s['design_highlights'],
                'tags': s['tags'],
                'confidence': s['confidence']
            }
        
        return result
    
    def get_screen_types_map(self, folder_name: str) -> Dict[str, str]:
        """获取截图类型映射（filename -> screen_type）"""
        product = self.get_product_by_folder(folder_name) or self.get_product(folder_name)
        if not product:
            return {}
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT filename, screen_type FROM screenshots WHERE product_id = ?
            """, (product['id'],))
            return {row['filename']: row['screen_type'] for row in cursor.fetchall()}
    
    def get_classification_map(self, folder_name: str) -> Dict[str, Dict]:
        """获取完整分类映射（filename -> {stage, module, feature, role}）"""
        product = self.get_product_by_folder(folder_name) or self.get_product(folder_name)
        if not product:
            return {}
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT filename, stage, module, feature, role FROM screenshots WHERE product_id = ?
            """, (product['id'],))
            return {
                row['filename']: {
                    'stage': row['stage'],
                    'module': row['module'],
                    'feature': row['feature'],
                    'role': row['role']
                }
                for row in cursor.fetchall()
            }


# 全局实例
_db_instance = None

def get_db() -> DBManager:
    """获取全局数据库实例"""
    global _db_instance
    if _db_instance is None:
        _db_instance = DBManager()
    return _db_instance
