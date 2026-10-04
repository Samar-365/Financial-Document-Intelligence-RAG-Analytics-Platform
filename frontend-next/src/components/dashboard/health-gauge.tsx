"use client";

import React from "react";
import { cn } from "@/lib/utils";

interface HealthGaugeProps {
  score: number; // 0–100
  label?: string;
  size?: number;
  isLoading?: boolean;
}

function getScoreColor(score: number): { stroke: string; text: string; label: string } {
  if (score >= 75) return { stroke: "#10b981", text: "text-emerald-400", label: "Excellent" };
  if (score >= 55) return { stroke: "#3b82f6", text: "text-blue-400", label: "Healthy" };
  if (score >= 40) return { stroke: "#f59e0b", text: "text-amber-400", label: "Moderate" };
  return { stroke: "#ef4444", text: "text-red-400", label: "At Risk" };
}

export function HealthGauge({
  score,
  label = "Financial Health Score",
  size = 200,
  isLoading = false,
}: HealthGaugeProps) {
  const clampedScore = Math.max(0, Math.min(100, score));
  const { stroke, text, label: statusLabel } = getScoreColor(clampedScore);

  const cx = size / 2;
  const cy = size / 2;
  const radius = size * 0.38;
  const strokeWidth = size * 0.065;

  // Arc from -210° to +30° (240° sweep) — bottom-open gauge
  const startAngle = -210;
  const endAngle = 30;
  const totalArc = endAngle - startAngle; // 240 degrees
  const filledArc = (clampedScore / 100) * totalArc;

  function polarToXY(angleDeg: number, r: number) {
    const rad = (angleDeg * Math.PI) / 180;
    return {
      x: cx + r * Math.cos(rad),
      y: cy + r * Math.sin(rad),
    };
  }

  function describeArc(startDeg: number, endDeg: number, r: number) {
    const start = polarToXY(startDeg, r);
    const end = polarToXY(endDeg, r);
    const largeArc = endDeg - startDeg > 180 ? 1 : 0;
    return `M ${start.x} ${start.y} A ${r} ${r} 0 ${largeArc} 1 ${end.x} ${end.y}`;
  }

  // Tick marks
  const ticks = [0, 25, 50, 75, 100];
  const tickRadius = radius + strokeWidth * 0.85;
  const tickLength = strokeWidth * 0.55;

  return (
    <div className="flex flex-col items-center gap-2">
      <div className="relative" style={{ width: size, height: size * 0.78 }}>
        <svg
          width={size}
          height={size * 0.78}
          viewBox={`0 0 ${size} ${size * 0.78}`}
          className="overflow-visible"
        >
          {/* Glow filter */}
          <defs>
            <filter id="gauge-glow" x="-30%" y="-30%" width="160%" height="160%">
              <feGaussianBlur stdDeviation="3" result="blur" />
              <feMerge>
                <feMergeNode in="blur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          </defs>

          {/* Background track */}
          <path
            d={describeArc(startAngle, endAngle, radius)}
            fill="none"
            stroke="rgba(148,163,184,0.12)"
            strokeWidth={strokeWidth}
            strokeLinecap="round"
          />

          {/* Colored fill arc */}
          {!isLoading && clampedScore > 0 && (
            <path
              d={describeArc(startAngle, startAngle + filledArc, radius)}
              fill="none"
              stroke={stroke}
              strokeWidth={strokeWidth}
              strokeLinecap="round"
              filter="url(#gauge-glow)"
              style={{ transition: "all 0.8s ease-out" }}
            />
          )}

          {/* Tick marks */}
          {ticks.map((tick) => {
            const tickAngle = startAngle + (tick / 100) * totalArc;
            const inner = polarToXY(tickAngle, radius - strokeWidth / 2 - tickLength);
            const outer = polarToXY(tickAngle, tickRadius);
            return (
              <line
                key={tick}
                x1={inner.x}
                y1={inner.y}
                x2={outer.x}
                y2={outer.y}
                stroke="rgba(148,163,184,0.3)"
                strokeWidth={1.5}
                strokeLinecap="round"
              />
            );
          })}

          {/* Needle dot */}
          {!isLoading && (
            <>
              {(() => {
                const needleAngle = startAngle + filledArc;
                const np = polarToXY(needleAngle, radius);
                return (
                  <circle
                    cx={np.x}
                    cy={np.y}
                    r={strokeWidth * 0.45}
                    fill="white"
                    filter="url(#gauge-glow)"
                    style={{ transition: "all 0.8s ease-out" }}
                  />
                );
              })()}
            </>
          )}

          {/* Score text */}
          <text
            x={cx}
            y={cy + size * 0.06}
            textAnchor="middle"
            dominantBaseline="middle"
            className={cn("font-bold fill-current", text)}
            style={{
              fontSize: size * 0.2,
              fontWeight: 800,
              fill: isLoading ? "rgba(148,163,184,0.2)" : stroke,
            }}
          >
            {isLoading ? "—" : Math.round(clampedScore)}
          </text>
          <text
            x={cx}
            y={cy + size * 0.22}
            textAnchor="middle"
            style={{
              fontSize: size * 0.072,
              fill: "rgba(148,163,184,0.7)",
              fontWeight: 500,
            }}
          >
            / 100
          </text>

          {/* Status label */}
          {!isLoading && (
            <text
              x={cx}
              y={cy + size * 0.345}
              textAnchor="middle"
              style={{
                fontSize: size * 0.067,
                fill: stroke,
                fontWeight: 700,
                letterSpacing: "0.05em",
                textTransform: "uppercase",
              }}
            >
              {statusLabel}
            </text>
          )}
        </svg>
      </div>

      <p className="text-xs font-medium text-slate-400 tracking-wide uppercase">{label}</p>
    </div>
  );
}
