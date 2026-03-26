<template>
  <div class="access-records-container">
    <el-card class="filter-card">
      <el-form :inline="true" :model="filterForm" class="filter-form">
        <el-form-item label="设备ID">
          <el-input v-model="filterForm.device_id" placeholder="请输入设备ID" clearable />
        </el-form-item>
        <el-form-item label="用户ID">
          <el-input v-model="filterForm.user_id" placeholder="请输入用户ID" clearable />
        </el-form-item>
        <el-form-item label="卡号">
          <el-input v-model="filterForm.card_id" placeholder="请输入卡号" clearable />
        </el-form-item>
        <el-form-item label="通行结果">
          <el-select v-model="filterForm.access_result" placeholder="请选择通行结果" clearable style="width: 200px;">
            <el-option label="成功" :value="true" />
            <el-option label="失败" :value="false" />
          </el-select>
        </el-form-item>
        <el-form-item label="时间范围">
          <el-date-picker
            v-model="filterForm.time_range"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD HH:mm:ss"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleQuery">查询</el-button>
          <el-button @click="resetQuery">重置</el-button>
          <!-- <el-button type="success" @click="handleExport">导出</el-button> -->
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="records-card">
      <template #header>
        <div class="card-header">
          <span>门禁记录列表</span>
          <div class="header-actions">
            <el-button type="danger" plain @click="handleBatchDelete">批量删除</el-button>
            <el-button type="warning" plain @click="handleCleanup">清理旧记录</el-button>
          </div>
        </div>
      </template>

      <el-table
        v-loading="loading"
        :data="recordsData"
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="id" label="记录ID" width="80" align="center" />
        <el-table-column prop="access_time" label="通行时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.access_time) }}
          </template>
        </el-table-column>
        <el-table-column prop="device_id" label="设备ID" width="100" align="center" />
        <el-table-column prop="device" label="设备信息" width="250">
          <template #default="{ row }">
            <div v-if="row.device">
              <div>{{ row.device.device_name || '-' }}</div>
              <div class="text-xs text-gray-500">{{ row.device.location || '-' }}</div>
            </div>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="user_id" label="用户ID" width="100" align="center" />
        <el-table-column prop="card_id" label="卡号" />
        <el-table-column prop="access_result" label="通行结果" width="100" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.access_result" type="success">成功</el-tag>
            <el-tag v-else type="danger">失败</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="reason" label="失败原因" />
        <el-table-column label="操作" width="150" align="center">
          <template #default="{ row }">
            <el-button type="text" @click="handleViewDetail(row)">查看详情</el-button>
            <el-button type="text" danger @click="handleDelete(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

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

    <!-- 详情对话框 -->
    <el-dialog
      v-model="detailVisible"
      title="门禁记录详情"
      width="500px"
    >
      <el-descriptions :column="1" border>
        <el-descriptions-item label="记录ID">{{ selectedRecord?.id }}</el-descriptions-item>
        <el-descriptions-item label="通行时间">
          {{ selectedRecord?.access_time ? formatDateTime(selectedRecord.access_time) : '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="设备信息">
          <div v-if="selectedRecord?.device">
            <div>设备编号: {{ selectedRecord.device.device_code }}</div>
            <div>设备名称: {{ selectedRecord.device.device_name || '-' }}</div>
            <div>设备位置: {{ selectedRecord.device.location || '-' }}</div>
          </div>
          <span v-else>-</span>
        </el-descriptions-item>
        <el-descriptions-item label="用户ID">{{ selectedRecord?.user_id || '-' }}</el-descriptions-item>
        <el-descriptions-item label="卡号">{{ selectedRecord?.card_id || '-' }}</el-descriptions-item>
        <el-descriptions-item label="通行结果">
          <el-tag v-if="selectedRecord?.access_result" type="success">成功</el-tag>
          <el-tag v-else type="danger">失败</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="失败原因">{{ selectedRecord?.reason || '-' }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>

    <!-- 清理旧记录对话框 -->
    <el-dialog
      v-model="cleanupVisible"
      title="清理旧记录"
      width="400px"
    >
      <div class="cleanup-content">
        <p>请选择要清理多少天之前的记录:</p>
        <el-input-number
          v-model="cleanupDays"
          :min="1"
          :max="365"
          :step="1"
          style="width: 100%"
        />
        <p class="text-gray-500">注意: 清理操作不可恢复，请谨慎操作。</p>
      </div>
      <template #footer>
        <el-button @click="cleanupVisible = false">取消</el-button>
        <el-button type="danger" @click="confirmCleanup">确认清理</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getAccessRecords, deleteAccessRecord, batchDeleteAccessRecords, exportAccessRecords, cleanupOldAccessRecords } from '../api/accessRecords'

// 加载状态
const loading = ref(false)

// 过滤表单
const filterForm = reactive({
  device_id: '',
  user_id: '',
  card_id: '',
  access_result: undefined,
  time_range: []
})

// 分页数据
const pagination = reactive({
  currentPage: 1,
  pageSize: 20,
  total: 0
})

// 记录数据
const recordsData = ref([])

// 选中的记录
const selectedRecords = ref([])

// 详情对话框
const detailVisible = ref(false)
const selectedRecord = ref(null)

// 清理对话框
const cleanupVisible = ref(false)
const cleanupDays = ref(90)

// 初始化加载数据
onMounted(() => {
  loadAccessRecords()
})

// 加载门禁记录
const loadAccessRecords = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.currentPage,
      page_size: pagination.pageSize,
      device_id: filterForm.device_id || undefined,
      user_id: filterForm.user_id || undefined,
      card_id: filterForm.card_id || undefined,
      access_result: filterForm.access_result,
      start_time: filterForm.time_range[0] || undefined,
      end_time: filterForm.time_range[1] || undefined
    }
    
    const response = await getAccessRecords(params)
    recordsData.value = response.items || []
    pagination.total = response.total || 0
  } catch (error) {
    ElMessage.error('加载门禁记录失败')
    console.error('加载门禁记录失败:', error)
  } finally {
    loading.value = false
  }
}

// 查询
const handleQuery = () => {
  pagination.currentPage = 1
  loadAccessRecords()
}

// 重置查询
const resetQuery = () => {
  Object.assign(filterForm, {
    device_id: '',
    user_id: '',
    card_id: '',
    access_result: undefined,
    time_range: []
  })
  pagination.currentPage = 1
  loadAccessRecords()
}

// 导出
// const handleExport = async () => {
//   try {
//     const params = {
//       device_id: filterForm.device_id || undefined,
//       user_id: filterForm.user_id || undefined,
//       // card_id: filterForm.card_id || undefined, // 移除 card_id 参数
//       access_result: filterForm.access_result === undefined ? null : filterForm.access_result,
//       start_time: filterForm.time_range && filterForm.time_range.length > 0 ? filterForm.time_range[0] : null,
//       end_time: filterForm.time_range && filterForm.time_range.length > 0 ? filterForm.time_range[1] : null
//     }
    
//     await exportAccessRecords(params)
//     ElMessage.success('导出成功')
//   } catch (error) {
//     ElMessage.error('导出失败')
//     console.error('导出失败:', error)
//   }
// }

// 分页大小变化
const handleSizeChange = (size) => {
  pagination.pageSize = size
  loadAccessRecords()
}

// 分页当前页变化
const handleCurrentChange = (current) => {
  pagination.currentPage = current
  loadAccessRecords()
}

// 选择记录变化
const handleSelectionChange = (selection) => {
  selectedRecords.value = selection
}

// 查看详情
const handleViewDetail = (record) => {
  selectedRecord.value = record
  detailVisible.value = true
}

// 删除单条记录
const handleDelete = async (recordId) => {
  try {
    await ElMessageBox.confirm(
      '确定要删除这条门禁记录吗？',
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await deleteAccessRecord(recordId)
    ElMessage.success('删除成功')
    loadAccessRecords()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
      console.error('删除失败:', error)
    }
  }
}

// 批量删除
const handleBatchDelete = async () => {
  if (selectedRecords.value.length === 0) {
    ElMessage.warning('请选择要删除的记录')
    return
  }
  
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedRecords.value.length} 条门禁记录吗？`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const recordIds = selectedRecords.value.map(record => record.id)
    await batchDeleteAccessRecords(recordIds)
    ElMessage.success('删除成功')
    selectedRecords.value = []
    loadAccessRecords()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
      console.error('删除失败:', error)
    }
  }
}

// 清理旧记录
const handleCleanup = () => {
  cleanupVisible.value = true
}

// 确认清理
const confirmCleanup = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要清理 ${cleanupDays.value} 天之前的门禁记录吗？`,
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'danger'
      }
    )
    
    await cleanupOldAccessRecords(cleanupDays.value)
    ElMessage.success('清理成功')
    cleanupVisible.value = false
    loadAccessRecords()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('清理失败')
      console.error('清理失败:', error)
    }
  }
}

// 格式化日期时间
const formatDateTime = (dateTime) => {
  if (!dateTime) return ''
  const date = new Date(dateTime)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}
</script>

<style scoped>
.access-records-container {
  padding: 20px;
}

.filter-card {
  margin-bottom: 20px;
}

.filter-form {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.cleanup-content {
  padding: 20px 0;
}

.cleanup-content p {
  margin-bottom: 16px;
}

.text-gray-500 {
  color: #909399;
  font-size: 14px;
}

.text-xs {
  font-size: 12px;
}
</style>