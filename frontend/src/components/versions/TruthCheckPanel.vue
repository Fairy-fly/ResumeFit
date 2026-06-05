<script setup lang="ts">
import type { ResumeVersionRead } from "../../api/resumeVersions";
import type { EvidenceStatus, RiskLevel, RiskType, TruthCheckResultRead } from "../../api/truthChecks";
import CollapsibleSection from "../common/CollapsibleSection.vue";
import LoadingButton from "../common/LoadingButton.vue";

defineProps<{
  selectedResumeVersion: ResumeVersionRead | null;
  truthCheck: TruthCheckResultRead | null;
  truthChecks: TruthCheckResultRead[];
  isLoadingTruthChecks: boolean;
  isCheckingTruth: boolean;
  truthErrorMessage: string;
  canCheckTruth: boolean;
  isOpen: boolean;
}>();

const emit = defineEmits<{
  (event: "check"): void;
  (event: "update:isOpen", value: boolean): void;
}>();

const riskLevelLabels: Record<RiskLevel, string> = {
  low: "低风险",
  medium: "中风险",
  high: "高风险"
};

const riskTypeLabels: Record<RiskType, string> = {
  fabricated_experience: "疑似编造经历",
  exaggerated_skill: "技能掌握程度夸大",
  unsupported_metric: "缺少证据的量化成果",
  unsupported_claim: "缺少证据的能力描述",
  role_exaggeration: "个人角色夸大",
  project_scope_exaggeration: "项目规模夸大",
  uncertain_statement: "不确定内容确定化",
  interview_risk: "面试追问风险"
};

const evidenceStatusLabels: Record<EvidenceStatus, string> = {
  supported: "有证据",
  partially_supported: "部分支持",
  unsupported: "缺少证据",
  uncertain: "不确定"
};

function formatDate(value: string): string {
  return new Intl.DateTimeFormat("zh-CN", {
    dateStyle: "medium",
    timeStyle: "short"
  }).format(new Date(value));
}
</script>

<template>
  <CollapsibleSection
    class="truth-section"
    title="真实性风险检测"
    :count="truthChecks.length"
    :model-value="isOpen"
    @update:model-value="emit('update:isOpen', $event)"
  >
    <p class="muted-text">选择一个已生成版本，检查是否存在夸大、缺证据或不确定表达。</p>
    <p v-if="selectedResumeVersion" class="muted-text">
      当前版本历史检测 {{ truthChecks.length }} 次，默认展示最近一次。
    </p>

    <p v-if="!selectedResumeVersion" class="muted-text">请先在上方选择一个已生成的定制简历版本。</p>
    <p v-if="isLoadingTruthChecks" class="muted-text">正在加载历史检测结果...</p>
    <p v-if="truthErrorMessage" class="error-message">{{ truthErrorMessage }}</p>
    <p v-if="selectedResumeVersion && !isLoadingTruthChecks && !truthCheck" class="muted-text">
      当前版本暂无历史检测结果。
    </p>

    <LoadingButton
      class="primary-button"
      :disabled="!canCheckTruth"
      :loading="isCheckingTruth"
      loading-text="正在检测真实性风险..."
      @click="emit('check')"
    >
      检测真实性风险
    </LoadingButton>

    <article v-if="truthCheck" class="truth-result-panel">
      <div class="truth-result-header">
        <div>
          <h3>检测结果</h3>
          <p class="muted-text">
            历史检测 {{ truthChecks.length }} 次 · 模型：{{ truthCheck.model_name }} ·
            {{ formatDate(truthCheck.created_at) }}
          </p>
        </div>
        <span class="risk-badge" :class="`risk-${truthCheck.overall_risk_level}`">
          {{ riskLevelLabels[truthCheck.overall_risk_level] }}
        </span>
      </div>

      <p class="truth-summary">{{ truthCheck.summary }}</p>

      <section class="risk-list" aria-labelledby="risky-statements-title">
        <h4 id="risky-statements-title">风险表达</h4>
        <p v-if="truthCheck.risky_statements.length === 0" class="muted-text">暂无明显风险表达。</p>
        <article v-for="item in truthCheck.risky_statements" :key="`${item.statement}-${item.risk_type}`" class="risk-item">
          <div class="risk-item-header">
            <strong>{{ item.statement }}</strong>
            <div class="risk-tags">
              <span :class="`risk-${item.risk_level}`">{{ riskLevelLabels[item.risk_level] }}</span>
              <span>{{ riskTypeLabels[item.risk_type] }}</span>
              <span>{{ evidenceStatusLabels[item.evidence_status] }}</span>
            </div>
          </div>
          <p>{{ item.reason }}</p>
          <div class="rewrite-box">
            <strong>更稳妥改法</strong>
            <p>{{ item.safer_rewrite }}</p>
          </div>
        </article>
      </section>

      <div class="truth-grid">
        <section class="truth-card">
          <h4>整体改写建议</h4>
          <ul>
            <li v-for="item in truthCheck.safer_rewrites" :key="item">{{ item }}</li>
            <li v-if="truthCheck.safer_rewrites.length === 0">暂无额外建议。</li>
          </ul>
        </section>

        <section class="truth-card">
          <h4>缺失证据</h4>
          <ul>
            <li v-for="item in truthCheck.missing_evidence" :key="item">{{ item }}</li>
            <li v-if="truthCheck.missing_evidence.length === 0">暂无明显缺失证据。</li>
          </ul>
        </section>

        <section class="truth-card wide">
          <h4>面试追问风险点</h4>
          <ul>
            <li v-for="item in truthCheck.interview_risk_points" :key="item">{{ item }}</li>
            <li v-if="truthCheck.interview_risk_points.length === 0">暂无明显追问风险点。</li>
          </ul>
        </section>
      </div>
    </article>
  </CollapsibleSection>
</template>
