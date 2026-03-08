<template>
  <div class="report-container">
    <!-- 返回按钮 -->
    <div class="header">
      <el-button @click="goBack" icon="ArrowLeft">返回</el-button>
      <h1>四诊合参诊断报告</h1>
      <el-button type="primary" @click="exportPDF" :loading="isExporting" icon="Download">
        导出PDF
      </el-button>
    </div>

    <!-- 加载状态 -->
    <div v-if="isLoading" class="loading-container">
      <el-skeleton :rows="8" animated />
    </div>

    <!-- 报告内容 -->
    <div v-else-if="reportData" class="report-content" ref="reportRef">
      <!-- 患者信息章节 -->
      <section class="report-section patient-info">
        <h2>患者信息</h2>
        <el-descriptions :column="4" border>
          <el-descriptions-item label="姓名">
            {{ reportData.patientInfo.name }}
          </el-descriptions-item>
          <el-descriptions-item label="性别">
            {{ reportData.patientInfo.gender }}
          </el-descriptions-item>
          <el-descriptions-item label="年龄">
            {{ reportData.patientInfo.age || '' }}岁
          </el-descriptions-item>
          <el-descriptions-item label="生日">
            {{ reportData.patientInfo.birthday || '' }}
          </el-descriptions-item>
          <el-descriptions-item label="住址" :span="3">
            {{ reportData.patientInfo.address }}
          </el-descriptions-item>
        </el-descriptions>
      </section>

      <!-- 四诊初步诊断章节 -->
      <section class="report-section diagnosis">
        <h2>四诊初步诊断</h2>

        <!-- 望诊 -->
        <div class="diagnosis-item">
          <h3>望诊（舌象分析）</h3>
          <el-card>
            <div v-if="reportData.diagnosis.wang && reportData.diagnosis.wang.imageUrl" class="diagnosis-image">
              <img :src="reportData.diagnosis.wang.imageUrl" alt="舌象图片" style="max-width: 100%; height: auto;" />
              <p><strong>舌苔图</strong></p>
            </div>
            <p class="diagnosis-result">
              
              {{ reportData.diagnosis.wang ? reportData.diagnosis.wang.result : '暂未进行舌象检查，请补充望诊数据以获得更准确的诊断。' }}
            </p>
          </el-card>
        </div>

        <!-- 闻诊 -->
        <div class="diagnosis-item">
          <h3>闻诊（体质诊断）</h3>
          <el-card>
            <el-row v-if="reportData.diagnosis.wen_audio" :gutter="20">
              <el-col :span="12">
                <div>
                  <strong>诊断结论：</strong>
                  {{ reportData.diagnosis.wen_audio.conclusion }}
                </div>
                <div v-if="reportData.diagnosis.wen_audio.confidence">
                  <strong>置信度：</strong>
                  {{ (reportData.diagnosis.wen_audio.confidence * 100).toFixed(1) }}%
                </div>
              </el-col>
              <el-col :span="12">
                <div v-if="reportData.diagnosis.wen_audio.tags">
                  <strong>体质标签：</strong>
                  <el-tag
                    v-for="tag in reportData.diagnosis.wen_audio.tags"
                    :key="tag"
                    effect="light"
                    class="tag"
                  >
                    {{ tag }}
                  </el-tag>
                </div>
                <div v-if="reportData.diagnosis.wen_audio.audioUrl" style="margin-top: 10px;">
                  <strong>音频：</strong>
                  <audio controls style="width: 100%;">
                    <source :src="reportData.diagnosis.wen_audio.audioUrl" type="audio/wav">
                    您的浏览器不支持音频播放。
                  </audio>
                </div>
              </el-col>
            </el-row>
            <div v-else>
              暂未进行声音分析，请补充闻诊数据。
            </div>
          </el-card>
        </div>

        <!-- 问诊 -->
        <div class="diagnosis-item">
          <h3>问诊（症状问卷）</h3>
          <el-card>
            <p>{{ reportData.diagnosis.wen_questionnaire ? reportData.diagnosis.wen_questionnaire.conclusion : '暂未进行症状问卷调查，请补充问诊数据。' }}</p>
          </el-card>
        </div>

        <!-- 切诊 -->
        <div class="diagnosis-item">
          <h3>切诊（脉搏检测）</h3>
          <el-card>
            <el-row v-if="reportData.diagnosis.qie" :gutter="20">
              <el-col :span="12">
                <div>
                  <strong>心率：</strong>
                  {{ reportData.diagnosis.qie.heartRate }}
                  <span class="unit">bpm</span>
                </div>
                <div>
                  <strong>血氧：</strong>
                  {{ reportData.diagnosis.qie.spo2 }}
                  <span class="unit">%</span>
                </div>
              </el-col>
              <el-col :span="12">
                <div>
                  <strong>信号有效率：</strong>
                  {{ reportData.diagnosis.qie.validRate }}
                  <span class="unit">%</span>
                </div>
                <div>
                  <strong>采样数：</strong>
                  {{ reportData.diagnosis.qie.sampleCount }}
                </div>
              </el-col>
            </el-row>
            <div v-if="reportData.diagnosis.qie && reportData.diagnosis.qie.tcmSuggestion" class="tcm-suggestion">
              <strong>中医建议：</strong>
              <p>{{ reportData.diagnosis.qie.tcmSuggestion }}</p>
            </div>
            <div v-else-if="!reportData.diagnosis.qie">
              暂未进行脉搏检测，请补充切诊数据。
            </div>
          </el-card>
        </div>
      </section>

      <!-- 综合诊断建议章节 -->
      <section class="report-section synthesis">
        <h2>综合诊断建议</h2>
        <el-card shadow="hover">
          <div class="synthesis-content" v-html="reportData.synthesis ? markdownToHtml(reportData.synthesis) : '暂无综合诊断建议，请确保所有四诊数据完整。'"></div>
        </el-card>
      </section>

      <!-- 报告生成时间 -->
      <section class="report-footer">
        <p>报告生成时间：{{ formatDate(reportData.createdAt) }}</p>
        <p class="disclaimer">本报告仅供参考，请在医生指导下使用。</p>
      </section>
    </div>

    <!-- 无数据状态 -->
    <div v-else class="no-data">
      <el-empty description="未找到报告数据" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter, useRoute } from "vue-router";
import { ElMessage } from "element-plus";
import axios from "axios";
import html2pdf from "html2pdf.js";
import { marked } from "marked";

const router = useRouter();
const route = useRoute();

const reportData = ref(null);
const isLoading = ref(false);
const isExporting = ref(false);
const reportRef = ref(null);

/**
 * 页面挂载时获取报告数据
 */
onMounted(async () => {
  const patientId = route.query.id || localStorage.getItem('current_patient_id')

  if (!patientId) {
    ElMessage.error("缺少患者ID，请先完成四诊操作")
    goBack()
    return
  }

  await fetchReportData(patientId)
});

/**
 * 从API获取报告数据
 */
const fetchReportData = async (patientId) => {
  isLoading.value = true;
  try {
    const idCard = localStorage.getItem('current_patient_idCard') || '';
    const response = await axios.get("/api/report/get-diagnosis", {
      params: {
        patientId: Number(patientId),  // 确保转为数字
        idCard: idCard
      },
    });

    if (response.data.code !== 200 && !response.data.success) {
      ElMessage.error(response.data.msg || "获取报告失败");
      return;
    }

    // 如果没有synthesis数据，则重新生成
    if (!response.data.data.synthesis) {
      await generateReport(patientId);
    } else {
      reportData.value = response.data.data;
    }
  } catch (error) {
    console.error("获取报告失败:", error);
    ElMessage.error("获取报告失败：" + error.message);
  } finally {
    isLoading.value = false;
  }
};

/**
 * 生成综合诊断报告
 */
const generateReport = async (patientId) => {
  try {
    const idCard = localStorage.getItem('current_patient_idCard') || '';  // 获取身份证
    const response = await axios.post("/api/report/generate", {
      patientId: Number(patientId),  // 确保转为数字
      idCard: idCard
    });

    if (response.data.code === 200 || response.data.success) {
      reportData.value = response.data.data;
      ElMessage.success("报告生成成功");
    } else {
      ElMessage.error(response.data.msg || "报告生成失败");
    }
  } catch (error) {
    console.error("生成报告失败:", error);
    ElMessage.error("生成报告失败：" + error.message);
  }
};

/**
 * 导出PDF
 */
const exportPDF = () => {
  if (!reportRef.value) {
    ElMessage.error("报告数据加载失败");
    return;
  }

  isExporting.value = true;

  try {
    const element = reportRef.value;
    const opt = {
      margin: 10,
      filename: `诊断报告_${reportData.value.patientInfo.name}_${formatDate(reportData.value.createdAt)}.pdf`,
      image: { type: "jpeg", quality: 0.98 },
      html2canvas: { scale: 2 },
      jsPDF: { orientation: "portrait", unit: "mm", format: "a4" },
    };

    html2pdf()
      .set(opt)
      .from(element)
      .save()
      .finally(() => {
        isExporting.value = false;
        ElMessage.success("PDF导出成功");
      });
  } catch (error) {
    isExporting.value = false;
    console.error("导出PDF失败:", error);
    ElMessage.error("导出PDF失败：" + error.message);
  }
};

/**
 * Markdown转HTML
 */
const markdownToHtml = (markdown) => {
  if (!markdown) return "";
  return marked.parse(markdown);
};

/**
 * 格式化日期
 */
const formatDate = (timestamp) => {
  if (!timestamp) return "";
  const date = new Date(timestamp);
  return date.toLocaleDateString("zh-CN") + " " + date.toLocaleTimeString("zh-CN");
};

/**
 * 返回诊断选择页面
 */
const goBack = () => {
  router.push({ path: "/detect", query: { id: route.query.id } });
};
</script>

<style scoped>
.report-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  min-height: 100vh;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.header h1 {
  flex: 1;
  text-align: center;
  margin: 0;
  color: #333;
}

.report-content {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.report-section {
  padding: 30px;
  border-bottom: 1px solid #eee;
}

.report-section:last-child {
  border-bottom: none;
}

.report-section h2 {
  color: #1e6ba8;
  font-size: 20px;
  margin-bottom: 20px;
  border-bottom: 3px solid #1e6ba8;
  padding-bottom: 10px;
}

.report-section h3 {
  color: #2c3e50;
  font-size: 16px;
  margin-top: 20px;
  margin-bottom: 15px;
}

.diagnosis-item {
  margin-bottom: 20px;
}

.diagnosis-image {
  text-align: center;
  margin-bottom: 15px;
}

.diagnosis-image img {
  max-width: 100%;
  max-height: 300px;
  border-radius: 4px;
}

.diagnosis-result {
  color: #555;
  line-height: 1.8;
  margin: 0;
}

.tag {
  margin: 5px 5px 5px 0;
}

.unit {
  color: #999;
  font-size: 14px;
  margin-left: 5px;
}

.tcm-suggestion {
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #eee;
}

.synthesis-content {
  line-height: 1.8;
  color: #333;
  font-size: 14px;
}

.synthesis-content :deep(h3) {
  color: #1e6ba8;
  margin-top: 15px;
  margin-bottom: 10px;
}

.synthesis-content :deep(h4) {
  color: #2c3e50;
  margin-top: 12px;
  margin-bottom: 8px;
}

.synthesis-content :deep(ul),
.synthesis-content :deep(ol) {
  margin: 10px 0;
  padding-left: 20px;
}

.synthesis-content :deep(li) {
  margin: 5px 0;
}

.synthesis-content :deep(strong) {
  color: #1e6ba8;
}

.report-footer {
  padding: 30px;
  background: #f9f9f9;
  text-align: center;
  color: #999;
  font-size: 12px;
}

.report-footer p {
  margin: 5px 0;
}

.disclaimer {
  color: #e74c3c;
  font-size: 11px;
}

.loading-container {
  padding: 30px;
  background: white;
  border-radius: 8px;
}

.no-data {
  padding: 60px 20px;
  text-align: center;
}

@media (max-width: 768px) {
  .report-container {
    padding: 10px;
  }

  .header {
    flex-direction: column;
    gap: 10px;
  }

  .header h1 {
    font-size: 18px;
    margin: 10px 0;
  }

  .report-section {
    padding: 20px;
  }

  .report-section h2 {
    font-size: 18px;
  }
}
</style>
