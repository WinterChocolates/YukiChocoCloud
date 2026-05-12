# ❄️🍫 YukiChocoCloud

> 「雪が溶ける前に、想い出をしまっておく場所。」
> *“Before the snow melts, a place to keep your memories.”*  
>  (´｡• ᵕ •｡`) ♡  **一个有一点点温度的二次元私有云盘** ♡

---

## 🧊 关于 YukiChocoCloud

在某个冬夜，外面飘着雪，手里捧着一杯热可可，  
代码一行一行落下来——于是就有了 **YukiChocoCloud**  ☁️

它来自你的名字 **WinterChocolates**，  
把 ❄️「雪」和 🍫「巧克力」轻轻搅在一起，  
煮成了一只专门存放 **“不愿融化的瞬间”** 的小盒子。

> 它可不是冷冰冰的 storage 哦。  
> 它是一个 **你愿意时常打开**、翻翻旧回忆的地方。 (◍•ᴗ•◍)❤

---

## ✨ 魔法特性 ( *´艸｀)

| 功能 | 说明 |
|------|------|
| 📁 **文件管理** | 新建文件夹 / 上传 / 下载 / 删除，支持拖拽上传和批量操作 |
| 🚀 **高速上传** | 分片上传，大文件也像雪花一样轻轻落下 |
| 🖼 **在线预览** | 图片、视频、音频，不用下载也能看一眼 |
| 🔗 **分享系统** | 加密分享链接，可以设置密码和有效期，只给想给的人看 |
| 🔨🗑 **回收站** | 删除不等于消失…… 软删除机制，记忆是可以反悔的 (๑•́ ₃ •̀๑) |
| 🔨👥 **多用户** | 每个家人都有自己的小天地，空间配额可调 |
| 🔨🎨 **主题切换**（即将到来） | ❄️ 冬日模式（银白与淡蓝） / 🍫 可可模式（暖棕与奶白） |
| 🔨🎀 **看板娘**（计划中） | 右下角会住进一只叫 **YukiChoco 酱** 的小家伙，陪你一起整理文件！ |

---

## 🖼 预览 (Preview)

> （*等截好图就放在这里哦～*）
>
> * 📂 文件管理界面  
> * 🎞 在线预览  
> * 🔗 分享页面  

---

## 🏗 用到的魔法材料 (Tech Stack)

### ❄️ 后端 (Backend)
- **FastAPI** — 轻快得像雪橇划过冰面
- **SQLAlchemy 2.0 (async)** — 与数据库优雅对话
- **asyncpg** — 异步 PostgreSQL 驱动
- **PostgreSQL** — 把所有元数据稳稳存放
- **python-jose + passlib** — JWT 认证 + bcrypt 密码哈希
- **aiofiles** — 异步文件 I/O

### 🍫 前端 (Frontend)
- **Vue 3 + TypeScript** — 组件就是一块块巧克力
- **Element Plus** — 漂亮的积木，搭出舒适界面
- **Pinia** — 轻巧的状态管理，一点也不重
- **Vue Router** — 单页应用路由
- **Axios** — HTTP 请求拦截器，自动携带 JWT
- **Vite** — 极速构建工具

---

## 🚀 快速开始 · 启动咒语 (Quick Start)

### ① 把仓库召唤到本地
```bash
git clone https://github.com/WinterChocolates/YukiChocoCloud.git
cd YukiChocoCloud
```

### ② 配置你的小秘密
```bash
cd backend
cp .env.example .env
```
然后编辑 `.env` 文件，填入你自己的密码和密钥：
```env
DATABASE_URL=postgresql+asyncpg://用户名:密码@localhost:5432/数据库名
SECRET_KEY=your_random_secret_string
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_postgres_password
POSTGRES_DB=yukichococloud
```

### ③ 启动数据库
确保 PostgreSQL 已安装并运行，然后创建数据库：
```bash
psql -U postgres -c "CREATE DATABASE yukichococloud;"
```

### ④ 启动后端
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```
后端运行在 http://localhost:8000

### ⑤ 启动前端
```bash
cd frontend
npm install
npm run dev
```
前端运行在 http://localhost:3000

### ⑥ 打开浏览器，走进雪与可可的世界
```text
http://localhost:3000
```

---

## 📖 API 文档
详见 [API.md](API.md)

---

## 📁 目录小地图 (Project Structure)

```
yuki-choco-cloud/
├── backend/
│   ├── app/          # ❄️ FastAPI 后端魔法工房
│   ├── uploads/      # 📦 你存放的所有记忆
│   └── .env.example
├── frontend/         # 🍫 Vue3 前端甜点屋
└── API.md            # 📖 API 接口文档
```

---

## 🗺 旅途纪事 (Roadmap)

| 版本 | 代号 | 内容 |
|------|------|------|
| ✅ v0.1 | 初雪 | 基础文件管理：浏览、上传、下载、删除 |
| ✅ v0.2 | 可可雨 | 分享系统：加密链接、密码与有效期 |
| 🔨 v0.3 | 积雪 | 回收站 / 操作日志 / 文件搜索 |
| 🎯 v1.0 | 融雪 | 主题切换、移动端适配、稳定版本 |

---

## 🎀 吉祥物 · YukiChoco 酱

> “初次见面，我是 YukiChoco 酱～”  

她是一位银发的小小守护者，  
脖子上围着巧克力色的围巾，手里总捧着一杯冒热气的可可。  
她就住在你的网盘里，会在未来的版本中跳出来帮你找文件、提醒备份，  
或者只是安静地陪你看雪花落下。

*（也许有一天，你会在右下角看到她害羞地挥手 👋）*

---

## 🎨 设计小哲学

- ❄️ **冬天**：安静、干净、留白  
- 🍫 **巧克力**：温暖、柔和、有记忆的质感  

> 整个界面希望让你感觉——  
> **像在下雪的傍晚，打开一盒巧克力那样自然。** 🍫❄️

---

## 🧠 一点小心思 (Philosophy)

> “Cloud storage stores files.  
>  YukiChocoCloud stores moments.”  
>  
>  「クラウドストレージはファイルを保存する。  
>   YukiChocoCloud は、瞬間（とき）を保存する。」

---

## ⚠️ 温柔提醒 (Disclaimer)

这个小家伙是 **个人项目**，最适合：

- 🏠 部署在自己家里的服务器 / NAS / 树莓派上
- 👨‍👩‍👧‍👦 给家人或几个亲密朋友使用
- 📖 当作学习与实验的游乐场

目前还未做完整的高可用和商业级安全加固，  
如果你要在生产环境使用，请一定先仔细评估哦～ (*＾-＾*)

---

## ❤️ 一起让雪下得更大吧 (Contributing)

无论你是：

- 提交了一个 Issue  
- 送来了一份 Pull Request  
- 或者只是点亮了一颗 Star ⭐  

——所有形式的参与都像冬夜里多飘落的一片雪花，  
让这个世界更完整了一点。 ありがとう！

---

## ⭐ 星之轨迹 (Star History)

如果你觉得 YukiChocoCloud 有一点点温度，  
就给它一颗星星吧～ ☁️✨

---

## 👤 制作者 (Author)

**WinterChocolates**

> 做一点温柔的东西  
> 即使它只是一个网盘  
>  
> “在代码的雪原上，煮一壶可可等你。” ( ˘ ³˘)♥

---

## 📜 许可证 (License)

MIT License

---

## ❄️ 最后的最后

如果某一天，你无意中打开 YukiChocoCloud，  
翻到一个很久以前上传的文件——

那它就已经不仅仅是“文件”了。  

它是一个，被你保存在这里的、  
**不会融化的冬天。**

おやすみなさい。  
愿所有记忆，都能被温柔存放。 🌙