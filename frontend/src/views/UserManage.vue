<template>
  <div class="user-manage-container">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <span>用户管理</span>
          <el-button v-if="authStore.hasRole('管理员') && authStore.hasPermission('user:create') && !isPropertyUser" type="primary" size="small" @click="showAddDialog = true">添加用户</el-button>
        </div>
      </template>
      
      <!-- 搜索栏 -->
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="用户名">
          <el-input v-model="searchForm.username" placeholder="请输入用户名" clearable style="width: 200px;"></el-input>
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="searchForm.role" placeholder="请选择角色" clearable style="width: 200px;">
            <el-option label="管理员" value="admin"></el-option>
            <el-option label="物业人员" value="property"></el-option>
            <el-option label="住户" value="resident"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchUsers">搜索</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>
      
      <!-- 用户列表 -->
      <el-table :data="usersData" style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" align="center"></el-table-column>
        <el-table-column prop="username" label="用户名"></el-table-column>
        <el-table-column prop="email" label="邮箱"></el-table-column>
        <el-table-column prop="phone" label="手机号"></el-table-column>
        <el-table-column prop="role_name" label="角色" width="120" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.role_name === '管理员'" type="success">管理员</el-tag>
            <el-tag v-else-if="row.role_name === '物业人员'" type="primary">物业人员</el-tag>
            <el-tag v-else type="info">住户</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180"></el-table-column>
        <el-table-column v-if="authStore.user.role === 'admin'" prop="is_active" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-switch
              v-model="row.is_active"
              @change="updateUserStatus(row)"
              :disabled="user.username === 'admin' || !authStore.hasRole('管理员')"
            />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" align="center">
          <template #default="{ row }">
            <el-button v-if="(authStore.hasRole('管理员') || authStore.hasRole('物业管理员')) && authStore.hasPermission('user:update')" type="primary" size="small" @click="editUser(row)" :disabled="row.username === 'admin'">编辑</el-button>
            <el-button v-if="(authStore.hasRole('管理员') || authStore.hasRole('物业管理员')) && authStore.hasPermission('user:update')" type="warning" size="small" @click="showChangePasswordDialog(row)" :disabled="row.username === 'admin'">重置密码</el-button>
            <el-button v-if="authStore.hasRole('管理员') && authStore.hasPermission('user:delete')" type="danger" size="small" @click="deleteUser(row.id)" :disabled="row.username === 'admin'">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.currentPage"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="pagination.total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
    
    <!-- 添加/编辑用户对话框 -->
    <el-dialog v-model="showAddDialog" :title="dialogTitle" width="500px">
      <el-form :model="userForm" :rules="rules" ref="userFormRef" label-width="100px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="userForm.username" placeholder="请输入用户名" :disabled="isEdit"></el-input>
        </el-form-item>
        <el-form-item label="密码" :required="!isEdit" prop="password" v-if="!isEdit">
          <el-input v-model="userForm.password" type="password" placeholder="请输入密码"></el-input>
        </el-form-item>
        <el-form-item label="确认密码" :required="!isEdit" prop="confirmPassword" v-if="!isEdit">
          <el-input v-model="userForm.confirmPassword" type="password" placeholder="请再次输入密码"></el-input>
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="userForm.email" type="email" placeholder="请输入邮箱"></el-input>
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="userForm.phone" placeholder="请输入手机号"></el-input>
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="userForm.role" placeholder="请选择角色">
            <el-option label="管理员" value="admin"></el-option>
            <el-option label="物业人员" value="property"></el-option>
            <el-option label="住户" value="resident"></el-option>
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="closeDialog">取消</el-button>
          <el-button type="primary" @click="submitForm">确定</el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 重置密码对话框 -->
    <el-dialog title="重置密码" v-model="showPasswordDialog" width="500px">
      <el-form ref="passwordFormRef" :model="passwordForm" :rules="passwordRules" label-width="100px">
        <el-form-item label="用户名">
          <el-input v-model="passwordForm.username" disabled></el-input>
        </el-form-item>
        <el-form-item label="新密码" prop="password">
          <el-input v-model="passwordForm.password" type="password" placeholder="请输入新密码"></el-input>
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input v-model="passwordForm.confirmPassword" type="password" placeholder="请确认新密码"></el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="closePasswordDialog">取消</el-button>
          <el-button type="primary" @click="submitPasswordForm">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { getUsers, addUser, updateUser, deleteUser, changePassword, resetPassword, updateUserStatus } from '@/api/user'
import { useAuthStore } from '@/store/auth' // 引入 useAuthStore

export default {
  name: 'UserManage',
  data() {
    return {
      authStore: useAuthStore(), // 获取 authStore 实例
      users: [],
      usersData: [],
      loading: false,
      searchForm: {
        username: '',
        role: ''
      },
      pagination: {
        currentPage: 1,
        pageSize: 10,
        total: 0
      },
      showAddDialog: false,
      showPasswordDialog: false,
      passwordFormRef: null,
      passwordForm: {
        id: '',
        username: '',
        password: '',
        confirmPassword: ''
      },
      passwordRules: {
        password: [
          { required: true, message: '请输入新密码', trigger: 'blur' },
          { min: 6, message: '密码长度至少6位', trigger: 'blur' }
        ],
        confirmPassword: [
          { required: true, message: '请确认新密码', trigger: 'blur' },
          { 
            validator: (rule, value, callback) => {
              if (value !== this.passwordForm.password) {
                callback(new Error('两次输入的密码不一致'))
              } else {
                callback()
              }
            }, 
            trigger: 'blur' 
          }
        ]
      },
      isEdit: false,
      dialogTitle: '添加用户',
      userForm: {
        username: '',
        password: '',
        confirmPassword: '',
        email: '',
        phone: '',
        role: 'resident'
      },
      rules: {
        username: [
          { required: true, message: '请输入用户名', trigger: 'blur' },
          { min: 3, max: 20, message: '用户名长度在 3 到 20 个字符', trigger: 'blur' }
        ],
        password: [
          { required: true, message: '请输入密码', trigger: 'blur' },
          { min: 6, message: '密码长度不能少于 6 个字符', trigger: 'blur' }
        ],
        confirmPassword: [
          { required: true, message: '请再次输入密码', trigger: 'blur' },
          {
            validator: (rule, value, callback) => {
              if (value !== this.userForm.password) {
                callback(new Error('两次输入密码不一致!'))
              } else {
                callback()
              }
            },
            trigger: 'blur'
          }
        ],
        email: [
          { required: true, message: '请输入邮箱', trigger: 'blur' },
          { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
        ],
        phone: [
          { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }
        ],
        role: [
          { required: true, message: '请选择角色', trigger: 'change' }
        ]
      },
      userFormRef: null
    }
  },
  computed: {
    isPropertyUser() {
      if (this.authStore.user && this.authStore.user.roles && this.authStore.user.roles.length > 0) {
        return this.authStore.user.roles.some(role => role.name === 'property');
      }
      return false;
    }
  },
  mounted() {
    this.fetchUsers()
  },
  methods: {
    async fetchUsers() {
      this.loading = true
      try {
        const response = await getUsers({
          page: this.pagination.currentPage,
          page_size: this.pagination.pageSize,
          username: this.searchForm.username,
          role: this.searchForm.role
        })
        
        // 处理后端返回的数据格式
        if (response.items && response.total !== undefined) {
          // FastAPI返回格式
          this.users = response.items
          this.pagination.total = response.total
        } else if (response.data && response.data.items && response.data.total !== undefined) {
          // 包装格式
          this.users = response.data.items
          this.pagination.total = response.data.total
        } else if (Array.isArray(response)) {
          // 直接返回数组
          this.users = response
          this.pagination.total = response.length
        } else {
          // 其他格式，尝试获取数据
          this.users = response.data || response.items || []
          this.pagination.total = response.total || this.users.length
        }
        
        this.usersData = this.users.map(user => {
          // 获取用户角色名称
          let roleName = user.role
          if (user.roles && Array.isArray(user.roles) && user.roles.length > 0) {
            roleName = user.roles[0].name
          }
          
          return {
            ...user,
            role_name: this.getRoleName(roleName),
            role: roleName
          }
        })
      } catch (error) {
        this.$message.error('获取用户列表失败')
        console.error(error)
      } finally {
        this.loading = false
      }
    },
    getRoleName(role) {
      const roleMap = {
        'admin': '管理员',
        'property': '物业人员',
        'resident': '住户',
        '管理员': '管理员',
        '物业人员': '物业人员',
        '住户': '住户'
      }
      return roleMap[role] || role
    },
    resetSearch() {
      this.searchForm = {
        username: '',
        role: ''
      }
      this.fetchUsers()
    },
    handleSizeChange(size) {
      this.pagination.pageSize = size
      this.fetchUsers()
    },
    handleCurrentChange(current) {
      this.pagination.currentPage = current
      this.fetchUsers()
    },
    editUser(row) {
      this.isEdit = true
      this.dialogTitle = '编辑用户'
      
      // 获取用户角色
      let userRole = 'resident'
      if (row.roles && Array.isArray(row.roles) && row.roles.length > 0) {
        const roleName = row.roles[0].name
        userRole = roleName === '管理员' ? 'admin' : 
                  roleName === '物业人员' ? 'property' : 'resident'
      } else if (row.role) {
        userRole = row.role
      }
      
      this.userForm = {
        ...row,
        password: '',
        confirmPassword: '',
        role: userRole
      }
      this.showAddDialog = true
    },
    closeDialog() {
      this.showAddDialog = false
      this.resetForm()
    },
    resetForm() {
      this.isEdit = false
      this.dialogTitle = '添加用户'
      this.userForm = {
        username: '',
        password: '',
        confirmPassword: '',
        email: '',
        phone: '',
        role: 'resident'
      }
      if (this.userFormRef) {
        this.userFormRef.resetFields()
      }
    },
    async submitForm() {
      this.$refs.userFormRef.validate(async (valid) => {
        if (valid) {
          try {
            const formData = { ...this.userForm }
            
            if (!this.isEdit) {
              // 添加用户时需要密码
              // 转换为后端期望的格式
              const userData = {
                username: formData.username,
                password: formData.password,
                email: formData.email,
                phone: formData.phone,
                name: formData.username, // 使用用户名作为姓名
                role_name: formData.role === 'admin' ? '管理员' : 
                          formData.role === 'property' ? '物业人员' : '住户'
              }
              console.log('创建用户数据:', userData)
              await addUser(userData)
              this.$message.success('添加用户成功')
            } else {
              // 编辑用户时不需要密码（除非用户修改）
              const userData = {
                email: formData.email,
                phone: formData.phone,
                name: formData.name || formData.username
              }
              
              // 如果用户修改了密码
              if (formData.password) {
                userData.password = formData.password
              }
              
              // 如果用户修改了角色
              if (formData.role) {
                userData.role_name = formData.role === 'admin' ? '管理员' : 
                                    formData.role === 'property' ? '物业人员' : '住户'
              }
              
              await updateUser(formData.id, userData)
              this.$message.success('更新用户成功')
            }
            this.closeDialog()
            this.fetchUsers()
          } catch (error) {
            this.$message.error(this.isEdit ? '更新用户失败' : '添加用户失败')
            console.error(error)
          }
        }
      })
    },
    async deleteUser(id) {
      this.$confirm('确定要删除该用户吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(async () => {
        try {
          await deleteUser(id)
          this.$message.success('删除用户成功')
          // 如果当前页只有一条数据且不是第一页，则回到上一页
          if (this.users.length === 1 && this.pagination.currentPage > 1) {
            this.pagination.currentPage--
          }
          this.fetchUsers()
        } catch (error) {
          // 处理特定错误情况
          if (error.response && error.response.status === 400) {
            this.$message.error(error.response.data.detail || '不能删除该用户')
          } else {
            this.$message.error('删除用户失败')
          }
          console.error(error)
        }
      }).catch(() => {
        // 用户取消删除
      })
    },
    showChangePasswordDialog(row) {
      this.passwordForm = {
        id: row.id,
        username: row.username,
        password: '',
        confirmPassword: ''
      }
      this.showPasswordDialog = true
    },
    closePasswordDialog() {
      this.showPasswordDialog = false
      this.passwordForm = {
        id: '',
        username: '',
        password: '',
        confirmPassword: ''
      }
      if (this.passwordFormRef) {
        this.passwordFormRef.resetFields()
      }
    },
    async submitPasswordForm() {
      this.$refs.passwordFormRef.validate(async (valid) => {
        if (valid) {
          try {
            await resetPassword(this.passwordForm.id, {
              new_password: this.passwordForm.password
            })
            this.$message.success('重置密码成功')
            this.closePasswordDialog()
          } catch (error) {
            this.$message.error('重置密码失败')
            console.error(error)
          }
        }
      })
    },
    async updateUserStatus(user) {
      try {
        await updateUserStatus(user.id, {
          is_active: user.is_active
        })
        this.$message.success('更新用户状态成功')
      } catch (error) {
        // 恢复开关状态
        user.is_active = !user.is_active
        this.$message.error('更新用户状态失败')
        console.error(error)
      }
    }
  }
}
</script>

<style scoped>
.user-manage-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-form {
  margin-bottom: 20px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>