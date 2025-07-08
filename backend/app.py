"""
Flask 主应用
提供视频合成的 REST API 接口
"""

import os
import uuid
import json
from datetime import datetime
from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
# from tasks import celery_app, compose_videos_task, get_video_info_task
from advanced_video_processor import AdvancedVideoProcessor
from logger_config import (
    setup_logging, AppLoggers, log_request_info, log_response_info,
    log_file_operation, log_video_processing, log_system_info, log_error
)

# 初始化日志系统
setup_logging('INFO')

# 创建 Flask 应用
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB 最大文件大小

# 启用 CORS
CORS(app)

# 配置目录 - 使用绝对路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
OUTPUT_FOLDER = os.path.join(BASE_DIR, 'outputs')
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'wmv', 'flv', 'webm'}

# 确保目录存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# 只在主进程中显示系统信息
if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
    log_system_info(f"上传目录: {UPLOAD_FOLDER}")
    log_system_info(f"输出目录: {OUTPUT_FOLDER}")
    log_system_info(f"最大文件大小: {app.config['MAX_CONTENT_LENGTH'] // (1024*1024)}MB")


def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    log_request_info('/api/health', 'GET')

    response_data = {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    }

    log_response_info('/api/health', 200, "系统运行正常")
    return jsonify(response_data)


@app.route('/api/transitions', methods=['GET'])
def get_available_transitions():
    """获取可用的转场效果列表"""
    log_request_info('/api/transitions', 'GET')

    transitions = [
        {'type': 'fade', 'name': '淡入淡出', 'description': '平滑的淡入淡出效果'},
        {'type': 'slide_left', 'name': '左滑', 'description': '从右向左滑动'},
        {'type': 'slide_right', 'name': '右滑', 'description': '从左向右滑动'},
        {'type': 'slide_up', 'name': '上滑', 'description': '从下向上滑动'},
        {'type': 'slide_down', 'name': '下滑', 'description': '从上向下滑动'},
        {'type': 'zoom_in', 'name': '放大', 'description': '放大转场效果'},
        {'type': 'zoom_out', 'name': '缩小', 'description': '缩小转场效果'},
    ]

    log_response_info('/api/transitions', 200, f"返回{len(transitions)}个转场效果")
    return jsonify({
        'status': 'success',
        'transitions': transitions
    })


@app.route('/api/upload', methods=['POST'])
def upload_video():
    """上传视频文件"""
    try:
        log_request_info('/api/upload', 'POST')

        if 'files' not in request.files:
            log_response_info('/api/upload', 400, "没有选择文件")
            return jsonify({'error': '没有选择文件'}), 400

        files = request.files.getlist('files')
        if not files or all(file.filename == '' for file in files):
            log_response_info('/api/upload', 400, "文件列表为空")
            return jsonify({'error': '没有选择文件'}), 400

        AppLoggers.UPLOAD.info(f"开始处理 {len(files)} 个文件")
        uploaded_files = []

        for file in files:
            if file and allowed_file(file.filename):
                # 生成安全的文件名
                original_filename = secure_filename(file.filename)
                file_extension = original_filename.rsplit('.', 1)[1].lower()
                unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
                file_path = os.path.join(UPLOAD_FOLDER, unique_filename)

                # 保存文件
                file.save(file_path)
                file_size = os.path.getsize(file_path)
                log_file_operation("上传", original_filename, True, f"大小: {file_size//1024}KB")

                # 获取视频信息
                processor = AdvancedVideoProcessor()
                video_info = processor.get_video_info(file_path)
                AppLoggers.UPLOAD.info(f"视频信息 | {original_filename} | {video_info.get('duration', 'N/A')}s | {video_info.get('width', 'N/A')}x{video_info.get('height', 'N/A')}")

                uploaded_files.append({
                    'original_name': original_filename,
                    'filename': unique_filename,
                    'path': file_path,
                    'size': file_size,
                    'info': video_info
                })
            else:
                log_file_operation("上传", file.filename, False, "不支持的文件格式")
                return jsonify({'error': f'不支持的文件格式: {file.filename}'}), 400

        log_response_info('/api/upload', 200, f"成功上传 {len(uploaded_files)} 个文件")
        return jsonify({
            'status': 'success',
            'message': f'成功上传 {len(uploaded_files)} 个文件',
            'files': uploaded_files
        })

    except Exception as e:
        log_error("上传", e, "文件上传过程中发生错误")
        return jsonify({'error': f'上传失败: {str(e)}'}), 500


@app.route('/api/compose', methods=['POST'])
def create_compose_task():
    """创建视频合成任务"""
    try:
        data = request.get_json()
        log_request_info('/api/compose', 'POST',
                        视频数量=len(data.get('video_files', [])) if data else 0,
                        转场数量=len(data.get('transitions', [])) if data else 0)

        if not data:
            log_response_info('/api/compose', 400, "请求数据为空")
            return jsonify({'error': '请求数据为空'}), 400

        video_files = data.get('video_files', [])
        transitions = data.get('transitions', [])
        output_filename = data.get('output_filename')

        if not video_files:
            log_response_info('/api/compose', 400, "没有提供视频文件")
            return jsonify({'error': '至少需要一个视频文件'}), 400

        AppLoggers.COMPOSE.info(f"开始合成任务 | 视频数量: {len(video_files)} | 转场数量: {len(transitions)}")

        # 验证文件存在
        for video_file in video_files:
            if not os.path.exists(video_file):
                log_file_operation("验证", os.path.basename(video_file), False, "文件不存在")
                return jsonify({'error': f'视频文件不存在: {video_file}'}), 400
            else:
                log_file_operation("验证", os.path.basename(video_file), True, "文件存在")

        # 使用高级视频处理器，支持复杂转场效果
        processor = AdvancedVideoProcessor()

        try:
            log_video_processing("开始合成", f"输出文件: {output_filename or '自动生成'}")
            output_path = processor.compose_videos_advanced(
                video_files=video_files,
                transitions=transitions,
                output_filename=output_filename
            )

            output_size = os.path.getsize(output_path) if os.path.exists(output_path) else 0
            log_video_processing("合成完成", f"输出文件: {os.path.basename(output_path)} | 大小: {output_size//1024}KB")
            log_response_info('/api/compose', 200, f"合成成功: {os.path.basename(output_path)}")

            return jsonify({
                'status': 'success',
                'result': {
                    'status': 'SUCCESS',
                    'output_path': output_path,
                    'output_filename': os.path.basename(output_path),
                    'message': '视频合成成功完成'
                }
            })

        except Exception as e:
            log_video_processing("合成失败", str(e), False)
            return jsonify({'error': f'视频合成失败: {str(e)}'}), 500

    except Exception as e:
        log_error("合成", e, "创建合成任务时发生错误")
        return jsonify({'error': f'创建任务失败: {str(e)}'}), 500


# 简化版本不需要任务状态查询
# @app.route('/api/task/<task_id>', methods=['GET'])
# def get_task_status(task_id):
#     """获取任务状态"""
#     # 直接返回完成状态，因为我们现在是同步处理
#     return jsonify({
#         'state': 'SUCCESS',
#         'current': 100,
#         'total': 100,
#         'status': '完成'
#     })


@app.route('/api/download/<filename>', methods=['GET'])
def download_file(filename):
    """下载合成的视频文件"""
    try:
        log_request_info('/api/download', 'GET', 文件名=filename)
        file_path = os.path.join(OUTPUT_FOLDER, filename)

        if not os.path.exists(file_path):
            log_file_operation("下载", filename, False, "文件不存在")
            log_response_info('/api/download', 404, f"文件不存在: {filename}")
            return jsonify({'error': '文件不存在'}), 404

        file_size = os.path.getsize(file_path)
        log_file_operation("下载", filename, True, f"大小: {file_size//1024}KB")
        log_response_info('/api/download', 200, f"下载文件: {filename}")

        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename,
            mimetype='video/mp4'
        )

    except Exception as e:
        log_error("下载", e, f"下载文件时发生错误: {filename}")
        return jsonify({'error': f'下载失败: {str(e)}'}), 500


@app.route('/api/preview/<filename>', methods=['GET'])
def preview_file(filename):
    """预览视频文件"""
    try:
        log_request_info('/api/preview', 'GET', 文件名=filename)

        # 首先尝试在上传目录中查找文件（原始上传的文件）
        upload_file_path = os.path.join(UPLOAD_FOLDER, filename)
        AppLoggers.PREVIEW.info(f"查找文件 | 上传目录 | {filename}")
        if os.path.exists(upload_file_path):
            file_size = os.path.getsize(upload_file_path)
            log_file_operation("预览", filename, True, f"上传目录 | 大小: {file_size//1024}KB")
            log_response_info('/api/preview', 200, f"预览文件: {filename}")
            return send_file(upload_file_path, mimetype='video/mp4')

        # 如果上传目录中没有，再尝试输出目录（合成后的文件）
        output_file_path = os.path.join(OUTPUT_FOLDER, filename)
        AppLoggers.PREVIEW.info(f"查找文件 | 输出目录 | {filename}")
        if os.path.exists(output_file_path):
            file_size = os.path.getsize(output_file_path)
            log_file_operation("预览", filename, True, f"输出目录 | 大小: {file_size//1024}KB")
            log_response_info('/api/preview', 200, f"预览文件: {filename}")
            return send_file(output_file_path, mimetype='video/mp4')

        # 列出目录内容以便调试
        upload_files = os.listdir(UPLOAD_FOLDER) if os.path.exists(UPLOAD_FOLDER) else []
        output_files = os.listdir(OUTPUT_FOLDER) if os.path.exists(OUTPUT_FOLDER) else []
        AppLoggers.PREVIEW.warning(f"文件未找到 | {filename} | 上传目录: {len(upload_files)}个文件 | 输出目录: {len(output_files)}个文件")

        # 两个目录都没有找到文件
        log_response_info('/api/preview', 404, f"文件不存在: {filename}")
        return jsonify({'error': f'文件不存在: {filename}'}), 404

    except Exception as e:
        log_error("预览", e, f"预览文件时发生错误: {filename}")
        return jsonify({'error': f'预览失败: {str(e)}'}), 500


@app.route('/api/files', methods=['GET'])
def list_files():
    """列出上传和输出的文件"""
    try:
        log_request_info('/api/files', 'GET')
        upload_files = []
        output_files = []

        # 列出上传的文件
        if os.path.exists(UPLOAD_FOLDER):
            for filename in os.listdir(UPLOAD_FOLDER):
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                if os.path.isfile(file_path):
                    upload_files.append({
                        'filename': filename,
                        'size': os.path.getsize(file_path),
                        'modified': datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
                    })

        # 列出输出的文件
        if os.path.exists(OUTPUT_FOLDER):
            for filename in os.listdir(OUTPUT_FOLDER):
                file_path = os.path.join(OUTPUT_FOLDER, filename)
                if os.path.isfile(file_path):
                    output_files.append({
                        'filename': filename,
                        'size': os.path.getsize(file_path),
                        'modified': datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
                    })

        AppLoggers.FILES.info(f"文件列表 | 上传文件: {len(upload_files)}个 | 输出文件: {len(output_files)}个")
        log_response_info('/api/files', 200, f"返回文件列表: 上传{len(upload_files)}个, 输出{len(output_files)}个")

        return jsonify({
            'status': 'success',
            'upload_files': upload_files,
            'output_files': output_files
        })

    except Exception as e:
        log_error("文件列表", e, "获取文件列表时发生错误")
        return jsonify({'error': f'获取文件列表失败: {str(e)}'}), 500


@app.errorhandler(413)
def too_large(e):
    """文件过大错误处理"""
    return jsonify({'error': '文件过大，最大支持 500MB'}), 413


@app.errorhandler(404)
def not_found(e):
    """404 错误处理"""
    return jsonify({'error': '接口不存在'}), 404


@app.errorhandler(500)
def internal_error(e):
    """500 错误处理"""
    return jsonify({'error': '服务器内部错误'}), 500


if __name__ == '__main__':
    # 只在主进程中显示启动信息
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        log_system_info("=" * 60)
        log_system_info("🎬 视频合成系统")
        log_system_info("=" * 60)

        # API接口文档
        api_endpoints = [
            ("GET", "/api/health", "健康检查"),
            ("GET", "/api/transitions", "获取转场效果列表"),
            ("POST", "/api/upload", "上传视频文件"),
            ("POST", "/api/compose", "创建合成任务"),
            ("GET", "/api/download/<filename>", "下载文件"),
            ("GET", "/api/preview/<filename>", "预览文件"),
            ("GET", "/api/files", "列出文件")
        ]

        log_system_info("📚 API接口列表:")
        for method, endpoint, description in api_endpoints:
            log_system_info(f"  {method:4} {endpoint:30} - {description}")

        log_system_info("=" * 60)
        log_system_info("🚀 服务器启动中...")
        log_system_info(f"📍 监听地址: http://0.0.0.0:5000")
        log_system_info(f"🔧 调试模式: 开启")
        log_system_info("=" * 60)

    app.run(debug=True, host='0.0.0.0', port=5000)
