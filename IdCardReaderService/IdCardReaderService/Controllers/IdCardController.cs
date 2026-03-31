using Microsoft.AspNetCore.Mvc;
using IdCardReaderService.Models;
using IdCardReaderService.Services;

namespace IdCardReaderService.Controllers
{
    /// <summary>
    /// 身份证读卡 API 控制器
    /// 本地 HTTP 接口，供后端服务调用
    /// </summary>
    [ApiController]
    [Route("api/[controller]")]
    public class IdCardController : ControllerBase
    {
        private readonly IIdCardReaderService _readerService;
        private readonly ILogger<IdCardController> _logger;

        public IdCardController(IIdCardReaderService readerService, ILogger<IdCardController> logger)
        {
            _readerService = readerService;
            _logger = logger;
        }

        /// <summary>
        /// 读取身份证信息
        /// GET /api/idcard/read
        /// </summary>
        [HttpGet("read")]
        public async Task<ActionResult<ApiResponse<IdCardInfo>>> Read()
        {
            try
            {
                _logger.LogInformation("收到读卡请求");
                var result = await _readerService.ReadIdCardAsync();
                
                return Ok(new ApiResponse<IdCardInfo>
                {
                    Success = result.Success,
                    Message = result.Message,
                    Data = result
                });
            }
            catch (Exception ex)
            {
                _logger.LogError($"读卡API异常: {ex.Message}");
                return StatusCode(500, new ApiResponse<IdCardInfo>
                {
                    Success = false,
                    Message = $"服务异常: {ex.Message}"
                });
            }
        }

        /// <summary>
        /// 检查读卡器状态
        /// GET /api/idcard/status
        /// </summary>
        [HttpGet("status")]
        public async Task<ActionResult<ApiResponse<object>>> Status()
        {
            try
            {
                var isConnected = await _readerService.IsReaderConnectedAsync();
                var statusMsg = await _readerService.GetReaderStatusAsync();

                return Ok(new ApiResponse<object>
                {
                    Success = true,
                    Message = statusMsg,
                    Data = new
                    {
                        connected = isConnected,
                        status = statusMsg,
                        timestamp = DateTime.Now
                    }
                });
            }
            catch (Exception ex)
            {
                _logger.LogError($"状态检查异常: {ex.Message}");
                return StatusCode(500, new ApiResponse<object>
                {
                    Success = false,
                    Message = $"服务异常: {ex.Message}"
                });
            }
        }

        /// <summary>
        /// 健康检查接口
        /// GET /api/idcard/health
        /// </summary>
        [HttpGet("health")]
        public ActionResult<ApiResponse<object>> Health()
        {
            return Ok(new ApiResponse<object>
            {
                Success = true,
                Message = "身份证读卡服务运行正常 (x86)",
                Data = new
                {
                    version = "1.0.0",
                    framework = "ASP.NET Core 8.0 x86",
                    platform = Environment.OSVersion.VersionString,
                    timestamp = DateTime.Now
                }
            });
        }

        /// <summary>
        /// 释放读卡器资源
        /// POST /api/idcard/release
        /// </summary>
        [HttpPost("release")]
        public ActionResult<ApiResponse<object>> Release()
        {
            try
            {
                _readerService.ReleaseReader();
                return Ok(new ApiResponse<object>
                {
                    Success = true,
                    Message = "读卡器已释放"
                });
            }
            catch (Exception ex)
            {
                return StatusCode(500, new ApiResponse<object>
                {
                    Success = false,
                    Message = $"释放失败: {ex.Message}"
                });
            }
        }
    }
}
