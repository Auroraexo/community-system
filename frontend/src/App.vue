<template>
  <router-view v-slot="{ Component }">
    <transition name="fade" mode="out-in">
      <keep-alive>
        <component :is="Component" />
      </keep-alive>
    </transition>
  </router-view>
</template>

<script setup>
// App根组件
</script>

<style>
/* 全局样式 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background-color: #f5f7fa;
}

/* 过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 通用布局类 */
.main-container {
  display: flex;
  min-height: 100vh;
}

.content-wrapper {
  flex: 1;
  padding: 20px;
  background-color: #f5f7fa;
}

.page-container {
  background: white;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

/* 表单样式 */
.form-item {
  margin-bottom: 20px;
}

/* 表格样式 */
.table-container {
  margin-top: 20px;
}

/* 按钮组样式 */
.button-group {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}
</style>