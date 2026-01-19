# 🚀 GitHub Pages 部署指南

## 快速开始

### 1. 启用GitHub Pages

1. 打开你的GitHub仓库: `https://github.com/GJson/daily_stock_analysis`
2. 进入 **Settings** → **Pages**
3. 配置如下：
   - **Source**: `Deploy from a branch`
   - **Branch**: `gh-pages`
   - **Folder**: `/ (root)`
4. 点击 **Save**

### 2. 修改Workflow文件

在 `.github/workflows/daily_analysis.yml` 文件末尾添加以下步骤：

```yaml
      - name: 生成静态数据文件
        if: always()
        run: |
          python scripts/generate_static_data.py || echo "数据生成失败，跳过部署"
      
      - name: 部署到GitHub Pages
        if: always() && hashFiles('docs/dashboard_data.json')
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./docs
          keep_files: false
          user_name: 'github-actions[bot]'
          user_email: 'github-actions[bot]@users.noreply.github.com'
```

### 3. 提交代码

```bash
git add .
git commit -m "添加GitHub Pages部署支持"
git push
```

### 4. 运行分析

1. 进入 **Actions** 标签
2. 选择 **"每日股票分析"** workflow
3. 点击 **"Run workflow"** → **"Run workflow"**
4. 等待分析完成

### 5. 访问页面

分析完成后，访问：
```
https://GJson.github.io/daily_stock_analysis/
```

## 工作原理

1. **GitHub Actions运行分析** → 执行股票分析并保存结果到数据库
2. **生成静态数据** → `scripts/generate_static_data.py` 从数据库读取并生成 `docs/dashboard_data.json`
3. **部署到GitHub Pages** → 自动将 `docs/` 目录部署到 `gh-pages` 分支
4. **前端展示** → `docs/index.html` 读取JSON数据并渲染可视化界面

## 文件说明

- `docs/index.html` - 前端页面（已创建）
- `docs/dashboard_data.json` - 数据文件（自动生成）
- `scripts/generate_static_data.py` - 数据生成脚本（已创建）

## 注意事项

1. **首次部署**: 需要先运行一次分析才能生成数据文件
2. **数据更新**: 每次分析完成后会自动更新
3. **访问地址**: `https://你的用户名.github.io/仓库名/`
4. **权限**: 需要给GitHub Actions写入权限（Settings → Actions → General → Workflow permissions）

## 故障排查

### 页面404

- 确认GitHub Pages已启用
- 检查 `gh-pages` 分支是否存在
- 确认访问路径正确

### 数据未显示

- 检查是否已运行分析
- 查看Actions日志确认数据生成是否成功
- 检查 `docs/dashboard_data.json` 文件是否存在

### 部署失败

- 检查GitHub Actions权限设置
- 查看Actions日志了解详细错误
- 确认 `peaceiris/actions-gh-pages@v3` 权限正确
