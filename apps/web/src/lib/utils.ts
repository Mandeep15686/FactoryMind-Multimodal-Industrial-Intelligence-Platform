import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export const severityColor: Record<string, string> = {
  CRITICAL: "text-red",
  MAJOR: "text-orange",
  MINOR: "text-yellow",
  NONE: "text-teal",
};

export const healthColor: Record<string, string> = {
  HEALTHY: "text-teal",
  DEGRADED: "text-yellow",
  CRITICAL: "text-red",
};
