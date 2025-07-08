"""
测试所有转场效果
"""

import requests
import time
import json

def test_transition_effects():
    """测试所有转场效果"""
    
    base_url = "http://localhost:5000"
    
    # 测试的转场效果
    transitions_to_test = [
        {"type": "fade", "duration": 1.0},
        {"type": "slide_left", "duration": 1.5},
        {"type": "slide_right", "duration": 1.5},
        {"type": "slide_up", "duration": 1.5},
        {"type": "slide_down", "duration": 1.5},
        {"type": "zoom_in", "duration": 2.0},
        {"type": "zoom_out", "duration": 2.0}
    ]
    
    print("🎬 开始测试转场效果")
    print("=" * 50)
    
    # 获取可用的转场效果
    try:
        response = requests.get(f"{base_url}/api/transitions")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 可用转场效果: {len(data['transitions'])} 种")
            for t in data['transitions']:
                print(f"   - {t['type']}: {t['name']}")
        else:
            print("❌ 无法获取转场效果列表")
            return
    except Exception as e:
        print(f"❌ 连接后端失败: {e}")
        return
    
    print("\n📁 检查上传的文件")
    try:
        response = requests.get(f"{base_url}/api/files")
        if response.status_code == 200:
            data = response.json()
            upload_files = data.get('upload_files', [])
            if len(upload_files) >= 2:
                print(f"✅ 找到 {len(upload_files)} 个上传文件")
                
                # 使用前几个文件进行测试
                test_files = upload_files[:min(3, len(upload_files))]
                video_files = [f"uploads/{f['filename']}" for f in test_files]
                
                print(f"📹 测试文件:")
                for i, f in enumerate(test_files):
                    print(f"   {i+1}. {f['filename']} ({f['size']} bytes)")
                
                # 测试每种转场效果
                for i, transition in enumerate(transitions_to_test):
                    print(f"\n🎭 测试转场效果 {i+1}/{len(transitions_to_test)}: {transition['type']}")
                    
                    # 创建转场配置
                    transitions_config = []
                    for j in range(len(video_files) - 1):
                        transitions_config.append(transition)
                    
                    # 发送合成请求
                    compose_data = {
                        "video_files": video_files,
                        "transitions": transitions_config,
                        "output_filename": f"test_{transition['type']}_{int(time.time())}.mp4"
                    }
                    
                    try:
                        print(f"   📤 发送合成请求...")
                        response = requests.post(
                            f"{base_url}/api/compose",
                            json=compose_data,
                            timeout=300  # 5分钟超时
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            if result.get('status') == 'success':
                                output_file = result['result']['output_filename']
                                print(f"   ✅ 合成成功: {output_file}")
                                
                                # 检查文件是否存在
                                preview_response = requests.head(f"{base_url}/api/preview/{output_file}")
                                if preview_response.status_code == 200:
                                    print(f"   ✅ 文件可访问: {base_url}/api/preview/{output_file}")
                                else:
                                    print(f"   ⚠️  文件无法访问")
                            else:
                                print(f"   ❌ 合成失败: {result.get('error', '未知错误')}")
                        else:
                            print(f"   ❌ 请求失败: HTTP {response.status_code}")
                            if response.text:
                                error_data = response.json()
                                print(f"      错误: {error_data.get('error', '未知错误')}")
                    
                    except requests.exceptions.Timeout:
                        print(f"   ⏰ 请求超时")
                    except Exception as e:
                        print(f"   ❌ 请求异常: {e}")
                    
                    # 等待一下再测试下一个
                    time.sleep(2)
                
            else:
                print(f"❌ 上传文件不足，需要至少2个文件，当前只有 {len(upload_files)} 个")
                print("请先通过前端界面上传一些测试视频文件")
        else:
            print("❌ 无法获取文件列表")
    except Exception as e:
        print(f"❌ 检查文件失败: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 转场效果测试完成")
    print("\n💡 使用建议:")
    print("1. 淡入淡出 (fade) - 最稳定，适合所有场景")
    print("2. 滑动转场 (slide_*) - 动感强，适合快节奏视频")
    print("3. 缩放转场 (zoom_*) - 视觉冲击力强，适合重点突出")
    print("4. 转场时长建议: 0.5-2.0秒，根据视频内容调整")
    print("5. 音频会自动处理淡入淡出，确保平滑过渡")

if __name__ == "__main__":
    test_transition_effects()
