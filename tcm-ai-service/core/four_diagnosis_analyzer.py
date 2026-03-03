"""
四诊合参综合诊断分析引擎
基于望、闻、问、切四个诊断板块的数据生成综合性医学建议
"""
import json
import logging

logger = logging.getLogger(__name__)


class FourDiagnosisAnalyzer:
    """四诊合参分析器"""
    
    def __init__(self):
        # 定义各诊法的权重
        self.wang_weight = 0.25   # 望诊权重
        self.wen_weight = 0.20    # 闻诊权重
        self.wen_weight_qa = 0.35 # 问诊权重（最高，因为包含最多症状信息）
        self.qie_weight = 0.20    # 切诊权重
    
    def generate_comprehensive_diagnosis(self, diagnosis_data: dict) -> dict:
        """
        生成综合诊断报告
        
        Args:
            diagnosis_data: {
                'wang_result': str,           # 望诊结论
                'wang_scores': dict,          # 望诊分数（可选）
                'wen_conclusion': str,        # 闻诊结论
                'wen_confidence': float,      # 闻诊置信度
                'wen_tags': list,             # 闻诊体质标签
                'wen_qa_conclusion': str,     # 问诊结论（如果有）
                'qie_hr': float,              # 切诊心率
                'qie_spo2': float,            # 切诊血氧
                'qie_suggestion': str         # 切诊建议
            }
        
        Returns:
            {
                'primary_constitution': str,      # 主要体质
                'secondary_constitutions': list,  # 次要体质
                'syndrome_analysis': str,         # 证候分析
                'comprehensive_suggestion': str,  # 综合建议
                'treatment_principles': list,     # 治疗原则
                'lifestyle_advice': list,         # 生活建议
                'follow_up_recommendations': str  # 随访建议
            }
        """
        try:
            logger.info("开始生成四诊合参综合诊断")
            
            # 1. 提取各诊法的关键信息
            wang_info = self._extract_wang_info(diagnosis_data.get('wang_result', ''))
            wen_info = self._extract_wen_info(
                diagnosis_data.get('wen_conclusion', ''),
                diagnosis_data.get('wen_tags', []),
                diagnosis_data.get('wen_confidence', 0)
            )
            wen_qa_info = self._extract_wen_qa_info(diagnosis_data.get('wen_qa_conclusion', ''))
            qie_info = self._extract_qie_info(
                diagnosis_data.get('qie_hr', 0),
                diagnosis_data.get('qie_spo2', 0),
                diagnosis_data.get('qie_suggestion', '')
            )
            
            # 2. 综合分析体质倾向
            constitution_analysis = self._analyze_constitution(
                wang_info, wen_info, wen_qa_info, qie_info
            )
            
            # 3. 生成证候分析
            syndrome_analysis = self._generate_syndrome_analysis(
                wang_info, wen_info, wen_qa_info, qie_info, constitution_analysis
            )
            
            # 4. 生成综合建议
            comprehensive_suggestion = self._generate_comprehensive_suggestion(
                constitution_analysis, syndrome_analysis, wen_qa_info, qie_info
            )
            
            # 5. 生成治疗原则
            treatment_principles = self._generate_treatment_principles(
                constitution_analysis, syndrome_analysis
            )
            
            # 6. 生成生活建议
            lifestyle_advice = self._generate_lifestyle_advice(
                constitution_analysis, wen_qa_info
            )
            
            # 7. 生成随访建议
            follow_up_recommendations = self._generate_follow_up(
                constitution_analysis, treatment_principles
            )
            
            result = {
                'success': True,
                'primary_constitution': constitution_analysis['primary'],
                'secondary_constitutions': constitution_analysis['secondary'],
                'syndrome_analysis': syndrome_analysis,
                'comprehensive_suggestion': comprehensive_suggestion,
                'treatment_principles': treatment_principles,
                'lifestyle_advice': lifestyle_advice,
                'follow_up_recommendations': follow_up_recommendations,
                'diagnostic_basis': {
                    'wang': wang_info,
                    'wen': wen_info,
                    'wen_qa': wen_qa_info,
                    'qie': qie_info
                }
            }
            
            logger.info(f"综合诊断生成成功: {constitution_analysis['primary']}")
            return result
            
        except Exception as e:
            logger.error(f"综合诊断生成异常: {str(e)}", exc_info=True)
            return {
                'success': False,
                'msg': f'诊断生成失败: {str(e)}'
            }
    
    def _extract_wang_info(self, wang_result: str) -> dict:
        """提取望诊信息"""
        # 关键词提取
        keywords = {
            '气血': '气血不足' in wang_result or '气血亏虚' in wang_result,
            '湿热': '湿热' in wang_result or '厚腻' in wang_result,
            '阴虚': '阴虚' in wang_result or '干燥' in wang_result,
            '阳虚': '阳虚' in wang_result or '淡白' in wang_result,
            '瘀血': '瘀血' in wang_result or '瘀' in wang_result,
            '脾胃': '脾胃' in wang_result
        }
        
        return {
            'raw_result': wang_result,
            'keywords': keywords,
            'confidence': 'high' if len(wang_result) > 20 else 'medium'
        }
    
    def _extract_wen_info(self, wen_conclusion: str, wen_tags: list, confidence: float) -> dict:
        """提取闻诊信息"""
        return {
            'raw_result': wen_conclusion,
            'tags': wen_tags,
            'confidence': confidence,
            'indicates_anxiety': any(tag in str(wen_tags) for tag in ['气滞', '心烦', '易怒'])
        }
    
    def _extract_wen_qa_info(self, wen_qa_conclusion: str) -> dict:
        """提取问诊信息"""
        # 简单的关键词提取
        keywords = {
            '乏力': '乏力' in wen_qa_conclusion or '疲劳' in wen_qa_conclusion,
            '便溏': '便溏' in wen_qa_conclusion,
            '便秘': '便秘' in wen_qa_conclusion or '干结' in wen_qa_conclusion,
            '怕冷': '怕冷' in wen_qa_conclusion,
            '手脚热': '手脚热' in wen_qa_conclusion,
            '容易出汗': '出汗' in wen_qa_conclusion,
            '口干': '口干' in wen_qa_conclusion
        }
        
        return {
            'raw_result': wen_qa_conclusion,
            'keywords': keywords,
            'symptom_count': sum(keywords.values())
        }
    
    def _extract_qie_info(self, hr: float, spo2: float, qie_suggestion: str) -> dict:
        """提取切诊信息"""
        hr_status = 'normal'
        if hr > 100:
            hr_status = 'high'  # 可能表示气虚、阳虚
        elif hr < 60:
            hr_status = 'low'   # 可能表示阳虚、血瘀
        
        return {
            'heart_rate': hr,
            'spo2': spo2,
            'hr_status': hr_status,
            'raw_suggestion': qie_suggestion
        }
    
    def _analyze_constitution(self, wang_info: dict, wen_info: dict, 
                             wen_qa_info: dict, qie_info: dict) -> dict:
        """综合分析体质倾向"""
        
        # 计算各种体质的得分
        scores = {
            '平和质': 50,
            '气虚质': 50,
            '阳虚质': 50,
            '阴虚质': 50,
            '痰湿质': 50,
            '湿热质': 50,
            '血瘀质': 50,
            '气郁质': 50
        }
        
        # 根据望诊调整
        if wang_info['keywords'].get('气血'):
            scores['气虚质'] += 20
        if wang_info['keywords'].get('湿热'):
            scores['湿热质'] += 25
        if wang_info['keywords'].get('阴虚'):
            scores['阴虚质'] += 20
        if wang_info['keywords'].get('阳虚'):
            scores['阳虚质'] += 20
        if wang_info['keywords'].get('瘀血'):
            scores['血瘀质'] += 20
        
        # 根据闻诊调整
        for tag in wen_info.get('tags', []):
            if '阴虚' in tag:
                scores['阴虚质'] += 15
            elif '阳虚' in tag:
                scores['阳虚质'] += 15
            elif '痰湿' in tag:
                scores['痰湿质'] += 15
            elif '湿热' in tag:
                scores['湿热质'] += 15
            elif '气滞' in tag:
                scores['气郁质'] += 15
        
        # 根据问诊调整
        if wen_qa_info['keywords'].get('便溏'):
            scores['脾阳虚质'] = scores.get('脾阳虚质', 50) + 20
            scores['阳虚质'] += 15
        if wen_qa_info['keywords'].get('便秘'):
            scores['阴虚质'] += 15
        if wen_qa_info['keywords'].get('怕冷'):
            scores['阳虚质'] += 20
        if wen_qa_info['keywords'].get('乏力'):
            scores['气虚质'] += 15
        
        # 根据切诊调整
        if qie_info['hr_status'] == 'high':
            scores['湿热质'] += 10
            scores['阴虚质'] += 10
        elif qie_info['hr_status'] == 'low':
            scores['阳虚质'] += 15
            scores['血瘀质'] += 10
        
        # 排序找出主要和次要体质
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        primary = sorted_scores[0][0]
        secondary = [item[0] for item in sorted_scores[1:3] if item[1] > 60]
        
        return {
            'primary': primary,
            'secondary': secondary,
            'scores': scores
        }
    
    def _generate_syndrome_analysis(self, wang_info: dict, wen_info: dict,
                                   wen_qa_info: dict, qie_info: dict,
                                   constitution_analysis: dict) -> str:
        """生成证候分析"""
        
        primary = constitution_analysis['primary']
        analysis = f"患者体质评估为【{primary}】。"
        
        # 根据各诊法补充分析
        if wang_info.get('raw_result'):
            analysis += f"舌象表现为{wang_info['raw_result']}。"
        
        if wen_info.get('raw_result'):
            analysis += f"音频分析提示{wen_info['raw_result']}。"
        
        # 症状总结
        symptoms = []
        if wen_qa_info['keywords'].get('乏力'):
            symptoms.append('乏力')
        if wen_qa_info['keywords'].get('便溏'):
            symptoms.append('便溏')
        if wen_qa_info['keywords'].get('怕冷'):
            symptoms.append('怕冷')
        if wen_qa_info['keywords'].get('口干'):
            symptoms.append('口干')
        
        if symptoms:
            analysis += f"主要症状包括：{', '.join(symptoms)}。"
        
        # 脉象分析
        if qie_info['heart_rate'] > 0:
            analysis += f"脉象提示平均心率 {qie_info['heart_rate']} bpm，"
            if qie_info['hr_status'] == 'high':
                analysis += "心率偏快，反映阴虚或热象。"
            elif qie_info['hr_status'] == 'low':
                analysis += "心率偏低，反映阳虚或血瘀倾向。"
            else:
                analysis += "心率基本平稳。"
        
        return analysis
    
    def _generate_comprehensive_suggestion(self, constitution_analysis: dict,
                                          syndrome_analysis: str,
                                          wen_qa_info: dict,
                                          qie_info: dict) -> str:
        """生成综合建议"""
        
        primary = constitution_analysis['primary']
        
        # 根据体质生成建议
        suggestions = {
            '平和质': '体质均衡，建议继续保持良好的生活作息和饮食习惯，定期检查。',
            '气虚质': '气虚体质，需要培养正气，建议加强运动，选择温和的锻炼方式；饮食以补气为主，可适当进补黄芪、西洋参等；避免过度疲劳。',
            '阳虚质': '阳虚体质，需要温阳扶阳，建议避免接触寒湿环境，戒烟限酒；饮食温阳为主，避免过食冷食；适当温阳灸疗。',
            '阴虚质': '阴虚体质，需要滋阴润燥，建议避免熬夜和过度劳累；饮食以滋阴为主，多食蜂蜜、银耳、雪耳等；少食辛辣刺激食物。',
            '痰湿质': '痰湿体质，需要健脾祛湿，建议加强运动，控制体重；饮食清淡，避免油腻厚腻之品；常喝薏米红豆粥等祛湿食物。',
            '湿热质': '湿热体质，需要清热祛湿，建议清淡饮食，避免辛辣刺激；戒烟限酒；适当运动促进代谢。',
            '血瘀质': '血瘀体质，需要活血化瘀，建议加强运动，促进血液循环；饮食以活血为主，可适当食用黑木耳、海带等；避免久坐。',
            '气郁质': '气郁体质，需要疏肝解郁，建议调畅情志，适当参加娱乐活动；坚持运动，特别是有氧运动；饮食以疏肝为主。'
        }
        
        suggestion = suggestions.get(primary, f'针对{primary}，建议加强健康管理。')
        
        return suggestion
    
    def _generate_treatment_principles(self, constitution_analysis: dict,
                                      syndrome_analysis: str) -> list:
        """生成治疗原则"""
        
        primary = constitution_analysis['primary']
        
        principles = {
            '平和质': ['维持平衡'],
            '气虚质': ['健脾益气', '增强体质'],
            '阳虚质': ['温阳扶阳', '培养阳气'],
            '阴虚质': ['滋阴润燥', '补充阴液'],
            '痰湿质': ['健脾祛湿', '化痰利湿'],
            '湿热质': ['清热祛湿', '利湿排毒'],
            '血瘀质': ['活血化瘀', '疏通经络'],
            '气郁质': ['疏肝解郁', '调畅气机']
        }
        
        return principles.get(primary, ['调理脾胃', '增强体质'])
    
    def _generate_lifestyle_advice(self, constitution_analysis: dict,
                                  wen_qa_info: dict) -> list:
        """生成生活建议"""
        
        advice = []
        
        # 作息建议
        advice.append('保持规律作息，避免熬夜（建议 22:30 前入睡）')
        
        # 运动建议
        if constitution_analysis['primary'] in ['气虚质', '阳虚质']:
            advice.append('适度运动，建议tai chi、八段锦等温和功法，避免过度消耗')
        else:
            advice.append('坚持适度运动，每天 30 分钟，支持有氧运动')
        
        # 饮食建议
        if '湿热' in constitution_analysis['primary']:
            advice.append('饮食清淡，避免油腻、辛辣、刺激食物；忌烟酒')
        elif '阳虚' in constitution_analysis['primary']:
            advice.append('饮食温阳，可食用羊肉、生姜、肉桂等温性食物')
        elif '阴虚' in constitution_analysis['primary']:
            advice.append('饮食滋阴，可食用冬瓜、绿豆、银耳等；忌烤烤炸食物')
        
        # 情志建议
        advice.append('调畅情志，避免过度压力和焦虑；可适当禅修、瑜伽')
        
        # 环境建议
        if '阳虚' in constitution_analysis['primary']:
            advice.append('避免长期接触冷湿环境；冬季注意保暖')
        elif '湿热' in constitution_analysis['primary']:
            advice.append('避免在潮湿环境中工作；居住环境通风干燥')
        
        return advice
    
    def _generate_follow_up(self, constitution_analysis: dict,
                           treatment_principles: list) -> str:
        """生成随访建议"""
        
        follow_up = "建议在 1-2 周后进行随访评估，观察体质改善情况。"
        follow_up += "如症状未见改善或加重，请及时就医咨询专業医生。"
        follow_up += "建议定期（每 3-6 个月）进行体质评估，动态调整健康管理方案。"
        
        return follow_up
