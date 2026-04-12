using IdCardReaderService.Models;
using System.Globalization;
using System.Text;

namespace IdCardReaderService.Services
{
    /// <summary>
    /// 身份证读卡器主服务实现 (x86)
    /// 通过 DLL 调用与读卡器硬件交互
    /// </summary>
    public class IdCardReaderService : IIdCardReaderService
    {
        private readonly ILogger<IdCardReaderService> _logger;
        private int _openedPort = -1;
        private bool _isConnected = false;
        private readonly object _lockObject = new();

        public IdCardReaderService(ILogger<IdCardReaderService> logger)
        {
            _logger = logger;
        }

        /// <summary>
        /// 读取身份证信息
        /// </summary>
        public async Task<IdCardInfo> ReadIdCardAsync()
        {
            return await Task.Run(() =>
            {
                lock (_lockObject)
                {
                    try
                    {
                        _logger.LogInformation("开始读卡...");

                        // 步骤 1: 初始化读卡器连接
                        if (!_isConnected)
                        {
                            var result = EnsureReaderConnected();
                            if (!result)
                            {
                                return new IdCardInfo
                                {
                                    Success = false,
                                    Message = "读卡器未连接或初始化失败"
                                };
                            }
                        }

                        // 步骤 2: 寻卡
                        byte[] manaInfo = new byte[16];
                        var searchResult = IdCardDllWrapper.SDT_StartFindIDCard(_openedPort, manaInfo, 0);
                        if (!IdCardDllWrapper.IsFindCardSuccess(searchResult))
                        {
                            _logger.LogWarning($"寻卡失败: {IdCardDllWrapper.GetErrorMessage(searchResult)}");
                            return new IdCardInfo
                            {
                                Success = false,
                                Message = $"寻卡失败: {IdCardDllWrapper.GetErrorMessage(searchResult)}"
                            };
                        }

                        _logger.LogInformation("寻卡成功");

                        // 步骤 3: 选卡
                        byte[] manaMsg = new byte[32];
                        var selectResult = IdCardDllWrapper.SDT_SelectIDCard(_openedPort, manaMsg, 0);
                        if (!IdCardDllWrapper.IsSdtSuccess(selectResult))
                        {
                            _logger.LogWarning($"选卡失败: {IdCardDllWrapper.GetErrorMessage(selectResult)}");
                            return new IdCardInfo
                            {
                                Success = false,
                                Message = $"选卡失败: {IdCardDllWrapper.GetErrorMessage(selectResult)}"
                            };
                        }

                        // 步骤 4: 读取中文和原始照片数据
                        byte[] chMsg = new byte[256];
                        uint chLen = (uint)chMsg.Length;
                        byte[] phMsg = new byte[1024];
                        uint phLen = (uint)phMsg.Length;
                        var readResult = IdCardDllWrapper.SDT_ReadBaseMsg(
                            _openedPort, chMsg, ref chLen, phMsg, ref phLen, 0);

                        if (!IdCardDllWrapper.IsSdtSuccess(readResult))
                        {
                            _logger.LogWarning($"读取基本信息失败: {IdCardDllWrapper.GetErrorMessage(readResult)}");
                            return new IdCardInfo
                            {
                                Success = false,
                                Message = $"读取基本信息失败: {IdCardDllWrapper.GetErrorMessage(readResult)}"
                            };
                        }

                        // 步骤 5: 解析中文区
                        var parsed = ParseChineseMessage(chMsg, (int)chLen);

                        // 步骤 6: 解码照片 (可选)
                        string? photoBase64 = null;
                        try
                        {
                            // AI辅助生成：OpenAI Codex（GPT-5）, 2026-04-12
                            // 照片解码失败不影响基础身份信息返回，保证读卡主流程不中断
                            byte[] bgrData = new byte[102 * 126 * 3];
                            var decodeResult = IdCardDllWrapper.unpack(phMsg, bgrData, 0);
                            if (decodeResult == IdCardDllWrapper.DECODE_SUCCESS)
                            {
                                var bmp = BuildBmpFromBgr(bgrData, 102, 126);
                                photoBase64 = Convert.ToBase64String(bmp);
                                _logger.LogInformation("照片解码成功");
                            }
                            else
                            {
                                _logger.LogWarning($"照片解码失败: {IdCardDllWrapper.GetErrorMessage(decodeResult)}。请确认 license.dat 在运行目录");
                            }
                        }
                        catch (DllNotFoundException)
                        {
                            _logger.LogWarning("未找到 DLL_File.dll，跳过照片解码");
                        }
                        catch (Exception ex)
                        {
                            _logger.LogWarning($"照片处理失败: {ex.Message}");
                        }

                        // AI辅助生成：OpenAI Codex（GPT-5）, 2026-04-12
                        // 组合成卡面预览图，便于前端直接展示读卡结果而不是只看文本字段
                        var idCardImageBase64 = BuildIdCardPreviewDataUrl(parsed, photoBase64);

                        var cardInfo = new IdCardInfo
                        {
                            Success = true,
                            Message = "读卡成功",
                            Name = parsed.Name,
                            Gender = parsed.Gender,
                            Nationality = parsed.Nationality,
                            IdNumber = parsed.IdNumber,
                            DateOfBirth = parsed.DateOfBirth,
                            Address = parsed.Address,
                            IssuingAuthority = parsed.IssuingAuthority,
                            ValidFrom = parsed.ValidFrom,
                            ValidTo = parsed.ValidTo,
                            PhotoBase64 = photoBase64,
                            IdCardImageBase64 = idCardImageBase64,
                            ReadTime = DateTime.Now
                        };

                        _logger.LogInformation($"读卡成功: {cardInfo.Name} ({cardInfo.IdNumber})");
                        return cardInfo;
                    }
                    catch (Exception ex)
                    {
                        _logger.LogError($"读卡异常: {ex.Message}");
                        return new IdCardInfo
                        {
                            Success = false,
                            Message = $"读卡异常: {ex.Message}"
                        };
                    }
                }
            });
        }

        /// <summary>
        /// 检查读卡器是否连接
        /// </summary>
        public async Task<bool> IsReaderConnectedAsync()
        {
            return await Task.Run(() =>
            {
                lock (_lockObject)
                {
                    return _isConnected || EnsureReaderConnected();
                }
            });
        }

        /// <summary>
        /// 获取当前读卡器状态
        /// </summary>
        public async Task<string> GetReaderStatusAsync()
        {
            return await Task.Run(() =>
            {
                lock (_lockObject)
                {
                    if (_isConnected)
                    {
                        return "已连接 (x86 进程)";
                    }
                    else if (EnsureReaderConnected())
                    {
                        return "已连接 (x86 进程)";
                    }
                    else
                    {
                        return "未连接 - 请检查读卡器硬件连接";
                    }
                }
            });
        }

        /// <summary>
        /// 释放读卡器资源
        /// </summary>
        public void ReleaseReader()
        {
            lock (_lockObject)
            {
                try
                {
                    if (_isConnected)
                    {
                        IdCardDllWrapper.SDT_ClosePort(_openedPort);
                        _isConnected = false;
                        _openedPort = -1;
                        _logger.LogInformation("读卡器已关闭");
                    }
                }
                catch (Exception ex)
                {
                    _logger.LogError($"关闭读卡器失败: {ex.Message}");
                }
            }
        }

        /// <summary>
        /// 内部方法: 确保读卡器已连接
        /// </summary>
        private bool EnsureReaderConnected()
        {
            try
            {
                if (_isConnected)
                    return true;

                // 厂商定义：1001 为 USB，1..16 为 COM 口。
                var candidatePorts = new[] { 1001, 1, 2, 3, 4 };
                foreach (var port in candidatePorts)
                {
                    var result = IdCardDllWrapper.SDT_OpenPort(port);
                    if (IdCardDllWrapper.IsSdtSuccess(result))
                    {
                        _isConnected = true;
                        _openedPort = port;
                        _logger.LogInformation($"读卡器初始化成功 (端口: {(port == 1001 ? "USB" : $"COM{port}")})");
                        return true;
                    }

                    _logger.LogDebug($"端口 {(port == 1001 ? "USB" : $"COM{port}")} 打开失败: {result}");
                }

                _logger.LogWarning("初始化失败：未找到可用 USB/COM 端口");
                return false;
            }
            catch (DllNotFoundException)
            {
                _logger.LogError("未找到读卡器 DLL 文件 (sdtapi.dll)");
                return false;
            }
            catch (Exception ex)
            {
                _logger.LogError($"初始化异常: {ex.Message}");
                return false;
            }
        }

        /// <summary>
        private sealed class ParsedCardInfo
        {
            public string? Name { get; init; }
            public string? Gender { get; init; }
            public string? Nationality { get; init; }
            public string? DateOfBirth { get; init; }
            public string? Address { get; init; }
            public string? IdNumber { get; init; }
            public string? IssuingAuthority { get; init; }
            public string? ValidFrom { get; init; }
            public string? ValidTo { get; init; }
        }

        // 按二代证 SDK 常见结构（UTF-16LE）解析中文区字节。
        private static ParsedCardInfo ParseChineseMessage(byte[] buffer, int length)
        {
            var effectiveLength = Math.Min(length, buffer.Length);
            var text = Encoding.Unicode.GetString(buffer, 0, effectiveLength);

            string SafeSlice(int start, int len)
            {
                if (start >= text.Length)
                    return string.Empty;
                var realLen = Math.Min(len, text.Length - start);
                return text.Substring(start, realLen).Trim('\0', ' ');
            }

            var name = SafeSlice(0, 15);
            var sexCode = SafeSlice(15, 1);
            var nationCode = SafeSlice(16, 2);
            var birthRaw = SafeSlice(18, 8);
            var address = SafeSlice(26, 35);
            var idNumber = SafeSlice(61, 18);
            var issue = SafeSlice(79, 15);
            var validFromRaw = SafeSlice(94, 8);
            var validToRaw = SafeSlice(102, 8);

            return new ParsedCardInfo
            {
                Name = name,
                Gender = sexCode == "1" ? "男" : sexCode == "2" ? "女" : sexCode,
                Nationality = ParseNation(nationCode),
                DateOfBirth = ParseDate(birthRaw),
                Address = address,
                IdNumber = idNumber,
                IssuingAuthority = issue,
                ValidFrom = ParseDate(validFromRaw),
                ValidTo = ParseDate(validToRaw)
            };
        }

        /// <summary>
        /// 将民族代码(01-56)转换为民族名称。
        /// </summary>
        private static string ParseNation(string nationCode)
        {
            if (string.IsNullOrWhiteSpace(nationCode))
                return nationCode;

            var map = new Dictionary<string, string>
            {
                ["01"] = "汉族", ["02"] = "蒙古族", ["03"] = "回族", ["04"] = "藏族", ["05"] = "维吾尔族", ["06"] = "苗族",
                ["07"] = "彝族", ["08"] = "壮族", ["09"] = "布依族", ["10"] = "朝鲜族", ["11"] = "满族", ["12"] = "侗族",
                ["13"] = "瑶族", ["14"] = "白族", ["15"] = "土家族", ["16"] = "哈尼族", ["17"] = "哈萨克族", ["18"] = "傣族",
                ["19"] = "黎族", ["20"] = "傈僳族", ["21"] = "佤族", ["22"] = "畲族", ["23"] = "高山族", ["24"] = "拉祜族",
                ["25"] = "水族", ["26"] = "东乡族", ["27"] = "纳西族", ["28"] = "景颇族", ["29"] = "柯尔克孜族", ["30"] = "土族",
                ["31"] = "达斡尔族", ["32"] = "仫佬族", ["33"] = "羌族", ["34"] = "布朗族", ["35"] = "撒拉族", ["36"] = "毛南族",
                ["37"] = "仡佬族", ["38"] = "锡伯族", ["39"] = "阿昌族", ["40"] = "普米族", ["41"] = "塔吉克族", ["42"] = "怒族",
                ["43"] = "乌孜别克族", ["44"] = "俄罗斯族", ["45"] = "鄂温克族", ["46"] = "崩龙族", ["47"] = "保安族", ["48"] = "裕固族",
                ["49"] = "京族", ["50"] = "塔塔尔族", ["51"] = "独龙族", ["52"] = "鄂伦春族", ["53"] = "赫哲族", ["54"] = "门巴族",
                ["55"] = "珞巴族", ["56"] = "基诺族",
            };

            var code = nationCode.Trim();
            return map.TryGetValue(code, out var nation) ? nation : nationCode;
        }

        private static byte[] BuildBmpFromBgr(byte[] bgr, int width, int height)
        {
            var srcStride = width * 3;
            var dstStride = ((srcStride + 3) / 4) * 4;
            var imageSize = dstStride * height;
            var fileSize = 54 + imageSize;
            var bmp = new byte[fileSize];

            bmp[0] = (byte)'B';
            bmp[1] = (byte)'M';
            BitConverter.GetBytes(fileSize).CopyTo(bmp, 2);
            BitConverter.GetBytes(54).CopyTo(bmp, 10);
            BitConverter.GetBytes(40).CopyTo(bmp, 14);
            BitConverter.GetBytes(width).CopyTo(bmp, 18);
            BitConverter.GetBytes(-height).CopyTo(bmp, 22);
            BitConverter.GetBytes((short)1).CopyTo(bmp, 26);
            BitConverter.GetBytes((short)24).CopyTo(bmp, 28);
            BitConverter.GetBytes(imageSize).CopyTo(bmp, 34);

            for (var y = 0; y < height; y++)
            {
                var srcOffset = (height - 1 - y) * srcStride;
                var dstOffset = 54 + y * dstStride;
                Array.Copy(bgr, srcOffset, bmp, dstOffset, srcStride);
            }

            return bmp;
        }

                // 芯片里没有整张卡面照片，这里生成一张整卡预览图供前端展示。
                private static string BuildIdCardPreviewDataUrl(ParsedCardInfo parsed, string? photoBase64)
                {
                        var photoSrc = string.IsNullOrWhiteSpace(photoBase64)
                                ? string.Empty
                                : $"data:image/bmp;base64,{photoBase64}";

                        string Esc(string? value)
                        {
                                if (string.IsNullOrEmpty(value)) return string.Empty;
                                return value
                                        .Replace("&", "&amp;")
                                        .Replace("<", "&lt;")
                                        .Replace(">", "&gt;")
                                        .Replace("\"", "&quot;")
                                        .Replace("'", "&#39;");
                        }

                        var name = Esc(parsed.Name);
                        var gender = Esc(parsed.Gender);
                        var nation = Esc(parsed.Nationality);
                        var birth = Esc(parsed.DateOfBirth);
                        var address = Esc(parsed.Address);
                        var idNumber = Esc(parsed.IdNumber);
                        var issue = Esc(parsed.IssuingAuthority);
                        var validPeriod = Esc($"{parsed.ValidFrom ?? string.Empty} - {parsed.ValidTo ?? string.Empty}");

                        var svg = $@"<svg xmlns='http://www.w3.org/2000/svg' width='720' height='454' viewBox='0 0 720 454'>
    <defs>
        <linearGradient id='bg' x1='0' y1='0' x2='1' y2='1'>
            <stop offset='0%' stop-color='#f6ece0'/>
            <stop offset='100%' stop-color='#eacfae'/>
        </linearGradient>
    </defs>
    <rect x='2' y='2' width='716' height='450' rx='26' fill='url(#bg)' stroke='#b77f42' stroke-width='4'/>
    <text x='360' y='62' text-anchor='middle' font-size='34' font-family='Microsoft YaHei, SimHei, sans-serif' fill='#8b3d1a'>中华人民共和国居民身份证</text>
    <rect x='500' y='112' width='176' height='220' rx='10' fill='#fff8ef' stroke='#c59a64'/>
    {(string.IsNullOrWhiteSpace(photoSrc) ? "" : $"<image href='{photoSrc}' x='509' y='121' width='158' height='202' preserveAspectRatio='xMidYMid slice'/>")}  
    <text x='74' y='128' font-size='28' font-family='Microsoft YaHei, SimHei, sans-serif' fill='#5a2d00'>姓名  {name}</text>
    <text x='74' y='172' font-size='25' font-family='Microsoft YaHei, SimHei, sans-serif' fill='#5a2d00'>性别  {gender}    民族  {nation}</text>
    <text x='74' y='216' font-size='25' font-family='Microsoft YaHei, SimHei, sans-serif' fill='#5a2d00'>出生  {birth}</text>
    <text x='74' y='260' font-size='24' font-family='Microsoft YaHei, SimHei, sans-serif' fill='#5a2d00'>住址  {address}</text>
    <text x='74' y='344' font-size='25' font-family='Consolas, Microsoft YaHei, monospace' fill='#3d2b10'>公民身份号码  {idNumber}</text>
    <text x='74' y='392' font-size='20' font-family='Microsoft YaHei, SimHei, sans-serif' fill='#7a4a18'>签发机关: {issue}</text>
    <text x='74' y='424' font-size='20' font-family='Microsoft YaHei, SimHei, sans-serif' fill='#7a4a18'>有效期限: {validPeriod}</text>
</svg>";

                        var svgBase64 = Convert.ToBase64String(Encoding.UTF8.GetBytes(svg));
                        return $"data:image/svg+xml;base64,{svgBase64}";
                }

        /// <summary>
        /// 内部方法: 将出生日期从 YYYYMMDD 格式转换为 YYYY-MM-DD
        /// </summary>
        private static string? ParseDate(string dateStr)
        {
            if (string.IsNullOrWhiteSpace(dateStr) || dateStr.Length != 8)
                return dateStr;

            try
            {
                var date = DateTime.ParseExact(dateStr, "yyyyMMdd", CultureInfo.InvariantCulture);
                return date.ToString("yyyy-MM-dd", CultureInfo.InvariantCulture);
            }
            catch
            {
                return dateStr;
            }
        }

        ~IdCardReaderService()
        {
            ReleaseReader();
        }
    }
}
