<script setup lang="ts">
import type { InterviewQuestionResultRead, QuestionDifficulty } from "../../api/interviewQuestions";
import type { ResumeVersionRead } from "../../api/resumeVersions";
import LoadingButton from "../common/LoadingButton.vue";

defineProps<{
  selectedResumeVersion: ResumeVersionRead | null;
  interviewQuestionResult: InterviewQuestionResultRead | null;
  interviewQuestionResults: InterviewQuestionResultRead[];
  isLoadingInterviewQuestions: boolean;
  isGeneratingInterviewQuestions: boolean;
  interviewErrorMessage: string;
  canGenerateInterviewQuestions: boolean;
}>();

const emit = defineEmits<{
  (event: "generate"): void;
}>();

const difficultyLabels: Record<QuestionDifficulty, string> = {
  easy: "基础",
  medium: "中等",
  hard: "较难"
};

function formatDate(value: string): string {
  return new Intl.DateTimeFormat("zh-CN", {
    dateStyle: "medium",
    timeStyle: "short"
  }).format(new Date(value));
}
</script>

<template>
  <section class="interview-section" aria-labelledby="interview-question-title">
    <div class="section-header">
      <div>
        <h2 id="interview-question-title">面试追问预测</h2>
        <p class="muted-text">基于当前选择的简历版本、JD、项目和真实性风险，生成保守可解释的追问准备。</p>
        <p v-if="selectedResumeVersion" class="muted-text">
          当前版本历史预测 {{ interviewQuestionResults.length }} 次，默认展示最近一次。
        </p>
      </div>
    </div>

    <p v-if="!selectedResumeVersion" class="muted-text">请先在上方选择一个已生成的定制简历版本。</p>
    <p v-if="isLoadingInterviewQuestions" class="muted-text">正在加载历史追问预测...</p>
    <p v-if="interviewErrorMessage" class="error-message">{{ interviewErrorMessage }}</p>
    <p v-if="selectedResumeVersion && !isLoadingInterviewQuestions && !interviewQuestionResult" class="muted-text">
      当前版本暂无历史追问预测结果。
    </p>

    <LoadingButton
      class="primary-button"
      :disabled="!canGenerateInterviewQuestions"
      :loading="isGeneratingInterviewQuestions"
      loading-text="正在生成面试追问..."
      @click="emit('generate')"
    >
      生成面试追问
    </LoadingButton>

    <article v-if="interviewQuestionResult" class="interview-result-panel">
      <div class="section-header">
        <div>
          <h3>追问预测结果</h3>
          <p class="muted-text">
            历史预测 {{ interviewQuestionResults.length }} 次 · 模型：{{ interviewQuestionResult.model_name }} ·
            {{ formatDate(interviewQuestionResult.created_at) }}
          </p>
        </div>
      </div>

      <p class="truth-summary">{{ interviewQuestionResult.summary }}</p>

      <section class="question-list" aria-labelledby="interview-questions-list-title">
        <h4 id="interview-questions-list-title">可能追问</h4>
        <p v-if="interviewQuestionResult.questions.length === 0" class="muted-text">暂无追问预测。</p>
        <article
          v-for="item in interviewQuestionResult.questions"
          :key="`${item.question}-${item.related_resume_section}`"
          class="question-item"
        >
          <div class="question-item-header">
            <strong>{{ item.question }}</strong>
            <span class="difficulty-badge">{{ difficultyLabels[item.difficulty] }}</span>
          </div>

          <div class="question-grid">
            <section class="question-card">
              <h5>为什么会问</h5>
              <p>{{ item.reason }}</p>
            </section>
            <section class="question-card">
              <h5>关联简历内容</h5>
              <p>{{ item.related_resume_section }}</p>
            </section>
            <section class="question-card wide">
              <h5>建议回答</h5>
              <p>{{ item.suggested_answer }}</p>
            </section>
            <section class="question-card">
              <h5>回答策略</h5>
              <p>{{ item.answer_strategy }}</p>
            </section>
            <section class="question-card">
              <h5>风险提醒</h5>
              <p>{{ item.risk_reminder }}</p>
            </section>
          </div>
        </article>
      </section>
    </article>
  </section>
</template>
