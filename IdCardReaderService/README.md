# 身份证读卡服务文档

## 项目说明

这是一个 **Windows x86 本地服务**，负责与身份证读卡器硬件通过 DLL 进行交互，并通过本地 HTTP 接口向上层应用暴露读卡能力。

## 架构设计

```
Vue3 前端 (浏览器)
        ↓
    本地网络
        ↓
Spring Boot / Flask 后端 (5000/8080)
        ↓
    本地 HTTP (127.0.0.1:9009)
        ↓
IdCardReaderService (x86, ASP.NET 6.0)
        ↓
    P/Invoke 调用 (DLL 交互)
        ↓
读卡器驱动 DLL (sdtapi.dll / BmID.dll / 等)
        ↓
    硬件
        ↓
身份证读卡器设备
```

## 构建和运行

### 环境要求
- Windows 7/8/10/11 (x86 支持)
- .NET 6.0 Runtime (x86 版本)
- 身份证读卡器驱动 + DLL 文件

### 构建 (仅适用于已安装 .NET 编译环境的开发机)
```bash
cd IdCardReaderService
dotnet build -c Release -r win-x86
```

### 编译后运行
```bash
dotnet run --project IdCardReaderService
```

### 使用预编译的发布版本
如果已生成发布包：
```bash
# 进入发布目录
cd bin/Release/net6.0/win-x86/publish

# 运行服务
./IdCardReaderService.exe
```

## API 接口

所有接口基址：`http://127.0.0.1:9009`

### 1. 读取身份证信息
**请求：**
```
GET /api/idcard/read
```

**响应示例 (成功)：**
```json
{
  "success": true,
  "message": "读卡成功",
  "data": {
    "idNumber": "110101199001011234",
    "name": "张三",
    "gender": "M",
    "nationality": "汉",
    "dateOfBirth": "1990-01-01",
    "address": "北京市朝阳区某街道123号",
    "issuingAuthority": "北京市朝阳区公安局",
    "validFrom": "2015-01-20",
    "validTo": "2025-01-20",
    "photoBase64": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
    "readTime": "2024-01-15T14:30:00"
  }
}
```

**响应示例 (失败)：**
```json
{
  "success": false,
  "message": "未检测到身份证",
  "data": null
}
```

### 2. 检查读卡器状态
**请求：**
```
GET /api/idcard/status
```

**响应：**
```json
{
  "success": true,
  "message": "已连接 (x86 进程)",
  "data": {
    "connected": true,
    "status": "已连接 (x86 进程)",
    "timestamp": "2024-01-15T14:30:00"
  }
}
```

### 3. 健康检查
**请求：**
```
GET /api/idcard/health
```

**响应：**
```json
{
  "success": true,
  "message": "身份证读卡服务运行正常 (x86)",
  "data": {
    "version": "1.0.0",
    "framework": "ASP.NET Core 6.0 x86",
    "platform": "Microsoft Windows NT 10.0.19045.0",
    "timestamp": "2024-01-15T14:30:00"
  }
}
```

### 4. 释放读卡器资源
**请求：**
```
POST /api/idcard/release
```

**响应：**
```json
{
  "success": true,
  "message": "读卡器已释放"
}
```

## Spring Boot 集成示例

在 Java 后端调用该服务：

```java
@GetMapping("/api/patient/read-idcard")
public ResponseEntity<?> readIdCard() {
    try {
        // 调用本地读卡服务
        String url = "http://127.0.0.1:9009/api/idcard/read";
        RestTemplate restTemplate = new RestTemplate();
        ResponseEntity<Map> response = restTemplate.getForEntity(url, Map.class);
        
        if (response.getStatusCode() == HttpStatus.OK) {
            Map body = response.getBody();
            if ((Boolean) body.get("success")) {
                Map data = (Map) body.get("data");
                // 处理身份证信息...
                return ResponseEntity.ok(data);
            }
        }
    } catch (Exception e) {
        return ResponseEntity.status(500).body("读卡失败: " + e.getMessage());
    }
    return ResponseEntity.status(500).body("读卡服务不可用");
}
```

## Python (FastAPI) 集成示例

在 Python 后端调用该服务：

```python
import httpx
from fastapi import APIRouter

router = APIRouter()

@router.get("/api/read-idcard")
async def read_idcard():
    """
    从本地 x86 读卡服务读取身份证信息
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://127.0.0.1:9009/api/idcard/read", timeout=10.0)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    return {"success": True, "data": data.get("data")}
                else:
                    return {"success": False, "message": data.get("message")}
    except Exception as e:
        return {"success": False, "message": f"读卡失败: {str(e)}"}
    
    return {"success": False, "message": "读卡服务不可用"}
```

## DLL 文件配置

### 支持的读卡器类型

| 硬件厂商 | DLL 文件 | 备注 |
|---------|---------|------|
| 申瑞 | sdtapi.dll | **推荐，目前主要使用** |
| 复旦微电子 | BmID.dll | 需在代码中切换调用 |
| 华视 | CVGm64.dll | x86 版本 |

### 配置步骤

1. 从读卡器驱动包中提取相应的 x86 DLL（**必须是 32-bit**）
2. 将 DLL 复制到 `Libs/` 目录
3. 编辑 `Services/IdCardDllWrapper.cs` 中的 `DLL_NAME` 常量选择正确的 DLL
4. 重新编译

### 例如使用复旦 DLL

在 IdCardDllWrapper.cs 中修改：

```csharp
private const string DLL_NAME = "BmID.dll";  // 改为使用复旦 DLL
```

## 故障排除

### 问题：启动时提示 "未找到读卡器 DLL 文件"
**解决方案：**
- 确保 DLL 文件已复制到 `Libs/` 目录或输出目录
- 确保 DLL 是 **x86 (32-bit)** 版本，而不是 x64
- 检查 DLL 名称是否与代码中 `DLL_NAME` 一致

### 问题：运行时提示 "寻卡失败" 或 "端口错误"
**解决方案：**
- 确保读卡器硬件已连接到 USB
- 检查读卡器驱动是否已安装
- 查看系统设备管理器中是否识别了读卡器
- 尝试在另一个 USB 端口

### 问题：读卡成功但数据为乱码
**解决方案：**
- DLL 可能使用了不同的字符编码（GB2312 而非 UTF-8）
- 修改 `IdCardReaderService.cs` 中的编码处理

```csharp
// 改为 GB2312 编码
var name = Encoding.GetEncoding("GB2312").GetString(nameBytes).Trim('\0').Trim();
```

## 部署

### 生产环境部署目录结构
```
/IdCardReaderService/
├── IdCardReaderService.exe         (主应用程序)
├── IdCardReaderService.dll
├── appsettings.json
├── Libs/
│   ├── sdtapi.dll                  (读卡器 DLL)
│   └── (其他必要 DLL)
└── dotnet-runtime/                 (如果是自包含部署)
```

### Windows 服务安装 (可选)

使用 NSSM (Non-Sucking Service Manager) 将其安装为 Windows 后台服务：

```batch
nssm install IdCardReaderService "C:\Path\To\IdCardReaderService.exe"
nssm start IdCardReaderService
```

### 自启动配置

在 Windows 启动时自动启动服务（通过任务计划程序或 VBS 脚本）

## 测试

### 使用 cURL 测试
```bash
# 检查服务状态
curl http://127.0.0.1:9009/api/idcard/health

# 尝试读卡
curl http://127.0.0.1:9009/api/idcard/read

# 检查读卡器连接
curl http://127.0.0.1:9009/api/idcard/status
```

### 使用 Swagger UI
启动服务后访问：`http://127.0.0.1:9009/swagger/index.html`

## 性能考虑

- 每次读卡操作耗时约 1-3 秒（取决于硬件）
- 建议在后端实现缓存或速率限制
- 多个并发读卡请求通过 `lock` 进行序列化处理

## 安全考虑

- 只在 127.0.0.1:9009 本地监听，不暴露到网络
- 在生产环境中，后端服务应与本读卡服务在同一机器上
- 身份证照片数据通过 Base64 编码传输，不加密

## 未来扩展

- [ ] 支持多读卡器并发
- [ ] 智能 COM 端口自动检测
- [ ] 读卡指纹采集
- [ ] WebSocket 实时状态推送
- [ ] 加密传输
