<template>
  <div class="home-layout">
    <Topbar :username="userStore.username" @logout="handleLogout" />

    <div class="home-body">
      <Sidebar
        :folders="folderList"
        :current-parent-id="currentParentId"
        :storage="storageInfo"
        @navigate="navigateTo"
      />

      <main class="content-area">
        <div class="content-header">
          <div class="header-left">
            <button
              class="back-btn"
              :disabled="folderStack.length <= 1"
              title="返回上级目录"
              @click="goBack"
            >
              <el-icon :size="18"><Back /></el-icon>
            </button>
            <el-breadcrumb separator="/">
              <el-breadcrumb-item
                v-for="item in breadcrumbs"
                :key="item.id ?? 'root'"
              >
                <el-link @click="navigateTo(item.id)" class="breadcrumb-link">
                  {{ item.name }}
                </el-link>
              </el-breadcrumb-item>
            </el-breadcrumb>
          </div>

          <div class="header-actions">
            <Transition name="batch-bar">
              <div v-if="selectedIds.size > 0" class="batch-action-bar">
                <span class="bar-info">已选 {{ selectedIds.size }} 项</span>
                <span class="bar-divider"></span>
                <button class="bar-btn download" @click="handleBatchDownload">
                  <el-icon :size="14"><Download /></el-icon>
                  <span>下载</span>
                </button>
                <button class="bar-btn danger" @click="handleBatchDelete">
                  <el-icon :size="14"><Delete /></el-icon>
                  <span>删除</span>
                </button>
                <button class="bar-btn text-btn" @click="clearSelection">
                  取消选择
                </button>
              </div>
            </Transition>
            <button
              v-if="files.length > 0"
              class="select-all-pill"
              :class="{ active: allSelected }"
              @click="toggleSelectAll"
            >
              {{ allSelected ? '取消全选' : '全选' }}
            </button>
            <input
              ref="headerFileInput"
              type="file"
              class="hidden-input"
              multiple
              @change="handleHeaderUpload"
            />
            <button class="upload-gold-btn" @click="headerFileInput?.click()">
              <el-icon :size="16"><Upload /></el-icon>
              <span>上传文件</span>
            </button>
          </div>
        </div>

        <div
          class="file-grid"
          v-loading="loading"
          @dragover.prevent
          @dragenter.prevent="onDragEnter"
          @dragleave.prevent="onDragLeave"
          @drop.prevent="onDrop"
        >
          <div v-if="isDragging" class="drop-overlay">
            <el-icon :size="48"><Upload /></el-icon>
            <span>拖放文件到此处上传</span>
          </div>
          <FileCard
            v-for="file in files"
            :key="file.id"
            :file="file"
            :selected="selectedIds.has(file.id)"
            @click="file.is_dir ? navigateTo(file.id) : toggleSelect(file.id)"
            @download="handleDownload(file)"
            @preview="openPreview(file)"
            @delete="handleDelete(file)"
            @share="handleShare(file)"
            @toggle-select="toggleSelect(file.id)"
          />

          <template v-if="loading && files.length === 0">
            <div v-for="n in 6" :key="n" class="skeleton-card">
              <div class="skeleton-icon" />
              <div class="skeleton-line skeleton-line--name" />
              <div class="skeleton-line skeleton-line--date" />
            </div>
          </template>

          <div v-if="!loading && files.length === 0" class="empty-state">
            <div class="empty-icon">📂</div>
            <p class="empty-text">暂无文件</p>
            <p class="empty-hint">点击右下角按钮上传文件</p>
          </div>
        </div>
      </main>
    </div>

    <UploadFloatButton
      ref="uploadFloatRef"
      @upload="handleUpload"
      @create-folder="handleCreateFolder"
    />

    <ShareDialog
      v-model:visible="shareDialogVisible"
      :file="shareFile"
    />

    <Teleport to="body">
      <Transition name="fade">
        <div
          v-if="previewFile"
          class="preview-overlay"
          @click.self="closePreview"
        >
          <div class="preview-container">
            <div class="preview-header">
              <span class="preview-name">{{ previewFile.name }}</span>
              <button class="preview-close" @click="closePreview">
                <el-icon :size="20"><Close /></el-icon>
              </button>
            </div>
            <div class="preview-body">
              <video
                v-if="previewUrl && isPreviewVideo"
                :src="previewUrl"
                class="preview-video"
                controls
                autoplay
              />
              <img
                v-else-if="previewUrl"
                :src="previewUrl"
                :alt="previewFile.name"
                class="preview-img"
              />
              <div v-else class="preview-loading">
                <el-icon :size="32" class="loading-icon"><Loading /></el-icon>
              </div>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import { useRouter } from "vue-router";
import { ElMessage, ElMessageBox } from "element-plus";
import { Upload, Download, Close, Loading, Back, Delete } from "@element-plus/icons-vue";
import { filesApi, type FileInfo, type StorageInfo } from "@/api";
import { useUserStore } from "@/stores/user";
import Topbar from "@/components/Topbar.vue";
import Sidebar from "@/components/Sidebar.vue";
import FileCard from "@/components/FileCard.vue";
import UploadFloatButton from "@/components/UploadFloatButton.vue";
import ShareDialog from "@/components/ShareDialog.vue";

const router = useRouter();
const userStore = useUserStore();

const uploadFloatRef = ref<InstanceType<typeof UploadFloatButton>>();
const files = ref<FileInfo[]>([]);
const loading = ref(false);
const currentParentId = ref<number | undefined>(undefined);
const headerFileInput = ref<HTMLInputElement>();
const selectedIds = ref<Set<number>>(new Set());
const previewFile = ref<FileInfo | null>(null);
const previewUrl = ref<string>();
const storageInfo = ref<StorageInfo>({ used: 0, total: 0 });
const isDragging = ref(false);
let dragCounter = 0;
const shareDialogVisible = ref(false);

const VIDEO_EXTS = /\.(mp4|mkv|avi|mov|webm)$/i;
const isPreviewVideo = computed(() => previewFile.value && VIDEO_EXTS.test(previewFile.value.name));
const shareFile = ref<FileInfo | null>(null);
const folderStack = ref<{ id?: number; name: string }[]>([
  { id: undefined, name: "根目录" },
]);

const breadcrumbs = computed(() => folderStack.value);

const folderList = computed(() => files.value.filter((f) => f.is_dir));

const allSelected = computed(() => {
  if (files.value.length === 0) return false;
  return files.value.every((f) => selectedIds.value.has(f.id));
});

async function loadFiles(parentId?: number) {
  loading.value = true;
  try {
    const { data: res } = await filesApi.list(parentId);
    if (res.code === 0) {
      files.value = res.data;
    }
  } finally {
    loading.value = false;
  }
}

async function loadStorageInfo() {
  try {
    const { data: res } = await filesApi.getStorageInfo();
    if (res.code === 0) {
      storageInfo.value = res.data;
    }
  } catch {
    // ignore
  }
}

function navigateTo(id?: number) {
  if (id === undefined) {
    currentParentId.value = undefined;
    folderStack.value = [{ id: undefined, name: "根目录" }];
  } else {
    currentParentId.value = id;
    const existingIndex = folderStack.value.findIndex((item) => item.id === id);
    if (existingIndex >= 0) {
      folderStack.value = folderStack.value.slice(0, existingIndex + 1);
    } else {
      const file = files.value.find((f) => f.id === id);
      folderStack.value.push({ id, name: file?.name ?? "未知文件夹" });
    }
  }
  loadFiles(currentParentId.value);
  clearSelection();
}

function goBack() {
  if (folderStack.value.length <= 1) return;
  const parentIndex = folderStack.value.length - 2;
  const parent = folderStack.value[parentIndex];
  navigateTo(parent.id);
}

function handleLogout() {
  userStore.logout();
  router.push("/login");
}

async function handleUpload(fileList: FileList) {
  const files = Array.from(fileList);
  let successCount = 0;
  for (const file of files) {
    try {
      const { data: res } = await filesApi.upload(file, currentParentId.value);
      if (res.code === 0) successCount++;
    } catch {
      ElMessage.error(`上传失败: ${file.name}`);
    }
  }
  if (successCount > 0) {
    ElMessage.success(`成功上传 ${successCount} 个文件`);
    loadFiles(currentParentId.value);
    loadStorageInfo();
  }
  uploadFloatRef.value?.clearInput();
}

async function handleHeaderUpload(e: Event) {
  const target = e.target as HTMLInputElement;
  if (target.files && target.files.length > 0) {
    await handleUpload(target.files);
    target.value = "";
  }
}

async function handleDownload(file: FileInfo) {
  if (file.is_dir) return;
  try {
    const res = await filesApi.download(file.id);
    const url = window.URL.createObjectURL(res.data);
    const a = document.createElement("a");
    a.href = url;
    a.download = file.name;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
    ElMessage.success("下载完成");
  } catch {
    ElMessage.error("下载失败");
  }
}

async function handleDelete(file: FileInfo) {
  try {
    await ElMessageBox.confirm(
      `确定要删除「${file.name}」吗？`,
      "删除确认",
      {
        confirmButtonText: "删除",
        cancelButtonText: "取消",
        type: "warning",
      }
    );
    const { data: res } = await filesApi.remove(file.id);
    if (res.code === 0) {
      ElMessage.success("删除成功");
      const next = new Set(selectedIds.value);
      next.delete(file.id);
      selectedIds.value = next;
      loadFiles(currentParentId.value);
      loadStorageInfo();
    }
  } catch {
    // User cancelled
  }
}

function toggleSelect(id: number) {
  const next = new Set(selectedIds.value);
  if (next.has(id)) {
    next.delete(id);
  } else {
    next.add(id);
  }
  selectedIds.value = next;
}

function clearSelection() {
  selectedIds.value = new Set();
}

function toggleSelectAll() {
  if (allSelected.value) {
    selectedIds.value = new Set();
  } else {
    selectedIds.value = new Set(files.value.map((f) => f.id));
  }
}

async function handleBatchDownload() {
  const selected = files.value.filter(
    (f) => selectedIds.value.has(f.id) && !f.is_dir
  );
  if (selected.length === 0) {
    ElMessage.warning("选中项中没有可下载的文件");
    return;
  }
  ElMessage.info(`开始下载 ${selected.length} 个文件...`);
  let successCount = 0;
  for (const file of selected) {
    try {
      const res = await filesApi.download(file.id);
      const url = window.URL.createObjectURL(res.data);
      const a = document.createElement("a");
      a.href = url;
      a.download = file.name;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
      successCount++;
    } catch {
      ElMessage.error(`下载失败: ${file.name}`);
    }
  }
  if (successCount > 0) {
    ElMessage.success(`成功下载 ${successCount} 个文件`);
  }
}

async function handleBatchDelete() {
  const count = selectedIds.value.size;
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${count} 个项目吗？`,
      "批量删除",
      {
        confirmButtonText: "删除",
        cancelButtonText: "取消",
        type: "warning",
      }
    );
  } catch {
    return;
  }
  const toDelete = files.value.filter((f) => selectedIds.value.has(f.id));
  let successCount = 0;
  for (const file of toDelete) {
    try {
      const { data: res } = await filesApi.remove(file.id);
      if (res.code === 0) successCount++;
    } catch {
      ElMessage.error(`删除失败: ${file.name}`);
    }
  }
  if (successCount > 0) {
    ElMessage.success(`成功删除 ${successCount} 个项目`);
    clearSelection();
    loadFiles(currentParentId.value);
    loadStorageInfo();
  }
}

async function openPreview(file: FileInfo) {
  previewFile.value = file;
  previewUrl.value = undefined;
  try {
    const res = await filesApi.preview(file.id);
    previewUrl.value = window.URL.createObjectURL(res.data);
  } catch {
    ElMessage.error("图片加载失败");
    previewFile.value = null;
  }
}

function closePreview() {
  if (previewUrl.value) {
    window.URL.revokeObjectURL(previewUrl.value);
  }
  previewUrl.value = undefined;
  previewFile.value = null;
}

function handleShare(file: FileInfo) {
  shareFile.value = file;
  shareDialogVisible.value = true;
}

async function handleCreateFolder() {
  try {
    const { value } = await ElMessageBox.prompt(
      "请输入文件夹名称",
      "新建文件夹",
      {
        confirmButtonText: "创建",
        cancelButtonText: "取消",
        inputPlaceholder: "文件夹名称",
      }
    );
    if (value) {
      const { data: res } = await filesApi.createFolder(
        value,
        currentParentId.value
      );
      if (res.code === 0) {
        ElMessage.success("文件夹创建成功");
        loadFiles(currentParentId.value);
      }
    }
  } catch {
    // User cancelled
  }
}

function onDragEnter() {
  dragCounter++;
  isDragging.value = true;
}

function onDragLeave() {
  dragCounter--;
  if (dragCounter <= 0) {
    isDragging.value = false;
    dragCounter = 0;
  }
}

function onDrop(e: DragEvent) {
  isDragging.value = false;
  dragCounter = 0;
  if (e.dataTransfer?.files && e.dataTransfer.files.length > 0) {
    handleUpload(e.dataTransfer.files);
  }
}

onMounted(() => {
  loadFiles();
  loadStorageInfo();
});
</script>

<style scoped lang="scss">
@use "@/assets/styles/variables" as *;

.home-layout {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
}

.home-body {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.content-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.content-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 28px;
  flex-shrink: 0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.back-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: $radius-sm;
  color: $color-text-secondary;
  cursor: pointer;
  transition: all $transition-fast;
  flex-shrink: 0;

  &:hover:not(:disabled) {
    background: rgba($color-chocolate, 0.15);
    border-color: rgba($color-chocolate, 0.3);
    color: $color-chocolate-light;
  }

  &:disabled {
    opacity: 0.3;
    cursor: not-allowed;
  }
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.hidden-input {
  display: none;
}

.batch-action-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  height: $action-bar-height;
  padding: 0 20px;
  border-radius: $action-bar-radius;
  background: rgba(14, 18, 32, 0.75);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border: 1px solid rgba(100, 160, 220, 0.1);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.04), 0 8px 32px rgba(0, 0, 0, 0.3);
}

.bar-info {
  font-size: 13px;
  color: $color-text-secondary;
  font-weight: 500;
  white-space: nowrap;
}

.bar-divider {
  width: 1px;
  height: 24px;
  background: rgba(255, 255, 255, 0.08);
  margin: 0 4px;
}

.bar-btn {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 7px 14px;
  border-radius: 12px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  border: none;
  transition: all 0.2s ease;

  &.download {
    background: rgba(139, 105, 20, 0.15);
    border: 1px solid rgba(196, 154, 108, 0.3);
    color: $color-chocolate-light;

    &:hover {
      box-shadow: 0 0 20px rgba(196, 154, 108, 0.35);
      background: rgba(139, 105, 20, 0.25);
    }
  }

  &.danger {
    background: rgba($color-danger, 0.1);
    border: 1px solid rgba($color-danger, 0.2);
    color: $color-danger;

    &:hover {
      box-shadow: 0 0 20px rgba($color-danger, 0.3);
      background: rgba($color-danger, 0.18);
    }
  }

  &.text-btn {
    background: transparent;
    border: none;
    color: $color-text-secondary;
    padding: 7px 10px;
    position: relative;

    &::after {
      content: "";
      position: absolute;
      bottom: 4px;
      left: 10px;
      right: 10px;
      height: 1px;
      background: $color-text-secondary;
      transform: scaleX(0);
      transition: transform 0.25s ease;
    }

    &:hover {
      color: $color-text-primary;

      &::after {
        transform: scaleX(1);
      }
    }
  }
}

.select-all-pill {
  display: inline-flex;
  align-items: center;
  padding: 6px 16px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: $color-text-secondary;
  transition: all 0.2s ease;

  &:hover {
    background: rgba(255, 255, 255, 0.08);
    color: $color-text-primary;
  }

  &.active {
    background: rgba($color-accent, 0.12);
    border-color: rgba($color-accent, 0.3);
    color: $color-accent;
    box-shadow: 0 0 12px rgba($color-accent, 0.15);
  }
}

.upload-gold-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 9px 20px;
  border-radius: 14px;
  background: linear-gradient(135deg, #D4A853, #F5D799, #C49A6C);
  color: #1a1a2e;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  border: none;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.3), 0 4px 16px rgba(0, 0, 0, 0.2);
  transition: all 0.25s ease;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 0 24px rgba(212, 168, 83, 0.4), 0 8px 24px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.3);
  }

  &:active {
    transform: translateY(0) scale(0.97);
  }
}

.breadcrumb-link {
  color: $color-text-secondary !important;
  font-size: 13px;

  &:hover {
    color: $color-chocolate-light !important;
  }
}

.file-grid {
  position: relative;
  flex: 1;
  display: flex;
  flex-wrap: wrap;
  align-content: flex-start;
  gap: 16px;
  padding: 0 28px 28px;
  overflow-y: auto;
  z-index: $z-sticky;
}

.skeleton-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 180px;
  height: 220px;
  padding: 12px;
  border-radius: 20px;
  background: linear-gradient(165deg, rgba(16, 22, 42, 0.6), rgba(10, 14, 28, 0.7));
  border: 1px solid rgba(100, 160, 220, 0.04);
}

.skeleton-icon {
  width: 88px;
  height: 88px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.04);
  margin: 16px 0 20px;
  animation: shimmer 1.5s ease-in-out infinite;
  background-image: linear-gradient(90deg, transparent 0%, rgba(255, 255, 255, 0.03) 50%, transparent 100%);
  background-size: 200% 100%;
}

.skeleton-line {
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.04);
  animation: shimmer 1.5s ease-in-out infinite;
  background-image: linear-gradient(90deg, transparent 0%, rgba(255, 255, 255, 0.03) 50%, transparent 100%);
  background-size: 200% 100%;

  &--name {
    width: 100px;
    height: 14px;
    margin-bottom: 8px;
  }

  &--date {
    width: 60px;
    height: 12px;
  }
}

.drop-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  background: rgba($color-accent, 0.06);
  backdrop-filter: blur(4px);
  border: 2px dashed rgba($color-accent, 0.4);
  border-radius: $radius-lg;
  z-index: $z-content;
  color: $color-accent;
  font-size: 16px;
  font-weight: 500;
  pointer-events: none;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  padding: 80px 20px;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
  opacity: 0.6;
}

.empty-text {
  font-size: 16px;
  color: $color-text-secondary;
  margin: 0 0 8px;
}

.empty-hint {
  font-size: 13px;
  color: $color-text-muted;
  margin: 0;
}

.preview-overlay {
  position: fixed;
  inset: 0;
  z-index: $z-modal;

  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.75);
  backdrop-filter: blur(8px);
}

.preview-container {
  display: flex;
  flex-direction: column;
  max-width: 90vw;
  max-height: 90vh;
  background: $bg-secondary;
  border: $glass-border;
  border-radius: $radius-lg;
  overflow: hidden;
  box-shadow: 0 16px 64px rgba(0, 0, 0, 0.5);
}

.preview-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  flex-shrink: 0;
}

.preview-name {
  font-size: 14px;
  font-weight: 500;
  color: $color-text-primary;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin-right: 16px;
}

.preview-close {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: none;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: $radius-sm;
  color: $color-text-secondary;
  cursor: pointer;
  transition: all $transition-fast;
  flex-shrink: 0;

  &:hover {
    color: $color-text-primary;
    background: rgba(255, 255, 255, 0.06);
  }
}

.preview-body {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
  min-width: 200px;
  min-height: 200px;
}

.preview-img {
  max-width: 85vw;
  max-height: 80vh;
  object-fit: contain;
  border-radius: $radius-sm;
}

.preview-video {
  max-width: 85vw;
  max-height: 80vh;
  border-radius: $radius-sm;
  outline: none;
}

.preview-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 80px;
  height: 80px;
  color: $color-text-muted;
}

.loading-icon {
  animation: spin 1s linear infinite;
}
</style>
