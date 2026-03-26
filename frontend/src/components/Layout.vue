<template>
  <div class="main-container">
    <!-- 侧边栏 -->
    <aside class="sidebar" :class="{ 'sidebar-collapsed': isCollapsed }">
      <div class="sidebar-header">
        <div class="logo-wrapper" @click="toggleCollapse">
          <div class="logo-text" v-if="!isCollapsed">小区门禁管理系统</div>
          <el-icon v-else><HomeFilled /></el-icon>
        </div>
        <el-button
          type="text"
          class="collapse-button"
          @click="toggleCollapse"
          :title="isCollapsed ? '展开菜单' : '收起菜单'"
        >
          <el-icon><ArrowLeft v-if="!isCollapsed" /><ArrowRight v-else /></el-icon>
        </el-button>
      </div>
      <nav class="sidebar-nav">
        <el-menu
          :default-active="activeMenu"
          class="sidebar-menu"
          :collapse="isCollapsed"
          :collapse-transition="false"
          router
        >
          <el-menu-item index="/dashboard" :icon="HomeFilled">
            <template #title>仪表盘</template>
          </el-menu-item>
          
          <el-menu-item
            v-if="hasPermission('user:read')"
            index="/users"
            :icon="UserFilled"
          >
            <template #title>用户管理</template>
          </el-menu-item>
          
          <el-menu-item
            v-if="hasPermission('device:read')"
            index="/devices"
            :icon="Monitor"
          >
            <template #title>设备管理</template>
          </el-menu-item>
          <el-menu-item
            v-if="hasPermission('log:read')"
            index="/logs"
            :icon="Document"
          >
            <template #title>操作日志</template>
          </el-menu-item>
          <el-menu-item
            v-if="hasPermission('access:read')"
            index="/access-records"
            :icon="Check"
          >
            <template #title>门禁记录</template>
          </el-menu-item>
        </el-menu>
      </nav>
    </aside>
    
    <!-- 主内容区 -->
    <div class="main-content">
      <!-- 顶部导航栏 -->
      <header class="topbar">
        <div class="topbar-left">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item v-if="currentRouteMeta.title">{{ currentRouteMeta.title }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        
        <div class="topbar-right">
          <el-dropdown>
            <div class="user-info">
              <el-avatar :size="40">
                {{ user?.name?.charAt(0) || user?.username?.charAt(0) || 'U' }}
              </el-avatar>
              <span class="user-name" v-if="user">{{ user.name || user.username }}</span>
              <el-icon class="dropdown-icon"><CaretBottom /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="showUserProfile">
                  <el-icon><User /></el-icon>
                  <span>个人信息</span>
                </el-dropdown-item>
                <el-dropdown-item @click="handleLogout">
                  <el-icon><SwitchButton /></el-icon>
                  <span>退出登录</span>
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </header>
      
      <!-- 内容区域 -->
      <main class="content-wrapper">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <keep-alive>
              <component :is="Component" />
            </keep-alive>
          </transition>
        </router-view>
      </main>
    </div>
    
    <!-- 用户信息对话框 -->
    <el-dialog
      v-model="showProfileDialog"
      title="个人信息"
      width="400px"
    >
      <el-descriptions :column="1" border>
        <el-descriptions-item label="用户名">{{ user?.username }}</el-descriptions-item>
        <el-descriptions-item label="姓名">{{ user?.name }}</el-descriptions-item>
        <el-descriptions-item label="邮箱">{{ user?.email }}</el-descriptions-item>
        <el-descriptions-item label="手机号">{{ user?.phone || '-' }}</el-descriptions-item>
        <el-descriptions-item label="角色">
          <el-tag v-for="role in user?.roles" :key="role.id" size="small" class="role-tag">
            {{ role.name }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">
          {{ formatDate(user?.created_at) }}
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../store/auth'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  HomeFilled, 
  UserFilled, 
  Monitor, 
  Document, 
  Check,
  ArrowLeft, 
  ArrowRight, 
  User, 
  SwitchButton,
  CaretBottom
} from '@element-plus/icons-vue'

// 路由
const router = useRouter()
const route = useRoute()

// 认证状态管理
const authStore = useAuthStore()

// 侧边栏折叠状态
const isCollapsed = ref(false)

// 用户信息对话框
const showProfileDialog = ref(false)

// 当前活动菜单项
const activeMenu = computed(() => {
  return route.path
})

// 当前路由元信息
const currentRouteMeta = computed(() => {
  return route.meta || {}
})

// 用户信息
const user = computed(() => {
  return authStore.user
})

// 检查权限
const hasPermission = (permission) => {
  return authStore.hasPermission(permission)
}

// 切换侧边栏折叠状态
const toggleCollapse = () => {
  isCollapsed.value = !isCollapsed.value
  // 保存到localStorage
  localStorage.setItem('sidebarCollapsed', isCollapsed.value)
}

// 显示用户信息
const showUserProfile = () => {
  showProfileDialog.value = true
}

// 退出登录
const handleLogout = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要退出登录吗？',
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // 调用登出方法
    await authStore.logout()
    ElMessage.success('退出登录成功')
    router.push('/login')
  } catch (error) {
    // 用户取消操作
  }
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return ''
  
  const date = new Date(dateString)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  
  return `${year}-${month}-${day} ${hours}:${minutes}`
}

// 监听路由变化，检查认证状态
watch(route, () => {
  if (!authStore.authenticated) {
    router.push('/login')
  }
}, { immediate: true })

// 页面加载时初始化
onMounted(() => {
  // 从localStorage读取侧边栏状态
  const savedCollapsed = localStorage.getItem('sidebarCollapsed')
  if (savedCollapsed !== null) {
    isCollapsed.value = savedCollapsed === 'true'
  }
  
  // 初始化认证状态
  authStore.initAuth()
})
</script>

<style scoped>
.main-container {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

/* 侧边栏样式 */
.sidebar {
  width: 240px;
  background: #001529;
  color: #fff;
  transition: width 0.3s ease;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.sidebar.sidebar-collapsed {
  width: 64px;
}

.sidebar-header {
  padding: 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #1f2937;
}

.logo-wrapper {
  display: flex;
  align-items: center;
  cursor: pointer;
  flex: 1;
}

.logo-text {
  font-size: 18px;
  font-weight: 600;
  color: #fff;
}

.collapse-button {
  color: #fff;
  padding: 8px;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.collapse-button:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.sidebar-nav {
  flex: 1;
  overflow-y: auto;
  padding: 8px 0;
}

.sidebar-menu {
  background: transparent;
  border-right: none;
}

.sidebar-menu :deep(.el-menu-item) {
  color: rgba(255, 255, 255, 0.65);
  height: 56px;
  line-height: 56px;
  margin: 0;
  padding: 0 20px;
  transition: all 0.3s;
}

.sidebar-menu :deep(.el-menu-item:hover) {
  background-color: rgba(255, 255, 255, 0.1);
  color: #fff;
}

.sidebar-menu :deep(.el-menu-item.is-active) {
  background-color: #1890ff;
  color: #fff;
}

.sidebar-menu :deep(.el-menu-item__icon) {
  color: inherit;
}

/* 主内容区样式 */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 顶部导航栏样式 */
.topbar {
  height: 64px;
  background: #fff;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
}

.topbar-left {
  flex: 1;
}

.topbar-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 8px;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.user-info:hover {
  background-color: #f0f0f0;
}

.user-name {
  margin: 0 8px 0 12px;
  font-weight: 500;
}

.dropdown-icon {
  font-size: 12px;
}

/* 内容区域样式 */
.content-wrapper {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
  background-color: #f5f7fa;
}

/* 角色标签样式 */
.role-tag {
  margin-right: 8px;
  margin-bottom: 8px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .sidebar {
    position: fixed;
    left: 0;
    top: 0;
    height: 100vh;
    z-index: 1000;
    transform: translateX(0);
  }
  
  .sidebar.sidebar-collapsed {
    transform: translateX(-100%);
    width: 240px;
  }
  
  .main-content {
    margin-left: 0;
  }
}
</style>