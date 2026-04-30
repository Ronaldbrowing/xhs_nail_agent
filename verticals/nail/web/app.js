(function () {
  const APP_CONFIG = {
    currentVertical: "nail",
    exampleBrief: "夏日蓝色猫眼短甲，适合黄皮，显白清透，想要小红书种草风",
    verticals: {
      nail: {
        label: "小红书美甲图文",
        styleOptions: [
          {
            value: "",
            label: "自动选择模板",
            description: "适合第一次使用，系统会根据你的内容需求自动整理结构。",
          },
          {
            value: "single_seed_summer_cat_eye_short",
            label: "夏日猫眼种草风",
            description: "更偏向种草分享，适合做夏日显白款式推荐。",
          },
          {
            value: "default",
            label: "通用结构预览",
            description: "先看标题、正文和页面结构，适合快速确认方向。",
          },
        ],
        skinToneOptions: [
          { value: "", label: "自动判断" },
          { value: "黄皮", label: "黄皮" },
          { value: "白皮", label: "白皮" },
          { value: "中性肤色", label: "中性肤色" },
        ],
        nailLengthOptions: [
          { value: "", label: "自动判断" },
          { value: "短甲", label: "短甲" },
          { value: "中长甲", label: "中长甲" },
          { value: "长甲", label: "长甲" },
        ],
        roleLabels: {
          cover: "封面",
          detail_closeup: "细节特写",
          skin_tone_fit: "显白效果",
          style_breakdown: "款式拆解",
          scene_mood: "场景氛围",
          save_summary: "收藏总结",
        },
      },
    },
    jobStatusMap: {
      idle: {
        badge: "待开始",
        title: "待开始",
        detail: "在左侧输入内容需求，点击「生成内容预览」即可开始。",
      },
      queued: {
        badge: "已提交",
        title: "已提交，等待开始",
        detail: "任务已经提交成功，Studio 正在为这次内容生成做准备。",
      },
      running: {
        badge: "生成中",
        title: "正在生成内容",
        detail: "Studio 正在整理标题、正文、标签和多页内容结构，请稍等。",
      },
      succeeded: {
        badge: "已完成",
        title: "生成完成",
        detail: "内容已经准备好，可以开始查看标题、正文和页面结构。",
      },
      restored: {
        badge: "已恢复",
        title: "已从结果包恢复",
        detail: "上次任务记录已过期，但已根据结果包恢复内容。",
      },
      failed: {
        badge: "生成失败",
        title: "生成失败",
        detail: "这次生成没有完成，你可以稍后重试，或展开开发信息查看技术错误。",
      },
      partial_failed: {
        badge: "部分完成",
        title: "部分内容已生成",
        detail: "这次任务只完成了部分内容，可以先看已有结果，再决定是否重新生成。",
      },
      timeout: {
        badge: "耗时较长",
        title: "生成时间较长，可稍后查看",
        detail: "生成时间较长，任务可能仍在后台继续运行。你可以稍后点击「继续查询」查看结果。",
      },
    },
    pageStatusMap: {
      planned: "页面结构已规划",
      prompt_ready: "页面结构已准备",
      generated: "图片已生成",
      failed: "页面生成失败",
    },
  };

  let selectedVertical = APP_CONFIG.currentVertical;
  let availableVerticals = [];
  let serverHistoryItems = [];
  let caseLibraryItems = [];
  let recentLocalJobs = [];
  let activeJobFromLocalStorage = null;
  let historyLoading = false;
  let historyError = null;
  let caseLibraryLoading = false;
  let caseLibraryError = null;
  let selectedCase = null;
  let currentVertical = APP_CONFIG.verticals[selectedVertical];
  const form = document.getElementById("note-form");
  const briefField = document.getElementById("brief");
  const verticalField = document.getElementById("vertical");
  const styleField = document.getElementById("style_id");
  const styleHelper = document.getElementById("style-helper");
  const skinToneField = document.getElementById("skin_tone");
  const nailLengthField = document.getElementById("nail_length");
  const enableImagesField = document.getElementById("enable_images");
  const maxWorkersField = document.getElementById("max_workers");
  const exampleButton = document.getElementById("example-button");
  const submitButton = document.getElementById("submit-button");
  const progressPanel = document.getElementById("progress-panel");
  const statusText = document.getElementById("status-text");
  const progressDetail = document.getElementById("progress-detail");
  const statusBadge = document.getElementById("status-badge");
  const resultMeta = document.getElementById("result-meta");
  const resultSection = document.getElementById("result-section");
  const resultEmpty = document.getElementById("result-empty");
  const noteSummary = document.getElementById("note-summary");
  const pagesGrid = document.getElementById("pages-grid");
  const currentVerticalBadge = document.getElementById("current-vertical-badge");
  const jobMeta = document.getElementById("job-meta");
  const resumePanel = document.getElementById("resume-panel");
  const resumeText = document.getElementById("resume-text");
  const continueButton = document.getElementById("continue-button");
  const clearJobButton = document.getElementById("clear-job-button");
  const refreshHistoryButton = document.getElementById("refresh-history-button");
  const historyPanel = document.getElementById("history-panel");
  const historyMeta = document.getElementById("history-meta");
  const historyEmpty = document.getElementById("history-empty");
  const historyList = document.getElementById("history-list");
  const recentJobsTitle = document.getElementById("recent-jobs-title");
  const caseLibraryPanel = document.getElementById("case-library-panel");
  const caseLibraryMeta = document.getElementById("case-library-meta");
  const caseLibraryEmpty = document.getElementById("case-library-empty");
  const caseLibraryList = document.getElementById("case-library-list");
  const selectedCasePanel = document.getElementById("selected-case-panel");
  const selectedCaseText = document.getElementById("selected-case-text");
  const clearCaseButton = document.getElementById("clear-case-button");
  const caseIdField = document.getElementById("case_id");

  const STORAGE_KEY = "nail_studio_last_job";
  let currentJobContext = null;
  let continueQueryPromise = null;
  let currentStatusKey = "idle";

  function ensureResumeElements() {
    if (!resumePanel || !resumeText || !continueButton || !clearJobButton) {
      console.error("resume-panel element is missing", {
        hasResumePanel: Boolean(resumePanel),
        hasResumeText: Boolean(resumeText),
        hasContinueButton: Boolean(continueButton),
        hasClearJobButton: Boolean(clearJobButton),
      });
      return false;
    }
    return true;
  }

  function populateSelect(selectElement, options) {
    selectElement.innerHTML = "";
    options.forEach(function (option) {
      const element = document.createElement("option");
      element.value = option.value;
      element.textContent = option.label;
      selectElement.appendChild(element);
    });
  }

  function getVerticalDefinition(vertical) {
    return availableVerticals.find(function (item) {
      return item && item.vertical === vertical;
    }) || null;
  }

  function buildGenericVerticalConfig(verticalDefinition) {
    const label = verticalDefinition && verticalDefinition.display_name
      ? verticalDefinition.display_name
      : (verticalDefinition && verticalDefinition.vertical) || selectedVertical;
    return {
      label: label,
      styleOptions: [
        {
          value: "",
          label: "自动选择模板",
          description: "当前内容场景暂未提供专用模板，Studio 会先按通用结构整理内容。",
        },
      ],
      skinToneOptions: [
        { value: "", label: "自动判断" },
      ],
      nailLengthOptions: [
        { value: "", label: "自动判断" },
      ],
      roleLabels: {},
    };
  }

  function getCurrentVerticalConfig() {
    return APP_CONFIG.verticals[selectedVertical] || buildGenericVerticalConfig(getVerticalDefinition(selectedVertical));
  }

  function updateCurrentVerticalState(vertical) {
    selectedVertical = vertical;
    currentVertical = getCurrentVerticalConfig();
    if (currentVerticalBadge) {
      currentVerticalBadge.textContent = "当前内容场景 · " + currentVertical.label;
    }
  }

  function updateStyleHelper() {
    const selected = currentVertical.styleOptions.find(function (item) {
      return item.value === styleField.value;
    }) || currentVertical.styleOptions[0];
    styleHelper.textContent = selected.description;
  }

  function initializeFormOptions() {
    currentVertical = getCurrentVerticalConfig();
    populateSelect(styleField, currentVertical.styleOptions);
    populateSelect(skinToneField, currentVertical.skinToneOptions);
    populateSelect(nailLengthField, currentVertical.nailLengthOptions);
    updateStyleHelper();
  }

  function formatError(err) {
    if (err === null || err === undefined) {
      return "未知错误";
    }
    if (typeof err === "string") {
      return err;
    }
    if (err instanceof Error) {
      if (err.message && typeof err.message === "string") {
        return err.message;
      }
      try { return String(err.message); } catch (_) { return err.toString(); }
    }
    if (typeof err === "object") {
      if (err.message && typeof err.message === "string") {
        return err.message;
      }
      if (err.detail) {
        return typeof err.detail === "string" ? err.detail : String(err.detail);
      }
      try {
        return JSON.stringify(err);
      } catch (_) {
        return String(err);
      }
    }
    try { return String(err); } catch (_) { return "未知错误"; }
  }

  function setJobMeta(payload) {
    if (typeof payload === "string") {
      jobMeta.textContent = payload;
    } else if (payload) {
      try {
        const safePayload = JSON.parse(JSON.stringify(payload, function (k, v) {
          if (v instanceof Error) {
            try { return { message: String(v.message), name: v.name }; } catch (_) { return String(v); }
          }
          if (typeof v === "object" && v !== null) {
            try { return v; } catch (_) { return String(v); }
          }
          return v;
        }));
        jobMeta.textContent = JSON.stringify(safePayload, null, 2);
      } catch (_) {
        jobMeta.textContent = typeof payload.message === "string" ? payload.message : String(payload);
      }
    }
  }

  function getPollConfig(generateImages) {
    if (generateImages) {
      return {
        pollIntervalMs: 5000,
        maxPollMs: 15 * 60 * 1000,
      };
    }
    return {
      pollIntervalMs: 1000,
      maxPollMs: 60000,
    };
  }

  function saveLastJob(context) {
    currentJobContext = context;
    activeJobFromLocalStorage = context;
    try {
      window.localStorage.setItem(STORAGE_KEY, JSON.stringify(context));
    } catch (error) {
      // Ignore storage failures and keep the in-memory context.
    }
  }

  function clearLastJob() {
    currentJobContext = null;
    activeJobFromLocalStorage = null;
    try {
      window.localStorage.removeItem(STORAGE_KEY);
    } catch (error) {
      // Ignore storage failures.
    }
  }

  function loadLastJob() {
    if (currentJobContext) {
      return currentJobContext;
    }
    try {
      const stored = window.localStorage.getItem(STORAGE_KEY);
      if (!stored) {
        return null;
      }
      currentJobContext = JSON.parse(stored);
      activeJobFromLocalStorage = currentJobContext;
      return currentJobContext;
    } catch (error) {
      return null;
    }
  }

  function getRecentJobs() {
    try {
      const jobs = JSON.parse(localStorage.getItem(RECENT_JOBS_KEY) || "[]");
      recentLocalJobs = Array.isArray(jobs) ? jobs : [];
      return recentLocalJobs;
    } catch (_) {
      recentLocalJobs = [];
      return [];
    }
  }

  function setRecentJobs(jobs) {
    recentLocalJobs = jobs;
    try {
      localStorage.setItem(RECENT_JOBS_KEY, JSON.stringify(jobs));
    } catch (_) {
      // Ignore storage failures.
    }
  }

  function upsertRecentJob(entry) {
    if (!entry || !entry.jobId) {
      return;
    }
    const jobs = getRecentJobs().filter(function (job) {
      return job.jobId !== entry.jobId;
    });
    const previous = getRecentJobs().find(function (job) {
      return job.jobId === entry.jobId;
    }) || {};
    jobs.unshift(Object.assign({}, previous, entry));
    if (jobs.length > 10) {
      jobs.length = 10;
    }
    setRecentJobs(jobs);
  }

  function removeRecentJob(jobId) {
    const jobs = getRecentJobs().filter(function (job) {
      return job.jobId !== jobId;
    });
    setRecentJobs(jobs);
  }

  function jobStatusLabel(status) {
    return (APP_CONFIG.jobStatusMap[status] || APP_CONFIG.jobStatusMap.idle).badge;
  }

  function generationModeLabel(generateImages) {
    return generateImages ? "真实图片" : "快速预览";
  }

  function showResumePanel(message) {
    if (!ensureResumeElements()) {
      return;
    }
    resumeText.textContent = message;
    resumePanel.hidden = false;
    resumePanel.style.display = "";
    resumePanel.removeAttribute("hidden");
    progressPanel.hidden = false;
  }

  function hideResumePanel() {
    if (!resumePanel) {
      console.error("resume-panel element is missing", {
        hasResumePanel: Boolean(resumePanel),
      });
      return;
    }
    resumePanel.hidden = true;
    resumePanel.style.display = "none";
    resumePanel.setAttribute("hidden", "");
    if (currentStatusKey === "idle") {
      progressPanel.hidden = true;
    }
  }

  function applyStatus(stateKey, detailText) {
    const state = APP_CONFIG.jobStatusMap[stateKey] || APP_CONFIG.jobStatusMap.idle;
    currentStatusKey = stateKey;
    statusText.textContent = state.title;
    progressDetail.textContent = detailText || state.detail;
    statusBadge.textContent = state.badge;
    statusBadge.className = "status-badge status-" + stateKey;
    progressPanel.hidden = stateKey === "idle" && resumePanel.hidden;
    progressPanel.classList.toggle("is-busy", stateKey === "queued" || stateKey === "running");
  }

  function clearResults() {
    noteSummary.innerHTML = "";
    pagesGrid.innerHTML = "";
    showResultEmptyState();
    resultMeta.textContent = "生成完成后，这里会展示标题、正文、标签和多页内容结构。";
  }

  function showResults() {
    hideResultEmptyState();
  }

  function showResultEmptyState() {
    if (resultEmpty) {
      resultEmpty.hidden = false;
    }
  }

  function hideResultEmptyState() {
    if (resultEmpty) {
      resultEmpty.hidden = true;
    }
  }

  function sanitizePayload(rawPayload) {
    const payload = {};
    Object.keys(rawPayload).forEach(function (key) {
      const value = rawPayload[key];
      if (value === undefined || value === null) {
        return;
      }
      if (typeof value === "string" && value.trim() === "") {
        return;
      }
      payload[key] = value;
    });
    return payload;
  }

  async function loadVerticalOptions() {
    const response = await fetchJson("/api/verticals");
    const verticals = Array.isArray(response.verticals) ? response.verticals.filter(function (item) {
      return item && item.enabled;
    }) : [];
    availableVerticals = verticals;

    if (verticalField) {
      verticalField.innerHTML = "";
      verticals.forEach(function (item) {
        const option = document.createElement("option");
        option.value = item.vertical;
        option.textContent = item.display_name || item.vertical;
        verticalField.appendChild(option);
      });
    }

    const hasDefaultVertical = verticals.some(function (item) {
      return item.vertical === APP_CONFIG.currentVertical;
    });
    const fallbackVertical = verticals.length > 0 ? verticals[0].vertical : APP_CONFIG.currentVertical;
    updateCurrentVerticalState(hasDefaultVertical ? APP_CONFIG.currentVertical : fallbackVertical);
    if (verticalField) {
      verticalField.value = selectedVertical;
    }
    initializeFormOptions();
  }

  function buildVerticalCasesUrl() {
    return "/api/verticals/" + encodeURIComponent(selectedVertical) + "/cases";
  }

  function buildCasePreviewUrl(item) {
    if (
      item &&
      typeof item.preview_url === "string" &&
      (item.preview_url.startsWith("/static/") || item.preview_url.startsWith("/api/verticals/"))
    ) {
      return item.preview_url;
    }
    if (!item || typeof item.image_path !== "string") {
      return null;
    }
    if (!item.image_path.startsWith("case_library/")) {
      return null;
    }
    if (item.image_path.indexOf("..") !== -1 || item.image_path.startsWith("/") || item.image_path.indexOf(":") !== -1) {
      return null;
    }
    return null;
  }

  function syncCaseInputWithSelection(item) {
    if (!caseIdField) {
      return;
    }
    caseIdField.value = item && item.case_id ? item.case_id : "";
  }

  function renderSelectedCasePanel() {
    if (!selectedCasePanel || !selectedCaseText) {
      return;
    }
    if (!selectedCase) {
      selectedCasePanel.hidden = true;
      return;
    }
    const label = selectedCase.title || selectedCase.case_id || "已选案例";
    const secondary = selectedCase.case_id && selectedCase.case_id !== label ? " · " + selectedCase.case_id : "";
    selectedCaseText.textContent = "已选择案例：" + label + secondary;
    selectedCasePanel.hidden = false;
  }

  function clearCaseSelection(options) {
    const settings = options || {};
    selectedCase = null;
    if (!settings.preserveInput) {
      syncCaseInputWithSelection(null);
    }
    renderSelectedCasePanel();
    renderCaseLibrary();
  }

  function selectCase(item) {
    selectedCase = item || null;
    syncCaseInputWithSelection(item);
    renderSelectedCasePanel();
    if (currentReferenceImage) {
      clearReferenceImage({ preserveCaseSelection: true });
    }
    renderCaseLibrary();
  }

  function buildCaseLibraryItem(item) {
    const article = document.createElement("article");
    article.className = "recent-job-item";
    article.dataset.caseId = item.case_id || "";

    const meta = document.createElement("div");
    meta.className = "recent-job-meta";

    const caseIdLabel = document.createElement("span");
    caseIdLabel.className = "recent-job-id";
    caseIdLabel.textContent = item.case_id || "case";
    meta.appendChild(caseIdLabel);

    const taskLabel = document.createElement("span");
    taskLabel.className = "recent-job-status";
    taskLabel.textContent = item.task || selectedVertical;
    meta.appendChild(taskLabel);

    const imageLabel = document.createElement("span");
    imageLabel.className = "recent-job-mode";
    imageLabel.textContent = item.has_image ? "含参考图" : "无图片";
    meta.appendChild(imageLabel);

    const summary = document.createElement("div");
    summary.className = "recent-job-summary";

    const title = document.createElement("span");
    title.className = "recent-job-brief";
    title.textContent = item.title || item.case_id || "未命名案例";
    summary.appendChild(title);

    const brief = document.createElement("span");
    brief.className = "recent-job-time";
    brief.textContent = item.brief || "可复用当前案例的风格方向。";
    summary.appendChild(brief);

    const actions = document.createElement("div");
    actions.className = "recent-job-actions";

    const chooseButton = document.createElement("button");
    chooseButton.type = "button";
    chooseButton.className = "secondary-button recent-job-open";
    chooseButton.textContent = selectedCase && selectedCase.case_id === item.case_id ? "已选中" : "使用案例";
    chooseButton.disabled = selectedCase && selectedCase.case_id === item.case_id;
    chooseButton.addEventListener("click", function () {
      selectCase(item);
    });
    actions.appendChild(chooseButton);

    const imageUrl = buildCasePreviewUrl(item);
    if (imageUrl) {
      const image = document.createElement("img");
      image.className = "page-image";
      image.src = imageUrl;
      image.alt = item.title || item.case_id || "案例预览";
      article.appendChild(image);
    }

    article.appendChild(meta);
    article.appendChild(summary);
    article.appendChild(actions);
    return article;
  }

  function renderCaseLibrary() {
    if (!caseLibraryPanel || !caseLibraryEmpty || !caseLibraryList || !caseLibraryMeta) {
      return;
    }

    caseLibraryPanel.hidden = false;
    caseLibraryList.innerHTML = "";

    if (caseLibraryLoading) {
      caseLibraryEmpty.hidden = true;
      caseLibraryList.hidden = true;
      caseLibraryMeta.textContent = "正在加载当前内容场景的案例库...";
      return;
    }

    if (caseLibraryError) {
      caseLibraryEmpty.hidden = false;
      caseLibraryList.hidden = true;
      caseLibraryMeta.textContent = "案例库暂时加载失败。";
      caseLibraryEmpty.querySelector("strong").textContent = "案例库加载失败";
      caseLibraryEmpty.querySelector("p").textContent = "你仍然可以直接填写 case_id，或改用本地参考图继续生成。";
      return;
    }

    caseLibraryEmpty.querySelector("strong").textContent = "还没有可用案例";
    caseLibraryEmpty.querySelector("p").textContent = "当当前内容场景存在可复用案例时，这里会显示可直接选择的案例卡片。";
    if (!caseLibraryItems.length) {
      caseLibraryEmpty.hidden = false;
      caseLibraryList.hidden = true;
      caseLibraryMeta.textContent = "当前内容场景暂时没有可选案例。";
      return;
    }

    caseLibraryEmpty.hidden = true;
    caseLibraryList.hidden = false;
    caseLibraryMeta.textContent = "选择案例后，Studio 会以案例风格方向继续生成。";
    caseLibraryItems.forEach(function (item) {
      caseLibraryList.appendChild(buildCaseLibraryItem(item));
    });
  }

  async function loadCaseLibrary() {
    if (!selectedVertical) {
      caseLibraryItems = [];
      caseLibraryLoading = false;
      caseLibraryError = null;
      renderCaseLibrary();
      return;
    }
    caseLibraryLoading = true;
    caseLibraryError = null;
    renderCaseLibrary();
    try {
      const response = await fetchJson(buildVerticalCasesUrl());
      caseLibraryItems = Array.isArray(response.items) ? response.items : [];
      caseLibraryLoading = false;
      caseLibraryError = null;
      renderCaseLibrary();
    } catch (error) {
      caseLibraryItems = [];
      caseLibraryLoading = false;
      caseLibraryError = error;
      renderCaseLibrary();
      setJobMeta({
        note: "case library load failed",
        vertical: selectedVertical,
        status: error.status || null,
        url: error.url || null,
        error: formatError(error),
      });
    }
  }

  function buildHistoryItem(item) {
    const article = document.createElement("article");
    article.className = "recent-job-item";
    article.dataset.noteId = item.note_id;

    const meta = document.createElement("div");
    meta.className = "recent-job-meta";

    const noteIdLabel = document.createElement("span");
    noteIdLabel.className = "recent-job-id";
    noteIdLabel.textContent = (item.note_id || "unknown").slice(0, 18) + "...";
    meta.appendChild(noteIdLabel);

    const statusLabel = document.createElement("span");
    statusLabel.className = "recent-job-status";
    statusLabel.textContent = jobStatusLabel(item.status || "idle");
    meta.appendChild(statusLabel);

    const modeLabel = document.createElement("span");
    modeLabel.className = "recent-job-mode";
    modeLabel.textContent = item.has_package ? "可回放" : "无结果包";
    meta.appendChild(modeLabel);

    const summary = document.createElement("div");
    summary.className = "recent-job-summary";

    const title = document.createElement("span");
    title.className = "recent-job-brief";
    title.textContent = item.selected_title || item.brief || item.note_id || "未命名内容";
    summary.appendChild(title);

    const time = document.createElement("span");
    time.className = "recent-job-time";
    time.textContent = item.created_at
      ? new Date(item.created_at).toLocaleString("zh-CN", { month: "numeric", day: "numeric", hour: "2-digit", minute: "2-digit" })
      : "时间未知";
    summary.appendChild(time);

    const actions = document.createElement("div");
    actions.className = "recent-job-actions";

    const openButton = document.createElement("button");
    openButton.type = "button";
    openButton.className = "secondary-button recent-job-open";
    openButton.textContent = "回放预览";
    openButton.disabled = !item.note_id;
    openButton.addEventListener("click", function () {
      replayHistoryItem(item);
    });

    actions.appendChild(openButton);
    article.appendChild(meta);
    article.appendChild(summary);
    article.appendChild(actions);
    return article;
  }

  function renderServerHistory() {
    if (!historyPanel || !historyList || !historyEmpty || !historyMeta) {
      return;
    }

    historyPanel.hidden = false;
    historyList.innerHTML = "";
    if (historyLoading) {
      historyEmpty.hidden = true;
      historyList.hidden = true;
      historyMeta.textContent = "正在从服务端加载历史内容...";
      return;
    }

    if (historyError) {
      historyEmpty.hidden = false;
      historyList.hidden = true;
      historyMeta.textContent = "历史内容暂时加载失败，请稍后点击刷新历史重试。";
      historyEmpty.querySelector("strong").textContent = "历史内容加载失败";
      historyEmpty.querySelector("p").textContent = "服务端历史暂时不可用，请稍后点击“刷新历史”重试。";
      return;
    }

    historyEmpty.querySelector("strong").textContent = "还没有历史内容";
    historyEmpty.querySelector("p").textContent = "当服务端存在历史 package 时，这里会显示可回放的记录。";
    if (!serverHistoryItems.length) {
      historyEmpty.hidden = false;
      historyList.hidden = true;
      historyMeta.textContent = "这里显示服务端历史内容，点击后会回放到下方内容预览区。";
      return;
    }

    historyEmpty.hidden = true;
    historyList.hidden = false;
    historyMeta.textContent = "历史内容来自服务端接口，可直接回放到右侧内容预览区。";
    serverHistoryItems.forEach(function (item) {
      historyList.appendChild(buildHistoryItem(item));
    });
  }

  async function loadServerHistory() {
    if (!selectedVertical) {
      serverHistoryItems = [];
      historyLoading = false;
      historyError = null;
      renderServerHistory();
      return;
    }
    historyLoading = true;
    historyError = null;
    renderServerHistory();
    try {
      const response = await fetchJson(buildVerticalNotesUrl());
      serverHistoryItems = Array.isArray(response.items) ? response.items : [];
      historyLoading = false;
      historyError = null;
      renderServerHistory();
    } catch (error) {
      serverHistoryItems = [];
      historyLoading = false;
      historyError = error;
      renderServerHistory();
      setJobMeta({
        note: "history load failed",
        vertical: selectedVertical,
        status: error.status || null,
        url: error.url || null,
        error: formatError(error),
      });
    }
  }

  async function replayHistoryItem(item) {
    if (!item || !item.note_id || !selectedVertical) {
      return;
    }
    applyStatus("running", "正在加载历史结果包");
    try {
      const packageData = await fetchJson(buildVerticalPackageUrl(item.note_id));
      const generateImages = Array.isArray(packageData.pages) && packageData.pages.some(function (page) {
        return Boolean(normalizeOutputImagePath(page.image_path));
      });
      renderPackage(packageData, generateImages, {
        job_id: item.job_id || null,
        note_id: item.note_id,
        status: "history_replay",
        error: null,
      });
      hideResultEmptyState();
      applyStatus("restored", "已从历史记录回放内容。");
      resultMeta.textContent = "当前正在查看服务端历史内容回放。";
      setJobMeta({
        note: "history replay",
        vertical: selectedVertical,
        note_id: item.note_id,
        generate_images: generateImages,
      });
    } catch (error) {
      applyStatus("failed", "历史内容加载失败");
      resultMeta.textContent = "这条历史内容暂时无法回放，请稍后刷新历史后重试。";
      setJobMeta({
        note: "history replay failed",
        vertical: selectedVertical,
        note_id: item.note_id,
        status: error.status || null,
        url: error.url || null,
        error: formatError(error),
      });
    }
  }

  function normalizeOutputImagePath(imagePath) {
    if (typeof imagePath !== "string" || imagePath.length === 0) {
      return null;
    }
    if (!imagePath.startsWith("output/")) {
      return null;
    }
    if (imagePath.indexOf("..") !== -1 || imagePath.startsWith("/") || imagePath.indexOf(":") !== -1) {
      return null;
    }
    return "/static/" + imagePath;
  }

  function labelForRole(role) {
    return currentVertical.roleLabels[role] || role || "未命名页面";
  }

  function labelForPageStatus(status) {
    return APP_CONFIG.pageStatusMap[status] || status || "状态未知";
  }

  function buildSummaryCard(label, contentNode) {
    const wrapper = document.createElement("dl");
    wrapper.className = "summary-card";
    const term = document.createElement("dt");
    term.textContent = label;
    const detail = document.createElement("dd");

    if (typeof contentNode === "string") {
      detail.textContent = contentNode || "—";
    } else if (contentNode) {
      detail.appendChild(contentNode);
    } else {
      detail.textContent = "—";
    }

    wrapper.appendChild(term);
    wrapper.appendChild(detail);
    return wrapper;
  }

  function buildTagList(tags) {
    const list = document.createElement("div");
    list.className = "tag-list";
    (tags || []).forEach(function (tag) {
      const chip = document.createElement("span");
      chip.className = "tag-chip";
      chip.textContent = tag;
      list.appendChild(chip);
    });
    if (!list.childNodes.length) {
      list.textContent = "—";
    }
    return list;
  }

  function buildPlaceholder(pageStatusLabel) {
    const placeholder = document.createElement("div");
    placeholder.className = "page-placeholder";

    const badge = document.createElement("span");
    badge.className = "placeholder-badge";
    badge.textContent = "图片待生成";

    const copy = document.createElement("div");
    copy.className = "placeholder-copy";
    copy.textContent = "当前是快速预览模式，这里先展示页面结构。确认方向后，再开启真实图片生成。";

    const status = document.createElement("div");
    status.className = "pill";
    status.textContent = pageStatusLabel;

    placeholder.appendChild(badge);
    placeholder.appendChild(copy);
    placeholder.appendChild(status);
    return placeholder;
  }

  function buildPageCard(page, generateImages) {
    const card = document.createElement("article");
    card.className = "page-card";

    const topLine = document.createElement("div");
    topLine.className = "page-topline";

    const headingWrap = document.createElement("div");
    const heading = document.createElement("h3");
    heading.textContent = "第 " + page.page_no + " 页";
    const role = document.createElement("p");
    role.className = "page-role";
    role.textContent = labelForRole(page.role);
    headingWrap.appendChild(heading);
    headingWrap.appendChild(role);

    const statusChip = document.createElement("span");
    statusChip.className = "meta-chip";
    statusChip.textContent = generateImages && normalizeOutputImagePath(page.image_path)
      ? "图片已生成"
      : labelForPageStatus(page.status);

    topLine.appendChild(headingWrap);
    topLine.appendChild(statusChip);
    card.appendChild(topLine);

    const imageUrl = normalizeOutputImagePath(page.image_path);
    if (generateImages && imageUrl) {
      const image = document.createElement("img");
      image.className = "page-image";
      image.src = imageUrl;
      image.alt = heading.textContent + " · " + role.textContent;
      card.appendChild(image);
    } else {
      card.appendChild(buildPlaceholder(labelForPageStatus(page.status)));
    }

    const metaRow = document.createElement("div");
    metaRow.className = "meta-row";
    const referenceChip = document.createElement("span");
    referenceChip.className = "meta-chip";
    referenceChip.textContent = page.used_reference ? "参考图已启用" : "当前未使用参考图";
    metaRow.appendChild(referenceChip);
    card.appendChild(metaRow);

    if (Array.isArray(page.issues) && page.issues.length > 0) {
      const issues = document.createElement("p");
      issues.className = "page-issues";
      issues.textContent = "问题：" + page.issues.join(" | ");
      card.appendChild(issues);
    }

    return card;
  }

  function renderPackage(packageData, generateImages, job) {
    clearResults();
    showResults();
    resultMeta.textContent = "已经为你整理出一版可查看的标题、正文、标签和页面结构。";

    noteSummary.appendChild(
      buildSummaryCard(
        "模板",
        styleField.selectedOptions[0] ? styleField.selectedOptions[0].textContent : "自动选择模板"
      )
    );
    noteSummary.appendChild(buildSummaryCard("标题", packageData.selected_title || "—"));
    noteSummary.appendChild(buildSummaryCard("正文", packageData.body || "—"));
    noteSummary.appendChild(buildSummaryCard("标签", buildTagList(packageData.tags || [])));

    setJobMeta({
      job_id: job.job_id,
      note_id: packageData.note_id,
      qa_score: packageData.diagnostics ? packageData.diagnostics.qa_score : null,
      error: job.error || null,
    });

    (packageData.pages || []).forEach(function (page) {
      pagesGrid.appendChild(buildPageCard(page, generateImages));
    });

    if (typeof resultSection.scrollIntoView === "function") {
      resultSection.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }

  function buildVerticalNotesUrl() {
    return "/api/verticals/" + encodeURIComponent(selectedVertical) + "/notes";
  }

  function buildVerticalPackageUrl(noteId) {
    return buildVerticalNotesUrl() + "/" + encodeURIComponent(noteId) + "/package";
  }

  async function fetchJson(url, options) {
    const response = await fetch(url, options);
    let payload = null;
    try {
      payload = await response.json();
    } catch (error) {
      payload = null;
    }
    if (!response.ok) {
      const err = new Error(payload && payload.detail ? payload.detail : "request failed");
      err.status = response.status;
      err.payload = payload;
      err.url = url;
      throw err;
    }
    return payload;
  }

  async function renderJobWithPackage(job, generateImages, statusKey, detailText) {
    if (!job.note_id) {
      throw new Error("job package render requires note_id");
    }

    applyStatus(statusKey, detailText);
    const packageData = await fetchJson(buildVerticalPackageUrl(job.note_id));
    saveLastJob({
      jobId: job.job_id,
      noteId: job.note_id,
      generateImages: generateImages,
    });
    upsertRecentJob({
      jobId: job.job_id,
      noteId: job.note_id,
      generateImages: generateImages,
      brief: briefField.value.trim().slice(0, 60),
      status: statusKey,
      title: packageData.selected_title || "",
      updatedAt: new Date().toISOString(),
    });
    renderRecentJobs();
    renderPackage(packageData, generateImages, job);
    hideResumePanel();
  }

  async function renderSucceededJob(job, generateImages) {
    return renderJobWithPackage(job, generateImages, "succeeded", "生成完成");
  }

  async function renderPartialFailedJob(job, generateImages) {
    return renderJobWithPackage(
      job,
      generateImages,
      "partial_failed",
      "部分内容已生成，可先查看已有预览"
    );
  }

  async function tryRenderPartialFailedJob(job, generateImages) {
    try {
      await renderPartialFailedJob(job, generateImages);
      resultMeta.textContent = "这次任务只完成了部分内容，你可以先查看已生成的标题、正文、标签和页面结构。";
      return true;
    } catch (error) {
      applyStatus("partial_failed", "部分完成，但结果包读取失败");
      resultMeta.textContent = "这次任务只完成了部分内容，可以先看已有结果，再决定是否重新生成。";
      setJobMeta({
        job_id: job.job_id,
        note_id: job.note_id || null,
        error: formatError(error),
        package_path: job.package_path || null,
        diagnostics: job.diagnostics || null,
      });
      return false;
    }
  }

  async function pollJob(jobId, generateImages) {
    const pollConfig = getPollConfig(generateImages);
    const startedAt = Date.now();
    while (Date.now() - startedAt < pollConfig.maxPollMs) {
      const job = await fetchJson("/api/jobs/" + encodeURIComponent(jobId));
      saveLastJob({
        jobId: job.job_id,
        noteId: job.note_id || null,
        generateImages: generateImages,
      });
      upsertRecentJob({
        jobId: job.job_id,
        noteId: job.note_id || null,
        generateImages: generateImages,
        brief: briefField.value.trim().slice(0, 60),
        status: job.status,
        updatedAt: new Date().toISOString(),
      });
      renderRecentJobs();
      if (job.status === "queued") {
        applyStatus("queued", "已提交，等待开始");
      } else if (job.status === "running") {
        applyStatus("running", "正在生成内容");
      }
      setJobMeta(job);
      if (job.status === "succeeded") {
        return { kind: "success", job: job };
      }
      if (job.status === "failed" || job.status === "partial_failed") {
        return { kind: "failed", job: job };
      }
      await new Promise(function (resolve) {
        window.setTimeout(resolve, pollConfig.pollIntervalMs);
      });
    }
    return { kind: "timeout", job: { job_id: jobId } };
  }

  async function continueQuery(jobContext, options) {
    const settings = options || {};
    if (!jobContext || !jobContext.jobId) {
      return;
    }
    if (continueQueryPromise) {
      return continueQueryPromise;
    }

    continueButton.disabled = true;
    continueButton.textContent = "查询中...";

    continueQueryPromise = (async function () {
      try {
        const job = await fetchJson("/api/jobs/" + encodeURIComponent(jobContext.jobId));
        setJobMeta(job);
        saveLastJob({
          jobId: job.job_id,
          noteId: job.note_id || null,
          generateImages: jobContext.generateImages,
        });

        if (job.status === "succeeded") {
          await renderSucceededJob(job, jobContext.generateImages);
          return;
        }

        if (job.status === "partial_failed") {
          if (job.note_id) {
            await tryRenderPartialFailedJob(job, jobContext.generateImages);
          } else {
            applyStatus("partial_failed");
            resultMeta.textContent = "这次任务只完成了部分内容，可以先看已有结果，再决定是否重新生成。";
          }
          return;
        }

        if (job.status === "failed") {
          applyStatus("failed");
          resultMeta.textContent = "这次生成没有完成。你可以修改内容需求后重试，技术错误已保留在开发信息里。";
          return;
        }

        applyStatus(job.status === "running" ? "running" : "queued");
        showResumePanel("生成时间较长，任务可能仍在后台继续运行。你可以稍后点击「继续查询」查看结果。");
        const result = await pollJob(job.job_id, jobContext.generateImages);

        if (result.kind === "timeout") {
          applyStatus("timeout");
          resultMeta.textContent = "生成时间较长，任务可能仍在后台继续运行。你可以稍后点击「继续查询」查看结果。";
          setJobMeta({ job_id: job.job_id, status: "timeout" });
          showResumePanel("生成时间较长，任务可能仍在后台继续运行。你可以稍后点击「继续查询」查看结果。");
          return;
        }

        if (result.kind === "failed") {
          const failedJob = result.job;
          if (failedJob.status === "partial_failed" && failedJob.note_id) {
            await tryRenderPartialFailedJob(failedJob, jobContext.generateImages);
          } else {
            applyStatus(failedJob.status === "partial_failed" ? "partial_failed" : "failed");
            resultMeta.textContent = failedJob.status === "partial_failed"
              ? "这次任务只完成了部分内容，可以先看已有结果，再决定是否重新生成。"
              : "这次生成没有完成。你可以修改内容需求后重试，技术错误已保留在开发信息里。";
            setJobMeta(failedJob);
          }
          return;
        }

        await renderSucceededJob(result.job, jobContext.generateImages);
      } catch (error) {
        const isNotFound = error.status === 404 ||
          (error.message && (
            error.message.includes("404") ||
            error.message.toLowerCase().includes("not found") ||
            error.message.includes("找不到")
          ));
        if (isNotFound) {
          // Fallback: jobStore lost but noteId may still have package on disk
          if (jobContext.noteId) {
            try {
              const packageData = await fetchJson(buildVerticalPackageUrl(jobContext.noteId));
              if (packageData && packageData.pages && packageData.pages.length > 0) {
                applyStatus("restored");
                resultMeta.textContent = "上次任务记录已过期，但已根据结果包恢复内容。";
                renderPackage(packageData, jobContext.generateImages, { job_id: jobContext.jobId, status: "restored", note_id: jobContext.noteId, error: null });
                setJobMeta({
                  note: "从结果包恢复",
                  job_id: jobContext.jobId,
                  note_id: jobContext.noteId,
                  status: "restored",
                });
                upsertRecentJob({
                  jobId: jobContext.jobId,
                  noteId: jobContext.noteId,
                  generateImages: jobContext.generateImages,
                  status: "restored",
                  title: packageData.selected_title || "",
                  updatedAt: new Date().toISOString(),
                });
                renderRecentJobs();
                hideResumePanel();
                return;
              }
            } catch (fallbackErr) {
              // fallback also failed, fall through to error message
            }
          }
          clearLastJob();
          applyStatus("failed", "无法找到上次任务");
          resultMeta.textContent = "无法找到上次任务，可能已过期或被清除。";
          setJobMeta({ error: formatError(error), note: "任务不存在或已失效" });
          hideResumePanel();
        } else {
          applyStatus("failed", "暂时无法查询任务");
          resultMeta.textContent = "暂时无法查询任务，任务可能仍在后台继续运行。你可以稍后点击「继续查询」查看结果。";
          setJobMeta({ error: formatError(error), url: error.url || null, status: error.status || null });
          // keep resume panel open so user can retry
        }
      } finally {
        continueQueryPromise = null;
        continueButton.disabled = false;
        continueButton.textContent = "继续查询";
        if (!settings.keepPanelOpen && statusBadge.textContent === APP_CONFIG.jobStatusMap.succeeded.badge) {
          hideResumePanel();
        }
      }
    })();

    return continueQueryPromise;
  }

  exampleButton.addEventListener("click", function () {
    briefField.value = APP_CONFIG.exampleBrief;
    if (!skinToneField.value) {
      skinToneField.value = "黄皮";
    }
    if (!nailLengthField.value) {
      nailLengthField.value = "短甲";
    }
  });

  if (verticalField) {
    verticalField.addEventListener("change", async function () {
      const nextVertical = verticalField.value;
      if (!nextVertical || nextVertical === selectedVertical) {
        return;
      }
      updateCurrentVerticalState(nextVertical);
      initializeFormOptions();
      clearCaseSelection();
      clearReferenceImage({ preserveCaseSelection: true });
      await loadCaseLibrary();
      await loadServerHistory();
    });
  }

  if (caseIdField) {
    caseIdField.addEventListener("input", function () {
      const typed = caseIdField.value.trim();
      if (!typed) {
        clearCaseSelection({ preserveInput: true });
        return;
      }
      if (selectedCase && selectedCase.case_id === typed) {
        return;
      }
      selectedCase = null;
      renderSelectedCasePanel();
      renderCaseLibrary();
      if (currentReferenceImage) {
        clearReferenceImage({ preserveCaseSelection: true });
      }
    });
  }

  if (clearCaseButton) {
    clearCaseButton.addEventListener("click", function () {
      clearCaseSelection();
    });
  }

  styleField.addEventListener("change", updateStyleHelper);
  if (refreshHistoryButton) {
    refreshHistoryButton.addEventListener("click", async function () {
      await loadServerHistory();
    });
  }
  continueButton.addEventListener("click", function () {
    const storedJob = loadLastJob();
    if (!storedJob) {
      return;
    }
    continueQuery(storedJob, { keepPanelOpen: false });
  });
  clearJobButton.addEventListener("click", function () {
    clearLastJob();
    hideResumePanel();
    setJobMeta("任务已清除");
    resultMeta.textContent = "生成完成后，这里会展示标题、正文、标签和多页内容结构。";
    applyStatus("idle");
  });

  form.addEventListener("submit", async function (event) {
    event.preventDefault();
    clearResults();
    hideResumePanel();
    submitButton.disabled = true;
    submitButton.textContent = "生成中...";

    const generateImages = enableImagesField.checked;
    const caseIdValue = caseIdField && caseIdField.value ? caseIdField.value.trim() : "";
    let referenceSource = "none";
    let referenceImagePath;
    let effectiveCaseId;

    if (caseIdValue) {
      referenceSource = "case_id";
      effectiveCaseId = caseIdValue;
    } else if (currentReferenceImage && currentReferenceImage.path) {
      referenceSource = "local_path";
      referenceImagePath = currentReferenceImage.path;
    }

    const payload = sanitizePayload({
      brief: briefField.value,
      style_id: styleField.value,
      skin_tone: skinToneField.value,
      nail_length: nailLengthField.value,
      generate_images: generateImages,
      max_workers: Number(maxWorkersField.value || "1"),
      reference_source: referenceSource,
      reference_image_path: referenceImagePath,
      case_id: effectiveCaseId,
    });

    try {
      applyStatus("queued");
      setJobMeta(payload);

      const created = await fetchJson("/api/nail/notes", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      applyStatus("queued", "已提交，等待开始");
      setJobMeta({ job_id: created.job_id, payload: payload });
      addRecentJob({
        jobId: created.job_id,
        noteId: null,
        generateImages: generateImages,
        brief: briefField.value.slice(0, 60),
        status: "queued",
        createdAt: new Date().toISOString(),
      });
      renderRecentJobs();
      saveLastJob({
        jobId: created.job_id,
        noteId: null,
        generateImages: generateImages,
      });

      const result = await pollJob(created.job_id, generateImages);
      if (result.kind === "timeout") {
        applyStatus("timeout");
        resultMeta.textContent = "生成时间较长，任务可能仍在后台继续运行。你可以稍后点击「继续查询」查看结果。";
        setJobMeta({ job_id: created.job_id, status: "timeout" });
        showResumePanel("生成时间较长，任务可能仍在后台继续运行。你可以稍后点击「继续查询」查看结果。");
        return;
      }

      if (result.kind === "failed") {
        const job = result.job;
        const finalStatus = job && job.status === "partial_failed" ? "partial_failed" : "failed";
        if (finalStatus === "partial_failed" && job && job.note_id) {
          await tryRenderPartialFailedJob(job, generateImages);
        } else {
          applyStatus(finalStatus);
          resultMeta.textContent = finalStatus === "partial_failed"
            ? "这次任务只完成了部分内容，可以先看已有结果，再决定是否重新生成。"
            : "这次生成没有完成。你可以修改内容需求后重试，技术错误已保留在开发信息里。";
          setJobMeta(job || { job_id: created.job_id, status: finalStatus });
        }
        return;
      }

      await renderSucceededJob(result.job, generateImages);
    } catch (error) {
      applyStatus("failed", "生成失败");
      resultMeta.textContent = "这次生成没有完成。你可以修改内容需求后重试，技术错误已保留在开发信息里。";
      setJobMeta({ error: formatError(error) });
    } finally {
      submitButton.disabled = false;
      submitButton.textContent = "生成内容预览";
    }
  });

  // --- Reference image upload ---
  let currentReferenceImage = null; // { path, previewUrl }

  const refInput = document.getElementById("reference-image-input");
  const refPlaceholder = document.getElementById("reference-placeholder");
  const refPreview = document.getElementById("reference-preview");
  const refPreviewImg = document.getElementById("reference-preview-img");
  const refRemoveBtn = document.getElementById("reference-remove-btn");
  const dropZone = document.getElementById("reference-drop-zone");

  function showReferencePreview(previewUrl) {
    refPlaceholder.hidden = true;
    refPreview.hidden = false;
    refPreviewImg.src = previewUrl;
  }

  function clearReferenceImage(options) {
    const settings = options || {};
    currentReferenceImage = null;
    refPreview.hidden = true;
    refPlaceholder.hidden = false;
    refPreviewImg.src = "";
    if (refInput) refInput.value = "";
    if (!settings.preserveCaseSelection) {
      renderCaseLibrary();
    }
  }

  if (refRemoveBtn) {
    refRemoveBtn.addEventListener("click", function (e) {
      e.stopPropagation();
      clearReferenceImage();
    });
  }

  if (dropZone) {
    dropZone.addEventListener("click", function () {
      if (refInput) refInput.click();
    });
    dropZone.addEventListener("dragover", function (e) {
      e.preventDefault();
      dropZone.classList.add("drag-over");
    });
    dropZone.addEventListener("dragleave", function () {
      dropZone.classList.remove("drag-over");
    });
    dropZone.addEventListener("drop", function (e) {
      e.preventDefault();
      dropZone.classList.remove("drag-over");
      const files = e.dataTransfer && e.dataTransfer.files;
      if (files && files.length > 0) {
        uploadReferenceFile(files[0]);
      }
    });
  }

  async function uploadReferenceFile(file) {
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    try {
      const resp = await fetch("/api/nail/assets/reference-image", {
        method: "POST",
        body: formData,
      });
      const data = await resp.json();
      if (!resp.ok) {
        throw new Error(data.detail || "上传失败");
      }
      currentReferenceImage = {
        path: data.reference_image_path,
        previewUrl: data.preview_url,
      };
      if (selectedCase || (caseIdField && caseIdField.value.trim())) {
        clearCaseSelection();
      }
      showReferencePreview(data.preview_url);
    } catch (err) {
      alert("上传失败：" + formatError(err));
      clearReferenceImage();
    }
  }

  if (refInput) {
    refInput.addEventListener("change", async function () {
      const file = refInput.files && refInput.files[0];
      if (!file) return;
      await uploadReferenceFile(file);
    });
  }

  // --- Recent jobs (localStorage) ---
  const RECENT_JOBS_KEY = "nail_studio_recent_jobs";
  function addRecentJob(entry) {
    upsertRecentJob(entry);
  }

  function renderRecentJobs() {
    const container = document.getElementById("recent-jobs-list");
    const panel = document.getElementById("recent-jobs-panel");
    if (!container || !panel) return;
    const jobs = getRecentJobs();
    panel.hidden = !jobs.length;
    if (!jobs.length) return;
    container.hidden = false;
    container.innerHTML = "";
    jobs.forEach(function (job) {
      const item = document.createElement("article");
      item.className = "recent-job-item";
      item.dataset.jobId = job.jobId;
      const date = job.createdAt ? new Date(job.createdAt).toLocaleString("zh-CN", { month: "numeric", day: "numeric", hour: "2-digit", minute: "2-digit" }) : "";
      const brief = job.brief || "";
      const status = jobStatusLabel(job.status || "idle");
      const mode = generationModeLabel(Boolean(job.generateImages));

      const meta = document.createElement("div");
      meta.className = "recent-job-meta";
      const jobIdSpan = document.createElement("span");
      jobIdSpan.className = "recent-job-id";
      jobIdSpan.textContent = ((job.jobId || "").slice(0, 12) || "unknown") + "...";
      const statusSpan = document.createElement("span");
      statusSpan.className = "recent-job-status";
      statusSpan.textContent = status;
      const modeSpan = document.createElement("span");
      modeSpan.className = "recent-job-mode";
      modeSpan.textContent = mode;
      meta.appendChild(jobIdSpan);
      meta.appendChild(statusSpan);
      meta.appendChild(modeSpan);

      const summary = document.createElement("div");
      summary.className = "recent-job-summary";
      const briefSpan = document.createElement("span");
      briefSpan.className = "recent-job-brief";
      briefSpan.textContent = brief;
      const timeSpan = document.createElement("span");
      timeSpan.className = "recent-job-time";
      timeSpan.textContent = date;
      summary.appendChild(briefSpan);
      summary.appendChild(timeSpan);

      const actions = document.createElement("div");
      actions.className = "recent-job-actions";

      const continueJobButton = document.createElement("button");
      continueJobButton.type = "button";
      continueJobButton.className = "secondary-button recent-job-open";
      continueJobButton.textContent = "继续查看";
      continueJobButton.addEventListener("click", function () {
        const stored = { jobId: job.jobId, noteId: job.noteId, generateImages: job.generateImages };
        setJobMeta({ job_id: job.jobId });
        saveLastJob(stored);
        showResumePanel("发现历史任务，是否继续查看？");
        resultMeta.textContent = "从最近任务列表恢复，可直接继续查询结果。";
      });

      const deleteJobButton = document.createElement("button");
      deleteJobButton.type = "button";
      deleteJobButton.className = "ghost-button recent-job-delete";
      deleteJobButton.textContent = "删除记录";
      deleteJobButton.addEventListener("click", function () {
        removeRecentJob(job.jobId);
        if (currentJobContext && currentJobContext.jobId === job.jobId) {
          clearLastJob();
          hideResumePanel();
        }
        renderRecentJobs();
      });

      actions.appendChild(continueJobButton);
      actions.appendChild(deleteJobButton);
      item.appendChild(meta);
      item.appendChild(summary);
      item.appendChild(actions);
      container.appendChild(item);
    });
  }

  function loadRecentJobs() {
    renderRecentJobs();
  }

  async function initializeApp() {
    initializeFormOptions();
    clearResults();
    applyStatus("idle");
    if (recentJobsTitle) {
      recentJobsTitle.textContent = "最近任务快捷入口";
    }
    loadRecentJobs();
    const storedJob = loadLastJob();
    if (storedJob && storedJob.jobId) {
      setJobMeta(storedJob);
      showResumePanel("发现上次任务，是否继续查看？");
      resultMeta.textContent = "如果你上次的任务已经跑完，可以直接继续查询并恢复内容预览。";
    }
    try {
      await loadVerticalOptions();
      await loadCaseLibrary();
      await loadServerHistory();
    } catch (error) {
      setJobMeta({
        note: "vertical bootstrap failed",
        status: error.status || null,
        url: error.url || null,
        error: formatError(error),
      });
    }
  }

  initializeApp();

  window.__nailStudioDebug = function () {
    return {
      hasResumePanel: Boolean(document.querySelector("#resume-panel")),
      resumePanelHidden: document.querySelector("#resume-panel")
        ? document.querySelector("#resume-panel").hidden
        : null,
      resumeText: document.querySelector("#resume-text")
        ? document.querySelector("#resume-text").textContent
        : null,
      hasContinueButton: Boolean(document.querySelector("#continue-button")),
      hasClearJobButton: Boolean(document.querySelector("#clear-job-button")),
    };
  };
})();
