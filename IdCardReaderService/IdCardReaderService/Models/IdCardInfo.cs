namespace IdCardReaderService.Models
{
    /// <summary>
    /// 身份证读卡结果数据模型
    /// </summary>
    public class IdCardInfo
    {
        /// <summary>
        /// 是否成功读卡
        /// </summary>
        public bool Success { get; set; }

        /// <summary>
        /// 错误信息
        /// </summary>
        public string? Message { get; set; }

        /// <summary>
        /// 身份证号码
        /// </summary>
        public string? IdNumber { get; set; }

        /// <summary>
        /// 姓名
        /// </summary>
        public string? Name { get; set; }

        /// <summary>
        /// 性别 (M/F)
        /// </summary>
        public string? Gender { get; set; }

        /// <summary>
        /// 民族代码
        /// </summary>
        public string? Nationality { get; set; }

        /// <summary>
        /// 出生日期 (YYYY-MM-DD)
        /// </summary>
        public string? DateOfBirth { get; set; }

        /// <summary>
        /// 地址
        /// </summary>
        public string? Address { get; set; }

        /// <summary>
        /// 签发机关
        /// </summary>
        public string? IssuingAuthority { get; set; }

        /// <summary>
        /// 有效期起始 (YYYY-MM-DD)
        /// </summary>
        public string? ValidFrom { get; set; }

        /// <summary>
        /// 有效期终止 (YYYY-MM-DD)
        /// </summary>
        public string? ValidTo { get; set; }

        /// <summary>
        /// 原始照片数据 (Base64)
        /// </summary>
        public string? PhotoBase64 { get; set; }

        /// <summary>
        /// 身份证整卡预览图 (Base64 或 data URL)
        /// </summary>
        public string? IdCardImageBase64 { get; set; }

        /// <summary>
        /// 读取时间戳
        /// </summary>
        public DateTime ReadTime { get; set; } = DateTime.Now;
    }

    /// <summary>
    /// API 响应包装类
    /// </summary>
    public class ApiResponse<T>
    {
        public bool Success { get; set; }
        public string? Message { get; set; }
        public T? Data { get; set; }
    }
}
