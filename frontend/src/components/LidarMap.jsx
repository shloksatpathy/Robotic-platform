import React, { useEffect, useRef } from 'react';
import './ComponentStyles.css';

/**
 * LidarMap component – renders an active, real-time 2D radar sweeping simulation.
 */
export default function LidarMap() {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let animationId;
    let angle = 0;
    
    // Dynamic simulated points (targets / obstacles)
    const targets = [
      { angle: 0.5, dist: 0.45, size: 5, intensity: 0, speed: 0.001 },
      { angle: 1.8, dist: 0.7, size: 6, intensity: 0, speed: -0.0008 },
      { angle: 3.4, dist: 0.35, size: 4, intensity: 0, speed: 0.0015 },
      { angle: 4.5, dist: 0.8, size: 5, intensity: 0, speed: -0.0012 },
      { angle: 5.6, dist: 0.6, size: 6, intensity: 0, speed: 0.0005 }
    ];

    const resizeCanvas = () => {
      if (!canvas) return;
      const parent = canvas.parentElement;
      if (parent) {
        const rect = parent.getBoundingClientRect();
        canvas.width = rect.width || 400;
        canvas.height = rect.height || 300;
      } else {
        canvas.width = 400;
        canvas.height = 300;
      }
    };
    
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    const render = () => {
      const w = canvas.width;
      const h = canvas.height;
      const cx = w / 2;
      const cy = h / 2;
      const maxRadius = Math.min(w, h) / 2 - 25;

      if (w <= 0 || h <= 0 || maxRadius <= 0) {
        animationId = requestAnimationFrame(render);
        return;
      }

      // Dark futuristic radar background
      ctx.fillStyle = '#060814';
      ctx.fillRect(0, 0, w, h);

      // Draw radar grids (concentric circles)
      ctx.strokeStyle = 'rgba(0, 240, 255, 0.08)';
      ctx.lineWidth = 1;
      for (let r = maxRadius / 4; r <= maxRadius; r += maxRadius / 4) {
        ctx.beginPath();
        ctx.arc(cx, cy, r, 0, Math.PI * 2);
        ctx.stroke();
      }

      // Draw crosshairs
      ctx.beginPath();
      ctx.moveTo(cx - maxRadius, cy);
      ctx.lineTo(cx + maxRadius, cy);
      ctx.moveTo(cx, cy - maxRadius);
      ctx.lineTo(cx, cy + maxRadius);
      ctx.stroke();

      // Draw angle labels
      ctx.fillStyle = 'rgba(0, 240, 255, 0.4)';
      ctx.font = '9px monospace';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText("000°", cx, cy - maxRadius - 12);
      ctx.fillText("090°", cx + maxRadius + 16, cy);
      ctx.fillText("180°", cx, cy + maxRadius + 12);
      ctx.fillText("270°", cx - maxRadius - 16, cy);

      // Update sweep angle (clockwise radar sweep)
      angle = (angle + 0.02) % (Math.PI * 2);

      // Draw sweep radar beam gradient
      ctx.save();
      ctx.translate(cx, cy);
      ctx.rotate(angle);
      
      const sweepTailAngle = 0.5; // width of tail in radians
      const tailGrad = ctx.createRadialGradient(0, 0, 0, 0, 0, maxRadius);
      tailGrad.addColorStop(0, 'rgba(0, 240, 255, 0.15)');
      tailGrad.addColorStop(1, 'rgba(0, 240, 255, 0)');
      
      ctx.fillStyle = tailGrad;
      ctx.beginPath();
      ctx.moveTo(0, 0);
      ctx.arc(0, 0, maxRadius, -sweepTailAngle, 0);
      ctx.closePath();
      ctx.fill();

      // Main sweep line
      ctx.strokeStyle = '#00f0ff';
      ctx.lineWidth = 2;
      ctx.shadowColor = '#00f0ff';
      ctx.shadowBlur = 10;
      ctx.beginPath();
      ctx.moveTo(0, 0);
      ctx.lineTo(maxRadius, 0);
      ctx.stroke();
      ctx.restore();

      // Draw target/obstacle particles
      targets.forEach(target => {
        // Move targets dynamically to simulate active environment
        target.angle = (target.angle + target.speed + Math.PI * 2) % (Math.PI * 2);

        // Detect sweep line crossing target
        const diff = Math.abs(angle - target.angle);
        if (diff < 0.06) {
          target.intensity = 1.0;
        } else {
          // Slow fade out
          target.intensity = Math.max(0.15, target.intensity - 0.006);
        }

        const tx = cx + Math.cos(target.angle) * target.dist * maxRadius;
        const ty = cy + Math.sin(target.angle) * target.dist * maxRadius;

        // Glowing particle
        ctx.save();
        ctx.shadowColor = '#00f0ff';
        ctx.shadowBlur = 12 * target.intensity;
        ctx.fillStyle = `rgba(0, 240, 255, ${target.intensity})`;
        ctx.beginPath();
        ctx.arc(tx, ty, target.size, 0, Math.PI * 2);
        ctx.fill();

        // Target marker expanding rings
        if (target.intensity > 0.6) {
          ctx.strokeStyle = `rgba(0, 240, 255, ${target.intensity - 0.5})`;
          ctx.lineWidth = 1;
          ctx.beginPath();
          ctx.arc(tx, ty, target.size + 6 + (1 - target.intensity) * 12, 0, Math.PI * 2);
          ctx.stroke();
        }
        ctx.restore();
      });

      // HUD text overlays
      ctx.fillStyle = 'rgba(0, 240, 255, 0.7)';
      ctx.shadowBlur = 0;
      ctx.font = '10px monospace';
      ctx.textAlign = 'left';
      ctx.fillText("RANGE: 100m", 15, 20);
      ctx.fillText("FREQ: 10Hz", 15, 34);
      ctx.fillText("SWEEP: SECURE", 15, 48);

      animationId = requestAnimationFrame(render);
    };

    render();

    return () => {
      window.removeEventListener('resize', resizeCanvas);
      cancelAnimationFrame(animationId);
    };
  }, []);

  return (
    <div className="lidar-map glass">
      <div className="lidar-header">
        <h3>LIDAR MAPPING</h3>
        <span className="live-tag">ACTIVE</span>
      </div>
      <div className="lidar-canvas-container">
        <canvas ref={canvasRef} className="lidar-canvas" />
      </div>
    </div>
  );
}
