<template>
  <el-dialog
    :model-value="visible"
    title="分享管理"
    width="460px"
    :close-on-click-modal="false"
    class="share-dialog"
    @update:model-value="$emit('update:visible', $event)"
    @closed="resetState"
    @open="loadExistingShares"
  >
    <!-- 已有分享列表 -->
    <div v-if="existingShares.length > 0 && !shareResult" class="existing-shares">
      <div class="section-title">已有分享</div>
      <div v-for="share in existingShares" :key="share.id" class="share-item">
        <div class="share-item-info">
          <div class="share-link-text">
            {{ getShareLink(share.token) }}
          </div>
          <div class="share-meta">
            <span v-if="share.has_password" class="meta-tag">
              <el-icon :size="12"><Lock /></el-icon> 有密码
            </span>
            <span v-if="share.expire_at" class="meta-tag">
              <el-icon :size="12"><Timer /></el-icon> {{ formatExpireTime(share.expire_at) }}
            </span>
            <span v-if="!share.expire_at && !share.has_password" class="meta-tag">
              公开链接
            </span>
          </div>
        </div>
        <div class="share-item-actions">
          <button
            class="action-btn copy"
            title="复制链接"
            @click="copyShareLink(share.token)"
          >
            <el-icon :size="14"><CopyDocument /></el-icon>
          </button>
          <button
            class="action-btn delete"
            title="删除分享"
            @click="handleDelete(share)"
          >
            <el-icon :size="14"><Delete /></el-icon>
          </button>
        </div>
      </div>
      <div class="divider" />
    </div>

    <!-- 创建新分享表单 -->
    <div v-if="!shareResult" class="share-form">
      <div class="section-title">创建新分享</div>
      <div class="form-row">
        <span class="form-label">密码保护</span>
        <el-switch v-model="enablePassword" />
      </div>
      <div v-if="enablePassword" class="form-row">
        <el-input
          v-model="password"
          type="password"
          placeholder="设置访问密码"
          show-password
          size="large"
        />
      </div>

      <div class="form-row">
        <span class="form-label">过期时间</span>
        <el-select v-model="expireOption" size="large" style="width: 100%">
          <el-option label="永不过期" value="never" />
          <el-option label="1 小时" value="1h" />
          <el-option label="1 天" value="1d" />
          <el-option label="7 天" value="7d" />
          <el-option label="自定义" value="custom" />
        </el-select>
      </div>
      <div v-if="expireOption === 'custom'" class="form-row">
        <el-date-picker
          v-model="customExpireDate"
          type="datetime"
          placeholder="选择过期时间"
          size="large"
          style="width: 100%"
          :disabled-date="(date: Date) => date.getTime() < Date.now() - 86400000"
        />
      </div>
    </div>

    <!-- 创建成功结果 -->
    <div v-else class="share-result">
      <div class="result-info">
        <el-icon :size="20" class="success-icon"><CircleCheck /></el-icon>
        <span>分享链接已生成</span>
      </div>
      <div class="link-row">
        <el-input
          :model-value="shareLink"
          readonly
          size="large"
        />
        <el-button
          type="primary"
          size="large"
          class="copy-btn"
          @click="copyLink"
        >
          {{ copied ? '已复制' : '复制' }}
        </el-button>
      </div>
      <div v-if="shareResult.has_password" class="result-hint">
        <el-icon :size="14"><Lock /></el-icon>
        <span>已设置密码保护</span>
      </div>
      <div v-if="shareResult.expire_at" class="result-hint">
        <el-icon :size="14"><Timer /></el-icon>
        <span>过期时间：{{ formatExpireTime(shareResult.expire_at) }}</span>
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button size="large" @click="$emit('update:visible', false)">
          {{ shareResult ? '关闭' : '取消' }}
        </el-button>
        <el-button
          v-if="!shareResult"
          type="primary"
          size="large"
          :loading="loading"
          class="create-btn"
          @click="handleCreate"
        >
          创建分享
        </el-button>
        <el-button
          v-if="shareResult"
          size="large"
          @click="shareResult = null"
        >
          返回
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { CircleCheck, Lock, Timer, Delete, CopyDocument } from "@element-plus/icons-vue";
import { sharesApi, type FileInfo, type ShareInfo } from "@/api";

const props = defineProps<{
  visible: boolean;
  file: FileInfo | null;
}>();

defineEmits<{
  "update:visible": [value: boolean];
}>();

const enablePassword = ref(false);
const password = ref("");
const expireOption = ref("never");
const customExpireDate = ref<Date | null>(null);
const shareResult = ref<ShareInfo | null>(null);
const loading = ref(false);
const copied = ref(false);
const existingShares = ref<ShareInfo[]>([]);

const shareLink = computed(() => {
  if (!shareResult.value) return "";
  return getShareLink(shareResult.value.token);
});

function getShareLink(token: string): string {
  return `${window.location.origin}/share/${token}`;
}

function getExpireAt(): string | undefined {
  const now = Date.now();
  switch (expireOption.value) {
    case "1h":
      return new Date(now + 3600000).toISOString();
    case "1d":
      return new Date(now + 86400000).toISOString();
    case "7d":
      return new Date(now + 604800000).toISOString();
    case "custom":
      return customExpireDate.value?.toISOString();
    default:
      return undefined;
  }
}

async function loadExistingShares() {
  if (!props.file) return;
  try {
    const { data: res } = await sharesApi.listByFile(props.file.id);
    if (res.code === 0) {
      existingShares.value = res.data;
    }
  } catch {
    // ignore
  }
}

async function handleCreate() {
  if (!props.file) return;
  loading.value = true;
  try {
    const { data: res } = await sharesApi.create(
      props.file.id,
      enablePassword.value ? password.value : undefined,
      getExpireAt()
    );
    if (res.code === 0) {
      shareResult.value = res.data;
      await loadExistingShares();
    }
  } catch {
    ElMessage.error("创建分享失败");
  } finally {
    loading.value = false;
  }
}

async function handleDelete(share: ShareInfo) {
  try {
    await ElMessageBox.confirm(
      "确定要删除此分享链接吗？删除后将无法访问。",
      "删除分享",
      {
        confirmButtonText: "删除",
        cancelButtonText: "取消",
        type: "warning",
      }
    );
    const { data: res } = await sharesApi.remove(share.id);
    if (res.code === 0) {
      ElMessage.success("分享已删除");
      await loadExistingShares();
    }
  } catch {
    // User cancelled
  }
}

async function copyShareLink(token: string) {
  try {
    await navigator.clipboard.writeText(getShareLink(token));
    ElMessage.success("链接已复制到剪贴板");
  } catch {
    ElMessage.error("复制失败，请手动复制");
  }
}

async function copyLink() {
  try {
    await navigator.clipboard.writeText(shareLink.value);
    copied.value = true;
    ElMessage.success("链接已复制到剪贴板");
    setTimeout(() => {
      copied.value = false;
    }, 2000);
  } catch {
    ElMessage.error("复制失败，请手动复制");
  }
}

function formatExpireTime(dateStr: string): string {
  const date = new Date(dateStr);
  return date.toLocaleString("zh-CN", {
    month: "numeric",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function resetState() {
  enablePassword.value = false;
  password.value = "";
  expireOption.value = "never";
  customExpireDate.value = null;
  shareResult.value = null;
  loading.value = false;
  copied.value = false;
  existingShares.value = [];
}
</script>

<style scoped lang="scss">
@use "@/assets/styles/variables" as *;

.share-dialog {
  :deep(.el-dialog) {
    background: rgba(16, 22, 42, 0.95);
    backdrop-filter: blur(24px);
    -webkit-backdrop-filter: blur(24px);
    border: 1px solid rgba(100, 160, 220, 0.1);
    border-radius: $radius-lg;
    box-shadow: 0 16px 64px rgba(0, 0, 0, 0.5);
  }

  :deep(.el-dialog__header) {
    padding: 20px 24px 16px;
    margin: 0;
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  }

  :deep(.el-dialog__title) {
    font-size: 16px;
    font-weight: 600;
    color: $color-text-primary;
  }

  :deep(.el-dialog__headerbtn .el-dialog__close) {
    color: $color-text-secondary;

    &:hover {
      color: $color-text-primary;
    }
  }

  :deep(.el-dialog__body) {
    padding: 20px 24px;
  }

  :deep(.el-dialog__footer) {
    padding: 12px 24px 20px;
    border-top: 1px solid rgba(255, 255, 255, 0.06);
  }
}

.section-title {
  font-size: 13px;
  font-weight: 600;
  color: $color-text-muted;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 12px;
}

.existing-shares {
  margin-bottom: 16px;
}

.share-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 10px 12px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: $radius-sm;
  margin-bottom: 8px;

  &:hover {
    background: rgba(255, 255, 255, 0.05);
  }
}

.share-item-info {
  flex: 1;
  min-width: 0;
}

.share-link-text {
  font-size: 12px;
  color: $color-text-secondary;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-family: monospace;
}

.share-meta {
  display: flex;
  gap: 8px;
  margin-top: 4px;
}

.meta-tag {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  font-size: 11px;
  color: $color-text-muted;
}

.share-item-actions {
  display: flex;
  gap: 4px;
  flex-shrink: 0;
}

.action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 6px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.04);
  color: $color-text-secondary;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: rgba(255, 255, 255, 0.08);
    color: $color-text-primary;
  }

  &.delete:hover {
    background: rgba($color-danger, 0.15);
    border-color: rgba($color-danger, 0.3);
    color: $color-danger;
  }

  &.copy:hover {
    background: rgba($color-accent, 0.15);
    border-color: rgba($color-accent, 0.3);
    color: $color-accent;
  }
}

.divider {
  height: 1px;
  background: rgba(255, 255, 255, 0.06);
  margin: 16px 0;
}

.share-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;

  &:has(.el-input),
  &:has(.el-select),
  &:has(.el-date-picker) {
    flex-direction: column;
    align-items: stretch;
  }
}

.form-label {
  font-size: 14px;
  color: $color-text-secondary;
}

.share-result {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.result-info {
  display: flex;
  align-items: center;
  gap: 8px;
  color: $color-accent;
  font-size: 14px;
  font-weight: 500;
}

.success-icon {
  color: #67c23a;
}

.link-row {
  display: flex;
  gap: 8px;

  .el-input {
    flex: 1;
  }
}

.copy-btn {
  flex-shrink: 0;
}

.result-hint {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: $color-text-muted;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.create-btn {
  background: linear-gradient(135deg, #D4A853, #F5D799, #C49A6C);
  border: none;
  color: #1a1a2e;
  font-weight: 600;

  &:hover {
    background: linear-gradient(135deg, #E0B863, #FFE7A9, #D4AA7C);
  }
}
</style>
