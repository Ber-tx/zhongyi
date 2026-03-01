"""
闻诊音频分析模块
通过频谱分析、音调变化等特征提取来判断体质倾向
"""
import numpy as np
from scipy import signal
from scipy.fft import fft
import logging

logger = logging.getLogger(__name__)


class SoundAnalyzer:
    """音频分析器 - 用于闻诊诊断"""
    
    def __init__(self):
        # 默认采样率 (MediaRecorder 通常为 48kHz)
        self.sample_rate = 48000
        # 分析频率范围 (Hz)
        self.freq_range = (50, 8000)
        
    def analyze(self, audio_bytes) -> dict:
        """
        分析音频文件
        
        Args:
            audio_bytes: 音频文件的字节数据
            
        Returns:
            dict: 分析结果包含体质判断、置信度等信息
        """
        try:
            # 1. 读取音频
            audio_data = self._load_audio(audio_bytes)
            if audio_data is None or len(audio_data) == 0:
                return self._failure_response("音频数据加载失败")
            
            logger.info(f"成功加载音频，长度: {len(audio_data)} samples")
            
            # 2. 提取特征
            features = self._extract_features(audio_data)
            logger.info(f"提取特征: {features}")
            
            # 3. 进行体质判断
            diagnosis = self._diagnose_constitution(features)
            logger.info(f"诊断结果: {diagnosis}")
            
            # 4. 格式化返回结果
            return self._format_result(diagnosis, features)
            
        except Exception as e:
            logger.error(f"音频分析异常: {str(e)}", exc_info=True)
            return self._failure_response(f"分析异常: {str(e)}")
    
    def _load_audio(self, audio_bytes) -> np.ndarray:
        """
        读取音频数据
        支持 WebM 格式（浏览器 MediaRecorder 默认格式）
        """
        try:
            # 方案1：尝试用 pydub (推荐，支持多种格式)
            try:
                from pydub import AudioSegment
                from io import BytesIO
                
                logger.info("使用 pydub 处理音频")
                audio = AudioSegment.from_file(BytesIO(audio_bytes), format="webm")
                
                # 转为 numpy 数组
                samples = np.array(audio.get_array_of_samples())
                
                # 如果是立体声，转为单声道
                if audio.channels == 2:
                    samples = samples.reshape((-1, 2)).mean(axis=1)
                
                # 转为浮点数并归一化到 [-1, 1]
                samples = samples.astype(np.float32) / np.max(np.abs(samples) + 1e-10)
                self.sample_rate = audio.frame_rate
                
                logger.info(f"pydub 成功加载音频: 采样率={self.sample_rate}, 通道数={audio.channels}")
                return samples
                
            except ImportError:
                logger.warning("pydub 未安装，尝试备用方案")
                raise
            
        except Exception as e1:
            logger.warning(f"pydub 处理失败: {str(e1)}, 尝试备用方案")
            
            try:
                # 方案2：尝试用 scipy 读取
                from scipy.io import wavfile
                from io import BytesIO
                import tempfile
                import os
                
                with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as tmp:
                    tmp.write(audio_bytes)
                    tmp_path = tmp.name
                
                try:
                    import subprocess
                    wav_path = tmp_path.replace('.webm', '.wav')
                    cmd = ['ffmpeg', '-i', tmp_path, '-q:a', '9', '-n', wav_path]
                    
                    try:
                        subprocess.run(cmd, capture_output=True, timeout=10)
                        if os.path.exists(wav_path):
                            sr, audio_data = wavfile.read(wav_path)
                            self.sample_rate = sr
                            audio_data = audio_data.astype(np.float32) / np.max(np.abs(audio_data) + 1e-10)
                            logger.info(f"FFmpeg 成功转换音频")
                            os.remove(wav_path)
                            return audio_data
                    except:
                        pass
                finally:
                    if os.path.exists(tmp_path):
                        os.remove(tmp_path)
                
            except Exception as e2:
                logger.warning(f"FFmpeg 方案也失败: {str(e2)}")
            
            # 方案3：直接提取 PCM 数据
            logger.info("使用 PCM 原始数据提取方案")
            return self._extract_raw_pcm(audio_bytes)
    
    def _extract_raw_pcm(self, audio_bytes) -> np.ndarray:
        """
        从原始字节数据中提取 PCM 音频
        支持多种采样率的 PCM 数据
        """
        try:
            # 尝试多种数据类型和采样率组合
            attempts = [
                (np.int16, 16000),  # 16-bit PCM, 16kHz
                (np.int16, 48000),  # 16-bit PCM, 48kHz
                (np.int16, 44100),  # 16-bit PCM, 44.1kHz
                (np.int32, 48000),  # 32-bit PCM, 48kHz
                (np.float32, 48000), # 32-bit float, 48kHz
                (np.float32, 16000), # 32-bit float, 16kHz
            ]
            
            best_result = None
            best_energy = 0
            
            for dtype, sample_rate in attempts:
                try:
                    # 计算每个样本的字节数
                    bytes_per_sample = np.dtype(dtype).itemsize
                    
                    # 检查字节数是否匹配
                    if len(audio_bytes) % bytes_per_sample == 0:
                        data = np.frombuffer(audio_bytes, dtype=dtype)
                        
                        # 转为浮点数
                        if dtype in [np.int16, np.int32]:
                            float_data = data.astype(np.float32) / np.iinfo(dtype).max
                        else:
                            float_data = data.astype(np.float32)
                        
                        # 检查数据有效性（计算能量）
                        energy = np.sqrt(np.mean(float_data ** 2))
                        
                        if energy > 0 and energy < 100 and energy > best_energy:
                            best_result = float_data
                            best_energy = energy
                            self.sample_rate = sample_rate
                            logger.info(f"PCM 提取成功: dtype={dtype}, sr={sample_rate}Hz, energy={energy:.4f}")
                            break
                            
                except Exception as e:
                    continue
            
            if best_result is not None:
                return best_result
            
            # 都失败了，返回空数组
            logger.error("PCM 提取失败：无有效数据")
            return np.array([])
            
        except Exception as e:
            logger.error(f"PCM 提取异常: {str(e)}")
            return np.array([])
    
    def _extract_features(self, audio_data: np.ndarray) -> dict:
        """
        提取音频特征
        """
        features = {}
        
        # 1. 能量特征
        features['rms_energy'] = float(np.sqrt(np.mean(audio_data ** 2)))
        
        # 2. 频谱分析
        spectrum = np.abs(fft(audio_data))
        freqs = np.fft.fftfreq(len(audio_data), 1 / self.sample_rate)
        
        # 只取正频率部分
        positive_idx = freqs > 0
        freqs = freqs[positive_idx]
        spectrum = spectrum[positive_idx]
        
        # 3. 低频/高频能量比
        low_freq_energy = np.sum(spectrum[(freqs >= 50) & (freqs < 500)])
        high_freq_energy = np.sum(spectrum[(freqs >= 2000) & (freqs < 8000)])
        mid_freq_energy = np.sum(spectrum[(freqs >= 500) & (freqs < 2000)])
        
        total_energy = low_freq_energy + mid_freq_energy + high_freq_energy
        
        features['low_freq_ratio'] = float(low_freq_energy / (total_energy + 1e-10))  # 低频占比
        features['mid_freq_ratio'] = float(mid_freq_energy / (total_energy + 1e-10))  # 中频占比
        features['high_freq_ratio'] = float(high_freq_energy / (total_energy + 1e-10)) # 高频占比
        
        # 4. 主频率 (基频 - fundamental frequency)
        if len(spectrum) > 0:
            peak_idx = np.argmax(spectrum)
            features['fundamental_freq'] = float(freqs[peak_idx]) if peak_idx < len(freqs) else 0
        else:
            features['fundamental_freq'] = 0
        
        # 5. 音调稳定性 (基于包络)
        try:
            envelope = self._compute_envelope(audio_data)
            features['pitch_stability'] = float(1.0 - np.std(envelope) / (np.mean(envelope) + 1e-10))
            features['pitch_stability'] = np.clip(features['pitch_stability'], 0, 1)
        except:
            features['pitch_stability'] = 0.5
        
        # 6. 音频时间特性
        features['duration'] = len(audio_data) / self.sample_rate
        
        # 7. 峰值因子 (动态范围)
        features['crest_factor'] = float(np.max(np.abs(audio_data)) / (np.sqrt(np.mean(audio_data ** 2)) + 1e-10))
        
        return features
    
    def _compute_envelope(self, signal_data: np.ndarray) -> np.ndarray:
        """
        计算音频包络
        """
        try:
            # 使用 Hilbert 变换计算解析信号的包络
            analytic_signal = signal.hilbert(signal_data)
            envelope = np.abs(analytic_signal)
            # 下采样以减少计算
            envelope = envelope[::100]
            return envelope
        except:
            return np.ones(len(signal_data))
    
    def _diagnose_constitution(self, features: dict) -> dict:
        """
        根据音频特征进行体质诊断
        
        简化规则：
        - 低频占比高 → 阴虚质 (声音沉闷、呼吸低沉)
        - 高频占比高 → 阳虚质 (声音尖锐、呼吸急促)
        - 低频高频平衡 → 平和质 (声音均衡)
        - 音调不稳定 → 气滞血瘀 (声音不连贯)
        """
        
        diagnosis = {
            'constitution': '',
            'main_finding': '',
            'confidence': 0.0,
            'tags': [],
            'details': []
        }
        
        low_freq = features.get('low_freq_ratio', 0)
        high_freq = features.get('high_freq_ratio', 0)
        mid_freq = features.get('mid_freq_ratio', 0)
        stability = features.get('pitch_stability', 0.5)
        crest = features.get('crest_factor', 1.0)
        rms = features.get('rms_energy', 0)
        
        # 规则 1: 频率分布判断
        confidence = 0.0
        
        if low_freq > 0.45:  # 低频占主导
            diagnosis['constitution'] = '阴虚质'
            diagnosis['tags'] = ['阴液不足', '脾胃虚弱', '呼吸沉缓']
            diagnosis['details'] = [
                '音频特征显示低频成分占比较高（{:.1f}%）'.format(low_freq * 100),
                '反映呼吸较为沉闷，可能存在气虚倾向',
                '建议滋阴润肺，加强脾胃调理'
            ]
            confidence = min(0.85, 0.5 + low_freq)
            
        elif high_freq > 0.40:  # 高频占主导
            diagnosis['constitution'] = '阳虚质'
            diagnosis['tags'] = ['阳气不足', '代谢缓慢', '体温偏低']
            diagnosis['details'] = [
                '音频特征显示高频成分占比较高（{:.1f}%）'.format(high_freq * 100),
                '反映呼吸可能急促，提示阳气偏升',
                '建议温阳健脾，增加运动强度'
            ]
            confidence = min(0.85, 0.5 + high_freq)
            
        else:  # 分布均衡
            diagnosis['constitution'] = '平和质'
            diagnosis['tags'] = ['气血充足', '呼吸均匀', '体质平衡']
            diagnosis['details'] = [
                '音频特征显示频率分布均衡',
                '反映呼吸节奏稳定，体质基本平衡',
                '建议保持良好生活习惯，定期锻炼'
            ]
            confidence = 0.75
        
        # 规则 2: 音调稳定性判断
        if stability < 0.4:
            diagnosis['tags'].append('气滞血瘀')
            diagnosis['details'].append('音调不稳定，可能存在情绪紧张或气血滞滞情况')
            confidence *= 0.9
        elif stability > 0.8:
            diagnosis['details'].append('音调稳定性良好，反映精神状态相对放松')
            confidence = min(1.0, confidence + 0.05)
        
        # 规则 3: 峰值因子 (动态范围)
        if crest > 3.0:
            diagnosis['tags'].append('湿热体质')
            diagnosis['details'].append('音频动态范围较大，可能反映体内湿热较重')
            confidence *= 0.8
        
        # 规则 4: RMS 能量 (音量)
        if rms < 0.05:  # 声音很小
            diagnosis['details'].append('音量较小，建议以正常音量重新录制')
            confidence *= 0.7
        elif rms > 0.4:  # 声音很大
            diagnosis['tags'].append('气虚易怒')
        
        diagnosis['confidence'] = float(np.clip(confidence, 0.3, 0.95))
        
        return diagnosis
    
    def _format_result(self, diagnosis: dict, features: dict) -> dict:
        """
        格式化返回结果
        """
        return {
            'success': True,
            'data': {
                'main_finding': diagnosis['constitution'],
                'confidence': diagnosis['confidence'],
                'constitution_tags': diagnosis['tags'],
                'details': diagnosis['details'],
                'features': features  # 可选：返回原始特征供前端展示
            }
        }
    
    def _failure_response(self, msg: str) -> dict:
        """
        失败响应
        """
        return {
            'success': False,
            'msg': msg
        }
