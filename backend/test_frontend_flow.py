import json
import urllib.request
import urllib.parse

def test_login():
    # 登录API
    login_url = "http://localhost:8000/api/auth/login"
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    # 发送登录请求
    req = urllib.request.Request(login_url, data=json.dumps(login_data).encode('utf-8'))
    req.add_header('Content-Type', 'application/json')
    
    try:
        with urllib.request.urlopen(req) as response:
            login_response = json.loads(response.read().decode('utf-8'))
            token = login_response.get('access_token')
            print(f"登录成功，获取到token: {token[:20]}...")
            return token
    except Exception as e:
        print(f"登录失败: {e}")
        return None

def test_users_api(token):
    # 用户列表API
    users_url = "http://localhost:8000/api/users/?page=1&page_size=10"
    
    # 发送用户列表请求
    req = urllib.request.Request(users_url)
    req.add_header('Authorization', f'Bearer {token}')
    req.add_header('Content-Type', 'application/json')
    
    try:
        with urllib.request.urlopen(req) as response:
            users_response = json.loads(response.read().decode('utf-8'))
            print("用户列表API调用成功！")
            print(f"返回数据: {json.dumps(users_response, indent=2, ensure_ascii=False)}")
            return True
    except urllib.error.HTTPError as e:
        print(f"HTTP错误: {e.code} - {e.reason}")
        try:
            error_content = json.loads(e.read().decode('utf-8'))
            print(f"错误详情: {error_content}")
        except:
            print(f"错误内容: {e.read().decode('utf-8')}")
        return False
    except Exception as e:
        print(f"请求失败: {e}")
        return False

if __name__ == "__main__":
    # 测试登录
    token = test_login()
    
    if token:
        # 测试用户列表API
        success = test_users_api(token)
        
        if success:
            print("\n✅ 用户管理功能测试通过！")
        else:
            print("\n❌ 用户管理功能测试失败！")
    else:
        print("\n❌ 登录失败，无法测试用户管理功能！")