<script setup lang="ts">
import { computed } from "vue";

import type { ChangeExplanation, ResumeVersionRead } from "../../api/resumeVersions";
import CollapsibleSection from "../common/CollapsibleSection.vue";
import LoadingButton from "../common/LoadingButton.vue";

interface DecoratedChangeExplanation {
  item: ChangeExplanation;
  title: string;
}

const props = defineProps<{
  resumeVersion: ResumeVersionRead;
  isExportingMarkdown: boolean;
  isExportingDocx: boolean;
  copyMessage: string;
  exportMessage: string;
  exportErrorMessage: string;
}>();

const emit = defineEmits<{
  (event: "copy"): void;
  (event: "export"): void;
  (event: "export-docx"): void;
}>();

function formatDate(value: string): string {
  return new Intl.DateTimeFormat("zh-CN", {
    dateStyle: "medium",
    timeStyle: "short"
  }).format(new Date(value));
}

const decoratedChangeExplanations = computed<DecoratedChangeExplanation[]>(() => {
  const sectionCounts = props.resumeVersion.change_explanations.reduce((counts, item) => {
    const section = normalizeSection(item.section);
    counts.set(section, (counts.get(section) ?? 0) + 1);
    return counts;
  }, new Map<string, number>());
  const usedTitleCounts = new Map<string, number>();
  const sectionOccurrences = new Map<string, number>();

  return props.resumeVersion.change_explanations.map((item) => {
    const section = normalizeSection(item.section);
    const sectionOccurrence = (sectionOccurrences.get(section) ?? 0) + 1;
    sectionOccurrences.set(section, sectionOccurrence);

    let title = section;
    if ((sectionCounts.get(section) ?? 0) > 1) {
      title = inferExplanationTitle(item, section) ?? `${section} ${sectionOccurrence}`;
    }

    const titleOccurrence = (usedTitleCounts.get(title) ?? 0) + 1;
    usedTitleCounts.set(title, titleOccurrence);

    return {
      item,
      title: titleOccurrence > 1 ? `${title} ${titleOccurrence}` : title
    };
  });
});

function normalizeSection(section: string): string {
  const normalized = section.trim();
  return normalized.length > 0 ? normalized : "修改说明";
}

function inferExplanationTitle(item: ChangeExplanation, section: string): string | null {
  const text = `${item.section} ${item.reason} ${item.source}`.toLowerCase();

  if (containsAny(text, ["学历", "教育", "学校", "专业"])) {
    return "教育经历说明";
  }

  if (containsAny(text, ["技能", "技术栈", "关键词", "匹配", "jd", "岗位要求"])) {
    return section.includes("技能") ? "技能匹配保留" : `${section}匹配优化`;
  }

  if (containsAny(text, ["真实", "证据", "作品", "链接", "不确定", "保守", "风险", "uncertain"])) {
    return section.includes("项目") ? "项目真实性说明" : `${section}真实性说明`;
  }

  if (containsAny(text, ["项目", "经历", "贡献", "职责", "角色"])) {
    return "项目经历优化";
  }

  if (containsAny(text, ["表达", "润色", "压缩", "突出", "重组", "精简", "改写"])) {
    return `${section}表达优化`;
  }

  return null;
}

function containsAny(value: string, keywords: string[]): boolean {
  return keywords.some((keyword) => value.includes(keyword));
}
</script>

<template>
  <section class="result-section" aria-labelledby="resume-version-title">
    <div class="section-header">
      <div>
        <h2 id="resume-version-title">{{ resumeVersion.title }}</h2>
        <p class="muted-text">
          模型：{{ resumeVersion.model_name }} · {{ resumeVersion.version_type }} ·
          {{ formatDate(resumeVersion.created_at) }}
        </p>
      </div>
      <div class="action-row">
        <button class="secondary-button" type="button" @click="emit('copy')">复制 Markdown</button>
        <LoadingButton
          class="secondary-button"
          :loading="isExportingMarkdown"
          loading-text="正在导出 Markdown..."
          @click="emit('export')"
        >
          导出 Markdown
        </LoadingButton>
        <LoadingButton
          class="secondary-button"
          :loading="isExportingDocx"
          loading-text="正在导出 DOCX..."
          @click="emit('export-docx')"
        >
          导出 DOCX
        </LoadingButton>
      </div>
    </div>

    <p v-if="copyMessage" class="copy-message">{{ copyMessage }}</p>
    <p v-if="exportMessage" class="copy-message">{{ exportMessage }}</p>
    <p v-if="exportErrorMessage" class="error-message">{{ exportErrorMessage }}</p>

    <CollapsibleSection class="markdown-panel" title="Markdown 简历" :default-open="true">
      <pre>{{ resumeVersion.content_markdown }}</pre>
    </CollapsibleSection>

    <CollapsibleSection
      class="explanation-panel"
      title="修改原因"
      :count="resumeVersion.change_explanations.length"
      :default-open="true"
    >
      <div v-if="decoratedChangeExplanations.length > 0" class="explanation-grid">
        <article
          v-for="explanation in decoratedChangeExplanations"
          :key="`${explanation.title}-${explanation.item.section}-${explanation.item.reason}`"
          class="explanation-card"
        >
          <div class="explanation-card-header">
            <strong>{{ explanation.title }}</strong>
            <span v-if="explanation.item.uncertain" class="explanation-tag">uncertain</span>
          </div>
          <p>{{ explanation.item.reason }}</p>
          <small>来源：{{ explanation.item.source }}</small>
        </article>
      </div>
      <p v-else class="muted-text">暂无修改说明。</p>
    </CollapsibleSection>
  </section>
</template>
