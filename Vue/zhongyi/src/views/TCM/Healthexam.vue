<template>
  <div class="tcm-panel health-panel">
    <div class="panel-title-bar">
      <span class="panel-step">居民体检管理</span>
      <span class="panel-hint">录入居民综合体检数据，支持查询与档案管理。标注 * 为必填，其余均为选填。</span>
    </div>

    <!-- 视图切换：列表 / 录入 -->
    <div v-if="view === 'list'" class="list-view">
      <div class="toolbar-row">
        <el-input v-model="keyword" placeholder="搜索姓名 / 身份证"
          clearable style="width:240px" @keyup.enter="loadList(1)" @clear="loadList(1)">
          <template #append><el-button @click="loadList(1)">查询</el-button></template>
        </el-input>
        <el-button class="btn-green" @click="openNewExam">＋ 新增体检</el-button>
        <span class="record-count">共 {{ total }} 位居民档案</span>
      </div>

      <div class="table-wrap">
        <el-table :data="examList" v-loading="loading" class="tcm-table" stripe
          empty-text="暂无体检记录，点击「新增体检」录入" height="100%">
          <el-table-column prop="id" label="编号" width="65" />
          <el-table-column prop="patientName" label="姓名" width="88" />
          <el-table-column prop="patientGender" label="性别" width="55" />
          <el-table-column prop="patientAge" label="年龄" width="60">
            <template #default="{ row }">{{ row.patientAge ? row.patientAge + '岁' : '—' }}</template>
          </el-table-column>
          <el-table-column prop="patientIdCard" label="身份证号" min-width="165" show-overflow-tooltip />
          <el-table-column label="主要体征" min-width="180">
            <template #default="{ row }">
              <span v-if="row.bloodPressureSystolic" class="badge">
                血压 {{ row.bloodPressureSystolic }}/{{ row.bloodPressureDiastolic }}
              </span>
              <span v-if="row.bmi" class="badge">BMI {{ row.bmi }}</span>
              <span v-if="row.fastingBloodGlucose" class="badge">
                血糖 {{ row.fastingBloodGlucose }}
              </span>
            </template>
          </el-table-column>
          <el-table-column label="体质结论" width="90">
            <template #default="{ row }">
              <el-tag v-if="row.constitutionType" type="warning" size="small">{{ row.constitutionType }}</el-tag>
              <span v-else class="text-muted">待辨识</span>
            </template>
          </el-table-column>
          <el-table-column label="体检日期" width="115">
            <template #default="{ row }">{{ fmtDate(row.examDate || row.createTime) }}</template>
          </el-table-column>
          <el-table-column label="操作" width="150" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" size="small" link @click="openEdit(row)">编辑</el-button>
              <el-button type="success" size="small" link @click="goDetect(row)">四诊辨识</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <div class="pagination-wrap">
        <el-pagination v-model:current-page="page" :page-size="12" :total="total"
          layout="prev, pager, next, total" @current-change="loadList" background small />
      </div>
    </div>

    <!-- 录入/编辑表单 -->
    <div v-else class="form-view">
      <div class="form-header">
        <el-button size="small" @click="view = 'list'">← 返回列表</el-button>
        <span class="form-title">{{ editId ? '编辑体检档案' : '新增体检档案' }}</span>
        <el-button size="small" class="btn-primary" :loading="saving" @click="saveExam">
          💾 保存档案
        </el-button>
      </div>

      <el-tabs v-model="activeTab" class="exam-tabs" type="border-card">

        <!-- Tab 1：基本信息 -->
        <el-tab-pane label="基本信息" name="basic">
          <el-form :model="form" label-width="95px" class="tcm-form" ref="formRef">
            <div class="section-heading">患者信息（必填）</div>
            <el-row :gutter="16">
              <el-col :span="6">
                <el-form-item label="姓名 *" prop="patientName"
                  :rules="[{required:true,message:'必填'}]">
                  <el-input v-model="form.patientName" placeholder="真实姓名" />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="性别 *">
                  <el-radio-group v-model="form.patientGender">
                    <el-radio value="男">男</el-radio>
                    <el-radio value="女">女</el-radio>
                  </el-radio-group>
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="出生日期 *">
                  <el-date-picker v-model="form.patientBirthday" type="date"
                    placeholder="选择" style="width:100%" value-format="YYYY-MM-DD" />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="身份证号 *">
                  <el-input v-model="form.patientIdCard" placeholder="18位" maxlength="18" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="16">
              <el-col :span="12">
                <el-form-item label="联系电话">
                  <el-input v-model="form.phone" placeholder="选填" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="住址">
                  <el-input v-model="form.address" placeholder="选填" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="16">
              <el-col :span="6">
                <el-form-item label="职业">
                  <el-input v-model="form.occupation" placeholder="选填" />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="婚姻状况">
                  <el-select v-model="form.marital" placeholder="选填" clearable>
                    <el-option label="未婚" value="未婚" /><el-option label="已婚" value="已婚" />
                    <el-option label="离异" value="离异" /><el-option label="丧偶" value="丧偶" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="体检日期">
                  <el-date-picker v-model="form.examDate" type="date"
                    placeholder="今日" style="width:100%" value-format="YYYY-MM-DD" />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="体质结论">
                  <el-select v-model="form.constitutionType" placeholder="可由辨识获得" clearable>
                    <el-option v-for="c in constitutions" :key="c" :label="c" :value="c" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>

            <div class="section-heading">生活习惯</div>
            <el-row :gutter="16">
              <el-col :span="6">
                <el-form-item label="吸烟">
                  <el-select v-model="form.smoking" clearable placeholder="选填">
                    <el-option label="不吸烟" value="不吸烟" /><el-option label="偶尔" value="偶尔吸烟" />
                    <el-option label="规律吸烟" value="规律吸烟" /><el-option label="已戒烟" value="已戒烟" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="饮酒">
                  <el-select v-model="form.drinking" clearable placeholder="选填">
                    <el-option label="不饮酒" value="不饮酒" /><el-option label="偶尔" value="偶尔饮酒" />
                    <el-option label="规律饮酒" value="规律饮酒" /><el-option label="已戒酒" value="已戒酒" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="运动频率">
                  <el-select v-model="form.exercise" clearable placeholder="选填">
                    <el-option label="几乎不运动" value="几乎不运动" />
                    <el-option label="每周1-2次" value="每周1-2次" />
                    <el-option label="每周3次以上" value="每周3次以上" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="睡眠质量">
                  <el-select v-model="form.sleepQuality" clearable placeholder="选填">
                    <el-option label="良好" value="良好" /><el-option label="一般" value="一般" />
                    <el-option label="较差（失眠）" value="较差" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>

            <div class="section-heading">病史信息</div>
            <el-row :gutter="16">
              <el-col :span="8">
                <el-form-item label="既往病史">
                  <el-input v-model="form.medicalHistory" type="textarea" :rows="2"
                    placeholder="如：高血压、糖尿病（无则留空）" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="家族病史">
                  <el-input v-model="form.familyHistory" type="textarea" :rows="2"
                    placeholder="如：父亲高血压（无则留空）" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="过敏史">
                  <el-input v-model="form.allergyHistory" type="textarea" :rows="2"
                    placeholder="药物/食物过敏（无则留空）" />
                </el-form-item>
              </el-col>
            </el-row>
          </el-form>
        </el-tab-pane>

        <!-- Tab 2：体格检查 -->
        <el-tab-pane label="体格检查" name="physical">
          <el-form :model="form" label-width="110px" class="tcm-form">
            <div class="section-heading">身体测量</div>
            <el-row :gutter="16">
              <el-col :span="6">
                <el-form-item label="身高 (cm)">
                  <el-input-number v-model="form.height" :min="50" :max="250" :precision="1"
                    style="width:100%" placeholder="选填" @change="calcBMI" />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="体重 (kg)">
                  <el-input-number v-model="form.weight" :min="10" :max="300" :precision="1"
                    style="width:100%" placeholder="选填" @change="calcBMI" />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="BMI">
                  <el-input v-model="form.bmi" readonly placeholder="自动计算">
                    <template #suffix>
                      <span :class="bmiClass">{{ bmiLabel }}</span>
                    </template>
                  </el-input>
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="腰围 (cm)">
                  <el-input-number v-model="form.waistCircumference" :min="30" :max="200" :precision="1"
                    style="width:100%" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="16">
              <el-col :span="6">
                <el-form-item label="臀围 (cm)">
                  <el-input-number v-model="form.hipCircumference" :min="30" :max="200" :precision="1"
                    style="width:100%" />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="体温 (℃)">
                  <el-input-number v-model="form.temperature" :min="34" :max="42" :precision="1"
                    style="width:100%" />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="心率 (bpm)">
                  <el-input-number v-model="form.heartRate" :min="30" :max="220"
                    style="width:100%" />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="血氧 SpO₂ (%)">
                  <el-input-number v-model="form.spo2" :min="70" :max="100" :precision="1"
                    style="width:100%" />
                </el-form-item>
              </el-col>
            </el-row>

            <div class="section-heading">血压</div>
            <el-row :gutter="16">
              <el-col :span="6">
                <el-form-item label="收缩压 (mmHg)">
                  <el-input-number v-model="form.bloodPressureSystolic" :min="50" :max="300"
                    style="width:100%" />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="舒张压 (mmHg)">
                  <el-input-number v-model="form.bloodPressureDiastolic" :min="30" :max="200"
                    style="width:100%" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="血压评估">
                  <el-input :value="bpLabel" readonly placeholder="自动评估" />
                </el-form-item>
              </el-col>
            </el-row>

            <div class="section-heading">体格检查结论</div>
            <el-row :gutter="16">
              <el-col :span="8">
                <el-form-item label="视力（左）">
                  <el-input v-model="form.visionLeft" placeholder="如 5.0" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="视力（右）">
                  <el-input v-model="form.visionRight" placeholder="如 5.0" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="听力">
                  <el-select v-model="form.hearing" clearable placeholder="选填">
                    <el-option label="正常" value="正常" />
                    <el-option label="轻度下降" value="轻度下降" />
                    <el-option label="明显下降" value="明显下降" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>
          </el-form>
        </el-tab-pane>

        <!-- Tab 3：实验室检查 -->
        <el-tab-pane label="实验室检查" name="lab">
          <el-form :model="form" label-width="130px" class="tcm-form">
            <div class="section-heading">血糖代谢</div>
            <el-row :gutter="16">
              <el-col :span="6">
                <el-form-item label="空腹血糖 (mmol/L)">
                  <el-input-number v-model="form.fastingBloodGlucose" :min="0" :max="50" :precision="2"
                    style="width:100%" />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="餐后2h血糖">
                  <el-input-number v-model="form.postprandialGlucose" :min="0" :max="50" :precision="2"
                    style="width:100%" />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="糖化血红蛋白 (%)">
                  <el-input-number v-model="form.hba1c" :min="0" :max="25" :precision="1"
                    style="width:100%" />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="血糖评估">
                  <el-input :value="glucoseLabel" readonly placeholder="自动评估" />
                </el-form-item>
              </el-col>
            </el-row>

            <div class="section-heading">血脂四项</div>
            <el-row :gutter="16">
              <el-col :span="6">
                <el-form-item label="总胆固醇 (mmol/L)">
                  <el-input-number v-model="form.totalCholesterol" :min="0" :max="20" :precision="2"
                    style="width:100%" />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="甘油三酯 (mmol/L)">
                  <el-input-number v-model="form.triglycerides" :min="0" :max="20" :precision="2"
                    style="width:100%" />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="HDL (mmol/L)">
                  <el-input-number v-model="form.hdl" :min="0" :max="10" :precision="2"
                    style="width:100%" />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="LDL (mmol/L)">
                  <el-input-number v-model="form.ldl" :min="0" :max="15" :precision="2"
                    style="width:100%" />
                </el-form-item>
              </el-col>
            </el-row>

            <div class="section-heading">肝功能</div>
            <el-row :gutter="16">
              <el-col :span="6">
                <el-form-item label="ALT (U/L)">
                  <el-input-number v-model="form.alt" :min="0" :max="2000" style="width:100%" />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="AST (U/L)">
                  <el-input-number v-model="form.ast" :min="0" :max="2000" style="width:100%" />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="总胆红素 (μmol/L)">
                  <el-input-number v-model="form.totalBilirubin" :min="0" :max="500" :precision="1"
                    style="width:100%" />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="白蛋白 (g/L)">
                  <el-input-number v-model="form.albumin" :min="0" :max="100" :precision="1"
                    style="width:100%" />
                </el-form-item>
              </el-col>
            </el-row>

            <div class="section-heading">肾功能</div>
            <el-row :gutter="16">
              <el-col :span="6">
                <el-form-item label="肌酐 (μmol/L)">
                  <el-input-number v-model="form.creatinine" :min="0" :max="2000" :precision="1"
                    style="width:100%" />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="尿素氮 (mmol/L)">
                  <el-input-number v-model="form.bun" :min="0" :max="100" :precision="2"
                    style="width:100%" />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="尿酸 (μmol/L)">
                  <el-input-number v-model="form.uricAcid" :min="0" :max="2000" style="width:100%" />
                </el-form-item>
              </el-col>
            </el-row>

            <div class="section-heading">血常规</div>
            <el-row :gutter="16">
              <el-col :span="6">
                <el-form-item label="血红蛋白 (g/L)">
                  <el-input-number v-model="form.hemoglobin" :min="0" :max="300" style="width:100%" />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="白细胞 (×10⁹/L)">
                  <el-input-number v-model="form.wbc" :min="0" :max="200" :precision="2"
                    style="width:100%" />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="红细胞 (×10¹²/L)">
                  <el-input-number v-model="form.rbc" :min="0" :max="20" :precision="2"
                    style="width:100%" />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="血小板 (×10⁹/L)">
                  <el-input-number v-model="form.platelets" :min="0" :max="2000" style="width:100%" />
                </el-form-item>
              </el-col>
            </el-row>
          </el-form>
        </el-tab-pane>

        <!-- Tab 4：辅助检查 -->
        <el-tab-pane label="辅助检查" name="aux">
          <el-form :model="form" label-width="105px" class="tcm-form">
            <div class="section-heading">影像学检查</div>
            <el-row :gutter="16">
              <el-col :span="12">
                <el-form-item label="胸部X光">
                  <el-input v-model="form.chestXray" type="textarea" :rows="2"
                    placeholder="如：肺纹理增重；未见异常" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="腹部超声">
                  <el-input v-model="form.abdominalUltrasound" type="textarea" :rows="2"
                    placeholder="如：肝胆脾肾未见明显异常" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="16">
              <el-col :span="12">
                <el-form-item label="心电图">
                  <el-input v-model="form.ecg" type="textarea" :rows="2"
                    placeholder="如：窦性心律，正常心电图" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="其他影像">
                  <el-input v-model="form.otherImaging" type="textarea" :rows="2"
                    placeholder="CT、MRI等结果" />
                </el-form-item>
              </el-col>
            </el-row>

            <div class="section-heading">尿常规</div>
            <el-row :gutter="16">
              <el-col :span="6">
                <el-form-item label="尿蛋白">
                  <el-select v-model="form.urineProtein" clearable placeholder="选填">
                    <el-option label="阴性(-)" value="-" />
                    <el-option label="弱阳性(±)" value="±" />
                    <el-option label="阳性(+)" value="+" />
                    <el-option label="强阳性(++)" value="++" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="尿糖">
                  <el-select v-model="form.urineGlucose" clearable placeholder="选填">
                    <el-option label="阴性(-)" value="-" />
                    <el-option label="阳性(+)" value="+" />
                    <el-option label="强阳性(++)" value="++" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="尿潜血">
                  <el-select v-model="form.urineBlood" clearable placeholder="选填">
                    <el-option label="阴性(-)" value="-" />
                    <el-option label="阳性(+)" value="+" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>

            <div class="section-heading">综合评估与建议</div>
            <el-row :gutter="16">
              <el-col :span="8">
                <el-form-item label="健康等级">
                  <el-select v-model="form.healthGrade" clearable placeholder="选填">
                    <el-option label="A 健康" value="A" />
                    <el-option label="B 基本健康" value="B" />
                    <el-option label="C 存在异常" value="C" />
                    <el-option label="D 需要干预" value="D" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="16">
                <el-form-item label="医生建议">
                  <el-input v-model="form.doctorAdvice" type="textarea" :rows="3"
                    placeholder="医生综合建议，包括饮食、运动、复查等" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row>
              <el-col :span="24">
                <el-form-item label="备注">
                  <el-input v-model="form.remarks" type="textarea" :rows="2" placeholder="其他备注信息" />
                </el-form-item>
              </el-col>
            </el-row>
          </el-form>
        </el-tab-pane>

      </el-tabs>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const router = useRouter()
const view    = ref('list')     // 'list' | 'form'
const editId  = ref(null)
const saving  = ref(false)
const loading = ref(false)
const activeTab = ref('basic')
const formRef = ref(null)

// 列表状态
const examList = ref([])
const total    = ref(0)
const page     = ref(1)
const keyword  = ref('')

// ===== 表单数据（完整字段）=====
const blankForm = () => ({
  patientName: '', patientGender: '男', patientBirthday: '',
  patientIdCard: '', phone: '', address: '', occupation: '',
  marital: '', examDate: '', constitutionType: '',
  smoking: '', drinking: '', exercise: '', sleepQuality: '',
  medicalHistory: '', familyHistory: '', allergyHistory: '',
  // 体格
  height: null, weight: null, bmi: '', waistCircumference: null,
  hipCircumference: null, temperature: null, heartRate: null, spo2: null,
  bloodPressureSystolic: null, bloodPressureDiastolic: null,
  visionLeft: '', visionRight: '', hearing: '',
  // 实验室
  fastingBloodGlucose: null, postprandialGlucose: null, hba1c: null,
  totalCholesterol: null, triglycerides: null, hdl: null, ldl: null,
  alt: null, ast: null, totalBilirubin: null, albumin: null,
  creatinine: null, bun: null, uricAcid: null,
  hemoglobin: null, wbc: null, rbc: null, platelets: null,
  // 辅助
  chestXray: '', abdominalUltrasound: '', ecg: '', otherImaging: '',
  urineProtein: '', urineGlucose: '', urineBlood: '',
  healthGrade: '', doctorAdvice: '', remarks: '',
})

const form = reactive(blankForm())

const constitutions = ['平和质','气虚质','阳虚质','阴虚质','痰湿质','湿热质','血瘀质','气郁质','特禀质']

// ===== 自动计算 BMI =====
const calcBMI = () => {
  if (form.height && form.weight) {
    const h = form.height / 100
    form.bmi = (form.weight / (h * h)).toFixed(1)
  } else {
    form.bmi = ''
  }
}

const bmiClass = computed(() => {
  const v = parseFloat(form.bmi)
  if (!v) return ''
  if (v < 18.5) return 'eval-blue'
  if (v < 24)   return 'eval-green'
  if (v < 28)   return 'eval-yellow'
  return 'eval-red'
})

const bmiLabel = computed(() => {
  const v = parseFloat(form.bmi)
  if (!v) return ''
  if (v < 18.5) return '偏瘦'
  if (v < 24)   return '正常'
  if (v < 28)   return '超重'
  return '肥胖'
})

const bpLabel = computed(() => {
  const s = form.bloodPressureSystolic
  const d = form.bloodPressureDiastolic
  if (!s || !d) return ''
  if (s < 120 && d < 80)  return '✓ 正常血压'
  if (s < 130 && d < 80)  return '⚠ 血压正常高值'
  if (s < 140 || d < 90)  return '⚠ 1级高血压'
  return '⛔ 2级及以上高血压'
})

const glucoseLabel = computed(() => {
  const v = form.fastingBloodGlucose
  if (!v) return ''
  if (v < 6.1)  return '✓ 正常'
  if (v < 7.0)  return '⚠ 空腹血糖受损'
  return '⛔ 糖尿病范围'
})

// ===== 列表加载 =====
const loadList = async (p = page.value) => {
  loading.value = true
  page.value = p
  try {
    const res = await axios.get('/api/health-exam/list', {
      params: { page: p, size: 12, keyword: keyword.value }
    })
    if (res.data.code === 200) {
      examList.value = res.data.data.list  || []
      total.value    = res.data.data.total || 0
    }
  } catch {
    examList.value = []
  } finally {
    loading.value = false
  }
}

const openNewExam = () => {
  Object.assign(form, blankForm())
  editId.value = null
  activeTab.value = 'basic'
  view.value = 'form'
}

const openEdit = (row) => {
  Object.assign(form, blankForm(), row)
  editId.value = row.id
  activeTab.value = 'basic'
  view.value = 'form'
}

const goDetect = (row) => {
  localStorage.setItem('current_patient_id', String(row.patientId || row.id))
  localStorage.setItem('current_patient_idCard', row.patientIdCard || '')
  ;['wang', 'wen', 'wenjuan', 'qie'].forEach(k =>
    localStorage.removeItem(`${k}_finished_id`)
  )
  router.push('/detect')
}

// ===== 保存 =====
const saveExam = async () => {
  if (!form.patientName || !form.patientIdCard) {
    activeTab.value = 'basic'
    ElMessage.warning('请填写姓名和身份证号（必填）')
    return
  }
  saving.value = true
  try {
    const url = editId.value ? `/api/health-exam/update/${editId.value}` : '/api/health-exam/save'
    const method = editId.value ? 'put' : 'post'
    const res = await axios[method](url, form)
    if (res.data.code === 200) {
      ElMessage.success(editId.value ? '更新成功' : '档案保存成功')
      view.value = 'list'
      loadList(1)
    } else {
      ElMessage.error(res.data.msg || '保存失败')
    }
  } catch {
    ElMessage.error('保存失败，请检查网络')
  } finally {
    saving.value = false
  }
}

const fmtDate = (t) => {
  if (!t) return '—'
  return new Date(t).toLocaleDateString('zh-CN')
}

onMounted(() => loadList(1))
</script>

<style scoped>
@import '@/styles/tcm-shared.css';

.health-panel { height: 100%; display: flex; flex-direction: column; overflow: hidden; }

.list-view, .form-view { flex: 1; display: flex; flex-direction: column; overflow: hidden; }

.table-wrap { flex: 1; overflow: hidden; }

.badge {
  display: inline-block; font-size: 11px;
  background: #f5e8c8; border: 1px solid #d4b483;
  padding: 1px 6px; border-radius: 10px; margin-right: 4px; color: #5a2d00;
}
.text-muted { color: #bbb; font-size: 12px; }

/* 表单视图 */
.form-header {
  display: flex; align-items: center; gap: 12px;
  padding: 10px 16px;
  background: #faf3e0; border-bottom: 1px solid #e8d5a0;
  flex-shrink: 0;
}
.form-title { flex: 1; text-align: center; font-size: 15px; font-weight: 700; color: #5a2d00; }

.exam-tabs {
  flex: 1; overflow: auto;
}
.exam-tabs :deep(.el-tabs__header) {
  background: #f5ead8; border-bottom: 1px solid #e8d5a0; margin: 0;
}
.exam-tabs :deep(.el-tabs__item) {
  color: #8b6030; font-weight: 600; font-size: 13px;
}
.exam-tabs :deep(.el-tabs__item.is-active) {
  color: #5a2d00; background: #f5e4a8;
}
.exam-tabs :deep(.el-tabs__content) {
  padding: 16px 20px; overflow-y: auto;
}

.section-heading {
  font-size: 13px; font-weight: 700; color: #5a2d00;
  padding: 5px 0 8px;
  border-bottom: 1px solid #e8d5a0;
  margin: 10px 0 10px;
  display: flex; align-items: center; gap: 6px;
}
.section-heading::before { content: '◈'; color: #c8a020; }

/* 评估颜色 */
.eval-blue   { color: #409eff; font-size: 12px; }
.eval-green  { color: #67c23a; font-size: 12px; }
.eval-yellow { color: #e6a23c; font-size: 12px; }
.eval-red    { color: #f56c6c; font-size: 12px; }

.btn-primary {
  background: linear-gradient(135deg,#8b3d1a,#c04a20) !important;
  color: #fdeabb !important; border: none !important;
  font-weight: 700 !important; border-radius: 4px !important;
}
.btn-green {
  background: #3a7050 !important; color: white !important;
  border: none !important; border-radius: 4px !important;
}
</style>