const DEFAULT_SCALE_OPTIONS = [
  '没有(根本不)',
  '很少(有一点)',
  '有时(有些)',
  '经常(相当)',
  '总是(非常)',
];

const CHILDREN_SCORE_OPTIONS = [
  { label: '无相关表现（0分）', value: 0 },
  { label: '偶尔轻微，每月1-2次（2分）', value: 2 },
  { label: '经常出现，每周2-3次（4分）', value: 4 },
  { label: '频繁出现，几乎每天（6分）', value: 6 },
];

const CHILDREN_CONSTITUTION_RULES = [
  {
    key: 'ph',
    name: '平和质',
    questionIndexes: [0, 1, 2, 3],
    coreState: '儿童体质均衡，气血充足，脾胃功能正常，生长发育良好，无明显体质偏颇。',
    diet: [
      '保持规律饮食，不挑食、不偏食，均衡摄入蛋白质、维生素、矿物质。',
      '根据年龄段合理添加辅食（0-1岁），循序渐进，贴合儿童消化能力。',
      '避免过度喂养或节食，维持适中食量。',
    ],
    avoid: ['避免熬夜和作息紊乱。', '避免受凉或过热，衣物随天气及时调整。', '避免长期缺少活动。'],
    suggestions: [
      '0-3岁每日睡眠12-14小时，3-6岁每日睡眠10-12小时。',
      '0-1岁可做被动操和翻身练习，1-3岁以爬行走路为主，3-6岁增加跑跳和球类运动。',
      '多陪伴与鼓励交流，营造轻松愉快的成长环境。',
    ],
  },
  {
    key: 'qiXu',
    name: '气虚质',
    questionIndexes: [4, 5, 6, 7],
    coreState: '儿童脾胃虚弱，气血生化不足，易疲劳、易感冒，消化功能欠佳。',
    diet: [
      '侧重健脾益气，多吃山药、薏米、小米、红枣、瘦肉等温和易消化食物。',
      '0-3岁可适当食用小米粥、山药泥等养胃辅食。',
      '少量多餐，减少积食。',
    ],
    avoid: ['避免生冷、油腻、辛辣食物。', '避免过度劳累和剧烈运动。', '避免腹部、背部受凉。'],
    suggestions: [
      '保证充足睡眠并安排15-30分钟午休。',
      '选择散步、慢走、被动操，每周3-4次，每次10-15分钟。',
      '减少人群密集场所暴露，感冒后及时调理，必要时在医生指导下进行食疗。',
    ],
  },
  {
    key: 'yangXu',
    name: '阳虚质',
    questionIndexes: [8, 9, 10, 11],
    coreState: '儿童阳气亏虚，脾胃虚寒，畏寒怕冷，消化功能弱，易腹泻。',
    diet: [
      '侧重温阳散寒、健脾养胃，可选生姜、红枣、小米、南瓜等温热性食物。',
      '羊肉少量食用，结合儿童耐受。',
      '0-3岁婴幼儿避免寒性辅食。',
    ],
    avoid: ['严格控制生冷食物，如冰饮、凉菜、生冷水果。', '避免吹冷风和寒湿环境。', '避免熬夜。'],
    suggestions: [
      '注意全身保暖，尤其腹部和手脚，室内保持温暖干燥。',
      '选择温暖环境下的温和运动，每周3次，每次10分钟。',
      '腹泻及时调理并补水，必要时医生指导下使用温和食疗。',
    ],
  },
  {
    key: 'yinXu',
    name: '阴虚质',
    questionIndexes: [12, 13, 14, 15],
    coreState: '儿童阴液不足，内热偏盛，口干咽燥，易盗汗、便秘。',
    diet: [
      '侧重滋阴清热、生津润燥，可选银耳、百合、莲子、雪梨、冬瓜、绿豆。',
      '少量多次补充温水，避免一次大量饮水。',
      '饮食以清淡为主。',
    ],
    avoid: ['避免辛辣、温热、油炸食物。', '避免高温暴晒和大量出汗。', '避免熬夜。'],
    suggestions: [
      '室内保持适宜湿度，夏季减少高温暴露。',
      '选择凉爽时段进行散步或慢跑，每周3次，每次10-15分钟。',
      '盗汗后及时擦干更衣，便秘时优先膳食纤维调理，避免自行使用泻药。',
    ],
  },
  {
    key: 'tanShi',
    name: '痰湿质',
    questionIndexes: [16, 17, 18, 19],
    coreState: '儿童脾胃运化失常，痰湿内积，体型偏胖，痰多、大便黏腻。',
    diet: [
      '侧重健脾祛湿，可选冬瓜、赤小豆、薏米、山药、芹菜等。',
      '0-3岁婴幼儿辅食以清淡易消化为主，避免过度喂养。',
      '控制总热量，规律进食。',
    ],
    avoid: ['避免油腻、甜食、生冷食物。', '避免暴饮暴食。', '避免久坐久卧。'],
    suggestions: [
      '保持规律作息，室内干燥通风，及时增减衣物。',
      '增加快走、跑跳、游泳等活动，每周4次，每次15-20分钟。',
      '痰多可适当拍背辅助排痰，并保持口腔清洁。',
    ],
  },
  {
    key: 'shiRe',
    name: '湿热质',
    questionIndexes: [20, 21, 22, 23],
    coreState: '儿童湿热内盛，脾胃失调，皮肤易长湿疹，小便发黄，大便黏腻。',
    diet: [
      '侧重清热利湿，可选绿豆、冬瓜、芹菜、西瓜、莲藕。',
      '饮食清淡并适量饮水，促进湿热排出。',
      '减少高糖高脂摄入。',
    ],
    avoid: ['避免油炸、辛辣、甜腻食物。', '避免熬夜。', '避免闷热潮湿环境久留。'],
    suggestions: [
      '保持室内通风干燥，夏季勤洗澡并保持皮肤清洁。',
      '在凉爽时段进行游泳、慢跑、跳绳，每周3-4次，每次15分钟。',
      '湿疹或痱子明显时及时清洁并在医生指导下处理，小便发黄时增加饮水。',
    ],
  },
  {
    key: 'qiYu',
    name: '气郁质',
    questionIndexes: [24, 25, 26, 27],
    coreState: '儿童情志不舒，肝气郁结，易烦躁易怒，睡眠及消化受影响。',
    diet: [
      '侧重疏肝理气、健脾开胃，可选陈皮、玫瑰花（少量）、小米、山药。',
      '保持规律饮食，减少情绪波动引发的进食紊乱。',
      '饮食清淡，避免过饱。',
    ],
    avoid: ['避免辛辣、油腻食物。', '避免过度指责、打骂等情绪刺激。', '避免熬夜。'],
    suggestions: [
      '营造轻松愉快的家庭环境，耐心倾听并引导表达。',
      '选择散步、慢跑、儿童瑜伽，每周3次，每次10-15分钟。',
      '通过讲故事、游戏和集体活动帮助释放情绪。',
    ],
  },
  {
    key: 'xueYu',
    name: '血瘀质',
    questionIndexes: [28, 29, 30, 31],
    coreState: '儿童气血运行不畅，血瘀内停，易出现瘀斑、面色偏暗。',
    diet: [
      '侧重活血化瘀、补气养血，可选黑木耳、洋葱、红枣、菠菜。',
      '适量补充优质蛋白，增强体质。',
      '饮食温和，注意消化负担。',
    ],
    avoid: ['避免生冷、油腻食物。', '避免久坐久卧。', '避免剧烈运动导致外伤。'],
    suggestions: [
      '保证充足睡眠并注意保暖，促进气血运行。',
      '进行散步、慢跑、拉伸，每周3-4次，每次10-15分钟。',
      '瘀斑出现48小时后可适当热敷；若频繁瘀斑建议及时就医排查。',
    ],
  },
  {
    key: 'teBing',
    name: '特禀质',
    questionIndexes: [32, 33, 34, 35],
    coreState: '儿童体质特殊，易过敏、易感冒，对食物和环境敏感。',
    diet: [
      '严格规避明确过敏原并记录过敏食物。',
      '0-3岁饮食宜清淡单一，新食物循序渐进添加并观察反应。',
      '增加富含维生素食物，支持免疫力。',
    ],
    avoid: ['避免接触花粉、尘螨、海鲜、牛奶等已知过敏原。', '避免过敏季节高暴露外出。', '避免作息紊乱导致免疫波动。'],
    suggestions: [
      '室内保持清洁通风，减少尘螨霉菌；外出按需佩戴口罩。',
      '选择室内或空气清新环境进行温和运动，每周3次，每次10分钟。',
      '过敏发作及时就医，按医嘱处理并定期体检监测体质变化。',
    ],
  },
];

const CHILDREN_DOMINANT_ORDER = ['ph', 'qiXu', 'yangXu', 'yinXu', 'tanShi', 'shiRe', 'qiYu', 'xueYu', 'teBing'];

function summarizeAnswers(answers = []) {
  const values = (answers || []).map((value) => Number(value) || 0).filter((value) => value > 0);
  if (!values.length) {
    return { average: 0, highCount: 0, lowCount: 0, total: 0 };
  }

  const total = values.reduce((sum, value) => sum + value, 0);
  return {
    average: total / values.length,
    highCount: values.filter((value) => value >= 4).length,
    lowCount: values.filter((value) => value <= 2).length,
    total,
  };
}

function buildRangeTitle(summary, titles) {
  if (summary.average >= 3.6) return titles.high;
  if (summary.average >= 2.8) return titles.medium;
  return titles.low;
}

function buildRangeSummary(summary, descriptions) {
  if (summary.average >= 3.6) return descriptions.high;
  if (summary.average >= 2.8) return descriptions.medium;
  return descriptions.low;
}

function buildResultBase(title, summary, diet, avoid, suggestions, badge) {
  return {
    kind: 'special',
    title,
    summary,
    diet: [...diet],
    avoid: [...avoid],
    suggestions: [...suggestions],
    badge,
  };
}

function buildHypertensionResult(answers = []) {
  const normalized = (answers || []).map((value) => Number(value) || 0);
  const scoreMap = { ph: 0, qx: 0, yx: 0, ts: 0, sr: 0, xy: 0, tb: 0, qy: 0 };

  const rules = [
    { key: 'qx', indexes: [0, 9, 17] },
    { key: 'yinXu', indexes: [1, 8, 16] },
    { key: 'ph', indexes: [1, 8, 16], reverse: true },
    { key: 'yx', indexes: [2, 10, 18] },
    { key: 'ts', indexes: [3, 11, 14] },
    { key: 'sr', indexes: [4, 12, 19] },
    { key: 'xy', indexes: [5, 13, 20] },
    { key: 'tb', indexes: [6, 21, 22] },
    { key: 'qy', indexes: [7, 15, 23] },
  ];

  rules.forEach((rule) => {
    const score = rule.indexes.reduce((sum, idx) => {
      const raw = normalized[idx] || 0;
      return sum + (rule.reverse ? (6 - raw) : raw);
    }, 0);
    scoreMap[rule.key] = score;
  });

  const constitutionScores = [
    { key: 'ph', name: '平和质', score: scoreMap.ph, level: getBiasLevel(scoreMap.ph) },
    { key: 'qx', name: '气虚质', score: scoreMap.qx, level: getBiasLevel(scoreMap.qx) },
    { key: 'yx', name: '阳虚质', score: scoreMap.yx, level: getBiasLevel(scoreMap.yx) },
    { key: 'ts', name: '痰湿质', score: scoreMap.ts, level: getBiasLevel(scoreMap.ts) },
    { key: 'sr', name: '湿热质', score: scoreMap.sr, level: getBiasLevel(scoreMap.sr) },
    { key: 'xy', name: '血瘀质', score: scoreMap.xy, level: getBiasLevel(scoreMap.xy) },
    { key: 'tb', name: '特禀质', score: scoreMap.tb, level: getBiasLevel(scoreMap.tb) },
    { key: 'qy', name: '气郁质', score: scoreMap.qy, level: getBiasLevel(scoreMap.qy) },
    { key: 'yinXu', name: '阴虚质', score: scoreMap.yinXu, level: getBiasLevel(scoreMap.yinXu) },
  ];

  const pathological = constitutionScores.filter((item) => item.key !== 'ph').sort((a, b) => b.score - a.score);
  const topOne = pathological[0] || constitutionScores[0];
  const topTwo = pathological[1] || topOne;
  const topThree = pathological[2] || topTwo;
  const pingHeQualified = scoreMap.ph >= 12 && pathological.every((item) => item.score < 9);

  let finalTypes = [];
  if (pingHeQualified) {
    finalTypes = [constitutionScores[0]];
  } else if (topTwo && (topOne.score - topTwo.score) <= 1) {
    finalTypes = [topOne, topTwo];
  } else {
    finalTypes = [topOne];
  }

  const mergedGuidance = mergeHypertensionGuidance(finalTypes.map((item) => item.key));
  const hasSelfReportRisk = normalized[13] > 0;

  const summaryParts = [
    `判定结果：${finalTypes.map((item) => item.name).join('、')}。`,
    `参考得分：${topOne.name}${topOne.score}分，${topTwo.name}${topTwo.score}分，第三参考${topThree.name}${topThree.score}分。`,
    `平和质反向计分后得分为${scoreMap.ph}分，按兜底规则用于最终判定。`,
  ];

  if (hasSelfReportRisk) {
    summaryParts.push('提示：第14题舌下青筋/瘀紫自填信度略低，建议结合医护观察或智能设备复核。');
  }

  return {
    ...buildResultBase(
      finalTypes.length === 2
        ? `高血压复合体质：${finalTypes[0].name}、${finalTypes[1].name}`
        : `高血压主导体质：${finalTypes[0].name}`,
      summaryParts.join(' '),
      mergedGuidance.diet,
      mergedGuidance.avoid,
      [
        ...mergedGuidance.suggestions,
        '本结果为中医体质辅助评估，不能替代医师面诊，需结合血压、用药和临床症状综合判断。',
      ],
      finalTypes.length === 2 ? '复合体质' : finalTypes[0].name,
    ),
    scoreMap,
    scoringRule: '每体质固定3题、每题0/2/4/6分、单体质满分18分。判定规则：第一名与第二名差值>1为单一体质；差值<=1为复合体质；平和质按第2/9/17题反向计分，且满足门槛时兜底判定。',
    constitutionScores: constitutionScores.map((item) => ({
      name: item.name,
      score: item.score,
      level: item.level,
    })),
    dominantConstitution: finalTypes.map((item) => item.name).join('、'),
    thirdConstitution: { name: topThree.name, score: topThree.score },
    candidateConstitutions: constitutionScores
      .sort((a, b) => b.score - a.score)
      .map((item) => ({ name: item.name, score: item.score, level: item.level })),
  };
}

function mergeHypertensionGuidance(typeKeys = []) {
  const diets = [];
  const avoids = [];
  const suggestions = [];

  typeKeys.forEach((key) => {
    const guide = HYPERTENSION_GUIDANCE[key] || HYPERTENSION_GUIDANCE.ph;
    diets.push(...guide.diet);
    avoids.push(...guide.avoid);
    suggestions.push(...guide.suggestions);
  });

  const uniq = (list) => [...new Set(list)];
  return {
    diet: uniq(diets),
    avoid: uniq(avoids),
    suggestions: uniq(suggestions),
  };
}

function getBiasLevel(score) {
  if (score >= 19) return '重度偏颇';
  if (score >= 13) return '中度偏颇';
  if (score >= 7) return '轻微偏颇';
  return '无明显偏颇';
}

const HYPERTENSION_GUIDANCE = {
  ph: {
    summary: '体质相对稳健，适合继续维持低盐、规律、监测的基础管理。',
    diet: ['坚持低盐低脂饮食，均衡摄入营养。', '避免过度进补，减少血压波动。', '保持定时定量，减少大起大落。'],
    avoid: ['避免长期熬夜。', '避免久坐不动。', '避免过度进食重口味食物。'],
    suggestions: ['规律监测血压并记录。', '保持适度运动，如散步、太极拳。', '如血压持续异常，及时复诊。'],
  },
  qx: {
    summary: '气虚清阳不升，容易头晕乏力、活动后心慌。',
    diet: ['多吃山药、薏米、红枣、瘦肉等健脾益气食物。', '少量多餐，避免过饥过饱。', '注意饮食温和，减少脾胃负担。'],
    avoid: ['避免生冷、节食和剧烈运动。', '避免久蹲猛起。', '避免过度劳累。'],
    suggestions: ['适合散步、八段锦等慢运动。', '注意劳逸结合和充足睡眠。', '血压偏低或头晕频繁时及时就医评估。'],
  },
  yx: {
    summary: '阳虚寒凝，畏寒、手脚冰凉、受凉后血压波动更明显。',
    diet: ['多吃生姜、红枣、小米、南瓜等温阳食物。', '少量食用羊肉等温热食材。', '避免寒凉伤阳。'],
    avoid: ['避免冰饮、凉菜、生冷水果。', '避免吹冷风和潮湿环境。', '避免清热泻火类偏寒饮品长期使用。'],
    suggestions: ['头部、腰腹重点保暖。', '冬季外出注意防寒。', '如寒凉饮食后明显不适，及时调整饮食结构。'],
  },
  ts: {
    summary: '痰湿壅盛，身体困重、打鼾、腹部肥厚，血压往往更难稳定。',
    diet: ['少油少盐少甜，控制总热量。', '多吃冬瓜、赤小豆、茯苓、芹菜等祛湿食物。', '严格控制夜宵和酒精。'],
    avoid: ['避免久坐久卧。', '避免甜食和高脂外卖。', '避免超重继续加重。'],
    suggestions: ['坚持快走、太极拳等规律运动。', '控制腹围和体重。', '改善打鼾与睡眠质量。'],
  },
  sr: {
    summary: '湿热蕴结，口苦口黏、油腻上火，闷热天血压更易升高。',
    diet: ['多吃绿豆、冬瓜、芹菜、苦瓜、莲藕等清热利湿食物。', '减少油炸、辛辣、甜食。', '保持饮食清淡并补足水分。'],
    avoid: ['避免烧烤、烈酒、浓茶。', '避免熬夜。', '避免长期闷热环境。'],
    suggestions: ['保持室内通风干燥。', '选择凉爽时段运动。', '必要时结合医生建议控制湿热症状。'],
  },
  xy: {
    summary: '血瘀阻络，头刺痛、麻木、唇暗、瘀斑更常见。',
    diet: ['少量活血食材如黑木耳、洋葱、山楂。', '保持均衡饮食和适量蛋白。', '避免过重油盐。'],
    avoid: ['避免久坐不动。', '避免外伤和过度负重。', '避免高脂厚味持续摄入。'],
    suggestions: ['进行轻度活血运动，如拉伸、慢走、八段锦。', '定期监测血压与末梢循环。', '疼痛麻木持续加重建议复诊。'],
  },
  tb: {
    summary: '特禀体质偏敏感，换季和过敏源可诱发血压波动。',
    diet: ['清淡饮食，少吃新奇发物。', '明确并规避过敏原。', '记录不适与食物、环境之间的关系。'],
    avoid: ['避免花粉、异味、粉尘等刺激。', '避免擅自更换药物。', '避免季节交替时忽视防护。'],
    suggestions: ['换季时适当加密血压测量。', '必要时进行过敏原评估。', '过敏明显时及时就医。'],
  },
  qy: {
    summary: '气郁化火，烦躁易怒、压力大时头胀血压容易飙升。',
    diet: ['多吃陈皮、玫瑰花、小米、山药等疏肝食材。', '保持规律进餐，避免情绪性进食。', '少油少辣，减少上火感。'],
    avoid: ['避免长期压抑和生闷气。', '避免熬夜与焦虑累积。', '避免暴饮暴食。'],
    suggestions: ['通过深呼吸、散步、冥想疏解情绪。', '保持充足睡眠。', '情绪与血压联动明显时建议专业评估。'],
  },
  yinXu: {
    summary: '阴虚火旺，口干、耳鸣、眼花、熬夜后头晕更明显。',
    diet: ['清淡滋阴，多吃银耳、百合、莲子、雪梨、冬瓜。', '少量多次饮水，避免辛辣烧烤。', '尽量减少温补壮阳类食补。'],
    avoid: ['避免浓茶、烈酒、烧烤与熬夜。', '避免过度出汗。', '避免长期情绪激动。'],
    suggestions: ['23点前入睡，保证7-8小时睡眠。', '可用菊花枸杞茶、麦冬茶等辅助。', '眼干耳鸣明显时及时复诊。'],
  },
};

const DIABETES_SCORE_OPTIONS = [
  { label: '从不出现（0分）', value: 0 },
  { label: '偶尔出现（2分）', value: 2 },
  { label: '经常出现（4分）', value: 4 },
  { label: '每次/频繁出现（6分）', value: 6 },
];

const DIABETES_CONSTITUTION_RULES = [
  { key: 'qiXu', name: '气虚质', indexes: [0, 9, 17] },
  { key: 'yinXu', name: '阴虚质', indexes: [1, 8, 16] },
  { key: 'yangXu', name: '阳虚质', indexes: [2, 10, 18] },
  { key: 'tanShi', name: '痰湿质', indexes: [3, 11, 14] },
  { key: 'shiRe', name: '湿热质', indexes: [4, 12, 19] },
  { key: 'xueYu', name: '血瘀质', indexes: [5, 13, 20] },
  { key: 'teBing', name: '特禀质', indexes: [6, 21, 22] },
  { key: 'qiYu', name: '气郁质', indexes: [7, 15, 22] },
  { key: 'ph', name: '平和质', indexes: [1, 8, 16], reverse: true },
];

const DIABETES_GUIDANCE = {
  qiXu: {
    summary: '以乏力、气短、活动后耗气明显为主，提示气虚偏颇。',
    diet: ['饮食以健脾益气为主，少量多餐，避免暴饮暴食。', '优先温和易消化食物，避免血糖大幅波动。', '按医嘱进行主食分配与蛋白质补充。'],
    avoid: ['避免过劳和熬夜。', '避免空腹高强度运动。', '避免忽视低血糖先兆。'],
    suggestions: ['规律监测血糖与疲劳程度变化。', '运动以中低强度、可持续为主。', '持续乏力明显时建议复诊评估。'],
  },
  yinXu: {
    summary: '以口干咽燥、眼干、皮肤口唇干裂为主，提示阴虚偏颇。',
    diet: ['饮食宜清淡润燥，避免辛辣温燥。', '补充足量饮水并分次饮用。', '结合血糖控制选择低升糖负荷食材。'],
    avoid: ['避免熬夜和长时间高温环境。', '避免重口味和油炸食物。', '避免长期情绪焦灼。'],
    suggestions: ['按时监测空腹与餐后血糖。', '关注眼部和皮肤干燥变化。', '症状持续加重建议就医完善并发症筛查。'],
  },
  yangXu: {
    summary: '以畏寒怕冷、食凉不适、腹泻倾向为主，提示阳虚偏颇。',
    diet: ['饮食宜温和，减少生冷食物。', '注意三餐规律，避免空腹受凉。', '按医嘱调整饮食结构稳定血糖。'],
    avoid: ['避免冰饮和寒凉食物。', '避免受凉和潮湿环境久待。', '避免忽视腹泻导致的血糖波动。'],
    suggestions: ['做好腹部与下肢保暖。', '选择温和运动并观察血糖反应。', '反复腹泻或明显畏寒建议及时就医。'],
  },
  tanShi: {
    summary: '以身体沉重、腹部肥胖、大便黏滞或异常为主，提示痰湿偏颇。',
    diet: ['控制总热量与精制糖摄入。', '饮食清淡，减少高油高甜。', '增加膳食纤维并结合血糖管理配餐。'],
    avoid: ['避免久坐少动。', '避免夜宵与暴饮暴食。', '避免长期不记录体重和腰围。'],
    suggestions: ['坚持体重管理和规律运动。', '记录体重、腰围、血糖三项趋势。', '必要时请医生评估代谢综合风险。'],
  },
  shiRe: {
    summary: '以口苦口臭、油腻、舌苔厚腻、小便黄赤为主，提示湿热偏颇。',
    diet: ['饮食宜清淡，减少辛辣油炸。', '合理补水，避免含糖饮料。', '按血糖管理原则控制总碳水负荷。'],
    avoid: ['避免高糖高脂和酒精。', '避免熬夜与闷热环境。', '避免忽视皮肤反复问题。'],
    suggestions: ['保持规律作息和清洁护理。', '血糖升高时加强症状观察。', '皮肤问题反复建议就医处理。'],
  },
  xueYu: {
    summary: '以肢体麻木、固定疼痛、瘀斑瘀紫表现为主，提示血瘀偏颇。',
    diet: ['饮食均衡，兼顾蛋白质与蔬菜。', '避免长期高油高盐。', '在血糖稳定前提下保持规律进食。'],
    avoid: ['避免久坐不动。', '避免外伤和过度负重运动。', '避免忽视末梢麻木疼痛变化。'],
    suggestions: ['关注下肢感觉和末梢循环。', '按医嘱进行并发症筛查。', '疼痛持续或夜间加重请及时就诊。'],
  },
  teBing: {
    summary: '以过敏体质表现明显为主，提示特禀偏颇。',
    diet: ['排查并规避明确过敏食物。', '保持饮食记录，观察过敏与血糖关系。', '新食物尝试应循序渐进。'],
    avoid: ['避免已知过敏原暴露。', '避免擅自更换降糖药物。', '避免在过敏高发季忽视防护。'],
    suggestions: ['必要时完善过敏原评估。', '季节交替阶段强化防护。', '药物或食物过敏明显时及时就医。'],
  },
  qiYu: {
    summary: '以焦虑、失落、情绪波动影响血糖为主，提示气郁偏颇。',
    diet: ['保持规律进餐，减少情绪性进食。', '避免高糖零食替代正餐。', '配合血糖管理进行分餐定量。'],
    avoid: ['避免长期压力累积。', '避免昼夜节律紊乱。', '避免忽视睡眠质量下降。'],
    suggestions: ['建立情绪与血糖联动记录。', '采用可持续减压方式如散步、呼吸训练。', '焦虑抑郁持续时建议专业评估。'],
  },
  ph: {
    summary: '平和质达标，提示当前体质相对稳定。',
    diet: ['继续执行控糖饮食，维持均衡营养。', '保持规律三餐，避免大起大落。', '结合医嘱维持体重与代谢稳定。'],
    avoid: ['避免放松血糖监测。', '避免长期熬夜与久坐。', '避免擅自停药或改药。'],
    suggestions: ['按计划复查糖化血红蛋白。', '保持运动、睡眠、饮食三项稳定。', '若症状反复应及时复诊调整方案。'],
  },
};

function buildDiabetesResult(answers = []) {
  const normalized = (answers || []).map((value) => Number(value) || 0);
  const scoreMap = {};

  DIABETES_CONSTITUTION_RULES.forEach((rule) => {
    const score = rule.indexes.reduce((sum, idx) => {
      const raw = normalized[idx] || 0;
      return sum + (rule.reverse ? (6 - raw) : raw);
    }, 0);
    scoreMap[rule.key] = score;
  });

  const constitutionScores = DIABETES_CONSTITUTION_RULES.map((rule) => ({
    key: rule.key,
    name: rule.name,
    score: scoreMap[rule.key] || 0,
    level: '满分18',
  }));

  const pathological = constitutionScores
    .filter((item) => item.key !== 'ph')
    .sort((a, b) => b.score - a.score);

  const topOne = pathological[0] || { key: 'ph', name: '平和质', score: scoreMap.ph || 0 };
  const topTwo = pathological[1] || topOne;
  const topThree = pathological[2] || topTwo;

  const otherScores = pathological.map((item) => item.score);
  const phScore = scoreMap.ph || 0;
  const manyZeroAnswers = normalized.filter((value) => value === 0).length >= 12;
  const pingHeQualified = phScore >= 12 && otherScores.every((value) => value < 9);

  let finalTypes = [];
  if (pingHeQualified && manyZeroAnswers) {
    finalTypes = [{ key: 'ph', name: '平和质', score: phScore }];
  } else if (topOne.score - topTwo.score > 1) {
    finalTypes = [topOne];
  } else {
    finalTypes = [topOne, topTwo];
  }

  const primary = finalTypes[0];
  const guide = DIABETES_GUIDANCE[primary.key] || DIABETES_GUIDANCE.ph;
  const isComposite = finalTypes.length === 2;

  const summaryParts = [
    `判定结果：${finalTypes.map((item) => item.name).join('、')}。`,
    `主要依据：${topOne.name}${topOne.score}分，${topTwo.name}${topTwo.score}分，差值${Math.abs(topOne.score - topTwo.score)}分。`,
    `第三参考体质：${topThree.name}${topThree.score}分（供医生综合辨证参考）。`,
    guide.summary,
  ];

  if (pingHeQualified) {
    summaryParts.push('平和质按反向计分（第2/9/17题），并满足平和质门槛时可优先兜底判定。');
  }

  if ((normalized[13] || 0) > 0) {
    summaryParts.push('提示：第14题涉及舌下静脉观察，自填结果可能受光线与观察经验影响，建议医护或设备复核。');
  }

  return {
    ...buildResultBase(
      isComposite ? `糖尿病复合体质：${finalTypes[0].name}、${finalTypes[1].name}` : `糖尿病主导体质：${primary.name}`,
      summaryParts.join(' '),
      guide.diet,
      guide.avoid,
      [
        ...guide.suggestions,
        '本结果为中医体质辅助评估，不能替代医师面诊，最终需结合血糖与临床症状综合判断。',
      ],
      isComposite ? '复合体质' : primary.name,
    ),
    scoreMap,
    scoringRule: '每题0/2/4/6分；九种体质按各自关联3题累计，单体质满分18分。判定优先级：单一体质（第一名与第二名差值>1）→复合体质（差值<=1）→平和质兜底（反向计分且满足门槛）。',
    constitutionScores: constitutionScores
      .sort((a, b) => b.score - a.score)
      .map((item) => ({ name: item.name, score: item.score, level: item.level })),
    dominantConstitution: finalTypes.map((item) => item.name).join('、'),
    thirdConstitution: { name: topThree.name, score: topThree.score },
  };
}

function buildChildrenResult(answers = []) {
  const normalized = (answers || []).map((value) => Number(value) || 0);
  const constitutionScores = CHILDREN_CONSTITUTION_RULES.map((rule) => {
    const score = rule.questionIndexes.reduce((sum, idx) => sum + (normalized[idx] || 0), 0);
    return {
      key: rule.key,
      name: rule.name,
      score,
      level: getChildrenBiasLevel(score),
      coreState: rule.coreState,
      diet: rule.diet,
      avoid: rule.avoid,
      suggestions: rule.suggestions,
    };
  });

  const maxScore = Math.max(...constitutionScores.map((item) => item.score), 0);
  const tied = constitutionScores.filter((item) => item.score === maxScore);
  const dominant = pickChildrenDominantConstitution(tied);
  const hasTie = tied.length > 1;

  const summaryLines = [
    `主导体质判定为${dominant.name}（${dominant.score}分，${dominant.level}）。`,
    `核心偏颇：${dominant.coreState}`,
  ];

  if (hasTie) {
    summaryLines.push(
      `本次最高分存在并列（${tied.map((item) => item.name).join('、')}），系统按规则优先平和质兜底；若仍并列，按题目匹配顺序判定。`,
    );
  }

  return {
    ...buildResultBase(
      `儿童主导体质：${dominant.name}`,
      summaryLines.join(' '),
      dominant.diet,
      dominant.avoid,
      dominant.suggestions,
      dominant.name,
    ),
    scoreMap: Object.fromEntries(constitutionScores.map((item) => [item.key, item.score])),
    scoringRule: '每题0/2/4/6分；每种体质4题，总分24分。0-6分无明显偏颇，7-12分轻微偏颇，13-18分中度偏颇，19-24分重度偏颇。',
    constitutionScores: constitutionScores.map((item) => ({
      key: item.key,
      name: item.name,
      score: item.score,
      level: item.level,
    })),
    dominantConstitution: dominant.name,
  };
}

function getChildrenBiasLevel(score) {
  if (score >= 19) return '重度偏颇';
  if (score >= 13) return '中度偏颇';
  if (score >= 7) return '轻微偏颇';
  return '无明显偏颇';
}

function pickChildrenDominantConstitution(tied = []) {
  if (!tied.length) {
    return {
      name: '平和质',
      score: 0,
      level: '无明显偏颇',
      coreState: '',
      diet: [],
      avoid: [],
      suggestions: [],
    };
  }
  return tied.slice().sort((a, b) => {
    return CHILDREN_DOMINANT_ORDER.indexOf(a.key) - CHILDREN_DOMINANT_ORDER.indexOf(b.key);
  })[0];
}

const FIVE_PERSONALITY_RULES = [
  {
    key: 'ty',
    name: '太阴',
    questionIndexes: [0, 1, 2, 3],
    summary: '情志郁结、思虑过多、敏感多疑，易陷入负面情绪。',
    music: ['《高山流水》', '《平沙落雁》'],
    behavior: ['每天主动与家人、朋友交流10-15分钟，释放情绪。', '每日练习腹式呼吸5-10分钟，放空思绪。', '每周参与1-2次温和运动，如散步、八段锦。'],
  },
  {
    key: 'sy',
    name: '少阴',
    questionIndexes: [4, 5, 6, 7],
    summary: '沉静内敛、思虑缜密，易因过度严谨陷入纠结。',
    music: ['《梅花三弄》', '《春江花月夜》'],
    behavior: ['培养一项轻松兴趣，如养花、练字。', '避免过度追求完美，学会适当妥协。', '减少纠结内耗，保留放松空间。'],
  },
  {
    key: 'tyang',
    name: '太阳',
    questionIndexes: [8, 9, 10, 11],
    summary: '情绪亢奋、精力旺盛，易冲动，易出现情绪波动。',
    music: ['《禅院钟声》', '《平湖秋月》'],
    behavior: ['每日预留10-15分钟独处时间，放空思绪。', '每周参与2-3次中等强度运动，如慢跑、游泳。', '通过运动释放多余精力，稳定情绪。'],
  },
  {
    key: 'syang',
    name: '少阳',
    questionIndexes: [12, 13, 14, 15],
    summary: '活泼好动、思维敏捷，易情绪波动，注意力不集中。',
    music: ['《广陵散》', '《汉宫秋月》'],
    behavior: ['培养需要耐心的兴趣爱好，如画画、插花。', '每日练习冥想5-10分钟，稳定心神。', '训练专注力，减少分心。'],
  },
  {
    key: 'yyph',
    name: '阴阳平和',
    questionIndexes: [16, 17, 18, 19],
    summary: '性格平和、心态豁达，不卑不亢，能从容应对生活中的各类事情。',
    music: ['《幽兰》', '《长清》'],
    behavior: ['保持规律作息，合理安排社交与独处时间。', '每周参与2-3次温和运动，维持身心平衡。', '继续保持平和心态，无需过度调理。'],
  },
];

function buildFiveStateResult(answers = []) {
  const normalized = (answers || []).map((value) => Number(value) || 0);
  const scores = FIVE_PERSONALITY_RULES.map((rule) => {
    const score = rule.questionIndexes.reduce((sum, idx) => sum + (normalized[idx] || 0), 0);
    return {
      key: rule.key,
      name: rule.name,
      score,
      level: getFivePersonalityLevel(score),
      summary: rule.summary,
      music: rule.music,
      behavior: rule.behavior,
    };
  });

  const sorted = scores.slice().sort((a, b) => b.score - a.score);
  const topOne = sorted[0];
  const topTwo = sorted[1] || topOne;
  const topThree = sorted[2] || topTwo;
  const tiedTop = sorted.filter((item) => item.score === topOne.score);
  const dominant = tiedTop.some((item) => item.key === 'yyph') ? scores.find((item) => item.key === 'yyph') : topOne;

  const summaryParts = [
    `主导人格判定为${dominant.name}。`,
    `参考得分：${topOne.name}${topOne.score}分，${topTwo.name}${topTwo.score}分，第三参考${topThree.name}${topThree.score}分。`,
    dominant.summary,
  ];

  if (tiedTop.length > 1) {
    summaryParts.push('最高分出现并列时，按阴阳平和人格兜底判定。');
  }

  const guidance = FIVE_PERSONALITY_GUIDANCE[dominant.key] || FIVE_PERSONALITY_GUIDANCE.yyph;

  return {
    ...buildResultBase(
      `五态主导人格：${dominant.name}`,
      summaryParts.join(' '),
      guidance.music,
      guidance.behavior,
      [
        '本测评仅判定唯一主导人格，不进行复合人格判定。',
        '如长期存在明显情绪困扰或睡眠问题，建议结合专业评估。',
      ],
      dominant.name,
    ),
    scoreMap: Object.fromEntries(scores.map((item) => [item.key, item.score])),
    scoringRule: '共20题，每题0/2/4/6分。五种人格各关联4题，单种人格满分24分。系统仅判定唯一主导人格；若最高分并列，则以阴阳平和人格兜底判定。',
    music: guidance.music,
    behavior: guidance.behavior,
    constitutionScores: scores.map((item) => ({ name: item.name, score: item.score, level: item.level })),
    dominantConstitution: dominant.name,
    candidateConstitutions: scores.slice().sort((a, b) => b.score - a.score).map((item) => ({
      name: item.name,
      score: item.score,
      level: item.level,
    })),
    thirdConstitution: { name: topThree.name, score: topThree.score },
  };
}

function getFivePersonalityLevel(score) {
  if (score >= 19) return '高度匹配';
  if (score >= 13) return '较高匹配';
  if (score >= 7) return '中等匹配';
  return '轻度匹配';
}

const FIVE_PERSONALITY_GUIDANCE = {
  ty: {
    music: ['《高山流水》', '《平沙落雁》'],
    behavior: ['每天主动与家人、朋友交流10-15分钟，释放情绪。', '每日练习腹式呼吸5-10分钟，放空思绪。', '每周参与1-2次温和运动，如散步、八段锦。'],
  },
  sy: {
    music: ['《梅花三弄》', '《春江花月夜》'],
    behavior: ['培养一项轻松的兴趣爱好，如养花、练字。', '避免过度追求完美，学会适当妥协。', '减少纠结内耗，保留放松空间。'],
  },
  tyang: {
    music: ['《禅院钟声》', '《平湖秋月》'],
    behavior: ['每日预留10-15分钟独处时间，放空思绪。', '每周参与2-3次中等强度运动，如慢跑、游泳。', '通过运动释放多余精力，稳定情绪。'],
  },
  syang: {
    music: ['《广陵散》', '《汉宫秋月》'],
    behavior: ['培养需要耐心的兴趣爱好，如画画、插花。', '每日练习冥想5-10分钟，稳定心神。', '训练专注力，减少分心。'],
  },
  yyph: {
    music: ['《幽兰》', '《长清》'],
    behavior: ['保持规律作息，合理安排社交与独处时间。', '每周参与2-3次温和运动，维持身心平衡。', '继续保持平和心态，无需过度调理。'],
  },
};

export const SPECIAL_QUESTIONNAIRE_TEMPLATES = {
  hypertension: {
    code: 'hypertension',
    title: '高血压专项问诊',
    subtitle: '高血压专用，24题九体质辨证（支持单一/复合体质）',
    audioEnabled: false,
    questionCount: 24,
    questions: [
      { content: '您平时容易头晕乏力、起身眼前发花、劳累后头沉加重？', remark: '关联气虚质', options: [{ label: '从不出现（0分）', value: 0 }, { label: '偶尔轻微（2分）', value: 2 }, { label: '经常明显（4分）', value: 4 }, { label: '每次劳累必发作（6分）', value: 6 }] },
      { content: '您平时口干咽燥、手心脚心发热、夜间心烦潮热？', remark: '关联阴虚质/平和质反向计分', options: [{ label: '从不出现（0分）', value: 0 }, { label: '偶尔轻微（2分）', value: 2 }, { label: '经常明显（4分）', value: 4 }, { label: '长期难安（6分）', value: 6 }] },
      { content: '您平时畏寒怕冷、手脚冰凉、腰腹怕凉、受凉头部发紧发沉？', remark: '关联阳虚质', options: [{ label: '从不出现（0分）', value: 0 }, { label: '偶尔轻微（2分）', value: 2 }, { label: '经常明显（4分）', value: 4 }, { label: '受凉必加重血压波动（6分）', value: 6 }] },
      { content: '您体型偏胖、身体困重、腹部松软肥厚、血压难控制、晨起头闷如裹？', remark: '关联痰湿质', options: [{ label: '从不出现（0分）', value: 0 }, { label: '偶尔轻微（2分）', value: 2 }, { label: '经常明显（4分）', value: 4 }, { label: '常年困重不清爽（6分）', value: 6 }] },
      { content: '您平时口苦口黏、面部油腻、易长痘上火、小便发黄燥热？', remark: '关联湿热质', options: [{ label: '从不出现（0分）', value: 0 }, { label: '偶尔轻微（2分）', value: 2 }, { label: '经常明显（4分）', value: 4 }, { label: '上火就血压升高（6分）', value: 6 }] },
      { content: '您头部刺痛/胀痛固定不移、肢体麻木、唇色偏暗、血压波动伴瘀沉感？', remark: '关联血瘀质', options: [{ label: '从不出现（0分）', value: 0 }, { label: '偶尔轻微（2分）', value: 2 }, { label: '经常明显（4分）', value: 4 }, { label: '长期刺痛麻木（6分）', value: 6 }] },
      { content: '您换季/接触异味花粉/特殊食物，易头痒头胀、过敏不适诱发血压不稳？', remark: '关联特禀质', options: [{ label: '从不出现（0分）', value: 0 }, { label: '偶尔轻微（2分）', value: 2 }, { label: '经常明显（4分）', value: 4 }, { label: '过敏必牵动血压（6分）', value: 6 }] },
      { content: '您情绪压抑、爱生闷气、烦躁易怒、生气后立刻头胀血压飙升？', remark: '关联气郁质', options: [{ label: '从不出现（0分）', value: 0 }, { label: '偶尔轻微（2分）', value: 2 }, { label: '经常明显（4分）', value: 4 }, { label: '情绪波动血压必炸（6分）', value: 6 }] },
      { content: '您视物干涩眼花、耳鸣频发、熬夜后头晕加重？', remark: '关联阴虚质/平和质反向计分', options: [{ label: '从不出现（0分）', value: 0 }, { label: '偶尔轻微（2分）', value: 2 }, { label: '经常明显（4分）', value: 4 }, { label: '常年耳鸣眼干（6分）', value: 6 }] },
      { content: '您说话气短懒言、稍微活动心慌乏力、血压偏低时头晕更明显？', remark: '关联气虚质', options: [{ label: '从不出现（0分）', value: 0 }, { label: '偶尔轻微（2分）', value: 2 }, { label: '经常明显（4分）', value: 4 }, { label: '一动就虚累头晕（6分）', value: 6 }] },
      { content: '您吃生冷、吹冷风后腹胀腹凉、头部发僵发沉、血压小幅波动？', remark: '关联阳虚质', options: [{ label: '从不出现（0分）', value: 0 }, { label: '偶尔轻微（2分）', value: 2 }, { label: '经常明显（4分）', value: 4 }, { label: '寒凉必不适（6分）', value: 6 }] },
      { content: '您大便黏腻粘马桶、口中发黏、晨起痰多、脑袋不清爽？', remark: '关联痰湿质', options: [{ label: '从不出现（0分）', value: 0 }, { label: '偶尔轻微（2分）', value: 2 }, { label: '经常明显（4分）', value: 4 }, { label: '常年黏腻痰多（6分）', value: 6 }] },
      { content: '您舌苔厚腻发黄、口内异味、容易上火长痘、闷热天血压易高？', remark: '关联湿热质', options: [{ label: '从不出现（0分）', value: 0 }, { label: '偶尔轻微（2分）', value: 2 }, { label: '经常明显（4分）', value: 4 }, { label: '湿热天必升压（6分）', value: 6 }] },
      { content: '您舌下青筋粗紫、身上易出瘀斑、久坐后头部发沉发僵？', remark: '关联血瘀质', options: [{ label: '从不出现（0分）', value: 0 }, { label: '偶尔轻微（2分）', value: 2 }, { label: '经常明显（4分）', value: 4 }, { label: '血瘀体征常年存在（6分）', value: 6 }] },
      { content: '您睡觉打鼾严重、口黏口苦、睡醒头沉不清醒？', remark: '关联痰湿质', options: [{ label: '从不出现（0分）', value: 0 }, { label: '偶尔轻微（2分）', value: 2 }, { label: '经常明显（4分）', value: 4 }, { label: '睡醒依旧昏沉（6分）', value: 6 }] },
      { content: '您长期心情低落、多想多虑、压力大就头胀失眠血压不稳？', remark: '关联气郁质', options: [{ label: '从不出现（0分）', value: 0 }, { label: '偶尔轻微（2分）', value: 2 }, { label: '经常明显（4分）', value: 4 }, { label: '压力大必失眠升压（6分）', value: 6 }] },
      { content: '您皮肤偏干、口唇易裂、常年燥热少汗？', remark: '关联阴虚质/平和质反向计分', options: [{ label: '从不出现（0分）', value: 0 }, { label: '偶尔轻微（2分）', value: 2 }, { label: '经常明显（4分）', value: 4 }, { label: '常年干燥燥热（6分）', value: 6 }] },
      { content: '您运动后虚汗多、心慌气短、血压忽高忽低？', remark: '关联气虚质·补充题', options: [{ label: '从不出现（0分）', value: 0 }, { label: '偶尔轻微（2分）', value: 2 }, { label: '经常明显（4分）', value: 4 }, { label: '一动虚汗心慌（6分）', value: 6 }] },
      { content: '您喝凉水/吃凉食后腹泻腹胀、头凉发紧不适？', remark: '关联阳虚质·补充题', options: [{ label: '从不出现（0分）', value: 0 }, { label: '偶尔轻微（2分）', value: 2 }, { label: '经常明显（4分）', value: 4 }, { label: '寒凉饮食必难受（6分）', value: 6 }] },
      { content: '您小便灼热发黄、下焦燥热、上火即心烦头胀？', remark: '关联湿热质·补充题', options: [{ label: '从不出现（0分）', value: 0 }, { label: '偶尔轻微（2分）', value: 2 }, { label: '经常明显（4分）', value: 4 }, { label: '内热重易升压（6分）', value: 6 }] },
      { content: '您肢体固定酸痛、久坐久站头沉刺痛加重？', remark: '关联血瘀质·补充题', options: [{ label: '从不出现（0分）', value: 0 }, { label: '偶尔轻微（2分）', value: 2 }, { label: '经常明显（4分）', value: 4 }, { label: '久不动瘀痛加重（6分）', value: 6 }] },
      { content: '您体质敏感、换季易鼻塞头胀、轻微刺激就血压波动？', remark: '关联特禀质·补充题', options: [{ label: '从不出现（0分）', value: 0 }, { label: '偶尔轻微（2分）', value: 2 }, { label: '经常明显（4分）', value: 4 }, { label: '体质极敏感（6分）', value: 6 }] },
      { content: '您接触花粉/异味/特殊食物后，易出现皮肤瘙痒、鼻塞头胀，诱发血压波动？', remark: '关联特禀质·补充题', options: [{ label: '从不出现（0分）', value: 0 }, { label: '偶尔轻微（2分）', value: 2 }, { label: '经常明显（4分）', value: 4 }, { label: '每次接触必不适升压（6分）', value: 6 }] },
      { content: '您易因琐事烦躁易怒、胸闷叹气，烦躁后即出现头胀、血压轻微升高？', remark: '关联气郁质·补充题', options: [{ label: '从不出现（0分）', value: 0 }, { label: '偶尔轻微（2分）', value: 2 }, { label: '经常明显（4分）', value: 4 }, { label: '烦躁必诱发头胀升压（6分）', value: 6 }] },
    ],
    buildResult: buildHypertensionResult,
  },
  diabetes: {
    code: 'diabetes',
    title: '糖尿病专项问诊',
    subtitle: '糖尿病患者专属，23题体质评估（无音频）',
    audioEnabled: false,
    questionCount: 23,
    questions: [
      { content: '您血糖波动时，容易出现乏力、精神萎靡吗？', remark: '关联气虚质', options: [{ label: '从不出现，血糖波动时精神状态正常（0分）', value: 0 }, { label: '偶尔出现，仅明显血糖波动时轻微乏力（2分）', value: 2 }, { label: '经常出现，血糖稍波动即乏力，休息后缓解（4分）', value: 4 }, { label: '每次血糖波动均出现，极度乏力，影响日常活动（6分）', value: 6 }] },
      { content: '您是否经常口干咽燥、总想喝水？', remark: '关联阴虚质（平和质反向计分）', options: [{ label: '从不口干，即使血糖升高也无明显口渴（0分）', value: 0 }, { label: '偶尔口干，血糖升高时轻微口渴，饮水后缓解（2分）', value: 2 }, { label: '经常口干咽燥，血糖正常时也口渴，需频繁饮水（4分）', value: 4 }, { label: '口干咽燥明显，饮水后仍不缓解，夜间需起床喝水（6分）', value: 6 }] },
      { content: '您是否经常手脚冰凉、畏寒怕冷？', remark: '关联阳虚质', options: [{ label: '从不畏寒怕冷，手脚始终温暖（0分）', value: 0 }, { label: '偶尔怕冷，冬季轻微手脚冰凉，保暖后快速缓解（2分）', value: 2 }, { label: '经常畏寒，手脚冰凉明显，血糖偏低时加重（4分）', value: 4 }, { label: '极度畏寒，全身怕冷，手脚冰凉难以缓解，影响睡眠（6分）', value: 6 }] },
      { content: '您是否身体沉重、腹部肥胖，且血糖控制难度较大？', remark: '关联痰湿质', options: [{ label: '身体轻盈，无腹部肥胖，血糖易控制（0分）', value: 0 }, { label: '偶尔身体沉重，腹部轻微肥胖，对血糖影响不大（2分）', value: 2 }, { label: '经常身体沉重，腹部肥胖明显，血糖控制需调整方案（4分）', value: 4 }, { label: '身体极度沉重，腹部肥胖突出，血糖长期控制不佳（6分）', value: 6 }] },
      { content: '您是否口苦、口臭，且容易出现皮肤湿疹、疮疖？', remark: '关联湿热质', options: [{ label: '无口苦口臭，皮肤状态良好（0分）', value: 0 }, { label: '偶尔口苦，皮肤偶尔长湿疹/疮疖，与血糖无关（2分）', value: 2 }, { label: '经常口苦口臭，皮肤反复出现湿疹/疮疖，血糖升高时加重（4分）', value: 4 }, { label: '口苦口臭明显，皮肤频繁长湿疹/疮疖，伴瘙痒，影响生活（6分）', value: 6 }] },
      { content: '您是否肢体麻木、有固定部位疼痛，尤其四肢末端？', remark: '关联血瘀质', options: [{ label: '无肢体麻木、疼痛，四肢感觉正常（0分）', value: 0 }, { label: '偶尔肢体末端轻微麻木，无疼痛，休息后缓解（2分）', value: 2 }, { label: '经常肢体麻木，伴轻微固定疼痛，血糖波动时加重（4分）', value: 4 }, { label: '肢体麻木、疼痛明显，影响活动，夜间加重（6分）', value: 6 }] },
      { content: '您是否容易对降糖药物、食物过敏，或季节交替时出现过敏反应？', remark: '关联特禀质', options: [{ label: '无任何过敏史，对降糖药物、食物均无不适（0分）', value: 0 }, { label: '偶尔对某种食物过敏，与降糖药物无关（2分）', value: 2 }, { label: '经常对多种食物或花粉过敏，偶尔出现药物轻微过敏（4分）', value: 4 }, { label: '对多种降糖药物、食物过敏，季节交替时过敏反应明显（6分）', value: 6 }] },
      { content: '您是否因血糖控制不佳而感到闷闷不乐、焦虑紧张，情绪波动大？', remark: '关联气郁质', options: [{ label: '心态平和，不受血糖控制情况影响（0分）', value: 0 }, { label: '偶尔因血糖波动感到焦虑，很快能调整（2分）', value: 2 }, { label: '经常因血糖控制不佳感到闷闷不乐、焦虑，影响睡眠（4分）', value: 4 }, { label: '长期情绪低落、焦虑，对血糖控制失去信心（6分）', value: 6 }] },
      { content: '您是否眼睛干涩、视物模糊？', remark: '关联阴虚质（平和质反向计分）', options: [{ label: '眼睛湿润，视力正常，无视物模糊（0分）', value: 0 }, { label: '偶尔眼睛干涩，血糖升高时轻微视物模糊（2分）', value: 2 }, { label: '经常眼睛干涩，视物模糊，血糖控制平稳后可缓解（4分）', value: 4 }, { label: '眼睛干涩明显，视物模糊加重，需干预改善（6分）', value: 6 }] },
      { content: '您是否说话声音低弱无力，稍说话即气短？', remark: '关联气虚质', options: [{ label: '声音洪亮，说话有力，无气短感（0分）', value: 0 }, { label: '声音尚可，偶尔气短，不影响交流（2分）', value: 2 }, { label: '声音经常低弱，说话易气短，需停顿休息（4分）', value: 4 }, { label: '声音极度低弱，稍说话即气短，难以连贯交流（6分）', value: 6 }] },
      { content: '您是否胃脘部、腰膝部怕冷，吃凉食后不适？', remark: '关联阳虚质', options: [{ label: '无怕冷表现，吃凉食无不适（0分）', value: 0 }, { label: '偶尔腰膝怕冷，吃凉食后轻微不适（2分）', value: 2 }, { label: '经常胃脘、腰膝怕冷，吃凉食后明显不适，血糖易波动（4分）', value: 4 }, { label: '极度怕冷，吃凉食后严重不适，血糖波动明显（6分）', value: 6 }] },
      { content: '您是否大便黏滞不爽（易粘马桶），或大便干燥？', remark: '关联痰湿质', options: [{ label: '大便正常，成形不粘马桶，与血糖无关（0分）', value: 0 }, { label: '偶尔大便异常，血糖波动时轻微黏滞或干燥（2分）', value: 2 }, { label: '经常大便黏滞或干燥，血糖升高时加重（4分）', value: 4 }, { label: '大便长期异常，黏滞难排或极度干燥，需辅助改善（6分）', value: 6 }] },
      { content: '您是否面部、鼻部油腻，舌苔厚腻？', remark: '关联湿热质（建议医护或设备复核）', options: [{ label: '面部清爽，舌苔正常，无油腻感（0分）', value: 0 }, { label: '偶尔面部轻微油腻，舌苔薄腻（2分）', value: 2 }, { label: '经常面部、鼻部油腻，舌苔厚腻，血糖升高时加重（4分）', value: 4 }, { label: '面部油腻明显，舌苔厚腻发黄，影响食欲（6分）', value: 6 }] },
      { content: '您是否舌下静脉瘀紫、增粗，肢体偶尔出现青紫瘀斑？', remark: '关联血瘀质（自填信度略低，建议复核）', options: [{ label: '舌下静脉正常，无瘀紫增粗，皮肤无瘀斑（0分）', value: 0 }, { label: '舌下静脉轻微瘀紫，无增粗，偶尔出现细小瘀斑（2分）', value: 2 }, { label: '舌下静脉明显瘀紫、轻度增粗，经常出现瘀斑（4分）', value: 4 }, { label: '舌下静脉严重瘀紫、增粗，皮肤频繁出现瘀斑（6分）', value: 6 }] },
      { content: '您是否容易感冒，感冒后恢复缓慢？', remark: '关联特禀质、痰湿质（交叉载荷）', options: [{ label: '不易感冒，感冒后快速恢复，不影响血糖（0分）', value: 0 }, { label: '偶尔感冒，恢复较快，对血糖影响小（2分）', value: 2 }, { label: '经常感冒，恢复缓慢，感冒时血糖明显升高（4分）', value: 4 }, { label: '频繁感冒，恢复极慢，血糖长期受影响（6分）', value: 6 }] },
      { content: '您是否因血糖波动、饮食限制而感到孤独、失落？', remark: '关联气郁质', options: [{ label: '无孤独失落感，能适应饮食限制和血糖波动（0分）', value: 0 }, { label: '偶尔因饮食限制感到失落，很快调整（2分）', value: 2 }, { label: '经常感到孤独、失落，对饮食限制和血糖控制感到困扰（4分）', value: 4 }, { label: '长期孤独失落，抵触饮食限制，影响血糖控制（6分）', value: 6 }] },
      { content: '您是否皮肤干燥、口唇干裂？', remark: '关联阴虚质（平和质反向计分）', options: [{ label: '皮肤湿润，口唇红润，无干裂（0分）', value: 0 }, { label: '偶尔皮肤干燥，口唇轻微干裂（2分）', value: 2 }, { label: '经常皮肤干燥、口唇干裂，血糖升高时加重（4分）', value: 4 }, { label: '皮肤极度干燥、脱屑，口唇严重干裂，影响进食（6分）', value: 6 }] },
      { content: '您是否运动后易出汗、气短乏力，且血糖波动明显？', remark: '关联气虚质（补充题）', options: [{ label: '运动后无出汗异常，气短乏力，血糖稳定（0分）', value: 0 }, { label: '偶尔运动后轻微出汗、气短，血糖无明显波动（2分）', value: 2 }, { label: '经常运动后明显出汗、气短乏力，血糖轻微波动（4分）', value: 4 }, { label: '运动后极度出汗、气短乏力，血糖波动明显（6分）', value: 6 }] },
      { content: '您是否吃凉食后出现腹胀、腹泻？', remark: '关联阳虚质（补充题）', options: [{ label: '吃凉食无不适，血糖稳定（0分）', value: 0 }, { label: '偶尔吃凉食后轻微腹胀，无腹泻，血糖无明显变化（2分）', value: 2 }, { label: '经常吃凉食后腹胀、腹泻，血糖轻微降低（4分）', value: 4 }, { label: '吃凉食后严重腹胀、腹泻，血糖明显降低，需调整饮食（6分）', value: 6 }] },
      { content: '您是否小便黄赤、排尿灼热？', remark: '关联湿热质（补充题）', options: [{ label: '小便清澈，无排尿灼热感（0分）', value: 0 }, { label: '偶尔小便微黄，无明显灼热感（2分）', value: 2 }, { label: '经常小便黄赤，排尿有轻微灼热感（4分）', value: 4 }, { label: '小便黄赤明显，排尿灼热感强烈（6分）', value: 6 }] },
      { content: '您是否肢体活动时疼痛加重，且疼痛部位固定？', remark: '关联血瘀质（补充题）', options: [{ label: '肢体活动无疼痛，活动自如（0分）', value: 0 }, { label: '偶尔肢体活动轻微疼痛，无固定部位（2分）', value: 2 }, { label: '经常肢体活动时疼痛，疼痛部位固定（4分）', value: 4 }, { label: '肢体活动时剧烈疼痛，疼痛部位固定，影响活动（6分）', value: 6 }] },
      { content: '您是否接触花粉、尘螨后易出现皮肤瘙痒、打喷嚏？', remark: '关联特禀质（补充题）', options: [{ label: '接触后无任何不适（0分）', value: 0 }, { label: '偶尔接触后轻微皮肤瘙痒，无打喷嚏（2分）', value: 2 }, { label: '经常接触后皮肤瘙痒、打喷嚏，需避开过敏原（4分）', value: 4 }, { label: '接触后立即出现明显瘙痒、打喷嚏，甚至诱发血糖波动（6分）', value: 6 }] },
      { content: '您是否容易烦躁易怒、情绪低落，且影响血糖控制？', remark: '关联气郁质、特禀质（交叉载荷）', options: [{ label: '情绪稳定，无烦躁易怒，不影响血糖（0分）', value: 0 }, { label: '偶尔烦躁，不影响情绪和血糖（2分）', value: 2 }, { label: '经常烦躁易怒、情绪低落，血糖轻微波动（4分）', value: 4 }, { label: '频繁烦躁易怒、情绪低落，明显影响血糖控制（6分）', value: 6 }] },
    ],
    buildResult: buildDiabetesResult,
  },
  children: {
    code: 'children',
    title: '儿童体质辨识',
    subtitle: '0-6周岁专用，36题智能量化辨识（无音频）',
    audioEnabled: false,
    questionCount: 36,
    questions: [
      { content: '儿童面色红润、精神饱满，白天活动有力，无频繁乏力、嗜睡？', options: [{ label: '无异常，精神状态佳（0分）', value: 0 }, { label: '偶尔轻微乏力，活动后恢复快（2分）', value: 2 }, { label: '经常精神欠佳，活动后易疲惫（4分）', value: 4 }, { label: '频繁嗜睡、乏力，精神萎靡（6分）', value: 6 }] },
      { content: '儿童饮食规律，不挑食、不偏食，食量适中，消化正常？', options: [{ label: '饮食规律，无挑食，消化良好（0分）', value: 0 }, { label: '偶尔挑食，消化基本正常（2分）', value: 2 }, { label: '经常挑食、偏食，偶尔腹胀、消化不良（4分）', value: 4 }, { label: '严重挑食、偏食，频繁腹胀、积食（6分）', value: 6 }] },
      { content: '儿童睡眠规律，入睡顺利，夜间无频繁惊醒、盗汗？', options: [{ label: '睡眠规律，入睡快，夜间无异常（0分）', value: 0 }, { label: '偶尔入睡稍慢，或夜间轻微惊醒1次（2分）', value: 2 }, { label: '经常入睡困难，夜间惊醒2-3次，偶有盗汗（4分）', value: 4 }, { label: '频繁入睡困难，夜间频繁惊醒，盗汗明显（6分）', value: 6 }] },
      { content: '儿童大小便正常，大便成形、无便秘腹泻，小便清澈、无异味？', options: [{ label: '大小便正常，无异常（0分）', value: 0 }, { label: '偶尔轻微便秘或腹泻，小便基本正常（2分）', value: 2 }, { label: '经常便秘或腹泻，小便偶尔发黄、有轻微异味（4分）', value: 4 }, { label: '频繁便秘或腹泻，小便发黄、异味明显（6分）', value: 6 }] },
      { content: '儿童容易疲劳、乏力，活动后气喘、出汗多，不愿多活动？', options: [{ label: '无疲劳乏力，活动正常（0分）', value: 0 }, { label: '偶尔活动后疲劳，休息后快速恢复（2分）', value: 2 }, { label: '经常疲劳乏力，活动后气喘、出汗较多（4分）', value: 4 }, { label: '频繁疲劳，稍活动即气喘、大汗淋漓，不愿活动（6分）', value: 6 }] },
      { content: '儿童容易感冒，感冒后恢复缓慢，反复出现呼吸道不适？', options: [{ label: '很少感冒，感冒后恢复快（0分）', value: 0 }, { label: '偶尔感冒，恢复时间正常（2分）', value: 2 }, { label: '经常感冒，恢复时间较长（4分）', value: 4 }, { label: '频繁感冒，反复不愈，易引发支气管炎等（6分）', value: 6 }] },
      { content: '儿童面色苍白或萎黄，嘴唇、指甲颜色偏淡，无光泽？', options: [{ label: '面色红润，嘴唇、指甲有光泽（0分）', value: 0 }, { label: '偶尔面色偏淡，嘴唇、指甲光泽稍差（2分）', value: 2 }, { label: '经常面色苍白/萎黄，嘴唇、指甲颜色偏淡（4分）', value: 4 }, { label: '面色极度苍白/萎黄，嘴唇、指甲无光泽（6分）', value: 6 }] },
      { content: '儿童食欲不振，进食量少，即使勉强进食也易腹胀、消化不良？', options: [{ label: '食欲良好，进食正常，消化佳（0分）', value: 0 }, { label: '偶尔食欲欠佳，消化基本正常（2分）', value: 2 }, { label: '经常食欲不振，进食量少，偶尔腹胀（4分）', value: 4 }, { label: '长期食欲不振，进食极少，频繁腹胀、积食（6分）', value: 6 }] },
      { content: '儿童畏寒怕冷，手脚冰凉，尤其冬季或接触冷水后明显？', options: [{ label: '不畏寒，手脚温暖（0分）', value: 0 }, { label: '偶尔手脚微凉，无明显畏寒（2分）', value: 2 }, { label: '经常手脚冰凉，轻微畏寒（4分）', value: 4 }, { label: '频繁畏寒怕冷，手脚冰凉明显，需长时间保暖（6分）', value: 6 }] },
      { content: '儿童腹部怕凉，吃生冷食物后易腹痛、腹泻？', options: [{ label: '腹部不怕凉，吃生冷食物无异常（0分）', value: 0 }, { label: '偶尔吃生冷食物后轻微腹痛，无腹泻（2分）', value: 2 }, { label: '经常吃生冷食物后腹痛，偶尔腹泻（4分）', value: 4 }, { label: '一吃生冷食物即腹痛、腹泻，腹部需持续保暖（6分）', value: 6 }] },
      { content: '儿童大便稀溏，不成形，或排便时腹痛？', options: [{ label: '大便成形，无腹痛（0分）', value: 0 }, { label: '偶尔大便稀溏，无明显腹痛（2分）', value: 2 }, { label: '经常大便稀溏，偶尔排便腹痛（4分）', value: 4 }, { label: '频繁大便稀溏，排便时腹痛明显（6分）', value: 6 }] },
      { content: '儿童精神不振，嗜睡，面色偏白、无光泽？', options: [{ label: '精神饱满，无嗜睡，面色红润（0分）', value: 0 }, { label: '偶尔精神欠佳，轻微嗜睡（2分）', value: 2 }, { label: '经常精神不振，嗜睡，面色偏白（4分）', value: 4 }, { label: '频繁嗜睡、精神萎靡，面色苍白无光泽（6分）', value: 6 }] },
      { content: '儿童口干咽燥，经常喝水，嘴唇干裂、起皮？', options: [{ label: '无口干，嘴唇湿润（0分）', value: 0 }, { label: '偶尔口干，嘴唇轻微干燥（2分）', value: 2 }, { label: '经常口干咽燥，频繁喝水，嘴唇偶尔干裂（4分）', value: 4 }, { label: '频繁口干咽燥，嘴唇干裂明显、起皮（6分）', value: 6 }] },
      { content: '儿童手心、脚心发热，夜间盗汗，入睡后出汗明显？', options: [{ label: '手心脚心温度正常，无盗汗（0分）', value: 0 }, { label: '偶尔手心脚心发热，无明显盗汗（2分）', value: 2 }, { label: '经常手心脚心发热，夜间轻微盗汗（4分）', value: 4 }, { label: '频繁手心脚心发热，夜间盗汗严重，需更换衣物（6分）', value: 6 }] },
      { content: '儿童大便干结、便秘，排便困难？', options: [{ label: '大便成形，排便顺畅（0分）', value: 0 }, { label: '偶尔大便干结，排便基本顺畅（2分）', value: 2 }, { label: '经常大便干结，偶尔排便困难（4分）', value: 4 }, { label: '频繁便秘，大便干结坚硬，排便困难明显（6分）', value: 6 }] },
      { content: '儿童眼睛干涩、发红，容易烦躁、易怒？', options: [{ label: '眼睛湿润，无烦躁易怒（0分）', value: 0 }, { label: '偶尔眼睛轻微干涩，情绪基本平稳（2分）', value: 2 }, { label: '经常眼睛干涩、发红，偶尔烦躁易怒（4分）', value: 4 }, { label: '频繁眼睛干涩发红，烦躁易怒明显（6分）', value: 6 }] },
      { content: '儿童体型偏胖，腹部松软，身体困重，不愿活动？', options: [{ label: '体型适中，身体灵活，爱活动（0分）', value: 0 }, { label: '体型基本适中，偶尔身体困重（2分）', value: 2 }, { label: '体型偏胖，经常身体困重，活动量少（4分）', value: 4 }, { label: '体型明显偏胖，身体极度困重，几乎不愿活动（6分）', value: 6 }] },
      { content: '儿童痰多，晨起或饭后痰多明显，舌苔厚腻？', options: [{ label: '无痰，舌苔正常（0分）', value: 0 }, { label: '偶尔有少量痰，舌苔基本正常（2分）', value: 2 }, { label: '经常痰多，舌苔轻微厚腻（4分）', value: 4 }, { label: '频繁痰多，舌苔厚腻明显，口腔有黏腻感（6分）', value: 6 }] },
      { content: '儿童大便黏腻，粘马桶，不易冲净？', options: [{ label: '大便成形，不粘马桶（0分）', value: 0 }, { label: '偶尔大便轻微黏腻（2分）', value: 2 }, { label: '经常大便黏腻，偶尔粘马桶（4分）', value: 4 }, { label: '频繁大便黏腻，严重粘马桶，不易冲净（6分）', value: 6 }] },
      { content: '儿童食欲不振，进食后腹胀，容易积食、舌苔厚白？', options: [{ label: '食欲良好，进食后无腹胀，舌苔正常（0分）', value: 0 }, { label: '偶尔食欲欠佳，进食后轻微腹胀（2分）', value: 2 }, { label: '经常食欲不振，进食后腹胀明显，偶尔积食（4分）', value: 4 }, { label: '长期食欲不振，进食后严重腹胀，频繁积食（6分）', value: 6 }] },
      { content: '儿童面部油腻、易长湿疹、痱子，皮肤容易瘙痒？', options: [{ label: '皮肤清爽，无湿疹、痱子（0分）', value: 0 }, { label: '偶尔面部轻微油腻，无明显皮肤不适（2分）', value: 2 }, { label: '经常面部油腻，偶尔长湿疹、痱子，轻微瘙痒（4分）', value: 4 }, { label: '频繁面部油腻，经常长湿疹、痱子，瘙痒明显（6分）', value: 6 }] },
      { content: '儿童口苦、口臭，口腔有黏腻感，舌苔黄腻？', options: [{ label: '无口苦口臭，舌苔正常（0分）', value: 0 }, { label: '偶尔口苦，无明显口臭（2分）', value: 2 }, { label: '经常口苦、口臭，舌苔轻微黄腻（4分）', value: 4 }, { label: '频繁口苦、口臭明显，舌苔黄腻厚重（6分）', value: 6 }] },
      { content: '儿童小便发黄、浑浊，有异味？', options: [{ label: '小便清澈，无异味（0分）', value: 0 }, { label: '偶尔小便轻微发黄，无明显异味（2分）', value: 2 }, { label: '经常小便发黄，有轻微异味（4分）', value: 4 }, { label: '频繁小便发黄、浑浊，异味明显（6分）', value: 6 }] },
      { content: '儿童大便黏腻、排便不畅，或偶尔腹泻、大便发黄？', options: [{ label: '大便成形，排便顺畅（0分）', value: 0 }, { label: '偶尔大便轻微黏腻（2分）', value: 2 }, { label: '经常大便黏腻、排便不畅，偶尔腹泻（4分）', value: 4 }, { label: '频繁大便黏腻、腹泻，大便发黄（6分）', value: 6 }] },
      { content: '儿童容易烦躁、易怒，爱哭闹，情绪波动明显？', options: [{ label: '情绪平稳，不易哭闹（0分）', value: 0 }, { label: '偶尔烦躁，哭闹后快速平复（2分）', value: 2 }, { label: '经常烦躁、易怒，频繁哭闹（4分）', value: 4 }, { label: '频繁烦躁易怒，哭闹不止，难以安抚（6分）', value: 6 }] },
      { content: '儿童性格内向、沉默寡言，不愿与人交流、玩耍？', options: [{ label: '性格开朗，乐于与人交流玩耍（0分）', value: 0 }, { label: '偶尔内向，熟悉环境后可正常交流（2分）', value: 2 }, { label: '经常沉默寡言，不愿主动与人交流（4分）', value: 4 }, { label: '长期沉默寡言，拒绝与人交流、玩耍（6分）', value: 6 }] },
      { content: '儿童入睡困难，夜间易惊醒，多梦，睡眠质量差？', options: [{ label: '入睡顺利，睡眠安稳（0分）', value: 0 }, { label: '偶尔入睡稍慢，夜间无明显惊醒（2分）', value: 2 }, { label: '经常入睡困难，夜间偶尔惊醒、多梦（4分）', value: 4 }, { label: '频繁入睡困难，夜间频繁惊醒、多梦，睡眠极差（6分）', value: 6 }] },
      { content: '儿童食欲不振，情绪不好时更不愿进食？', options: [{ label: '食欲良好，不受情绪影响（0分）', value: 0 }, { label: '偶尔情绪不好时食欲轻微下降（2分）', value: 2 }, { label: '经常情绪不好时食欲不振（4分）', value: 4 }, { label: '频繁因情绪问题拒绝进食（6分）', value: 6 }] },
      { content: '儿童面色偏暗，嘴唇、指甲颜色偏紫暗，无光泽？', options: [{ label: '面色红润，嘴唇、指甲有光泽（0分）', value: 0 }, { label: '偶尔面色偏暗，嘴唇、指甲光泽稍差（2分）', value: 2 }, { label: '经常面色偏暗，嘴唇、指甲颜色偏紫暗（4分）', value: 4 }, { label: '频繁面色暗沉，嘴唇、指甲紫暗明显（6分）', value: 6 }] },
      { content: '儿童肢体容易出现瘀斑、淤青，轻微碰撞即发紫？', options: [{ label: '无瘀斑淤青，碰撞后不易发紫（0分）', value: 0 }, { label: '偶尔出现轻微瘀斑，碰撞后恢复快（2分）', value: 2 }, { label: '经常出现瘀斑，轻微碰撞即发紫（4分）', value: 4 }, { label: '频繁出现瘀斑淤青，轻微碰撞即严重发紫，恢复缓慢（6分）', value: 6 }] },
      { content: '儿童经常出现肢体麻木、活动不便（排除外伤）？', options: [{ label: '无肢体麻木，活动灵活（0分）', value: 0 }, { label: '偶尔轻微肢体麻木，活动后缓解（2分）', value: 2 }, { label: '经常肢体麻木，偶尔活动不便（4分）', value: 4 }, { label: '频繁肢体麻木，活动明显不便（6分）', value: 6 }] },
      { content: '儿童皮肤粗糙、干燥，或身上有暗红色胎记、血管瘤（排除外伤）？', options: [{ label: '无（0分）', value: 0 }, { label: '偶尔轻微（2分）', value: 2 }, { label: '经常明显（4分）', value: 4 }, { label: '总是存在（6分）', value: 6 }] },
      { content: '儿童容易过敏（如皮肤过敏、花粉过敏、食物过敏）？', options: [{ label: '无过敏史，不易过敏（0分）', value: 0 }, { label: '偶尔轻微过敏，无明显不适（2分）', value: 2 }, { label: '经常过敏，出现轻微皮疹、瘙痒（4分）', value: 4 }, { label: '频繁过敏，出现明显皮疹、瘙痒，甚至呼吸困难（6分）', value: 6 }] },
      { content: '儿童容易感冒，感冒后反复不愈，易引发哮喘、鼻炎？', options: [{ label: '很少感冒，感冒后恢复快（0分）', value: 0 }, { label: '偶尔感冒，恢复时间正常（2分）', value: 2 }, { label: '经常感冒，恢复缓慢，偶尔引发鼻炎（4分）', value: 4 }, { label: '频繁感冒，反复不愈，经常引发哮喘、鼻炎（6分）', value: 6 }] },
      { content: '儿童对某些食物（如牛奶、鸡蛋、海鲜）不耐受，食用后出现不适？', options: [{ label: '无食物不耐受，食用各类食物无不适（0分）', value: 0 }, { label: '偶尔食用某类食物后轻微不适（2分）', value: 2 }, { label: '经常食用某类食物后出现不适（如腹胀、皮疹）（4分）', value: 4 }, { label: '频繁对多种食物不耐受，食用后明显不适（6分）', value: 6 }] },
      { content: '儿童体质敏感，环境变化（如温度、气味）后易出现不适？', options: [{ label: '体质不敏感，环境变化无不适（0分）', value: 0 }, { label: '偶尔环境变化后轻微不适（2分）', value: 2 }, { label: '经常环境变化后出现不适（如哭闹、头晕）（4分）', value: 4 }, { label: '频繁环境变化后明显不适，难以适应（6分）', value: 6 }] },
    ],
    buildResult: buildChildrenResult,
  },
  fivePersonality: {
    code: 'fivePersonality',
    title: '五态人格测评',
    subtitle: '五态性格专用，20题唯一主导人格判定',
    audioEnabled: false,
    questionCount: 20,
    questions: [
      { content: '您平时性格偏内向、沉默寡言，遇事习惯藏在心里，不善于主动表达？', options: [{ label: '从不如此（0分）', value: 0 }, { label: '偶尔如此（2分）', value: 2 }, { label: '经常如此（4分）', value: 4 }, { label: '一直如此（6分）', value: 6 }] },
      { content: '您容易过度思虑、钻牛角尖，遇到事情反复纠结，难以释怀？', options: [{ label: '从不如此（0分）', value: 0 }, { label: '偶尔如此（2分）', value: 2 }, { label: '经常如此（4分）', value: 4 }, { label: '一直如此（6分）', value: 6 }] },
      { content: '您对负面信息过于敏感，容易多愁善感，情绪易低落？', options: [{ label: '从不如此（0分）', value: 0 }, { label: '偶尔如此（2分）', value: 2 }, { label: '经常如此（4分）', value: 4 }, { label: '一直如此（6分）', value: 6 }] },
      { content: '您习惯独处，不喜欢与人过多交往，独处时更能保持内心平和？', options: [{ label: '从不如此（0分）', value: 0 }, { label: '偶尔如此（2分）', value: 2 }, { label: '经常如此（4分）', value: 4 }, { label: '一直如此（6分）', value: 6 }] },
      { content: '您平时沉静内敛，心思缜密，善于观察细节，不喜欢张扬炫耀？', options: [{ label: '从不如此（0分）', value: 0 }, { label: '偶尔如此（2分）', value: 2 }, { label: '经常如此（4分）', value: 4 }, { label: '一直如此（6分）', value: 6 }] },
      { content: '您做事严谨认真，注重规则，不喜欢敷衍了事、半途而废？', options: [{ label: '从不如此（0分）', value: 0 }, { label: '偶尔如此（2分）', value: 2 }, { label: '经常如此（4分）', value: 4 }, { label: '一直如此（6分）', value: 6 }] },
      { content: '您情绪稳定，不易冲动，遇到事情能冷静思考、从容应对？', options: [{ label: '从不如此（0分）', value: 0 }, { label: '偶尔如此（2分）', value: 2 }, { label: '经常如此（4分）', value: 4 }, { label: '一直如此（6分）', value: 6 }] },
      { content: '您不喜欢热闹场合，偏爱安静环境，安静时更能集中注意力？', options: [{ label: '从不如此（0分）', value: 0 }, { label: '偶尔如此（2分）', value: 2 }, { label: '经常如此（4分）', value: 4 }, { label: '一直如此（6分）', value: 6 }] },
      { content: '您性格外向、活泼开朗，喜欢与人交往，善于主动表达自己的想法？', options: [{ label: '从不如此（0分）', value: 0 }, { label: '偶尔如此（2分）', value: 2 }, { label: '经常如此（4分）', value: 4 }, { label: '一直如此（6分）', value: 6 }] },
      { content: '您做事果断、雷厉风行，有主见，不喜欢拖拖拉拉、犹豫不决？', options: [{ label: '从不如此（0分）', value: 0 }, { label: '偶尔如此（2分）', value: 2 }, { label: '经常如此（4分）', value: 4 }, { label: '一直如此（6分）', value: 6 }] },
      { content: '您情绪饱满、乐观积极，遇到挫折能快速调整心态，不轻易消沉？', options: [{ label: '从不如此（0分）', value: 0 }, { label: '偶尔如此（2分）', value: 2 }, { label: '经常如此（4分）', value: 4 }, { label: '一直如此（6分）', value: 6 }] },
      { content: '您喜欢热闹场合，乐于参与集体活动，善于带动氛围？', options: [{ label: '从不如此（0分）', value: 0 }, { label: '偶尔如此（2分）', value: 2 }, { label: '经常如此（4分）', value: 4 }, { label: '一直如此（6分）', value: 6 }] },
      { content: '您性格活泼、思维敏捷，反应迅速，善于变通，不喜欢墨守成规？', options: [{ label: '从不如此（0分）', value: 0 }, { label: '偶尔如此（2分）', value: 2 }, { label: '经常如此（4分）', value: 4 }, { label: '一直如此（6分）', value: 6 }] },
      { content: '您善于表达、能言善辩，喜欢与人交流探讨，乐于分享自己的观点？', options: [{ label: '从不如此（0分）', value: 0 }, { label: '偶尔如此（2分）', value: 2 }, { label: '经常如此（4分）', value: 4 }, { label: '一直如此（6分）', value: 6 }] },
      { content: '您对新鲜事物充满好奇，乐于尝试，不喜欢一成不变的生活？', options: [{ label: '从不如此（0分）', value: 0 }, { label: '偶尔如此（2分）', value: 2 }, { label: '经常如此（4分）', value: 4 }, { label: '一直如此（6分）', value: 6 }] },
      { content: '您情绪易波动，容易兴奋，也能快速冷静下来，不钻牛角尖？', options: [{ label: '从不如此（0分）', value: 0 }, { label: '偶尔如此（2分）', value: 2 }, { label: '经常如此（4分）', value: 4 }, { label: '一直如此（6分）', value: 6 }] },
      { content: '您性格平和、心态豁达，不卑不亢，能从容应对生活中的各类事情？', options: [{ label: '从不如此（0分）', value: 0 }, { label: '偶尔如此（2分）', value: 2 }, { label: '经常如此（4分）', value: 4 }, { label: '一直如此（6分）', value: 6 }] },
      { content: '您善于调节情绪，遇到负面情绪能快速疏导，不钻牛角尖？', options: [{ label: '从不如此（0分）', value: 0 }, { label: '偶尔如此（2分）', value: 2 }, { label: '经常如此（4分）', value: 4 }, { label: '一直如此（6分）', value: 6 }] },
      { content: '您待人真诚、友善包容，能换位思考，善于与人和谐相处？', options: [{ label: '从不如此（0分）', value: 0 }, { label: '偶尔如此（2分）', value: 2 }, { label: '经常如此（4分）', value: 4 }, { label: '一直如此（6分）', value: 6 }] },
      { content: '您生活作息规律，能合理安排自己的生活，心态平和稳定？', options: [{ label: '从不如此（0分）', value: 0 }, { label: '偶尔如此（2分）', value: 2 }, { label: '经常如此（4分）', value: 4 }, { label: '一直如此（6分）', value: 6 }] },
    ],
    buildResult: buildFiveStateResult,
  },
};

export const SPECIAL_QUESTIONNAIRE_LIST = Object.values(SPECIAL_QUESTIONNAIRE_TEMPLATES);

export function getSpecialQuestionnaireTemplate(code) {
  return SPECIAL_QUESTIONNAIRE_TEMPLATES[code] || null;
}

export function buildSpecialQuestionnaireResult(code, answers = []) {
  const template = getSpecialQuestionnaireTemplate(code);
  if (!template) return null;
  return template.buildResult(answers, template);
}

export function getSpecialQuestionnaireDefaultOptions() {
  return [...DEFAULT_SCALE_OPTIONS];
}
