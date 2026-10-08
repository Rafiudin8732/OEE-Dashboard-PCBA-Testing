// Utility functions for the dashboard

const API_BASE = '/api';

// Format percentage
function formatPercent(value) {
  return `${parseFloat(value).toFixed(1)}%`;
}

// Format number with commas
function formatNumber(value) {
  return parseInt(value).toLocaleString();
}

// Format hours from minutes
function formatHours(minutes) {
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  return `${hours}h ${mins}m`;
}

// Parse date
function parseDate(dateStr) {
  return new Date(dateStr);
}

// Format date
function formatDate(dateObj) {
  if (typeof dateObj === 'string') {
    dateObj = new Date(dateObj);
  }
  return dateObj.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  });
}

// API Calls
async function apiCall(endpoint, method = 'GET', data = null) {
  const options = {
    method: method,
    headers: {
      'Content-Type': 'application/json'
    }
  };
  
  if (data) {
    options.body = JSON.stringify(data);
  }
  
  try {
    const response = await fetch(`${API_BASE}${endpoint}`, options);
    if (!response.ok) throw new Error(`API Error: ${response.statusText}`);
    return await response.json();
  } catch (error) {
    console.error(`API Call Failed: ${endpoint}`, error);
    throw error;
  }
}

// Get KPI summary
async function getKPISummary(lineId = null, days = 14) {
  let endpoint = `/kpi-summary?days=${days}`;
  if (lineId) endpoint += `&line_id=${lineId}`;
  return apiCall(endpoint);
}

// Get trend data
async function getTrendData(lineId = null, days = 14) {
  let endpoint = `/trend?days=${days}`;
  if (lineId) endpoint += `&line_id=${lineId}`;
  return apiCall(endpoint);
}

// Get shift records
async function getShiftRecords(filters = {}) {
  let endpoint = '/shift-records';
  const params = new URLSearchParams();
  if (filters.line_id) params.append('line_id', filters.line_id);
  if (filters.shift) params.append('shift', filters.shift);
  if (filters.date_from) params.append('date_from', filters.date_from);
  if (filters.date_to) params.append('date_to', filters.date_to);
  if (params.toString()) endpoint += '?' + params.toString();
  return apiCall(endpoint);
}

// Get production lines
async function getProductionLines() {
  return apiCall('/lines');
}

// Get defect data
async function getDefectData(lineId = null, days = 14) {
  let endpoint = `/defects?days=${days}`;
  if (lineId) endpoint += `&line_id=${lineId}`;
  return apiCall(endpoint);
}

// Get live data
async function getLiveData(lineId = null) {
  let endpoint = '/live-data';
  if (lineId) endpoint += `?line_id=${lineId}`;
  return apiCall(endpoint);
}

// Upload file
async function uploadFile(file, fileType = 'production-data') {
  const formData = new FormData();
  formData.append('file', file);
  
  try {
    const response = await fetch(`${API_BASE}/upload/${fileType}`, {
      method: 'POST',
      body: formData
    });
    if (!response.ok) throw new Error(`Upload Error: ${response.statusText}`);
    return await response.json();
  } catch (error) {
    console.error('Upload Failed', error);
    throw error;
  }
}

// Export data
async function exportData(format = 'excel', filters = {}) {
  try {
    const response = await fetch(`${API_BASE}/export/${format}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(filters)
    });
    if (!response.ok) throw new Error(`Export Error: ${response.statusText}`);
    
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `oee-report-${new Date().toISOString().slice(0,10)}.${format === 'excel' ? 'xlsx' : format}`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  } catch (error) {
    console.error('Export Failed', error);
    throw error;
  }
}

// Show toast notification
function showToast(message, type = 'info', duration = 3000) {
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.textContent = message;
  toast.style.cssText = `
    position: fixed;
    bottom: 20px;
    right: 20px;
    padding: 16px 24px;
    border-radius: 8px;
    background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#0ea5e9'};
    color: white;
    z-index: 9999;
    box-shadow: 0 8px 24px rgba(0,0,0,0.3);
    font-weight: 500;
  `;
  document.body.appendChild(toast);
  setTimeout(() => {
    toast.remove();
  }, duration);
}

// Debounce function
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}
