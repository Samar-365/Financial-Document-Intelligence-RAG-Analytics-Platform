import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatCurrency(
  value?: number | null,
  currency: "INR" | "USD" = "INR",
  unit: string = "Cr"
): string {
  if (value === undefined || value === null || isNaN(value)) return "—";
  const prefix = currency === "INR" ? "₹" : "$";
  return `${prefix}${value.toLocaleString("en-IN", {
    minimumFractionDigits: 1,
    maximumFractionDigits: 2,
  })} ${unit}`;
}

export function formatPercent(value?: number | null): string {
  if (value === undefined || value === null || isNaN(value)) return "—";
  const sign = value > 0 ? "+" : "";
  return `${sign}${value.toFixed(2)}%`;
}

export function formatBytes(bytes?: number | null): string {
  if (!bytes || bytes <= 0) return "0 B";
  const k = 1024;
  const sizes = ["B", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
}
