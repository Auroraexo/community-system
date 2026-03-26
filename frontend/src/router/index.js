import { createRouter, createWebHistory } from 'vue-router'

// 路由懒加载
const Login = () => import('../views/Login.vue')
const Register = () => import('../views/Register.vue')
const Layout = () => import('../components/Layout.vue')
const Dashboard = () => import('../views/Dashboard.vue')
const UserManage = () => import('../views/UserManage.vue')
const DeviceManage = () => import('../views/DeviceManage.vue')
const LogQuery = () => import('../views/LogQuery.vue')
const AccessRecords = () => import('../views/AccessRecords.vue')

// 路由配置
const routes = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresAuth: false, title: '登录' }
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
    meta: { requiresAuth: false, title: '注册' }
  },
  {
    path: '/',
    name: 'Layout',
    component: Layout,
    meta: { requiresAuth: true },
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: Dashboard,
        meta: { title: '仪表盘' }
      },
      {
        path: 'users',
        name: 'UserManage',
        component: UserManage,
        meta: { title: '用户管理', permission: 'user:read' }
      },
      {
        path: 'devices',
        name: 'DeviceManage',
        component: DeviceManage,
        meta: { title: '设备管理', permission: 'device:read' }
      },
      {
        path: 'logs',
        name: 'LogQuery',
        component: LogQuery,
        meta: { title: '操作日志', permission: 'log:read' }
      },
      {
        path: 'access-records',
        name: 'AccessRecords',
        component: AccessRecords,
        meta: { title: '门禁记录', permission: 'access:read' }
      }
    ]
  }
]

// 路由守卫和权限检查在文件末尾已实现

// 创建路由实例
const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  document.title = to.meta.title ? `${to.meta.title} - 小区门禁管理系统` : '小区门禁管理系统'
  
  // 检查是否需要认证
  if (to.meta.requiresAuth) {
    const token = localStorage.getItem('token')
    if (!token) {
      // 未登录，跳转到登录页
      return next({ path: '/login', query: { redirect: to.fullPath } })
    }
    
    // 检查权限
    if (to.meta.permission) {
      const userStr = localStorage.getItem('user')
      if (userStr) {
        try {
          const user = JSON.parse(userStr)
          const hasPermission = checkPermission(user, to.meta.permission)
          if (!hasPermission) {
            return next({ path: '/dashboard' })
          }
        } catch (e) {
          console.error('解析用户信息失败', e)
          localStorage.removeItem('token')
          localStorage.removeItem('user')
          return next({ path: '/login' })
        }
      }
    }
  } else if (to.path === '/login' || to.path === '/register') {
    // 如果已登录，跳转到仪表盘
    const token = localStorage.getItem('token')
    if (token) {
      return next({ path: '/dashboard' })
    }
  }
  
  next()
})

// 检查用户权限
function checkPermission(user, requiredPermission) {
  // 如果是管理员，直接返回true
  const isAdmin = user.roles && user.roles.some(role => role.name === '管理员')
  if (isAdmin) {
    return true
  }
  
  // 检查具体权限
  if (user.roles) {
    for (const role of user.roles) {
      if (role.permissions && role.permissions.some(perm => perm.name === requiredPermission)) {
        return true
      }
    }
  }
  
  return false
}

export default router