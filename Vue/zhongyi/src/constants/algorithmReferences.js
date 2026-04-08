/**
 * 算法参考文献与出处
 * 根据项目实际使用的开源库和研究论文
 */

export const algorithmReferences = {
  wang: {
    title: '望诊 - 舌象分析',
    references: [
      {
        title: 'Qwen2-VL Technical Report',
        authors: 'Qwen Team',
        year: 2024,
        source: '阿里通义千问视觉语言模型',
        url: 'https://qwenlm.github.io/blog/qwen2-vl/'
      },
      {
        title: '舌诊数字化与中医舌象图像分析研究',
        authors: '中医药图像分析研究团队',
        year: 2022,
        source: '中医药数字化研究',
        url: ''
      },
      {
        title: 'OpenAI API-Compatible Vision Model Usage Guide',
        authors: '阿里云百炼 / DashScope',
        year: 2024,
        source: '视觉模型接入文档',
        url: 'https://www.alibabacloud.com/help/zh/model-studio'
      }
    ]
  },

  wen_audio: {
    title: '闻诊 - 音频声学分析',
    references: [
      {
        title: 'Vocal Acoustic Analysis (VAA) - 语音声学基础参数分析',
        authors: 'Teixeira, J. et al.',
        year: 2013,
        source: 'Procedia Technology - ScienceDirect',
        url: 'https://doi.org/10.1016/j.protcy.2013.12.003'
      },
      {
        title: 'PraatScripts - 开源语言学与语音信号处理工具库',
        authors: 'Feinberg, D.',
        year: 2021,
        source: 'GitHub - drfeinberg/PraatScripts',
        url: 'https://github.com/drfeinberg/PraatScripts'
      }
    ]
  },

  wen_questionnaire: {
    title: '问诊 - 中医体质评估',
    references: [
        {
          title: '中医体质分类与判定 - 国家标准（GB/T 16180-2008）',
          authors: '王琦教授及体质学研究团队',
          year: 2008,
          source: '国家标准化管理委员会',
          url: 'https://openstd.samr.gov.cn/bzgk/gb/newGbInfo?hcno=827D6D266BA52A2983F93638DA871028'
        }
    ]
  },

  qie: {
    title: '切诊 - 脉象数字化采集与分析',
    references: [
      {
        title: 'MAX30102 心率/血氧传感芯片 - 脉象采集硬件基础',
        authors: 'aromring (开源贡献者)',
        year: 2024,
        source: 'GitHub - aromring/MAX30102_by_RF',
        url: 'https://github.com/aromring/MAX30102_by_RF'
      }
    ]
  }
};
