import React, { useEffect, useState, useRef, useMemo } from 'react';
import './ComponentStyles.css';

/**
 * Computes live stats (current, min, max, avg) from a data array.
 */
function useStats(data) {
  return useMemo(() => {
    if (!data || data.length === 0) return null;
    const current = data[data.length - 1];
    const min = Math.min(...data);
    const max = Math.max(...data);
    const avg = data.reduce((a, b) => a + b, 0) / data.length;
    return { current, min, max, avg };
  }, [data]);
}

/**
 * Determines a health status string from value and optional thresholds.
 */
function getStatus(value, warnLow, warnHigh, critLow, critHigh) {
  if (value === undefined || value === null) return 'unknown';
  if ((critLow !== undefined && value < critLow) || (critHigh !== undefined && value > critHigh)) return 'critical';
  if ((warnLow !== undefined && value < warnLow) || (warnHigh !== undefined && value > warnHigh)) return 'warning';
  return 'ok';
}

/**
 * LineChart component rendering a clean vector plot with adjacent stats readout.
 */
const LineChart = ({ data, label, unit, warnLow, warnHigh, critLow, critHigh }) => {
  const canvasRef = useRef(null);
  const stats = useStats(data);
  const status = stats ? getStatus(stats.current, warnLow, warnHigh, critLow, critHigh) : 'unknown';

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const w = canvas.width = 340;
    const h = canvas.height = 160;
    ctx.clearRect(0, 0, w, h);

    // Grid lines
    ctx.strokeStyle = 'rgba(59, 130, 246, 0.06)';
    ctx.lineWidth = 1;
    for (let x = 0; x < w; x += 40) {
      ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, h); ctx.stroke();
    }
    for (let y = 0; y < h; y += 30) {
      ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(w, y); ctx.stroke();
    }

    if (data && data.length > 1) {
      const max = Math.max(...data);
      const min = Math.min(...data);
      const range = max - min || 1;

      const points = data.map((v, i) => {
        const x = (i / (data.length - 1)) * (w - 30) + 15;
        const y = h - 25 - ((v - min) / range) * (h - 50);
        return { x, y, val: v };
      });

      // Area fill
      ctx.save();
      const fillGrad = ctx.createLinearGradient(0, 0, 0, h);
      fillGrad.addColorStop(0, 'rgba(59, 130, 246, 0.12)');
      fillGrad.addColorStop(1, 'rgba(20, 184, 166, 0)');
      ctx.fillStyle = fillGrad;
      ctx.beginPath();
      ctx.moveTo(points[0].x, h);
      points.forEach(p => ctx.lineTo(p.x, p.y));
      ctx.lineTo(points[points.length - 1].x, h);
      ctx.closePath();
      ctx.fill();
      ctx.restore();

      // Stroke line
      ctx.save();
      ctx.strokeStyle = '#3b82f6';
      ctx.lineWidth = 2;
      ctx.lineJoin = 'round';
      ctx.beginPath();
      points.forEach((p, i) => {
        if (i === 0) ctx.moveTo(p.x, p.y);
        else ctx.lineTo(p.x, p.y);
      });
      ctx.stroke();
      ctx.restore();

      // Data dots
      points.forEach(p => {
        ctx.save();
        ctx.fillStyle = '#f1f5f9';
        ctx.strokeStyle = '#3b82f6';
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        ctx.arc(p.x, p.y, 2.5, 0, Math.PI * 2);
        ctx.fill();
        ctx.stroke();
        ctx.restore();
      });

      // Latest value label
      ctx.fillStyle = '#94a3b8';
      ctx.font = '600 11px "JetBrains Mono", monospace';
      ctx.textAlign = 'right';
      ctx.fillText(data[data.length - 1].toFixed(2), w - 15, 18);
    }
  }, [data]);

  const statusClass = status === 'ok' ? 'status-ok' : status === 'warning' ? 'status-warning' : 'status-critical';

  return (
    <div className="chart-card glass">
      <div className="chart-canvas-wrapper">
        <h4>{label}</h4>
        <div className="chart-canvas-container">
          <canvas ref={canvasRef} style={{ width: '100%', height: 'auto', display: 'block' }} />
        </div>
      </div>
      {stats && (
        <div className="chart-stats-readout">
          <div className="stat-row">
            <span className="stat-label">Current</span>
            <span className="stat-value">{stats.current.toFixed(2)} {unit}</span>
          </div>
          <div className="stat-row">
            <span className="stat-label">Min</span>
            <span className="stat-value">{stats.min.toFixed(2)} {unit}</span>
          </div>
          <div className="stat-row">
            <span className="stat-label">Max</span>
            <span className="stat-value">{stats.max.toFixed(2)} {unit}</span>
          </div>
          <div className="stat-row">
            <span className="stat-label">Avg</span>
            <span className="stat-value">{stats.avg.toFixed(2)} {unit}</span>
          </div>
          <div className="stat-row">
            <span className="stat-label">Status</span>
            <span className={`stat-value ${statusClass}`}>{status.toUpperCase()}</span>
          </div>
        </div>
      )}
    </div>
  );
};

const TelemetryTab = ({ stats }) => {
  // Simulated telemetry queues
  const [tempData, setTempData] = useState([24.2, 24.5, 24.3, 24.7, 24.8, 25.1, 24.9]);
  const [pressData, setPressData] = useState([101.3, 101.4, 101.2, 101.5, 101.6, 101.5, 101.7]);
  const [xData, setXData] = useState([0.15, 0.18, 0.22, 0.17, 0.12, 0.08, 0.11]);
  const [yData, setYData] = useState([-0.05, -0.07, -0.04, -0.02, 0.01, 0.03, 0.00]);
  const [zData, setZData] = useState([9.81, 9.80, 9.82, 9.79, 9.81, 9.83, 9.82]);

  // Update simulated data periodically
  useEffect(() => {
    const interval = setInterval(() => {
      const shiftAndAppend = (arr, maxVariance) => {
        const lastVal = arr[arr.length - 1];
        const nextVal = lastVal + (Math.random() - 0.5) * maxVariance;
        return [...arr.slice(1), nextVal];
      };
      setTempData(prev => shiftAndAppend(prev, 0.6));
      setPressData(prev => shiftAndAppend(prev, 0.3));
      setXData(prev => shiftAndAppend(prev, 0.1));
      setYData(prev => shiftAndAppend(prev, 0.1));
      setZData(prev => shiftAndAppend(prev, 0.05));
    }, 1500);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="telemetry-tab">
      <div className="charts-grid">
        <LineChart data={tempData} label="Core Temp" unit="°C" warnHigh={30} critHigh={40} />
        <LineChart data={pressData} label="Pressure" unit="kPa" warnLow={100} warnHigh={103} critLow={98} critHigh={105} />
        <LineChart data={xData} label="Orientation X (pitch)" unit="°" />
        <LineChart data={yData} label="Orientation Y (roll)" unit="°" />
        <LineChart data={zData} label="Orientation Z (yaw)" unit="°" />
      </div>
    </div>
  );
};

export default TelemetryTab;
