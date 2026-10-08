const lines = ['Line A', 'Line B', 'Line C', 'Line D'];
const shifts = ['Day', 'Swing', 'Night'];
const defectTypes = ['AOI', 'ICT', 'Solder', 'Labeling', 'Mechanical'];

function formatDate(date) {
  const d = new Date(date);
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

function generateMockData() {
  const data = [];
  const startDate = new Date('2026-09-15');

  for (let day = 0; day < 14; day++) {
    const currentDate = new Date(startDate);
    currentDate.setDate(startDate.getDate() + day);

    lines.forEach((line, lineIndex) => {
      shifts.forEach((shift, shiftIndex) => {
        const plannedMinutes = 480;
        const runMinutes = plannedMinutes * (0.9 + (lineIndex * 0.025) + (shiftIndex * 0.02) + Math.sin(day / 3 + lineIndex) * 0.04);
        const targetRate = 18 + lineIndex * 1.5 + shiftIndex * 0.8;
        const actualUnits = Math.round((runMinutes * targetRate) * (0.88 + (lineIndex * 0.04) + (shiftIndex * 0.03) + (day % 5) * 0.01))
        const goodUnits = Math.round(actualUnits * (0.965 + (lineIndex * 0.008) - (shiftIndex * 0.004) + ((day % 4) * 0.003)));
        const defectBreakdown = {};
        let remaining = actualUnits - goodUnits;

        defectTypes.forEach((type, idx) => {
          const share = idx === defectTypes.length - 1 ? remaining : Math.max(0, Math.round((remaining * (0.16 + idx * 0.12 + Math.random() * 0.18))));
          defectBreakdown[type] = share;
          remaining -= share;
        });

        data.push({
          date: currentDate.toISOString(),
          line,
          shift,
          plannedMinutes: Math.round(plannedMinutes),
          runMinutes: Math.round(runMinutes),
          actualUnits,
          goodUnits,
          targetUnits: Math.round(runMinutes * targetRate),
          defectBreakdown,
        });
      });
    });
  }

  return data;
}

const productionData = generateMockData();
const lineFilter = document.getElementById('lineFilter');
const shiftFilter = document.getElementById('shiftFilter');

function populateFilters() {
  lines.forEach((line) => {
    const option = document.createElement('option');
    option.value = line;
    option.textContent = line;
    lineFilter.appendChild(option);
  });
}

function getFilteredData() {
  const selectedLine = lineFilter.value;
  const selectedShift = shiftFilter.value;

  return productionData.filter((record) => {
    const lineMatch = selectedLine === 'All' || record.line === selectedLine;
    const shiftMatch = selectedShift === 'All' || record.shift === selectedShift;
    return lineMatch && shiftMatch;
  });
}

function calculateAvailability(record) {
  return (record.runMinutes / record.plannedMinutes) * 100;
}

function calculatePerformance(record) {
  return (record.actualUnits / record.targetUnits) * 100;
}

function calculateQuality(record) {
  return (record.goodUnits / record.actualUnits) * 100;
}

function calculateOEE(record) {
  return calculateAvailability(record) * calculatePerformance(record) * calculateQuality(record) / 10000;
}

function formatPercentage(value) {
  return `${value.toFixed(1)}%`;
}

function renderKpis(filteredData) {
  const totalUnits = filteredData.reduce((sum, record) => sum + record.actualUnits, 0);
  const goodUnits = filteredData.reduce((sum, record) => sum + record.goodUnits, 0);
  const plannedMinutes = filteredData.reduce((sum, record) => sum + record.plannedMinutes, 0);
  const runMinutes = filteredData.reduce((sum, record) => sum + record.runMinutes, 0);

  const availability = (runMinutes / plannedMinutes) * 100;
  const performance = (totalUnits / filteredData.reduce((sum, record) => sum + record.targetUnits, 0)) * 100;
  const quality = (goodUnits / totalUnits) * 100;
  const oee = (availability * performance * quality) / 10000;

  document.getElementById('availabilityKpi').textContent = formatPercentage(availability);
  document.getElementById('performanceKpi').textContent = formatPercentage(performance);
  document.getElementById('qualityKpi').textContent = formatPercentage(quality);
  document.getElementById('oeeKpi').textContent = formatPercentage(oee);

  document.getElementById('goodUnitsMetric').textContent = goodUnits.toLocaleString();
  document.getElementById('totalUnitsMetric').textContent = totalUnits.toLocaleString();
  document.getElementById('runTimeMetric').textContent = `${(runMinutes / 60).toFixed(1)}h`;
  document.getElementById('downtimeMetric').textContent = `${(plannedMinutes - runMinutes).toFixed(0)}m`;
}

function renderTrendChart(filteredData) {
  const grouped = {};

  filteredData.forEach((record) => {
    const dateKey = new Date(record.date).toISOString().slice(0, 10);
    if (!grouped[dateKey]) grouped[dateKey] = [];
    grouped[dateKey].push(record);
  });

  const labels = Object.keys(grouped).sort().map((key) => formatDate(key));
  const oeeSeries = labels.map((_, idx) => {
    const key = Object.keys(grouped).sort()[idx];
    const entries = grouped[key];
    const dailyOEE = entries.reduce((sum, record) => sum + calculateOEE(record), 0) / entries.length;
    return dailyOEE;
  });

  const trendCtx = document.getElementById('oeeTrendChart');

  if (window.oeeTrendChart) {
    window.oeeTrendChart.destroy();
  }

  window.oeeTrendChart = new Chart(trendCtx, {
    type: 'line',
    data: {
      labels,
      datasets: [{
        label: 'OEE %',
        data: oeeSeries,
        borderColor: '#4da3ff',
        backgroundColor: 'rgba(77, 163, 255, 0.18)',
        fill: true,
        tension: 0.35,
        borderWidth: 2.5,
        pointRadius: 3,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
      },
      scales: {
        y: {
          beginAtZero: false,
          min: 60,
          max: 100,
          ticks: {
            callback: (value) => `${value}%`,
            color: '#8ea3be',
          },
          grid: { color: 'rgba(148, 163, 184, 0.08)' },
        },
        x: {
          ticks: { color: '#8ea3be' },
          grid: { display: false },
        },
      },
    },
  });
}

function renderLineComparisonChart(filteredData) {
  const lineValues = {};

  filteredData.forEach((record) => {
    if (!lineValues[record.line]) lineValues[record.line] = [];
    lineValues[record.line].push(calculateOEE(record));
  });

  const labels = Object.keys(lineValues);
  const values = labels.map((line) => {
    const avg = lineValues[line].reduce((sum, value) => sum + value, 0) / lineValues[line].length;
    return avg;
  });

  const barCtx = document.getElementById('lineComparisonChart');

  if (window.lineComparisonChart) {
    window.lineComparisonChart.destroy();
  }

  window.lineComparisonChart = new Chart(barCtx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: 'Average OEE',
        data: values,
        backgroundColor: ['#4da3ff', '#2dd4bf', '#8b5cf6', '#f59e0b'],
        borderRadius: 8,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        y: {
          beginAtZero: false,
          min: 60,
          max: 100,
          ticks: {
            callback: (value) => `${value}%`,
            color: '#8ea3be',
          },
          grid: { color: 'rgba(148, 163, 184, 0.08)' },
        },
        x: {
          ticks: { color: '#8ea3be' },
          grid: { display: false },
        },
      },
    },
  });
}

function renderDefectChart(filteredData) {
  const totals = { AOI: 0, ICT: 0, Solder: 0, Labeling: 0, Mechanical: 0 };

  filteredData.forEach((record) => {
    Object.entries(record.defectBreakdown).forEach(([type, value]) => {
      totals[type] += value;
    });
  });

  const values = Object.values(totals);
  const hasData = values.some((value) => value > 0);

  const defectCtx = document.getElementById('defectChart');

  if (window.defectChart) {
    window.defectChart.destroy();
  }

  window.defectChart = new Chart(defectCtx, {
    type: 'doughnut',
    data: {
      labels: defectTypes,
      datasets: [{
        data: hasData ? values : [1, 1, 1, 1, 1],
        backgroundColor: ['#4da3ff', '#2dd4bf', '#8b5cf6', '#f59e0b', '#f87171'],
        borderWidth: 0,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: '62%',
      plugins: {
        legend: {
          position: 'bottom',
          labels: { color: '#8ea3be', boxWidth: 12 },
        },
      },
    },
  });
}

function renderTable(filteredData) {
  const rows = filteredData
    .slice()
    .sort((a, b) => new Date(a.date) - new Date(b.date))
    .map((record) => {
      const availability = calculateAvailability(record);
      const performance = calculatePerformance(record);
      const quality = calculateQuality(record);
      const oee = calculateOEE(record);
      const labelClass = oee >= 80 ? 'good' : oee >= 65 ? 'warn' : 'bad';

      return `
        <tr>
          <td>${formatDate(record.date)}</td>
          <td>${record.line}</td>
          <td>${record.shift}</td>
          <td>${formatPercentage(availability)}</td>
          <td>${formatPercentage(performance)}</td>
          <td>${formatPercentage(quality)}</td>
          <td><span class="badge ${labelClass}">${formatPercentage(oee)}</span></td>
          <td>${record.goodUnits.toLocaleString()}</td>
        </tr>
      `;
    })
    .join('');

  document.getElementById('performanceTable').innerHTML = rows;
}

function renderDashboard() {
  const filteredData = getFilteredData();
  renderKpis(filteredData);
  renderTrendChart(filteredData);
  renderLineComparisonChart(filteredData);
  renderDefectChart(filteredData);
  renderTable(filteredData);
}

lineFilter.addEventListener('change', renderDashboard);
shiftFilter.addEventListener('change', renderDashboard);

populateFilters();
renderDashboard();
