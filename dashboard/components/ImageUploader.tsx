"use client";

import { useCallback } from "react";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

interface ImageUploaderProps {
  value: File | null;
  onChange: (file: File | null) => void;
  label?: string;
  accept?: string;
}

export function ImageUploader({
  value,
  onChange,
  label = "Image de fond",
  accept = "image/jpeg,image/png,image/webp",
}: ImageUploaderProps) {
  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      onChange(file || null);
    },
    [onChange]
  );

  return (
    <div className="space-y-2">
      <Label>{label}</Label>
      <Input
        type="file"
        accept={accept}
        onChange={handleChange}
        className="cursor-pointer border-stone-200 bg-stone-50 focus-visible:ring-stone-900"
      />
      {value && (
        <p className="text-sm text-stone-500">
          {value.name} ({(value.size / 1024).toFixed(1)} Ko)
        </p>
      )}
    </div>
  );
}
