<template>
  <div class="log-query-container">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <span>操作日志</span>
        </div>
      </template>
      
      <!-- 搜索栏 -->
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="操作用户">
          <el-input v-model="searchForm.username" placeholder="请输入操作用户名" clearable></el-input>
        </el-form-item>
        <el-form-item label="操作类型">
          <el-select v-model="searchForm.action" placeholder="请选择操作类型" clearable style="width: 200px;">
            <el-option label="登录" value="login"></el-option>
            <el-option label="登出" value="logout"></el-option>
            <el-option label="创建" value="create"></el-option>
            <el-option label="更新" value="update"></el-option>
            <el-option label="删除" value="delete"></el-option>
            <el-option label="查询" value="query"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="操作对象">
          <el-select v-model="searchForm.target_type" placeholder="请选择操作对象" clearable style="width: 200px;">
            <el-option label="用户" value="user"></el-option>
            <el-option label="设备" value="device"></el-option>
            <el-option label="系统" value="system"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="操作时间">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
          ></el-date-picker>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchLogs">搜索</el-button>
          <el-button @click="resetSearch">重置</el-button>
          <el-button @click="exportLogs" type="info">导出</el-button>
        </el-form-item>
      </el-form>
      
      <!-- 日志列表 -->
      <el-table :data="logsData" style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" align="center"></el-table-column>
        <el-table-column prop="username" label="操作用户"></el-table-column>
        <el-table-column prop="action" label="操作类型" width="180" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.action === 'login'" type="success">登录</el-tag>
            <el-tag v-else-if="row.action === 'logout'" type="info">登出</el-tag>
            <el-tag v-else-if="row.action === 'create'" type="primary">创建</el-tag>
            <el-tag v-else-if="row.action === 'update'" type="warning">更新</el-tag>
            <el-tag v-else-if="row.action === 'delete'" type="danger">删除</el-tag>
            <el-tag v-else type="info">查询</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="target_type" label="操作对象" width="150" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.target_type === 'user'" type="primary">用户</el-tag>
            <el-tag v-else-if="row.target_type === 'device'" type="info">设备</el-tag>
            <el-tag v-else type="warning">系统</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="resource_id" label="对象ID" width="120" align="center"></el-table-column>
        <el-table-column prop="details" label="操作详情">
          <template #default="{ row }">
            <el-tooltip class="item" effect="dark" :content="row.details || '无详细信息'" placement="top">
              <div class="log-details">{{ row.details || '无详细信息' }}</div>
            </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column prop="ip_address" label="IP地址" width="150"></el-table-column>
        <el-table-column prop="created_at" label="操作时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
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
  </div>
</template>

<script>
import { getLogs, exportLogs as exportLogsApi } from '../api/log.js'

export default {
  name: 'LogQuery',
  data() {
    return {
      logs: [],
      logsData: [],
      loading: false,
      searchForm: {
        username: '',
        action: '',
        target_type: ''
      },
      dateRange: [],
      pagination: {
        currentPage: 1,
        pageSize: 10,
        total: 0
      }
    }
  },
  mounted() {
    this.fetchLogs()
  },
  methods: {
    async fetchLogs() {
      this.loading = true
      try {
        const params = {
          page: this.pagination.currentPage,
          page_size: this.pagination.pageSize,
          username: this.searchForm.username,
          action: this.searchForm.action,
          target_type: this.searchForm.target_type
        }
        
        // 添加日期范围
        if (this.dateRange && this.dateRange.length === 2) {
          params.start_date = this.dateRange[0]
          params.end_date = this.dateRange[1]
        }
        
        const response = await getLogs(params)
        this.logs = response.items || []
        this.pagination.total = response.total || 0
        this.logsData = this.logs
      } catch (error) {
        this.$message.error('获取日志列表失败')
        console.error(error)
      } finally {
        this.loading = false
      }
    },
    resetSearch() {
      this.searchForm = {
        username: '',
        action: '',
        target_type: ''
      }
      this.dateRange = []
      this.fetchLogs()
    },
    handleSizeChange(size) {
      this.pagination.pageSize = size
      this.fetchLogs()
    },
    handleCurrentChange(current) {
      this.pagination.currentPage = current
      this.fetchLogs()
    },
    formatDateTime(dateString) {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      })
    },
    async exportLogs() {
      try {
        const params = {
          username: this.searchForm.username,
          action: this.searchForm.action,
          target_type: this.searchForm.target_type
        }
        
        // 添加日期范围
        if (this.dateRange && this.dateRange.length === 2) {
          params.start_date = this.dateRange[0]
          params.end_date = this.dateRange[1]
        }
        
        // 创建下载链接
        const queryParams = new URLSearchParams(params).toString()
        const downloadUrl = `/api/logs/export?${queryParams}`
        
        // 创建临时链接并点击下载
        const link = document.createElement('a')
        link.href = downloadUrl
        link.download = `操作日志_${new Date().toISOString().slice(0, 10)}.xlsx`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        
        this.$message.success('导出日志成功')
      } catch (error) {
        this.$message.error('导出日志失败')
        console.error(error)
      }
    }
  }
}
</script>

<style scoped>
.log-query-container {
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

.log-details {
  max-width: 300px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>