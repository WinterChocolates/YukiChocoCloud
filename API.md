# YukiChocoCloud API 文档

Base URL: `http://localhost:8000`

## 响应格式

所有接口统一返回：

```json
{
  "code": 0,
  "message": "ok",
  "data": {}
}
```

错误响应返回对应 HTTP 状态码：

```json
{
  "detail": "错误信息"
}
```

## 认证方式

需要认证的接口须在请求头中携带：`Authorization: Bearer <token>`

---

## 认证

### 注册

```
POST /api/auth/register
```

**请求体：**

```json
{
  "username": "string (3-64 字符)",
  "password": "string (6-128 字符)"
}
```

**响应：**

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "id": 1,
    "username": "alice",
    "is_admin": false,
    "created_at": "2026-05-06T00:00:00"
  }
}
```

**错误：**
- `400` - 用户名已被注册

---

### 登录

```
POST /api/auth/login
```

**请求体：**

```json
{
  "username": "string",
  "password": "string"
}
```

**响应：**

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
  }
}
```

**错误：**
- `401` - 用户名或密码错误

---

## 文件管理

> 所有文件接口需要认证。

### 获取文件列表

```
GET /api/files?parent_id=
```

**查询参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| parent_id | int | 否 | 父目录 ID，省略则返回根目录 |

**请求体：** 无

**响应：**

```json
{
  "code": 0,
  "message": "ok",
  "data": [
    {
      "id": 1,
      "name": "Documents",
      "is_dir": true,
      "size": 0,
      "created_at": "2026-05-06T00:00:00"
    },
    {
      "id": 2,
      "name": "photo.png",
      "is_dir": false,
      "size": 102400,
      "created_at": "2026-05-06T00:01:00"
    }
  ]
}
```

---

### 创建文件夹

```
POST /api/files
```

**请求体：**

```json
{
  "name": "string (1-255 字符)",
  "parent_id": null
}
```

**响应：**

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "id": 3,
    "name": "Photos",
    "is_dir": true,
    "size": 0,
    "created_at": "2026-05-06T00:02:00"
  }
}
```

**错误：**
- `400` - 父目录不存在

---

### 删除文件

```
DELETE /api/files/{file_id}
```

软删除，将 `is_deleted` 置为 `true`，同时删除物理文件。删除文件夹时会递归删除所有子文件的物理文件。

**请求体：** 无

**响应：**

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "id": 2,
    "name": "photo.png",
    "is_dir": false,
    "size": 102400,
    "created_at": "2026-05-06T00:01:00"
  }
}
```

**错误：**
- `404` - 文件不存在

---

## 上传与下载

> 所有上传/下载接口需要认证。

### 上传文件

```
POST /api/upload
Content-Type: multipart/form-data
```

**表单字段：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| file | File | 是 | 上传的文件 |
| parent_id | int | 否 | 目标目录 ID |

文件存储路径：`uploads/{user_id}/{year}/{month}/{filename}`

**响应：**

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "id": 4,
    "name": "report.pdf",
    "is_dir": false,
    "size": 2048000,
    "created_at": "2026-05-06T00:03:00"
  }
}
```

---

### 下载文件

```
GET /api/download/{file_id}
```

**请求体：** 无

**响应：** 流式文件下载（`application/octet-stream`）。

**错误：**
- `404` - 文件不存在

---

### 预览文件

```
GET /api/preview/{file_id}
```

以 inline 方式返回文件内容（自动识别 MIME 类型），适用于图片等浏览器可直接渲染的文件。

**请求体：** 无

**响应：** 流式文件内容（`image/png`、`image/jpeg` 等对应 MIME 类型）。

**错误：**
- `404` - 文件不存在

---

### 获取存储信息

```
GET /api/files/storage
```

**请求体：** 无

**响应：**

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "used": 524288000,
    "total": 10737418240
  }
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| used | int | 已使用存储空间（字节） |
| total | int | 总存储空间（字节，默认 10 GB） |

---

## 分享

### 创建分享

```
POST /api/shares
```

需要认证。

**请求体：**

```json
{
  "file_id": 2,
  "password": "可选密码",
  "expire_at": "2026-05-13T00:00:00"
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| file_id | int | 是 | 要分享的文件 ID |
| password | string | 否 | 访问密码（最长 128 字符） |
| expire_at | datetime | 否 | 过期时间（ISO 8601 格式） |

**响应：**

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "id": 1,
    "token": "a1b2c3d4e5f6...",
    "file_id": 2,
    "has_password": true,
    "expire_at": "2026-05-13T00:00:00",
    "created_at": "2026-05-06T00:04:00"
  }
}
```

**错误：**
- `404` - 文件不存在

---

### 访问分享

```
POST /api/public/share/{token}
```

无需认证。

**请求体（可选）：**

```json
{
  "password": "string"
}
```

**响应：**

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "file_name": "photo.png",
    "file_size": 102400,
    "is_dir": false
  }
}
```

**错误：**
- `404` - 分享不存在
- `403` - 分享链接已过期
- `403` - 密码错误

---

## 健康检查

```
GET /health
```

**请求体：** 无

**响应：**

```json
{
  "status": "ok"
}
```
