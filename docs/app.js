const translations = {
  en: {
    overallLabel: "Overall Bubble Score",
    priceLabel: "QQQ Price",
    followX: "Follow @villiva",
    conceptEyebrow: "Concept",
    conceptTitle: "Model Sources & Principle",
    warningsLabel: "Warnings",
    warningsTitle: "Active Signals",
    metricsLabel: "Signal Details",
    metricsTitle: "Indicator Details",
    sourcesLabel: "Data",
    sourcesTitle: "Data Sources & Refresh",
    methodLabel: "Method",
    methodCopy:
      "This dashboard monitors NASDAQ bubble pressure. It compresses valuation, liquidity, leverage/derivatives, breadth/concentration, and price confirmation into a 0-100 score. A high score means top fragility is rising, not that an exact top date has been predicted.",
    snapshotPrefix: "Snapshot",
    dailySnapshot: "Daily snapshot",
    loading: "Loading the latest data snapshot.",
    noWarning: "No active warning.",
    noData: "No data",
    dataLoadFailed: "Data load failed",
    metricHeaders: ["Indicator", "Value", "Score", "Source"],
    sourceFields: {
      source: "Source",
      cadence: "Cadence",
      latest: "Latest",
      note: "Note"
    },
    sourceCards: {
      qqq: {
        title: "QQQ price and price-derived signals",
        source: "Yahoo Finance chart API",
        cadence: "Daily snapshot via GitHub Actions",
        note: "Used for QQQ price, 50/200DMA distance, 3M/6M return, and drawdown."
      },
      finra: {
        title: "Margin leverage",
        source: "FINRA margin statistics",
        cadence: "Monthly source data with publication lag; checked daily by the workflow",
        note: "Authoritative aggregate margin data, but not a daily leverage feed. Use it as a slow-moving structural risk indicator."
      },
      manual: {
        title: "Configured valuation, liquidity, derivatives, and breadth inputs",
        source: "config/indicators.json",
        cadence: "Manual only; not covered by the daily refresh",
        note: "The daily workflow can refresh the page snapshot, but these inputs only change when config/indicators.json is edited."
      },
      workflow: {
        title: "Dashboard refresh",
        source: "GitHub Actions",
        cadence: "Weekdays, once per day",
        note: "The page reads docs/data/dashboard.json. It updates when the workflow commits a new snapshot."
      }
    },
    moduleLabels: {
      valuation: "Valuation",
      liquidity: "Liquidity",
      leverage_derivatives: "Leverage / Derivatives",
      breadth_concentration: "Breadth / Concentration",
      price_confirmation: "Price Confirmation"
    },
    statusMeta: {
      Green: {
        title: "Green - Normal",
        copy: "Bubble pressure has not formed a systemic high-risk combination. Keep routine monitoring."
      },
      Yellow: {
        title: "Yellow - Watch",
        copy: "The market is heating up. Track flows, breadth, and leverage more closely."
      },
      Orange: {
        title: "Orange - De-risk",
        copy: "Late-cycle bubble risk is rising. Avoid adding leverage and reduce high-beta concentration."
      },
      Red: {
        title: "Red - High Alert",
        copy: "Multiple modules are high-risk at the same time. Prioritize hedging, profit-taking, and concentration control."
      }
    },
    decisions: [
      ["Green", "Normal allocation", "Routine rebalancing and monitoring."],
      ["Yellow", "Stop chasing", "Watch flows and market breadth."],
      ["Orange", "Reduce risk", "Cut leverage and high-beta concentration."],
      ["Red", "High alert", "Hedge, take profits, and enforce stops."]
    ],
    conceptCards: [
      {
        title: "Minsky: Ponzi Finance",
        body:
          "The model borrows from Minsky's financial instability hypothesis: long expansions encourage risk-taking, financing shifts from stable cash-flow support toward speculative and Ponzi-like structures, and the system becomes more fragile."
      },
      {
        title: "Kindleberger: Bubble Stages",
        body:
          "The dashboard treats bubbles as a staged process: new narrative, boom, euphoria, funding stress, and reversal. The aim is to detect the transition from healthy momentum to late-cycle fragility."
      },
      {
        title: "LPPL / Critical Point Logic",
        body:
          "If a model claims to identify a top window, it resembles log-periodic power law thinking: prices accelerate faster than fundamentals and instability concentrates near a critical zone. This dashboard does not make exact date predictions."
      },
      {
        title: "Funding-valuation tension",
        body:
          "The operating principle is simple: when valuation expansion needs more marginal capital, but visible inflows weaken and leverage/speculation rises, the market becomes dependent on fragile buyers."
      }
    ],
    warningMap: {}
  },
  zh: {
    overallLabel: "泡沫风险总分",
    priceLabel: "QQQ 价格",
    followX: "关注 @villiva",
    conceptEyebrow: "概念",
    conceptTitle: "模型来源与原理解读",
    warningsLabel: "预警",
    warningsTitle: "当前触发信号",
    metricsLabel: "信号明细",
    metricsTitle: "指标明细",
    sourcesLabel: "数据",
    sourcesTitle: "数据来源与更新时间",
    methodLabel: "方法",
    methodCopy:
      "该面板用于监控 NASDAQ 泡沫压力。它把估值、流动性、杠杆/衍生品、市场广度/集中度和价格确认压缩成 0-100 分。高分代表顶部脆弱性上升，不代表已经预测出精确见顶日期。",
    snapshotPrefix: "快照",
    dailySnapshot: "每日数据快照",
    loading: "正在读取最新数据快照。",
    noWarning: "暂无触发信号。",
    noData: "暂无数据",
    dataLoadFailed: "数据读取失败",
    metricHeaders: ["指标", "数值", "分数", "来源"],
    sourceFields: {
      source: "来源",
      cadence: "更新频率",
      latest: "最新数据",
      note: "说明"
    },
    sourceCards: {
      qqq: {
        title: "QQQ 价格与价格派生信号",
        source: "Yahoo Finance chart API",
        cadence: "通过 GitHub Actions 每日生成快照",
        note: "用于 QQQ 价格、50/200 日均线偏离、3个月/6个月收益和回撤。"
      },
      finra: {
        title: "保证金杠杆",
        source: "FINRA margin statistics",
        cadence: "源数据为月度且有发布时间滞后；工作流每天检查是否有更新",
        note: "这是权威的总体保证金数据，但不是日频杠杆数据。它更适合作为慢变量结构性风险指标。"
      },
      manual: {
        title: "估值、流动性、衍生品和广度配置项",
        source: "config/indicators.json",
        cadence: "仅手动更新，不属于每日自动刷新范围",
        note: "每日工作流可以刷新页面快照，但这些输入只有在 config/indicators.json 被编辑后才会改变。"
      },
      workflow: {
        title: "Dashboard 刷新",
        source: "GitHub Actions",
        cadence: "工作日每天一次",
        note: "页面读取 docs/data/dashboard.json；工作流提交新快照后页面随之更新。"
      }
    },
    moduleLabels: {
      valuation: "估值压力",
      liquidity: "资金增量",
      leverage_derivatives: "杠杆/衍生品",
      breadth_concentration: "广度/集中度",
      price_confirmation: "价格确认"
    },
    statusMeta: {
      Green: {
        title: "Green - 正常",
        copy: "泡沫压力尚未形成系统性高危组合，维持常规监控。"
      },
      Yellow: {
        title: "Yellow - 观察",
        copy: "市场开始偏热，需要更密切跟踪资金流、市场广度和杠杆变化。"
      },
      Orange: {
        title: "Orange - 降风险",
        copy: "泡沫晚期概率上升，避免增加杠杆，并降低高 beta 集中暴露。"
      },
      Red: {
        title: "Red - 强警戒",
        copy: "多个模块同时高危，优先考虑对冲、止盈和降低集中仓位。"
      }
    },
    decisions: [
      ["Green", "正常配置", "常规再平衡，继续跟踪。"],
      ["Yellow", "停止追高", "观察资金流和市场广度。"],
      ["Orange", "降低风险", "减少杠杆和高 beta 集中。"],
      ["Red", "强警戒", "对冲、止盈、严格止损。"]
    ],
    conceptCards: [
      {
        title: "Minsky：庞氏融资",
        body:
          "模型借鉴 Minsky 金融不稳定假说：长期繁荣会诱导更激进的风险承担，融资结构从现金流可支撑逐步滑向投机型和庞氏型，系统脆弱性随之上升。"
      },
      {
        title: "Kindleberger：泡沫阶段",
        body:
          "面板把泡沫理解为一个阶段过程：新叙事、繁荣、狂热、资金压力和反转。目标是识别市场从健康动量进入泡沫晚期脆弱状态的转折。"
      },
      {
        title: "LPPL / 临界点逻辑",
        body:
          "如果模型声称能识别顶部窗口，它更接近 LPPL 的思想：价格上涨快于基本面，并在临界区附近集中释放不稳定性。本面板不做精确日期预测。"
      },
      {
        title: "资金与估值张力",
        body:
          "运行原理很简单：当估值扩张需要更多边际资金，而可见资金流入走弱、杠杆和投机占比上升时，市场就越来越依赖脆弱买盘。"
      }
    ],
    warningMap: {
      "NASDAQ valuation pressure is elevated.": "NASDAQ 估值压力处于偏高区域。",
      "FINRA margin leverage is in a historically high zone.": "FINRA 保证金杠杆处于历史高位区间。",
      "Breadth/concentration signals suggest narrowing leadership.": "市场广度/集中度信号显示上涨领导力正在收窄。",
      "QQQ is extended above its 200-day moving average.": "QQQ 相对 200 日均线明显偏离。",
      "Price has pulled back from highs while bubble pressure remains high.": "价格已从高位回落，但泡沫压力仍然较高。",
      "Run scripts/update_data.py to generate a fresh snapshot.": "运行 scripts/update_data.py 生成最新数据快照。"
    }
  }
};

const statusColors = {
  Green: "#26734d",
  Yellow: "#a37716",
  Orange: "#b85223",
  Red: "#b3263a"
};

let currentLanguage = localStorage.getItem("dashboardLanguage") || "zh";
let latestData = null;

function t() {
  return translations[currentLanguage] || translations.zh;
}

function fmtPct(value) {
  if (value === null || value === undefined || Number.isNaN(value)) return "--";
  return `${(value * 100).toFixed(1)}%`;
}

function fmtNum(value, digits = 1) {
  if (value === null || value === undefined || Number.isNaN(value)) return "--";
  return Number(value).toFixed(digits);
}

function fmtDateTime(value) {
  if (!value) return "--";
  return new Date(value).toLocaleString();
}

function scoreColor(score) {
  if (score >= 75) return statusColors.Red;
  if (score >= 60) return statusColors.Orange;
  if (score >= 40) return statusColors.Yellow;
  return statusColors.Green;
}

function setLanguage(lang) {
  currentLanguage = lang;
  localStorage.setItem("dashboardLanguage", lang);
  document.documentElement.lang = lang === "zh" ? "zh-CN" : "en";
  document.getElementById("lang-en").classList.toggle("active", lang === "en");
  document.getElementById("lang-zh").classList.toggle("active", lang === "zh");
  if (latestData) render(latestData);
}

function drawChart(canvas, rows) {
  const ctx = canvas.getContext("2d");
  const rect = canvas.getBoundingClientRect();
  const ratio = window.devicePixelRatio || 1;
  canvas.width = Math.max(320, rect.width) * ratio;
  canvas.height = 220 * ratio;
  ctx.scale(ratio, ratio);

  const width = canvas.width / ratio;
  const height = canvas.height / ratio;
  ctx.clearRect(0, 0, width, height);

  if (!rows || rows.length < 2) {
    ctx.fillStyle = "#66707a";
    ctx.fillText("No price history", 18, 32);
    return;
  }

  const closes = rows.map((r) => Number(r.close));
  const min = Math.min(...closes);
  const max = Math.max(...closes);
  const pad = 18;
  const xStep = (width - pad * 2) / (rows.length - 1);
  const y = (value) => height - pad - ((value - min) / (max - min || 1)) * (height - pad * 2);

  ctx.strokeStyle = "#d9ded7";
  ctx.lineWidth = 1;
  for (let i = 0; i < 4; i += 1) {
    const gy = pad + ((height - pad * 2) / 3) * i;
    ctx.beginPath();
    ctx.moveTo(pad, gy);
    ctx.lineTo(width - pad, gy);
    ctx.stroke();
  }

  ctx.strokeStyle = "#2364aa";
  ctx.lineWidth = 2;
  ctx.beginPath();
  closes.forEach((close, idx) => {
    const x = pad + xStep * idx;
    const yy = y(close);
    if (idx === 0) ctx.moveTo(x, yy);
    else ctx.lineTo(x, yy);
  });
  ctx.stroke();

  const lastY = y(closes[closes.length - 1]);
  ctx.fillStyle = "#2364aa";
  ctx.beginPath();
  ctx.arc(width - pad, lastY, 4, 0, Math.PI * 2);
  ctx.fill();

  ctx.fillStyle = "#66707a";
  ctx.font = "12px system-ui";
  ctx.fillText(`High ${max.toFixed(2)}`, pad, 14);
  ctx.fillText(`Low ${min.toFixed(2)}`, pad, height - 4);
}

async function loadDashboard() {
  const response = await fetch("./data/dashboard.json", { cache: "no-store" });
  latestData = await response.json();
  render(latestData);
}

function renderStaticText() {
  document.querySelectorAll("[data-i18n]").forEach((node) => {
    const key = node.getAttribute("data-i18n");
    node.textContent = t()[key] || node.textContent;
  });
}

function renderConcept() {
  document.getElementById("concept-grid").innerHTML = t()
    .conceptCards.map(
      (card) => `<article class="concept-card">
        <h3>${card.title}</h3>
        <p>${card.body}</p>
      </article>`
    )
    .join("");
}

function renderSources(data) {
  const cards = t().sourceCards;
  const fields = t().sourceFields;
  const sourceRows = [
    {
      ...cards.qqq,
      latest: data.price ? `${data.price.latest_date} · QQQ ${fmtNum(data.price.latest, 2)}` : "--"
    },
    {
      ...cards.finra,
      latest: data.finra ? data.finra.month : "--"
    },
    {
      ...cards.manual,
      latest: data.manual_inputs?.manual_inputs_updated_at || "Not set",
      note: `${cards.manual.note} ${currentLanguage === "zh" ? data.manual_inputs?.manual_update_path_zh || "" : data.manual_inputs?.manual_update_path || ""}`.trim()
    },
    {
      ...cards.workflow,
      latest: `${t().snapshotPrefix}: ${fmtDateTime(data.generated_at)}`
    }
  ];

  document.getElementById("source-grid").innerHTML = sourceRows
    .map(
      (row) => `<article class="source-card">
        <h3>${row.title}</h3>
        <dl>
          <div><dt>${fields.source}</dt><dd>${row.source}</dd></div>
          <div><dt>${fields.cadence}</dt><dd>${row.cadence}</dd></div>
          <div><dt>${fields.latest}</dt><dd>${row.latest}</dd></div>
          <div><dt>${fields.note}</dt><dd>${row.note}</dd></div>
        </dl>
      </article>`
    )
    .join("");
}

function localizeWarning(message) {
  return t().warningMap[message] || message;
}

function render(data) {
  renderStaticText();
  renderConcept();
  renderSources(data);

  const meta = t().statusMeta[data.status] || t().statusMeta.Yellow;
  const score = Number(data.overall_score);
  const statusColor = statusColors[data.status] || statusColors.Yellow;

  document.getElementById("overall-score").textContent = fmtNum(score, 0);
  document.getElementById("status-title").textContent = meta.title;
  document.getElementById("status-copy").textContent = meta.copy;
  document.getElementById("status-pill").textContent = data.status;
  document.getElementById("status-pill").style.borderColor = statusColor;
  document.getElementById("status-pill").style.color = statusColor;
  document.getElementById("generated-at").textContent = `${t().snapshotPrefix}: ${fmtDateTime(data.generated_at)}`;
  document.getElementById("update-frequency").textContent = t().dailySnapshot;

  const deg = Math.round(score * 3.6);
  const ring = document.getElementById("score-ring");
  ring.style.background = `conic-gradient(${scoreColor(score)} 0deg, ${scoreColor(score)} ${deg}deg, #e6e8e1 ${deg}deg)`;

  document.getElementById("price-title").textContent = `QQQ ${fmtNum(data.price.latest, 2)} · ${data.price.latest_date}`;
  document.getElementById("ret-3m").textContent = `3M ${fmtPct(data.price.return_3m)}`;
  document.getElementById("dist-200").textContent = `200DMA ${fmtPct(data.price.distance_200dma)}`;

  document.getElementById("decision-strip").innerHTML = t()
    .decisions.map(([name, title, copy]) => {
      const active = name === data.status;
      return `<div class="decision" style="${active ? `border-color:${statusColors[name]};` : ""}">
        <strong style="${active ? `color:${statusColors[name]};` : ""}">${name} · ${title}</strong>
        <span>${copy}</span>
      </div>`;
    })
    .join("");

  document.getElementById("modules").innerHTML = Object.entries(data.modules)
    .map(([key, value]) => {
      const color = scoreColor(value);
      return `<article class="module">
        <p class="label">${t().moduleLabels[key] || key}</p>
        <div class="module-value" style="color:${color}">${fmtNum(value, 0)}</div>
        <div class="bar"><span style="width:${value}%; background:${color}"></span></div>
      </article>`;
    })
    .join("");

  const warnings = data.warnings && data.warnings.length ? data.warnings : [t().noWarning];
  document.getElementById("warnings-list").innerHTML = warnings.map((w) => `<li>${localizeWarning(w)}</li>`).join("");

  const groups = Object.entries(data.metrics || {});
  const [indicatorHeader, valueHeader, scoreHeader, sourceHeader] = t().metricHeaders;
  document.getElementById("metric-table").innerHTML = groups
    .map(([group, rows]) => {
      const body = (rows || [])
        .map(
          (m) => `<div class="metric-row">
          <span>${m.name}</span>
          <span>${m.value === null ? "--" : fmtNum(m.value, 2)}</span>
          <span>${m.score === null ? "--" : fmtNum(m.score, 0)}</span>
          <span>${m.source}</span>
        </div>`
        )
        .join("");
      return `<div class="metric-group">
        <p class="label">${group}</p>
        <div class="metric-row"><span>${indicatorHeader}</span><span>${valueHeader}</span><span>${scoreHeader}</span><span>${sourceHeader}</span></div>
        ${body || `<div class="metric-row"><span>${t().noData}</span><span>--</span><span>--</span><span>--</span></div>`}
      </div>`;
    })
    .join("");

  drawChart(document.getElementById("price-chart"), data.history);
}

document.getElementById("lang-en").addEventListener("click", () => setLanguage("en"));
document.getElementById("lang-zh").addEventListener("click", () => setLanguage("zh"));
window.addEventListener("resize", () => latestData && drawChart(document.getElementById("price-chart"), latestData.history));

setLanguage(currentLanguage);
loadDashboard().catch((error) => {
  document.getElementById("status-title").textContent = t().dataLoadFailed;
  document.getElementById("status-copy").textContent = error.message;
});
