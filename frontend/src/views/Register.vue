<template>
  <div class="register-container">
    <div class="register-form-wrapper">
      <div class="register-title">用户注册</div>
      <el-form
        ref="registerFormRef"
        :model="registerForm"
        :rules="registerRules"
        label-position="top"
        class="register-form"
      >
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="registerForm.username"
            placeholder="请输入用户名（3-50个字符）"
            prefix-icon="User"
            clearable
          />
        </el-form-item>
        
        <el-form-item label="邮箱" prop="email">
          <el-input
            v-model="registerForm.email"
            placeholder="请输入邮箱地址"
            prefix-icon="Message"
            clearable
          />
        </el-form-item>
        
        <el-form-item label="姓名" prop="name">
          <el-input
            v-model="registerForm.name"
            placeholder="请输入您的姓名"
            prefix-icon="Avatar"
            clearable
          />
        </el-form-item>
        
        <el-form-item label="手机号" prop="phone">
          <el-input
            v-model="registerForm.phone"
            placeholder="请输入手机号（选填）"
            prefix-icon="Phone"
            clearable
          />
        </el-form-item>
        
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="registerForm.password"
            type="password"
            placeholder="请输入密码（至少6个字符）"
            prefix-icon="Lock"
            show-password
          />
        </el-form-item>
        
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input
            v-model="registerForm.confirmPassword"
            type="password"
            placeholder="请再次输入密码"
            prefix-icon="Lock"
            show-password
          />
        </el-form-item>
        
        <el-form-item>
          <el-button
            type="primary"
            class="register-button"
            :loading="loading"
            @click="handleRegister"
          >
            注册
          </el-button>
          <div class="login-link">
            已有账号？<a href="/login">返回登录</a>
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
      
      <!-- 成功提示 -->
      <el-alert
        v-if="successMessage"
        :title="successMessage"
        type="success"
        show-icon
        class="success-alert"
        :closable="false"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../store/auth'
import { ElMessage } from 'element-plus'

// 路由
const router = useRouter()

// 认证状态管理
const authStore = useAuthStore()

// 表单引用
const registerFormRef = ref(null)

// 加载状态
const loading = ref(false)

// 错误信息
const error = ref('')

// 成功信息
const successMessage = ref('')

// 注册表单
const registerForm = reactive({
  username: '',
  email: '',
  name: '',
  phone: '',
  password: '',
  confirmPassword: ''
})

// 表单验证规则
const registerRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 50, message: '用户名长度在 3 到 50 个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' }
  ],
  name: [
    { required: true, message: '请输入姓名', trigger: 'blur' },
    { min: 1, max: 50, message: '姓名长度在 1 到 50 个字符', trigger: 'blur' }
  ],
  phone: [
    { pattern: /^1[3-9]\d{9}$/, message: '请输入有效的手机号码', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少为 6 个字符', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== registerForm.password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

// 处理注册
const handleRegister = async () => {
  // 表单验证
  const valid = await registerFormRef.value.validate()
  if (!valid) {
    return
  }
  
  loading.value = true
  error.value = ''
  successMessage.value = ''
  
  try {
    // 准备注册数据
    const registerData = {
      username: registerForm.username,
      email: registerForm.email,
      name: registerForm.name,
      phone: registerForm.phone || null,
      password: registerForm.password
    }
    
    // 调用注册方法
    await authStore.register(registerData)
    
    // 注册成功，显示提示
    successMessage.value = '注册成功！请登录'
    
    // 清空表单
    registerFormRef.value.resetFields()
    
    // 3秒后跳转到登录页
    setTimeout(() => {
      router.push('/login')
    }, 3000)
  } catch (err) {
    // 显示错误信息
    error.value = authStore.error || '注册失败，请重试'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.register-form-wrapper {
  width: 100%;
  max-width: 500px;
  background: white;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.register-title {
  font-size: 24px;
  font-weight: 600;
  color: #1f2937;
  text-align: center;
  margin-bottom: 30px;
}

.register-form {
  width: 100%;
}

.register-button {
  width: 100%;
  height: 44px;
  font-size: 16px;
  margin-bottom: 15px;
}

.login-link {
  text-align: center;
  font-size: 14px;
  color: #6b7280;
}

.login-link a {
  color: #4f46e5;
  text-decoration: none;
  transition: color 0.2s;
}

.login-link a:hover {
  color: #4338ca;
  text-decoration: underline;
}

.error-alert,
.success-alert {
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