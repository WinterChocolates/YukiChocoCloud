<template>
  <div class="upload-float-wrapper">
    <input
      ref="fileInput"
      type="file"
      class="hidden-input"
      multiple
      @change="handleFileChange"
    />
    <button
      class="upload-btn"
      :class="{ expanded: showMenu }"
      @click="toggleMenu"
    >
      <el-icon class="btn-icon" :class="{ rotated: showMenu }">
        <Plus />
      </el-icon>
    </button>

    <Transition name="slide-up">
      <div v-if="showMenu" class="upload-menu glass-card-sm">
        <button class="menu-item" @click="triggerUpload">
          <el-icon><Upload /></el-icon>
          <span>上传文件</span>
        </button>
        <button class="menu-item" @click="$emit('createFolder')">
          <el-icon><FolderAdd /></el-icon>
          <span>新建文件夹</span>
        </button>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { Plus, Upload, FolderAdd } from "@element-plus/icons-vue";

const emit = defineEmits<{
  upload: [files: FileList];
  createFolder: [];
}>();

const fileInput = ref<HTMLInputElement>();
const showMenu = ref(false);

function toggleMenu() {
  showMenu.value = !showMenu.value;
}

function triggerUpload() {
  fileInput.value?.click();
  showMenu.value = false;
}

function handleFileChange(e: Event) {
  const target = e.target as HTMLInputElement;
  if (target.files && target.files.length > 0) {
    emit("upload", target.files);
  }
}

function clearInput() {
  if (fileInput.value) {
    fileInput.value.value = "";
  }
}

defineExpose({ clearInput });
</script>

<style scoped lang="scss">
@use "@/assets/styles/variables" as *;

.upload-float-wrapper {
  position: fixed;
  bottom: 32px;
  right: 32px;
  z-index: $z-float;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 12px;
}

.hidden-input {
  display: none;
}

.upload-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 56px;
  height: 56px;
  border: none;
  border-radius: 50%;
  background: $color-chocolate-gradient;
  color: white;
  cursor: pointer;
  box-shadow: $shadow-soft, $shadow-glow-chocolate;
  transition: transform $transition-normal, box-shadow $transition-normal;
  animation: float 3s ease-in-out 2;

  &:hover {
    transform: translateY(-2px) scale(1.05);
    box-shadow: $shadow-soft, 0 0 30px rgba($color-chocolate, 0.5);
  }

  &:active {
    transform: scale(0.95);
  }
}

.btn-icon {
  font-size: 24px;
  transition: transform $transition-normal;

  &.rotated {
    transform: rotate(45deg);
  }
}

.upload-menu {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 8px;
  min-width: 200px;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  background: none;
  border: none;
  border-radius: $radius-sm;
  color: $color-text-primary;
  font-size: 13px;
  font-family: inherit;
  cursor: pointer;
  transition: background $transition-fast;

  &:hover {
    background: rgba(255, 255, 255, 0.06);
  }

  .el-icon {
    font-size: 18px;
    color: $color-chocolate-light;
  }
}

.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.25s ease;
}

.slide-up-enter-from,
.slide-up-leave-to {
  opacity: 0;
  transform: translateY(8px) scale(0.95);
}
</style>
