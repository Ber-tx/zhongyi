import os
from pydub import AudioSegment

ROOT_DIR = r"E:\项目\Vue\zhongyi\src\assets\audio"

total = 0
success = 0
deleted = 0
failed = 0

for root, dirs, files in os.walk(ROOT_DIR):
    for file in files:
        if file.lower().endswith(".wav"):
            total += 1

            wav_path = os.path.join(root, file)
            mp3_path = os.path.join(root, file[:-4] + ".mp3")

            try:
                # 转换
                audio = AudioSegment.from_wav(wav_path)
                audio.export(mp3_path, format="mp3", bitrate="192k")

                # 检查 MP3 是否生成成功
                if os.path.exists(mp3_path) and os.path.getsize(mp3_path) > 0:
                    os.remove(wav_path)  # 删除原 WAV
                    print(f"[成功+删除] {wav_path}")
                    success += 1
                    deleted += 1
                else:
                    print(f"[失败] MP3未生成: {wav_path}")
                    failed += 1

            except Exception as e:
                print(f"[错误] {wav_path} -> {e}")
                failed += 1

print("\n====== 完成 ======")
print(f"总数: {total}")
print(f"成功转换: {success}")
print(f"已删除WAV: {deleted}")
print(f"失败: {failed}")