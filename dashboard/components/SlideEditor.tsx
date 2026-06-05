"use client";

import { useCallback, useState } from "react";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { ImageUploader } from "./ImageUploader";
import { TemplateSelector } from "./TemplateSelector";
import { fetchLeafeeImage, type SlideContent } from "@/lib/api";
import { toast } from "sonner";
import type { TemplateInfo } from "@/lib/api";

interface SlideEditorProps {
  slideIndex: number;
  slide: SlideContent;
  images: (File | null)[];
  imagePrompt?: string;
  introTemplates: TemplateInfo[];
  tipTemplates: TemplateInfo[];
  onSlideChange: (slide: SlideContent) => void;
  onImageChange: (index: number, file: File | null) => void;
  onImagePromptChange?: (index: number, prompt: string) => void;
  onPreview?: () => void;
  onRegenerateImage?: () => void;
  regeneratingImage?: boolean;
}

export function SlideEditor({
  slideIndex,
  slide,
  images,
  imagePrompt,
  introTemplates,
  tipTemplates,
  onSlideChange,
  onImageChange,
  onImagePromptChange,
  onPreview,
  onRegenerateImage,
  regeneratingImage,
}: SlideEditorProps) {
  const isIntro = slideIndex === 0;
  const isLeafeeSlide = slideIndex === 3;
  const [loadingLeafee, setLoadingLeafee] = useState(false);

  const handleUseLeafeeImage = useCallback(async () => {
    setLoadingLeafee(true);
    try {
      const file = await fetchLeafeeImage();
      onImageChange(slideIndex, file);
      toast.success("Image Leafee chargée");
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "Erreur chargement image Leafee");
    } finally {
      setLoadingLeafee(false);
    }
  }, [slideIndex, onImageChange]);

  const update = useCallback(
    (updates: Partial<SlideContent>) => {
      onSlideChange({ ...slide, ...updates });
    },
    [slide, onSlideChange]
  );

  const templates = isIntro ? introTemplates : tipTemplates;

  const currentTemplate = templates.find((t) => t.id === (slide.template_id || "leafee-v2"));
  const supportsTitleBgColor = currentTemplate?.variables?.includes("title_bg_color");

  const TITLE_BG_COLORS = [
    { id: "red", label: "Red — #EA403F", value: "#EA403F" },
    { id: "orange", label: "Orange — #FF933D", value: "#FF933D" },
    { id: "yellow", label: "Yellow — #F2CD46", value: "#F2CD46" },
    { id: "lime", label: "Lime Green — #78C25E", value: "#78C25E" },
    { id: "teal", label: "Teal — #77C8A6", value: "#77C8A6" },
    { id: "light-blue", label: "Light Blue — #3496F0", value: "#3496F0" },
    { id: "dark-blue", label: "Dark Blue — #3496F0", value: "#3496F0" },
    { id: "violet", label: "Violet — #5756D4", value: "#5756D4" },
    { id: "pink", label: "Pink — #F7D7E9", value: "#F7D7E9" },
    { id: "brown", label: "Brown — #A3895B", value: "#A3895B" },
    { id: "dark-green", label: "Dark Green — #32523B", value: "#32523B" },
  ] as const;

  const currentTitleBgColor = slide.title_bg_color || "#FF933D";

  return (
    <div className="space-y-6">
      <div className="grid gap-4 sm:grid-cols-2">
        <div className="space-y-2">
          <Label>Type</Label>
          <p className="text-sm text-stone-500">
            {isIntro ? "Slide intro" : "Slide conseil"}
          </p>
        </div>

        <TemplateSelector
          templates={templates}
          value={slide.template_id || "leafee-v2"}
          onValueChange={(v) => update({ template_id: v })}
        />
      </div>

      <ImageUploader
        value={images[slideIndex]}
        onChange={(f) => onImageChange(slideIndex, f)}
        label="Image de fond"
      />
      {supportsTitleBgColor && (
        <div className="space-y-2">
          <Label>Couleur principale</Label>
          <Select
            value={currentTitleBgColor}
            onValueChange={(value) => update({ title_bg_color: value })}
          >
            <SelectTrigger className="border-stone-200 bg-stone-50 focus:ring-stone-900">
              <SelectValue />
            </SelectTrigger>
            <SelectContent className="border-stone-200 bg-white">
              {TITLE_BG_COLORS.map((color) => (
                <SelectItem key={color.id} value={color.value}>
                  <span className="inline-flex items-center gap-2">
                    <span
                      className="inline-block h-3 w-3 rounded-full border border-stone-300"
                      style={{ backgroundColor: color.value }}
                    />
                    {color.label}
                  </span>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      )}
      {isLeafeeSlide && (
        <Button
          type="button"
          variant="outline"
          size="sm"
          onClick={handleUseLeafeeImage}
          disabled={loadingLeafee}
          className="border-stone-300 text-stone-800 hover:bg-stone-100"
        >
          {loadingLeafee ? "Chargement…" : "Utiliser l'image Leafee"}
        </Button>
      )}

      {onImagePromptChange && (
        <div className="space-y-2">
          <Label>Prompt photo</Label>
          <div className="flex gap-2">
            <textarea
              readOnly={!onImagePromptChange}
              value={imagePrompt ?? ""}
              onChange={onImagePromptChange ? (e) => onImagePromptChange(slideIndex, e.target.value) : undefined}
              placeholder="Prompt pour générer l'image de cette slide (éditable)"
              rows={4}
              className="flex min-h-[80px] w-full rounded-md border border-stone-200 bg-stone-50 px-3 py-2 text-sm text-stone-950 placeholder:text-stone-400 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-stone-900"
            />
            <div className="flex flex-col gap-2 shrink-0">
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={() => {
                  navigator.clipboard.writeText(imagePrompt ?? "");
                  toast.success("Copié");
                }}
                className="border-stone-300 text-stone-800 hover:bg-stone-100"
              >
                Copier
              </Button>
              {onRegenerateImage && (
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={onRegenerateImage}
                  disabled={regeneratingImage}
                  className="border-stone-300 text-stone-800 hover:bg-stone-100"
                >
                  {regeneratingImage ? "Génération…" : "Regénérer"}
                </Button>
              )}
            </div>
          </div>
          <p className="text-xs text-stone-500">
            Modifie le prompt puis clique sur Regénérer pour cette slide, ou sur Générer les images pour toutes.
          </p>
        </div>
      )}

      {isIntro ? (
        <>
          <div className="space-y-2">
            <Label>Titre</Label>
            <Input
              value={slide.title || ""}
              onChange={(e) => update({ title: e.target.value })}
              placeholder="ex: Monstera care guide"
            />
          </div>
          <div className="space-y-2">
            <Label>Texte</Label>
            <textarea
              value={slide.body || ""}
              onChange={(e) => update({ body: e.target.value })}
              placeholder="ex: Everyone loves this plant..."
              className="flex min-h-[100px] w-full rounded-md border border-stone-200 bg-stone-50 px-3 py-2 text-sm text-stone-950 placeholder:text-stone-400 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-stone-900"
            />
          </div>
        </>
      ) : (
        <>
          <div className="space-y-2">
            <Label>Tag</Label>
            <Input
              value={slide.tag || ""}
              onChange={(e) => update({ tag: e.target.value })}
              placeholder="ex: WATER"
            />
          </div>
          <div className="space-y-2">
            <Label>Texte</Label>
            <textarea
              value={slide.body || ""}
              onChange={(e) => update({ body: e.target.value })}
              placeholder="ex: Stop drowning it..."
              className="flex min-h-[100px] w-full rounded-md border border-stone-200 bg-stone-50 px-3 py-2 text-sm text-stone-950 placeholder:text-stone-400 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-stone-900"
            />
          </div>
        </>
      )}

      {onPreview && (
        <div className="space-y-1">
          <Button
            variant="outline"
            size="sm"
            onClick={onPreview}
            disabled={!images[slideIndex]}
          >
            Prévisualiser
          </Button>
          {!images[slideIndex] && (
            <p className="text-xs text-stone-500">Ajoute une image de fond pour activer</p>
          )}
        </div>
      )}
    </div>
  );
}
