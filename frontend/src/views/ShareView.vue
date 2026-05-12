<template>
  <div class="share-page">
    <div class="share-card glass-card" :class="{ visible: mounted }">
      <div class="card-header">
        <div class="logo-row">
          <svg class="logo-svg" width="48" height="48" viewBox="0 0 24 24" fill="none" aria-hidden="true">
            <path d="M12 2v20M2 12h20M5.6 5.6l12.8 12.8M18.4 5.6L5.6 18.4" stroke="url(#share-logo-grad)" stroke-width="1.5" stroke-linecap="round"/>
            <circle cx="12" cy="12" r="3" fill="url(#share-logo-grad)" opacity="0.8"/>
            <defs><linearGradient id="share-logo-grad" x1="0" y1="0" x2="24" y2="24"><stop stop-color="#C49A6C"/><stop offset="1" stop-color="#8B6914"/></linearGradient></defs>
          </svg>
        </div>
        <h1 class="logo-title">YukiChocoCloud</h1>
        <p class="logo-subtitle">文件分享</p>
      </div>

      <div class="card-body">
        <!-- Loading State -->
        <div v-if="step === 'loading'" class="state-loading">
          <el-icon :size="32" class="loading-icon"><Loading /></el-icon>
          <span class="state-text">正在验证分享链接...</span>
        </div>

        <!-- Password State -->
        <div v-else-if="step === 'password'" class="state-password">
          <div class="password-icon">
            <el-icon :size="36"><Lock /></el-icon>
          </div>
          <p class="state-text">此分享需要密码访问</p>
          <el-input
            v-model="password"
            type="password"
            placeholder="请输入访问密码"
            size="large"
            show-password
            @keyup.enter="handleAccess"
          />
          <el-button
            type="primary"
            size="large"
            :loading="accessing"
            class="access-btn"
            @click="handleAccess"
          >
            访问
          </el-button>
          <p v-if="passwordError" class="error-hint">{{ passwordError }}</p>
        </div>

        <!-- Ready State -->
        <div v-else-if="step === 'ready'" class="state-ready">
          <div class="file-icon-wrapper">
            <el-icon :size="48"><Document /></el-icon>
          </div>
          <div class="file-info">
            <h2 class="file-name">{{ fileInfo?.file_name }}</h2>
            <p class="file-size">{{ formatSize(fileInfo?.file_size ?? 0) }}</p>
          </div>
          <el-button
            v-if="!fileInfo?.is_dir"
            type="primary"
            size="large"
            :loading="downloading"
            class="download-btn"
            @click="handleDownload"
          >
            <el-icon :size="18"><Download /></el-icon>
            <span>下载文件</span>
          </el-button>
          <p v-else class="folder-hint">文件夹分享暂不支持下载</p>
        </div>

        <!-- Error State -->
        <div v-else-if="step === 'error'" class="state-error">
          <div class="error-icon">
            <el-icon :size="48"><CircleClose /></el-icon>
          </div>
          <p class="error-message">{{ errorMessage }}</p>
          <el-button size="large" class="back-btn" @click="router.push('/')">
            返回首页
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { Loading, Lock, Document, Download, CircleClose } from "@element-plus/icons-vue";
import { sharesApi, type PublicShareInfo } from "@/api";

const route = useRoute();
const router = useRouter();

const step = ref<"loading" | "password" | "ready" | "error">("loading");
const mounted = ref(false);
const password = ref("");
const passwordError = ref("");
const accessing = ref(false);
const downloading = ref(false);
const fileInfo = ref<PublicShareInfo | null>(null);
const errorMessage = ref("");

const token = route.params.token as string;

function formatSize(bytes: number): string {
  if (bytes === 0) return "0 B";
  const units = ["B", "KB", "MB", "GB", "TB"];
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${units[i]}`;
}

async function tryAccess(pwd?: string) {
  try {
    const { data: res } = await sharesApi.access(token, pwd);
    if (res.code === 0) {
      fileInfo.value = res.data;
      step.value = "ready";
    }
  } catch (err: any) {
    const status = err.response?.status;
    const detail = err.response?.data?.detail || "";

    if (status === 404) {
      step.value = "error";
      errorMessage.value = "分享链接不存在";
    } else if (status === 403) {
      if (detail.toLowerCase().includes("expired")) {
        step.value = "error";
        errorMessage.value = "分享链接已过期";
      } else if (detail.toLowerCase().includes("password")) {
        step.value = "password";
      } else {
        step.value = "password";
      }
    } else {
      step.value = "error";
      errorMessage.value = "访问失败，请稍后重试";
    }
  }
}

async function handleAccess() {
  if (!password.value) {
    passwordError.value = "请输入密码";
    return;
  }
  passwordError.value = "";
  accessing.value = true;
  try {
    const { data: res } = await sharesApi.access(token, password.value);
    if (res.code === 0) {
      fileInfo.value = res.data;
      step.value = "ready";
    }
  } catch (err: any) {
    const status = err.response?.status;
    const detail = err.response?.data?.detail || "";

    if (status === 403) {
      if (detail.toLowerCase().includes("expired")) {
        step.value = "error";
        errorMessage.value = "分享链接已过期";
      } else {
        passwordError.value = "密码错误";
      }
    } else if (status === 404) {
      step.value = "error";
      errorMessage.value = "分享链接不存在";
    } else {
      passwordError.value = "访问失败，请稍后重试";
    }
  } finally {
    accessing.value = false;
  }
}

async function handleDownload() {
  downloading.value = true;
  try {
    const res = await sharesApi.download(token, password.value || undefined);
    const url = window.URL.createObjectURL(res.data);
    const a = document.createElement("a");
    a.href = url;
    a.download = fileInfo.value?.file_name || "download";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
    ElMessage.success("下载完成");
  } catch {
    ElMessage.error("下载失败");
  } finally {
    downloading.value = false;
  }
}

onMounted(() => {
  requestAnimationFrame(() => {
    mounted.value = true;
  });
  tryAccess();
});
</script>

<style scoped lang="scss">
@use "@/assets/styles/variables" as *;

.share-page {
  position: relative;
  z-index: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100%;
  background: radial-gradient(ellipse at 50% 30%, rgba($color-accent, 0.06) 0%, transparent 60%);
}

.share-card {
  width: 420px;
  padding: 40px 36px 36px;
  opacity: 0;
  transform: translateY(24px);
  transition: opacity 0.6s ease, transform 0.6s ease;

  &.visible {
    opacity: 1;
    transform: translateY(0);
  }
}

.card-header {
  text-align: center;
  margin-bottom: 32px;
}

.logo-row {
  margin-bottom: 16px;
}

.logo-svg {
  display: inline-block;
  animation: float 3s ease-in-out 2;
}

.logo-title {
  font-size: 24px;
  font-weight: 700;
  margin: 0 0 8px;
  background: $color-chocolate-gradient;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.logo-subtitle {
  font-size: 12px;
  color: $color-text-muted;
  margin: 0;
  letter-spacing: 0.5px;
}

.card-body {
  min-height: 200px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.state-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.loading-icon {
  color: $color-accent;
  animation: spin 1s linear infinite;
}

.state-text {
  font-size: 14px;
  color: $color-text-secondary;
}

.state-password {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  width: 100%;
}

.password-icon {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba($color-accent, 0.1);
  color: $color-accent;
  margin-bottom: 8px;
}

.access-btn {
  width: 100%;
  height: 42px;
  font-size: 15px;
  letter-spacing: 2px;
  margin-top: 4px;
}

.error-hint {
  font-size: 13px;
  color: $color-danger;
  margin: 0;
}

.state-ready {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
  width: 100%;
}

.file-icon-wrapper {
  width: 88px;
  height: 88px;
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(20, 24, 36, 0.5);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.06);
  color: $color-text-secondary;
}

.file-info {
  text-align: center;
}

.file-name {
  font-size: 18px;
  font-weight: 600;
  color: $color-text-primary;
  margin: 0 0 8px;
  word-break: break-all;
}

.file-size {
  font-size: 14px;
  color: $color-text-muted;
  margin: 0;
}

.download-btn {
  width: 100%;
  height: 48px;
  font-size: 16px;
  font-weight: 600;
  gap: 8px;
  background: linear-gradient(135deg, #D4A853, #F5D799, #C49A6C);
  border: none;
  color: #1a1a2e;

  &:hover {
    background: linear-gradient(135deg, #E0B863, #FFE7A9, #D4AA7C);
  }
}

.folder-hint {
  font-size: 14px;
  color: $color-text-muted;
  margin: 0;
}

.state-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.error-icon {
  color: $color-danger;
  opacity: 0.8;
}

.error-message {
  font-size: 16px;
  color: $color-text-secondary;
  margin: 0;
  text-align: center;
}

.back-btn {
  margin-top: 8px;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
