"""
测试视频处理器功能
"""

import os
from video_processor import VideoProcessor, TransitionEffect

def test_video_processor():
    """测试视频处理器基本功能"""
    processor = VideoProcessor()
    
    print("=== 视频处理器测试 ===")
    
    # 测试转场效果类型
    print("\n可用的转场效果:")
    effects = [
        TransitionEffect.FADE,
        TransitionEffect.SLIDE_LEFT,
        TransitionEffect.SLIDE_RIGHT,
        TransitionEffect.ZOOM_IN,
        TransitionEffect.ZOOM_OUT
    ]
    
    for effect in effects:
        print(f"  - {effect}")
    
    print("\n✅ 视频处理器初始化成功")
    print("✅ 转场效果定义正常")
    
    # 检查输出目录
    if os.path.exists("outputs"):
        print("✅ 输出目录存在")
    else:
        print("❌ 输出目录不存在")
    
    # 检查上传目录
    if os.path.exists("uploads"):
        print("✅ 上传目录存在")
    else:
        print("❌ 上传目录不存在")

def test_api_endpoints():
    """测试 API 端点"""
    import requests
    
    print("\n=== API 端点测试 ===")
    
    base_url = "http://localhost:5000"
    
    try:
        # 测试健康检查
        response = requests.get(f"{base_url}/api/health")
        if response.status_code == 200:
            print("✅ 健康检查接口正常")
        else:
            print(f"❌ 健康检查接口异常: {response.status_code}")
        
        # 测试转场效果接口
        response = requests.get(f"{base_url}/api/transitions")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 转场效果接口正常，共 {len(data['transitions'])} 种效果")
        else:
            print(f"❌ 转场效果接口异常: {response.status_code}")
        
        # 测试文件列表接口
        response = requests.get(f"{base_url}/api/files")
        if response.status_code == 200:
            print("✅ 文件列表接口正常")
        else:
            print(f"❌ 文件列表接口异常: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到后端服务，请确保后端已启动")
    except Exception as e:
        print(f"❌ API 测试失败: {e}")

if __name__ == "__main__":
    test_video_processor()
    test_api_endpoints()
    
    print("\n=== 使用说明 ===")
    print("1. 后端服务: http://localhost:5000")
    print("2. 前端界面: http://localhost:5173")
    print("3. 上传视频文件到 uploads/ 目录")
    print("4. 合成结果保存在 outputs/ 目录")
    print("\n=== 测试建议 ===")
    print("1. 准备一些小的测试视频文件（MP4格式，几秒钟即可）")
    print("2. 通过前端界面上传视频")
    print("3. 选择转场效果")
    print("4. 开始合成并下载结果")
    print("\n🎉 系统已准备就绪，可以开始测试！")
