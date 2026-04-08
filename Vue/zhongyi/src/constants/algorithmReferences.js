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
        title: 'Sound as a bell: a deep learning approach for health status classification through speech acoustic biomarkers',
        authors: 'Wang et al.',
        year: 2024,
        source: 'Chinese Medicine 19, 101（MFCC 主特征，Conv2D 验证集准确率 84.93%）',
        url: 'https://doi.org/10.1186/s13020-024-00973-3'
      },
      {
        title: 'Vocal Acoustic Analysis - Jitter, Shimmer and HNR Parameters',
        authors: 'Teixeira et al.',
        year: 2013,
        source: 'Procedia Technology 9, 1112-1122（经典声学病理诊断特征）',
        url: 'https://doi.org/10.1016/j.protcy.2013.12.124'
      },
      {
        title: 'PraatScripts',
        authors: 'Feinberg, D.',
        year: 2021,
        source: 'GitHub（parselmouth 提取 Jitter/Shimmer/HNR 实现参考）',
        url: 'https://github.com/drfeinberg/PraatScripts'
      },
      {
        title: 'Classification research of TCM pulse conditions based on multi-label voice analysis',
        authors: 'Shen et al.',
        year: 2024,
        source: 'Journal of Traditional Chinese Medical Sciences 11(2), 172-179（多标签模型准确率 92.74%）',
        url: 'https://doi.org/10.1016/j.jtcms.2024.03.008'
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
