<template>
  <div class="login-container">
    <div class="login-form-wrapper">
      <div class="login-title">小区门禁管理系统</div>
      <el-form
        ref="loginFormRef"
        :model="loginForm"
        :rules="loginRules"
        label-position="top"
        class="login-form"
      >
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="请输入用户名"
            prefix-icon="User"
            clearable
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            prefix-icon="Lock"
            show-password
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        
        <el-form-item>
          <el-button
            type="primary"
            class="login-button"
            :loading="loading"
            @click="handleLogin"
          >
            登录
          </el-button>
          <div class="register-link">
            还没有账号？<a href="/register">立即注册</a>
          </div>
        </el-form-item>
      </el-form>
      
      <!-- 错误提示 -->
      <el-alert
        v-if="error"
        :title="error"
        type="error"
        show-icon
        class="error-alert"
        :closable="false"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../store/auth'
import { ElMessage } from 'element-plus'

// 路由
const router = useRouter()
const route = useRoute()

// 认证状态管理
const authStore = useAuthStore()

// 表单引用
const loginFormRef = ref(null)

// 加载状态
const loading = ref(false)

// 错误信息
const error = ref('')

// 登录表单
const loginForm = reactive({
  username: '',
  password: ''
})

// 表单验证规则
const loginRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 50, message: '用户名长度在 3 到 50 个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少为 6 个字符', trigger: 'blur' }
  ]
}

// 处理登录
const handleLogin = async () => {
  // 表单验证
  const valid = await loginFormRef.value.validate()
  if (!valid) {
    return
  }
  
  loading.value = true
  error.value = ''
  
  try {
    // 调用登录方法
    await authStore.login(loginForm.username, loginForm.password)
    
    // 登录成功，显示提示
    ElMessage.success('登录成功')
    
    // 跳转到目标页面或仪表盘
    const redirect = route.query.redirect || '/dashboard'
    router.push(redirect)
  } catch (err) {
    // 显示错误信息
    error.value = authStore.error || '登录失败，请重试'
  } finally {
    loading.value = false
  }
}

// 页面加载时检查是否已登录
onMounted(() => {
  if (authStore.authenticated) {
    router.push('/dashboard')
  }
})
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.login-form-wrapper {
  width: 100%;
  max-width: 400px;
  background: white;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.login-title {
  font-size: 24px;
  font-weight: 600;
  color: #1f2937;
  text-align: center;
  margin-bottom: 30px;
}

.login-form {
  width: 100%;
}

.login-button {
  width: 100%;
  height: 44px;
  font-size: 16px;
  margin-bottom: 15px;
}

.register-link {
  text-align: center;
  font-size: 14px;
  color: #6b7280;
}

.register-link a {
  color: #4f46e5;
  text-decoration: none;
  transition: color 0.2s;
}

.register-link a:hover {
  color: #4338ca;
  text-decoration: underline;
}

.error-alert {
  margin-bottom: 20px;
}

:deep(.el-input__wrapper) {
  border-radius: 8px;
  transition: all 0.3s;
}

:deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 2px rgba(79, 70, 229, 0.2);
}

:deep(.el-input__wrapper.is-focused) {
  box-shadow: 0 0 0 2px rgba(79, 70, 229, 0.3);
  border-color: #4f46e5;
}

:deep(.el-button--primary) {
  background-color: #4f46e5;
  border-color: #4f46e5;
}

:deep(.el-button--primary:hover) {
  background-color: #4338ca;
  border-color: #4338ca;
}

:deep(.el-button--primary.is-loading) {
  background-color: #4f46e5;
  border-color: #4f46e5;
}
</style>