"use client";

import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Building2, Calendar, Clock, FileSpreadsheet, Loader2, Sparkles } from "lucide-react";

interface MetadataFormProps {
  selectedFile: File | null;
  onSubmit: (metadata: {
    company_name?: string;
    fiscal_year?: number;
    fiscal_period?: string;
  }) => Promise<void>;
  isLoading: boolean;
}

const COMMON_COMPANIES = [
  "Reliance Industries",
  "Tata Consultancy Services",
  "Infosys Ltd",
  "HDFC Bank",
  "Tata Motors",
  "ICICI Bank",
];

export function MetadataForm({
  selectedFile,
  onSubmit,
  isLoading,
}: MetadataFormProps) {
  const [companyName, setCompanyName] = useState("");
  const [fiscalYear, setFiscalYear] = useState<number>(2024);
  const [fiscalPeriod, setFiscalPeriod] = useState("Annual");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) return;

    await onSubmit({
      company_name: companyName.trim() || undefined,
      fiscal_year: fiscalYear || undefined,
      fiscal_period: fiscalPeriod || undefined,
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {/* Company Name */}
        <div className="sm:col-span-1 space-y-1.5">
          <label className="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
            <Building2 className="h-3.5 w-3.5 text-blue-400" />
            Company Name
          </label>
          <Input
            value={companyName}
            onChange={(e) => setCompanyName(e.target.value)}
            placeholder="e.g. Reliance Industries"
            disabled={isLoading}
          />
        </div>

        {/* Fiscal Year */}
        <div className="space-y-1.5">
          <label className="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
            <Calendar className="h-3.5 w-3.5 text-emerald-400" />
            Fiscal Year
          </label>
          <select
            value={fiscalYear}
            onChange={(e) => setFiscalYear(Number(e.target.value))}
            disabled={isLoading}
            className="flex h-10 w-full rounded-lg border border-slate-800 bg-slate-900/80 px-3 py-2 text-sm text-slate-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 transition-all cursor-pointer"
          >
            {[2026, 2025, 2024, 2023, 2022, 2021, 2020].map((yr) => (
              <option key={yr} value={yr}>
                FY{yr}
              </option>
            ))}
          </select>
        </div>

        {/* Fiscal Period */}
        <div className="space-y-1.5">
          <label className="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
            <Clock className="h-3.5 w-3.5 text-indigo-400" />
            Period / Quarter
          </label>
          <select
            value={fiscalPeriod}
            onChange={(e) => setFiscalPeriod(e.target.value)}
            disabled={isLoading}
            className="flex h-10 w-full rounded-lg border border-slate-800 bg-slate-900/80 px-3 py-2 text-sm text-slate-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 transition-all cursor-pointer"
          >
            <option value="Annual">Annual (Full Year)</option>
            <option value="Q1">Q1 (First Quarter)</option>
            <option value="Q2">Q2 (Second Quarter / H1)</option>
            <option value="Q3">Q3 (Third Quarter / 9M)</option>
            <option value="Q4">Q4 (Fourth Quarter)</option>
          </select>
        </div>
      </div>

      {/* Quick Suggestion Chips */}
      <div className="flex flex-wrap items-center gap-1.5 pt-1">
        <span className="text-[11px] text-slate-500 font-medium mr-1">Quick Select:</span>
        {COMMON_COMPANIES.map((name) => (
          <button
            key={name}
            type="button"
            onClick={() => setCompanyName(name)}
            className="text-[11px] px-2 py-0.5 rounded-md border border-slate-800 bg-slate-900/60 text-slate-400 hover:text-white hover:border-slate-700 transition-all"
          >
            {name}
          </button>
        ))}
      </div>

      {/* Action Button */}
      <div className="pt-2 flex justify-end">
        <Button
          type="submit"
          variant="gradient"
          disabled={!selectedFile || isLoading}
          className="gap-2 min-w-[180px]"
        >
          {isLoading ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" />
              <span>Uploading & Processing...</span>
            </>
          ) : (
            <>
              <Sparkles className="h-4 w-4" />
              <span>Ingest & Vectorize Document</span>
            </>
          )}
        </Button>
      </div>
    </form>
  );
}
