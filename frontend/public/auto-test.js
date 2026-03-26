// 自动化测试脚本 - 完整用户管理功能测试
console.log('开始自动化用户管理功能测试...');

// 全局变量
let authToken = null;
let currentUser = null;
const API_BASE_URL = '/api';
const TEST_USER = {
    username: 'admin',
    password: 'admin123'
};

// API请求封装
async function apiRequest(url, options = {}) {
    console.log(`发起API请求: ${url}`);
    
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
        },
    };

    if (authToken) {
        defaultOptions.headers['Authorization'] = `Bearer ${authToken}`;
        console.log(`已添加认证Token: ${authToken.substring(0, 20)}...`);
    }

    const requestOptions = {
        ...defaultOptions,
        ...options,
        headers: {
            ...defaultOptions.headers,
            ...options.headers,
        },
    };

    try {
        const response = await fetch(`${API_BASE_URL}${url}`, requestOptions);
        console.log(`响应状态: ${response.status} ${response.statusText}`);
        
        // 检查认证状态
        if (response.status === 401) {
            console.error('❌ 401未授权错误!');
            console.log('尝试重新登录...');
            await testLogin();
            // 重新发起请求
            return apiRequest(url, options);
        }
        
        // 处理空响应
        if (response.status === 204) {
            console.log('✅ 请求成功 (无内容响应)');
            return {};
        }
        
        if (!response.ok) {
            console.error(`❌ 请求失败: ${response.status}`);
            try {
                const errorData = await response.json();
                console.error('错误详情:', errorData);
            } catch (e) {
                console.error('无法解析错误响应');
            }
            throw new Error(`请求失败: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('✅ 请求成功，响应数据:', JSON.stringify(data).substring(0, 200) + '...');
        return data;
    } catch (error) {
        console.error('❌ API请求错误:', error.message);
        throw error;
    }
}

// 测试登录
async function testLogin() {
    console.log('\n=== 测试登录 ===');
    try {
        const response = await apiRequest('/auth/login', {
            method: 'POST',
            body: JSON.stringify(TEST_USER)
        });
        
        authToken = response.access_token;
        currentUser = response.user;
        localStorage.setItem('access_token', authToken);
        
        console.log(`✅ 登录成功! 用户名: ${currentUser.username}`);
        console.log(`角色: ${currentUser.roles ? currentUser.roles.map(r => r.name).join(', ') : '无'}`);
        
        return true;
    } catch (error) {
        console.error('❌ 登录失败');
        return false;
    }
}

// 测试获取当前用户信息
async function testCurrentUser() {
    console.log('\n=== 测试获取当前用户信息 ===');
    try {
        const response = await apiRequest('/users/me', {
            method: 'GET'
        });
        
        currentUser = response;
        console.log(`✅ 成功获取当前用户信息: ${response.username}`);
        console.log('用户详情:', response);
        return true;
    } catch (error) {
        console.error('❌ 获取当前用户信息失败');
        return false;
    }
}

// 测试获取用户列表 - 尝试多种路径格式
async function testUserList() {
    console.log('\n=== 测试获取用户列表 ===');
    
    // 尝试不同的路径格式
    const pathsToTry = [
        '/users/?page=1&page_size=10',
        '/users?page=1&page_size=10',
        '/api/users/?page=1&page_size=10',
        '/api/users?page=1&page_size=10'
    ];
    
    for (const path of pathsToTry) {
        console.log(`\n尝试路径: ${path}`);
        try {
            // 确保使用正确的基础URL组合
            let finalPath = path;
            if (path.startsWith('/api/')) {
                finalPath = path.substring(4); // 去掉 /api/ 前缀
            }
            
            const response = await apiRequest(finalPath, {
                method: 'GET'
            });
            
            console.log(`✅ 成功获取用户列表! 总数: ${response.total}`);
            console.log(`用户数量: ${response.items ? response.items.length : 0}`);
            return true;
        } catch (error) {
            console.error(`❌ 路径 ${path} 请求失败`);
        }
    }
    
    console.error('❌ 所有路径格式都失败');
    return false;
}

// 测试创建用户
async function testCreateUser() {
    console.log('\n=== 测试创建用户 ===');
    
    const newUser = {
        username: `testuser_${Date.now()}`,
        email: `test_${Date.now()}@example.com`,
        password: 'testpass123',
        name: '测试用户',
        phone: '13800138000',
        role_name: '住户'
    };
    
    try {
        // 使用带斜杠的路径
        console.log('尝试创建用户 (路径: /users/)');
        const response = await apiRequest('/users/', {
            method: 'POST',
            body: JSON.stringify(newUser)
        });
        
        console.log(`✅ 成功创建用户! ID: ${response.id}, 用户名: ${response.username}`);
        return response;
    } catch (error) {
        console.error('❌ 创建用户失败:', error.message);
        return null;
    }
}

// 完整的测试流程
async function runFullTest() {
    console.log('\n=======================================');
    console.log('开始完整用户管理功能测试流程');
    console.log('=======================================');
    
    // 1. 登录测试
    const loginSuccess = await testLogin();
    if (!loginSuccess) {
        console.error('测试中断: 登录失败');
        return;
    }
    
    // 2. 获取当前用户信息
    const userInfoSuccess = await testCurrentUser();
    if (!userInfoSuccess) {
        console.error('测试警告: 获取用户信息失败，但继续测试');
    }
    
    // 3. 获取用户列表
    await testUserList();
    
    // 4. 创建用户测试
    await testCreateUser();
    
    console.log('\n=======================================');
    console.log('测试完成!');
    console.log('=======================================');
}

// 检查是否需要登录
function checkAuth() {
    authToken = localStorage.getItem('access_token');
    if (authToken) {
        console.log('发现已有认证Token，直接进行测试');
        runFullTest();
    } else {
        console.log('未发现认证Token，开始登录测试');
        runFullTest();
    }
}

// 主函数执行
checkAuth();

// 导出测试函数供HTML调用
window.userManagementTest = {
    runFullTest,
    testLogin,
    testCurrentUser,
    testUserList,
    testCreateUser
};