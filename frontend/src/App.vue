<template>
  <SnowBackground />
  <router-view v-slot="{ Component }">
    <Transition name="fade" mode="out-in">
      <component :is="Component" />
    </Transition>
  </router-view>
</template>

<script setup lang="ts">
import SnowBackground from "@/components/SnowBackground.vue";
import { useThemeStore } from "@/stores/theme";

// 初始化主题
useThemeStore();
</script>

<style lang="scss">
#app {
  position: relative;
  width: 100%;
  height: 100%;
  background: linear-gradient(170deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
  overflow: hidden;
  transition: background 0.5s ease;
}
</style>
