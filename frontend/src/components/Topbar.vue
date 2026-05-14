<template>
  <header class="topbar glass-card">
    <div class="topbar-left">
      <span class="logo">
        <svg class="logo-icon" width="24" height="24" viewBox="0 0 24 24" fill="none" aria-hidden="true">
          <path d="M12 2v20M2 12h20M5.6 5.6l12.8 12.8M18.4 5.6L5.6 18.4" stroke="url(#logo-grad)" stroke-width="1.5" stroke-linecap="round"/>
          <circle cx="12" cy="12" r="3" fill="url(#logo-grad)" opacity="0.8"/>
          <defs><linearGradient id="logo-grad" x1="0" y1="0" x2="24" y2="24"><stop stop-color="#C49A6C"/><stop offset="1" stop-color="#8B6914"/></linearGradient></defs>
        </svg>
        <span class="logo-text">YukiChocoCloud</span>
      </span>
    </div>

    <div class="topbar-center">
      <div class="search-box">
        <el-icon class="search-icon"><Search /></el-icon>
        <input
          type="text"
          class="search-input"
          placeholder="搜索文件...（即将推出）"
          aria-label="搜索文件"
          disabled
        />
      </div>
    </div>

    <div class="topbar-right">
      <button
        class="theme-btn"
        @click="themeStore.toggleTheme()"
        :title="themeStore.mode === 'winter' ? '切换到可可模式' : '切换到冬日模式'"
        :aria-label="themeStore.mode === 'winter' ? '切换到可可模式' : '切换到冬日模式'"
      >
        <el-icon v-if="themeStore.mode === 'winter'"><Sunny /></el-icon>
        <el-icon v-else><Moon /></el-icon>
      </button>
      <div class="user-avatar">
        <span>{{ avatarLetter }}</span>
      </div>
      <button class="logout-btn" @click="$emit('logout')" title="退出登录" aria-label="退出登录">
        <el-icon><SwitchButton /></el-icon>
      </button>
    </div>
  </header>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { Search, SwitchButton, Sunny, Moon } from "@element-plus/icons-vue";
import { useThemeStore } from "@/stores/theme";

const themeStore = useThemeStore();

const props = defineProps<{
  username: string;
}>();

defineEmits<{
  logout: [];
}>();

const avatarLetter = computed(() =>
  props.username ? props.username.charAt(0).toUpperCase() : "U"
);
</script>

<style scoped lang="scss">
@use "@/assets/styles/variables" as *;

.topbar {
  position: sticky;
  top: 0;
  z-index: $z-sticky;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: $topbar-height;
  padding: 0 24px;
  border-radius: 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.topbar-left {
  flex-shrink: 0;
}

.logo {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 700;
  user-select: none;
}

.logo-icon {
  font-size: 22px;
}

.logo-text {
  background: $color-chocolate-gradient;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.topbar-center {
  flex: 1;
  max-width: 400px;
  margin: 0 32px;
}

.search-box {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: $radius-xl;
  transition: border-color $transition-fast, box-shadow $transition-fast;

  &:focus-within {
    border-color: rgba($color-chocolate, 0.5);
    box-shadow: 0 0 0 2px rgba($color-chocolate, 0.1);
  }
}

.search-icon {
  color: $color-text-muted;
  font-size: 16px;
  flex-shrink: 0;
}

.search-input {
  flex: 1;
  background: none;
  border: none;
  outline: none;
  color: $color-text-primary;
  font-size: 14px;
  font-family: inherit;

  &::placeholder {
    color: $color-text-muted;
  }
}

.topbar-right {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-shrink: 0;
}

.user-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: $color-chocolate-gradient;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 700;
  color: white;
  cursor: default;
}

.theme-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  background: none;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: $radius-sm;
  color: $color-text-secondary;
  cursor: pointer;
  transition: color $transition-fast, border-color $transition-fast, background $transition-fast, transform $transition-fast;

  &:hover {
    color: $color-warm-glow;
    border-color: rgba($color-warm-glow, 0.3);
    background: rgba($color-warm-glow, 0.08);
    transform: rotate(15deg);
  }

  .el-icon {
    font-size: 18px;
    transition: transform 0.3s ease;
  }
}

.logout-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  background: none;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: $radius-sm;
  color: $color-text-secondary;
  cursor: pointer;
  transition: color $transition-fast, border-color $transition-fast, background $transition-fast;

  &:hover {
    color: #E85D75;
    border-color: rgba(#E85D75, 0.3);
    background: rgba(#E85D75, 0.08);
  }
}
</style>
