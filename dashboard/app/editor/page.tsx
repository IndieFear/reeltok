"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { SlideEditor } from "@/components/SlideEditor";
import { CarouselPreview } from "@/components/CarouselPreview";
import {
  deleteContentHistoryEntry,
  fetchContentHistoryImage,
  fetchLeafeeImage,
  fetchGirlImage,
  listGirlsImages,
  generateContent,
  generateCarousel,
  generateImagesFromPrompts,
  generateSingleImage,
  getContentHistoryEntry,
  getContentTypes,
  getTemplates,
  IMAGE_MODELS,
  listContentHistory,
  previewSlide,
  publishCarousel,
  type ContentHistoryEntry,
  type ContentType,
  type ImageModel,
  type SlideContent,
  type CarouselContent,
  type TemplatesResponse,
  type GirlsImage,
} from "@/lib/api";
import { toast } from "sonner";
import {
  ChevronLeft,
  ChevronRight,
  Download,
  FileText,
  History,
  ImageIcon,
  Layers,
  Loader2,
  Send,
  Settings,
  Sparkles,
  Wand2,
} from "lucide-react";

const DEFAULT_SLIDES: SlideContent[] = [
  { type: "intro", title: "", body: "", template_id: "leafee-v2" },
  ...Array(5)
    .fill(null)
    .map(() => ({ type: "tip" as const, tag: "", body: "", template_id: "leafee-v2" })),
];

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

function getLeafeeSlideIndexFromContent(content: CarouselContent): number {
  const idx = content.tips?.findIndex((t) => t.tag === "LEAFEE");
  return idx >= 0 ? idx + 1 : -1;
}

function getLeafeeSlideIndexFromSlides(slides: SlideContent[]): number {
  return slides.findIndex((s) => s.type === "tip" && s.tag === "LEAFEE");
}

function base64ToFile(base64: string, filename: string, mime: string): File {
  const bin = atob(base64);
  const arr = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) arr[i] = bin.charCodeAt(i);
  return new File([arr], filename, { type: mime });
}

function fileToDataUrl(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result as string);
    reader.onerror = () => reject(new Error("Lecture fichier impossible"));
    reader.readAsDataURL(file);
  });
}

function formatHistoryDate(value: string): string {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "";
  return new Intl.DateTimeFormat("fr-FR", {
    day: "2-digit",
    month: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);
}

function GeneratedImagesGrid({
  images,
  selectedIndex,
  onSelect,
}: {
  images: (File | null)[];
  selectedIndex: number;
  onSelect: (index: number) => void;
}) {
  const [previewUrls, setPreviewUrls] = useState<(string | null)[]>([]);

  useEffect(() => {
    const urls = images.map((image) => (image ? URL.createObjectURL(image) : null));
    setPreviewUrls(urls);
    return () => {
      urls.forEach((url) => {
        if (url) URL.revokeObjectURL(url);
      });
    };
  }, [images]);

  const visibleImages = previewUrls
    .map((url, index) => ({ url, index }))
    .filter((item): item is { url: string; index: number } => Boolean(item.url));

  if (visibleImages.length === 0) return null;

  return (
    <Card className="border-stone-200 bg-white shadow-sm">
      <CardHeader className="pb-3">
        <CardTitle className="text-base">Images générées</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4">
          {visibleImages.map(({ url, index }) => (
            <button
              key={`${index}-${url}`}
              type="button"
              onClick={() => onSelect(index)}
              className={`overflow-hidden rounded-xl border bg-white text-left shadow-sm transition ${
                selectedIndex === index
                  ? "border-stone-900 ring-2 ring-stone-900/10"
                  : "border-stone-200 hover:border-stone-400"
              }`}
            >
              <div
                className="aspect-[9/16] bg-cover bg-center"
                style={{ backgroundImage: `url(${url})` }}
              />
              <div className="flex items-center justify-between px-3 py-2 text-xs">
                <span className="font-medium text-stone-900">Slide {index + 1}</span>
                <span className="text-stone-500">Ouvrir</span>
              </div>
            </button>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

export default function EditorPage() {
  const [slides, setSlides] = useState<SlideContent[]>(DEFAULT_SLIDES);
  const [images, setImages] = useState<(File | null)[]>(Array(6).fill(null));
  const [faceRefFile, setFaceRefFile] = useState<File | null>(null);
  const [selectedFaceRefId, setSelectedFaceRefId] = useState<string>("fille1");
  /** Si true, la référence selfie vient d’un fichier local, pas de fille1/2/3. */
  const [isCustomFaceRef, setIsCustomFaceRef] = useState(false);
  const [selectedImageModel, setSelectedImageModel] = useState<ImageModel>("runware");
  const [girlsImages, setGirlsImages] = useState<GirlsImage[]>([]);
  const faceFileInputRef = useRef<HTMLInputElement>(null);
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [templates, setTemplates] = useState<TemplatesResponse | null>(null);
  const [contentTypes, setContentTypes] = useState<ContentType[]>([]);
  const [contentType, setContentType] = useState("care-guide");
  const [keyword, setKeyword] = useState("");
  const [customInstructions, setCustomInstructions] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const [isGeneratingImages, setIsGeneratingImages] = useState(false);
  const [isGeneratingCarousel, setIsGeneratingCarousel] = useState(false);
  const [isPublishing, setIsPublishing] = useState(false);
  const [status, setStatus] = useState<string>("");
  const [progress, setProgress] = useState<number>(0);
  const [generatedSlides, setGeneratedSlides] = useState<{ base64: string; filename: string }[] | null>(null);
  const [caption, setCaption] = useState("");
  const [tiktokDescription, setTiktokDescription] = useState("");
  const [postMode, setPostMode] = useState<"DIRECT_POST" | "MEDIA_UPLOAD">("DIRECT_POST");
  const [uploadPostAccounts, setUploadPostAccounts] = useState<string[]>(["leftonreadgirl"]);
  const [imagePrompts, setImagePrompts] = useState<string[]>([]);
  const [regeneratingSingleImage, setRegeneratingSingleImage] = useState(false);
  const [globalTitleColor, setGlobalTitleColor] = useState<string | null>(null);
  const [contentHistory, setContentHistory] = useState<ContentHistoryEntry[]>([]);
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);
  const [openingHistoryId, setOpeningHistoryId] = useState<string | null>(null);
  const [deletingHistoryId, setDeletingHistoryId] = useState<string | null>(null);
  const [currentHistoryId, setCurrentHistoryId] = useState<string | null>(null);

  const UPLOAD_POST_ACCOUNTS = [
    { id: "leftonreadgirl", label: "@leftonreadgirl" },
    { id: "leftonreadgirlUS", label: "@leftonreadgirlUS" },
    { id: "watereddownbf", label: "@watereddownbf" },
  ];

  const refreshContentHistory = useCallback(async () => {
    setIsLoadingHistory(true);
    try {
      const items = await listContentHistory();
      setContentHistory(items);
    } catch {
      toast.error("Erreur chargement historique");
    } finally {
      setIsLoadingHistory(false);
    }
  }, []);

  useEffect(() => {
    getTemplates()
      .then(setTemplates)
      .catch(() => toast.error("Erreur chargement templates"));
    getContentTypes()
      .then(setContentTypes)
      .catch(() => toast.error("Erreur chargement types"));
    listGirlsImages()
      .then(setGirlsImages)
      .catch(() => toast.error("Erreur chargement images"));
    void refreshContentHistory();
  }, [refreshContentHistory]);

  useEffect(() => {
    const needs7 = contentType === "top-x" || contentType === "top-signs" || contentType === "decor" || contentType === "astrology";
    if (needs7) {
      setSlides((prev) => {
        if (prev.length >= 7) return prev;
        const next = [...prev];
        while (next.length < 7) next.push({ type: "tip" as const, tag: "", body: "", template_id: "leafee-v2" });
        return next;
      });
      setImages((prev) => {
        if (prev.length >= 7) return prev;
        return [...prev, ...Array(7 - prev.length).fill(null)];
      });
    }
  }, [contentType]);

  const buildImageReferenceImages = useCallback(async (): Promise<string[] | undefined> => {
    if (!faceRefFile) return undefined;
    if (isCustomFaceRef) {
      try {
        const dataUrl = await fileToDataUrl(faceRefFile);
        return [dataUrl];
      } catch {
        return undefined;
      }
    }
    return [selectedFaceRefId];
  }, [faceRefFile, isCustomFaceRef, selectedFaceRefId]);

  const applyGeminiContent = useCallback((content: CarouselContent) => {
    const targetSlideCount = content.tips.length + 1;
    setSlides((prev) => {
      const next = [...prev];
      while (next.length < targetSlideCount) next.push({ type: "tip" as const, tag: "", body: "", template_id: "leafee-v2" });
      if (next.length > targetSlideCount) next.length = targetSlideCount;
      next[0] = { ...next[0], type: "intro", title: content.intro_title, body: content.intro_body };
      content.tips.forEach((tip, i) => {
        next[i + 1] = { ...next[i + 1], type: "tip", tag: tip.tag, body: tip.body };
      });
      return next;
    });
    setImages((prev) => {
      if (prev.length > targetSlideCount) return prev.slice(0, targetSlideCount);
      if (prev.length < targetSlideCount) return [...prev, ...Array(targetSlideCount - prev.length).fill(null)];
      return prev;
    });
    setCaption(content.caption);
    setTiktokDescription(content.tiktok_description);
    setImagePrompts(content.image_prompts ?? []);
    setSelectedIndex((prev) => Math.min(prev, targetSlideCount - 1));
  }, []);

  const handleOpenHistoryEntry = useCallback(
    async (id: string) => {
      setOpeningHistoryId(id);
      try {
        const entry = await getContentHistoryEntry(id);
        setKeyword(entry.keyword);
        setContentType(entry.content_type);
        setCustomInstructions(entry.custom_prompt ?? "");
        setCurrentHistoryId(entry.id);
        applyGeminiContent(entry.content);
        const loadedImages: (File | null)[] = Array(entry.content.tips.length + 1).fill(null);
        if (entry.generated_images?.length) {
          const fetchedImages = await Promise.all(
            entry.generated_images.map(async (image) => {
              try {
                const file = await fetchContentHistoryImage(
                  entry.id,
                  image.slide_index,
                  image.filename || `history_slide_${image.slide_index + 1}.jpg`,
                );
                return { index: image.slide_index, file };
              } catch {
                return null;
              }
            }),
          );
          fetchedImages.forEach((item) => {
            if (item && item.index >= 0 && item.index < loadedImages.length) {
              loadedImages[item.index] = item.file;
            }
          });
        }
        setImages(loadedImages);
        setGeneratedSlides(null);
        setSelectedIndex(0);
        toast.success(entry.generated_images?.length ? "Sujet et images rechargés" : "Sujet rechargé");
      } catch (e) {
        toast.error(e instanceof Error ? e.message : "Erreur ouverture historique");
      } finally {
        setOpeningHistoryId(null);
      }
    },
    [applyGeminiContent],
  );

  const handleDeleteHistoryEntry = useCallback(
    async (id: string) => {
      setDeletingHistoryId(id);
      try {
        await deleteContentHistoryEntry(id);
        setContentHistory((prev) => prev.filter((entry) => entry.id !== id));
        if (currentHistoryId === id) {
          setCurrentHistoryId(null);
        }
        toast.success("Sujet supprimé");
      } catch (e) {
        toast.error(e instanceof Error ? e.message : "Erreur suppression historique");
      } finally {
        setDeletingHistoryId(null);
      }
    },
    [currentHistoryId],
  );

  const handleGenerateContentOnly = async () => {
    if (!keyword.trim()) {
      toast.error("Saisis un mot-clé");
      return;
    }
    setIsGenerating(true);
    setStatus("Génération du contenu...");
    setProgress(10);
    try {
      const numSlides = contentType === "top-x" || contentType === "top-signs" || contentType === "decor" || contentType === "astrology" ? 7 : 6;
      const content = await generateContent(
        keyword.trim(),
        numSlides,
        contentType,
        false,
        0,
        customInstructions.trim() || undefined
      );
      setCurrentHistoryId(content.history_id ?? null);
      applyGeminiContent(content);
      void refreshContentHistory();
      setProgress(100);
      setStatus("Contenu généré !");
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "Erreur");
    } finally {
      setIsGenerating(false);
      setTimeout(() => { setStatus(""); setProgress(0); }, 2000);
    }
  };

  const handleGenerateAll = async () => {
    if (!keyword.trim()) {
      toast.error("Saisis un mot-clé");
      return;
    }
    setIsGenerating(true);
    setStatus("Génération du contenu...");
    setProgress(10);
    try {
      const imagesSnapshot = [...images];
      const numSlides = contentType === "top-x" || contentType === "top-signs" || contentType === "decor" || contentType === "astrology" ? 7 : 6;
      const content = await generateContent(
        keyword.trim(),
        numSlides,
        contentType,
        false,
        0,
        customInstructions.trim() || undefined
      );
      setCurrentHistoryId(content.history_id ?? null);
      applyGeminiContent(content);
      void refreshContentHistory();
      setProgress(40);
      setStatus("Contenu généré !");

      if (content.image_prompts?.length && content.image_prompts.some((p) => p?.trim())) {
        setIsGeneratingImages(true);
        setStatus("Génération des images (slides sans image)...");
        setProgress(50);
        try {
          const prompts = content.image_prompts;
          const indicesToGenerate: number[] = [];
          prompts.forEach((p, i) => {
            if (p?.trim() && !imagesSnapshot[i]) {
              indicesToGenerate.push(i);
            }
          });

          if (indicesToGenerate.length > 0) {
            const referenceImages = indicesToGenerate[0] === 0 ? await buildImageReferenceImages() : undefined;
            const promptsToGenerate = indicesToGenerate.map((i) => prompts[i]);
            const { images: fetched } = await generateImagesFromPrompts(
              promptsToGenerate,
              referenceImages,
              selectedImageModel,
              content.history_id,
              indicesToGenerate,
            );

            const mergedImages: (File | null)[] = (() => {
              const baseLength = Math.max(imagesSnapshot.length, prompts.length);
              const arr: (File | null)[] = Array(baseLength).fill(null);
              for (let i = 0; i < baseLength; i++) {
                arr[i] = imagesSnapshot[i] ?? null;
              }
              return arr;
            })();

            fetched.forEach((img, idx) => {
              const slideIndex = indicesToGenerate[idx];
              if (slideIndex != null && img.base64) {
                mergedImages[slideIndex] = base64ToFile(img.base64, img.filename || `slide_${slideIndex}.jpg`, img.mime || "image/jpeg");
              }
            });

            const leafeeIdx = getLeafeeSlideIndexFromContent(content);
            if (leafeeIdx >= 0) mergedImages[leafeeIdx] = await fetchLeafeeImage();

            setImages(mergedImages);
            void refreshContentHistory();
          }
          setProgress(90);
          setStatus("Images générées (slides sans image) !");
          const successCount = indicesToGenerate.length;
          if (successCount > 0) {
            toast.success(`${successCount} image(s) générée(s) (les images existantes ont été conservées)`);
          } else {
            toast.info("Aucune image générée : toutes les slides avaient déjà une image.");
          }
        } catch {
          toast.warning("Contenu généré. Ajoute les images manuellement.");
        } finally {
          setIsGeneratingImages(false);
        }
      }
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "Erreur");
    } finally {
      setIsGenerating(false);
      setProgress(100);
      setTimeout(() => { setStatus(""); setProgress(0); }, 2000);
    }
  };

  const handleGenerateImages = async () => {
    if (!imagePrompts.some((p) => p?.trim())) {
      toast.error("Aucun prompt disponible");
      return;
    }
    setIsGeneratingImages(true);
    setStatus("Génération des images...");
    setProgress(20);
    try {
      const imagesSnapshot = [...images];
      const indicesToGenerate: number[] = [];
      imagePrompts.forEach((p, i) => {
        if (p?.trim() && !imagesSnapshot[i]) {
          indicesToGenerate.push(i);
        }
      });

      if (indicesToGenerate.length === 0) {
        toast.info("Toutes les slides ont déjà une image. Rien à générer.");
        setIsGeneratingImages(false);
        setProgress(100);
        setTimeout(() => { setStatus(""); setProgress(0); }, 2000);
        return;
      }

      const promptsToGenerate = indicesToGenerate.map((i) => imagePrompts[i]);
      const referenceImages = indicesToGenerate[0] === 0 ? await buildImageReferenceImages() : undefined;
      const { images: fetched } = await generateImagesFromPrompts(
        promptsToGenerate,
        referenceImages,
        selectedImageModel,
        currentHistoryId,
        indicesToGenerate,
      );
      setProgress(60);
      const slideCount = imagePrompts.length || 6;
      const files: (File | null)[] = Array(slideCount).fill(null);
      for (let i = 0; i < slideCount; i++) {
        files[i] = imagesSnapshot[i] ?? null;
      }

      fetched.forEach((img, idx) => {
        const slideIndex = indicesToGenerate[idx];
        if (slideIndex != null && slideIndex < slideCount && img.base64) {
          files[slideIndex] = base64ToFile(img.base64, img.filename || `slide_${slideIndex}.jpg`, img.mime || "image/jpeg");
        }
      });
      const leafeeIdx = getLeafeeSlideIndexFromSlides(slides);
      if (leafeeIdx >= 0) files[leafeeIdx] = await fetchLeafeeImage();
      setImages(files);
      void refreshContentHistory();
      setProgress(90);
      setStatus("Images générées !");
      const successCount = indicesToGenerate.length;
      toast.success(`${successCount} image(s) générée(s) (les images existantes ont été conservées)`);
    } catch {
      toast.error("Erreur lors de la génération");
    } finally {
      setIsGeneratingImages(false);
      setProgress(100);
      setTimeout(() => { setStatus(""); setProgress(0); }, 2000);
    }
  };

  const handleSlideChange = useCallback((index: number, slide: SlideContent) => {
    setSlides((prev) => {
      const next = [...prev];
      next[index] = slide;
      return next;
    });
  }, []);

  const handleImageChange = useCallback((index: number, file: File | null) => {
    setImages((prev) => {
      const next = [...prev];
      next[index] = file;
      return next;
    });
  }, []);

  const handleImagePromptChange = useCallback((index: number, prompt: string) => {
    setImagePrompts((prev) => {
      const next = [...prev];
      while (next.length <= index) next.push("");
      next[index] = prompt;
      return next;
    });
  }, []);

  const handleRegenerateSingleImage = useCallback(async () => {
    const prompt = imagePrompts[selectedIndex];
    if (!prompt?.trim()) {
      toast.error("Aucun prompt pour cette slide");
      return;
    }
    setRegeneratingSingleImage(true);
    try {
      const referenceImages = selectedIndex === 0 ? await buildImageReferenceImages() : undefined;
      const result = await generateSingleImage(selectedIndex, prompt, referenceImages, selectedImageModel, currentHistoryId);
      const file = base64ToFile(result.base64, result.filename || `slide_${selectedIndex}.jpg`, result.mime || "image/jpeg");
      handleImageChange(selectedIndex, file);
      void refreshContentHistory();
      toast.success(`Slide ${selectedIndex + 1} régénérée`);
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "Erreur");
    } finally {
      setRegeneratingSingleImage(false);
    }
  }, [selectedIndex, imagePrompts, handleImageChange, buildImageReferenceImages, selectedImageModel, currentHistoryId, refreshContentHistory]);

  const applyGlobalTitleColor = useCallback(
    (color: string | null) => {
      setGlobalTitleColor(color);
      console.log("[Editor] Nouveau globalTitleColor:", color);
      if (!templates || !color) {
        return;
      }
      setSlides((prev) =>
        prev.map((slide, index) => {
          const isIntroSlide = index === 0;
          const tplId = slide.template_id || "leafee-v2";
          const tpl = (isIntroSlide ? templates.intro : templates.tip).find((t) => t.id === tplId);
          if (tpl?.variables?.includes("title_bg_color")) {
            return { ...slide, title_bg_color: color };
          }
          return slide;
        }),
      );
    },
    [templates],
  );

  const handleGenerateCarousel = async () => {
    const hasAtLeastOneImage = images.some(Boolean);
    if (!hasAtLeastOneImage) {
      toast.error("Ajoute au moins une image");
      return;
    }
    // S'assurer que la couleur globale est bien appliquée à toutes les slides Leafee
    let slidesForGeneration = slides;
    console.log("[Editor] handleGenerateCarousel globalTitleColor:", globalTitleColor);
    if (globalTitleColor && templates) {
      slidesForGeneration = slides.map((slide, index) => {
        const isIntroSlide = index === 0;
        const tplId = slide.template_id || "leafee-v2";
        const tpl = (isIntroSlide ? templates.intro : templates.tip).find((t) => t.id === tplId);
        if (tpl?.variables?.includes("title_bg_color")) {
          return { ...slide, title_bg_color: globalTitleColor };
        }
        return slide;
      });
      console.log("[Editor] slidesForGeneration (avec couleur globale):", slidesForGeneration);
      setSlides(slidesForGeneration);
    }
    setIsGeneratingCarousel(true);
    setStatus("Génération du carousel...");
    setProgress(30);
    setGeneratedSlides(null);
    try {
      const files = images.slice(0, slidesForGeneration.length).filter((f): f is File => f !== null);
      const result = await generateCarousel(slidesForGeneration, files);
      setProgress(80);
      setGeneratedSlides(result.slides);
      setStatus("Carousel généré !");
      toast.success("Carousel généré !");
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "Erreur");
    } finally {
      setIsGeneratingCarousel(false);
      setProgress(100);
      setTimeout(() => { setStatus(""); setProgress(0); }, 2000);
    }
  };

  const handlePublish = async () => {
    if (!generatedSlides || generatedSlides.length === 0) {
      toast.error("Génère d'abord le carousel");
      return;
    }
    if (uploadPostAccounts.length === 0) {
      toast.error("Sélectionne au moins un compte");
      return;
    }
    setIsPublishing(true);
    setStatus(`Publication sur ${uploadPostAccounts.length} compte(s)...`);
    setProgress(10);
    try {
      for (let i = 0; i < uploadPostAccounts.length; i++) {
        const account = uploadPostAccounts[i];
        setStatus(`Publication sur @${account}...`);
        setProgress(Math.round(((i + 0.5) / uploadPostAccounts.length) * 100));
        const blobs = generatedSlides.map((s) => {
          const bin = atob(s.base64);
          const arr = new Uint8Array(bin.length);
          for (let j = 0; j < bin.length; j++) arr[j] = bin.charCodeAt(j);
          return new File([arr], s.filename, { type: "image/jpeg" });
        });
        await publishCarousel(caption || "Carousel", tiktokDescription || caption || "Carousel", blobs, postMode, account);
        toast.success(`Publié sur @${account}`);
      }
      setStatus("Publication terminée !");
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "Erreur");
    } finally {
      setIsPublishing(false);
      setProgress(100);
      setTimeout(() => { setStatus(""); setProgress(0); }, 2000);
    }
  };

  const handlePreview = async () => {
    const img = images[selectedIndex];
    if (!img) return;
    try {
      const result = await previewSlide(slides[selectedIndex], img);
      setGeneratedSlides([{ base64: result.base64, filename: "preview.jpg" }]);
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "Erreur");
    }
  };

  const toggleAccount = (id: string) => {
    setUploadPostAccounts((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id].sort()
    );
  };

  const handleCustomFaceFile = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    e.target.value = "";
    if (!file) return;
    if (!file.type.startsWith("image/")) {
      toast.error("Choisis un fichier image (JPG, PNG…)");
      return;
    }
    setFaceRefFile(file);
    setIsCustomFaceRef(true);
    toast.success(`Référence selfie : ${file.name}`);
  }, []);

  const backToPresetFace = useCallback(async () => {
    if (girlsImages.length === 0) {
      setIsCustomFaceRef(false);
      setFaceRefFile(null);
      return;
    }
    setIsCustomFaceRef(false);
    const id = selectedFaceRefId && girlsImages.some((g) => g.id === selectedFaceRefId)
      ? selectedFaceRefId
      : girlsImages[0].id;
    try {
      const f = await fetchGirlImage(id);
      setSelectedFaceRefId(id);
      setFaceRefFile(f);
      toast.success("Image preset chargée");
    } catch {
      toast.error("Impossible de recharger le preset");
    }
  }, [girlsImages, selectedFaceRefId]);

  const introTemplates = templates?.intro ?? [];
  const tipTemplates = templates?.tip ?? [];

  const hasContent = slides[0]?.title || slides[0]?.body;
  const hasImages = images.some(Boolean);
  const canGenerateCarousel = hasContent && hasImages;
  const selectedImageModelLabel = IMAGE_MODELS.find((model) => model.id === selectedImageModel)?.label ?? "modèle image";
  const selectedSlide = slides[selectedIndex] ?? DEFAULT_SLIDES[0];
  const selectedSlideHasImage = Boolean(images[selectedIndex]);
  const imageCount = images.filter(Boolean).length;
  const completedSlides = slides.filter((slide, index) =>
    index === 0 ? Boolean(slide.title || slide.body) : Boolean(slide.tag || slide.body)
  ).length;
  const currentContentType = contentTypes.find((c) => c.id === contentType);

  return (
    <div className="min-h-screen overflow-hidden bg-stone-50 text-stone-950">
      <div className="pointer-events-none fixed inset-0 bg-stone-50" />
      <div className="relative mx-auto flex min-h-screen max-w-[1560px] flex-col px-4 py-5 sm:px-6 lg:px-8">
        <header className="mb-5 flex flex-col gap-4 rounded-[2rem] border border-stone-200 bg-white p-4 shadow-sm md:flex-row md:items-center md:justify-between">
          <div>
            <div className="mb-2 inline-flex items-center gap-2 rounded-full border border-stone-200 bg-stone-100 px-3 py-1 text-xs font-medium text-stone-600">
              <Wand2 className="h-3.5 w-3.5" />
              Studio principal
            </div>
            <h1 className="text-2xl font-semibold tracking-tight text-stone-950 sm:text-3xl">
              ReelTok — Éditeur
            </h1>
            <p className="mt-1 max-w-2xl text-sm text-stone-500">
              Travaille slide par slide, garde les réglages sous la main, puis génère et publie depuis le même écran.
            </p>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <div className="rounded-2xl border border-stone-200 bg-stone-50 px-4 py-2 text-sm text-stone-600">
              <span className="text-stone-400">Progression</span>{" "}
              <span className="font-semibold text-stone-950">{completedSlides}/{slides.length}</span>
              <span className="mx-2 text-stone-300">·</span>
              <span className="font-semibold text-stone-950">{imageCount}</span> images
            </div>
            <Link href="/automation">
              <Button
                variant="outline"
                className="h-11 rounded-2xl border-stone-300 bg-white text-stone-900 hover:bg-stone-100"
              >
                Automatisation
              </Button>
            </Link>
            <Link href="/config">
              <Button
                variant="outline"
                className="h-11 rounded-2xl border-stone-300 bg-white text-stone-900 hover:bg-stone-100"
              >
                <Settings className="h-4 w-4" />
                Settings prompts
              </Button>
            </Link>
          </div>
        </header>

        {/* Status bar */}
        {(status || isGenerating || isGeneratingImages || isGeneratingCarousel || isPublishing) && (
          <div className="mb-5 rounded-2xl border border-stone-200 bg-white p-4 shadow-sm">
            <div className="flex items-center gap-3 mb-2">
              <Loader2 className="w-5 h-5 animate-spin text-stone-700" />
              <span className="font-medium text-stone-900">{status || "En cours..."}</span>
            </div>
            <div className="h-2 w-full overflow-hidden rounded-full bg-stone-100">
              <div
                className="h-full bg-stone-900 transition-all duration-500"
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>
        )}

        <div className="mb-5 grid gap-3 lg:grid-cols-[1.4fr_auto]">
          <Card className="border-stone-200 bg-white shadow-sm">
            <CardContent className="p-4">
              <div className="grid gap-3 xl:grid-cols-[1.2fr_220px_1fr_auto] xl:items-end">
                <div>
                  <Label className="mb-2 block text-xs uppercase tracking-[0.2em] text-stone-500">Sujet</Label>
                  <Input
                    placeholder={currentContentType?.keyword_placeholder || "ex: Monstera"}
                    value={keyword}
                    onChange={(e) => setKeyword(e.target.value)}
                    className="h-12 rounded-2xl border-stone-200 bg-stone-50 text-lg text-stone-950 placeholder:text-stone-400 focus-visible:ring-stone-900"
                  />
                </div>
                <div>
                  <Label className="mb-2 block text-xs uppercase tracking-[0.2em] text-stone-500">Format</Label>
                  <Select value={contentType} onValueChange={setContentType}>
                    <SelectTrigger className="h-12 rounded-2xl border-stone-200 bg-stone-50 focus:ring-stone-900">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {contentTypes.map((ct) => (
                        <SelectItem key={ct.id} value={ct.id}>{ct.name}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label className="mb-2 block text-xs uppercase tracking-[0.2em] text-stone-500">Direction</Label>
                  <Input
                    placeholder="Ton, angle, contrainte de prompt..."
                    value={customInstructions}
                    onChange={(e) => setCustomInstructions(e.target.value)}
                    className="h-12 rounded-2xl border-stone-200 bg-stone-50 focus-visible:ring-stone-900"
                  />
                </div>
                <div className="flex gap-2">
                  <Button
                    onClick={handleGenerateAll}
                    disabled={isGenerating || isGeneratingImages}
                    className="h-12 rounded-2xl bg-stone-950 px-6 font-semibold text-white hover:bg-stone-800"
                  >
                    <Sparkles className="h-4 w-4" />
                    {isGenerating ? "Génération..." : "Générer tout"}
                  </Button>
                  <Button
                    onClick={handleGenerateContentOnly}
                    disabled={isGenerating}
                    variant="outline"
                    className="h-12 rounded-2xl border-stone-200 bg-white px-4 text-stone-900 hover:bg-stone-100"
                  >
                    <FileText className="h-4 w-4" />
                    Texte
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          <div className="grid grid-cols-3 gap-2 rounded-[1.5rem] border border-stone-200 bg-white p-2 text-center shadow-sm lg:w-[360px]">
            <div className="rounded-2xl bg-stone-50 px-3 py-3">
              <p className="text-lg font-semibold text-stone-950">{slides.length}</p>
              <p className="text-[11px] uppercase tracking-[0.18em] text-stone-400">Slides</p>
            </div>
            <div className="rounded-2xl bg-stone-50 px-3 py-3">
              <p className="text-lg font-semibold text-stone-950">{imageCount}</p>
              <p className="text-[11px] uppercase tracking-[0.18em] text-stone-400">Images</p>
            </div>
            <div className="rounded-2xl bg-stone-50 px-3 py-3">
              <p className="text-lg font-semibold text-stone-950">{uploadPostAccounts.length}</p>
              <p className="text-[11px] uppercase tracking-[0.18em] text-stone-400">Comptes</p>
            </div>
          </div>
        </div>

        <div className="grid flex-1 grid-cols-1 gap-5 xl:grid-cols-[280px_minmax(0,1fr)_360px]">
          <aside className="space-y-4">
            <Card className="border-stone-200 bg-white shadow-sm">
              <CardHeader className="pb-3">
                <CardTitle className="flex items-center gap-2 text-base">
                  <Layers className="h-4 w-4 text-stone-500" />
                  Navigation slides
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-2">
                  {slides.map((slide, i) => {
                    const slideComplete = i === 0 ? Boolean(slide.title || slide.body) : Boolean(slide.tag || slide.body);
                    return (
                    <button
                      key={i}
                      onClick={() => setSelectedIndex(i)}
                      className={`rounded-2xl border p-3 text-left transition-all ${
                        selectedIndex === i
                          ? "border-stone-950 bg-stone-950 text-white shadow-sm"
                          : images[i]
                            ? "border-emerald-200 bg-emerald-50 text-stone-900 hover:border-emerald-300"
                            : "border-stone-200 bg-stone-50 text-stone-500 hover:border-stone-300 hover:bg-white"
                      }`}
                    >
                      <span className="block text-sm font-semibold">Slide {i + 1}</span>
                      <span className="mt-1 block text-xs opacity-70">
                        {i === 0 ? "Intro" : slide.tag || "Conseil"} {slideComplete ? "· prêt" : ""}
                      </span>
                    </button>
                  )})}
                </div>
                <div className="flex justify-between mt-4">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setSelectedIndex((prev) => Math.max(0, prev - 1))}
                    disabled={selectedIndex === 0}
                  >
                    <ChevronLeft className="w-4 h-4" />
                  </Button>
                  <span className="text-sm text-stone-500">Slide {selectedIndex + 1} / {slides.length}</span>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setSelectedIndex((prev) => Math.min(slides.length - 1, prev + 1))}
                    disabled={selectedIndex === slides.length - 1}
                  >
                    <ChevronRight className="w-4 h-4" />
                  </Button>
                </div>
              </CardContent>
            </Card>

            <Card className="border-stone-200 bg-white shadow-sm">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between gap-2">
                  <CardTitle className="text-base flex items-center gap-2">
                    <History className="w-4 h-4 text-stone-500" />
                    Historique
                  </CardTitle>
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={() => void refreshContentHistory()}
                    disabled={isLoadingHistory}
                    className="h-8 px-2 text-xs text-stone-500 hover:bg-stone-100 hover:text-stone-900"
                  >
                    {isLoadingHistory ? "..." : "Rafraîchir"}
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                {contentHistory.length === 0 ? (
                  <p className="text-sm text-stone-500">
                    Aucun sujet généré pour le moment.
                  </p>
                ) : (
                  <div className="space-y-2">
                    {contentHistory.slice(0, 8).map((entry) => (
                      <div key={entry.id} className="rounded-2xl border border-stone-200 bg-stone-50 p-3">
                        <div className="flex items-start justify-between gap-2">
                          <div className="min-w-0">
                            <p className="truncate text-sm font-medium text-stone-900" title={entry.keyword}>
                              {entry.keyword}
                            </p>
                            <p className="mt-1 text-xs text-stone-500">
                              {entry.content_type} · {formatHistoryDate(entry.created_at)}
                              {entry.generated_images?.length ? ` · ${entry.generated_images.length} image(s)` : ""}
                            </p>
                          </div>
                          <div className="flex shrink-0 flex-col gap-2">
                            <Button
                              type="button"
                              variant="outline"
                              size="sm"
                              onClick={() => void handleOpenHistoryEntry(entry.id)}
                              disabled={openingHistoryId === entry.id || deletingHistoryId === entry.id}
                              className="h-8 border-stone-200 bg-white px-2 text-xs hover:bg-stone-100"
                            >
                              {openingHistoryId === entry.id ? "..." : "Ouvrir"}
                            </Button>
                            <Button
                              type="button"
                              variant="ghost"
                              size="sm"
                              onClick={() => void handleDeleteHistoryEntry(entry.id)}
                              disabled={deletingHistoryId === entry.id || openingHistoryId === entry.id}
                              className="h-8 px-2 text-xs text-red-400 hover:bg-red-500/10 hover:text-red-300"
                            >
                              {deletingHistoryId === entry.id ? "..." : "Supprimer"}
                            </Button>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </aside>

          <main className="min-w-0 space-y-5">
            <GeneratedImagesGrid
              images={images}
              selectedIndex={selectedIndex}
              onSelect={setSelectedIndex}
            />

            <Card className="border-stone-200 bg-white shadow-sm">
              <CardHeader className="border-b border-stone-200 pb-4">
                <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                  <div>
                    <CardTitle className="text-xl">
                      {selectedIndex === 0 ? "Slide intro" : `Slide conseil ${selectedIndex}`}
                    </CardTitle>
                    <p className="mt-1 text-sm text-stone-500">
                      {selectedSlideHasImage ? "Image attachée" : "Ajoute ou génère une image"} · {currentContentType?.name ?? contentType}
                    </p>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    <Button
                      onClick={handleGenerateImages}
                      disabled={isGeneratingImages || !imagePrompts.some((p) => p?.trim())}
                      variant="outline"
                      className="rounded-2xl border-stone-200 bg-white text-stone-900 hover:bg-stone-100"
                    >
                      <ImageIcon className="h-4 w-4" />
                      Générer images
                    </Button>
                    <Button
                      onClick={handleGenerateCarousel}
                      disabled={isGeneratingCarousel || !canGenerateCarousel}
                      className="rounded-2xl bg-stone-950 text-white hover:bg-stone-800"
                    >
                      <Download className="h-4 w-4" />
                      Rendu final
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="p-5">
                {templates ? (
                  <SlideEditor
                    slideIndex={selectedIndex}
                    slide={selectedSlide}
                    images={images}
                    imagePrompt={imagePrompts[selectedIndex]}
                    introTemplates={introTemplates}
                    tipTemplates={tipTemplates}
                    onSlideChange={(s) => handleSlideChange(selectedIndex, s)}
                    onImageChange={handleImageChange}
                    onImagePromptChange={handleImagePromptChange}
                    onPreview={handlePreview}
                    onRegenerateImage={handleRegenerateSingleImage}
                    regeneratingImage={regeneratingSingleImage}
                  />
                ) : (
                  <Skeleton className="h-64 w-full" />
                )}
              </CardContent>
            </Card>

            {generatedSlides && generatedSlides.length > 0 && (
              <Card className="border-stone-200 bg-white shadow-sm">
                <CardHeader className="pb-3">
                  <CardTitle>Résultat final</CardTitle>
                </CardHeader>
                <CardContent>
                  <CarouselPreview slides={generatedSlides} />
                </CardContent>
              </Card>
            )}
          </main>

          <aside className="space-y-4">
            <Card className="border-stone-200 bg-white shadow-sm">
              <CardHeader className="pb-3">
                <CardTitle className="text-base text-stone-950">Actions rapides</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <Button
                  onClick={handleGenerateAll}
                  disabled={isGenerating || isGeneratingImages}
                  className="h-11 w-full rounded-2xl bg-stone-950 font-semibold text-white hover:bg-stone-800"
                >
                  <Sparkles className="h-4 w-4" />
                  Générer contenu + images
                </Button>
                <Button
                  onClick={() => setImages((prev) => prev.map(() => null))}
                  variant="outline"
                  className="h-11 w-full rounded-2xl border-stone-200 bg-white text-stone-900 hover:bg-stone-100"
                >
                  Supprimer toutes les images
                </Button>
                <Button
                  onClick={handlePublish}
                  disabled={isPublishing || !generatedSlides?.length || uploadPostAccounts.length === 0}
                  className="h-11 w-full rounded-2xl bg-stone-900 text-white hover:bg-stone-700"
                >
                  <Send className="h-4 w-4" />
                  Publier ({uploadPostAccounts.length})
                </Button>
              </CardContent>
            </Card>

            <Card className="border-stone-200 bg-white shadow-sm">
              <CardHeader className="pb-3">
                <CardTitle className="text-base">Réglages image</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label className="mb-2 block text-xs text-stone-500">Modèle image</Label>
                  <Select value={selectedImageModel} onValueChange={(value) => setSelectedImageModel(value as ImageModel)}>
                    <SelectTrigger className="h-11 rounded-2xl border-stone-200 bg-stone-50">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {IMAGE_MODELS.map((model) => (
                        <SelectItem key={model.id} value={model.id}>
                          {model.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <p className="mt-2 text-xs text-stone-500">{selectedImageModelLabel}</p>
                </div>

                <div>
                  <Label className="mb-2 block text-xs text-stone-500">Couleur globale Leafee</Label>
                  <Select value={globalTitleColor ?? ""} onValueChange={(value) => applyGlobalTitleColor(value)}>
                    <SelectTrigger className="h-11 rounded-2xl border-stone-200 bg-stone-50">
                      <SelectValue placeholder="Par défaut (orange)" />
                    </SelectTrigger>
                    <SelectContent>
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

                <div className="rounded-2xl border border-stone-200 bg-stone-50 p-3">
                  <input
                    ref={faceFileInputRef}
                    type="file"
                    accept="image/*"
                    className="hidden"
                    onChange={handleCustomFaceFile}
                  />
                  <div className="flex flex-wrap gap-2">
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      className="border-stone-200 bg-white text-stone-900 hover:bg-stone-100"
                      onClick={() => faceFileInputRef.current?.click()}
                    >
                      Ma photo
                    </Button>
                    {isCustomFaceRef && girlsImages.length > 0 && (
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        className="text-stone-500 hover:bg-stone-100 hover:text-stone-900"
                        onClick={() => void backToPresetFace()}
                      >
                        Presets
                      </Button>
                    )}
                  </div>
                  {isCustomFaceRef && faceRefFile && (
                    <p className="mt-2 truncate text-xs text-stone-500" title={faceRefFile.name}>
                      {faceRefFile.name}
                    </p>
                  )}
                  {girlsImages.length > 0 && (
                    <Select
                      value={selectedFaceRefId}
                      disabled={isCustomFaceRef}
                      onValueChange={async (value) => {
                        setIsCustomFaceRef(false);
                        setSelectedFaceRefId(value);
                        try {
                          const f = await fetchGirlImage(value);
                          setFaceRefFile(f);
                        } catch {
                          toast.error("Image non trouvée");
                        }
                      }}
                    >
                      <SelectTrigger className="mt-3 h-10 rounded-2xl border-stone-200 bg-white text-xs">
                        <SelectValue placeholder="Référence preset" />
                      </SelectTrigger>
                      <SelectContent className="border-stone-200 bg-white">
                        {girlsImages.map((img) => (
                          <SelectItem key={img.id} value={img.id} className="cursor-pointer">
                            {img.filename}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  )}
                </div>
              </CardContent>
            </Card>

            <Card className="border-stone-200 bg-white shadow-sm">
              <CardHeader className="pb-3">
                <CardTitle className="text-base">Publication</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  {UPLOAD_POST_ACCOUNTS.map((acc) => (
                    <label
                      key={acc.id}
                      className={`flex cursor-pointer items-center gap-3 rounded-2xl border p-3 transition-colors ${
                        uploadPostAccounts.includes(acc.id)
                          ? "border-stone-900 bg-stone-100"
                          : "border-stone-200 bg-stone-50 hover:bg-white"
                      }`}
                    >
                      <input
                        type="checkbox"
                        checked={uploadPostAccounts.includes(acc.id)}
                        onChange={() => toggleAccount(acc.id)}
                        className="rounded"
                      />
                      <span className="text-sm">{acc.label}</span>
                    </label>
                  ))}
                </div>
                <Select value={postMode} onValueChange={(v) => setPostMode(v as "DIRECT_POST" | "MEDIA_UPLOAD")}>
                  <SelectTrigger className="h-10 rounded-2xl border-stone-200 bg-stone-50 text-xs">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="DIRECT_POST">Publication directe</SelectItem>
                    <SelectItem value="MEDIA_UPLOAD">Brouillon (inbox)</SelectItem>
                  </SelectContent>
                </Select>
              </CardContent>
            </Card>

            <Card className="border-stone-200 bg-white shadow-sm">
              <CardHeader className="pb-3">
                <CardTitle className="text-base">Caption</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <Input
                  value={caption}
                  onChange={(e) => setCaption(e.target.value)}
                  placeholder="Caption du post..."
                  className="rounded-2xl border-stone-200 bg-stone-50 focus-visible:ring-stone-900"
                />
                <textarea
                  value={tiktokDescription}
                  onChange={(e) => setTiktokDescription(e.target.value)}
                  placeholder="Description longue..."
                  rows={4}
                  className="w-full rounded-2xl border border-stone-200 bg-stone-50 px-3 py-2 text-sm text-stone-950 placeholder:text-stone-400 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-stone-900"
                />
              </CardContent>
            </Card>
          </aside>
        </div>
      </div>
    </div>
  );
}
