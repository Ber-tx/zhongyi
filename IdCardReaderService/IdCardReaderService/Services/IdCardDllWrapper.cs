using System.Runtime.InteropServices;

namespace IdCardReaderService.Services
{
    /// <summary>
    /// 身份证读卡器 DLL 交互包装类 (x86)
    /// 
    /// 按厂商 HX-FDX3S 开发包定义的 DLL 调用签名。
    /// 依赖文件：sdtapi.dll、DLL_File.dll、license.dat。
    /// </summary>
    public class IdCardDllWrapper
    {
        private const string SDT_DLL = "sdtapi.dll";
        private const string DECODE_DLL = "DLL_File.dll";

        // =================== sdtapi.dll (HX-FDX3S 有驱动) ===================

        /// <summary>
        /// 打开端口。厂商定义：1001 表示 USB，1..16 表示 COM1..COM16。
        /// </summary>
        [DllImport(SDT_DLL, SetLastError = true, CallingConvention = CallingConvention.StdCall)]
        public static extern int SDT_OpenPort(int iPort);

        /// <summary>
        /// 关闭设备端口
        /// </summary>
        [DllImport(SDT_DLL, SetLastError = true, CallingConvention = CallingConvention.StdCall)]
        public static extern int SDT_ClosePort(int iPort);

        /// <summary>
        /// 寻卡
        /// </summary>
        [DllImport(SDT_DLL, SetLastError = true, CallingConvention = CallingConvention.StdCall)]
        public static extern int SDT_StartFindIDCard(int iPort, byte[] pucManaInfo, int iIfOpen);

        /// <summary>
        /// 选卡
        /// </summary>
        [DllImport(SDT_DLL, SetLastError = true, CallingConvention = CallingConvention.StdCall)]
        public static extern int SDT_SelectIDCard(int iPort, byte[] pucManaMsg, int iIfOpen);

        /// <summary>
        /// 读取中文和照片原始数据。
        /// pucCHMsg 通常为 UTF-16LE 编码结构化字段，pucPHMsg 为照片原始数据块。
        /// </summary>
        [DllImport(SDT_DLL, SetLastError = true, CallingConvention = CallingConvention.StdCall)]
        public static extern int SDT_ReadBaseMsg(
            int iPort,
            byte[] pucCHMsg,
            ref uint puiCHMsgLen,
            byte[] pucPHMsg,
            ref uint puiPHMsgLen,
            int iIfOpen);

        /// <summary>
        /// 新版照片解码库函数。
        /// 返回 1 表示成功；依赖当前工作目录存在 license.dat。
        /// </summary>
        [DllImport(DECODE_DLL, SetLastError = true, CallingConvention = CallingConvention.Cdecl)]
        public static extern int unpack(byte[] szSrcWltData, byte[] szDstPicData, int iIsSaveToBmp);

        // =================== 错误码定义 ===================

        public const int SDT_FIND_CARD_SUCCESS = 0x9F; // 寻卡成功（厂商示例）
        public const int SDT_SUCCESS = 0x90;        // 厂商示例中常见成功码
        public const int SDT_SUCCESS_ALT = 0;       // 某些场景会返回 0
        public const int DECODE_SUCCESS = 1;        // unpack 成功
        public const int SDT_NO_CARD = -1;          // 未检测到卡
        public const int SDT_PORT_ERROR = -2;       // 端口错误
        public const int SDT_READ_ERROR = -3;       // 读取错误
        public const int SDT_TIMEOUT = -4;          // 超时
        public const int SDT_DEVICE_NOT_FOUND = -5; // 设备未找到

        /// <summary>
        /// 将错误码转换为可读的错误信息
        /// </summary>
        public static string GetErrorMessage(int errorCode)
        {
            return errorCode switch
            {
                SDT_FIND_CARD_SUCCESS => "寻卡成功",
                SDT_SUCCESS => "操作成功",
                SDT_SUCCESS_ALT => "操作成功",
                DECODE_SUCCESS => "解码成功",
                SDT_NO_CARD => "未检测到身份证",
                SDT_PORT_ERROR => "端口错误或不支持",
                SDT_READ_ERROR => "读取身份证失败",
                SDT_TIMEOUT => "操作超时",
                SDT_DEVICE_NOT_FOUND => "读卡器设备未找到",
                _ => $"未知错误 (错误码: {errorCode}, 0x{errorCode:X})"
            };
        }

        public static bool IsSdtSuccess(int code)
        {
            return code == SDT_SUCCESS || code == SDT_SUCCESS_ALT;
        }

        public static bool IsFindCardSuccess(int code)
        {
            return code == SDT_FIND_CARD_SUCCESS || IsSdtSuccess(code);
        }
    }
}
