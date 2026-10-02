"use strict";

(() => {
  const $ = (selector) => document.querySelector(selector);
  const app = $("#app");
  const dialog = $("#confirm-dialog");
  const icons = {
    logo: '<path d="M5 5h14v5H10v9H5z" fill="currentColor" stroke="none"/>',
    grid: '<rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/>',
    book: '<path d="M4 4h6a3 3 0 0 1 3 3v14a4 4 0 0 0-4-2H4zM13 7a3 3 0 0 1 3-3h4v15h-3a4 4 0 0 0-4 2"/>',
    chart: '<path d="M4 20V11m8 9V4m8 16v-6M2 22h20"/>',
    clock: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    shield:
      '<path d="m12 3 8 3v6c0 5-8 9-8 9s-8-4-8-9V6z"/><path d="m8 12 3 3 5-6"/>',
    arrow: '<path d="M4 12h16m-6-6 6 6-6 6"/>',
    back: '<path d="M20 12H4m6-6-6 6 6 6"/>',
    check: '<path d="m5 12 4 4L19 6"/>',
    flag: '<path d="M5 21V3m0 1c5-4 9 4 14 0v10c-5 4-9-4-14 0"/>',
    info: '<circle cx="12" cy="12" r="9"/><path d="M12 11v6m0-10v.1"/>',
    lock: '<rect x="5" y="10" width="14" height="11" rx="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3m-4 5v2"/>',
    bolt: '<path d="m13 2-9 12h7l-1 8 10-13h-8z"/>',
    down: '<path d="m6 9 6 6 6-6"/>',
    terminal: '<path d="m4 6 5 6-5 6m9 0h7"/>',
    restart: '<path d="M3 10a9 9 0 1 1 2 8M3 4v6h6"/>',
  };
  const icon = (name, size = 18) =>
    `<svg width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.65" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${icons[name] || icons.info}</svg>`;
  const esc = (value) =>
    String(value ?? "").replace(
      /[&<>"']/g,
      (ch) =>
        ({
          "&": "&amp;",
          "<": "&lt;",
          ">": "&gt;",
          '"': "&quot;",
          "'": "&#39;",
        })[ch],
    );
  let meta = null;
  let session = null;
  let answers = {};
  let flags = [];
  let view = "overview";
  let index = 0;
  let offset = 0;
  let busy = false;
  let saveStatus = "saved";
  let saveError = "";
  let pending = new Map();
  let savePromise = null;
  let debounce = null;
  let expiryRequested = false;
  let reviewFilter = "all";
  let toastTimer = null;
  let pendingCommand = null;
  let resetNotice = "";
  let checkingVersion = false;

  async function request(path, method = "GET", body) {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 15000);
    let response;
    try {
      response = await fetch(path, {
        method,
        credentials: "same-origin",
        signal: controller.signal,
        headers: {
          Accept: "application/json",
          ...(session && method !== "GET" && !(path === "/api/exam" && method === "POST")
            ? { "X-Exam-Bank": session.bank_version, "X-Exam-Id": session.id } : {}),
          ...(method !== "GET" ? { "Content-Type": "application/json" } : {}),
        },
        ...(body !== undefined ? { body: JSON.stringify(body) } : {}),
      });
    } catch (error) {
      throw new Error(
        error.name === "AbortError"
          ? "The connection timed out. Your changes are still here; retry to save them."
          : "Connection interrupted. Your changes are still here; reconnect and retry.",
      );
    } finally {
      clearTimeout(timeout);
    }
    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
      const error = new Error(
        data.error ||
          `The server could not complete that action (${response.status}).`,
      );
      error.status = response.status;
      error.code = data.code;
      if (data.code === "exam_reset") resetAttempt(data.error);
      throw error;
    }
    return data;
  }

  function resetAttempt(message) {
    pending.clear();
    clearTimeout(debounce);
    pendingCommand = null;
    session = null;
    answers = {};
    flags = [];
    index = 0;
    offset = 0;
    expiryRequested = false;
    saveStatus = "saved";
    saveError = "";
    reviewFilter = "all";
    view = "overview";
    resetNotice = message;
    if (dialog.open) dialog.close();
    setBusy(false);
    if (meta) render(true);
  }

  async function checkBankVersion() {
    if (!session || busy || checkingVersion || document.hidden) return;
    checkingVersion = true;
    try {
      const latest = await request("/api/meta");
      if (session && session.bank_version !== latest.blueprint.bank_version) {
        meta = latest;
        resetAttempt("New questions are available. Enter your name to start a fresh exam; previous answers and time do not carry over.");
      }
    } catch (_) {
      // Connectivity errors must not erase a valid current attempt.
    } finally {
      checkingVersion = false;
    }
  }

  function adopt(next, hydrate = false) {
    session = next;
    offset = Number(next.server_now) - Date.now() / 1000;
    if (hydrate) {
      answers = structuredClone(next.answers || {});
      flags = [...(next.flags || [])];
      index = Math.max(
        0,
        Math.min(next.questions.length - 1, next.current_index || 0),
      );
    }
    if (next.status !== "active") {
      pending.clear();
      clearTimeout(debounce);
      answers = structuredClone(next.answers || {});
      flags = [...(next.flags || [])];
      if (dialog.open) dialog.close();
      view = "results";
      render();
    }
  }

  function isAnswered(question) {
    if (question.lab === "raid")
      return Boolean(
        session?.raid?.diagnosed ||
        session?.raid?.identified ||
        session?.raid?.replaced ||
        session?.raid?.rebuilt,
      );
    const answer = answers[question.id];
    if (Array.isArray(answer)) return answer.length > 0;
    if (answer && typeof answer === "object")
      return Object.values(answer).some(
        (value) => value !== "" && value !== null && value !== undefined,
      );
    return false;
  }
  const answeredCount = () => session?.questions.filter(isAnswered).length || 0;
  const domainName = (id) =>
    (session?.domains || meta.domains).find((domain) => domain.id === id)?.name || `Domain ${id}`;
  const remaining = () =>
    Math.max(0, Math.ceil(session.deadline - (Date.now() / 1000 + offset)));
  const durationLabel = (seconds) =>
    `${Math.floor(seconds / 60)}:${String(Math.floor(seconds % 60)).padStart(2, "0")}`;
  const shortDomain = (name) => name.replace(/^\d\.0\s*/, "");

  function toast(message, type = "") {
    const target = $("#toast");
    clearTimeout(toastTimer);
    target.textContent = message;
    target.className = `toast ${type}`;
    target.hidden = false;
    toastTimer = setTimeout(() => {
      target.hidden = true;
    }, 6500);
  }

  function shell(content, crumb) {
    return `<div class="shell"><aside class="sidebar" aria-label="Workspace navigation">
      <a class="brand" href="#" data-action="overview" aria-label="Core 1 overview"><span class="brand-mark">${icon("logo", 23)}</span><span class="brand-name">core<span> / 01</span></span></a>
      <div class="brand-caption">THE EXAM WORKSPACE</div><div class="nav-label">YOUR WORKSPACE</div>
      <nav aria-label="Main"><button class="nav-button ${view === "overview" ? "active" : ""}" data-action="overview" aria-label="Overview" ${view === "overview" ? 'aria-current="page"' : ""}>${icon("grid")}<span>Overview</span></button>
      <button class="nav-button ${view === "exam" ? "active" : ""}" data-action="exam" aria-label="Exam workspace" ${!session || session?.status !== "active" ? "disabled" : ""} ${view === "exam" ? 'aria-current="page"' : ""}>${icon("book")}<span>Exam workspace</span>${session?.status === "active" ? '<span class="nav-badge">LIVE</span>' : ""}</button>
      <button class="nav-button ${view === "results" ? "active" : ""}" data-action="results" aria-label="Results" ${!session?.report ? "disabled" : ""} ${view === "results" ? 'aria-current="page"' : ""}>${icon("chart")}<span>Results & review</span></button></nav>
      <div class="sidebar-bottom"><div class="edition-card"><div class="edition-line"><span class="edition-dot"></span> A+ Core 1 · ${esc(view === "overview" ? meta.exam_code : session?.exam_code || meta.exam_code)}</div><p>Objectives-aligned practice.<br>Independent practice material.</p></div><div class="sidebar-foot">${icon("lock", 12)} Your progress, saved automatically</div></div>
      </aside><div class="workspace"><header class="topbar ${session?.status === "active" ? "with-timer" : ""}"><div class="breadcrumb">Certification practice <span>/</span> <strong>${esc(crumb)}</strong></div>${session?.status === "active" ? '<div class="compact-timer" aria-label="Time remaining"><span>Time left</span><strong id="compact-timer-value" class="mono"></strong></div>' : '<div class="workspace-status">Practice workspace</div>'}</header><main class="content ${view === "exam" ? "exam-content" : ""}" id="main" tabindex="-1">${content}</main></div></div>`;
  }
  function footer() {
    return `<p class="page-foot">${icon("info", 13)}<span>${esc(view === "overview" ? meta.disclaimer : session?.disclaimer || meta.disclaimer)}</span></p>`;
  }
  function overview() {
    const active = session?.status === "active";
    return `<div class="page-heading"><div><div class="eyebrow">A+ CORE 1 · 220-1201</div><h1>Core 1 practice exam</h1><p>Your space to put knowledge into practice and see where you stand.</p></div><span class="version-pill">220-1201 · OBJECTIVES v4.0</span></div>
      ${resetNotice ? `<div class="legacy-notice" role="status">${esc(resetNotice)}</div>` : ""}
      <div class="stats-row"><div class="stat-card"><span class="stat-icon">${icon("book", 21)}</span><div><div class="stat-value">${meta.question_count} <span>questions</span></div><div class="stat-label">Including 5 interactive labs</div></div></div><div class="stat-card"><span class="stat-icon">${icon("clock", 21)}</span><div><div class="stat-value">${meta.duration_seconds / 60} <span>minutes</span></div><div class="stat-label">One uninterrupted session</div></div></div><div class="stat-card"><span class="stat-icon">${icon("shield", 21)}</span><div><div class="stat-value">675 <span>/ 900</span></div><div class="stat-label">Practice passing threshold</div></div></div></div>
      <div class="dashboard-grid"><section class="launch-card"><div class="launch-tag">${icon("bolt", 14)} ${active ? "SESSION IN PROGRESS" : "FULL-LENGTH EXAM"}</div><h2>${active ? "Pick up where you left off." : "90 questions. Five practical labs."}</h2><p>${active ? `${answeredCount()} of ${meta.question_count} questions answered. Your timer is still running; return to your session to continue.` : "Work through realistic scenarios and practical labs across all five Core 1 domains. Review your results when you finish."}</p>${!active ? nameField() : ""}<button class="btn primary" data-action="${active ? "exam" : "start"}">${active ? "Resume exam" : "Start practice exam"} ${icon("arrow", 16)}</button><div class="launch-footer">${icon("lock", 11)} ${active ? "Answers are saved to this workspace" : "Your timer starts when you begin"}</div>${active && session.exam_code !== meta.exam_code ? '<p class="legacy-notice">Your saved attempt is 220-1101.</p><button class="btn" data-action="new-dialog">Start 220-1201 instead</button>' : ""}</section>
      <section class="panel blueprint" aria-labelledby="blueprint-title"><div class="card-heading"><h2 id="blueprint-title">The exam blueprint</h2><span class="eyebrow">5 DOMAINS</span></div><div class="domain-list">${meta.domains.map((domain) => `<div class="domain-row"><div class="domain-top"><span>${esc(shortDomain(domain.name))}</span><strong>${domain.weight}%</strong></div><progress class="domain-track" max="100" value="${domain.weight}" aria-label="${esc(domain.name)} blueprint weight ${domain.weight} percent"></progress></div>`).join("")}</div><p class="blueprint-foot">Mapped to all 27 numbered 220-1201 objectives. This fixed 90-item practice form samples the published scope; it does not reproduce the real exam.</p></section></div>
      <section class="panel prep-panel" aria-labelledby="before-title"><div class="card-heading"><h2 id="before-title">Before you begin</h2><span class="eyebrow">A QUICK BRIEFING</span></div><div class="prep-grid"><div class="prep-item"><span class="prep-number">01</span><div><h3>Make the time yours</h3><p>The 90-minute timer keeps running if you leave. Your saved session resumes in this browser.</p></div></div><div class="prep-item"><span class="prep-number">02</span><div><h3>Work through the labs</h3><p>Five practical tasks come first. Partial credit counts, so complete the steps you know.</p></div></div><div class="prep-item"><span class="prep-number">03</span><div><h3>Flag it. Come back to it.</h3><p>Jump between questions, flag uncertain answers, and review before you submit.</p></div></div></div></section>${footer()}`;
  }

  function grid() {
    return session.questions
      .map(
        (question, questionIndex) =>
          `<button class="grid-button ${isAnswered(question) ? "answered" : ""} ${flags.includes(question.id) ? "flagged" : ""} ${questionIndex === index ? "current" : ""}" data-index="${questionIndex}" aria-label="Question ${questionIndex + 1}, ${isAnswered(question) ? "answered" : "unanswered"}${flags.includes(question.id) ? ", flagged" : ""}" ${questionIndex === index ? 'aria-current="step"' : ""}>${questionIndex + 1}</button>`,
      )
      .join("");
  }
  function exam() {
    const question = session.questions[index];
    return `<div class="page-heading exam-heading"><div><div class="eyebrow">A+ CORE 1 · ${esc(session.exam_code)}</div><h1>Practice in progress</h1><p>${session.candidate_name ? `Candidate: <strong dir="auto">${esc(session.candidate_name)}</strong> · ` : ""}You can return to any question.</p></div><div id="save-status" class="save-status" role="status" aria-live="polite"></div></div>
      <div class="exam-layout"><div><section class="panel question-card" aria-labelledby="question-title"><div class="question-meta"><span class="question-number">QUESTION ${String(index + 1).padStart(2, "0")} <span class="muted">/ ${session.questions.length}</span></span><span class="chip">${esc(shortDomain(domainName(question.domain)))}</span>${question.kind === "pbq" ? '<span class="chip lab">INTERACTIVE LAB</span>' : ""}</div><h2 class="question-title" id="question-title" tabindex="-1">${esc(question.title)}</h2><p class="question-prompt">${esc(question.prompt)}</p>${question.kind === "pbq" ? lab(question) : choices(question)}<div class="question-tools"><button class="flag-button ${flags.includes(question.id) ? "flagged" : ""}" id="flag-button" data-action="flag" aria-pressed="${flags.includes(question.id)}">${icon("flag", 15)}<span>${flags.includes(question.id) ? "Flagged for review" : "Flag for review"}</span></button>${question.lab !== "raid" ? '<button class="clear-button" data-action="clear-answer">Clear answer</button>' : '<span class="muted lab-note">Lab state is saved automatically</span>'}</div></section><div class="exam-navigation"><button class="btn" data-action="previous" ${index === 0 ? "disabled" : ""}>${icon("back", 14)} Previous</button><div class="nav-right">${index < session.questions.length - 1 ? '<button class="btn subtle" data-action="skip">Skip for now</button><button class="btn primary" data-action="next">Next question ' + icon("arrow", 14) + "</button>" : '<button class="btn primary" data-action="submit-dialog">Review & submit ' + icon("check", 15) + "</button>"}</div></div></div>
      <aside class="exam-aside" aria-label="Exam progress"><section class="panel timer-card"><div class="timer-label">${icon("clock", 14)} Time remaining</div><div class="timer-value mono" id="timer" aria-label="Time remaining">90:00</div><progress class="timer-bar" id="timer-progress" max="${meta.duration_seconds}" value="${remaining()}" aria-label="Remaining exam time"></progress><p class="timer-note">Timer continues while you are away.</p></section><section class="panel navigator-card"><div class="navigator-heading">Question navigator <span id="answered-label">${answeredCount()} / ${session.questions.length}</span></div><div class="question-grid" id="question-grid" aria-label="Jump to question">${grid()}</div><div class="grid-legend"><span><i class="legend-dot"></i> Answered</span><span><i class="legend-dot empty"></i> Unanswered</span><span><i class="legend-dot flag"></i> Flagged</span></div><button class="btn" data-action="submit-dialog">Finish & submit ${icon("arrow", 13)}</button></section><p class="progress-text">${icon("info", 13)}Your answers remain editable until you submit or time runs out.</p></aside></div>${footer()}`;
  }
  function choices(question) {
    const selected = answers[question.id] || [];
    return `<p class="selection-hint" id="selection-hint">${question.kind === "multiple" ? `Choose ${question.select_count} answers. <span id="selection-count">${selected.length} selected.</span>` : "Choose the best answer."}</p><fieldset class="options" aria-label="Answer choices" aria-describedby="selection-hint">${question.options.map((option, optionIndex) => `<label class="answer-option ${selected.includes(option.id) ? "selected" : ""}"><input type="${question.kind === "multiple" ? "checkbox" : "radio"}" name="question-answer" value="${esc(option.id)}" ${selected.includes(option.id) ? "checked" : ""}><span class="option-letter">${String.fromCharCode(65 + optionIndex)}</span><span class="option-text">${esc(option.text)}</span></label>`).join("")}</fieldset>`;
  }
  function lab(question) {
    const briefing = question.briefing?.length
      ? `<div class="lab-briefing"><h3>YOUR TASK</h3><ul>${question.briefing.map((line) => `<li>${esc(line)}</li>`).join("")}</ul></div>`
      : "";
    const reference = question.reference
      ? `<pre class="lab-reference">${esc(question.reference)}</pre>`
      : "";
    if (question.lab === "raid") return `${briefing}${reference}${terminal()}`;
    let group = null;
    const saved = answers[question.id] || {};
    const fields = question.fields
      .map((field) => {
        let heading = "";
        if (field.group && field.group !== group) {
          group = field.group;
          heading = `<h3 class="lab-group">${esc(group)}</h3>`;
        }
        return `${heading}<div class="lab-field"><label for="field-${esc(field.id)}">${esc(field.label)}</label>${field.type === "select" ? `<select id="field-${esc(field.id)}" data-field="${esc(field.id)}"><option value="">Select an option</option>${field.options.map((option) => `<option value="${esc(option.value)}" ${String(saved[field.id] ?? "") === String(option.value) ? "selected" : ""}>${esc(option.label)}</option>`).join("")}</select>` : `<input id="field-${esc(field.id)}" data-field="${esc(field.id)}" type="${field.type === "number" ? "number" : "text"}" value="${esc(saved[field.id] ?? "")}" ${field.min !== undefined ? `min="${field.min}"` : ""} ${field.max !== undefined ? `max="${field.max}"` : ""} ${field.type === "number" ? 'step="1" inputmode="numeric"' : 'autocomplete="off" spellcheck="false"'} placeholder="Enter ${field.type === "number" ? "a value" : "your configuration"}">`}</div>`;
      })
      .join("");
    return `${briefing}${reference}${question.lab === "vms" ? '<div id="vm-budget" class="vm-budget" role="status" aria-live="polite"></div>' : ""}<fieldset class="lab-fields" aria-label="${esc(question.title)} configuration">${fields}</fieldset><p class="lab-note">Changes save automatically. Each correct configuration earns partial credit.</p>`;
  }
  function updateVmBudget() {
    const target = $("#vm-budget");
    if (!target) return;
    const values = answers[session.questions[index].id] || {};
    const total = (resource) =>
      ["db", "vdi", "web"].reduce(
        (sum, vm) => sum + (Number(values[`${vm}_${resource}`]) || 0),
        0,
      );
    const cpu = total("cpu");
    const ram = total("ram");
    const exceeded = cpu > 16 || ram > 64;
    target.classList.toggle("exceeded", exceeded);
    target.innerHTML = `<strong>Host allocation</strong><span>${cpu} / 16 vCPU</span><span>${ram} / 64 GiB RAM</span><p>${exceeded ? "Host capacity exceeded. Reduce the allocation to earn CPU and RAM credit." : "Within host capacity. Match each VM to its change ticket."}</p>`;
  }
  function terminal() {
    const raid = session.raid || {};
    return `<div class="terminal"><div class="terminal-header"><span class="terminal-dot"></span><span class="terminal-dot"></span><span class="terminal-dot"></span><span>RAID MAINTENANCE CONSOLE</span></div><div class="terminal-output" id="terminal-output" role="log" aria-label="RAID command history" aria-live="polite">${terminalHistory()}</div><form class="terminal-form" id="terminal-form"><label class="terminal-prompt" for="raid-command">$</label><input id="raid-command" aria-label="RAID command" autocomplete="off" spellcheck="false" placeholder="Type help to see available commands"><button type="submit">Run ↵</button></form></div><p class="terminal-note">Simulated environment · Type <code>help</code> for supported commands. Commands do not access your system.</p><div class="terminal-milestones" aria-label="Lab progress">${[
      ["diagnosed", "Diagnose"],
      ["identified", "Identify"],
      ["replaced", "Replace"],
      ["rebuilt", "Rebuild"],
    ]
      .map(
        ([key, label]) =>
          `<span class="milestone ${raid[key] ? "done" : ""}">${raid[key] ? "✓ " : ""}${label}</span>`,
      )
      .join("")}</div>`;
  }
  function terminalHistory() {
    const history = session.raid?.history || [];
    return history.length
      ? history
          .map(
            (entry) =>
              `<div class="terminal-command">${entry.command ? `$ ${esc(entry.command)}` : ""}</div><div>${esc(entry.output)}</div>`,
          )
          .join("")
      : "RAID controller ready.\nType help to explore available commands.";
  }

  function answerText(question, value) {
    if (Array.isArray(value)) {
      if (!value.length) return "<p>No answer selected.</p>";
      return `<ul>${value.map((id) => `<li>${esc(question.options?.find((option) => option.id === id)?.text || id)}</li>`).join("")}</ul>`;
    }
    if (value && typeof value === "object") {
      const entries = question.fields?.length
        ? question.fields.map((field) => [field.id, value[field.id]])
        : Object.entries(value);
      if (
        !entries.length ||
        !entries.some(
          ([, val]) => val !== "" && val !== null && val !== undefined,
        )
      )
        return "<p>No configuration entered.</p>";
      return `<ul>${entries
        .map(([key, val]) => {
          const field = question.fields?.find((item) => item.id === key);
          const label =
            field?.label || key.charAt(0).toUpperCase() + key.slice(1);
          const display =
            field?.options?.find(
              (option) => String(option.value) === String(val),
            )?.label ??
            (typeof val === "boolean"
              ? val
                ? "Completed"
                : "Not completed"
              : val);
          return `<li>${esc(label)}: ${display === "" || display === null || display === undefined ? "Not entered" : esc(display)}</li>`;
        })
        .join("")}</ul>`;
    }
    return `<p>${esc(value || "No answer entered.")}</p>`;
  }
  function results() {
    const report = session.report;
    if (!report)
      return '<div class="panel prep-panel"><h1>Your report is being prepared</h1><p>Please refresh the page to retrieve your results.</p></div>';
    const passed = report.passed;
    const portion = Math.max(0, Math.min(1, (report.score - 100) / 800));
    const circumference = 2 * Math.PI * 75;
    const review = report.review.filter(
      (item) => reviewFilter !== "practice" || !item.correct,
    );
    return `<div class="page-heading"><div><div class="eyebrow">SESSION COMPLETE · ${session?.status === "expired" ? "TIME EXPIRED" : "RESULTS & REVIEW"}</div><h1>Your practice results</h1>${session.candidate_name ? `<p class="candidate-result" dir="auto">${esc(session.candidate_name)} · ${esc(session.exam_code)}</p>` : ""}<p>${passed ? "You reached the practice threshold. Keep building on what you know." : "Every attempt points the way forward. Let’s find your next focus."}</p></div><button class="btn" data-action="new-dialog">${icon("restart", 14)} New attempt</button></div><div class="result-grid"><section class="panel score-card" aria-label="Scaled practice score"><div class="score-tag">YOUR PRACTICE SCORE</div><div class="score-ring"><svg class="score-circle" width="169" height="169" viewBox="0 0 169 169" aria-hidden="true"><circle cx="84.5" cy="84.5" r="75" fill="none" stroke="#eeebf8" stroke-width="8"/><circle cx="84.5" cy="84.5" r="75" fill="none" stroke="#7764d4" stroke-width="8" stroke-linecap="round" stroke-dasharray="${portion * circumference} ${circumference}" transform="rotate(-90 84.5 84.5)"/></svg><div class="score-ring-inner"><div class="score-number">${report.score}</div><div class="score-out-of">OUT OF 900</div></div></div><span class="result-badge ${passed ? "pass" : ""}">${passed ? "Practice threshold reached" : "Keep practicing"}</span><p>Practice pass: 675 · Score range: 100–900</p><div class="result-meta"><div><strong>${durationLabel(report.elapsed_seconds)}</strong>Time elapsed</div><div><strong>${answeredCount()} / ${session.questions.length}</strong>Answered</div><div><strong>${passed ? "Pass" : "Below threshold"}</strong>Practice outcome</div></div></section><section class="panel result-domains"><div class="card-heading"><h2>Where you stand</h2><span class="eyebrow">BY DOMAIN</span></div><div class="domain-list">${report.domains.map((domain) => `<div class="domain-row"><div class="domain-top"><span>${esc(shortDomain(domain.name))}</span><strong>${Math.round(domain.percent)}%</strong></div><progress class="domain-track" value="${Math.max(0, Math.min(100, domain.percent))}" max="100" aria-label="${esc(domain.name)} performance ${Math.round(domain.percent)} percent"></progress></div>`).join("")}</div><p>Domain performance reflects weighted scored points. Labs award partial credit. Five undisclosed pilot questions are excluded from the score.</p></section></div>${report.certificate ? `<section class="panel certificate-callout"><div><span class="eyebrow">YOUR PRACTICE MILESTONE</span><h2>Your mock certificate is ready</h2><p>Issued to <strong dir="auto">${esc(report.certificate.candidate_name)}</strong>. A practice award, not an official CompTIA qualification.</p><p>Save it before starting a new attempt. The new attempt replaces access to this report in this browser.</p></div><a class="btn primary" href="/api/exam/certificate" target="_blank" rel="noopener">View / print mock certificate</a></section>` : ""}<section class="review-section" aria-labelledby="review-title"><div class="review-header"><div><h2 id="review-title">Question review</h2><p>Open a question to see your answer and the reasoning behind it.</p></div><div class="filter-tabs" aria-label="Filter review"><button class="${reviewFilter === "all" ? "active" : ""}" data-filter="all" aria-pressed="${reviewFilter === "all"}">All questions (${report.review.length})</button><button class="${reviewFilter === "practice" ? "active" : ""}" data-filter="practice" aria-pressed="${reviewFilter === "practice"}">Needs practice (${report.review.filter((item) => !item.correct).length})</button></div></div><div class="review-list">${
      review.length
        ? review
            .map((item) => {
              const question = session.questions.find(
                (question) => question.id === item.id,
              );
              const questionIndex = session.questions.indexOf(question);
              return `<details class="review-item"><summary><span class="review-index">${String(questionIndex + 1).padStart(2, "0")}</span><span class="review-item-title">${esc(question.title)}</span><span class="review-status ${item.correct ? "correct" : item.credit > 0 ? "partial" : ""}">${item.correct ? "Correct" : item.credit > 0 ? "Partial credit" : "Needs practice"}</span><span class="review-expand">${icon("down", 13)}</span></summary><div class="review-body">${item.objective ? `<p class="objective-reference">Objective ${esc(item.objective)} · ${esc(meta.blueprint.objectives[item.objective])}</p>` : ""}<p class="review-prompt">${esc(question.prompt)}</p><div class="review-comparison"><div class="review-answer"><h3>Your answer</h3>${answerText(question, item.answer)}</div><div class="review-answer expected"><h3>Expected answer</h3>${answerText(question, item.expected)}</div></div><p class="review-explanation"><strong>The reasoning</strong><br>${esc(item.explanation)}</p>${item.sources?.length ? `<p class="review-sources">References: ${item.sources.map(id => meta.blueprint.sources.find(source => source.id === id)).filter(Boolean).map(source => `<a href="${esc(source.url)}" target="_blank" rel="noopener noreferrer">${esc(source.title)}</a>`).join(" · ")}</p>` : ""}</div></details>`;
            })
            .join("")
        : '<div class="panel empty-review">Every question earned full credit. Excellent work.</div>'
    }</div></section>${footer()}`;
  }

  function render(focus = false) {
    app.innerHTML = shell(
      view === "overview" ? overview() : view === "exam" ? exam() : results(),
      view === "overview"
        ? "Overview"
        : view === "exam"
          ? "Exam workspace"
          : "Results & review",
    );
    updateSaveStatus();
    updateVmBudget();
    updateTimer();
    if (focus) {
      const target = $("#question-title") || $("#main");
      target?.focus({ preventScroll: true });
      window.scrollTo({ top: 0, behavior: "instant" });
    }
    const output = $("#terminal-output");
    if (output) output.scrollTop = output.scrollHeight;
  }

  function updateSaveStatus() {
    const status = $("#save-status");
    if (!status) return;
    status.className = `save-status ${saveStatus}`;
    status.innerHTML = `<span class="save-dot"></span>${saveStatus === "saving" ? "Saving changes…" : saveStatus === "error" ? `Not saved. <button data-action="retry-save">Retry</button><span class="save-detail">${esc(saveError)}</span>` : "All changes saved"}`;
    status.title = saveStatus === "error" ? saveError : "";
  }
  function updateProgress() {
    const gridTarget = $("#question-grid");
    if (gridTarget) gridTarget.innerHTML = grid();
    const count = $("#answered-label");
    if (count)
      count.textContent = `${answeredCount()} / ${session.questions.length}`;
  }
  function queueSave(questionId, patch) {
    if (!session || session?.status !== "active") return;
    const previous = pending.get(questionId) || {};
    pending.set(questionId, { ...previous, ...patch, question_id: questionId });
    saveStatus = "saving";
    updateSaveStatus();
    updateProgress();
    clearTimeout(debounce);
    debounce = setTimeout(() => {
      flushSaves().catch(() => {});
    }, 400);
  }
  async function flushSaves() {
    clearTimeout(debounce);
    if (savePromise) {
      await savePromise;
      if (pending.size) return flushSaves();
      return;
    }
    if (!pending.size || session?.status !== "active") return;
    savePromise = (async () => {
      saveStatus = "saving";
      updateSaveStatus();
      while (pending.size && session?.status === "active") {
        const [questionId, patch] = pending.entries().next().value;
        pending.delete(questionId);
        try {
          adopt(await request("/api/exam", "PATCH", patch));
        } catch (error) {
          if (error.code === "exam_reset") throw error;
          pending.set(questionId, {
            ...patch,
            ...(pending.get(questionId) || {}),
          });
          saveStatus = "error";
          saveError = error.message;
          updateSaveStatus();
          throw error;
        }
      }
      saveStatus = "saved";
      saveError = "";
      updateSaveStatus();
    })();
    try {
      await savePromise;
    } finally {
      savePromise = null;
    }
  }
  function setBusy(value) {
    busy = value;
    app.setAttribute("aria-busy", String(value));
    // Disable only interactive exam fields while an ordered transition is in flight.
    app.querySelectorAll(".options, .lab-fields").forEach((fieldset) => {
      fieldset.disabled = value;
    });
    const command = $("#raid-command");
    if (command) command.disabled = value;
  }
  async function navigate(next) {
    if (!session || busy || next < 0 || next >= session.questions.length) return;
    if (pendingCommand) {
      toast(
        "Retry the unsaved RAID command before leaving this question.",
        "error",
      );
      return;
    }
    setBusy(true);
    try {
      await flushSaves();
      if (session?.status !== "active") return;
      const response = await request("/api/exam", "PATCH", {
        current_index: next,
      });
      adopt(response);
      if (session?.status === "active") {
        index = next;
        render(true);
      }
    } catch (error) {
      toast(error.message, "error");
    } finally {
      setBusy(false);
    }
  }
  async function changeView(next) {
    if (busy) return;
    if (pendingCommand) {
      toast(
        "Retry the unsaved RAID command before leaving this question.",
        "error",
      );
      return;
    }
    setBusy(true);
    try {
      if (session?.status === "active") await flushSaves();
      if (next === "exam" && session?.status !== "active") return;
      if (next === "results" && !session?.report) return;
      view = next;
      render(true);
    } catch (error) {
      toast(error.message, "error");
    } finally {
      setBusy(false);
    }
  }
  function nameField() {
    return `<div class="candidate-entry"><label for="candidate-name">Name on your mock certificate</label><input id="candidate-name" name="candidate_name" type="text" required maxlength="80" autocomplete="name" dir="auto" value="${esc(session?.candidate_name || "")}" aria-describedby="candidate-help"><p id="candidate-help">A display name is fine. It is saved with this attempt and appears on your certificate if you pass.</p></div>`;
  }
  async function start() {
    if (busy) return;
    const nameInput = (dialog.open ? dialog : app).querySelector('[name="candidate_name"]');
    if (!nameInput || !nameInput.reportValidity()) return;
    const candidateName = nameInput.value.trim();
    setBusy(true);
    const button = $('[data-action="start"]');
    if (button) {
      button.disabled = true;
      button.textContent = "Opening your exam…";
    }
    try {
      const response = await request("/api/exam", "POST", { candidate_name: candidateName });
      resetNotice = "";
      pending.clear();
      expiryRequested = false;
      pendingCommand = null;
      saveStatus = "saved";
      reviewFilter = "all";
      adopt(response, true);
      view = session?.status === "active" ? "exam" : "results";
      if (dialog.open) dialog.close();
      render(true);
    } catch (error) {
      toast(error.message, "error");
      if (button) {
        button.disabled = false;
        button.innerHTML = `Start practice exam ${icon("arrow", 16)}`;
      }
    } finally {
      setBusy(false);
    }
  }
  async function submit(expired = false) {
    if (busy && !expired) return;
    if (pendingCommand && !expired) {
      toast("Retry the unsaved RAID command before submitting.", "error");
      return;
    }
    setBusy(true);
    const button = $("#confirm-submit");
    if (button) {
      button.disabled = true;
      button.textContent = "Preparing report…";
    }
    try {
      if (expired) await flushSaves().catch(() => {});
      else await flushSaves();
      if (!session) return;
      if (session?.status === "active")
        adopt(await request("/api/exam/submit", "POST", {}), true);
      view = "results";
      if (dialog.open) dialog.close();
      render(true);
    } catch (error) {
      if (error.code === "exam_reset") return;
      const target = $("#dialog-error");
      if (target) {
        target.textContent = error.message;
        target.hidden = false;
      }
      toast(error.message, "error");
      if (button) {
        button.disabled = false;
        button.textContent = "Submit exam";
      }
      if (expired) {
        saveStatus = "error";
        saveError =
          "Time has expired. Reconnect and retry to retrieve your final report.";
        updateSaveStatus();
      }
    } finally {
      setBusy(false);
    }
  }
  function openConfirm(type) {
    if (busy) return;
    const newAttempt = type === "new";
    const unanswered = session.questions.length - answeredCount();
    $("#dialog-content").innerHTML =
      `<div class="dialog-icon">${icon(newAttempt ? "restart" : "check", 21)}</div><h2 id="dialog-title">${newAttempt ? "Start a fresh attempt?" : "Ready to finish?"}</h2><p>${newAttempt ? "A new 220-1201 session will replace access to your current attempt in this browser. Save any existing certificate before continuing." : "Your answers will be final when you submit. You can then explore your score, domain breakdown, and answer explanations."}</p>${newAttempt ? nameField() : `<div class="dialog-counts"><div><strong>${unanswered}</strong>Unanswered</div><div><strong>${flags.length}</strong>Flagged for review</div></div>${unanswered ? "<p>Unanswered questions receive no credit. Partially completed labs may still receive partial credit.</p>" : "<p>You have entered an answer for every question.</p>"}`}<p class="dialog-error" id="dialog-error" role="alert" hidden></p><div class="dialog-actions"><button class="btn" id="cancel-dialog">${newAttempt ? "Keep reviewing" : "Keep working"}</button><button class="btn primary" id="confirm-submit">${newAttempt ? "Start new attempt" : "Submit exam"}</button></div>`;
    $("#cancel-dialog").addEventListener("click", () => {
      if (!busy) dialog.close();
    });
    $("#confirm-submit").addEventListener("click", () =>
      newAttempt ? start() : submit(),
    );
    dialog.showModal();
    $("#cancel-dialog").focus();
  }
  function updateTimer() {
    if (!session || session?.status !== "active") return;
    const seconds = remaining();
    const compact = $("#compact-timer-value");
    if (compact) {
      compact.textContent = durationLabel(seconds);
      compact.classList.toggle("urgent", seconds <= 300);
    }
    const timer = $("#timer");
    if (timer) {
      timer.textContent = durationLabel(seconds);
      timer.classList.toggle("urgent", seconds <= 300);
      timer.setAttribute(
        "aria-label",
        `${Math.floor(seconds / 60)} minutes ${seconds % 60} seconds remaining`,
      );
      $("#timer-progress").value = seconds;
    }
    if (seconds === 0 && !expiryRequested) {
      expiryRequested = true;
      pendingCommand = null;
      toast("Time is up. Your saved answers are being submitted.");
      submit(true);
    }
  }

  app.addEventListener("change", (event) => {
    if (busy || !session || session?.status !== "active") return;
    if (event.target.matches('input[name="question-answer"]')) {
      const question = session.questions[index];
      const selected = Array.from(
        app.querySelectorAll('input[name="question-answer"]:checked'),
      ).map((input) => input.value);
      if (selected.length > question.select_count) {
        event.target.checked = false;
        toast(
          `Choose ${question.select_count} answers. Deselect an answer before choosing another.`,
        );
        return;
      }
      answers[question.id] = selected;
      app
        .querySelectorAll(".answer-option")
        .forEach((label) =>
          label.classList.toggle(
            "selected",
            label.querySelector("input").checked,
          ),
        );
      const count = $("#selection-count");
      if (count)
        count.textContent = `${selected.length} selected.${selected.length !== question.select_count ? ` Choose exactly ${question.select_count}.` : ""}`;
      queueSave(question.id, { answer: [...selected] });
    }
    if (event.target.matches("select[data-field]")) saveField(event.target);
  });
  app.addEventListener("input", (event) => {
    if (busy || !session || session?.status !== "active") return;
    if (event.target.matches("input[data-field]")) saveField(event.target);
  });
  function saveField(input) {
    const question = session.questions[index];
    const value =
      input.type === "number" && input.value !== ""
        ? Number(input.value)
        : input.value;
    answers[question.id] = {
      ...(answers[question.id] || {}),
      [input.dataset.field]: value,
    };
    updateVmBudget();
    queueSave(question.id, { answer: { ...answers[question.id] } });
  }
  app.addEventListener("submit", async (event) => {
    if (event.target.id !== "terminal-form") return;
    event.preventDefault();
    if (busy || session?.status !== "active") return;
    const input = $("#raid-command");
    const command = input.value.trim();
    if (!command) return;
    await sendRaidCommand(command);
  });
  async function sendRaidCommand(command) {
    pendingCommand = command;
    setBusy(true);
    saveStatus = "saving";
    updateSaveStatus();
    try {
      await flushSaves();
      if (session?.status !== "active") return;
      adopt(await request("/api/exam/command", "POST", { command }));
      pendingCommand = null;
      saveStatus = "saved";
      render();
      $("#raid-command")?.focus();
    } catch (error) {
      if (error.code === "exam_reset") return;
      saveStatus = "error";
      saveError = error.message;
      updateSaveStatus();
      toast(error.message, "error");
    } finally {
      setBusy(false);
      $("#raid-command")?.focus();
    }
  }
  app.addEventListener("click", async (event) => {
    const target = event.target.closest("button, a[data-action]");
    if (!target) return;
    if (target.matches("a")) event.preventDefault();
    if (busy) return;
    if (target.dataset.index !== undefined) {
      await navigate(Number(target.dataset.index));
      return;
    }
    if (target.dataset.filter) {
      reviewFilter = target.dataset.filter;
      const scroll = window.scrollY;
      render();
      window.scrollTo({ top: scroll, behavior: "instant" });
      $(`[data-filter="${reviewFilter}"]`)?.focus({ preventScroll: true });
      return;
    }
    switch (target.dataset.action) {
      case "overview":
        await changeView("overview");
        break;
      case "exam":
        await changeView("exam");
        break;
      case "results":
        await changeView("results");
        break;
      case "start":
        await start();
        break;
      case "previous":
        await navigate(index - 1);
        break;
      case "next":
      case "skip":
        await navigate(index + 1);
        break;
      case "flag": {
        const question = session.questions[index];
        const flagged = !flags.includes(question.id);
        flags = flagged
          ? [...flags, question.id]
          : flags.filter((id) => id !== question.id);
        target.classList.toggle("flagged", flagged);
        target.setAttribute("aria-pressed", String(flagged));
        target.querySelector("span").textContent = flagged
          ? "Flagged for review"
          : "Flag for review";
        queueSave(question.id, { flagged });
        break;
      }
      case "clear-answer": {
        const question = session.questions[index];
        answers[question.id] = question.kind === "pbq" ? {} : [];
        queueSave(question.id, { answer: answers[question.id] });
        render();
        $('[data-action="clear-answer"]')?.focus();
        break;
      }
      case "retry-save":
        if (remaining() === 0) await submit(true);
        else if (pendingCommand) await sendRaidCommand(pendingCommand);
        else {
          try {
            await flushSaves();
            if (!pending.size) {
              saveStatus = "saved";
              updateSaveStatus();
            }
          } catch (error) {
            toast(error.message, "error");
          }
        }
        break;
      case "submit-dialog":
        openConfirm("submit");
        break;
      case "new-dialog":
        openConfirm("new");
        break;
      case "reload":
        await boot();
        break;
    }
  });
  dialog.addEventListener("cancel", (event) => {
    if (busy) event.preventDefault();
  });
  window.addEventListener("beforeunload", (event) => {
    if (pending.size || savePromise || pendingCommand) {
      event.preventDefault();
      event.returnValue = "";
    }
  });
  window.addEventListener("online", () => {
    if (session?.status === "active" && pending.size)
      flushSaves().catch(() => {});
    if (session?.status === "active" && remaining() === 0) submit(true);
  });
  document.addEventListener("visibilitychange", () => {
    if (!document.hidden) {
      updateTimer();
      checkBankVersion();
    }
  });
  setInterval(updateTimer, 1000);
  setInterval(checkBankVersion, 30000);

  async function boot() {
    try {
      meta = await request("/api/meta");
      try {
        adopt(await request("/api/exam"), true);
      } catch (error) {
        if (error.status !== 404 && error.code !== "exam_reset") throw error;
        if (error.status === 404) resetAttempt("");
      }
      view = session
        ? session?.status === "active"
          ? "exam"
          : "results"
        : "overview";
      render();
    } catch (error) {
      app.innerHTML = `<main class="loading-screen" id="main"><div class="panel prep-panel"><h2>Let’s reconnect your workspace.</h2><p class="muted">${esc(error.message)}</p><br><button class="btn primary" data-action="reload">Try again ${icon("restart", 14)}</button></div></main>`;
    }
  }
  boot();
})();
