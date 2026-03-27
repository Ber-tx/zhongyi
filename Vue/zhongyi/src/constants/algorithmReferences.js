/**
 * 算法参考文献与出处
 * 根据项目实际使用的开源库和研究论文
 */

export const algorithmReferences = {
  wang: {
    title: '望诊 - 舌象分析',
    references: [
      {
        title: 'YOLOv8: Ultralytics 实时目标检测框架',
        authors: 'Jocher, G. et al.',
        year: 2023,
        source: '开源 - Ultralytics',
        url: 'https://github.com/ultralytics/ultralytics'
      },
      {
        title: '应用于医学图像识别（舌象、面诊等）的计算机视觉基础',
        authors: 'IEEE Computer Vision and Pattern Recognition',
        year: 2023,
        source: '学术会议',
        url: 'https://cvpr.thecvf.com/'
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
