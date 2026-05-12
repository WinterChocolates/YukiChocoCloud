<template>
  <aside class="sidebar glass-card">
    <div class="sidebar-header">
      <span class="sidebar-title">文件管理</span>
    </div>

    <nav class="sidebar-nav">
      <div
        class="nav-item"
        :class="{ active: currentParentId === undefined }"
        @click="$emit('navigate', undefined)"
      >
        <el-icon class="nav-icon"><HomeFilled /></el-icon>
        <span>全部文件</span>
      </div>

      <div class="nav-divider" />

      <div class="nav-section-title">最近访问</div>

      <div
        v-for="folder in folders"
        :key="folder.id"
        class="nav-item"
        :class="{ active: currentParentId === folder.id }"
        @click="$emit('navigate', folder.id)"
      >
        <el-icon class="nav-icon folder-icon"><Folder /></el-icon>
        <span class="nav-label">{{ folder.name }}</span>
      </div>

      <div v-if="folders.length === 0" class="nav-empty">
        暂无文件夹
      </div>
    </nav>

    <div class="sidebar-footer">
      <div class="storage-stats">
        <div class="storage-label">存储空间</div>
        <div class="storage-bar-container">
          <div class="storage-bar">
            <div class="storage-fill" :style="{ width: storagePercent + '%' }" />
          </div>
          <span class="storage-usage">{{ formatBytes(storage.used) }} / {{ formatBytes(storage.total) }}</span>
        </div>
      </div>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { Folder, HomeFilled } from "@element-plus/icons-vue";
import type { FileInfo, StorageInfo } from "@/api";

const props = defineProps<{
  folders: FileInfo[];
  currentParentId?: number;
  storage: StorageInfo;
}>();

defineEmits<{
  navigate: [id: number | undefined];
}>();

function formatBytes(bytes: number): string {
  if (bytes === 0) return "0 B";
  const units = ["B", "KB", "MB", "GB", "TB"];
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${units[i]}`;
}

const storagePercent = computed(() => {
  if (props.storage.total === 0) return 0;
  return Math.min(100, Math.round((props.storage.used / props.storage.total) * 100));
});
</script>

<style scoped lang="scss">
@use "@/assets/styles/variables" as *;

.sidebar {
  display: flex;
  flex-direction: column;
  width: $sidebar-width;
  height: 100%;
  border-radius: 0;
  border-right: 1px solid rgba(255, 255, 255, 0.06);
  overflow: hidden;
}

.sidebar-header {
  padding: 20px 20px 12px;
  flex-shrink: 0;
}

.sidebar-title {
  font-size: 13px;
  font-weight: 600;
  color: $color-text-secondary;
  letter-spacing: 1px;
  text-transform: uppercase;
}

.sidebar-nav {
  flex: 1;
  overflow-y: auto;
  padding: 4px 12px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: $radius-sm;
  color: $color-text-secondary;
  cursor: pointer;
  transition: all $transition-fast;
  font-size: 14px;
  margin-bottom: 2px;

  &:hover {
    background: rgba(255, 255, 255, 0.04);
    color: $color-text-primary;
  }

  &.active {
    background: rgba($color-chocolate, 0.12);
    color: $color-chocolate-light;
    border-left: 3px solid $color-chocolate;
    padding-left: 9px;

    .nav-icon {
      color: $color-chocolate-light;
    }
  }
}

.nav-icon {
  font-size: 18px;
  flex-shrink: 0;
}

.folder-icon {
  color: $color-chocolate-light;
}

.nav-label {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.nav-divider {
  height: 1px;
  background: rgba(255, 255, 255, 0.06);
  margin: 8px 12px;
}

.nav-section-title {
  font-size: 11px;
  font-weight: 600;
  color: $color-text-muted;
  letter-spacing: 0.5px;
  padding: 8px 12px 4px;
  text-transform: uppercase;
}

.nav-empty {
  font-size: 12px;
  color: $color-text-muted;
  padding: 16px 12px;
  text-align: center;
}

.sidebar-footer {
  padding: 16px 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
  flex-shrink: 0;
}

.storage-stats {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.storage-label {
  font-size: 11px;
  font-weight: 600;
  color: $color-text-muted;
  letter-spacing: 0.5px;
  text-transform: uppercase;
}

.storage-bar-container {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.storage-bar {
  width: 100%;
  height: 6px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 2px;
  overflow: hidden;
}

.storage-fill {
  height: 100%;
  background: $color-chocolate-gradient;
  border-radius: 2px;
}

.storage-usage {
  font-size: 11px;
  color: $color-text-muted;
}
</style>
