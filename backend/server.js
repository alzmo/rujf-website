import express from 'express';
import mongoose from 'mongoose';
import cors from 'cors';
import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';

dotenv.config();
const app = express();

// ========== 中间件 ==========
app.use(cors());
app.use(express.json());

// ========== 数据模型 ==========
const diarySchema = new mongoose.Schema({
  content: { type: String, required: true },
  createdAt: { type: Date, default: Date.now },
});
const Diary = mongoose.model('Diary', diarySchema);

// ========== 路由：健康检查 ==========
app.get('/health', (req, res) => {
  res.json({
    status: 'OK',
    message: '日记服务运行正常',
    timestamp: new Date().toISOString(),
  });
});

// ========== 路由：获取所有日记 ==========
app.get('/api/diaries', async (req, res) => {
  try {
    console.log('📖 正在获取日记列表...');
    const diaries = await Diary.find().sort({ createdAt: -1 });
    console.log(`✅ 找到 ${diaries.length} 篇日记`);
    res.json(diaries);
  } catch (error) {
    console.error('❌ 获取日记失败:', error);
    res.status(500).json({ error: '获取日记失败' });
  }
});

// ========== 路由：创建日记 ==========
app.post('/api/diaries', async (req, res) => {
  try {
    const { content, password } = req.body;

    if (!content) return res.status(400).json({ error: '日记内容不能为空' });
    if (password !== process.env.WRITE_PASSWORD) {
      console.log('❌ 密码验证失败');
      return res.status(401).json({ error: '无效密码' });
    }

    console.log('📝 正在创建新日记...');
    const diary = new Diary({ content: content.trim() });
    const savedDiary = await diary.save();

    console.log('✅ 日记创建成功:', savedDiary._id);
    res.status(201).json({ message: '日记保存成功', diary: savedDiary });
  } catch (error) {
    console.error('❌ 保存日记失败:', error);
    res.status(500).json({ error: '保存日记失败' });
  }
});

// ========== 路由：获取单篇日记 ==========
app.get('/api/diaries/:id', async (req, res) => {
  try {
    const diary = await Diary.findById(req.params.id);
    if (!diary) return res.status(404).json({ error: '日记未找到' });
    res.json(diary);
  } catch (error) {
    res.status(500).json({ error: '获取日记失败' });
  }
});

// ========== 前端静态托管（Render关键部分） ==========
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const frontendPath = path.join(__dirname, '../frontend');

app.use(express.static(frontendPath));
app.get('*', (req, res) => {
  res.sendFile(path.join(frontendPath, 'index.html'));
});

// ========== 错误处理 ==========
app.use((err, req, res, next) => {
  console.error('服务器错误:', err);
  res.status(500).json({ error: '服务器内部错误' });
});

// ========== 连接数据库并启动 ==========
const startServer = async () => {
  try {
    console.log('🔗 正在连接数据库...');
    if (!process.env.MONGODB_URI) throw new Error('MONGODB_URI 环境变量未设置');

    await mongoose.connect(process.env.MONGODB_URI, {
      useNewUrlParser: true,
      useUnifiedTopology: true,
    });

    console.log('✅ 已连接到 MongoDB');

    const PORT = process.env.PORT || 10000;
    app.listen(PORT, () => {
      console.log(`🌍 服务器运行在端口 ${PORT}`);
      console.log(`📊 健康检查: /health`);
      console.log(`📖 日记API: /api/diaries`);
    });
  } catch (error) {
    console.error('❌ 启动失败:', error.message);
    process.exit(1);
  }
};

// 优雅关闭
process.on('SIGINT', async () => {
  console.log('\n👋 正在关闭服务器...');
  await mongoose.connection.close();
  console.log('✅ 数据库连接已关闭');
  process.exit(0);
});

startServer();
