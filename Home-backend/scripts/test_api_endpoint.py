"""
测试 API 端点是否正常工作
"""
import requests
import json

def test_api():
    base_url = "http://localhost:8002/api/v1"

    print("=" * 60)
    print("🧪 API 端点测试")
    print("=" * 60)

    # 1. 健康检查
    print("\n📌 测试 1: 健康检查")
    try:
        response = requests.get(f"{base_url.replace('/api/v1', '')}/health", timeout=5)
        if response.status_code == 200:
            print(f"✅ 后端服务运行正常")
            print(f"   响应: {response.json()}")
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ 无法连接到后端服务！")
        print(f"💡 请先启动后端: cd Home-backend && python main.py")
        return False
    except Exception as e:
        print(f"❌ 健康检查失败: {e}")
        return False

    # 2. 获取通知列表
    print(f"\n📌 测试 2: 获取用户 101 的通知列表")
    try:
        response = requests.get(f"{base_url}/notifications/?user_id=101", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API 返回成功")
            print(f"   通知数量: {len(data)}")
            if len(data) > 0:
                print(f"\n   示例数据:")
                print(f"   {json.dumps(data[0], indent=2, ensure_ascii=False)}")
            else:
                print(f"⚠️  返回空数组，数据库中可能没有数据")
        else:
            print(f"❌ API 返回错误: {response.status_code}")
            print(f"   响应: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False

    # 3. 获取未读数量
    print(f"\n📌 测试 3: 获取未读数量")
    try:
        response = requests.get(f"{base_url}/notifications/unread-count?user_id=101", timeout=5)
        if response.status_code == 200:
            count = response.json()
            print(f"✅ 未读数量: {count}")
        else:
            print(f"❌ 获取未读数量失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 请求失败: {e}")

    # 4. 测试标记已读
    print(f"\n📌 测试 4: 标记通知已读")
    if len(data) > 0:
        notif_id = data[0]['id']
        try:
            response = requests.put(
                f"{base_url}/notifications/{notif_id}/read?user_id=101",
                timeout=5
            )
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 标记已读成功")
                print(f"   is_read: {result.get('is_read')}")
            else:
                print(f"❌ 标记已读失败: {response.status_code}")
        except Exception as e:
            print(f"❌ 请求失败: {e}")

    print("\n" + "=" * 60)
    print("✅ 测试完成")
    print("=" * 60)
    print("\n💡 如果所有测试通过，现在可以在浏览器中访问前端查看数据")

if __name__ == "__main__":
    try:
        test_api()
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被中断")
