import json
import urllib.request
import urllib.parse
import random
import string

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

def test_create_user(token):
    # 生成随机用户名
    random_username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    
    # 创建用户API
    create_user_url = "http://localhost:8000/api/users/"
    create_user_data = {
        "username": random_username,
        "password": "test123",
        "email": f"{random_username}@example.com",
        "phone": "13800138000",
        "name": f"测试用户_{random_username}",
        "role_name": "住户"
    }
    
    # 发送创建用户请求
    req = urllib.request.Request(create_user_url, data=json.dumps(create_user_data).encode('utf-8'))
    req.add_header('Authorization', f'Bearer {token}')
    req.add_header('Content-Type', 'application/json')
    
    try:
        with urllib.request.urlopen(req) as response:
            create_response = json.loads(response.read().decode('utf-8'))
            print("创建用户API调用成功！")
            print(f"创建的用户数据: {json.dumps(create_response, indent=2, ensure_ascii=False)}")
            return create_response.get('id')
    except urllib.error.HTTPError as e:
        print(f"HTTP错误: {e.code} - {e.reason}")
        try:
            error_content = json.loads(e.read().decode('utf-8'))
            print(f"错误详情: {error_content}")
        except:
            print(f"错误内容: {e.read().decode('utf-8')}")
        return None
    except Exception as e:
        print(f"请求失败: {e}")
        return None

def test_update_user(token, user_id):
    # 更新用户API
    update_user_url = f"http://localhost:8000/api/users/{user_id}"
    update_user_data = {
        "name": "更新后的测试用户",
        "phone": "13900139000"
    }
    
    # 发送更新用户请求
    req = urllib.request.Request(update_user_url, data=json.dumps(update_user_data).encode('utf-8'), method='PUT')
    req.add_header('Authorization', f'Bearer {token}')
    req.add_header('Content-Type', 'application/json')
    
    try:
        with urllib.request.urlopen(req) as response:
            update_response = json.loads(response.read().decode('utf-8'))
            print("更新用户API调用成功！")
            print(f"更新后的用户数据: {json.dumps(update_response, indent=2, ensure_ascii=False)}")
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

def test_delete_user(token, user_id):
    # 删除用户API
    delete_user_url = f"http://localhost:8000/api/users/{user_id}"
    
    # 发送删除用户请求
    req = urllib.request.Request(delete_user_url, method='DELETE')
    req.add_header('Authorization', f'Bearer {token}')
    req.add_header('Content-Type', 'application/json')
    
    try:
        with urllib.request.urlopen(req) as response:
            print("删除用户API调用成功！")
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
        # 测试创建用户
        user_id = test_create_user(token)
        
        if user_id:
            # 测试更新用户
            update_success = test_update_user(token, user_id)
            
            if update_success:
                # 测试删除用户
                delete_success = test_delete_user(token, user_id)
                
                if delete_success:
                    print("\n✅ 用户管理增删改查功能测试全部通过！")
                else:
                    print("\n❌ 删除用户功能测试失败！")
            else:
                print("\n❌ 更新用户功能测试失败！")
        else:
            print("\n❌ 创建用户功能测试失败！")
    else:
        print("\n❌ 登录失败，无法测试用户管理功能！")