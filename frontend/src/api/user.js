import request from '../utils/request'

/**
 * 获取用户列表
 * @param {Object} params - 查询参数
 * @param {number} params.page - 页码
 * @param {number} params.page_size - 每页数量
 * @param {string} params.username - 用户名（可选）
 * @param {string} params.role - 角色（可选）
 * @returns {Promise}
 */
export const getUsers = (params) => {
  return request({
    url: '/users/',
    method: 'GET',
    params
  })
}

/**
 * 获取用户详情
 * @param {number} id - 用户ID
 * @returns {Promise}
 */
export const getUserDetail = (id) => {
  return request({
    url: `/users/${id}`,
    method: 'GET'
  })
}

/**
 * 添加用户
 * @param {Object} data - 用户数据
 * @param {string} data.username - 用户名
 * @param {string} data.password - 密码
 * @param {string} data.email - 邮箱
 * @param {string} data.phone - 手机号
 * @param {string} data.role - 角色
 * @returns {Promise}
 */
export const addUser = (data) => {
  return request({
    url: '/users/',
    method: 'POST',
    data
  })
}

/**
 * 更新用户信息
 * @param {number} id - 用户ID
 * @param {Object} data - 用户数据
 * @returns {Promise}
 */
export const updateUser = (id, data) => {
  return request({
    url: `/users/${id}`,
    method: 'PUT',
    data
  })
}

/**
 * 删除用户
 * @param {number} id - 用户ID
 * @returns {Promise}
 */
export const deleteUser = (id) => {
  return request({
    url: `/users/${id}`,
    method: 'DELETE'
  })
}

/**
 * 修改用户密码
 * @param {number} id - 用户ID
 * @param {Object} data - 密码数据
 * @param {string} data.old_password - 旧密码
 * @param {string} data.new_password - 新密码
 * @returns {Promise}
 */
export const changePassword = (id, data) => {
  return request({
    url: `/users/${id}/change-password`,
    method: 'POST',
    data
  })
}

/**
 * 重置用户密码
 * @param {number} id - 用户ID
 * @param {Object} data - 重置数据
 * @param {string} data.new_password - 新密码
 * @returns {Promise}
 */
export const resetPassword = (id, data) => {
  return request({
    url: `/users/${id}/reset-password`,
    method: 'POST',
    data
  })
}

/**
 * 更新用户状态
 * @param {number} id - 用户ID
 * @param {Object} data - 状态数据
 * @param {boolean} data.isActive - 是否激活
 * @returns {Promise}
 */
export const updateUserStatus = (id, data) => {
  return request({
    url: `/users/${id}/status`,
    method: 'PUT',
    data
  })
}