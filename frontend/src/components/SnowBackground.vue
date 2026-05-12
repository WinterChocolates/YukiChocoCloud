<template>
  <div v-if="!prefersReducedMotion" class="snow-container" aria-hidden="true">
    <div
      v-for="flake in snowflakes"
      :key="flake.id"
      class="snowflake"
      :style="flake.style"
    />
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";

const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

const SNOW_COUNT = 60;

interface Snowflake {
  id: number;
  style: Record<string, string>;
}

function rand(min: number, max: number): number {
  return Math.random() * (max - min) + min;
}

const snowflakes = computed<Snowflake[]>(() => {
  return Array.from({ length: SNOW_COUNT }, (_, i) => {
    const size = rand(3, 8);
    const left = rand(0, 100);
    const duration = rand(8, 20);
    const delay = rand(0, 15);
    const drift = rand(-40, 40);
    const opacity = rand(0.3, 0.8);
    const blur = size < 5 ? rand(0, 1) : 0;

    return {
      id: i,
      style: {
        width: `${size}px`,
        height: `${size}px`,
        left: `${left}%`,
        "--snow-drift": `${drift}px`,
        opacity: String(opacity),
        filter: blur > 0 ? `blur(${blur}px)` : "none",
        animation: `snowfall ${duration}s linear ${delay}s infinite`,
      },
    };
  });
});
</script>

<style scoped lang="scss">
@use "@/assets/styles/variables" as *;

.snow-container {
  position: fixed;
  inset: 0;
  z-index: $z-background;
  pointer-events: none;
  overflow: hidden;
}

.snowflake {
  position: absolute;
  top: -10px;
  border-radius: 50%;
  background: radial-gradient(
    circle at 30% 30%,
    rgba(255, 255, 255, 0.95),
    rgba(232, 237, 245, 0.6)
  );
  will-change: transform;
}
</style>
