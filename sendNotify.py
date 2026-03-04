import os
import json
import requests

# 微信配置
appID = os.environ.get("APP_ID")
appSecret = os.environ.get("APP_SECRET")
openId = os.environ.get("OPEN_ID")

def get_access_token():
    """获取微信 access token"""
    if not appID or not appSecret:
        print("Error: APP_ID or APP_SECRET not set in environment variables.")
        return None
    url = f'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={appID.strip()}&secret={appSecret.strip()}'
    try:
        response = requests.get(url).json()
        access_token = response.get('access_token')
        if not access_token:
            print(f"Error fetching access token: {response}")
        return access_token
    except Exception as e:
        print(f"Exception while getting access token: {e}")
        return None

def send_template_message(template_id, data, url="https://weixin.qq.com"):
    """发送微信模板消息"""
    if not template_id:
        print("Error: template_id is empty.")
        return

    access_token = get_access_token()
    if not access_token:
        return
    
    if not openId:
        print("Error: OPEN_ID not set in environment variables.")
        return

    body = {
        "touser": openId.strip(),
        "template_id": template_id.strip(),
        "url": url,
        "data": data
    }
    
    api_url = f'https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={access_token}'
    try:
        response = requests.post(api_url, data=json.dumps(body))
        print(f"WeChat API Response: {response.text}")
    except Exception as e:
        print(f"Exception while sending template message: {e}")

def send(title, content):
    """通用通知函数，供其他模块调用"""
    print(f"Notification - Title: {title}\nContent: {content}")
    
    # 尝试使用通用的通知模板（如果用户定义了）
    # 如果没有指定，尝试使用默认模板
    general_template_id = os.environ.get("TEMPLATE_ID")
    if general_template_id:
        # 针对通用消息，我们构造一个简单的数据结构
        # 这里假设模板中包含 "message" 或 "today_note" 等字段
        # 由于不确定具体模板，这里我们构造一个较为通用的结构
        data = {
            "message": {"value": f"{title}\n{content}"},
            "today_note": {"value": content}
        }
        send_template_message(general_template_id, data)
    else:
        print("No TEMPLATE_ID found, skipping WeChat notification.")
