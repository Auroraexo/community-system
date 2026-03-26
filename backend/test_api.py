import json
import urllib.request
import urllib.parse

# 测试用户列表API
url = "http://localhost:8000/api/users"
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTc2MjMxOTY3M30.jnxp0MrMIeqx3wlvAtC58cSFZVo3FUaDTM-43F953K0"

try:
    # 创建请求对象
    req = urllib.request.Request(url)
    req.add_header('Authorization', f'Bearer {token}')
    req.add_header('Content-Type', 'application/json')
    
    # 发送请求
    with urllib.request.urlopen(req) as response:
        status_code = response.getcode()
        headers = dict(response.headers)
        content = response.read().decode('utf-8')
        
        print(f"Status Code: {status_code}")
        print(f"Response Headers: {headers}")
        print(f"Response Content: {content}")
        
        if status_code == 200:
            print("API调用成功！")
            data = json.loads(content)
            print(f"返回数据: {data}")
        else:
            print("API调用失败！")
        
except urllib.error.HTTPError as e:
    print(f"HTTP错误: {e.code} - {e.reason}")
    print(f"响应内容: {e.read().decode('utf-8')}")
except Exception as e:
    print(f"请求异常: {e}")