<template>
  <div class="register-page">
    <div class="register-card glass-card" :class="{ visible: mounted }">
      <div class="card-header">
        <div class="logo-row">
          <svg class="logo-svg" width="48" height="48" viewBox="0 0 24 24" fill="none" aria-hidden="true">
            <path d="M12 2v20M2 12h20M5.6 5.6l12.8 12.8M18.4 5.6L5.6 18.4" stroke="url(#register-logo-grad)" stroke-width="1.5" stroke-linecap="round"/>
            <circle cx="12" cy="12" r="3" fill="url(#register-logo-grad)" opacity="0.8"/>
            <defs><linearGradient id="register-logo-grad" x1="0" y1="0" x2="24" y2="24"><stop stop-color="#C49A6C"/><stop offset="1" stop-color="#8B6914"/></linearGradient></defs>
          </svg>
        </div>
        <h1 class="logo-title">YukiChocoCloud</h1>
        <p class="logo-subtitle">冬の雲に、チョコレートの温もりを</p>
      </div>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="0"
        @submit.prevent="handleRegister"
        class="register-form"
      >
        <el-form-item prop="username">
          <label for="register-username" class="sr-only">用户名</label>
          <el-input
            id="register-username"
            v-model="form.username"
            placeholder="用户名（3-64 字符）"
            size="large"
          >
            <template #prefix>
              <el-icon><User /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item prop="password">
          <label for="register-password" class="sr-only">密码</label>
          <el-input
            id="register-password"
            v-model="form.password"
            type="password"
            placeholder="密码（6-128 字符）"
            size="large"
            show-password
          >
            <template #prefix>
              <el-icon><Lock /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item prop="confirmPassword">
          <label for="register-confirm" class="sr-only">确认密码</label>
          <el-input
            id="register-confirm"
            v-model="form.confirmPassword"
            type="password"
            placeholder="确认密码"
            size="large"
            show-password
            @keyup.enter="handleRegister"
          >
            <template #prefix>
              <el-icon><Lock /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            class="register-btn"
            @click="handleRegister"
          >
            注 册
          </el-button>
        </el-form-item>
      </el-form>

      <div class="card-footer">
        <span class="footer-text">已有账号？</span>
        <router-link to="/login" class="login-link">返回登录</router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { ElMessage, type FormInstance, type FormRules } from "element-plus";
import { User, Lock } from "@element-plus/icons-vue";
import { useUserStore } from "@/stores/user";

const router = useRouter();
const userStore = useUserStore();
const formRef = ref<FormInstance>();
const loading = ref(false);
const mounted = ref(false);

const form = reactive({
  username: "",
  password: "",
  confirmPassword: "",
});

const validateConfirmPassword = (rule: any, value: string, callback: any) => {
  if (value !== form.password) {
    callback(new Error("两次输入的密码不一致"));
  } else {
    callback();
  }
};

const rules: FormRules = {
  username: [
    { required: true, message: "请输入用户名", trigger: "blur" },
    { min: 3, max: 64, message: "用户名长度为 3-64 字符", trigger: "blur" },
  ],
  password: [
    { required: true, message: "请输入密码", trigger: "blur" },
    { min: 6, max: 128, message: "密码长度为 6-128 字符", trigger: "blur" },
  ],
  confirmPassword: [
    { required: true, message: "请确认密码", trigger: "blur" },
    { validator: validateConfirmPassword, trigger: "blur" },
  ],
};

async function handleRegister() {
  const valid = await formRef.value?.validate().catch(() => false);
  if (!valid) return;

  loading.value = true;
  const success = await userStore.register(form.username, form.password);
  if (success) {
    ElMessage.success("注册成功，请登录");
    router.push("/login");
  }
  loading.value = false;
}

onMounted(() => {
  requestAnimationFrame(() => {
    mounted.value = true;
  });
});
</script>

<style scoped lang="scss">
@use "@/assets/styles/variables" as *;

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}

.register-page {
  position: relative;
  z-index: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100%;
  background: radial-gradient(ellipse at 50% 30%, rgba($color-accent, 0.06) 0%, transparent 60%);
}

.register-card {
  width: 400px;
  padding: 40px 36px 36px;
  opacity: 0;
  transform: translateY(24px);
  transition: opacity 0.6s ease, transform 0.6s ease;

  &.visible {
    opacity: 1;
    transform: translateY(0);
  }
}

.card-header {
  text-align: center;
  margin-bottom: 36px;
}

.logo-row {
  margin-bottom: 16px;
}

.logo-svg {
  display: inline-block;
  animation: float 3s ease-in-out 2;
}

.logo-title {
  font-size: 24px;
  font-weight: 700;
  margin: 0 0 8px;
  background: $color-chocolate-gradient;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.logo-subtitle {
  font-size: 12px;
  color: $color-text-muted;
  margin: 0;
  letter-spacing: 0.5px;
}

.register-form {
  :deep(.el-form-item) {
    margin-bottom: 22px;
  }

  :deep(.el-input__wrapper) {
    padding: 6px 14px !important;
  }

  :deep(.el-input__inner) {
    height: 22px !important;
  }
}

.register-btn {
  width: 100%;
  height: 42px;
  font-size: 15px;
  letter-spacing: 2px;
  margin-top: 4px;
}

.card-footer {
  text-align: center;
  margin-top: 24px;
  font-size: 13px;
  color: $color-text-muted;
}

.login-link {
  color: $color-accent;
  font-weight: 500;

  &:hover {
    color: $color-warm-glow;
  }
}
</style>
