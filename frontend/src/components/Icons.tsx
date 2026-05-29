"use client";

import type { SVGProps } from "react";

type IconProps = SVGProps<SVGSVGElement>;

const base: IconProps = {
  viewBox: "0 0 24 24",
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 1.8,
  strokeLinecap: "round",
  strokeLinejoin: "round",
};

export const Ico = {
  translate: (p: IconProps) => (
    <svg {...base} {...p}><path d="M4 5h7M9 3v2c0 4-2 7-5 8M5 9c0 2.5 2.5 4.5 5 5"/><path d="M13 19l4-9 4 9M14.5 16h5"/></svg>
  ),
  queue: (p: IconProps) => (
    <svg {...base} {...p}><path d="M8 6h13M8 12h13M8 18h13"/><circle cx="3.5" cy="6" r="1.3"/><circle cx="3.5" cy="12" r="1.3"/><circle cx="3.5" cy="18" r="1.3"/></svg>
  ),
  bolt: (p: IconProps) => (
    <svg {...base} {...p}><path d="M13 2L4 14h7l-1 8 9-12h-7l1-8z"/></svg>
  ),
  arrowR: (p: IconProps) => (
    <svg {...base} strokeWidth={2} {...p}><path d="M5 12h14M13 6l6 6-6 6"/></svg>
  ),
  copy: (p: IconProps) => (
    <svg {...base} {...p}><rect x="9" y="9" width="11" height="11" rx="2"/><path d="M5 15V5a2 2 0 012-2h10"/></svg>
  ),
  check: (p: IconProps) => (
    <svg {...base} strokeWidth={2.2} {...p}><path d="M20 6L9 17l-5-5"/></svg>
  ),
  flag: (p: IconProps) => (
    <svg {...base} {...p}><path d="M4 21V4M4 4h13l-2 4 2 4H4"/></svg>
  ),
  x: (p: IconProps) => (
    <svg {...base} strokeWidth={2} {...p}><path d="M6 6l12 12M18 6L6 18"/></svg>
  ),
  scan: (p: IconProps) => (
    <svg {...base} {...p}><path d="M4 8V5a1 1 0 011-1h3M16 4h3a1 1 0 011 1v3M20 16v3a1 1 0 01-1 1h-3M8 20H5a1 1 0 01-1-1v-3M4 12h16"/></svg>
  ),
  brain: (p: IconProps) => (
    <svg {...base} strokeWidth={1.6} {...p}><path d="M9 3a3 3 0 00-3 3 3 3 0 00-2 4 3 3 0 001 4 3 3 0 003 4 3 3 0 003-1V3.5A2.5 2.5 0 009 3zM15 3a3 3 0 013 3 3 3 0 012 4 3 3 0 01-1 4 3 3 0 01-3 4 3 3 0 01-3-1"/></svg>
  ),
  pulse: (p: IconProps) => (
    <svg {...base} {...p}><path d="M2 12h4l2 7 4-16 3 9 2-2h5"/></svg>
  ),
  gauge: (p: IconProps) => (
    <svg {...base} {...p}><path d="M5 18a8 8 0 1114 0"/><path d="M12 14l4-3"/></svg>
  ),
  tag: (p: IconProps) => (
    <svg {...base} {...p}><path d="M3 7v5l8 8 8-8-8-8H6a3 3 0 00-3 3z"/><circle cx="8" cy="9" r="1"/></svg>
  ),
  alert: (p: IconProps) => (
    <svg {...base} {...p}><path d="M12 9v4M12 17h.01"/><path d="M10.3 3.9L2.4 18a2 2 0 001.7 3h15.8a2 2 0 001.7-3L13.7 3.9a2 2 0 00-3.4 0z"/></svg>
  ),
  cpu: (p: IconProps) => (
    <svg {...base} {...p}><rect x="7" y="7" width="10" height="10" rx="2"/><path d="M9 3v2M15 3v2M9 19v2M15 19v2M3 9h2M3 15h2M19 9h2M19 15h2"/></svg>
  ),
  msg: (p: IconProps) => (
    <svg {...base} {...p}><path d="M21 15a2 2 0 01-2 2H8l-4 4V5a2 2 0 012-2h13a2 2 0 012 2z"/></svg>
  ),
  edit: (p: IconProps) => (
    <svg {...base} {...p}><path d="M12 20h9M16.5 3.5a2 2 0 013 3L7 19l-4 1 1-4 12.5-12.5z"/></svg>
  ),
  spark: (p: IconProps) => (
    <svg {...base} strokeWidth={1.6} {...p}><path d="M12 3v4M12 17v4M3 12h4M17 12h4M6 6l2 2M16 16l2 2M18 6l-2 2M8 16l-2 2"/></svg>
  ),
};
