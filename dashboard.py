# -*- coding: utf-8 -*-
"""
===================================
A股智能分析系统 - 可视化仪表盘
===================================

提供Web界面展示分析结果:
1. 决策仪表盘 - 展示最新的分析结果
2. 历史记录 - 查看历史分析
3. 股票详情 - 查看单只股票的详细分析
"""

import logging
import json
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
from flask import Flask, render_template_string, jsonify, request
from flask_cors import CORS

from storage import get_db, AnalysisRecord
from config import get_config

logger = logging.getLogger(__name__)

# 创建Flask应用
app = Flask(__name__)
CORS(app)  # 允许跨域请求


# ========== HTML模板 ==========

DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📈 A股智能分析仪表盘</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            color: #333;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .header {
            background: white;
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 24px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .header h1 {
            font-size: 28px;
            color: #1a202c;
            margin-bottom: 8px;
        }
        
        .header .subtitle {
            color: #718096;
            font-size: 14px;
        }
        
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }
        
        .stat-card {
            background: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .stat-card .label {
            font-size: 12px;
            color: #718096;
            margin-bottom: 8px;
        }
        
        .stat-card .value {
            font-size: 32px;
            font-weight: bold;
            color: #1a202c;
        }
        
        .stat-card.buy .value { color: #10b981; }
        .stat-card.hold .value { color: #f59e0b; }
        .stat-card.sell .value { color: #ef4444; }
        
        .stocks-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
            gap: 24px;
        }
        
        .stock-card {
            background: white;
            border-radius: 12px;
            padding: 24px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        .stock-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 12px rgba(0, 0, 0, 0.15);
        }
        
        .stock-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
        }
        
        .stock-name {
            font-size: 20px;
            font-weight: bold;
            color: #1a202c;
        }
        
        .stock-code {
            font-size: 14px;
            color: #718096;
        }
        
        .signal-badge {
            display: inline-block;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
        }
        
        .signal-buy { background: #d1fae5; color: #065f46; }
        .signal-hold { background: #fef3c7; color: #92400e; }
        .signal-sell { background: #fee2e2; color: #991b1b; }
        
        .score {
            font-size: 36px;
            font-weight: bold;
            margin: 16px 0;
        }
        
        .score.high { color: #10b981; }
        .score.medium { color: #f59e0b; }
        .score.low { color: #ef4444; }
        
        .info-row {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #e5e7eb;
        }
        
        .info-row:last-child {
            border-bottom: none;
        }
        
        .info-label {
            color: #718096;
            font-size: 14px;
        }
        
        .info-value {
            color: #1a202c;
            font-size: 14px;
            font-weight: 500;
        }
        
        .dashboard-section {
            margin-top: 24px;
        }
        
        .section-title {
            font-size: 18px;
            font-weight: bold;
            color: #1a202c;
            margin-bottom: 12px;
        }
        
        .checklist {
            list-style: none;
            padding: 0;
        }
        
        .checklist li {
            padding: 8px 0;
            font-size: 14px;
        }
        
        .loading {
            text-align: center;
            padding: 40px;
            color: white;
            font-size: 18px;
        }
        
        .error {
            background: #fee2e2;
            color: #991b1b;
            padding: 16px;
            border-radius: 8px;
            margin: 16px 0;
        }
        
        .refresh-btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            margin-top: 16px;
        }
        
        .refresh-btn:hover {
            background: #5568d3;
        }
        
        @media (max-width: 768px) {
            .stocks-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📈 A股智能分析仪表盘</h1>
            <div class="subtitle">实时分析结果 | 最后更新: <span id="lastUpdate">加载中...</span></div>
        </div>
        
        <div id="stats" class="stats">
            <!-- 统计信息将在这里动态加载 -->
        </div>
        
        <div id="stocks" class="stocks-grid">
            <div class="loading">正在加载分析结果...</div>
        </div>
    </div>
    
    <script>
        async function loadDashboard() {
            try {
                const response = await fetch('/api/latest');
                const data = await response.json();
                
                if (data.error) {
                    document.getElementById('stocks').innerHTML = 
                        `<div class="error">${data.error}</div>`;
                    return;
                }
                
                // 更新最后更新时间
                const now = new Date();
                document.getElementById('lastUpdate').textContent = 
                    now.toLocaleString('zh-CN');
                
                // 更新统计信息
                updateStats(data.stocks);
                
                // 更新股票列表
                updateStocks(data.stocks);
                
            } catch (error) {
                document.getElementById('stocks').innerHTML = 
                    `<div class="error">加载失败: ${error.message}</div>`;
            }
        }
        
        function updateStats(stocks) {
            const statsDiv = document.getElementById('stats');
            const buyCount = stocks.filter(s => ['买入', '加仓', '强烈买入'].includes(s.operation_advice)).length;
            const holdCount = stocks.filter(s => ['持有', '观望'].includes(s.operation_advice)).length;
            const sellCount = stocks.filter(s => ['卖出', '减仓', '强烈卖出'].includes(s.operation_advice)).length;
            const avgScore = stocks.length > 0 ? 
                Math.round(stocks.reduce((sum, s) => sum + s.sentiment_score, 0) / stocks.length) : 0;
            
            statsDiv.innerHTML = `
                <div class="stat-card buy">
                    <div class="label">🟢 建议买入/加仓</div>
                    <div class="value">${buyCount}</div>
                </div>
                <div class="stat-card hold">
                    <div class="label">🟡 建议持有/观望</div>
                    <div class="value">${holdCount}</div>
                </div>
                <div class="stat-card sell">
                    <div class="label">🔴 建议减仓/卖出</div>
                    <div class="value">${sellCount}</div>
                </div>
                <div class="stat-card">
                    <div class="label">📈 平均评分</div>
                    <div class="value">${avgScore}</div>
                </div>
            `;
        }
        
        function updateStocks(stocks) {
            const stocksDiv = document.getElementById('stocks');
            
            if (stocks.length === 0) {
                stocksDiv.innerHTML = '<div class="error">暂无分析结果</div>';
                return;
            }
            
            stocksDiv.innerHTML = stocks.map(stock => {
                const signalClass = getSignalClass(stock.operation_advice);
                const scoreClass = getScoreClass(stock.sentiment_score);
                const dashboard = stock.analysis_data?.dashboard || {};
                const core = dashboard.core_conclusion || {};
                const battle = dashboard.battle_plan || {};
                const sniper = battle.sniper_points || {};
                
                return `
                    <div class="stock-card">
                        <div class="stock-header">
                            <div>
                                <div class="stock-name">${stock.name}</div>
                                <div class="stock-code">${stock.code}</div>
                            </div>
                            <span class="signal-badge ${signalClass}">${stock.operation_advice}</span>
                        </div>
                        
                        <div class="score ${scoreClass}">${stock.sentiment_score}分</div>
                        
                        <div class="info-row">
                            <span class="info-label">趋势预测</span>
                            <span class="info-value">${stock.trend_prediction}</span>
                        </div>
                        
                        ${core.one_sentence ? `
                        <div class="dashboard-section">
                            <div class="section-title">📌 核心结论</div>
                            <p style="color: #4b5563; font-size: 14px; line-height: 1.6;">
                                ${core.one_sentence}
                            </p>
                        </div>
                        ` : ''}
                        
                        ${sniper.ideal_buy || sniper.stop_loss || sniper.take_profit ? `
                        <div class="dashboard-section">
                            <div class="section-title">🎯 操作点位</div>
                            <div class="info-row">
                                <span class="info-label">理想买入</span>
                                <span class="info-value">${sniper.ideal_buy || '-'}</span>
                            </div>
                            <div class="info-row">
                                <span class="info-label">止损位</span>
                                <span class="info-value">${sniper.stop_loss || '-'}</span>
                            </div>
                            <div class="info-row">
                                <span class="info-label">目标位</span>
                                <span class="info-value">${sniper.take_profit || '-'}</span>
                            </div>
                        </div>
                        ` : ''}
                        
                        ${battle.action_checklist && battle.action_checklist.length > 0 ? `
                        <div class="dashboard-section">
                            <div class="section-title">✅ 检查清单</div>
                            <ul class="checklist">
                                ${battle.action_checklist.map(item => `<li>${item}</li>`).join('')}
                            </ul>
                        </div>
                        ` : ''}
                    </div>
                `;
            }).join('');
        }
        
        function getSignalClass(advice) {
            if (['买入', '加仓', '强烈买入'].includes(advice)) return 'signal-buy';
            if (['持有', '观望'].includes(advice)) return 'signal-hold';
            return 'signal-sell';
        }
        
        function getScoreClass(score) {
            if (score >= 70) return 'high';
            if (score >= 40) return 'medium';
            return 'low';
        }
        
        // 页面加载时获取数据
        loadDashboard();
        
        // 每30秒自动刷新
        setInterval(loadDashboard, 30000);
    </script>
</body>
</html>
"""


# ========== API路由 ==========

@app.route('/')
def index():
    """主页面"""
    return render_template_string(DASHBOARD_HTML)


@app.route('/api/latest')
def api_latest():
    """获取最新的分析结果"""
    try:
        db = get_db()
        today = date.today()
        
        # 获取今日的分析结果
        records = db.get_analysis_by_date(today)
        
        # 如果没有今日数据,获取最新的分析结果
        if not records:
            records = db.get_latest_analysis(limit=20)
        
        stocks = [record.to_dict() for record in records]
        
        return jsonify({
            'success': True,
            'stocks': stocks,
            'count': len(stocks),
            'date': today.isoformat()
        })
    except Exception as e:
        logger.error(f"获取最新分析结果失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/stock/<code>')
def api_stock(code):
    """获取指定股票的分析结果"""
    try:
        db = get_db()
        records = db.get_latest_analysis(code=code, limit=10)
        
        stocks = [record.to_dict() for record in records]
        
        return jsonify({
            'success': True,
            'code': code,
            'stocks': stocks,
            'count': len(stocks)
        })
    except Exception as e:
        logger.error(f"获取股票分析结果失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/history')
def api_history():
    """获取历史分析记录"""
    try:
        days = int(request.args.get('days', 7))
        db = get_db()
        
        start_date = date.today() - timedelta(days=days)
        records = []
        
        for i in range(days):
            check_date = start_date + timedelta(days=i)
            day_records = db.get_analysis_by_date(check_date)
            records.extend(day_records)
        
        stocks = [record.to_dict() for record in records]
        
        return jsonify({
            'success': True,
            'stocks': stocks,
            'count': len(stocks),
            'days': days
        })
    except Exception as e:
        logger.error(f"获取历史记录失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


def run_server(host: str = "127.0.0.1", port: int = 5000, debug: bool = False):
    """
    启动可视化服务
    
    Args:
        host: 监听地址
        port: 监听端口
        debug: 是否启用调试模式
    """
    logger.info(f"启动可视化仪表盘服务: http://{host}:{port}")
    app.run(host=host, port=port, debug=debug, threaded=True)


def run_server_in_thread(host: str = "127.0.0.1", port: int = 5000, debug: bool = False):
    """
    在后台线程中启动可视化服务
    
    Args:
        host: 监听地址
        port: 监听端口
        debug: 是否启用调试模式
    """
    import threading
    import time
    
    def serve():
        try:
            logger.info(f"可视化仪表盘服务启动中: http://{host}:{port}")
            # 在后台线程中运行,不使用reloader
            app.run(host=host, port=port, debug=False, threaded=True, use_reloader=False)
        except Exception as e:
            logger.error(f"可视化仪表盘服务运行出错: {e}")
    
    t = threading.Thread(target=serve, daemon=True)
    t.start()
    
    # 等待一下确保服务启动
    time.sleep(0.5)
    
    return t


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    config = get_config()
    run_server(
        host=config.webui_host,
        port=config.webui_port + 1,  # 使用不同的端口避免冲突
        debug=config.debug
    )
