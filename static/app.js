(function () {
  "use strict";

  function money(value) {
    return "₹" + Number(value || 0).toLocaleString("en-IN", { maximumFractionDigits: 0 });
  }

  function numberValue(form, name) {
    const el = form.querySelector('[name="' + name + '"]');
    return el ? Math.max(parseFloat(el.value) || 0, 0) : 0;
  }

  function localCalculate(form) {
    const area = numberValue(form, "area");
    const yieldPerAcre = numberValue(form, "yield_per_acre");
    const price = numberValue(form, "price");
    const names = ["seed", "fertilizer", "pesticide", "labor", "machinery", "irrigation", "transport", "other"];
    let totalCost = 0;
    names.forEach((name) => { totalCost += numberValue(form, name); });
    const production = area * yieldPerAcre;
    const revenue = production * price;
    const profit = revenue - totalCost;
    const roi = totalCost ? profit / totalCost * 100 : 0;
    const margin = revenue ? profit / revenue * 100 : 0;
    const risk = profit < 0 || margin < 10 ? "High" : margin < 25 ? "Medium" : "Low";
    return {
      production, revenue, total_cost: totalCost, profit, roi, margin, risk,
      break_even_price: production ? totalCost / production : 0,
      break_even_yield: price && area ? totalCost / price / area : 0
    };
  }

  function set(id, value) {
    const el = document.getElementById(id);
    if (el) el.textContent = value;
  }

  const simForm = document.getElementById("sim-form");
  if (simForm) {
    const crop = document.getElementById("crop");
    const yieldInput = document.getElementById("yield_per_acre");
    const priceInput = document.getElementById("price");
    const saveBtn = document.getElementById("saveBtn");
    const saveField = document.getElementById("save_plan");

    if (crop) {
      crop.addEventListener("change", function () {
        const selected = crop.options[crop.selectedIndex];
        if (selected && yieldInput && priceInput) {
          yieldInput.value = selected.dataset.yield || yieldInput.value;
          priceInput.value = selected.dataset.price || priceInput.value;
          update();
        }
      });
    }

    function update() {
      const r = localCalculate(simForm);
      set("profit-display", money(r.profit));
      set("revenue-display", money(r.revenue));
      set("cost-display", money(r.total_cost));
      set("roi-display", r.roi.toFixed(1) + "%");
      set("risk-display", r.risk);
      set("be-price", money(r.break_even_price));
      set("be-yield", r.break_even_yield.toFixed(2));
      set("production", r.production.toLocaleString("en-IN", { maximumFractionDigits: 1 }));
      set("margin", r.margin.toFixed(1) + "%");
      set("profit-message", r.profit < 0 ? "This plan is currently loss-making." : "This plan is profitable under your assumptions.");
      const hero = document.querySelector(".result-hero");
      if (hero) hero.classList.toggle("loss", r.profit < 0);
      return r;
    }

    simForm.querySelectorAll("input, select").forEach((el) => el.addEventListener("input", update));

    if (saveBtn) {
      saveBtn.addEventListener("click", function () {
        saveField.value = "1";
        simForm.submit();
      });
    }

    update();

    const priceSlider = document.getElementById("priceSlider");
    const yieldSlider = document.getElementById("yieldSlider");
    const costSlider = document.getElementById("costSlider");
    const baseline = () => localCalculate(simForm);

    function updateWhatIf() {
      const base = baseline();
      const p = Number(priceSlider ? priceSlider.value : 0);
      const y = Number(yieldSlider ? yieldSlider.value : 0);
      const c = Number(costSlider ? costSlider.value : 0);
      const scenarioRevenue = base.revenue * (1 + p / 100) * (1 + y / 100);
      const scenarioCost = base.total_cost * (1 + c / 100);
      const scenarioProfit = scenarioRevenue - scenarioCost;
      const change = base.profit ? (scenarioProfit - base.profit) / Math.abs(base.profit) * 100 : 0;
      const margin = scenarioRevenue ? scenarioProfit / scenarioRevenue * 100 : 0;
      const risk = scenarioProfit < 0 || margin < 10 ? "High" : margin < 25 ? "Medium" : "Low";
      set("priceOut", (p >= 0 ? "+" : "") + p + "%");
      set("yieldOut", (y >= 0 ? "+" : "") + y + "%");
      set("costOut", (c >= 0 ? "+" : "") + c + "%");
      set("scenarioProfit", money(scenarioProfit));
      set("scenarioChange", (change >= 0 ? "+" : "") + change.toFixed(1) + "%");
      set("scenarioRisk", risk);
    }

    [priceSlider, yieldSlider, costSlider].forEach((el) => { if (el) el.addEventListener("input", updateWhatIf); });
    updateWhatIf();
  }

  const dashboardCrop = document.querySelector("[data-crop-select]");
  if (dashboardCrop) {
    const y = document.querySelector("[data-yield-input]");
    const p = document.querySelector("[data-price-input]");
    dashboardCrop.addEventListener("change", function () {
      const option = dashboardCrop.options[dashboardCrop.selectedIndex];
      if (option) {
        if (y) y.value = option.dataset.yield || y.value;
        if (p) p.value = option.dataset.price || p.value;
      }
    });
  }

  const canvas = document.getElementById("compareChart");
  if (canvas && window.compareData) {
    const ctx = canvas.getContext("2d");
    const data = window.compareData;
    const width = canvas.clientWidth || 800;
    const height = 260;
    const ratio = window.devicePixelRatio || 1;
    canvas.width = width * ratio;
    canvas.height = height * ratio;
    canvas.style.height = height + "px";
    ctx.scale(ratio, ratio);
    const max = Math.max.apply(null, data.map((d) => Math.max(d.profit, 1)));
    const pad = 35;
    const chartW = width - pad * 2;
    const chartH = height - 55;
    const barW = Math.max(14, chartW / data.length - 14);
    ctx.font = "10px DM Sans, sans-serif";
    data.forEach((d, i) => {
      const x = pad + i * (chartW / data.length) + 8;
      const h = Math.max(4, d.profit / max * chartH);
      const y = height - 28 - h;
      ctx.fillStyle = "#73a773";
      ctx.fillRect(x, y, barW, h);
      ctx.fillStyle = "#526057";
      ctx.textAlign = "center";
      ctx.fillText(d.crop, x + barW / 2, height - 10);
    });
  }
})();
