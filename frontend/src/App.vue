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
</script>

<style lang="scss">
#app {
  position: relative;
  width: 100%;
  height: 100%;
  background: linear-gradient(170deg, #0a0e1a 0%, #0d1225 40%, #101428 100%);
  overflow: hidden;
}
</style>
