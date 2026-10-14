"use client";

import React, { useRef, useState } from "react";
import { FolderUp, FileText, X, AlertCircle, CheckCircle2 } from "lucide-react";
import { formatBytes, cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";

interface UploadDropzoneProps {
  selectedFile: File | null;
  onFileSelect: (file: File | null) => void;
  disabled?: boolean;
}

export function UploadDropzone({
  selectedFile,
  onFileSelect,
  disabled = false,
}: UploadDropzoneProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024; // 50MB
  const ALLOWED_EXTENSIONS = [".pdf", ".xlsx", ".xls", ".csv"];

  const validateAndSetFile = (file: File) => {
    setErrorMessage(null);
    const ext = "." + file.name.split(".").pop()?.toLowerCase();

    if (!ALLOWED_EXTENSIONS.includes(ext)) {
      setErrorMessage(
        `Invalid file type (${ext}). Please upload a PDF, Excel, or CSV document.`
      );
      return;
    }

    if (file.size > MAX_FILE_SIZE_BYTES) {
      setErrorMessage(
        `File size exceeds 50MB limit (${formatBytes(file.size)}).`
      );
      return;
    }

    onFileSelect(file);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    if (!disabled) setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (disabled) return;

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      validateAndSetFile(e.target.files[0]);
    }
  };

  return (
    <div className="space-y-3">
      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf,.xlsx,.xls,.csv"
        className="hidden"
        disabled={disabled}
        onChange={handleFileInputChange}
      />

      {!selectedFile ? (
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => !disabled && fileInputRef.current?.click()}
          className={cn(
            "group relative flex flex-col items-center justify-center rounded-xl border-2 border-dashed p-8 text-center transition-all cursor-pointer",
            isDragging
              ? "border-[#E63946] bg-[rgba(184,29,36,0.18)] scale-[1.01]"
              : "border-[rgba(184,29,36,0.45)] bg-[#111018] hover:border-[#E63946] hover:bg-[#171522]",
            disabled && "opacity-50 pointer-events-none"
          )}
        >
          <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-[rgba(184,29,36,0.18)] text-[#E63946] mb-3 border border-[rgba(196,30,58,0.4)] shadow-[0_0_15px_rgba(184,29,36,0.25)] group-hover:scale-110 transition-transform">
            <FolderUp className="h-7 w-7" />
          </div>
          <h3 className="text-sm font-semibold text-white">
            Click to upload or drag and drop financial reports
          </h3>
          <p className="text-xs text-slate-400 mt-1 max-w-sm">
            Supports Annual Reports, 10-K, 10-Q, and Ind AS statements (.pdf, .xlsx, .csv up to 50MB)
          </p>
        </div>
      ) : (
        <div className="flex items-center justify-between rounded-xl border border-[rgba(196,30,58,0.4)] bg-[rgba(184,29,36,0.12)] p-4">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-[rgba(184,29,36,0.2)] text-[#E63946] border border-[rgba(196,30,58,0.4)]">
              <FileText className="h-5 w-5" />
            </div>
            <div>
              <p className="text-sm font-semibold text-white truncate max-w-[280px] sm:max-w-md">
                {selectedFile.name}
              </p>
              <p className="text-xs text-slate-400">
                {formatBytes(selectedFile.size)} • Ready for ingestion
              </p>
            </div>
          </div>

          <Button
            type="button"
            variant="ghost"
            size="icon"
            onClick={() => onFileSelect(null)}
            disabled={disabled}
            className="text-slate-400 hover:text-[#E63946] hover:bg-[rgba(184,29,36,0.15)]"
            title="Remove file"
          >
            <X className="h-4 w-4" />
          </Button>
        </div>
      )}

      {errorMessage && (
        <div className="flex items-center gap-2 rounded-lg border border-[rgba(230,57,70,0.4)] bg-[rgba(184,29,36,0.15)] p-3 text-xs text-[#FF6B6B]">
          <AlertCircle className="h-4 w-4 shrink-0 text-[#E63946]" />
          <span>{errorMessage}</span>
        </div>
      )}
    </div>
  );
}
