import os
from pydub import AudioSegment

# 根目录（你的音频目录）
ROOT_DIR = r"E:\项目\Vue\zhongyi\src\assets\audio"

# 统计
total = 0
success = 0
skipped = 0
failed = 0

for root, dirs, files in os.walk(ROOT_DIR):
    for file in files:
        if file.lower().endswith(".wav"):
            total += 1

            wav_path = os.path.join(root, file)
            mp3_path = os.path.join(root, file[:-4] + ".mp3")

            # 如果已经存在 mp3，跳过
            if os.path.exists(mp3_path):
                print(f"[跳过] 已存在: {mp3_path}")
                skipped += 1
                continue

            try:
                audio = AudioSegment.from_wav(wav_path)
                audio.export(mp3_path, format="mp3", bitrate="192k")

                print(f"[成功] {mp3_path}")
                success += 1
            except Exception as e:
                print(f"[失败] {wav_path} -> {e}")
                failed += 1

print("\n====== 转换完成 ======")
print(f"总文件: {total}")
print(f"成功: {success}")
print(f"跳过: {skipped}")
print(f"失败: {failed}")