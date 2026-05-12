import { createRouter, createWebHistory } from "vue-router";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/login",
      name: "Login",
      component: () => import("../views/Login.vue"),
      meta: { transition: "fade" },
    },
    {
      path: "/",
      name: "Home",
      component: () => import("../views/Home.vue"),
      meta: { requiresAuth: true, transition: "fade" },
    },
    {
      path: "/share/:token",
      name: "Share",
      component: () => import("../views/ShareView.vue"),
    },
  ],
});

router.beforeEach((to) => {
  const token = localStorage.getItem("token");
  if (to.meta.requiresAuth && !token) {
    return { name: "Login" };
  }
  if (to.name === "Login" && token) {
    return { name: "Home" };
  }
});

export default router;
