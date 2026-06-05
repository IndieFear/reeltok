"use client";

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import type { TemplateInfo } from "@/lib/api";

interface TemplateSelectorProps {
  templates: TemplateInfo[];
  value: string;
  onValueChange: (value: string) => void;
  label?: string;
}

export function TemplateSelector({
  templates,
  value,
  onValueChange,
  label = "Template",
}: TemplateSelectorProps) {
  return (
    <div className="space-y-2">
      <Label>{label}</Label>
      <Select value={value} onValueChange={onValueChange}>
        <SelectTrigger className="border-stone-200 bg-stone-50 focus:ring-stone-900">
          <SelectValue placeholder="Choisir un template" />
        </SelectTrigger>
        <SelectContent>
          {templates.map((t) => (
            <SelectItem key={t.id} value={t.id}>
              {t.name}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
}
