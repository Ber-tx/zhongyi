using IdCardReaderService.Services;

var builder = WebApplication.CreateBuilder(args);

// 设置为 x86 构建，并配置端口
builder.WebHost.UseUrls("http://127.0.0.1:9009");

// Add services to the container
builder.Services.AddControllers();
builder.Services.AddScoped<IIdCardReaderService, IdCardReaderService.Services.IdCardReaderService>();

// 添加 CORS 支持
builder.Services.AddCors(options =>
{
    options.AddPolicy("LocalOnly", policy =>
    {
        // AI辅助生成：OpenAI Codex（GPT-5）, 2026-04-12
        // 仅放行本机前端和本地调试场景，避免读卡接口被外部页面直接访问
        policy.WithOrigins("http://127.0.0.1", "http://localhost")
              .AllowAnyMethod()
              .AllowAnyHeader();
    });
});

var app = builder.Build();

// 厂商解码库会在当前工作目录查找 license.dat，固定到应用目录可避免路径漂移。
Directory.SetCurrentDirectory(AppContext.BaseDirectory);

app.UseCors("LocalOnly");
app.UseAuthorization();

app.MapControllers();

Console.WriteLine("=== 中医 AI - 身份证读卡服务 (x86) ===");
Console.WriteLine("监听地址: http://127.0.0.1:9009");

app.Run();
