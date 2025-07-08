"""
高级视频处理器
实现复杂的转场效果，确保音频正常
"""

import os
import uuid
import numpy as np
from typing import List, Dict, Any, Optional
from moviepy.editor import (
    VideoFileClip, CompositeVideoClip, concatenate_videoclips,
    AudioFileClip, CompositeAudioClip
)
from moviepy.video.fx.all import fadein, fadeout, resize
from moviepy.audio.fx.all import audio_fadein, audio_fadeout


class AdvancedVideoProcessor:
    """高级视频处理器，支持复杂转场效果"""
    
    def __init__(self, output_dir: str = "outputs"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def create_fade_transition(self, clip1: VideoFileClip, clip2: VideoFileClip, 
                              duration: float = 1.0) -> List[VideoFileClip]:
        """
        创建淡入淡出转场
        
        Args:
            clip1: 第一个视频片段
            clip2: 第二个视频片段
            duration: 转场持续时间
        
        Returns:
            处理后的视频片段列表
        """
        try:
            print(f"应用淡入淡出转场，持续时间: {duration}秒")
            
            # 确保转场时间不超过视频长度
            safe_duration = min(duration, clip1.duration * 0.5, clip2.duration * 0.5)
            
            # 第一个片段：在结尾添加淡出效果
            if clip1.duration > safe_duration:
                clip1_main = clip1.subclip(0, clip1.duration - safe_duration)
                clip1_fade = clip1.subclip(clip1.duration - safe_duration, clip1.duration)
                clip1_fade = fadeout(clip1_fade, safe_duration)
                
                # 处理音频淡出
                if clip1_fade.audio is not None:
                    clip1_fade = clip1_fade.set_audio(
                        audio_fadeout(clip1_fade.audio, safe_duration)
                    )
                
                clip1_processed = concatenate_videoclips([clip1_main, clip1_fade])
            else:
                clip1_processed = fadeout(clip1, safe_duration)
                if clip1_processed.audio is not None:
                    clip1_processed = clip1_processed.set_audio(
                        audio_fadeout(clip1_processed.audio, safe_duration)
                    )
            
            # 第二个片段：在开头添加淡入效果
            if clip2.duration > safe_duration:
                clip2_fade = clip2.subclip(0, safe_duration)
                clip2_fade = fadein(clip2_fade, safe_duration)
                
                # 处理音频淡入
                if clip2_fade.audio is not None:
                    clip2_fade = clip2_fade.set_audio(
                        audio_fadein(clip2_fade.audio, safe_duration)
                    )
                
                clip2_main = clip2.subclip(safe_duration, clip2.duration)
                clip2_processed = concatenate_videoclips([clip2_fade, clip2_main])
            else:
                clip2_processed = fadein(clip2, safe_duration)
                if clip2_processed.audio is not None:
                    clip2_processed = clip2_processed.set_audio(
                        audio_fadein(clip2_processed.audio, safe_duration)
                    )
            
            return [clip1_processed, clip2_processed]
            
        except Exception as e:
            print(f"淡入淡出转场失败: {e}")
            return [clip1, clip2]
    
    def create_crossfade_transition(self, clip1: VideoFileClip, clip2: VideoFileClip, 
                                   duration: float = 1.0) -> VideoFileClip:
        """
        创建交叉淡入淡出转场（重叠效果）
        
        Args:
            clip1: 第一个视频片段
            clip2: 第二个视频片段
            duration: 转场持续时间
        
        Returns:
            合成后的视频片段
        """
        try:
            print(f"应用交叉淡入淡出转场，持续时间: {duration}秒")
            
            # 确保转场时间合理
            safe_duration = min(duration, clip1.duration * 0.3, clip2.duration * 0.3)
            
            # 第一个片段的主体部分
            clip1_main = clip1.subclip(0, clip1.duration - safe_duration)
            
            # 第一个片段的结尾部分（淡出）
            clip1_end = clip1.subclip(clip1.duration - safe_duration, clip1.duration)
            clip1_end = fadeout(clip1_end, safe_duration)
            if clip1_end.audio is not None:
                clip1_end = clip1_end.set_audio(
                    audio_fadeout(clip1_end.audio, safe_duration)
                )
            
            # 第二个片段的开头部分（淡入）
            clip2_start = clip2.subclip(0, safe_duration)
            clip2_start = fadein(clip2_start, safe_duration)
            if clip2_start.audio is not None:
                clip2_start = clip2_start.set_audio(
                    audio_fadein(clip2_start.audio, safe_duration)
                )
            
            # 第二个片段的剩余部分
            clip2_main = clip2.subclip(safe_duration, clip2.duration)
            
            # 创建重叠的转场部分
            # 视频重叠
            transition_video = CompositeVideoClip([
                clip1_end,
                clip2_start
            ], size=clip1.size)
            
            # 音频混合
            if clip1_end.audio is not None and clip2_start.audio is not None:
                transition_audio = CompositeAudioClip([
                    clip1_end.audio,
                    clip2_start.audio
                ])
                transition_video = transition_video.set_audio(transition_audio)
            elif clip1_end.audio is not None:
                transition_video = transition_video.set_audio(clip1_end.audio)
            elif clip2_start.audio is not None:
                transition_video = transition_video.set_audio(clip2_start.audio)
            
            # 拼接所有部分
            parts = [clip1_main, transition_video, clip2_main]
            # 过滤掉空的部分
            parts = [part for part in parts if part.duration > 0]
            
            return concatenate_videoclips(parts)
            
        except Exception as e:
            print(f"交叉淡入淡出转场失败: {e}")
            return concatenate_videoclips([clip1, clip2])
    
    def create_slide_transition(self, clip1: VideoFileClip, clip2: VideoFileClip,
                               direction: str = "left", duration: float = 1.0) -> VideoFileClip:
        """
        创建滑动转场
        
        Args:
            clip1: 第一个视频片段
            clip2: 第二个视频片段
            direction: 滑动方向 (left, right, up, down)
            duration: 转场持续时间
        
        Returns:
            合成后的视频片段
        """
        try:
            print(f"应用滑动转场，方向: {direction}, 持续时间: {duration}秒")
            
            w, h = clip1.size
            safe_duration = min(duration, clip1.duration * 0.3, clip2.duration * 0.3)
            
            # 第一个片段的主体部分
            clip1_main = clip1.subclip(0, clip1.duration - safe_duration)
            
            # 转场部分的片段
            clip1_transition = clip1.subclip(clip1.duration - safe_duration, clip1.duration)
            clip2_transition = clip2.subclip(0, safe_duration)
            
            # 根据方向设置第二个片段的位置动画
            def position_func(t):
                progress = t / safe_duration
                if direction == "left":
                    return (w * (1 - progress), 0)
                elif direction == "right":
                    return (-w * (1 - progress), 0)
                elif direction == "up":
                    return (0, h * (1 - progress))
                elif direction == "down":
                    return (0, -h * (1 - progress))
                else:
                    return (0, 0)
            
            # 应用位置动画
            clip2_animated = clip2_transition.set_position(position_func)
            
            # 创建转场合成
            transition_composite = CompositeVideoClip([
                clip1_transition,
                clip2_animated
            ], size=(w, h))
            
            # 处理音频（简单混合）
            if clip1_transition.audio is not None and clip2_transition.audio is not None:
                # 第一个片段音频淡出，第二个片段音频淡入
                audio1 = audio_fadeout(clip1_transition.audio, safe_duration)
                audio2 = audio_fadein(clip2_transition.audio, safe_duration)
                transition_audio = CompositeAudioClip([audio1, audio2])
                transition_composite = transition_composite.set_audio(transition_audio)
            elif clip1_transition.audio is not None:
                transition_composite = transition_composite.set_audio(
                    audio_fadeout(clip1_transition.audio, safe_duration)
                )
            elif clip2_transition.audio is not None:
                transition_composite = transition_composite.set_audio(
                    audio_fadein(clip2_transition.audio, safe_duration)
                )
            
            # 第二个片段的剩余部分
            clip2_main = clip2.subclip(safe_duration, clip2.duration)
            
            # 拼接所有部分
            parts = [clip1_main, transition_composite, clip2_main]
            parts = [part for part in parts if part.duration > 0]
            
            return concatenate_videoclips(parts)
            
        except Exception as e:
            print(f"滑动转场失败: {e}")
            return concatenate_videoclips([clip1, clip2])
    
    def create_zoom_transition(self, clip1: VideoFileClip, clip2: VideoFileClip,
                              zoom_type: str = "in", duration: float = 1.0) -> VideoFileClip:
        """
        创建缩放转场
        
        Args:
            clip1: 第一个视频片段
            clip2: 第二个视频片段
            zoom_type: 缩放类型 (in, out)
            duration: 转场持续时间
        
        Returns:
            合成后的视频片段
        """
        try:
            print(f"应用缩放转场，类型: {zoom_type}, 持续时间: {duration}秒")
            
            safe_duration = min(duration, clip1.duration * 0.3, clip2.duration * 0.3)
            
            # 第一个片段的主体部分
            clip1_main = clip1.subclip(0, clip1.duration - safe_duration)
            
            # 转场部分
            clip1_transition = clip1.subclip(clip1.duration - safe_duration, clip1.duration)
            clip2_transition = clip2.subclip(0, safe_duration)
            
            if zoom_type == "in":
                # 第一个片段放大淡出
                def resize_func1(t):
                    progress = t / safe_duration
                    return 1 + 0.5 * progress
                
                clip1_zoomed = clip1_transition.resize(resize_func1)
                clip1_zoomed = fadeout(clip1_zoomed, safe_duration)
                
                # 第二个片段从小放大淡入
                def resize_func2(t):
                    progress = t / safe_duration
                    return 0.5 + 0.5 * progress
                
                clip2_zoomed = clip2_transition.resize(resize_func2)
                clip2_zoomed = fadein(clip2_zoomed, safe_duration)
            else:  # zoom_out
                # 第一个片段缩小淡出
                def resize_func1(t):
                    progress = t / safe_duration
                    return 1 - 0.5 * progress
                
                clip1_zoomed = clip1_transition.resize(resize_func1)
                clip1_zoomed = fadeout(clip1_zoomed, safe_duration)
                
                # 第二个片段从大缩小淡入
                def resize_func2(t):
                    progress = t / safe_duration
                    return 1.5 - 0.5 * progress
                
                clip2_zoomed = clip2_transition.resize(resize_func2)
                clip2_zoomed = fadein(clip2_zoomed, safe_duration)
            
            # 创建转场合成
            transition_composite = CompositeVideoClip([
                clip1_zoomed,
                clip2_zoomed
            ], size=clip1.size)
            
            # 处理音频
            if clip1_transition.audio is not None and clip2_transition.audio is not None:
                audio1 = audio_fadeout(clip1_transition.audio, safe_duration)
                audio2 = audio_fadein(clip2_transition.audio, safe_duration)
                transition_audio = CompositeAudioClip([audio1, audio2])
                transition_composite = transition_composite.set_audio(transition_audio)
            elif clip1_transition.audio is not None:
                transition_composite = transition_composite.set_audio(
                    audio_fadeout(clip1_transition.audio, safe_duration)
                )
            elif clip2_transition.audio is not None:
                transition_composite = transition_composite.set_audio(
                    audio_fadein(clip2_transition.audio, safe_duration)
                )
            
            # 第二个片段的剩余部分
            clip2_main = clip2.subclip(safe_duration, clip2.duration)
            
            # 拼接所有部分
            parts = [clip1_main, transition_composite, clip2_main]
            parts = [part for part in parts if part.duration > 0]
            
            return concatenate_videoclips(parts)
            
        except Exception as e:
            print(f"缩放转场失败: {e}")
            return concatenate_videoclips([clip1, clip2])
    
    def apply_transition(self, clip1: VideoFileClip, clip2: VideoFileClip,
                        transition_config: Dict[str, Any]) -> VideoFileClip:
        """
        应用指定的转场效果
        
        Args:
            clip1: 第一个视频片段
            clip2: 第二个视频片段
            transition_config: 转场配置
        
        Returns:
            应用转场后的视频片段
        """
        transition_type = transition_config.get("type", "fade")
        duration = transition_config.get("duration", 1.0)
        
        print(f"应用转场效果: {transition_type}")
        
        if transition_type == "fade":
            return self.create_crossfade_transition(clip1, clip2, duration)
        elif transition_type == "slide_left":
            return self.create_slide_transition(clip1, clip2, "left", duration)
        elif transition_type == "slide_right":
            return self.create_slide_transition(clip1, clip2, "right", duration)
        elif transition_type == "slide_up":
            return self.create_slide_transition(clip1, clip2, "up", duration)
        elif transition_type == "slide_down":
            return self.create_slide_transition(clip1, clip2, "down", duration)
        elif transition_type == "zoom_in":
            return self.create_zoom_transition(clip1, clip2, "in", duration)
        elif transition_type == "zoom_out":
            return self.create_zoom_transition(clip1, clip2, "out", duration)
        else:
            # 默认使用简单拼接
            print(f"未知转场类型 {transition_type}，使用简单拼接")
            return concatenate_videoclips([clip1, clip2])

    def compose_videos_advanced(self, video_files: List[str], transitions: List[Dict[str, Any]],
                               output_filename: Optional[str] = None) -> str:
        """
        高级视频合成，支持复杂转场效果

        Args:
            video_files: 视频文件路径列表
            transitions: 转场配置列表
            output_filename: 输出文件名

        Returns:
            输出文件路径
        """
        if not video_files:
            raise ValueError("至少需要一个视频文件")

        if not output_filename:
            output_filename = f"advanced_composed_{uuid.uuid4().hex[:8]}.mp4"

        output_path = os.path.join(self.output_dir, output_filename)

        try:
            # 加载视频片段
            print(f"加载 {len(video_files)} 个视频文件")
            clips = []
            for i, video_file in enumerate(video_files):
                try:
                    print(f"正在加载第 {i+1} 个视频: {video_file}")
                    clip = VideoFileClip(video_file)
                    clips.append(clip)
                    print(f"成功加载视频: {video_file}, 时长: {clip.duration}秒, 尺寸: {clip.size}, 音频: {clip.audio is not None}")
                except Exception as e:
                    print(f"加载视频失败: {video_file}, 错误: {str(e)}")
                    raise ValueError(f"无法加载视频: {video_file}")

            if not clips:
                raise ValueError("没有成功加载任何视频")

            # 统一视频尺寸（使用第一个视频的尺寸）
            target_size = clips[0].size
            print(f"统一视频尺寸为: {target_size}")

            # 调整所有视频到相同尺寸
            resized_clips = []
            for i, clip in enumerate(clips):
                if clip.size != target_size:
                    print(f"调整第 {i+1} 个视频尺寸从 {clip.size} 到 {target_size}")
                    resized_clip = clip.resize(target_size)
                    resized_clips.append(resized_clip)
                else:
                    resized_clips.append(clip)

            if len(resized_clips) == 1:
                # 只有一个视频，直接输出
                print("只有一个视频，直接输出")
                final_clip = resized_clips[0]
            else:
                # 应用转场效果
                print(f"开始应用转场效果，合成 {len(resized_clips)} 个视频片段")

                # 确保转场配置数量正确
                while len(transitions) < len(resized_clips) - 1:
                    transitions.append({"type": "fade", "duration": 1.0})

                # 逐步应用转场效果
                result_clip = resized_clips[0]

                for i in range(1, len(resized_clips)):
                    transition_config = transitions[i - 1]
                    print(f"应用第 {i} 个转场: {transition_config}")

                    try:
                        result_clip = self.apply_transition(
                            result_clip,
                            resized_clips[i],
                            transition_config
                        )
                        print(f"第 {i} 个转场应用成功")
                    except Exception as e:
                        print(f"第 {i} 个转场应用失败: {e}，使用简单拼接")
                        result_clip = concatenate_videoclips([result_clip, resized_clips[i]])

                final_clip = result_clip

            # 输出视频
            print(f"开始输出视频到: {output_path}")
            print(f"最终视频时长: {final_clip.duration}秒")
            print(f"最终视频尺寸: {final_clip.size}")
            print(f"最终视频音频: {final_clip.audio is not None}")

            # 输出设置
            output_params = {
                'codec': 'libx264',
                'verbose': False,
                'logger': None,
                'preset': 'medium',  # 平衡质量和速度
                'ffmpeg_params': ['-crf', '23']  # 控制质量
            }

            if final_clip.audio is not None:
                output_params.update({
                    'audio_codec': 'aac',
                    'temp_audiofile': 'temp-audio.m4a',
                    'remove_temp': True
                })

            final_clip.write_videofile(output_path, **output_params)

            print(f"视频合成完成: {output_path}")

            # 清理资源
            for clip in clips:
                clip.close()
            for clip in resized_clips:
                if clip not in clips:  # 避免重复关闭
                    clip.close()
            final_clip.close()

            return output_path

        except Exception as e:
            print(f"视频合成过程中出错: {str(e)}")
            import traceback
            traceback.print_exc()

            # 清理资源
            try:
                for clip in clips:
                    clip.close()
            except:
                pass
            try:
                for clip in resized_clips:
                    clip.close()
            except:
                pass
            try:
                final_clip.close()
            except:
                pass

            raise e

    def get_video_info(self, video_path: str) -> Dict[str, Any]:
        """获取视频信息"""
        try:
            clip = VideoFileClip(video_path)
            info = {
                "duration": clip.duration,
                "size": clip.size,
                "fps": clip.fps,
                "has_audio": clip.audio is not None
            }
            clip.close()
            return info
        except Exception as e:
            return {"error": str(e)}
