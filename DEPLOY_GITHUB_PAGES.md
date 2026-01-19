# 🚀 部署到GitHub Pages指南

## 前置条件

1. 确保你的GitHub仓库是公开的（或你有GitHub Pro账户）
2. 已配置GitHub Actions（分析完成后会自动部署）

## 部署步骤

### 1. 启用GitHub Pages

1. 打开你的GitHub仓库页面
2. 进入 **Settings** → **Pages**
3. 在 **Source** 部分选择：
   - Source: `Deploy from a branch`
   - Branch: `gh-pages`
   - Folder: `/ (root)`
4. 点击 **Save**

### 2. 验证部署

1. 等待GitHub Actions完成（分析完成后会自动部署）
2. 访问: `https://你的用户名.github.io/daily_stock_analysis/`
3. 如果看到仪表盘页面，说明部署成功！

### 3. 自定义域名（可选）

如果需要使用自定义域名：

1. 在仓库根目录创建 `CNAME` 文件
2. 写入你的域名，例如: `dashboard.example.com`
3. 在DNS中添加CNAME记录指向 `你的用户名.github.io`

## 工作原理

1. **GitHub Actions运行分析** → 生成分析结果并保存到数据库
2. **生成静态数据** → `scripts/generate_static_data.py` 从数据库读取数据并生成JSON文件
3. **部署到GitHub Pages** → 使用 `peaceiris/actions-gh-pages` 将 `docs/` 目录部署到 `gh-pages` 分支
4. **前端读取数据** → `index.html` 通过fetch读取 `dashboard_data.json` 并渲染

## 文件结构

```
docs/
├── index.html              # 前端页面
├── dashboard_data.json     # 数据文件（自动生成）
└── README.md              # 说明文档
```

## 故障排查

### 页面显示"加载失败"

1. 检查是否已运行分析（GitHub Actions）
2. 检查 `docs/dashboard_data.json` 是否存在
3. 查看GitHub Actions日志确认部署是否成功

### 数据未更新

1. 确保GitHub Actions已成功运行
2. 检查 `generate_static_data.py` 是否执行成功
3. 等待几分钟让GitHub Pages更新（可能有缓存）

### 404错误

1. 确认GitHub Pages已启用
2. 检查仓库名称是否正确
3. 确认访问路径: `https://你的用户名.github.io/仓库名/`

## 注意事项

- GitHub Pages有构建时间限制（约10分钟）
- 免费账户每月有流量限制（100GB）
- 数据文件会在每次分析后自动更新
- 如果长时间未运行分析，数据可能过期
