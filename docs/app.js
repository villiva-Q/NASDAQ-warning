const i18n = {
  en: {
    followX: "Follow @villiva",
    navOverview: "Verdict",
    navTopRisk: "Top risk",
    navBottom: "Bottom model",
    navEvidence: "Evidence",
    navMethod: "Method",
    heroEyebrow: "Market regime · Risk management · Public data",
    heroTitle: "Know which phase the bubble is in, instead of guessing the exact top.",
    heroLead:
      "A traceable two-layer framework separates a high-valuation melt-up from weakening marginal liquidity, then tests whether forced liquidation is cooling after a real drawdown.",
    readingLabel: "How to read",
    readingOneTitle: "Start with the regime",
    readingOneCopy: "Bubble risk and bottom readiness answer two different questions.",
    readingTwoTitle: "Track marginal change",
    readingTwoCopy: "Look for alignment across price, leverage, CapEx, and liquidity.",
    readingThreeTitle: "Audit the evidence",
    readingThreeCopy: "Freshness, confidence, and calibration constrain every signal.",
    liveSnapshot: "Latest snapshot",
    drawdownOnly: "Active only after a real drawdown",
    briefingLabel: "Research brief",
    drawdownLabel: "From 52W high",
    confidenceLabel: "Data confidence",
    marketContextLabel: "Market context",
    marketContextTitle: "Price is strong. The risk is in the structure.",
    marketContextCopy:
      "Split the headline score into four explainable drivers so one bright number cannot hide what is actually moving the model.",
    lateCycleTitle: "The AI melt-up can continue, while its failure signal lives at the margin.",
    lateCycleCopy:
      "CapEx momentum, liquidity drain, and options-driven buying explain both why a bubble can extend and when that extension becomes fragile.",
    thesisOne: "CapEx second derivative",
    thesisOneCopy: "Not just how high spending is, but whether its growth rate is slowing.",
    thesisTwo: "Liquidity drain",
    thesisTwoCopy: "Reserves, TGA, SOFR/RRP, and SRF constrain how long the melt-up can run.",
    thesisThree: "Mechanical bid",
    thesisThreeCopy: "Passive flows and dealer gamma can make rising prices generate more buying.",
    viewTopEvidence: "View the three top-risk evidence groups",
    viewMicronEvidence: "View Micron component evidence",
    bottomSectionTitle: "A bottom is not cheapness. It is forced selling beginning to stop.",
    bottomSectionCopy:
      "This layer matters only after a real QQQ drawdown. It tests whether volatility, rates, risk appetite, leverage, breadth, and price are stabilizing together.",
    viewCalibration: "View threshold backtest",
    evidenceLabel: "Evidence reliability",
    evidenceTitle: "A signal cannot be more reliable than its data.",
    evidenceCopy:
      "Every metric carries a refresh cadence, as-of date, freshness, confidence, and score-usage tag, with official data, public proxies, and manual inputs kept distinct.",
    viewQualityDetails: "View data quality by model section",
    indicatorDetailsTitle: "Complete indicator ledger",
    viewAllMetrics: "Open the full indicator table",
    frameworkSectionTitle: "Turn a market narrative into a falsifiable monitoring system.",
    frameworkSectionCopy:
      "The model is not built to call one perfect top or bottom. It binds market regimes to repeatable risk-management actions.",
    footerCopy: "A public-data project for market regimes, risk management, and research discipline.",
    footerDisclaimer: "For research and risk monitoring only. Not investment advice.",
    dailySnapshot: "Daily snapshot",
    bubbleLabel: "Bubble Risk",
    bottomLabel: "Bottom Readiness",
    priceLabel: "QQQ Price",
    warningsLabel: "Warnings",
    warningsTitle: "Active Signals",
    coreMetricsLabel: "Bubble Core Inputs",
    contextMetricsLabel: "Bubble Context Signals",
    dataQualityLabel: "Data Quality",
    dataQualityTitle: "Freshness & Confidence",
    topFragilityLabel: "Top Fragility",
    topFragilityTitle: "AI Melt-Up Overlay",
    micronLabel: "Micron Canary",
    bottomSignalsLabel: "Bottom Model",
    bottomSignalsTitle: "Liquidation-End Signals",
    calibrationLabel: "Calibration",
    calibrationTitle: "Backtest Thresholds",
    conceptEyebrow: "Framework",
    conceptTitle: "How The Two-Layer Model Works",
    sourcesLabel: "Data",
    sourcesTitle: "Data Sources & Refresh",
    methodLabel: "Method",
    noWarning: "No active warning.",
    loading: "Loading the latest data snapshot.",
    dataLoadFailed: "Data load failed",
    snapshotPrefix: "Snapshot",
    metricHeaders: ["Indicator", "Value", "Score", "Refresh", "Last Updated", "Freshness", "Confidence", "Used"],
    bottomHeaders: ["Signal", "Observed Value", "Score", "Source"],
    thresholdHeaders: ["Threshold", "Events", "Avg Days From Low", "21D Avg", "21D Hit", "63D Avg", "63D Hit"],
    moduleLabels: {
      price_confirmation: "Price Confirmation",
      finra_margin_slow: "FINRA Margin Slow",
      daily_leverage_proxy: "Daily Leverage Proxy",
      ai_fragility_overlay: "AI Fragility Overlay"
    },
    statusMeta: {
      Green: ["Green - Normal", "Bubble pressure is not yet a systemic high-risk combination."],
      Yellow: ["Yellow - Watch", "The market is heating up. Track flows, breadth, and leverage more closely."],
      Orange: ["Orange - De-risk", "Late-cycle bubble risk is rising. Avoid adding leverage and reduce high-beta concentration."],
      Red: ["Red - High Alert", "Multiple modules are high risk together. Prioritize hedging, profit-taking, and concentration control."]
    },
    bottomStatus: {
      "No setup": ["No Setup", "QQQ has not pulled back enough for a bottom-readiness signal to matter."],
      Wait: ["Wait", "The drawdown has started, but liquidation-end evidence is still weak."],
      Watch: ["Watch", "Some stabilization is appearing. Treat this as a watch zone, not confirmation."],
      "Entry zone": ["Entry Zone", "The calibrated score is in the staged-entry zone after a meaningful drawdown."],
      Confirmed: ["Confirmed", "Most public proxies suggest forced selling has probably cooled."]
    },
    decisions: [
      ["Green", "Normal allocation", "Routine rebalancing and monitoring."],
      ["Yellow", "Stop chasing", "Watch flows and market breadth."],
      ["Orange", "Reduce risk", "Cut leverage and high-beta concentration."],
      ["Red", "High alert", "Hedge, take profits, and enforce stops."]
    ],
    bottomDecisions: [
      ["0-7", "Wait", "Liquidation risk is usually unresolved."],
      ["8-11", "Observe", "Only small test positions, if any."],
      ["12-13", "Watch", "Bottom process may be forming."],
      ["13+", "Staged entry", "Use only with drawdown and price confirmation."]
    ],
    conceptCards: [
      {
        title: "Top Risk Layer",
        body: "The bubble score monitors late-cycle fragility: price extension, FINRA margin leverage, and QQQ/TQQQ leveraged trading activity. A high score warns that the market depends on fragile marginal buyers."
      },
      {
        title: "Bottom Readiness Layer",
        body: "The bottom score is only meaningful after a real QQQ drawdown. It rises when volatility normalizes, rates stop worsening, crypto risk appetite stabilizes, leverage cools, breadth repairs, and price stops falling."
      },
      {
        title: "No Paid Microstructure Data",
        body: "Dealer gamma, put walls, and CTA flow are not directly available for free. The dashboard uses public proxies: VIX/VIX3M, VXN/VIX changes, TQQQ/QQQ volume, QQQ trend, QQEW/QQQ breadth, BTC, and FINRA margin debt."
      },
      {
        title: "Calibration Discipline",
        body: "The bottom framework is backtested on QQQ drawdown events. FINRA data is lagged by 21 days to avoid look-ahead bias, and missing free signals are excluded from the score denominator instead of being treated as bearish."
      },
      {
        title: "Micron Canary",
        body: "Micron is treated as an AI-memory canary. A low static P/E is not automatically safe when gross margin, EPS, and customer lock-in are extreme; the dashboard watches for peak-earnings risk."
      }
    ],
    briefingStatus: {
      Green: ["Risk remains contained.", "Keep routine exposure and monitor whether leverage or liquidity begins to deteriorate."],
      Yellow: ["The market is heating up.", "Avoid chasing. Watch whether price strength becomes increasingly dependent on leverage and narrow leadership."],
      Orange: ["Stay involved, but reduce fragile exposure.", "Late-cycle risk is elevated. Avoid adding leverage and prioritize concentration control over calling an exact top."],
      Red: ["Capital preservation takes priority.", "Several fragility layers are aligned. Hedging, profit-taking, and strict exposure limits deserve priority."]
    },
    methodCopy:
      "This dashboard is a risk and timing aid, not investment advice. Use the bubble score to identify top fragility and the bottom-readiness score to judge whether a selloff is moving from forced liquidation toward stabilization."
  },
  zh: {
    followX: "关注 @villiva",
    navOverview: "结论",
    navTopRisk: "顶部风险",
    navBottom: "底部框架",
    navEvidence: "证据",
    navMethod: "方法",
    heroEyebrow: "市场状态·风险管理·公开数据",
    heroTitle: "看清泡沫处于哪一段，而不是猜某一天见顶。",
    heroLead:
      "用一套可追溯的双层框架，区分“高估值但仍在融涨”与“边际流动性转弱”，并在真实回撤后判断强制清算是否降温。",
    readingLabel: "阅读方式",
    readingOneTitle: "先看状态",
    readingOneCopy: "泡沫风险与底部就绪是两个不同问题。",
    readingTwoTitle: "再看边际变化",
    readingTwoCopy: "价格、杠杆、CapEx 与流动性是否共振。",
    readingThreeTitle: "最后查证据",
    readingThreeCopy: "新鲜度、置信度和回测约束决定信号强度。",
    liveSnapshot: "最新快照",
    drawdownOnly: "仅在有效回撤后启用",
    briefingLabel: "当日研究摘要",
    drawdownLabel: "距 52 周高点",
    confidenceLabel: "数据置信度",
    marketContextLabel: "市场上下文",
    marketContextTitle: "价格很强，但风险来自结构。",
    marketContextCopy: "把总分拆成四个可解释的来源，避免一个鲜艳的数字掩盖真正驱动因素。",
    lateCycleTitle: "AI 融涨还能继续，死亡信号却看边际。",
    lateCycleCopy: "CapEx 绝对值、流动性抽水和期权机械买盘，共同解释泡沫为什么能延长，以及它会在什么条件下变得脆弱。",
    thesisOne: "CapEx 二阶导",
    thesisOneCopy: "不只看支出高不高，更看增速是否放缓。",
    thesisTwo: "流动性抽水",
    thesisTwoCopy: "准备金、TGA、SOFR/RRP 与 SRF 是融涨的底层约束。",
    thesisThree: "机械买盘",
    thesisThreeCopy: "被动资金与 dealer gamma 让上涨本身产生新买盘。",
    viewTopEvidence: "查看三组顶部证据",
    viewMicronEvidence: "查看美光分项证据",
    bottomSectionTitle: "底部不是便宜，而是强制卖出开始停止。",
    bottomSectionCopy: "这一层只在 QQQ 真实回撤后才有意义：检查波动率、利率、风险偏好、杠杆、广度和价格是否一起企稳。",
    viewCalibration: "查看阈值回测",
    evidenceLabel: "证据可靠性",
    evidenceTitle: "一个信号，不能比它的数据更可靠。",
    evidenceCopy: "每个指标都带刷新频率、截止日期、新鲜度、置信度和是否入分，并明确区分官方数据、公开代理与手动输入。",
    viewQualityDetails: "查看分区数据质量",
    indicatorDetailsTitle: "全部指标明细",
    viewAllMetrics: "展开完整指标表",
    frameworkSectionTitle: "把市场叙事，变成可反驳的监测系统。",
    frameworkSectionCopy: "模型不追求一次性猜对顶底，而是把不同市场状态与对应的风险管理动作绑定。",
    footerCopy: "一个面向市场状态、风险管理与研究纪律的公开数据项目。",
    footerDisclaimer: "仅作研究与风险监测，不构成投资建议。",
    dailySnapshot: "每日快照",
    bubbleLabel: "泡沫风险",
    bottomLabel: "底部就绪度",
    priceLabel: "QQQ 价格",
    warningsLabel: "预警",
    warningsTitle: "当前触发信号",
    coreMetricsLabel: "泡沫核心指标",
    contextMetricsLabel: "泡沫背景信号",
    dataQualityLabel: "数据质量",
    dataQualityTitle: "新鲜度与置信度",
    topFragilityLabel: "顶部脆弱性",
    topFragilityTitle: "AI 融涨覆盖层",
    micronLabel: "美光金丝雀",
    bottomSignalsLabel: "底部模型",
    bottomSignalsTitle: "清算结束信号",
    calibrationLabel: "校准",
    calibrationTitle: "回测阈值",
    conceptEyebrow: "框架",
    conceptTitle: "双层模型如何工作",
    sourcesLabel: "数据",
    sourcesTitle: "数据来源与刷新",
    methodLabel: "方法",
    noWarning: "暂无触发信号。",
    loading: "正在读取最新数据快照。",
    dataLoadFailed: "数据读取失败",
    snapshotPrefix: "快照",
    metricHeaders: ["指标", "数值", "分数", "刷新", "更新时间", "新鲜度", "置信度", "入分"],
    bottomHeaders: ["信号", "观测值", "分数", "来源"],
    thresholdHeaders: ["阈值", "触发事件", "距离低点均值", "21日均值", "21日胜率", "63日均值", "63日胜率"],
    moduleLabels: {
      price_confirmation: "价格确认",
      finra_margin_slow: "FINRA 慢变量",
      daily_leverage_proxy: "日频杠杆代理",
      ai_fragility_overlay: "AI 脆弱覆盖层"
    },
    statusMeta: {
      Green: ["Green - 正常", "泡沫压力尚未形成系统性高风险组合。"],
      Yellow: ["Yellow - 观察", "市场开始升温，需要更密切跟踪资金流、广度和杠杆。"],
      Orange: ["Orange - 降风险", "泡沫晚期脆弱性上升，避免增加杠杆，降低高 beta 集中暴露。"],
      Red: ["Red - 强警戒", "多个模块同时高危，优先考虑对冲、止盈和控制集中仓位。"]
    },
    bottomStatus: {
      "No setup": ["无底部设置", "QQQ 回撤还不够，底部就绪信号暂时意义不大。"],
      Wait: ["等待", "回撤已经开始，但清算结束证据仍然很弱。"],
      Watch: ["观察", "部分稳定信号开始出现，但还不是确认。"],
      "Entry zone": ["分批区", "有意义回撤后，分数进入校准后的分批入场区。"],
      Confirmed: ["确认", "多数公开代理显示强制卖出大概率已经降温。"]
    },
    decisions: [
      ["Green", "正常配置", "常规再平衡，继续跟踪。"],
      ["Yellow", "停止追高", "观察资金流和市场广度。"],
      ["Orange", "降低风险", "减少杠杆和高 beta 集中。"],
      ["Red", "强警戒", "对冲、止盈、严格止损。"]
    ],
    bottomDecisions: [
      ["0-7", "等待", "清算风险通常尚未解除。"],
      ["8-11", "观察", "最多小仓试探。"],
      ["12-13", "关注", "底部过程可能正在形成。"],
      ["13+", "分批", "必须结合回撤和价格确认使用。"]
    ],
    conceptCards: [
      {
        title: "顶部风险层",
        body: "泡沫分数监控晚周期脆弱性：价格延伸、FINRA 保证金杠杆、QQQ/TQQQ 杠杆交易活跃度。高分代表市场越来越依赖脆弱的边际买盘。"
      },
      {
        title: "底部就绪层",
        body: "底部评分只在 QQQ 出现真实回撤后才有意义。波动率正常化、利率压力停止恶化、加密风险偏好企稳、杠杆降温、广度修复、价格止跌时，分数会上升。"
      },
      {
        title: "不使用付费微观结构数据",
        body: "Dealer gamma、put wall、CTA flow 没有稳定免费源。面板用公开代理替代：VIX/VIX3M、VXN/VIX、TQQQ/QQQ 成交量、QQQ 趋势、QQEW/QQQ 广度、BTC 和 FINRA 保证金。"
      },
      {
        title: "校准纪律",
        body: "底部框架基于 QQQ 回撤事件回测。FINRA 月度数据滞后 21 天对齐，避免未来函数；免费源缺失的指标会从分母剔除，不会被当成看空信号。"
      },
      {
        title: "美光金丝雀",
        body: "美光被视作 AI 存储链条的金丝雀。低静态 P/E 不必然安全；当毛利率、EPS 和客户锁单强度都极端时，面板会把它识别为峰值利润陷阱风险。"
      }
    ],
    briefingStatus: {
      Green: ["风险仍处于可控区间。", "保持常规暴露，继续监测杠杆或流动性是否开始恶化。"],
      Yellow: ["市场正在升温。", "不追高，关注价格强势是否越来越依赖杠杆与狭窄龙头。"],
      Orange: ["保持参与，但先降低脆弱暴露。", "晚周期风险已抬升。避免新增杠杆，优先控制集中度，而不是试图猜中精确顶部。"],
      Red: ["资本保全优先。", "多个脆弱性层已共振，对冲、止盈和严格暴露上限应成为优先事项。"]
    },
    methodCopy:
      "这个 dashboard 是风险和择时辅助工具，不是投资建议。泡沫分数用于识别顶部脆弱性，底部就绪分用于判断一次下跌是否正在从强制清算转向稳定。"
  }
};

const statusColors = {
  Green: "#26734d",
  Yellow: "#a37716",
  Orange: "#b85223",
  Red: "#b3263a",
  Wait: "#b3263a",
  Watch: "#a37716",
  "Entry zone": "#2364aa",
  Confirmed: "#26734d",
  "No setup": "#66707a",
  Normal: "#26734d",
  Hot: "#b85223",
  Fragile: "#b3263a"
};

let currentLanguage = localStorage.getItem("dashboardLanguage") || "zh";
let latestData = null;

function tr() {
  return i18n[currentLanguage] || i18n.zh;
}

function fmtPct(value) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return "--";
  return `${(Number(value) * 100).toFixed(1)}%`;
}

function fmtNum(value, digits = 1) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return "--";
  return Number(value).toFixed(digits);
}

function fmtValue(value) {
  if (value === null || value === undefined || value === "") return "--";
  if (typeof value === "number") {
    if (Number.isNaN(value)) return "--";
    if (Math.abs(value) >= 1000000) return value.toLocaleString(undefined, { maximumFractionDigits: 0 });
    if (Math.abs(value) < 1) return fmtNum(value, 3);
    return fmtNum(value, Math.abs(value) < 10 ? 2 : 1);
  }
  return String(value);
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

function setZenMode(enabled) {
  const button = document.getElementById("view-mode-toggle");
  document.documentElement.classList.toggle("zen-mode", enabled);
  button.textContent = enabled ? "V mode" : "禅 mode";
  button.setAttribute("aria-pressed", String(enabled));
  button.setAttribute("aria-label", enabled ? "恢复 V mode 旧数字排版" : "切换到禅 mode 数字居中排版");
}

function setRing(id, score, maxScore, color) {
  const ring = document.getElementById(id);
  const deg = Math.round((score / maxScore) * 360);
  ring.style.background = `conic-gradient(${color} 0deg, ${color} ${deg}deg, #e6e8e1 ${deg}deg)`;
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
  if (!rows || rows.length < 2) return;

  const closes = rows.map((r) => Number(r.close));
  const min = Math.min(...closes);
  const max = Math.max(...closes);
  const pad = 24;
  const y = (value) => height - pad - ((value - min) / (max - min || 1)) * (height - pad * 2);
  const xStep = (width - pad * 2) / (rows.length - 1);

  ctx.strokeStyle = "#deddd7";
  ctx.lineWidth = 1;
  for (let i = 0; i < 4; i += 1) {
    const gy = pad + ((height - pad * 2) / 3) * i;
    ctx.beginPath();
    ctx.moveTo(pad, gy);
    ctx.lineTo(width - pad, gy);
    ctx.stroke();
  }

  const area = ctx.createLinearGradient(0, pad, 0, height - pad);
  area.addColorStop(0, "rgba(45, 101, 166, 0.22)");
  area.addColorStop(1, "rgba(45, 101, 166, 0)");

  ctx.beginPath();
  closes.forEach((close, idx) => {
    const x = pad + xStep * idx;
    const yy = y(close);
    if (idx === 0) ctx.moveTo(x, yy);
    else ctx.lineTo(x, yy);
  });
  ctx.lineTo(width - pad, height - pad);
  ctx.lineTo(pad, height - pad);
  ctx.closePath();
  ctx.fillStyle = area;
  ctx.fill();

  ctx.strokeStyle = "#2d65a6";
  ctx.lineWidth = 2.25;
  ctx.beginPath();
  closes.forEach((close, idx) => {
    const x = pad + xStep * idx;
    const yy = y(close);
    if (idx === 0) ctx.moveTo(x, yy);
    else ctx.lineTo(x, yy);
  });
  ctx.stroke();

  const lastX = width - pad;
  const lastY = y(closes[closes.length - 1]);
  ctx.fillStyle = "#ffffff";
  ctx.beginPath();
  ctx.arc(lastX, lastY, 5, 0, Math.PI * 2);
  ctx.fill();
  ctx.strokeStyle = "#2d65a6";
  ctx.lineWidth = 2.5;
  ctx.stroke();

  ctx.fillStyle = "#69717b";
  ctx.font = "12px system-ui";
  ctx.fillText(`High ${max.toFixed(2)}`, pad, 14);
  ctx.fillText(`Low ${min.toFixed(2)}`, pad, height - 4);
}

function renderStaticText() {
  document.querySelectorAll("[data-i18n]").forEach((node) => {
    const key = node.getAttribute("data-i18n");
    node.textContent = tr()[key] || node.textContent;
  });
}

function renderDecisionStrip(id, rows, activeLabel) {
  document.getElementById(id).innerHTML = rows
    .map(([name, title, copy]) => {
      const active = name === activeLabel || (activeLabel === "Entry zone" && name === "13+");
      return `<div class="decision ${active ? "active" : ""}">
        <strong>${name} · ${title}</strong>
        <span>${copy}</span>
      </div>`;
    })
    .join("");
}

function renderModules(data) {
  document.getElementById("modules").innerHTML = Object.entries(data.modules)
    .map(([key, value]) => {
      const color = scoreColor(value);
      return `<article class="module">
        <p class="label">${tr().moduleLabels[key] || key}</p>
        <div class="module-value" style="color:${color}">${fmtNum(value, 0)}</div>
        <div class="bar"><span style="width:${value}%; background:${color}"></span></div>
      </article>`;
    })
    .join("");
}

function freshnessLabel(value) {
  const labels =
    currentLanguage === "zh"
      ? { fresh: "新鲜", aging: "临近过期", stale: "过期", unknown: "未知" }
      : { fresh: "Fresh", aging: "Aging", stale: "Stale", unknown: "Unknown" };
  return labels[value] || labels.unknown;
}

function confidenceLabel(value) {
  const labels =
    currentLanguage === "zh"
      ? { high: "高", medium: "中", low: "低" }
      : { high: "High", medium: "Medium", low: "Low" };
  return labels[value] || "--";
}

function usedLabel(value) {
  return currentLanguage === "zh" ? (value ? "是" : "否") : value ? "Yes" : "No";
}

function localizedWarning(value) {
  if (currentLanguage !== "zh") return value;
  const warnings = {
    "FINRA margin leverage is in a historically high zone.": "FINRA 保证金杠杆已处于历史高位区间。",
    "Micron profits look extreme enough that low P/E may be a peak-earnings trap.": "美光利润已极端到足以让低 P/E 变成峰值利润陷阱。",
    "Manual supply-chain inputs imply high demand lock-in and customer urgency.": "手动供应链输入显示需求锁定度与客户紧迫性偏高。",
    "MU has started to draw down materially from its 52-week high.": "MU 已开始较明显地脱离 52 周高点。"
  };
  return warnings[value] || value;
}

function renderMetricGroups(title, groups) {
  const headers = tr().metricHeaders;
  const entries = Object.entries(groups || {});
  if (!entries.length) return "";
  return `<div class="metric-section">
    <p class="label">${title}</p>
    ${entries
      .map(([group, rows]) => {
        const body = (rows || [])
          .map(
            (m) => `<div class="metric-row metric-row-wide">
              <span>${m.name}</span><span>${fmtValue(m.value)}</span><span>${fmtNum(m.score, 0)}</span>
              <span>${m.refresh || "manual"}</span><span>${m.as_of || "--"}</span>
              <span class="freshness ${m.freshness || "unknown"}">${freshnessLabel(m.freshness)}</span>
              <span class="confidence ${m.confidence || "low"}">${confidenceLabel(m.confidence)}<small>${fmtNum(m.confidence_score, 0)}</small></span>
              <span>${usedLabel(Boolean(m.used_in_score))}</span>
            </div>`
          )
          .join("");
        return `<div class="metric-group">
          <p class="label">${group}</p>
          <div class="metric-row metric-row-wide">${headers.map((h) => `<span>${h}</span>`).join("")}</div>
          ${body}
        </div>`;
      })
      .join("")}
  </div>`;
}

function renderDataQuality(data) {
  const quality = data.data_quality;
  if (!quality) return;
  const summary = quality.summary || {};
  const issueCount = (quality.issues?.stale_or_unknown_used || []).length + (quality.issues?.low_confidence_used || []).length;
  const cards =
    currentLanguage === "zh"
      ? [
          ["自动覆盖率", `${fmtNum(summary.auto_coverage_pct, 1)}%`, `${summary.auto_metrics || 0}/${summary.total_metrics || 0} 个指标自动刷新`],
          ["新鲜度", fmtNum(summary.freshness_score, 0), `新鲜 ${summary.fresh || 0} · 临近 ${summary.aging || 0} · 过期 ${summary.stale || 0}`],
          ["置信度", fmtNum(summary.confidence_score, 0), "官方源最高，Cboe/Yahoo 为代理源"],
          ["待关注", String(issueCount), "过期、未知或低置信入分项"]
        ]
      : [
          ["Auto Coverage", `${fmtNum(summary.auto_coverage_pct, 1)}%`, `${summary.auto_metrics || 0}/${summary.total_metrics || 0} metrics update automatically`],
          ["Freshness", fmtNum(summary.freshness_score, 0), `Fresh ${summary.fresh || 0} · Aging ${summary.aging || 0} · Stale ${summary.stale || 0}`],
          ["Confidence", fmtNum(summary.confidence_score, 0), "Official sources score highest; Cboe/Yahoo are proxies"],
          ["Needs Review", String(issueCount), "Stale, unknown, or low-confidence scored inputs"]
        ];

  document.getElementById("data-quality-summary").innerHTML = cards
    .map(
      ([title, value, copy]) => `<article class="quality-card">
        <p class="label">${title}</p>
        <strong>${value}</strong>
        <span>${copy}</span>
      </article>`
    )
    .join("");

  const rows = quality.section_breakdown || [];
  document.getElementById("data-quality-table").innerHTML = `
    <div class="metric-row quality-row">
      <span>${currentLanguage === "zh" ? "区块" : "Section"}</span>
      <span>${currentLanguage === "zh" ? "自动/总数" : "Auto/Total"}</span>
      <span>${currentLanguage === "zh" ? "新鲜" : "Fresh"}</span>
      <span>${currentLanguage === "zh" ? "临近" : "Aging"}</span>
      <span>${currentLanguage === "zh" ? "过期/未知" : "Stale/Unknown"}</span>
      <span>${currentLanguage === "zh" ? "置信度" : "Confidence"}</span>
    </div>
    ${rows
      .map(
        (row) => `<div class="metric-row quality-row">
          <span>${row.section}</span>
          <span>${row.auto}/${row.total}</span>
          <span>${row.fresh}</span>
          <span>${row.aging}</span>
          <span>${(row.stale || 0) + (row.unknown || 0)}</span>
          <span>${fmtNum(row.confidence_score, 0)}</span>
        </div>`
      )
      .join("")}`;
}

function renderTopFragility(data) {
  const overlay = data.top_fragility_overlay;
  if (!overlay) return;
  const headers =
    currentLanguage === "zh"
      ? ["分组", "信号", "数值", "得分", "来源", "新鲜度", "置信度"]
      : ["Group", "Signal", "Value", "Score", "Source", "Freshness", "Confidence"];
  document.getElementById("top-fragility-copy").textContent =
    currentLanguage === "zh"
      ? "真正的顶部脆弱性不只是估值高，而是 AI CapEx 增速放缓、流动性抽水和机械买盘拥挤逐步共振。"
      : overlay.principle?.summary || "";
  const rows = Object.entries(overlay.groups || {}).flatMap(([group, payload]) =>
    (payload.metrics || []).map((m) => ({ group, groupScore: payload.score, ...m }))
  );
  document.getElementById("top-fragility-table").innerHTML = `
    <div class="metric-row fragility-row">
      ${headers.map((header) => `<span>${header}</span>`).join("")}
    </div>
    ${rows
      .map(
        (m) => `<div class="metric-row fragility-row">
          <span><strong>${m.group}</strong><small>${fmtNum(m.groupScore, 0)}</small></span>
          <span>${m.name}<small>${m.note || ""}</small></span>
          <span>${fmtValue(m.value)}</span>
          <span>${fmtNum(m.score, 0)}</span>
          <span>${m.source || "--"}<small>${m.as_of || "--"}</small></span>
          <span class="freshness ${m.freshness || "unknown"}">${freshnessLabel(m.freshness)}</span>
          <span class="confidence ${m.confidence || "low"}">${confidenceLabel(m.confidence)}<small>${fmtNum(m.confidence_score, 0)}</small></span>
        </div>`
      )
      .join("")}`;
}

function renderMicronCanary(data) {
  const micron = data.micron_canary;
  if (!micron) return;
  if (micron.available === false) {
    document.getElementById("micron-title").textContent = "MU --";
    document.getElementById("micron-copy").textContent = micron.error || "--";
    return;
  }

  const score = Number(micron.score);
  const color = scoreColor(score);
  document.getElementById("micron-score").textContent = fmtNum(score, 0);
  document.getElementById("micron-title").textContent = `MU ${micron.status} · ${fmtNum(micron.price.latest, 2)} · ${micron.as_of}`;
  document.getElementById("micron-copy").textContent =
    currentLanguage === "zh"
      ? "美光被视为 AI 存储链的金丝雀：当毛利率、EPS 和需求锁定度都趋于极端时，低静态 P/E 不代表安全。"
      : micron.principle?.summary || "";
  document.getElementById("micron-pe").textContent = `P/E ${fmtNum(micron.fundamentals.trailing_pe, 1)}`;
  document.getElementById("micron-margin").textContent = `GM ${fmtPct(micron.fundamentals.latest_gross_margin)}`;
  document.getElementById("micron-eps").textContent = `EPS ${fmtNum(micron.fundamentals.ttm_diluted_eps, 1)}`;
  setRing("micron-ring", score, 100, color);

  document.getElementById("micron-group-grid").innerHTML = Object.entries(micron.groups || {})
    .map(([name, group]) => {
      const groupColor = scoreColor(Number(group.score));
      return `<article class="canary-group">
        <p class="label">${name}</p>
        <strong style="color:${groupColor}">${fmtNum(group.score, 0)}</strong>
        <div class="bar"><span style="width:${group.score}%; background:${groupColor}"></span></div>
      </article>`;
    })
    .join("");

  const rows = Object.entries(micron.groups || {}).flatMap(([group, payload]) =>
    (payload.metrics || []).map((m) => ({ group, ...m }))
  );
  const headers = currentLanguage === "zh" ? ["分组", "信号", "数值", "得分", "来源"] : ["Group", "Signal", "Value", "Score", "Source"];
  document.getElementById("micron-table").innerHTML = `
    <div class="metric-row micron-row">
      ${headers.map((header) => `<span>${header}</span>`).join("")}
    </div>
    ${rows
      .map(
        (m) => `<div class="metric-row micron-row">
          <span>${m.group}</span>
          <span>${m.name}<small>${m.note || ""}</small></span>
          <span>${fmtValue(m.value)}</span>
          <span>${fmtNum(m.score, 0)}</span>
          <span>${m.source || "--"}</span>
        </div>`
      )
      .join("")}`;
}

function renderBottomSignals(bottom) {
  const headers = tr().bottomHeaders;
  const rows = bottom?.signals || [];
  document.getElementById("bottom-signal-table").innerHTML = `
    <div class="metric-row bottom-row">${headers.map((h) => `<span>${h}</span>`).join("")}</div>
    ${rows
      .map(
        (m) => `<div class="metric-row bottom-row">
          <span><strong>${m.name}</strong><small>${m.note || ""}</small></span>
          <span>${fmtValue(m.value)}</span>
          <span>${m.score === null || m.score === undefined ? "--" : fmtNum(m.score, 0)}</span>
          <span>${m.source || "--"}</span>
        </div>`
      )
      .join("")}`;
}

function renderCalibration(bottom) {
  const headers = tr().thresholdHeaders;
  const rows = bottom?.calibration?.threshold_summary || [];
  document.getElementById("calibration-table").innerHTML = `
    <div class="metric-row calibration-row">${headers.map((h) => `<span>${h}</span>`).join("")}</div>
    ${rows
      .map(
        (r) => `<div class="metric-row calibration-row ${r.threshold === bottom.calibration.best_threshold ? "highlight" : ""}">
          <span>${fmtNum(r.threshold, 0)}</span>
          <span>${r.triggered_events}/${r.events}</span>
          <span>${fmtNum(r.avg_days_from_low, 1)}</span>
          <span>${fmtPct(r.avg_fwd_21d)}</span>
          <span>${fmtPct(r.hit_rate_21d)}</span>
          <span>${fmtPct(r.avg_fwd_63d)}</span>
          <span>${fmtPct(r.hit_rate_63d)}</span>
        </div>`
      )
      .join("")}`;

  const wf = bottom?.calibration?.walk_forward;
  if (!wf) {
    document.getElementById("walk-forward-copy").textContent = "";
  } else if (currentLanguage === "zh") {
    document.getElementById("walk-forward-copy").textContent =
      `Walk-forward：${wf.triggered_events}/${wf.tested_events} 个事件，21 日收益 ${fmtPct(wf.avg_fwd_21d)}，胜率 ${fmtPct(wf.hit_rate_21d)}；63 日收益 ${fmtPct(wf.avg_fwd_63d)}，胜率 ${fmtPct(wf.hit_rate_63d)}。`;
  } else {
    document.getElementById("walk-forward-copy").textContent =
      `Walk-forward: ${wf.triggered_events}/${wf.tested_events} events, 21D ${fmtPct(wf.avg_fwd_21d)} with ${fmtPct(wf.hit_rate_21d)} hit rate; 63D ${fmtPct(wf.avg_fwd_63d)} with ${fmtPct(wf.hit_rate_63d)} hit rate.`;
  }
}

function renderConcept() {
  document.getElementById("concept-grid").innerHTML = tr()
    .conceptCards.map(
      (card) => `<article class="concept-card"><h3>${card.title}</h3><p>${card.body}</p></article>`
    )
    .join("");
}

function renderSources(data) {
  const bottom = data.bottom_framework;
  const sourceRows =
    currentLanguage === "zh"
      ? [
          ["Yahoo Finance", "QQQ、TQQQ、SPY、QQEW、VIX、VIX3M、VXN、TNX 与 BTC-USD", data.price?.latest_date],
          ["FINRA", "月度保证金数据；底部回测中按发布滞后对齐", data.finra?.month || "--"],
          ["FRED / NY Fed / Treasury", "银行准备金、TGA、SOFR 减 ON RRP，以及 SRF / 回购操作", data.top_fragility_overlay?.groups?.liquidity_drain?.metrics?.[0]?.as_of || "--"],
          ["SEC Companyfacts", "MSFT、AMZN、GOOGL、META CapEx 代理与美光财务数据", data.top_fragility_overlay?.groups?.ai_capex_cycle?.metrics?.[0]?.as_of || "--"],
          ["Cboe 代理", "免费 SPX / SPXW 看涨看跌成交量代理；不等同精确 0DTE 或 dealer gamma", data.top_fragility_overlay?.groups?.options_mechanical_bid?.metrics?.[1]?.as_of || "--"],
          ["自动刷新", "更新数据快照并保留模型所需的追溯信息", fmtDateTime(data.generated_at)]
        ]
      : [
          ["Yahoo Finance", "QQQ, TQQQ, SPY, QQEW, VIX, VIX3M, VXN, TNX, and BTC-USD", data.price?.latest_date],
          ["FINRA", "Monthly margin statistics, lagged by publication date in the bottom backtest", data.finra?.month || "--"],
          ["FRED / NY Fed / Treasury", "Bank reserves, TGA, SOFR minus ON RRP, and SRF / repo operations", data.top_fragility_overlay?.groups?.liquidity_drain?.metrics?.[0]?.as_of || "--"],
          ["SEC Companyfacts", "MSFT, AMZN, GOOGL, META CapEx proxies and Micron financial statements", data.top_fragility_overlay?.groups?.ai_capex_cycle?.metrics?.[0]?.as_of || "--"],
          ["Cboe Proxy", "Free SPX / SPXW call-put volume proxy; not exact 0DTE or dealer gamma", data.top_fragility_overlay?.groups?.options_mechanical_bid?.metrics?.[1]?.as_of || "--"],
          ["Automated refresh", "Updates the data snapshot while preserving model provenance", fmtDateTime(data.generated_at)]
        ];
  document.getElementById("source-grid").innerHTML = sourceRows
    .map(
      ([title, body, latest]) => `<article class="source-card">
        <h3>${title}</h3>
        <p>${body}</p>
        <small>${latest || "--"}</small>
      </article>`
    )
    .join("");
}

function render(data) {
  renderStaticText();
  renderConcept();
  renderSources(data);

  const bubbleScore = Number(data.overall_score);
  const bubbleColor = scoreColor(bubbleScore);
  const bubbleMeta = tr().statusMeta[data.status] || tr().statusMeta.Yellow;
  document.getElementById("overall-score").textContent = fmtNum(bubbleScore, 0);
  document.getElementById("status-title").textContent = bubbleMeta[0];
  document.getElementById("status-copy").textContent = bubbleMeta[1];
  setRing("score-ring", bubbleScore, 100, bubbleColor);

  const bottom = data.bottom_framework;
  const bottomScore = bottom?.available ? Number(bottom.score) : 0;
  const bottomStatus = bottom?.status || "No setup";
  const bottomColor = statusColors[bottomStatus] || statusColors["No setup"];
  const bottomMeta = tr().bottomStatus[bottomStatus] || tr().bottomStatus["No setup"];
  document.getElementById("bottom-score").textContent = fmtNum(bottomScore, 1);
  document.getElementById("bottom-status-title").textContent = bottomMeta[0];
  document.getElementById("bottom-status-copy").textContent = bottom?.available ? bottomMeta[1] : bottom?.error || "--";
  document.getElementById("bottom-threshold").textContent = bottom?.available
    ? currentLanguage === "zh"
      ? `参考阈值 ${bottom.calibration.best_threshold}/20 · 当前回撤 ${fmtPct(bottom.qqq.drawdown_from_52w_high)}`
      : `Threshold ${bottom.calibration.best_threshold}/20 · ${fmtPct(bottom.qqq.drawdown_from_52w_high)} drawdown`
    : "--";
  setRing("bottom-ring", bottomScore, 20, bottomColor);

  const briefing = tr().briefingStatus[data.status] || tr().briefingStatus.Yellow;
  const highestModule = Object.entries(data.modules || {}).sort((a, b) => Number(b[1]) - Number(a[1]))[0];
  const highestModuleLabel = highestModule ? tr().moduleLabels[highestModule[0]] || highestModule[0] : "--";
  const driverCopy = highestModule
    ? currentLanguage === "zh"
      ? ` 当前最高风险贡献来自${highestModuleLabel}（${fmtNum(highestModule[1], 0)}）。`
      : ` The largest current contribution is ${highestModuleLabel} (${fmtNum(highestModule[1], 0)}).`
    : "";
  document.getElementById("briefing-status").textContent = `${data.status} · ${fmtNum(bubbleScore, 1)}`;
  document.getElementById("briefing-title").textContent = briefing[0];
  document.getElementById("briefing-copy").textContent = `${briefing[1]}${driverCopy}`;
  document.getElementById("brief-qqq").textContent = fmtNum(data.price?.latest, 2);
  document.getElementById("brief-drawdown").textContent = fmtPct(data.price?.drawdown_from_52w_high);
  document.getElementById("brief-confidence").textContent = `${fmtNum(data.data_quality?.summary?.confidence_score, 1)} / 100`;

  document.getElementById("status-pill").textContent = data.status;
  document.getElementById("status-pill").style.color = bubbleColor;
  document.getElementById("status-pill").style.borderColor = bubbleColor;
  document.getElementById("generated-at").textContent = `${tr().snapshotPrefix}: ${fmtDateTime(data.generated_at)}`;
  document.getElementById("update-frequency").textContent = tr().dailySnapshot;

  document.getElementById("price-title").textContent = `QQQ ${fmtNum(data.price.latest, 2)} · ${data.price.latest_date}`;
  document.getElementById("ret-3m").textContent = `3M ${fmtPct(data.price.return_3m)}`;
  document.getElementById("dist-200").textContent = `200DMA ${fmtPct(data.price.distance_200dma)}`;
  drawChart(document.getElementById("price-chart"), data.history);

  renderDecisionStrip("decision-strip", tr().decisions, data.status);
  renderDecisionStrip("bottom-decision-strip", tr().bottomDecisions, bottomStatus);
  renderModules(data);
  renderDataQuality(data);
  renderTopFragility(data);
  renderMicronCanary(data);
  renderBottomSignals(bottom);
  renderCalibration(bottom);

  const warnings = data.warnings && data.warnings.length ? data.warnings.map(localizedWarning) : [tr().noWarning];
  document.getElementById("warnings-list").innerHTML = warnings.map((w) => `<li>${w}</li>`).join("");
  document.getElementById("metric-table").innerHTML = [
    renderMetricGroups(tr().coreMetricsLabel, data.core_metrics),
    renderMetricGroups(tr().contextMetricsLabel, data.metrics)
  ].join("");
  document.getElementById("method-copy").textContent = tr().methodCopy;
}

async function loadDashboard() {
  try {
    const response = await fetch("./data/dashboard.json", { cache: "no-store" });
    latestData = await response.json();
  } catch (error) {
    if (!window.DASHBOARD_DATA) throw error;
    latestData = window.DASHBOARD_DATA;
  }
  render(latestData);
}

document.getElementById("lang-en").addEventListener("click", () => setLanguage("en"));
document.getElementById("lang-zh").addEventListener("click", () => setLanguage("zh"));
document.getElementById("view-mode-toggle").addEventListener("click", () => {
  setZenMode(!document.documentElement.classList.contains("zen-mode"));
});
window.addEventListener("resize", () => latestData && drawChart(document.getElementById("price-chart"), latestData.history));

setZenMode(false);
setLanguage(currentLanguage);
loadDashboard().catch((error) => {
  document.getElementById("status-title").textContent = tr().dataLoadFailed;
  document.getElementById("status-copy").textContent = error.message;
});
