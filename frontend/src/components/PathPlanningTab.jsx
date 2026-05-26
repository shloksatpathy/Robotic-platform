import React from 'react';
import './PathPlanningTab.css';

/**
 * PathPlanningTab — Placeholder page for future path planning feature.
 * Displays a styled "coming soon" card with planned feature descriptions.
 */
export default function PathPlanningTab() {
  return (
    <div className="pathplanning-tab">
      <div className="pathplanning-card">
        {/* Icon */}
        <div className="pathplanning-icon">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.8"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M12 13V2l8 4-8 4" />
            <path d="M20.561 10.222a9 9 0 1 1-12.55-5.29" />
            <path d="M8.002 16.293a3.5 3.5 0 0 1 6.056-1.862" />
          </svg>
        </div>

        <h2>Path Planning</h2>
        <span className="pathplanning-badge">Coming Soon</span>

        <p className="pathplanning-description">
          Advanced autonomous navigation and path planning capabilities are under development.
          This module will enable real-time waypoint management, obstacle avoidance, and
          route optimization for the Kristellar rover.
        </p>

        {/* Planned features list */}
        <ul className="pathplanning-features">
          <li>
            <span className="pathplanning-feature-dot" />
            Interactive waypoint editor with drag-and-drop
          </li>
          <li>
            <span className="pathplanning-feature-dot" />
            A* and RRT* pathfinding algorithms
          </li>
          <li>
            <span className="pathplanning-feature-dot" />
            Real-time obstacle detection integration
          </li>
          <li>
            <span className="pathplanning-feature-dot" />
            Terrain mapping and cost analysis
          </li>
          <li>
            <span className="pathplanning-feature-dot" />
            Mission planning with checkpoint sequencing
          </li>
        </ul>
      </div>
    </div>
  );
}
