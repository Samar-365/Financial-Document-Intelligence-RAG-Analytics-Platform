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
        `Invalid file type (${ext}). Please upload a PDF, Excel (.xlsx/.xls), or CSV filing.`
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
    <div className="space-y-4">
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
            "group relative flex flex-col items-center justify-center border-2 border-black p-10 sm:p-14 text-center transition-all cursor-pointer bg-white",
            isDragging
              ? "bg-zinc-100 shadow-[6px_6px_0px_#FF0000]"
              : "hover:shadow-[6px_6px_0px_#000000]",
            disabled && "opacity-50 pointer-events-none"
          )}
        >
          <div className="flex h-14 w-14 items-center justify-center border-2 border-black bg-black text-white mb-4 group-hover:scale-105 transition-transform shadow-[3px_3px_0px_#FF0000]">
            <FolderUp className="h-7 w-7 text-white" />
          </div>

          <div className="space-y-2 max-w-md">
            <h3 className="text-xl sm:text-2xl font-black uppercase tracking-tight text-black">
              DRAG &amp; DROP FILING <span className="stroke-text-thick">HERE</span>
            </h3>
            <p className="text-xs font-mono text-zinc-600 uppercase">
              OR CLICK TO BROWSE LOCAL FILESYSTEM
            </p>
          </div>

          <div className="mt-6 flex flex-wrap items-center justify-center gap-2">
            {["PDF (ANNUAL REPORTS & 10-K)", "EXCEL (.XLSX)", "CSV DATASETS"].map((tag) => (
              <span
                key={tag}
                className="border border-black bg-white px-2 py-1 text-[10px] font-mono font-bold uppercase tracking-wider text-black shadow-[1px_1px_0px_#000000]"
              >
                {tag}
              </span>
            ))}
          </div>

          <div className="mt-4 text-[10px] font-mono text-zinc-500 uppercase tracking-widest">
            [ MAX INGESTION CAPACITY: 50 MB / DOCUMENT ]
          </div>
        </div>
      ) : (
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between border-2 border-black bg-white p-5 shadow-[4px_4px_0px_#000000] gap-4">
          <div className="flex items-center gap-4">
            <div className="flex h-12 w-12 items-center justify-center border border-black bg-black text-white shrink-0">
              <FileText className="h-6 w-6 text-[#FF0000]" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-sm font-black uppercase tracking-tight text-black truncate max-w-[260px] sm:max-w-md">
                  {selectedFile.name}
                </span>
                <span className="border border-black bg-black text-white px-1.5 py-0.5 text-[9px] font-mono font-bold uppercase">
                  READY
                </span>
              </div>
              <div className="flex items-center gap-3 text-xs font-mono text-zinc-600 mt-1">
                <span>SIZE: {formatBytes(selectedFile.size)}</span>
                <span>•</span>
                <span>TYPE: {selectedFile.name.split(".").pop()?.toUpperCase()}</span>
              </div>
            </div>
          </div>

          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={() => onFileSelect(null)}
            disabled={disabled}
            className="border border-black bg-white hover:bg-[#FF0000] hover:text-white rounded-none font-black uppercase tracking-wider text-xs gap-1.5 shadow-[2px_2px_0px_#000000]"
          >
            <X className="h-4 w-4" />
            <span>REMOVE</span>
          </Button>
        </div>
      )}

      {errorMessage && (
        <div className="flex items-center gap-2 border border-black bg-[#FF0000] text-white p-3 text-xs font-mono uppercase tracking-wider shadow-[3px_3px_0px_#000000]">
          <AlertCircle className="h-4 w-4 shrink-0 text-white" />
          <span>{errorMessage}</span>
        </div>
      )}
    </div>
  );
}
