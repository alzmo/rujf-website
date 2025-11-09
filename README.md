# RUJF.AI 每日点点 - 极简日记

一个极其简单的公开日记网站，别人打开网址就能看到内容。

## 功能特点

- 🎯 极简设计：单个HTML文件前端，单个JS文件后端
- 📱 响应式：完美支持手机和电脑
- 🔒 简单密码保护写入
- 🚀 快速部署：使用Render免费服务
- 💾 MongoDB云数据库

## 项目结构

```
rujf-diary-simple/
├── backend/
│   ├── server.js          # 后端主文件
│   ├── package.json       # 后端依赖
│   ├── .env              # 环境变量
│   └── .gitignore        # Git忽略文件
└── frontend/
    └── index.html        # 前端单页应用
```

## 本地开发

1. 启动后端：
```bash
cd backend
npm install
node server.js
```

2. 打开前端：
直接在浏览器中打开 `frontend/index.html` 或使用本地服务器

## 部署说明

1. 后端部署到 Render Web Service
2. 前端部署到 Render Static Site
3. 配置环境变量
4. 绑定自定义域名

## 写入方式

1. **数据库直操作**（推荐）：在MongoDB Atlas界面直接插入
2. **API调用**：使用curl或Postman调用POST接口
3. **简单密码**：保护写入权限