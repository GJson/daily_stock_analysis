# -*- coding: utf-8 -*-
"""
生成静态数据文件供GitHub Pages使用
将数据库中的分析结果导出为JSON文件
"""

import json
import sys
from pathlib import Path
from datetime import date, timedelta

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from storage import get_db

def generate_static_data():
    """生成静态数据文件"""
    db = get_db()
    
    # 获取最新的分析结果
    today = date.today()
    records = db.get_analysis_by_date(today)
    
    # 如果没有今日数据,获取最新的分析结果
    if not records:
        records = db.get_latest_analysis(limit=20)
    
    # 转换为字典列表
    stocks = [record.to_dict() for record in records]
    
    # 统计数据
    buy_count = sum(1 for s in stocks if s['operation_advice'] in ['买入', '加仓', '强烈买入'])
    hold_count = sum(1 for s in stocks if s['operation_advice'] in ['持有', '观望'])
    sell_count = sum(1 for s in stocks if s['operation_advice'] in ['卖出', '减仓', '强烈卖出'])
    avg_score = sum(s['sentiment_score'] for s in stocks) / len(stocks) if stocks else 0
    
    # 构建数据对象
    data = {
        'success': True,
        'date': today.isoformat(),
        'stats': {
            'total': len(stocks),
            'buy': buy_count,
            'hold': hold_count,
            'sell': sell_count,
            'avg_score': round(avg_score, 1)
        },
        'stocks': stocks,
        'last_update': records[0].created_at.isoformat() if records else None
    }
    
    # 确保docs目录存在
    docs_dir = project_root / 'docs'
    docs_dir.mkdir(exist_ok=True)
    
    # 保存JSON文件
    json_file = docs_dir / 'dashboard_data.json'
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"✅ 已生成静态数据文件: {json_file}")
    print(f"   股票数量: {len(stocks)}")
    print(f"   统计: 买入{buy_count} 持有{hold_count} 卖出{sell_count}")
    
    return json_file

if __name__ == "__main__":
    try:
        generate_static_data()
    except Exception as e:
        print(f"❌ 生成静态数据失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
