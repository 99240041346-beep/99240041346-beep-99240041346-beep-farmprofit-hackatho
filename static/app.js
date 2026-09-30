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
      set("scenarioRevenue", money(scenarioRevenue));
      set("scenarioCost", money(scenarioCost));
      set("scenarioProfit", money(scenarioProfit));
      set("scenarioMargin", margin.toFixed(1) + "%");
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
  // Manual weather location + soil-aware irrigation
  const locationInput = document.getElementById("weatherLocationInput");
  const locationSearch = document.getElementById("weatherLocationSearch");
  const locationResults = document.getElementById("locationResults");
  const selectedLocation = document.getElementById("selectedWeatherLocation");
  const irrigationBtn = document.getElementById("checkIrrigation");
  const irrigationStatus = document.getElementById("irrigationStatus");
  const irrigationResult = document.getElementById("irrigationResult");
  let selectedWeatherLocation = null;

  function locationLabel(place) {
    return [place.name, place.admin2 || place.admin1, place.country].filter(Boolean).join(", ");
  }

  function renderLocationResults(results) {
    if (!locationResults) return;
    locationResults.innerHTML = "";
    if (!results.length) {
      locationResults.hidden = false;
      locationResults.innerHTML = '<div class="location-empty">No matching places found. Try a nearby town or district.</div>';
      return;
    }
    results.forEach((place) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "location-option";
      button.innerHTML = "<strong></strong><small></small>";
      button.querySelector("strong").textContent = place.name || "Selected place";
      button.querySelector("small").textContent = [place.admin2 || place.admin1, place.country].filter(Boolean).join(" • ");
      button.addEventListener("click", () => selectFarmLocation(place));
      locationResults.appendChild(button);
    });
    locationResults.hidden = false;
  }

  function selectFarmLocation(place) {
    selectedWeatherLocation = place;
    if (locationInput) locationInput.value = locationLabel(place);
    if (selectedLocation) selectedLocation.textContent = "✓ " + locationLabel(place);
    if (locationResults) locationResults.hidden = true;
    localStorage.setItem("agriwise-weather-location", JSON.stringify(place));
    if (irrigationStatus) irrigationStatus.textContent = "Farm location selected.";
    // On the Weather page, immediately reload the real forecast for the chosen result.
    if (window.WEATHER_PAGE && (!window.WEATHER_PAGE.selectedPlace || String(window.WEATHER_PAGE.selectedPlace.latitude) !== String(place.latitude) || String(window.WEATHER_PAGE.selectedPlace.longitude) !== String(place.longitude))) {
      const params = new URLSearchParams({
        location: locationLabel(place),
        lat: place.latitude,
        lon: place.longitude,
        country: place.country || ""
      });
      window.location.href = "/weather?" + params.toString();
    }
  }

  async function searchFarmLocation() {
    const q = locationInput ? locationInput.value.trim() : "";
    if (q.length < 2) {
      if (irrigationStatus) irrigationStatus.textContent = "Type a village, town or city name.";
      return;
    }
    if (irrigationStatus) irrigationStatus.textContent = "Finding matching places…";
    try {
      const response = await fetch("/api/location-search?q=" + encodeURIComponent(q));
      const data = await response.json();
      const results = Array.isArray(data.results) ? data.results : [];
      renderLocationResults(results);
      if (irrigationStatus) {
        irrigationStatus.textContent = results.length
          ? "Choose a location to display its recorded weather."
          : "No matching place found. Try the village, town, district or nearest city name.";
      }
    } catch (_) {
      if (irrigationStatus) irrigationStatus.textContent = "Please try the location search again.";
    }
  }

  async function checkIrrigation() {
    if (!selectedWeatherLocation) {
      if (irrigationStatus) irrigationStatus.textContent = "Choose your farm location first.";
      return;
    }
    const crop = document.getElementById("irrigationCrop")?.value || "Rice";
    const soil = document.getElementById("irrigationSoil")?.value || "Loamy";
    const area = Math.max(Number(document.getElementById("irrigationArea")?.value || 1), 0.1);\n    const stage = document.getElementById("irrigationStage")?.value || "Vegetative";
    if (irrigationBtn) { irrigationBtn.disabled = true; irrigationBtn.textContent = "Calculating…"; }
    if (irrigationStatus) irrigationStatus.textContent = "Preparing your irrigation plan…";
    try {
      const params = new URLSearchParams({
        lat: selectedWeatherLocation.latitude, lon: selectedWeatherLocation.longitude,
        name: selectedWeatherLocation.name || "Selected farm", crop, soil, stage, area
      });
      const response = await fetch("/api/irrigation?" + params.toString());
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "Irrigation calculation failed");
      const a = data.irrigation;
      if (irrigationResult) {
        irrigationResult.hidden = false;
        irrigationResult.innerHTML = `
          <div class="irrigation-main">
            <div><span class="irrigation-badge">${a.action}</span><h3>${a.timing}</h3><p>${a.soil_note}</p></div>
            <div class="water-number"><small>Estimated water</small><strong>${Number(a.estimated_total_litres).toLocaleString("en-IN")} L</strong><span>for ${area} acres</span></div>
          </div>
          <div class="irrigation-stats">
            <div><small>Per acre</small><b>${Number(a.estimated_litres_per_acre).toLocaleString("en-IN")} L</b></div>
            <div><small>Water need</small><b>${a.estimated_need_mm} mm</b></div>
            <div><small>Rain next 24h</small><b>${a.rain_24h_mm} mm</b></div>
            <div><small>Rain probability</small><b>${a.rain_probability_percent}%</b></div>
            <div><small>Soil holding</small><b>${a.soil_water_holding}</b></div>
            <div><small>Temperature</small><b>${a.temperature_c}°C</b></div>
          </div>
          <div class="irrigation-method"><strong>Recommended method:</strong> ${a.irrigation_method} · <strong>Typical interval:</strong> ${a.typical_interval}</div>
          <div class="irrigation-disclaimer">${a.method} Adjust using field soil moisture, crop growth stage and local agronomist guidance.</div>`;
      }
      if (irrigationStatus) irrigationStatus.textContent = "Irrigation plan ready for " + locationLabel(selectedWeatherLocation) + ".";
    } catch (error) {
      if (irrigationStatus) irrigationStatus.textContent = "Irrigation guidance is based on the selected farm conditions.";
    } finally {
      if (irrigationBtn) { irrigationBtn.disabled = false; irrigationBtn.textContent = "Predict irrigation"; }
    }
  }

  if (locationSearch) locationSearch.addEventListener("click", searchFarmLocation);
  if (window.WEATHER_PAGE && window.WEATHER_PAGE.selectedPlace) {
    selectedWeatherLocation = window.WEATHER_PAGE.selectedPlace;
    if (locationInput) locationInput.value = locationLabel(selectedWeatherLocation);
    if (selectedLocation) selectedLocation.textContent = "✓ " + locationLabel(selectedWeatherLocation);
    localStorage.setItem("agriwise-weather-location", JSON.stringify(selectedWeatherLocation));
  }
  if (locationInput) locationInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter") { event.preventDefault(); searchFarmLocation(); }
  });
  if (irrigationBtn) irrigationBtn.addEventListener("click", checkIrrigation);

  try {
    const saved = JSON.parse(localStorage.getItem("agriwise-weather-location") || "null");
    if (saved && saved.latitude && saved.longitude) selectFarmLocation(saved);
  } catch (_) {}

})();
