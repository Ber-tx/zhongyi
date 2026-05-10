"""
闻诊音频分析模块 v2.0
特征提取算法来源：
  [1] MFCC特征：Wang et al. (2024). "Sound as a bell: a deep learning approach for health
      status classification through speech acoustic biomarkers." Chinese Medicine 19, 101.
      https://doi.org/10.1186/s13020-024-00973-3
      → 北京中医药大学发表，直接针对TCM九种体质分类，使用MFCC作为主特征，Conv2D验证集准确率84.93%

  [2] Jitter / Shimmer / HNR：Teixeira et al. (2013). "Vocal Acoustic Analysis – Jitter,
      Shimmer and HNR Parameters." Procedia Technology 9, 1112-1122.
      https://doi.org/10.1016/j.protcy.2013.12.124
      → 经典声学病理诊断特征，通过 parselmouth (Praat Python接口) 提取

  [3] parselmouth 实现参考：Feinberg, D. (2021). PraatScripts (GitHub).
      https://github.com/drfeinberg/PraatScripts
      → 提供了在Python中用parselmouth提取Jitter/Shimmer/HNR的标准脚本

  [4] 多标签脉象语音分类：Shen et al. (2024). "Classification research of TCM pulse conditions
      based on multi-label voice analysis." Journal of Traditional Chinese Medical Sciences
      11(2), 172-179. https://doi.org/10.1016/j.jtcms.2024.03.008
      → 验证了语音特征+DNN在TCM诊断中的可行性，多标签模型准确率92.74%

依赖：
    pip install librosa parselmouth numpy scipy
    音频格式转换仍依赖 pydub / ffmpeg（同原版）
"""

import numpy as np
from scipy import signal
from scipy.fft import fft
import logging
import tempfile
import os

logger = logging.getLogger(__name__)


class SoundAnalyzer:
    """
    音频分析器 - 用于闻诊诊断 v2.0

    特征体系（共约40维）：
      - MFCC 1-13阶 均值+标准差（26维）  → 来源 [1]
      - 基频(F0) 均值/标准差             → 声调高低与稳定性
      - Jitter（音调微扰）               → 来源 [2][3]
      - Shimmer（振幅微扰）              → 来源 [2][3]
      - HNR（谐波噪声比）                → 来源 [2][3]
      - RMS能量 / 峰值因子               → 保留原版指标
    """

    def __init__(self):
        self.sample_rate = 48000

    # ------------------------------------------------------------------ #
    #  公共接口                                                             #
    # ------------------------------------------------------------------ #

    def analyze(self, audio_bytes: bytes) -> dict:
        """
        分析音频，返回体质判断结果。

        Returns:
            {
              'success': True,
              'data': {
                'main_finding': str,       # 主体质
                'confidence': float,       # 置信度 0-1
                'constitution_tags': list, # 辅助标签
                'details': list,           # 文字说明
                'features': dict           # 原始特征值（供前端展示）
              }
            }
            或 {'success': False, 'msg': str}
        """
        try:
            audio_data = self._load_audio(audio_bytes)
            if audio_data is None or len(audio_data) < self.sample_rate * 0.5:
                return self._failure_response("音频数据加载失败或时长过短（建议至少录制3秒）")

            logger.info(f"成功加载音频，长度: {len(audio_data)} samples, 采样率: {self.sample_rate} Hz")

            features = self._extract_features(audio_data)
            logger.info(f"提取特征完成: {features}")

            diagnosis = self._diagnose_constitution(features)
            logger.info(f"诊断结果: {diagnosis}")

            return self._format_result(diagnosis, features)

        except Exception as e:
            logger.error(f"音频分析异常: {str(e)}", exc_info=True)
            return self._failure_response(f"分析异常: {str(e)}")

    # ------------------------------------------------------------------ #
    #  音频加载（保持原版逻辑，仅增加临时文件路径返回供parselmouth使用）      #
    # ------------------------------------------------------------------ #

    def _load_audio(self, audio_bytes: bytes):
        """返回 (numpy_array, tmp_wav_path_or_None)"""
        # 方案1: pydub
        try:
            from pydub import AudioSegment
            from io import BytesIO

            audio = AudioSegment.from_file(BytesIO(audio_bytes), format="webm")
            samples = np.array(audio.get_array_of_samples())
            if audio.channels == 2:
                samples = samples.reshape((-1, 2)).mean(axis=1)
            samples = samples.astype(np.float32) / (np.max(np.abs(samples)) + 1e-10)
            self.sample_rate = audio.frame_rate
            self._save_tmp_wav(samples)          # 供 parselmouth 使用
            logger.info(f"pydub 加载成功: sr={self.sample_rate}")
            return samples
        except Exception as e1:
            logger.warning(f"pydub 失败: {e1}")

        # 方案2: ffmpeg → wav
        try:
            import subprocess
            from scipy.io import wavfile

            with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as tmp:
                tmp.write(audio_bytes)
                tmp_path = tmp.name
            wav_path = tmp_path.replace('.webm', '.wav')
            subprocess.run(['ffmpeg', '-i', tmp_path, '-q:a', '9', '-n', wav_path],
                           capture_output=True, timeout=10)
            if os.path.exists(wav_path):
                sr, audio_data = wavfile.read(wav_path)
                self.sample_rate = sr
                audio_data = audio_data.astype(np.float32) / (np.max(np.abs(audio_data)) + 1e-10)
                self._tmp_wav_path = wav_path          # 直接交给 parselmouth
                os.remove(tmp_path)
                return audio_data
        except Exception as e2:
            logger.warning(f"ffmpeg 失败: {e2}")

        # 方案3: 原始PCM
        return self._extract_raw_pcm(audio_bytes)

    def _save_tmp_wav(self, samples: np.ndarray):
        """将numpy数组存为临时wav，供parselmouth读取"""
        try:
            from scipy.io import wavfile
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as f:
                self._tmp_wav_path = f.name
            # 转为int16写入
            wavfile.write(self._tmp_wav_path,
                          self.sample_rate,
                          (samples * 32767).astype(np.int16))
        except Exception as e:
            logger.warning(f"临时wav保存失败: {e}")
            self._tmp_wav_path = None

    def _extract_raw_pcm(self, audio_bytes: bytes) -> np.ndarray:
        attempts = [
            (np.int16, 16000), (np.int16, 48000), (np.int16, 44100),
            (np.int32, 48000), (np.float32, 48000), (np.float32, 16000),
        ]
        best_result, best_energy = None, 0
        for dtype, sample_rate in attempts:
            try:
                bps = np.dtype(dtype).itemsize
                if len(audio_bytes) % bps == 0:
                    data = np.frombuffer(audio_bytes, dtype=dtype)
                    float_data = (data.astype(np.float32) / np.iinfo(dtype).max
                                  if dtype in [np.int16, np.int32]
                                  else data.astype(np.float32))
                    energy = np.sqrt(np.mean(float_data ** 2))
                    if 0 < energy < 100 and energy > best_energy:
                        best_result, best_energy = float_data, energy
                        self.sample_rate = sample_rate
                        self._save_tmp_wav(float_data)
                        break
            except Exception:
                continue
        if best_result is None:
            logger.error("PCM 提取失败")
            return np.array([])
        return best_result

    # ------------------------------------------------------------------ #
    #  特征提取                                                             #
    # ------------------------------------------------------------------ #

    # AI辅助生成：ChatGPT（GPT-5.3）, 2026-03-20
    def _extract_features(self, audio_data: np.ndarray) -> dict:
        """
                这里沿用“特征提取 + 规则映射”的工程实现：论文特征负责提供可解释性，
                规则阈值则根据项目展示场景做了收敛和降级处理。

        特征体系说明：
          ① MFCC（梅尔频率倒谱系数）
             来源: Wang et al. 2024 [1] — 北京中医药大学直接将MFCC作为体质分类的
             输入特征，是目前TCM语音诊断中效果最好的特征集。
             提取方式: librosa.feature.mfcc，n_mfcc=13，与论文一致。
             特征数: 13均值 + 13标准差 = 26维

          ② 基频 F0（音高均值与稳定性）
             来源: Shen et al. 2024 [4] — TCM脉象语音分类中使用了基频特征。
             提取方式: librosa.pyin（概率YIN算法，比原版FFT最大值精确得多）

          ③ Jitter（音调微扰）/ Shimmer（振幅微扰）/ HNR（谐波噪声比）
             来源: Teixeira et al. 2013 [2]，实现参考 Feinberg PraatScripts [3]。
             Jitter反映声带规律性，Shimmer反映振幅稳定性，HNR反映气息纯净度，
             均与中医"气虚""气滞"等概念直接对应。
             提取方式: parselmouth (Praat Python接口)
        """
        features = {}

        # ① 基础能量特征（原版保留）
        features['rms_energy'] = float(np.sqrt(np.mean(audio_data ** 2)))
        features['crest_factor'] = float(
            np.max(np.abs(audio_data)) / (np.sqrt(np.mean(audio_data ** 2)) + 1e-10))
        features['duration'] = len(audio_data) / self.sample_rate

        # ② MFCC 特征 —— 来源 [1] Wang et al. 2024
        try:
            import librosa
            # 重采样到 16kHz（MFCC分析的标准采样率）
            y16 = librosa.resample(audio_data, orig_sr=self.sample_rate, target_sr=16000)
            mfcc = librosa.feature.mfcc(y=y16, sr=16000, n_mfcc=13)
            for i in range(13):
                features[f'mfcc_mean_{i+1}'] = float(np.mean(mfcc[i]))
                features[f'mfcc_std_{i+1}']  = float(np.std(mfcc[i]))
            logger.info("MFCC 提取成功（26维）")
        except ImportError:
            logger.warning("librosa 未安装，降级为频带能量比（精度下降）")
            self._fallback_spectrum_features(audio_data, features)
        except Exception as e:
            logger.warning(f"MFCC 提取失败: {e}，降级处理")
            self._fallback_spectrum_features(audio_data, features)

        # ③ 基频 F0 —— 来源 [4] Shen et al. 2024
        try:
            import librosa
            y16 = librosa.resample(audio_data, orig_sr=self.sample_rate, target_sr=16000)
            f0, voiced_flag, _ = librosa.pyin(
                y16,
                fmin=librosa.note_to_hz('C2'),   # ~65 Hz
                fmax=librosa.note_to_hz('C7'),   # ~2093 Hz
                sr=16000
            )
            voiced_f0 = f0[voiced_flag]
            features['f0_mean']      = float(np.mean(voiced_f0))      if len(voiced_f0) > 0 else 0.0
            features['f0_std']       = float(np.std(voiced_f0))       if len(voiced_f0) > 0 else 0.0
            features['voiced_ratio'] = float(np.mean(voiced_flag))    # 有声帧比例
            logger.info(f"F0 提取成功: mean={features['f0_mean']:.1f}Hz, std={features['f0_std']:.2f}")
        except Exception as e:
            logger.warning(f"F0 提取失败: {e}")
            features['f0_mean'] = features['f0_std'] = features['voiced_ratio'] = 0.0

        # ④ Jitter / Shimmer / HNR —— 来源 [2][3]
        self._extract_praat_features(features)

        return features

    def _extract_praat_features(self, features: dict):
        """
        使用 parselmouth (Praat Python接口) 提取 Jitter/Shimmer/HNR。
        实现参考：Feinberg PraatScripts [3]
          https://github.com/drfeinberg/PraatScripts
        特征含义（Teixeira et al. 2013 [2]）：
          - localJitter: 相邻周期长度变化率，反映声带振动不规则性
          - localShimmer: 相邻周期振幅变化率，反映气流稳定性
          - HNR(dB): 谐波噪声比，越高声音越纯净，气虚者偏低
        """
        tmp_path = getattr(self, '_tmp_wav_path', None)
        if tmp_path is None or not os.path.exists(tmp_path):
            logger.warning("无临时wav文件，跳过 parselmouth 特征")
            features.update({'jitter': 0.0, 'shimmer': 0.0, 'hnr': 0.0})
            return
        try:
            import parselmouth
            from parselmouth.praat import call

            sound = parselmouth.Sound(tmp_path)
            f0min, f0max = 75, 500   # 与 Feinberg PraatScripts 一致

            # HNR
            harmonicity = call(sound, "To Harmonicity (cc)", 0.01, f0min, 0.1, 1.0)
            features['hnr'] = float(call(harmonicity, "Get mean", 0, 0))

            # Jitter & Shimmer
            point_process = call(sound, "To PointProcess (periodic, cc)", f0min, f0max)
            features['jitter'] = float(
                call(point_process, "Get jitter (local)", 0, 0, 0.0001, 0.02, 1.3))
            features['shimmer'] = float(
                call([sound, point_process], "Get shimmer (local)", 0, 0, 0.0001, 0.02, 1.3, 1.6))

            logger.info(f"Praat特征: jitter={features['jitter']:.4f}, "
                        f"shimmer={features['shimmer']:.4f}, hnr={features['hnr']:.2f}dB")
        except ImportError:
            logger.warning("parselmouth 未安装（pip install parselmouth），跳过 Jitter/Shimmer/HNR")
            features.update({'jitter': 0.0, 'shimmer': 0.0, 'hnr': 0.0})
        except Exception as e:
            logger.warning(f"parselmouth 特征提取失败: {e}")
            features.update({'jitter': 0.0, 'shimmer': 0.0, 'hnr': 0.0})
        finally:
            # 清理临时文件
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass

    def _fallback_spectrum_features(self, audio_data: np.ndarray, features: dict):
        """当 librosa 不可用时降级为原版频带能量比"""
        spectrum = np.abs(fft(audio_data))
        freqs    = np.fft.fftfreq(len(audio_data), 1 / self.sample_rate)
        pos      = freqs > 0
        freqs, spectrum = freqs[pos], spectrum[pos]
        low  = np.sum(spectrum[(freqs >= 50)   & (freqs < 500)])
        mid  = np.sum(spectrum[(freqs >= 500)  & (freqs < 2000)])
        high = np.sum(spectrum[(freqs >= 2000) & (freqs < 8000)])
        total = low + mid + high + 1e-10
        features['low_freq_ratio']  = float(low  / total)
        features['mid_freq_ratio']  = float(mid  / total)
        features['high_freq_ratio'] = float(high / total)
        # 填充MFCC位置为0，避免后续KeyError
        for i in range(13):
            features[f'mfcc_mean_{i+1}'] = 0.0
            features[f'mfcc_std_{i+1}']  = 0.0

    # ------------------------------------------------------------------ #
    #  体质诊断                                                             #
    # ------------------------------------------------------------------ #

    # AI辅助生成：ChatGPT（GPT-5.3）, 2026-03-20
    def _diagnose_constitution(self, features: dict) -> dict:
        """多特征加权判定：先做稳健归一化，再计算各体质证据分。"""
        diagnosis = {
            'constitution': '',
            'main_finding': '',
            'confidence': 0.0,
            'tags': [],
            'details': []
        }

        def clamp01(v):
            return float(np.clip(v, 0.0, 1.0))

        def norm(v, lo, hi):
            if hi <= lo:
                return 0.0
            return clamp01((float(v) - lo) / (hi - lo))

        mfcc1 = float(features.get('mfcc_mean_1', 0.0))
        mfcc2 = float(features.get('mfcc_mean_2', 0.0))
        mfcc_var = float(np.mean([features.get(f'mfcc_std_{i}', 0.0) for i in range(1, 6)]))
        f0_mean = float(features.get('f0_mean', 0.0))
        f0_std = float(features.get('f0_std', 0.0))
        voiced_ratio = float(features.get('voiced_ratio', 0.0))
        jitter = float(features.get('jitter', 0.0))
        shimmer = float(features.get('shimmer', 0.0))
        hnr = float(features.get('hnr', 0.0))
        rms = float(features.get('rms_energy', 0.0))
        duration = float(features.get('duration', 0.0))

        using_fallback = (abs(mfcc1) < 1e-9 and features.get('low_freq_ratio') is not None)

        # 1) 特征质量分（用于置信度）
        q_duration = norm(duration, 1.5, 8.0)
        q_energy = norm(rms, 0.02, 0.12)
        q_voiced = norm(voiced_ratio, 0.25, 0.85)
        q_hnr = norm(hnr, 5.0, 20.0) if hnr > 0 else 0.0
        quality = 0.35 * q_duration + 0.30 * q_energy + 0.20 * q_voiced + 0.15 * q_hnr
        if using_fallback:
            quality *= 0.85
        if jitter == 0.0 and shimmer == 0.0:
            quality *= 0.9

        # 2) 体质证据分（0~1）
        # 平和：能量稳定、音调稳定、噪声低
        s_pinghe = (
            0.30 * norm(hnr, 12.0, 24.0) +
            0.20 * (1.0 - norm(jitter, 0.004, 0.018)) +
            0.20 * (1.0 - norm(shimmer, 0.02, 0.08)) +
            0.15 * (1.0 - norm(abs(mfcc2), 12.0, 45.0)) +
            0.15 * (1.0 - norm(f0_std, 20.0, 90.0))
        )

        # 气虚：低能量、微扰高、谐噪比低
        s_qixu = (
            0.30 * (1.0 - norm(rms, 0.03, 0.10)) +
            0.25 * norm(jitter, 0.006, 0.022) +
            0.20 * norm(shimmer, 0.03, 0.10) +
            0.15 * (1.0 - norm(hnr, 8.0, 20.0)) +
            0.10 * (1.0 - norm(voiced_ratio, 0.35, 0.85))
        )

        # 阴虚：偏高音、波动偏大、频谱偏尖
        s_yinxu = (
            0.30 * norm(f0_mean, 170.0, 290.0) +
            0.25 * norm(f0_std, 18.0, 80.0) +
            0.20 * norm(mfcc2, 5.0, 45.0) +
            0.15 * norm(mfcc_var, 18.0, 55.0) +
            0.10 * norm(shimmer, 0.02, 0.08)
        )

        # 阳虚：低音低能、声势偏弱
        s_yangxu = (
            0.35 * (1.0 - norm(f0_mean, 95.0, 170.0)) +
            0.25 * (1.0 - norm(rms, 0.03, 0.10)) +
            0.20 * (1.0 - norm(voiced_ratio, 0.35, 0.85)) +
            0.20 * (1.0 - norm(hnr, 8.0, 20.0))
        )

        # 气滞血瘀：音调不稳、节律起伏、微扰增高
        s_qizhi = (
            0.30 * norm(f0_std, 20.0, 90.0) +
            0.25 * norm(mfcc_var, 20.0, 60.0) +
            0.20 * norm(jitter, 0.006, 0.022) +
            0.15 * norm(shimmer, 0.03, 0.10) +
            0.10 * norm(abs(mfcc2), 12.0, 45.0)
        )

        if using_fallback:
            low_freq = float(features.get('low_freq_ratio', 0.0))
            high_freq = float(features.get('high_freq_ratio', 0.0))
            s_yinxu += 0.18 * norm(low_freq, 0.30, 0.60)
            s_yangxu += 0.18 * norm(high_freq, 0.30, 0.60)
            s_pinghe += 0.08 * (1.0 - norm(abs(low_freq - high_freq), 0.05, 0.30))

        scores = {
            '平和质': round(clamp01(s_pinghe), 4),
            '气虚质': round(clamp01(s_qixu), 4),
            '阴虚质': round(clamp01(s_yinxu), 4),
            '阳虚质': round(clamp01(s_yangxu), 4),
            '气滞血瘀': round(clamp01(s_qizhi), 4),
        }

        ordered = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
        constitution = ordered[0][0]
        top_score = ordered[0][1]
        second_score = ordered[1][1]
        margin = max(0.0, top_score - second_score)

        # 3) 置信度：分数分离度 + 数据质量
        confidence = 0.45 + 0.30 * quality + 0.30 * margin
        if margin < 0.08:
            confidence -= 0.08
        confidence = float(np.clip(confidence, 0.35, 0.95))

        diagnosis['constitution'] = constitution
        diagnosis['confidence'] = confidence

        const_tags = {
            '平和质': ['气血充足', '呼吸均匀', '体质平衡'],
            '气虚质': ['气力不足', '声音偏弱', '声带振动不规则'],
            '阴虚质': ['阴液不足', '声调偏高', '音色偏燥'],
            '阳虚质': ['阳气不足', '声音低沉', '气息偏弱'],
            '气滞血瘀': ['气机不畅', '音调波动', '声音不连贯'],
        }
        diagnosis['tags'] = const_tags.get(constitution, [])

        details = [
            f"综合证据分: 平和={scores['平和质']}, 气虚={scores['气虚质']}, 阴虚={scores['阴虚质']}, 阳虚={scores['阳虚质']}, 气滞血瘀={scores['气滞血瘀']}",
            f"主次分离度={margin:.3f}，录音质量={quality:.3f}",
            f"关键特征: F0={f0_mean:.1f}Hz, F0波动={f0_std:.1f}, Jitter={jitter:.4f}, Shimmer={shimmer:.4f}, HNR={hnr:.1f}dB",
        ]

        advice_map = {
            '平和质': '建议保持规律作息与适度运动。',
            '气虚质': '建议先改善睡眠与体能，结合补气调理。',
            '阴虚质': '建议滋阴润燥，减少熬夜与辛辣刺激。',
            '阳虚质': '建议温阳健脾，规律有氧运动并注意保暖。',
            '气滞血瘀': '建议疏肝理气，采用舒缓运动改善节律。',
        }
        details.append(advice_map.get(constitution, '建议结合四诊信息综合判断。'))

        if duration < 1.5:
            details.append('录音时长偏短，建议录制3-10秒稳定语音。')
        if rms < 0.02:
            details.append('录音音量偏低，建议贴近麦克风并降低环境噪声。')
        if using_fallback:
            details.append('当前处于降级特征模式（无librosa），建议安装完整依赖后再测。')

        diagnosis['details'] = details
        return diagnosis

    # ------------------------------------------------------------------ #
    #  格式化输出（保持原版结构不变）                                        #
    # ------------------------------------------------------------------ #

    def _format_result(self, diagnosis: dict, features: dict) -> dict:
        return {
            'success': True,
            'data': {
                'main_finding':      diagnosis['constitution'],
                'confidence':        diagnosis['confidence'],
                'constitution_tags': diagnosis['tags'],
                'details':           diagnosis['details'],
                'features':          features,
            }
        }

    def _failure_response(self, msg: str) -> dict:
        return {'success': False, 'msg': msg}