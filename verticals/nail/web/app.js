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

  const currentVertical = APP_CONFIG.verticals[APP_CONFIG.currentVertical];
  const form = document.getElementById("note-form");
  const briefField = document.getElementById("brief");
  const styleField = document.getElementById("style_id");
  const styleHelper = document.getElementById("style-helper");
  const skinToneField = document.getElementById("skin_tone");
  const nailLengthField = document.getElementById("nail_length");
  const enableImagesField = document.getElementById("enable_images");
  const maxWorkersField = document.getElementById("max_workers");
  const exampleButton = document.getElementById("example-button");
  const submitButton = document.getElementById("submit-button");
  const statusText = document.getElementById("status-text");
  const progressDetail = document.getElementById("progress-detail");
  const statusBadge = document.getElementById("status-badge");
  const resultMeta = document.getElementById("result-meta");
  const resultSection = document.getElementById("result-section");
  const resultEmpty = document.getElementById("result-empty");
  const noteSummary = document.getElementById("note-summary");
  const pagesGrid = document.getElementById("pages-grid");
  const jobMeta = document.getElementById("job-meta");
  const resumePanel = document.getElementById("resume-panel");
  const resumeText = document.getElementById("resume-text");
  const continueButton = document.getElementById("continue-button");

  const STORAGE_KEY = "nail_studio_last_job";
  let currentJobContext = null;
  let continueQueryPromise = null;

  function populateSelect(selectElement, options) {
    selectElement.innerHTML = "";
    options.forEach(function (option) {
      const element = document.createElement("option");
      element.value = option.value;
      element.textContent = option.label;
      selectElement.appendChild(element);
    });
  }

  function updateStyleHelper() {
    const selected = currentVertical.styleOptions.find(function (item) {
      return item.value === styleField.value;
    }) || currentVertical.styleOptions[0];
    styleHelper.textContent = selected.description;
  }

  function initializeFormOptions() {
    populateSelect(styleField, currentVertical.styleOptions);
    populateSelect(skinToneField, currentVertical.skinToneOptions);
    populateSelect(nailLengthField, currentVertical.nailLengthOptions);
    updateStyleHelper();
  }

  function setJobMeta(payload) {
    jobMeta.textContent = typeof payload === "string" ? payload : JSON.stringify(payload, null, 2);
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
    try {
      window.localStorage.setItem(STORAGE_KEY, JSON.stringify(context));
    } catch (error) {
      // Ignore storage failures and keep the in-memory context.
    }
  }

  function clearLastJob() {
    currentJobContext = null;
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
      return currentJobContext;
    } catch (error) {
      return null;
    }
  }

  function showResumePanel(message) {
    resumeText.textContent = message;
    resumePanel.hidden = false;
  }

  function hideResumePanel() {
    resumePanel.hidden = true;
  }

  function applyStatus(stateKey, detailText) {
    const state = APP_CONFIG.jobStatusMap[stateKey] || APP_CONFIG.jobStatusMap.idle;
    statusText.textContent = state.title;
    progressDetail.textContent = detailText || state.detail;
    statusBadge.textContent = state.badge;
    statusBadge.className = "status-badge status-" + stateKey;
  }

  function clearResults() {
    noteSummary.innerHTML = "";
    pagesGrid.innerHTML = "";
    resultEmpty.hidden = false;
    resultMeta.textContent = "生成完成后，这里会展示标题、正文、标签和多页内容结构。";
  }

  function showResults() {
    resultEmpty.hidden = true;
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
      output_dir: packageData.output_dir,
      package_path: packageData.package_path,
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

  async function fetchJson(url, options) {
    const response = await fetch(url, options);
    let payload = null;
    try {
      payload = await response.json();
    } catch (error) {
      payload = null;
    }
    if (!response.ok) {
      throw new Error(payload && payload.detail ? payload.detail : "request failed");
    }
    return payload;
  }

  async function renderSucceededJob(job, generateImages) {
    if (!job.note_id) {
      throw new Error("job succeeded but note_id is missing");
    }

    applyStatus("succeeded", "生成完成");
    const packageData = await fetchJson("/api/nail/notes/" + encodeURIComponent(job.note_id) + "/package");
    saveLastJob({
      jobId: job.job_id,
      noteId: job.note_id,
      generateImages: generateImages,
    });
    renderPackage(packageData, generateImages, job);
    hideResumePanel();
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

        if (job.status === "failed" || job.status === "partial_failed") {
          applyStatus(job.status === "failed" ? "failed" : "partial_failed");
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
          applyStatus(failedJob.status === "partial_failed" ? "partial_failed" : "failed");
          resultMeta.textContent = "这次生成没有完成。你可以修改内容需求后重试，技术错误已保留在开发信息里。";
          setJobMeta(failedJob);
          return;
        }

        await renderSucceededJob(result.job, jobContext.generateImages);
      } catch (error) {
        applyStatus("failed", "生成失败");
        resultMeta.textContent = "这次生成没有完成。你可以修改内容需求后重试，技术错误已保留在开发信息里。";
        setJobMeta({ error: error.message || String(error) });
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

  styleField.addEventListener("change", updateStyleHelper);
  continueButton.addEventListener("click", function () {
    const storedJob = loadLastJob();
    if (!storedJob) {
      return;
    }
    continueQuery(storedJob, { keepPanelOpen: false });
  });

  form.addEventListener("submit", async function (event) {
    event.preventDefault();
    clearResults();
    hideResumePanel();
    submitButton.disabled = true;
    submitButton.textContent = "生成中...";

    const generateImages = enableImagesField.checked;
    const payload = sanitizePayload({
      brief: briefField.value,
      style_id: styleField.value,
      skin_tone: skinToneField.value,
      nail_length: nailLengthField.value,
      generate_images: generateImages,
      max_workers: Number(maxWorkersField.value || "1"),
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
        applyStatus("failed", "生成失败");
        resultMeta.textContent = "这次生成没有完成。你可以修改内容需求后重试，技术错误已保留在开发信息里。";
        setJobMeta(job || { job_id: created.job_id, status: "failed" });
        return;
      }

      await renderSucceededJob(result.job, generateImages);
    } catch (error) {
      applyStatus("failed", "生成失败");
      resultMeta.textContent = "这次生成没有完成。你可以修改内容需求后重试，技术错误已保留在开发信息里。";
      setJobMeta({ error: error.message || String(error) });
    } finally {
      submitButton.disabled = false;
      submitButton.textContent = "生成内容预览";
    }
  });

  initializeFormOptions();
  clearResults();
  applyStatus("idle");
  const storedJob = loadLastJob();
  if (storedJob && storedJob.jobId) {
    setJobMeta(storedJob);
    showResumePanel("发现上次任务，是否继续查看？");
    resultMeta.textContent = "如果你上次的任务已经跑完，可以直接继续查询并恢复内容预览。";
  }
})();
