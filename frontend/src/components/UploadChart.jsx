import React, { useRef } from "react";

const ACCEPT = "image/png,image/jpeg,image/webp";
const MAX_BYTES = 8 * 1024 * 1024;

export default function UploadChart({ file, preview, onFile }) {
  const inputRef = useRef(null);

  const pick = () => inputRef.current?.click();

  const handle = (f) => {
    if (!f) return;
    if (!ACCEPT.split(",").includes(f.type)) {
      alert("Please upload a PNG, JPG, or WebP image.");
      return;
    }
    if (f.size > MAX_BYTES) {
      alert("Image too large (max 8 MB).");
      return;
    }
    const reader = new FileReader();
    reader.onload = () => onFile(f, reader.result);
    reader.readAsDataURL(f);
  };

  return (
    <div>
      <input
        ref={inputRef}
        type="file"
        accept={ACCEPT}
        className="hidden"
        onChange={(e) => handle(e.target.files?.[0])}
      />
      <div
        onClick={pick}
        onDragOver={(e) => e.preventDefault()}
        onDrop={(e) => {
          e.preventDefault();
          handle(e.dataTransfer.files?.[0]);
        }}
        className="cursor-pointer border-2 border-dashed border-line rounded-lg p-4 hover:border-emerald-400 transition"
      >
        {preview ? (
          <div className="space-y-2">
            <img
              src={preview}
              alt="Chart preview"
              className="rounded-md max-h-64 w-full object-contain bg-black/30"
            />
            <p className="text-xs text-slate-400 truncate">
              {file?.name} · {(file?.size / 1024).toFixed(1)} KB · click to change
            </p>
          </div>
        ) : (
          <div className="text-center text-sm text-slate-400 py-10">
            <p className="font-medium text-slate-200">Drop screenshot here</p>
            <p className="mt-1">or click to choose a file (PNG, JPG, WebP, max 8 MB)</p>
          </div>
        )}
      </div>
    </div>
  );
}
