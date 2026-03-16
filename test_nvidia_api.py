#!/usr/bin/env python3
"""测试 NVIDIA API 连接"""

import asyncio
import aiohttp
import json

async def test_nvidia_api():
    # 你的配置
    base_url = "https://integrate.api.nvidia.com/v1"
    api_key = "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"
    model = "openai/gpt-oss-20b"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": "你是一个音乐播放助手"},
            {"role": "user", "content": "播放儿歌多多"},
        ],
        "temperature": 0.1,
        "max_tokens": 100,
    }
    
    print(f"测试配置:")
    print(f"  Base URL: {base_url}")
    print(f"  Model: {model}")
    print(f"  API Key: {api_key[:20]}...{api_key[-10:]}")
    print()
    
    try:
        async with aiohttp.ClientSession() as session:
            print("发送请求...")
            async with session.post(
                f"{base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=aiohttp.ClientTimeout(total=30),
            ) as response:
                print(f"状态码: {response.status}")
                response_text = await response.text()
                print(f"响应: {response_text}")
                
                if response.status == 200:
                    result = await response.json()
                    print(f"✓ 成功!")
                    print(f"内容: {result['choices'][0]['message']['content']}")
                else:
                    print(f"✗ 失败")
                    
    except Exception as e:
        print(f"✗ 异常: {e}")

if __name__ == "__main__":
    asyncio.run(test_nvidia_api())
