"use client";

import { useCallback, useEffect, useState } from "react";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Images } from "lucide-react";

interface ImageUploaderProps {
  value: File | null;
  onChange: (file: File | null) => void;
  label?: string;
  accept?: string;
  previewUrl?: string | null;
  onOpenLibrary?: () => void;
}

export function ImageUploader({
  value,
  onChange,
  label = "Image de fond",
  accept = "image/jpeg,image/png,image/webp",
  previewUrl,
  onOpenLibrary,
}: ImageUploaderProps) {
  const [localPreview, setLocalPreview] = useState<string | null>(null);

  useEffect(() => {
    if (previewUrl) {
      setLocalPreview(previewUrl);
      return;
    }
    if (!value) {
      setLocalPreview(null);
      return;
    }
    const url = URL.createObjectURL(value);
    setLocalPreview(url);
    return () => URL.revokeObjectURL(url);
  }, [value, previewUrl]);

  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      onChange(file || null);
    },
    [onChange],
  );

  return (
    <div className="space-y-2">
      <Label>{label}</Label>
      <div className="flex flex-wrap gap-2">
        <Input
          type="file"
          accept={accept}
          onChange={handleChange}
          className="max-w-xs cursor-pointer border-stone-200 bg-stone-50 focus-visible:ring-stone-900"
        />
        {onOpenLibrary && (
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={onOpenLibrary}
            className="border-stone-200"
          >
            <Images className="h-4 w-4" />
            <span className="ml-1.5">Bibliothèque</span>
          </Button>
        )}
      </div>
      {value && (
        <p className="text-sm text-stone-500">
          {value.name} ({(value.size / 1024).toFixed(1)} Ko)
        </p>
      )}
      {localPreview && (
        <div className="overflow-hidden rounded-xl border border-stone-200 bg-stone-100">
          <div
            className="aspect-[9/16] max-h-48 w-full max-w-[108px] bg-cover bg-center"
            style={{ backgroundImage: `url(${localPreview})` }}
          />
        </div>
      )}
    </div>
  );
}
