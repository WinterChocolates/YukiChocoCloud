import { defineStore } from "pinia";
import { ref, watch } from "vue";

export type ThemeMode = "winter" | "cocoa";

export const useThemeStore = defineStore("theme", () => {
  const mode = ref<ThemeMode>(
    (localStorage.getItem("theme") as ThemeMode) || "winter"
  );

  function setTheme(newMode: ThemeMode) {
    mode.value = newMode;
    localStorage.setItem("theme", newMode);
    applyTheme(newMode);
  }

  function toggleTheme() {
    setTheme(mode.value === "winter" ? "cocoa" : "winter");
  }

  function applyTheme(theme: ThemeMode) {
    document.documentElement.setAttribute("data-theme", theme);
  }

  // 初始化时应用主题
  applyTheme(mode.value);

  return {
    mode,
    setTheme,
    toggleTheme,
  };
});
