const statusMeta = {
  Green: {
    color: "#26734d",
    title: "Green - 正常",
    copy: "泡沫压力没有形成系统性高危组合，维持常规监控。"
  },
  Yellow: {
    color: "#a37716",
    title: "Yellow - 观察",
    copy: "市场偏热，开始跟踪资金流、广度和杠杆变化。"
  },
  Orange: {
    color: "#b85223",
    title: "Orange - 降风险",
    copy: "泡沫晚期概率上升，避免加杠杆，降低高 beta 暴露。"
  },
  Red: {
    color: "#b3263a",
    title: "Red - 强警戒",
    copy: "多个模块同时高危，优先考虑对冲、止盈和降低集中仓位。"
  }
};

const moduleLabels = {
  valuation: "估值压力",
  liquidity: "资金增量",
  leverage_derivatives: "杠杆/衍生品",
  breadth_concentration: "广度/集中度",
  price_confirmation: "价格确认"
};

const decisions = [
  ["Green", "正常配置", "常规再平衡，继续跟踪。"],
  ["Yellow", "停止追高", "观察资金流和市场广度。"],
  ["Orange", "降低风险", "减少杠杆和高 beta 集中。"],
  ["Red", "强警戒", "对冲、止盈、严格止损。"]
];

function fmtPct(value) {
  if (value === null || value === undefined || Number.isNaN(value)) return "--";
  return `${(value * 100).toFixed(1)}%`;
}

function fmtNum(value, digits = 1) {
  if (value === null || value === undefined || Number.isNaN(value)) return "--";
  return Number(value).toFixed(digits);
}

function scoreColor(score) {
  if (score >= 75) return "#b3263a";
  if (score >= 60) return "#b85223";
  if (score >= 40) return "#a37716";
  return "#26734d";
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
  const data = await response.json();
  render(data);
}

function render(data) {
  const meta = statusMeta[data.status] || statusMeta.Yellow;
  const score = Number(data.overall_score);

  document.getElementById("overall-score").textContent = fmtNum(score, 0);
  document.getElementById("status-title").textContent = meta.title;
  document.getElementById("status-copy").textContent = meta.copy;
  document.getElementById("status-pill").textContent = data.status;
  document.getElementById("status-pill").style.borderColor = meta.color;
  document.getElementById("status-pill").style.color = meta.color;
  document.getElementById("generated-at").textContent = new Date(data.generated_at).toLocaleString();

  const deg = Math.round(score * 3.6);
  const ring = document.getElementById("score-ring");
  ring.style.background = `conic-gradient(${scoreColor(score)} 0deg, ${scoreColor(score)} ${deg}deg, #e6e8e1 ${deg}deg)`;

  document.getElementById("price-title").textContent = `QQQ ${fmtNum(data.price.latest, 2)} · ${data.price.latest_date}`;
  document.getElementById("ret-3m").textContent = `3M ${fmtPct(data.price.return_3m)}`;
  document.getElementById("dist-200").textContent = `200DMA ${fmtPct(data.price.distance_200dma)}`;

  document.getElementById("decision-strip").innerHTML = decisions
    .map(([name, title, copy]) => {
      const active = name === data.status;
      return `<div class="decision" style="${active ? `border-color:${statusMeta[name].color};` : ""}">
        <strong style="${active ? `color:${statusMeta[name].color};` : ""}">${name} · ${title}</strong>
        <span>${copy}</span>
      </div>`;
    })
    .join("");

  document.getElementById("modules").innerHTML = Object.entries(data.modules)
    .map(([key, value]) => {
      const color = scoreColor(value);
      return `<article class="module">
        <p class="label">${moduleLabels[key] || key}</p>
        <div class="module-value" style="color:${color}">${fmtNum(value, 0)}</div>
        <div class="bar"><span style="width:${value}%; background:${color}"></span></div>
      </article>`;
    })
    .join("");

  const warnings = data.warnings && data.warnings.length ? data.warnings : ["No active warning."];
  document.getElementById("warnings-list").innerHTML = warnings.map((w) => `<li>${w}</li>`).join("");

  const groups = Object.entries(data.metrics || {});
  document.getElementById("metric-table").innerHTML = groups
    .map(([group, rows]) => {
      const body = (rows || [])
        .map((m) => `<div class="metric-row">
          <span>${m.name}</span>
          <span>${m.value === null ? "--" : fmtNum(m.value, 2)}</span>
          <span>${m.score === null ? "--" : fmtNum(m.score, 0)}</span>
          <span>${m.source}</span>
        </div>`)
        .join("");
      return `<div class="metric-group">
        <p class="label">${group}</p>
        <div class="metric-row"><span>Indicator</span><span>Value</span><span>Score</span><span>Source</span></div>
        ${body || '<div class="metric-row"><span>No data</span><span>--</span><span>--</span><span>--</span></div>'}
      </div>`;
    })
    .join("");

  drawChart(document.getElementById("price-chart"), data.history);
}

window.addEventListener("resize", () => loadDashboard().catch(() => {}));
loadDashboard().catch((error) => {
  document.getElementById("status-title").textContent = "Data load failed";
  document.getElementById("status-copy").textContent = error.message;
});
