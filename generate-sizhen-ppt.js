const pptxgen = require("pptxgenjs");
const React = require("react");
const { renderToStaticMarkup } = require("react-dom/server");
const {
  FaHeartbeat,
  FaRobot,
  FaBalanceScale,
  FaStethoscope,
  FaBrain,
  FaSearch,
  FaFileMedicalAlt,
  FaMicrophoneAlt,
  FaCamera,
  FaBookMedical,
} = require("react-icons/fa");

const pptx = new pptxgen();
pptx.defineLayout({ name: "WIDE_16_9", width: 13.333, height: 7.5 });
pptx.layout = "WIDE_16_9";
pptx.author = "河南大学 · 唐霄";
pptx.company = "河南大学";
pptx.subject = "中国国际大学生创新大赛新医科赛道项目路演";
pptx.title = "四诊合参";
pptx.lang = "zh-CN";
pptx.theme = {
  headFontFace: "Microsoft YaHei",
  bodyFontFace: "Microsoft YaHei",
  lang: "zh-CN",
};

const W = 13.333;
const H = 7.5;
const FONT = "Microsoft YaHei";

const C = {
  primary: "1A8A7A",
  primaryDark: "0D5E52",
  teal2: "0D9488",
  blue: "2563EB",
  purple: "7C3AED",
  bg: "F8FAFC",
  warm: "FFF8F0",
  text: "1E293B",
  sub: "64748B",
  border: "E2E8F0",
  white: "FFFFFF",
  ink: "0F172A",
  dark: "1E293B",
  gold: "FBBF24",
  mint: "99F6E4",
  paleMint: "ECFDF5",
  red: "EF4444",
};

function svgDataUri(Icon, color = C.primary, size = 64) {
  const svg = renderToStaticMarkup(React.createElement(Icon, { color: `#${color}`, size }));
  return `data:image/svg+xml;base64,${Buffer.from(svg, "utf8").toString("base64")}`;
}

function text(slide, value, x, y, w, h, opts = {}) {
  slide.addText(value, {
    x, y, w, h,
    fontFace: FONT,
    margin: opts.margin ?? 0,
    fit: "shrink",
    breakLine: false,
    ...opts,
  });
}

function rect(slide, x, y, w, h, opts = {}) {
  slide.addShape(pptx.ShapeType.rect, {
    x, y, w, h,
    fill: { color: opts.fill ?? C.white, transparency: opts.fillTransparency ?? 0 },
    line: { color: opts.line ?? opts.fill ?? C.border, transparency: opts.lineTransparency ?? 0, width: opts.lineWidth ?? 1 },
    radius: opts.radius ?? 0.06,
    shadow: opts.shadow,
    rotate: opts.rotate,
  });
}

function circle(slide, x, y, d, opts = {}) {
  slide.addShape(pptx.ShapeType.ellipse, {
    x, y, w: d, h: d,
    fill: { color: opts.fill ?? C.white, transparency: opts.fillTransparency ?? 0 },
    line: { color: opts.line ?? opts.fill ?? C.white, transparency: opts.lineTransparency ?? 100, width: opts.lineWidth ?? 1 },
  });
}

function line(slide, x1, y1, x2, y2, opts = {}) {
  slide.addShape(pptx.ShapeType.line, {
    x: x1, y: y1, w: x2 - x1, h: y2 - y1,
    line: {
      color: opts.color ?? C.border,
      transparency: opts.transparency ?? 0,
      width: opts.width ?? 1,
      beginArrowType: opts.beginArrowType,
      endArrowType: opts.endArrowType,
      dash: opts.dash,
    },
  });
}

function icon(slide, Icon, color, x, y, w, h) {
  slide.addImage({ data: svgDataUri(Icon, color, 64), x, y, w, h });
}

function kicker(slide, label, x, y, color, dark = false) {
  circle(slide, x, y + 0.045, 0.085, { fill: color });
  text(slide, label, x + 0.14, y, 2.5, 0.18, {
    fontSize: 8.2,
    bold: true,
    charSpace: 1.3,
    color: dark ? "CBD5E1" : C.sub,
  });
}

function page(slide, n, dark = false) {
  text(slide, `0${n}`, 12.16, 7.05, 0.5, 0.16, {
    fontSize: 8,
    bold: true,
    color: dark ? "64748B" : "94A3B8",
    align: "right",
  });
}

function title(slide, kickerLabel, heading, sub, n, opts = {}) {
  kicker(slide, kickerLabel, 0.68, 0.52, opts.color ?? C.primary, opts.dark);
  text(slide, heading, 0.68, 0.88, opts.w ?? 8.3, 0.45, {
    fontSize: opts.size ?? 27,
    bold: true,
    color: opts.dark ? C.white : C.text,
  });
  if (sub) {
    text(slide, sub, 0.7, 1.42, opts.sw ?? 7.7, 0.22, {
      fontSize: 10.8,
      color: opts.dark ? "CBD5E1" : C.sub,
    });
  }
  page(slide, n, opts.dark);
}

function softShadow() {
  return { type: "outer", color: "64748B", opacity: 0.16, blur: 1.4, angle: 45, distance: 1.1 };
}

function addFineGrid(slide, color = "FFFFFF", transparency = 93) {
  for (let i = 0; i < 13; i++) line(slide, i + 0.2, 0.1, i + 0.2, H - 0.1, { color, transparency, width: 0.35 });
  for (let j = 0; j < 7; j++) line(slide, 0.15, j + 0.25, W - 0.15, j + 0.25, { color, transparency, width: 0.35 });
}

function addAiTcmOrb(slide, cx, cy, scale = 1) {
  const d = 2.45 * scale;
  circle(slide, cx - d / 2, cy - d / 2, d, { fill: C.primary, fillTransparency: 10, line: C.mint, lineTransparency: 35, lineWidth: 1 });
  circle(slide, cx - 0.86 * scale, cy - 0.86 * scale, 1.72 * scale, { fill: C.ink, fillTransparency: 18, line: C.mint, lineTransparency: 70 });
  circle(slide, cx - 0.42 * scale, cy - 0.42 * scale, 0.84 * scale, { fill: C.blue, fillTransparency: 8, line: C.white, lineTransparency: 60 });
  for (let i = 0; i < 10; i++) {
    const a = (Math.PI * 2 * i) / 10;
    const r1 = 0.92 * scale;
    const r2 = 1.18 * scale;
    const x1 = cx + Math.cos(a) * r1;
    const y1 = cy + Math.sin(a) * r1;
    const x2 = cx + Math.cos(a) * r2;
    const y2 = cy + Math.sin(a) * r2;
    line(slide, x1, y1, x2, y2, { color: C.mint, transparency: 38, width: 0.7 });
    circle(slide, x2 - 0.035 * scale, y2 - 0.035 * scale, 0.07 * scale, { fill: C.mint, fillTransparency: 15 });
  }
  text(slide, "AI", cx - 0.3 * scale, cy - 0.25 * scale, 0.6 * scale, 0.24 * scale, {
    fontSize: 20 * scale,
    bold: true,
    color: C.white,
    align: "center",
    margin: 0,
  });
  text(slide, "TCM", cx - 0.44 * scale, cy + 0.18 * scale, 0.88 * scale, 0.18 * scale, {
    fontSize: 9 * scale,
    bold: true,
    color: C.mint,
    align: "center",
    margin: 0,
  });
}

async function main() {
  // 01 Cover: competition-style big thesis + single premium visual
  {
    const slide = pptx.addSlide();
    slide.background = { color: C.primaryDark };
    addFineGrid(slide, "FFFFFF", 94);
    rect(slide, 0, 0, W, H, { fill: C.primaryDark, lineTransparency: 100 });
    circle(slide, -1.05, -1.2, 3.4, { fill: C.white, fillTransparency: 94 });
    circle(slide, 9.35, -0.65, 5.4, { fill: C.blue, fillTransparency: 88, line: C.mint, lineTransparency: 80 });
    circle(slide, 10.08, 4.9, 2.7, { fill: C.mint, fillTransparency: 92 });
    for (let i = 0; i < 7; i++) {
      line(slide, 8.1 + i * 0.32, 5.98 - i * 0.18, 10.1 + i * 0.24, 5.05 - i * 0.12, { color: C.mint, transparency: 66, width: 0.8 });
    }
    addAiTcmOrb(slide, 10.95, 2.65, 1.12);

    text(slide, "四诊合参", 0.76, 1.34, 4.7, 0.78, {
      fontSize: 48,
      bold: true,
      color: C.white,
    });
    line(slide, 0.82, 2.4, 3.58, 2.4, { color: C.mint, width: 1.3, transparency: 8 });
    line(slide, 0.82, 2.57, 2.0, 2.57, { color: C.blue, width: 2.3, transparency: 0 });
    text(slide, "基于多模态 AI 与检索增强推理的\n中医辅助诊断系统", 0.8, 2.88, 6.2, 0.7, {
      fontSize: 19,
      bold: true,
      color: "DDFCF4",
      breakLine: false,
      fit: "shrink",
      paraSpaceAfterPt: 3,
    });
    rect(slide, 0.82, 4.3, 3.15, 0.42, { fill: C.white, fillTransparency: 91, line: C.mint, lineTransparency: 60 });
    text(slide, "中国国际大学生创新大赛 · 新医科赛道", 1.03, 4.42, 2.74, 0.13, {
      fontSize: 8.5,
      bold: true,
      color: "E6FFFA",
      align: "center",
    });
    text(slide, "河南大学 · 软件学院  |  申报人：唐霄  |  指导教师：陈磊", 0.82, 6.28, 6.8, 0.22, {
      fontSize: 10.2,
      color: "CCFBF1",
    });
    text(slide, "PROJECT ROADSHOW", 10.38, 5.82, 1.95, 0.16, {
      fontSize: 7.8,
      bold: true,
      color: C.mint,
      charSpace: 1.4,
      align: "center",
    });
    page(slide, 1, true);
  }

  // 02 Origin story: emotional trigger, giant 60-year evidence
  {
    const slide = pptx.addSlide();
    slide.background = { color: C.warm };
    rect(slide, 0, 0, 0.34, H, { fill: C.primary, lineTransparency: 100 });
    circle(slide, 9.85, -0.55, 2.6, { fill: C.primary, fillTransparency: 92 });
    circle(slide, 10.9, 5.55, 1.65, { fill: C.blue, fillTransparency: 93 });
    kicker(slide, "WHY WE STARTED", 0.74, 0.55, C.primary);
    text(slide, "不是从模型开始，而是从一次告别开始。", 0.74, 0.95, 8.6, 0.45, {
      fontSize: 26,
      bold: true,
      color: C.text,
    });

    text(slide, "60", 0.78, 2.05, 2.16, 0.78, {
      fontSize: 58,
      bold: true,
      color: C.primary,
    });
    text(slide, "年经验", 2.55, 2.41, 1.25, 0.25, {
      fontSize: 15,
      bold: true,
      color: C.primaryDark,
    });
    line(slide, 0.84, 3.08, 3.75, 3.08, { color: C.primary, width: 1.4, transparency: 15 });
    text(slide, "带不走，也传不下", 0.84, 3.38, 3.1, 0.3, {
      fontSize: 17,
      bold: true,
      color: C.text,
    });
    text(slide, "一个县城老中医退休后留下的问题", 0.86, 3.84, 3.2, 0.2, {
      fontSize: 10.4,
      color: C.sub,
    });

    rect(slide, 4.55, 1.86, 7.35, 3.68, {
      fill: C.white,
      fillTransparency: 10,
      line: "F3E7D6",
      shadow: { type: "outer", color: "B45309", opacity: 0.09, blur: 1.2, angle: 45, distance: 1.0 },
    });
    text(slide, "“", 4.83, 2.02, 0.34, 0.42, { fontSize: 38, bold: true, color: C.primary, margin: 0 });
    const story = "我的外公是一位在县城工作了大半辈子的老中医。\n他常说，学中医最难的不是背书，而是“看”。\n看了大半辈子舌苔，带了几十个徒弟，\n每个徒弟出师至少要跟诊三年。\n\n去年他退休了。60 年的中医诊断经验，带不走，也传不下。";
    text(slide, story, 5.22, 2.18, 5.95, 2.42, {
      fontSize: 17.2,
      color: C.text,
      breakLine: false,
      paraSpaceAfterPt: 6,
      fit: "shrink",
    });
    text(slide, "能不能用 AI，把老中医“看”的能力留下来？", 5.22, 4.86, 5.7, 0.28, {
      fontSize: 17,
      bold: true,
      italic: true,
      color: C.primary,
      fit: "shrink",
    });
    page(slide, 2);
  }

  // 03 Pain: memorable three-one proof board
  {
    const slide = pptx.addSlide();
    slide.background = { color: C.bg };
    title(slide, "MARKET PAIN", "中医诊断卡在三个“一”上", "不是没有需求，而是诊断能力、设备成本和可信工具之间出现断层。", 3);

    const items = [
      {
        num: "80%",
        label: "基层缺诊断",
        desc: "县级以下机构缺少能独立开展四诊辨证论治的执业医师",
        icon: FaHeartbeat,
        color: C.primary,
      },
      {
        num: "<500元",
        label: "必须低成本",
        desc: "主流设备 3-100 万元/套，难以下沉到基层真实场景",
        icon: FaRobot,
        color: C.blue,
      },
      {
        num: "12亿",
        label: "年诊疗人次",
        desc: "高频诊疗需求下，AI 辅助诊断工具仍接近空白",
        icon: FaBalanceScale,
        color: C.purple,
      },
    ];
    line(slide, 1.08, 3.4, 12.1, 3.4, { color: C.border, width: 1.1 });
    items.forEach((it, i) => {
      const cx = 2.35 + i * 4.25;
      circle(slide, cx - 0.66, 2.74, 1.32, { fill: C.white, line: it.color, lineTransparency: 15, lineWidth: 1.2 });
      circle(slide, cx - 0.46, 2.94, 0.92, { fill: it.color, fillTransparency: 90 });
      icon(slide, it.icon, it.color, cx - 0.2, 3.2, 0.4, 0.4);
      rect(slide, cx - 1.38, 4.2, 2.76, 1.18, { fill: C.white, line: C.border, shadow: softShadow() });
      rect(slide, cx - 1.38, 4.2, 2.76, 0.06, { fill: it.color, lineTransparency: 100 });
      text(slide, it.num, cx - 1.12, 1.86, 2.24, 0.48, {
        fontSize: 33,
        bold: true,
        color: it.color,
        align: "center",
      });
      text(slide, it.label, cx - 1.08, 4.44, 2.16, 0.22, {
        fontSize: 14.2,
        bold: true,
        color: C.text,
        align: "center",
      });
      text(slide, it.desc, cx - 1.04, 4.86, 2.08, 0.28, {
        fontSize: 9.2,
        color: C.sub,
        align: "center",
        breakLine: false,
        fit: "shrink",
      });
    });
    rect(slide, 0.72, 6.2, 11.86, 0.4, { fill: "EEF6F4", line: "D7EDE8" });
    text(slide, "结论：基层需要的不是昂贵大设备，而是一套可部署、可解释、可追溯的四诊辅助诊断系统。", 1.02, 6.33, 11.25, 0.11, {
      fontSize: 9.6,
      bold: true,
      color: C.primaryDark,
      align: "center",
    });
    text(slide, "数据来源：国家中医药管理局、中国健康管理协会及公开行业资料", 0.75, 6.88, 4.7, 0.14, {
      fontSize: 7.6,
      color: "94A3B8",
    });
  }

  // 04 Timing: three phases with a high-contrast turning point
  {
    const slide = pptx.addSlide();
    slide.background = { color: C.dark };
    addFineGrid(slide, "FFFFFF", 96);
    circle(slide, -0.95, 5.15, 2.5, { fill: C.primary, fillTransparency: 89 });
    circle(slide, 10.2, -1.2, 4.1, { fill: C.blue, fillTransparency: 90 });
    title(slide, "WHY NOW", "为什么是现在？", "算法可用、推理可信、政策与产业场景同时到位。", 4, { dark: true, color: C.blue });

    const eras = [
      {
        year: "2024 以前",
        badge: "做不了",
        color: "94A3B8",
        lines: ["舌诊精度不够临床不可用", "大模型易编造诊断依据", "缺少可商业化部署路径"],
      },
      {
        year: "2024—2025",
        badge: "条件成熟",
        color: C.primary,
        lines: ["YOLOv8 mAP 提升进入实用区间", "RAG 让结论可追溯、可核验", "中医药振兴资金与基层需求落地"],
      },
      {
        year: "现在",
        badge: "我们能做",
        color: C.blue,
        lines: ["自训练模型输出 20 维舌象指标", "本地知识库推理，每条结论带依据", "与器械公司合作，真实场景可部署"],
      },
    ];
    eras.forEach((era, i) => {
      const x = 0.78 + i * 4.16;
      rect(slide, x, 2.02, 3.56, 4.22, {
        fill: i === 2 ? "0B1F44" : C.ink,
        line: i === 2 ? C.blue : "334155",
        lineTransparency: i === 2 ? 0 : 20,
        shadow: { type: "outer", color: "000000", opacity: 0.24, blur: 1.4, angle: 45, distance: 1.1 },
      });
      rect(slide, x, 2.02, 3.56, 0.08, { fill: era.color, lineTransparency: 100 });
      text(slide, era.year, x + 0.34, 2.48, 1.78, 0.24, {
        fontSize: 15.5,
        bold: true,
        color: era.color,
      });
      rect(slide, x + 2.26, 2.43, 0.92, 0.34, {
        fill: era.color,
        fillTransparency: 84,
        line: era.color,
        lineTransparency: 55,
      });
      text(slide, era.badge, x + 2.26, 2.54, 0.92, 0.11, {
        fontSize: 8.2,
        bold: true,
        color: era.color,
        align: "center",
      });
      era.lines.forEach((l, j) => {
        const y = 3.34 + j * 0.78;
        circle(slide, x + 0.38, y + 0.06, 0.08, { fill: era.color });
        text(slide, l, x + 0.58, y - 0.02, 2.72, 0.26, {
          fontSize: 10.8,
          color: "E2E8F0",
          fit: "shrink",
        });
      });
    });
    line(slide, 4.42, 4.15, 4.72, 4.15, { color: "64748B", width: 1.1, endArrowType: "triangle" });
    line(slide, 8.58, 4.15, 8.88, 4.15, { color: C.blue, width: 1.4, endArrowType: "triangle" });
    page(slide, 4, true);
  }

  // 05 Solution: architecture, not a generic process
  {
    const slide = pptx.addSlide();
    slide.background = { color: C.bg };
    title(slide, "OUR SOLUTION", "我们的解法", "将四诊数字化，让每一份诊断都有据可查", 5);

    const xs = [1.05, 3.98, 7.0, 9.98];
    const colors = [C.primary, C.teal2, C.blue, C.purple];
    const heads = ["多模态数据采集", "AI 特征提取", "RAG 知识检索", "综合推理生成报告"];
    const descs = [
      "摄像头·麦克风\n传感器·问卷",
      "YOLOv8 舌诊20维\n音频·问卷·脉搏",
      "《中医诊断学》向量化\n检索辨证依据",
      "Agent 自动编排\n输出带引文的诊断",
    ];
    const icons = [FaCamera, FaBrain, FaBookMedical, FaFileMedicalAlt];

    // central backbone
    line(slide, 1.76, 3.74, 11.36, 3.74, { color: "CBD5E1", width: 1.1 });
    xs.forEach((x, i) => {
      const color = colors[i];
      circle(slide, x + 0.48, 2.5, 1.08, { fill: color, fillTransparency: 88, line: color, lineTransparency: 10, lineWidth: 1.1 });
      circle(slide, x + 0.62, 2.64, 0.8, { fill: C.white, line: color, lineTransparency: 25 });
      icon(slide, icons[i], color, x + 0.82, 2.84, 0.38, 0.38);
      circle(slide, x + 0.92, 3.62, 0.24, { fill: color });
      text(slide, String(i + 1), x + 0.92, 3.69, 0.24, 0.06, {
        fontSize: 7.2,
        bold: true,
        color: C.white,
        align: "center",
        margin: 0,
      });
      rect(slide, x, 4.18, 2.42, 1.22, { fill: C.white, line: C.border, shadow: softShadow() });
      rect(slide, x, 4.18, 2.42, 0.06, { fill: color, lineTransparency: 100 });
      text(slide, heads[i], x + 0.22, 4.46, 1.98, 0.2, {
        fontSize: 12.1,
        bold: true,
        color: C.text,
        align: "center",
      });
      text(slide, descs[i], x + 0.24, 4.84, 1.94, 0.34, {
        fontSize: 8.9,
        color: C.sub,
        align: "center",
        breakLine: false,
        paraSpaceAfterPt: 2,
        fit: "shrink",
      });
      if (i < 3) {
        line(slide, x + 2.2, 3.74, xs[i + 1] + 0.08, 3.74, { color: colors[i + 1], width: 1.35, transparency: 20, endArrowType: "triangle" });
      }
    });
    rect(slide, 4.78, 1.87, 3.74, 0.55, { fill: C.ink, line: C.blue, lineTransparency: 40 });
    text(slide, "多模态 AI × 可追溯 RAG × 临床低成本部署", 5.05, 2.07, 3.2, 0.13, {
      fontSize: 9.8,
      bold: true,
      color: C.white,
      align: "center",
    });
    line(slide, 6.65, 2.42, 6.65, 3.42, { color: C.blue, width: 1.0, transparency: 30, dash: "dash" });

    rect(slide, 0.76, 6.2, 11.82, 0.54, { fill: C.paleMint, line: "CCFBF1" });
    text(slide, "整套硬件成本 < 500元    |    部署时间 < 10分钟    |    每个诊断结论附带文献出处", 1.0, 6.4, 11.35, 0.1, {
      fontSize: 10.8,
      bold: true,
      color: C.primaryDark,
      align: "center",
    });
  }

  await pptx.writeFile({ fileName: "四诊合参_路演前5页_省金国金风格.pptx" });
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
