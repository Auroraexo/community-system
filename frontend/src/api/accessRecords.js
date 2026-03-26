import request from '../utils/request'

/**
 * 获取门禁记录列表
 * @param {Object} params 查询参数
 * @param {number} params.page 页码
 * @param {number} params.page_size 每页条数
 * @param {number} params.device_id 设备ID
 * @param {number} params.user_id 用户ID
 * @param {string} params.card_id 卡号
 * @param {boolean} params.access_result 通行结果
 * @param {string} params.start_time 开始时间
 * @param {string} params.end_time 结束时间
 * @returns {Promise}
 */
export const getAccessRecords = (params) => {
  return request({
    url: '/access-records',
    method: 'get',
    params
  })
}

/**
 * 获取单个门禁记录详情
 * @param {number} recordId 记录ID
 * @returns {Promise}
 */
export const getAccessRecordDetail = (recordId) => {
  return request({
    url: `/access-records/${recordId}`,
    method: 'get'
  })
}

/**
 * 删除门禁记录
 * @param {number} recordId 记录ID
 * @returns {Promise}
 */
export const deleteAccessRecord = (recordId) => {
  return request({
    url: `/access-records/${recordId}`,
    method: 'delete'
  })
}

/**
 * 批量删除门禁记录
 * @param {Array<number>} recordIds 记录ID数组
 * @returns {Promise}
 */
export const batchDeleteAccessRecords = (recordIds) => {
  return request({
    url: '/access-records/batch-delete',
    method: 'post',
    data: recordIds
  })
}

/**
 * 导出门禁记录
 * @param {Object} params 查询参数
 * @returns {Promise}
 */
export const exportAccessRecords = async (params) => {
  // 添加默认参数以避免422错误
  const exportParams = {
    limit: 1000,
    ...params
  };
  
  const response = await request({
    url: '/access-records/export',
    method: 'get',
    params: exportParams,
    responseType: 'blob' // 指定响应类型为blob
  })
  
  // 创建下载链接
  const blob = new Blob([response], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  
  // 设置文件名
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-')
  link.download = `门禁记录_${timestamp}.xlsx`
  link.href = url
  
  // 触发下载
  document.body.appendChild(link)
  link.click()
  
  // 清理
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
  
  return response
}

/**
 * 清理旧门禁记录
 * @param {number} days 保留多少天的记录
 * @returns {Promise}
 */
export const cleanupOldAccessRecords = (days) => {
  return request({
    url: '/access-records/cleanup',
    method: 'delete',
    params: { days }
  })
}

/**
 * 获取门禁统计摘要
 * @param {Object} params 查询参数
 * @param {string} params.start_time 开始时间
 * @param {string} params.end_time 结束时间
 * @returns {Promise}
 */
export const getAccessStatsSummary = (params) => {
  return request({
    url: '/access-records/stats/summary',
    method: 'get',
    params: {
      // 添加默认值避免400错误
      ...params
    }
  })
}

/**
 * 获取设备门禁统计
 * @param {number} deviceId 设备ID
 * @param {number} days 查询天数
 * @returns {Promise}
 */
export const getDeviceAccessStats = (deviceId, days = 7) => {
  return request({
    url: `/access-records/stats/device/${deviceId}`,
    method: 'get',
    params: { days }
  })
}