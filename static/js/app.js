// Main Dashboard Application Logic

let currentPage = 'dashboard';
let currentLineFilter = '';
let currentShiftFilter = '';
let currentDateFrom = '';
let currentDateTo = '';
let chartInstances = {};

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
  initializeNavigation();
  initializeFilters();
  initializeEventListeners();
  loadDashboardData();
});

// Navigation
function initializeNavigation() {
  document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', () => {
      const page = item.dataset.page;
      switchPage(page);
    });
  });
}

function switchPage(pageName) {
  document.querySelectorAll('.page').forEach(page => {
    page.classList.remove('active');
  });
  
  document.querySelector(`.${pageName}-page`).classList.add('active');
  
  document.querySelectorAll('.nav-item').forEach(item => {
    item.classList.remove('active');
  });
  
  document.querySelector(`[data-page="${pageName}"]`).classList.add('active');
  currentPage = pageName;
  
  if (pageName === 'production') loadProductionPage();
  if (pageName === 'quality') loadQualityPage();
  if (pageName === 'reports') loadReportsPage();
}

// Filters
function initializeFilters() {
  loadProductionLinesForFilter();
}

async function loadProductionLinesForFilter() {
  try {
    const lines = await getProductionLines();
    const lineFilter = document.getElementById('lineFilter');
    lines.forEach(line => {
      const option = document.createElement('option');
      option.value = line.id;
      option.textContent = line.name;
      lineFilter.appendChild(option);
    });
  } catch (error) {
    console.error('Failed to load lines', error);
  }
}

function initializeEventListeners() {
  // Filter apply
  document.getElementById('applyFilters').addEventListener('click', loadDashboardData);
  
  // Export buttons
  document.getElementById('exportExcel').addEventListener('click', () => {
    exportData('excel', getFilterParams());
  });
  
  document.getElementById('exportPDF').addEventListener('click', () => {
    exportData('pdf', getFilterParams());
  });
  
  // Refresh button
  document.querySelector('.btn-icon').addEventListener('click', loadDashboardData);
  
  // Upload area
  const uploadArea = document.getElementById('uploadArea');
  const fileInput = document.getElementById('fileInput');
  
  uploadArea.addEventListener('click', () => fileInput.click());
  uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.style.borderColor = '#0ea5e9';
  });
  uploadArea.addEventListener('dragleave', () => {
    uploadArea.style.borderColor = 'rgba(203, 213, 225, 0.1)';
  });
  uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.style.borderColor = 'rgba(203, 213, 225, 0.1)';
    const files = e.dataTransfer.files;
    if (files.length) handleFileUpload(files[0]);
  });
  
  fileInput.addEventListener('change', (e) => {
    if (e.target.files.length) handleFileUpload(e.target.files[0]);
  });
}

function getFilterParams() {
  return {
    line_id: document.getElementById('lineFilter').value || null,
    shift: document.getElementById('shiftFilter').value || null,
    date_from: document.getElementById('dateFrom').value || null,
    date_to: document.getElementById('dateTo').value || null
  };
}

// Dashboard Data Loading
async function loadDashboardData() {
  try {
    const filters = getFilterParams();
    
    // Get KPI summary
    const summary = await getKPISummary(filters.line_id, 14);
    updateKPICards(summary);
    updateMetrics(summary);
    
    // Get trend data
    const trend = await getTrendData(filters.line_id, 14);
    updateOEETrendChart(trend);
    
    // Get shift records
    const records = await getShiftRecords(filters);
    updateShiftTable(records);
    
    // Get line performance
    const lines = await getProductionLines();
    updateLinePerformanceChart(records, lines);
    
    // Get defects
    const defects = await getDefectData(filters.line_id, 14);
    updateDefectChart(defects);
  } catch (error) {
    console.error('Failed to load dashboard data', error);
    showToast('Failed to load dashboard data', 'error');
  }
}

// Update KPI Cards
function updateKPICards(data) {
  document.getElementById('kpiAvailability').textContent = formatPercent(data.availability);
  document.getElementById('kpiPerformance').textContent = formatPercent(data.performance);
  document.getElementById('kpiQuality').textContent = formatPercent(data.quality);
  document.getElementById('kpiOEE').textContent = formatPercent(data.oee);
}

// Update Metrics
function updateMetrics(data) {
  document.getElementById('metricGoodUnits').textContent = formatNumber(data.good_units);
  document.getElementById('metricTotalUnits').textContent = formatNumber(data.total_units);
  // Add more metrics as needed
}

// Update OEE Trend Chart
function updateOEETrendChart(data) {
  const ctx = document.getElementById('oeeTrendChart');
  
  if (chartInstances.oeeTrend) {
    chartInstances.oeeTrend.destroy();
  }
  
  const labels = data.map(d => formatDate(d.date));
  const values = data.map(d => d.oee);
  
  chartInstances.oeeTrend = new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
        label: 'OEE %',
        data: values,
        borderColor: '#0ea5e9',
        backgroundColor: 'rgba(14, 165, 233, 0.1)',
        fill: true,
        tension: 0.4,
        borderWidth: 2,
        pointRadius: 4,
        pointBackgroundColor: '#0ea5e9',
        pointBorderColor: '#fff'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false }
      },
      scales: {
        y: {
          beginAtZero: true,
          max: 100,
          grid: { color: 'rgba(203, 213, 225, 0.1)' },
          ticks: { color: '#a0aec0' }
        },
        x: {
          grid: { display: false },
          ticks: { color: '#a0aec0' }
        }
      }
    }
  });
}

// Update Line Performance Chart
function updateLinePerformanceChart(records, lines) {
  const ctx = document.getElementById('linePerformanceChart');
  
  if (chartInstances.linePerformance) {
    chartInstances.linePerformance.destroy();
  }
  
  // Group by line
  const lineData = {};
  lines.forEach(line => {
    lineData[line.name] = [];
  });
  
  records.forEach(record => {
    if (lineData[record.line_name]) {
      lineData[record.line_name].push(record.oee);
    }
  });
  
  const labels = Object.keys(lineData);
  const values = labels.map(line => {
    const avg = lineData[line].length > 0
      ? lineData[line].reduce((a, b) => a + b) / lineData[line].length
      : 0;
    return parseFloat(avg.toFixed(2));
  });
  
  const colors = ['#0ea5e9', '#10b981', '#8b5cf6', '#f97316'];
  
  chartInstances.linePerformance = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: 'Average OEE %',
        data: values,
        backgroundColor: colors.slice(0, labels.length),
        borderRadius: 8
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false }
      },
      scales: {
        y: {
          beginAtZero: true,
          max: 100,
          grid: { color: 'rgba(203, 213, 225, 0.1)' },
          ticks: { color: '#a0aec0' }
        },
        x: {
          grid: { display: false },
          ticks: { color: '#a0aec0' }
        }
      }
    }
  });
}

// Update Defect Chart
function updateDefectChart(data) {
  const ctx = document.getElementById('defectChart');
  
  if (chartInstances.defect) {
    chartInstances.defect.destroy();
  }
  
  const labels = Object.keys(data);
  const values = Object.values(data);
  const colors = ['#0ea5e9', '#10b981', '#8b5cf6', '#f97316', '#ef4444'];
  
  chartInstances.defect = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: labels,
      datasets: [{
        data: values,
        backgroundColor: colors.slice(0, labels.length),
        borderColor: '#1a2640',
        borderWidth: 2
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: '60%',
      plugins: {
        legend: {
          position: 'bottom',
          labels: { color: '#a0aec0' }
        }
      }
    }
  });
}

// Update Shift Table
function updateShiftTable(records) {
  const tbody = document.querySelector('#shiftTable tbody');
  tbody.innerHTML = '';
  
  records.forEach(record => {
    const row = document.createElement('tr');
    const statusClass = record.oee >= 80 ? 'good' : record.oee >= 65 ? 'warn' : 'bad';
    
    row.innerHTML = `
      <td>${record.date}</td>
      <td>${record.line_name}</td>
      <td>${record.shift}</td>
      <td>${formatPercent(record.availability)}</td>
      <td>${formatPercent(record.performance)}</td>
      <td>${formatPercent(record.quality)}</td>
      <td><span style="background: ${statusClass === 'good' ? 'rgba(16, 185, 129, 0.2)' : statusClass === 'warn' ? 'rgba(249, 115, 22, 0.2)' : 'rgba(239, 68, 68, 0.2)'}; color: ${statusClass === 'good' ? '#10b981' : statusClass === 'warn' ? '#f97316' : '#ef4444'}; padding: 4px 8px; border-radius: 4px;">${formatPercent(record.oee)}</span></td>
      <td>${formatNumber(record.good_units)}</td>
    `;
    tbody.appendChild(row);
  });
}

// File Upload Handler
async function handleFileUpload(file) {
  try {
    showToast('Uploading file...', 'info');
    const result = await uploadFile(file, 'production-data');
    
    if (result.success) {
      showToast(`Imported ${result.records_imported} records successfully`, 'success');
      if (result.errors.length > 0) {
        console.warn('Upload errors:', result.errors);
      }
      loadDashboardData();
    } else {
      showToast(`Upload error: ${result.error}`, 'error');
    }
  } catch (error) {
    showToast('File upload failed', 'error');
    console.error('Upload error', error);
  }
}

// Production Page
function loadProductionPage() {
  // Implement production page logic
}

// Quality Page
function loadQualityPage() {
  // Implement quality page logic
}

// Reports Page
function loadReportsPage() {
  // Implement reports page logic
}
