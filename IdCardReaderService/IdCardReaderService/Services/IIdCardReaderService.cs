using IdCardReaderService.Models;

namespace IdCardReaderService.Services
{
    /// <summary>
    /// 身份证读卡器服务接口
    /// </summary>
    public interface IIdCardReaderService
    {
        /// <summary>
        /// 读取身份证信息
        /// </summary>
        Task<IdCardInfo> ReadIdCardAsync();

        /// <summary>
        /// 检查读卡器是否连接
        /// </summary>
        Task<bool> IsReaderConnectedAsync();

        /// <summary>
        /// 获取当前读卡器状态
        /// </summary>
        Task<string> GetReaderStatusAsync();

        /// <summary>
        /// 释放读卡器资源
        /// </summary>
        void ReleaseReader();
    }
}
