// 测试脚本：验证用户管理功能
console.log('开始测试用户管理功能...');

// 测试1: 检查localStorage中的认证状态
function checkAuthStatus() {
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

// 测试2: 登录功能
async function testLogin() {
  console.log('\n=== 测试登录功能 ===');
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
      console.log('✅ 登录成功');
      localStorage.setItem('token', data.access_token);
      localStorage.setItem('user', JSON.stringify(data.user));
      return data.access_token;
    } else {
      console.error('❌ 登录失败:', data.detail || '未知错误');
      return null;
    }
  } catch (error) {
    console.error('❌ 登录出错:', error.message);
    return null;
  }
}

// 测试3: 获取用户列表
async function testGetUsers(token) {
  console.log('\n=== 测试获取用户列表 ===');
  try {
    const response = await fetch('/api/users/', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    const data = await response.json();
    
    if (response.ok) {
      console.log('✅ 获取用户列表成功');
      console.log('用户数量:', data.total || data.items?.length || 0);
      console.log('用户列表:', data.items || data);
      return data;
    } else {
      console.error('❌ 获取用户列表失败:', data.detail || '未知错误');
      return null;
    }
  } catch (error) {
    console.error('❌ 获取用户列表出错:', error.message);
    return null;
  }
}

// 测试4: 添加用户
async function testAddUser(token) {
  console.log('\n=== 测试添加用户 ===');
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
      console.log('✅ 添加用户成功，用户ID:', data.id);
      return data.id;
    } else {
      console.error('❌ 添加用户失败:', data.detail || '未知错误');
      return null;
    }
  } catch (error) {
    console.error('❌ 添加用户出错:', error.message);
    return null;
  }
}

// 测试5: 更新用户
async function testUpdateUser(token, userId) {
  console.log('\n=== 测试更新用户 ===');
  
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
      console.log('✅ 更新用户成功');
      return true;
    } else {
      console.error('❌ 更新用户失败:', data.detail || '未知错误');
      return false;
    }
  } catch (error) {
    console.error('❌ 更新用户出错:', error.message);
    return false;
  }
}

// 测试6: 删除用户
async function testDeleteUser(token, userId) {
  console.log('\n=== 测试删除用户 ===');
  
  try {
    const response = await fetch(`/api/users/${userId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    if (response.ok) {
      console.log('✅ 删除用户成功');
      return true;
    } else {
      const data = await response.json();
      console.error('❌ 删除用户失败:', data.detail || '未知错误');
      return false;
    }
  } catch (error) {
    console.error('❌ 删除用户出错:', error.message);
    return false;
  }
}

// 执行所有测试
async function runAllTests() {
  // 检查当前认证状态
  let authData = checkAuthStatus();
  let token = authData ? authData.token : null;
  
  // 如果没有token，先登录
  if (!token) {
    token = await testLogin();
    if (!token) {
      console.error('无法获取token，测试终止');
      return;
    }
  }
  
  // 测试获取用户列表
  await testGetUsers(token);
  
  // 测试添加用户
  const userId = await testAddUser(token);
  
  if (userId) {
    // 测试更新用户
    await testUpdateUser(token, userId);
    
    // 测试删除用户
    await testDeleteUser(token, userId);
  }
  
  console.log('\n=== 测试完成 ===');
}

// 自动执行测试
runAllTests();