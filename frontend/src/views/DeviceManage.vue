<template>
  <div class="device-manage-container">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <span>设备管理</span>
          <el-button type="primary" size="small" @click="showAddDialog = true">添加设备</el-button>
        </div>
      </template>
      
      <!-- 搜索栏 -->
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="设备编号">
          <el-input v-model="searchForm.device_code" placeholder="请输入设备编号" clearable style="width: 200px;"></el-input>
        </el-form-item>
        <el-form-item label="设备名称">
          <el-input v-model="searchForm.name" placeholder="请输入设备名称" clearable style="width: 200px;"></el-input>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="请选择状态" clearable style="width: 200px;">
            <el-option label="在线" value="online"></el-option>
            <el-option label="离线" value="offline"></el-option>
            <el-option label="禁用" value="disabled"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchDevices">搜索</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>
      
      <!-- 设备列表 -->
      <el-table :data="devicesData" style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" align="center"></el-table-column>
        <el-table-column prop="device_code" label="设备编号"></el-table-column>
        <el-table-column prop="device_name" label="设备名称"></el-table-column>
        <el-table-column prop="type" label="设备类型" width="120" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.type === 'gate'" type="primary">门禁</el-tag>
            <el-tag v-else-if="row.type === 'camera'" type="info">摄像头</el-tag>
            <el-tag v-else type="warning">其他</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="location" label="安装位置"></el-table-column>
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.status === 'online'" type="success">在线</el-tag>
            <el-tag v-else-if="row.status === 'offline'" type="danger">离线</el-tag>
            <el-tag v-else type="warning">禁用</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180"></el-table-column>
        <el-table-column prop="updated_at" label="最后活跃时间" width="180"></el-table-column>
        <el-table-column label="操作" width="180" align="center">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="editDevice(row)">编辑</el-button>
            <el-button 
              :type="row.status === 'disabled' ? 'success' : 'warning'" 
              size="small" 
              @click="toggleStatus(row)"
            >
              {{ row.status === 'disabled' ? '启用' : '禁用' }}
            </el-button>
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
    
    <!-- 添加/编辑设备对话框 -->
    <el-dialog v-model="showAddDialog" :title="dialogTitle" width="600px">
      <el-form :model="deviceForm" :rules="rules" ref="deviceFormRef" label-width="100px">
        <el-form-item label="设备编号" prop="device_code">
          <el-input v-model="deviceForm.device_code" placeholder="请输入设备编号" :disabled="isEdit"></el-input>
        </el-form-item>
        <el-form-item label="设备名称" prop="name">
          <el-input v-model="deviceForm.name" placeholder="请输入设备名称"></el-input>
        </el-form-item>
        <el-form-item label="设备类型" prop="type">
          <el-select v-model="deviceForm.type" placeholder="请选择设备类型">
            <el-option label="门禁" value="gate"></el-option>
            <el-option label="摄像头" value="camera"></el-option>
            <el-option label="其他" value="other"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="安装位置" prop="location">
          <el-input v-model="deviceForm.location" placeholder="请输入安装位置"></el-input>
        </el-form-item>
        <el-form-item label="设备IP" prop="ip_address">
          <el-input v-model="deviceForm.ip_address" placeholder="请输入设备IP地址"></el-input>
        </el-form-item>
        <el-form-item label="设备描述">
          <el-input v-model="deviceForm.description" type="textarea" placeholder="请输入设备描述" :rows="3"></el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="closeDialog">取消</el-button>
          <el-button type="primary" @click="submitForm">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { getDevices, addDevice, updateDevice, updateDeviceStatus } from '../api/device.js'

export default {
  name: 'DeviceManage',
  data() {
    return {
      devices: [],
      devicesData: [],
      loading: false,
      searchForm: {
        device_code: '',
        name: '',
        status: ''
      },
      pagination: {
        currentPage: 1,
        pageSize: 10,
        total: 0
      },
      showAddDialog: false,
      isEdit: false,
      dialogTitle: '添加设备',
      deviceForm: {
        device_code: '',
        name: '',
        type: 'gate',
        location: '',
        ip_address: '',
        description: ''
      },
      rules: {
        device_code: [
          { required: true, message: '请输入设备编号', trigger: 'blur' },
          { min: 6, max: 32, message: '设备编号长度在 6 到 32 个字符', trigger: 'blur' }
        ],
        name: [
          { required: true, message: '请输入设备名称', trigger: 'blur' },
          { min: 2, max: 50, message: '设备名称长度在 2 到 50 个字符', trigger: 'blur' }
        ],
        type: [
          { required: true, message: '请选择设备类型', trigger: 'change' }
        ],
        location: [
          { required: true, message: '请输入安装位置', trigger: 'blur' }
        ]
      },
      deviceFormRef: null
    }
  },
  mounted() {
    this.fetchDevices()
  },
  methods: {
    async fetchDevices() {
      this.loading = true
      try {
        const response = await getDevices({
          page: this.pagination.currentPage,
          page_size: this.pagination.pageSize,
          device_code: this.searchForm.device_code,
          name: this.searchForm.name,
          status: this.searchForm.status
        })
        // 适配后端响应格式
        if (response) {
          this.devices = response.items || []
          this.pagination.total = response.total || 0
          this.devicesData = this.devices
        } else {
          throw new Error('响应格式不正确')
        }
      } catch (error) {
        this.$message.error('获取设备列表失败：' + (error.message || ''))
        console.error('获取设备列表错误:', error)
      } finally {
        this.loading = false
      }
    },
    resetSearch() {
      this.searchForm = {
        device_code: '',
        name: '',
        status: ''
      }
      this.fetchDevices()
    },
    handleSizeChange(size) {
      this.pagination.pageSize = size
      this.fetchDevices()
    },
    handleCurrentChange(current) {
      this.pagination.currentPage = current
      this.fetchDevices()
    },
    editDevice(row) {
      this.isEdit = true
      this.dialogTitle = '编辑设备'
      this.deviceForm = { ...row }
      this.showAddDialog = true
    },
    closeDialog() {
      this.showAddDialog = false
      this.resetForm()
    },
    resetForm() {
      this.isEdit = false
      this.dialogTitle = '添加设备'
      this.deviceForm = {
        device_code: '',
        name: '',
        type: 'gate',
        location: '',
        ip_address: '',
        description: ''
      }
      if (this.deviceFormRef) {
        this.deviceFormRef.resetFields()
      }
    },
    async submitForm() {
      this.$refs.deviceFormRef.validate(async (valid) => {
        if (valid) {
          try {
            if (!this.isEdit) {
              await addDevice(this.deviceForm)
              this.$message.success('添加设备成功')
            } else {
              await updateDevice(this.deviceForm.id, this.deviceForm)
              this.$message.success('更新设备成功')
            }
            this.closeDialog()
            this.fetchDevices()
          } catch (error) {
            this.$message.error(this.isEdit ? '更新设备失败' : '添加设备失败')
            console.error(error)
          }
        }
      })
    },
    async toggleStatus(row) {
      const newStatus = row.status === 'disabled' ? 'online' : 'disabled'
      const actionText = newStatus === 'disabled' ? '禁用' : '启用'
      
      this.$confirm(`确定要${actionText}该设备吗？`, '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(async () => {
        try {
          await updateDeviceStatus(row.id, newStatus)
          this.$message.success(`${actionText}设备成功`)
          this.fetchDevices()
        } catch (error) {
          this.$message.error(`${actionText}设备失败`)
          console.error(error)
        }
      }).catch(() => {
        // 用户取消操作
      })
    }
  }
}
</script>

<style scoped>
.device-manage-container {
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