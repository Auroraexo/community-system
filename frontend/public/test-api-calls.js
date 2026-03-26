// 测试脚本：验证前端应用是否正确调用后端API
console.log('开始测试前端API调用...');

// 测试1: 检查前端应用是否正确配置了API基础URL
function testApiBaseUrl() {
  console.log('\n=== 测试API基础URL配置 ===');
  
  // 检查Vite代理配置
  const apiBaseUrl = '/api';
  console.log('API基础URL:', apiBaseUrl);
  
  // 测试API可访问性
  fetch(`${apiBaseUrl}/health`, {
    method: 'GET'
  })
  .then(response => {
    if (response.ok) {
      console.log('✅ API基础URL配置正确');
    } else {
      console.log('⚠️ API基础URL可访问，但健康检查失败');
    }
  })
  .catch(error => {
    console.error('❌ API基础URL不可访问:', error.message);
  });
}

// 测试2: 检查认证状态
function testAuthStatus() {
  console.log('\n=== 测试认证状态 ===');
  
  const token = localStorage.getItem('token');
  const userStr = localStorage.getItem('user');
  
  console.log('Token存在:', !!token);
  console.log('用户信息存在:', !!userStr);
  
  if (token && userStr) {
    try {
      const user = JSON.parse(userStr);
      console.log('用户名:', user.username);
      console.log('用户角色:', user.roles);
      return { token, user };
    } catch (e) {
      console.error('解析用户信息失败:', e);
      return null;
    }
  }
  return null;
}

// 测试3: 测试登录API
async function testLoginApi() {
  console.log('\n=== 测试登录API ===');
  
  try {
    const response = await fetch('/api/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        username: 'admin',
        password: 'admin123'
      })
    });
    
    const data = await response.json();
    
    if (response.ok && data.access_token) {
      console.log('✅ 登录API调用成功');
      localStorage.setItem('token', data.access_token);
      localStorage.setItem('user', JSON.stringify(data.user));
      return data.access_token;
    } else {
      console.error('❌ 登录API调用失败:', data.detail || '未知错误');
      return null;
    }
  } catch (error) {
    console.error('❌ 登录API调用出错:', error.message);
    return null;
  }
}

// 测试4: 测试获取用户列表API
async function testGetUsersApi(token) {
  console.log('\n=== 测试获取用户列表API ===');
  
  try {
    const response = await fetch('/api/users/', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    const data = await response.json();
    
    if (response.ok) {
      console.log('✅ 获取用户列表API调用成功');
      console.log('用户数量:', data.total || data.items?.length || 0);
      return data;
    } else {
      console.error('❌ 获取用户列表API调用失败:', data.detail || '未知错误');
      return null;
    }
  } catch (error) {
    console.error('❌ 获取用户列表API调用出错:', error.message);
    return null;
  }
}

// 测试5: 测试添加用户API
async function testAddUserApi(token) {
  console.log('\n=== 测试添加用户API ===');
  
  const timestamp = Date.now();
  const username = `test_user_${timestamp}`;
  
  try {
    const response = await fetch('/api/users/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        username: username,
        password: 'test123456',
        email: `${username}@example.com`,
        phone: '13800138000',
        name: `测试用户_${timestamp}`,
        role_name: '住户'
      })
    });
    
    const data = await response.json();
    
    if (response.ok) {
      console.log('✅ 添加用户API调用成功，用户ID:', data.id);
      return data.id;
    } else {
      console.error('❌ 添加用户API调用失败:', data.detail || '未知错误');
      return null;
    }
  } catch (error) {
    console.error('❌ 添加用户API调用出错:', error.message);
    return null;
  }
}

// 测试6: 测试更新用户API
async function testUpdateUserApi(token, userId) {
  console.log('\n=== 测试更新用户API ===');
  
  try {
    const response = await fetch(`/api/users/${userId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        name: '更新后的测试用户',
        phone: '13900139000'
      })
    });
    
    const data = await response.json();
    
    if (response.ok) {
      console.log('✅ 更新用户API调用成功');
      return true;
    } else {
      console.error('❌ 更新用户API调用失败:', data.detail || '未知错误');
      return false;
    }
  } catch (error) {
    console.error('❌ 更新用户API调用出错:', error.message);
    return false;
  }
}

// 测试7: 测试删除用户API
async function testDeleteUserApi(token, userId) {
  console.log('\n=== 测试删除用户API ===');
  
  try {
    const response = await fetch(`/api/users/${userId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    if (response.ok) {
      console.log('✅ 删除用户API调用成功');
      return true;
    } else {
      const data = await response.json();
      console.error('❌ 删除用户API调用失败:', data.detail || '未知错误');
      return false;
    }
  } catch (error) {
    console.error('❌ 删除用户API调用出错:', error.message);
    return false;
  }
}

// 执行所有测试
async function runAllTests() {
  // 测试API基础URL配置
  testApiBaseUrl();
  
  // 测试认证状态
  let authData = testAuthStatus();
  let token = authData ? authData.token : null;
  
  // 如果没有token，先登录
  if (!token) {
    token = await testLoginApi();
    if (!token) {
      console.error('无法获取token，测试终止');
      return;
    }
  }
  
  // 测试获取用户列表
  await testGetUsersApi(token);
  
  // 测试添加用户
  const userId = await testAddUserApi(token);
  
  if (userId) {
    // 测试更新用户
    await testUpdateUserApi(token, userId);
    
    // 测试删除用户
    await testDeleteUserApi(token, userId);
  }
  
  console.log('\n=== 测试完成 ===');
}

// 自动执行测试
runAllTests();