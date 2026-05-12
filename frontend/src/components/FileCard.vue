<template>
  <div
    class="file-card-v2"
    :class="{ selected }"
    @click="$emit('click')"
  >
    <div
      class="card-select-area"
      :class="{ visible: selected }"
      @click.stop="$emit('toggleSelect')"
    >
      <div class="checkbox-box" :class="{ checked: selected }">
        <el-icon v-if="selected" :size="12"><Check /></el-icon>
      </div>
    </div>

    <div class="card-actions-top-right">
      <button
        v-if="isPreviewable"
        class="action-glass-btn preview"
        title="预览"
        aria-label="预览文件"
        @click.stop="$emit('preview')"
      >
        <el-icon :size="16"><ZoomIn /></el-icon>
      </button>
      <button
        v-if="!file.is_dir"
        class="action-glass-btn download"
        title="下载"
        aria-label="下载文件"
        @click.stop="$emit('download')"
      >
        <el-icon :size="16"><Download /></el-icon>
      </button>
      <button
        class="action-glass-btn share"
        title="分享"
        aria-label="分享文件"
        @click.stop="$emit('share')"
      >
        <el-icon :size="16"><Share /></el-icon>
      </button>
      <button
        class="action-glass-btn delete"
        title="删除"
        aria-label="删除文件"
        @click.stop="$emit('delete')"
      >
        <el-icon :size="16"><Delete /></el-icon>
      </button>
    </div>

    <div class="card-icon-container">
      <div v-if="file.is_dir" class="icon-glass folder-glass">
        <div class="folder-icon-wrapper">
          <el-icon :size="44"><Folder /></el-icon>
        </div>
      </div>
      <div v-else-if="isImage" class="icon-glass">
        <img
          v-if="thumbUrl"
          :src="thumbUrl"
          :alt="file.name"
          class="thumbnail-img"
        />
        <div v-else class="thumbnail-loading">
          <el-icon :size="18" class="loading-icon"><Loading /></el-icon>
        </div>
      </div>
      <div v-else class="icon-glass" :class="fileTypeClass">
        <el-icon :size="36"><Document /></el-icon>
      </div>
    </div>

    <div class="card-info">
      <div class="card-name" :title="file.name">{{ file.name }}</div>
      <div class="card-date">{{ formattedDate }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted } from "vue";
import {
  Folder,
  Document,
  Download,
  Check,
  ZoomIn,
  Loading,
  Delete,
  Share,
} from "@element-plus/icons-vue";
import { filesApi, type FileInfo } from "@/api";

const props = defineProps<{
  file: FileInfo;
  selected?: boolean;
}>();

defineEmits<{
  click: [];
  download: [];
  preview: [];
  delete: [];
  share: [];
  toggleSelect: [];
}>();

const IMAGE_EXTS = /\.(jpg|jpeg|png|gif|webp|svg|bmp)$/i;
const VIDEO_EXTS = /\.(mp4|mkv|avi|mov|webm)$/i;

const isImage = computed(() => !props.file.is_dir && IMAGE_EXTS.test(props.file.name));
const isVideo = computed(() => !props.file.is_dir && VIDEO_EXTS.test(props.file.name));
const isPreviewable = computed(() => isImage.value || isVideo.value);

const thumbUrl = ref<string>();

async function loadThumb() {
  if (!isImage.value) return;
  try {
    const res = await filesApi.preview(props.file.id);
    thumbUrl.value = window.URL.createObjectURL(res.data);
  } catch {
    // thumbnail load failed, fallback to icon
  }
}

onMounted(() => loadThumb());

onUnmounted(() => {
  if (thumbUrl.value) {
    window.URL.revokeObjectURL(thumbUrl.value);
  }
});

const formattedSize = computed(() => {
  if (props.file.is_dir) return "";
  const bytes = props.file.size;
  if (bytes === 0) return "0 B";
  const units = ["B", "KB", "MB", "GB", "TB"];
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${units[i]}`;
});

const formattedDate = computed(() => {
  const d = new Date(props.file.created_at);
  return d.toLocaleDateString("zh-CN", {
    month: "short",
    day: "numeric",
  });
});

const fileTypeClass = computed(() => {
  const name = props.file.name.toLowerCase();
  if (/\.(mp4|mkv|avi|mov)$/.test(name)) return "type-video";
  if (/\.(mp3|wav|flac|ogg)$/.test(name)) return "type-audio";
  if (/\.(zip|rar|7z|tar|gz)$/.test(name)) return "type-archive";
  if (/\.(pdf)$/.test(name)) return "type-pdf";
  return "type-default";
});
</script>

<style scoped lang="scss">
@use "@/assets/styles/variables" as *;

.file-card-v2 {
  position: relative;
  display: flex;
  flex-direction: column;
  width: $file-card-width;
  height: $file-card-height;
  padding: 12px;
  cursor: pointer;
  user-select: none;
  border-radius: $file-card-radius;
  background: linear-gradient(165deg, rgba(16, 22, 42, 0.9), rgba(10, 14, 28, 0.95));
  border: 1px solid rgba(100, 160, 220, 0.06);
  transition: transform 0.35s $ease-out-expo, box-shadow 0.35s $ease-out-expo, border-color 0.35s $ease-out-expo;

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 0 20px rgba(100, 160, 220, 0.15), 0 8px 32px rgba(0, 0, 0, 0.3);
    border-color: rgba(100, 160, 220, 0.15);
    z-index: 1;

    .card-actions-top-right {
      opacity: 1;
      pointer-events: auto;
    }

    .card-icon-container .icon-glass {
      transform: scale(1.04);
    }

    .card-icon-container .icon-glass.folder-glass {
      box-shadow: 0 0 20px rgba(212, 168, 83, 0.2);
      border-color: rgba(212, 168, 83, 0.25);
    }
  }

  &:active {
    transform: translateY(0);
  }

  &.selected {
    border-color: rgba(100, 160, 220, 0.25);
    box-shadow: 0 0 24px rgba(100, 160, 220, 0.15), 0 4px 20px rgba(0, 0, 0, 0.25);
    background: linear-gradient(165deg, rgba(20, 28, 50, 0.9), rgba(14, 18, 34, 0.95));

    &::before {
      content: "";
      position: absolute;
      left: 0;
      top: 20%;
      bottom: 20%;
      width: 3px;
      border-radius: 0 3px 3px 0;
      background: $color-accent;
      animation: breathe-glow 2.5s ease-in-out infinite;
      z-index: 3; // within card context
    }

    .card-select-area {
      opacity: 1;
    }
  }
}

.card-select-area {
  position: absolute;
  top: 4px;
  left: 4px;
  padding: 6px;
  opacity: 0;
  transition: opacity 0.2s ease;
  z-index: 2;
}

.checkbox-box {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border: 1.5px solid rgba(255, 255, 255, 0.25);
  border-radius: 5px;
  background: rgba(255, 255, 255, 0.05);
  cursor: pointer;
  transition: all 0.2s ease;
  color: white;

  &:hover {
    border-color: rgba($color-accent, 0.5);
    background: rgba($color-accent, 0.1);
  }

  &.checked {
    background: $color-accent;
    border-color: $color-accent;
    box-shadow: 0 0 10px rgba($color-accent, 0.4);
  }
}

.card-actions-top-right {
  position: absolute;
  top: 8px;
  right: 8px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  opacity: 0;
  pointer-events: none;
  z-index: 4;
}

.action-glass-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: rgba(20, 24, 36, 0.7);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.12);
  color: rgba(255, 255, 255, 0.75);
  cursor: pointer;
  opacity: 0;
  transform: translateY(-4px);
  transition: opacity 0.25s $ease-out-expo 0s, transform 0.25s $ease-out-expo 0s,
              background 0.2s ease, border-color 0.2s ease, color 0.2s ease, box-shadow 0.2s ease;

  &:active {
    transform: scale(0.92) translateY(0);
  }
}

.file-card-v2:hover .action-glass-btn {
  opacity: 1;
  transform: translateY(0);

  &:nth-child(1) { transition-delay: 0ms; }
  &:nth-child(2) { transition-delay: 40ms; }
  &:nth-child(3) { transition-delay: 80ms; }

  &:hover {
    background: rgba(255, 255, 255, 0.14);
    transform: scale(1.08) translateY(0);
    color: #fff;
  }

  &:active {
    transform: scale(0.92) translateY(0);
  }

  &.delete:hover {
    background: rgba($color-danger, 0.2);
    box-shadow: 0 0 16px rgba($color-danger, 0.35);
    color: $color-danger;
    border-color: rgba($color-danger, 0.3);
  }

  &.share:hover {
    background: rgba($color-accent, 0.2);
    box-shadow: 0 0 16px rgba($color-accent, 0.35);
    color: $color-accent;
    border-color: rgba($color-accent, 0.3);
  }
}

.card-icon-container {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 8px;
}

.icon-glass {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 88px;
  height: 88px;
  border-radius: 20px;
  background: rgba(20, 24, 36, 0.5);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.06);
  transition: transform 0.35s $ease-out-expo, box-shadow 0.35s $ease-out-expo, border-color 0.35s $ease-out-expo;
  overflow: hidden;

  &.folder-glass {
    border-color: rgba(212, 168, 83, 0.15);
    box-shadow: 0 0 12px rgba(212, 168, 83, 0.1);

    .folder-icon-wrapper {
      color: $color-folder-glow;
      filter: drop-shadow(0 0 8px rgba(212, 168, 83, 0.5));
      animation: folder-float 3s ease-in-out 2;
    }
  }

  .thumbnail-img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .thumbnail-loading {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    height: 100%;
    color: $color-text-muted;
  }

  .loading-icon {
    animation: spin 1s linear infinite;
  }

  &.type-video {
    background: linear-gradient(135deg, rgba(#7EB8DA, 0.15), rgba(#5A9BC4, 0.1));
    color: #7EB8DA;
  }

  &.type-audio {
    background: linear-gradient(135deg, rgba(#A78BFA, 0.15), rgba(#8B5CF6, 0.1));
    color: #A78BFA;
  }

  &.type-archive {
    background: linear-gradient(135deg, rgba(#F59E0B, 0.15), rgba(#D97706, 0.1));
    color: #F59E0B;
  }

  &.type-pdf {
    background: linear-gradient(135deg, rgba(#EF4444, 0.15), rgba(#DC2626, 0.1));
    color: #EF4444;
  }

  &.type-default {
    background: linear-gradient(135deg, rgba($color-text-secondary, 0.12), rgba($color-text-muted, 0.08));
    color: $color-text-secondary;
  }
}

.card-info {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.card-name {
  font-size: 14px;
  font-weight: 600;
  color: $color-text-primary;
  text-align: center;
  line-height: 1.3;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  word-break: break-all;
}

.card-date {
  font-size: 12px;
  font-weight: 400;
  color: rgba(138, 148, 168, 0.55);
  margin-top: 4px;
}
</style>
