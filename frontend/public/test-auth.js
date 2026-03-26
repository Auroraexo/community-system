// 测试前端认证和API调用
console.log('开始测试前端认证和API调用...');

// 检查localStorage中是否有token
const token = localStorage.getItem('token');
console.log('Token from localStorage:', token ? '存在' : '不存在');

// 检查localStorage中是否有用户信息
const userStr = localStorage.getItem('user');
console.log('User info from localStorage:', userStr ? '存在' : '不存在');

if (userStr) {
  try {
    const user = JSON.parse(userStr);
    console.log('User info:', user);
  } catch (e) {
    console.error('解析用户信息失败:', e);
  }
}

// 测试API调用
async function testAPI() {
  if (!token) {
    console.error('没有token，无法测试API');
    return;
  }
  
  try {
    console.log('测试获取用户列表API...');
    const response = await fetch('/api/users/', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    console.log('API响应状态:', response.status);
    
    if (response.ok) {
      const data = await response.json();
      console.log('API响应数据:', data);
      console.log('用户数量:', data.total || data.items?.length || 0);
    } else {
      const errorData = await response.json();
      console.error('API错误:', errorData);
    }
  } catch (error) {
    console.error('API调用出错:', error);
  }
}

// 如果有token，测试API调用
if (token) {
  testAPI();
} else {
  console.log('没有token，尝试登录...');
  
  // 尝试登录
  fetch('/api/auth/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      username: 'admin',
      password: 'admin123'
    })
  })
  .then(response => {
    if (response.ok) {
      return response.json();
    } else {
      throw new Error('登录失败');
    }
  })
  .then(data => {
    console.log('登录成功，获取到token:', data.access_token ? '是' : '否');
    
    // 保存token到localStorage
    localStorage.setItem('token', data.access_token);
    localStorage.setItem('user', JSON.stringify(data.user));
    
    // 测试API调用
    testAPI();
  })
  .catch(error => {
    console.error('登录出错:', error);
  });
}

console.log('测试脚本执行完毕');