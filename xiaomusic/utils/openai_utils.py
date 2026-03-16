#!/usr/bin/env python3
"""用于AI大模型调用的工具类"""

import asyncio
import json
import logging
from typing import Any

import aiohttp

log = logging.getLogger(__package__)

# 简化的音乐分析提示，专注于快速提取
MUSIC_ANALYSIS_PROMPT = """
你是一个音乐播放口令分析师，专门负责从用户指令中提取歌曲名和歌手名信息。

任务要求：
1. 识别用户指令中的歌曲名和歌手名
2. 按照JSON格式返回结果：{"name": "歌曲名", "artist": "歌手名"}
3. 如果只识别到歌曲名，返回：{"name": "歌曲名", "artist": ""}
4. 如果只识别到歌手名，返回：{"name": "", "artist": "歌手名"}
5. 如果识别出多个歌名名，返回：{"name": "", "artist": "歌手名1,歌手名2"}
6. 如果都没有识别到，返回：{}
7. 不要添加任何额外解释或文字，只返回JSON格式结果
8. 特别要注意一些歌曲名称中包含'的'字的歌，不要识别错误了。如用户指令：你的答案，应返回：{"name": "你的答案", "artist": ""}
"""


def create_openai_client(base_url: str, api_key: str) -> dict:
    """
    创建API客户端配置，返回包含base_url和api_key的字典

    Args:
        base_url: API的基础URL
        api_key: API密钥

    Returns:
        包含API配置信息的字典
    """
    return {
        "base_url": base_url,
        "api_key": api_key,
    }


# 默认使用通义千问API【阿里云百炼】: qwen-flash
async def call_openai_chat(
    client: dict,
    messages: list[dict[str, str]],
    model: str = "qwen-flash",
    temperature: float = 0.1,  # 更低的温度值以获得更一致的结果
    max_tokens: int | None = 100,  # 限制输出长度以提高速度
    timeout: int = 10,  # 减少超时时间
    extra_body: dict[str, Any] | None = None,
) -> str | None:
    """
    异步调用API聊天接口

    Args:
        client: 包含base_url和api_key的API配置字典
        messages: 消息列表，每个消息包含role和content
        model: 使用的模型名称
        temperature: 控制输出随机性的参数
        max_tokens: 最大输出token数
        timeout: 请求超时时间（秒）
        extra_body: 额外的请求体参数

    Returns:
        模型返回的内容，失败时返回None
    """
    try:
        base_url = client["base_url"]
        api_key = client["api_key"]
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        # 准备请求数据
        data = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
        }

        if max_tokens:
            data["max_tokens"] = max_tokens

        # 如果有额外参数，合并到请求数据中
        if extra_body:
            data.update(extra_body)

        # 使用aiohttp进行异步请求
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=aiohttp.ClientTimeout(total=timeout),
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    content = result["choices"][0]["message"]["content"]
                    log.debug(
                        f"API call successful, response length: {len(content) if content else 0}"
                    )
                    return content
                else:
                    log.warning(
                        f"API call failed with status {response.status}: {await response.text()}"
                    )
                    return None

    except asyncio.TimeoutError:
        log.warning(f"API call timed out after {timeout} seconds")
        return None
    except Exception as e:
        log.warning(f"Error calling API: {e}")
        return None


async def analyze_music_command(
    command: str,
    # 默认使用通义千问API【阿里云百炼】: qwen-flash
    base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1",
    api_key: str = "",
    model: str = "qwen-flash",
    temperature: float = 0.1,  # 更低的温度值以获得更一致、更快的结果
) -> dict[str, str]:
    """
    快速分析音乐播放口令，提取歌曲名和歌手名

    Args:
        command: 用户的音乐播放指令
        base_url: API的基础URL
        api_key: API密钥
        model: 使用的模型名称
        temperature: 控制输出随机性的参数（较低值保持一致性）

    Returns:
        包含歌曲名和歌手名的字典，格式为 {"name": "歌曲名", "artist": "歌手名"}
    """
    import time
    start_time = time.time()
    
    log.info(f"[AI分析] 开始调用大模型 - 指令: '{command}', 模型: {model}, API: {base_url}")
    
    try:
        headers = {
            "Authorization": f"Bearer {api_key[:10]}...{api_key[-4:]}",  # 脱敏显示
            "Content-Type": "application/json",
        }

        # 准备请求数据
        data = {
            "model": model,
            "messages": [
                {"role": "system", "content": MUSIC_ANALYSIS_PROMPT},
                {"role": "user", "content": f"用户指令：{command}"},
            ],
            "temperature": temperature,
            "max_tokens": 100,  # 限制输出长度以提高速度
        }
        
        log.info(f"[AI分析] 请求参数 - 模型: {model}, 温度: {temperature}, 最大tokens: 100")

        # 使用aiohttp进行异步请求
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=aiohttp.ClientTimeout(total=10),  # 减少超时时间
            ) as response:
                elapsed_time = time.time() - start_time
                
                if response.status == 200:
                    result = await response.json()
                    content = result["choices"][0]["message"]["content"]
                    
                    log.info(f"[AI分析] ✓ API调用成功 - 耗时: {elapsed_time:.2f}秒, 原始响应: {content}")

                    # 快速提取JSON部分
                    start = content.find("{")
                    end = content.rfind("}") + 1
                    if start != -1 and end != 0:
                        json_str = content[start:end]
                        parsed_result = json.loads(json_str)
                        final_result = {
                            "name": parsed_result.get("name", ""),
                            "artist": parsed_result.get("artist", ""),
                        }
                        log.info(f"[AI分析] ✓ 解析成功 - 歌曲: '{final_result.get('name')}', 歌手: '{final_result.get('artist')}'")
                        return final_result
                    else:
                        log.warning(f"[AI分析] ✗ JSON解析失败 - 无法从响应中提取JSON: {content}")
                else:
                    error_text = await response.text()
                    log.error(f"[AI分析] ✗ API调用失败 - 状态码: {response.status}, 耗时: {elapsed_time:.2f}秒, 错误: {error_text}")
                    
    except asyncio.TimeoutError:
        elapsed_time = time.time() - start_time
        log.error(f"[AI分析] ✗ 请求超时 - 耗时: {elapsed_time:.2f}秒")
    except json.JSONDecodeError as e:
        elapsed_time = time.time() - start_time
        log.error(f"[AI分析] ✗ JSON解析错误 - 耗时: {elapsed_time:.2f}秒, 错误: {e}")
    except Exception as e:
        elapsed_time = time.time() - start_time
        log.error(f"[AI分析] ✗ 未知错误 - 耗时: {elapsed_time:.2f}秒, 错误: {e}")

    log.info(f"[AI分析] 返回空结果")
    return {}


def format_openai_messages(conversation_history: list[str]) -> list[dict[str, str]]:
    """
    将对话历史格式化为API所需的格式

    Args:
        conversation_history: 对话历史列表，交替包含用户和助手的消息

    Returns:
        格式化后的消息列表
    """
    messages = []
    for i, msg in enumerate(conversation_history):
        role = "user" if i % 2 == 0 else "assistant"
        messages.append({"role": role, "content": msg})
    return messages


async def stream_openai_chat(
    client: dict,
    messages: list[dict[str, str]],
    model: str = "TBStars2-200B-A13B",
    temperature: float = 0.7,
) -> str | None:
    """
    流式调用API聊天接口

    Args:
        client: 包含base_url和api_key的API配置字典
        messages: 消息列表
        model: 使用的模型名称
        temperature: 控制输出随机性的参数

    Returns:
        完整的流式响应内容，失败时返回None
    """
    try:
        base_url = client["base_url"]
        api_key = client["api_key"]
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        # 准备请求数据
        data = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "stream": True,  # 启用流式响应
        }

        # 使用aiohttp进行异步请求
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{base_url}/chat/completions", headers=headers, json=data
            ) as response:
                if response.status == 200:
                    full_content = ""
                    # 逐行读取流式响应
                    async for line in response.content:
                        line_str = line.decode("utf-8").strip()

                        if line_str.startswith("data: ") and line_str != "data: [DONE]":
                            data_str = line_str[6:]  # 移除 'data: ' 前缀
                            try:
                                chunk_data = json.loads(data_str)
                                if chunk_data["choices"] and chunk_data["choices"][0][
                                    "delta"
                                ].get("content"):
                                    content_piece = chunk_data["choices"][0]["delta"][
                                        "content"
                                    ]
                                    full_content += content_piece
                                    # 可以在这里实时处理流式返回的内容
                                    print(content_piece, end="", flush=True)
                            except json.JSONDecodeError:
                                continue

                    print()  # 换行
                    return full_content
                else:
                    log.error(
                        f"Stream API call failed with status {response.status}: {await response.text()}"
                    )
                    return None

    except Exception as e:
        log.error(f"Error in stream_openai_chat: {e}")
        return None
