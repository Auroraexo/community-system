import request from '../utils/request'

/**
 * 用户登录
 * @param {Object} data - 登录数据
 * @param {string} data.username - 用户名
 * @param {string} data.password - 密码
 * @returns {Promise}
 */
export const login = (data) => {
  return request({
    url: '/auth/login',
    method: 'POST',
    data
  })
}

/**
 * 用户登出
 * @returns {Promise}
 */
export const logout = () => {
  return request({
    url: '/auth/logout',
    method: 'POST'
  })
}

/**
 * 获取当前用户信息
 * @returns {Promise}
 */
export const getCurrentUser = () => {
  return request({
    url: '/users/me',
    method: 'GET'
  })
}

/**
 * 刷新Token
 * @returns {Promise}
 */
export const refreshToken = () => {
  return request({
    url: '/auth/refresh/',
    method: 'POST'
  })
}

/**
 * 修改密码
 * @param {Object} data - 密码数据
 * @param {string} data.old_password - 旧密码
 * @param {string} data.new_password - 新密码
 * @returns {Promise}
 */
export const changePassword = (data) => {
  return request({
    url: '/auth/change-password/',
    method: 'POST',
    data
  })
}