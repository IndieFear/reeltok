const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export type ImageModel = "runware" | "replicate-gpt-image-2" | "replicate-grok-imagine-image";

export const IMAGE_MODELS: { id: ImageModel; label: string }[] = [
  { id: "runware", label: "Runware - Flux 2 Klein" },
  { id: "replicate-gpt-image-2", label: "Replicate - OpenAI GPT Image 2" },
  { id: "replicate-grok-imagine-image", label: "Replicate - xAI Grok Imagine" },
];

export interface TipSlide {
  tag: string;
  body: string;
}

export interface CarouselContent {
  intro_title: string;
  intro_body: string;
  tips: TipSlide[];
  caption: string;
  tiktok_description: string;
  image_prompts?: string[];
  history_id?: string | null;
}

export interface GeneratedImageHistoryItem {
  slide_index: number;
  image_model: ImageModel;
  source_url: string;
  filename?: string | null;
  mime?: string | null;
  generated_at: string;
}

export interface ContentHistoryEntry {
  id: string;
  created_at: string;
  keyword: string;
  content_type: string;
  num_slides: number;
  custom_prompt?: string | null;
  content: CarouselContent;
  generated_images?: GeneratedImageHistoryItem[];
}

export interface GeneratedImageResult {
  base64: string;
  filename: string;
  mime: string;
  source_url?: string | null;
  error?: string;
}

export interface TemplateInfo {
  id: string;
  name: string;
  variables: string[];
}

export interface TemplatesResponse {
  intro: TemplateInfo[];
  tip: TemplateInfo[];
}

export interface ContentType {
  id: string;
  name: string;
  keyword_placeholder: string;
  description: string;
}

export async function getContentTypes(): Promise<ContentType[]> {
  const res = await fetch(`${API_URL}/api/content-types`);
  if (!res.ok) throw new Error("Erreur chargement types de contenu");
  return res.json();
}

export async function getPromptPreview(
  keyword: string,
  contentType: string = "care-guide",
  numSlides: number = 6
): Promise<{ prompt: string }> {
  const params = new URLSearchParams({
    keyword,
    content_type: contentType,
    num_slides: String(numSlides),
  });
  const res = await fetch(`${API_URL}/api/prompt-preview?${params}`);
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Erreur chargement prompt");
  }
  return res.json();
}

export async function generateContent(
  keyword: string,
  numSlides: number = 6,
  contentType: string = "care-guide",
  useCache: boolean = false,
  variationIndex: number = 0,
  customPrompt?: string | null
): Promise<CarouselContent> {
  const res = await fetch(`${API_URL}/api/generate-content`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      keyword,
      num_slides: numSlides,
      content_type: contentType,
      use_cache: useCache,
      variation_index: variationIndex,
      ...(customPrompt?.trim() ? { custom_prompt: customPrompt.trim() } : {}),
    }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Erreur génération contenu");
  }
  return res.json();
}

export async function listContentHistory(): Promise<ContentHistoryEntry[]> {
  const res = await fetch(`${API_URL}/api/content-history`);
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Erreur chargement historique");
  }
  const data = await res.json();
  return data.items ?? [];
}

export async function getContentHistoryEntry(id: string): Promise<ContentHistoryEntry> {
  const res = await fetch(`${API_URL}/api/content-history/${id}`);
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Erreur ouverture historique");
  }
  return res.json();
}

export async function deleteContentHistoryEntry(id: string): Promise<void> {
  const res = await fetch(`${API_URL}/api/content-history/${id}`, {
    method: "DELETE",
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Erreur suppression historique");
  }
}

export async function fetchContentHistoryImage(
  historyId: string,
  slideIndex: number,
  filename: string = `history_slide_${slideIndex + 1}.jpg`
): Promise<File> {
  const res = await fetch(`${API_URL}/api/content-history/${historyId}/image/${slideIndex}`);
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Erreur chargement image historique");
  }
  const blob = await res.blob();
  return new File([blob], filename, { type: blob.type || "image/jpeg" });
}

export async function generateImagesFromPrompts(
  prompts: string[],
  referenceImages?: string[],
  imageModel: ImageModel = "runware",
  historyId?: string | null,
  slideIndices?: number[]
): Promise<{ images: GeneratedImageResult[] }> {
  const res = await fetch(`${API_URL}/api/generate-images-from-prompts`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      prompts,
      image_model: imageModel,
      ...(historyId ? { history_id: historyId } : {}),
      ...(slideIndices?.length ? { slide_indices: slideIndices } : {}),
      ...(referenceImages?.length ? { reference_images: referenceImages } : {}),
    }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Erreur génération images");
  }
  return res.json();
}

export async function generateSingleImage(
  index: number,
  prompt: string,
  referenceImages?: string[],
  imageModel: ImageModel = "runware",
  historyId?: string | null
): Promise<GeneratedImageResult> {
  const res = await fetch(`${API_URL}/api/generate-single-image`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      prompt,
      index,
      image_model: imageModel,
      ...(historyId ? { history_id: historyId } : {}),
      ...(referenceImages?.length ? { reference_images: referenceImages } : {}),
    }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Erreur génération image");
  }
  return res.json();
}

export async function getTemplates(): Promise<TemplatesResponse> {
  const res = await fetch(`${API_URL}/api/templates`);
  if (!res.ok) throw new Error("Erreur chargement templates");
  return res.json();
}

export async function fetchLeafeeImage(): Promise<File> {
  const res = await fetch(`${API_URL}/api/leafee-image`);
  if (!res.ok) throw new Error("Image Leafee introuvable");
  const blob = await res.blob();
  return new File([blob], "leafee.jpg", { type: "image/jpeg" });
}

export interface GirlsImage {
  id: string;
  filename: string;
  url: string;
}

export async function listGirlsImages(): Promise<GirlsImage[]> {
  const res = await fetch(`${API_URL}/api/girls-images`);
  if (!res.ok) throw new Error("Erreur chargement images");
  const data = await res.json();
  return data.images;
}

export async function fetchGirlImage(imageId: string): Promise<File> {
  const res = await fetch(`${API_URL}/api/fille-image/${imageId}`);
  if (!res.ok) throw new Error(`Image ${imageId} introuvable`);
  const blob = await res.blob();
  return new File([blob], `${imageId}.png`, { type: "image/png" });
}

export interface PromptOverride {
  extra_instructions: string;
  full_prompt?: string | null;
}

export interface PromptOverridesResponse {
  overrides: Record<string, PromptOverride>;
}

export async function getPromptConfig(): Promise<PromptOverridesResponse> {
  const res = await fetch(`${API_URL}/api/prompt-config`);
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Erreur chargement config de prompts");
  }
  return res.json();
}

export async function savePromptConfig(payload: PromptOverridesResponse): Promise<PromptOverridesResponse> {
  const res = await fetch(`${API_URL}/api/prompt-config`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Erreur sauvegarde config de prompts");
  }
  return res.json();
}

export interface SlideContent {
  type: "intro" | "tip";
  title?: string;
  body?: string;
  tag?: string;
  template_id?: string;
  title_bg_color?: string;
}

export async function generateCarousel(
  slidesContent: SlideContent[],
  images: File[]
): Promise<{ slides: { base64: string; filename: string }[] }> {
  const form = new FormData();
  form.append("slides_content", JSON.stringify(slidesContent));
  images.forEach((img) => form.append("images", img));

  const res = await fetch(`${API_URL}/api/generate-carousel`, {
    method: "POST",
    body: form,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Erreur génération carousel");
  }
  return res.json();
}

export async function previewSlide(
  slideContent: SlideContent,
  image: File
): Promise<{ base64: string }> {
  const form = new FormData();
  form.append("slide_content", JSON.stringify(slideContent));
  form.append("image", image);

  const res = await fetch(`${API_URL}/api/preview-slide`, {
    method: "POST",
    body: form,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Erreur prévisualisation");
  }
  return res.json();
}

export async function publishCarousel(
  title: string,
  description: string,
  images: File[],
  postMode: string = "DIRECT_POST",
  uploadPostUser?: string
): Promise<{ success: boolean; result?: unknown }> {
  const form = new FormData();
  form.append("title", title);
  form.append("description", description);
  form.append("post_mode", postMode);
  if (uploadPostUser) form.append("upload_post_user", uploadPostUser);
  images.forEach((img) => form.append("images", img));

  const res = await fetch(`${API_URL}/api/publish`, {
    method: "POST",
    body: form,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Erreur publication");
  }
  return res.json();
}

// --- Automation ---

export type AutomationJobStatus =
  | "imported"
  | "scheduled"
  | "generating"
  | "ready"
  | "publishing"
  | "published"
  | "failed"
  | "skipped";

export type PostMode = "DIRECT_POST" | "MEDIA_UPLOAD";
export type PrivacyLevel = "PUBLIC_TO_EVERYONE" | "MUTUAL_FOLLOW_FRIENDS" | "SELF_ONLY";

export interface AutomationConfig {
  sheet_csv_url: string;
  enabled: boolean;
  posts_per_day: number;
  start_hour: number;
  end_hour: number;
  default_content_type: string;
  image_model: ImageModel;
  upload_post_user: string;
  upload_post_users: string[];
  post_mode: PostMode;
  privacy_level: PrivacyLevel;
  auto_add_music: boolean;
  reference_image: string;
  auto_generate_on_sync: boolean;
  timezone: string;
  scheduler_interval_seconds: number;
}

export interface AutomationJobLog {
  at: string;
  level: "info" | "success" | "error" | "warning";
  message: string;
}

export interface AutomationJobSlide {
  filename: string;
  url: string;
}

export interface AutomationJob {
  id: string;
  topic: string;
  content_type: string;
  account: string;
  status: AutomationJobStatus;
  scheduled_at: string | null;
  error: string | null;
  history_id: string | null;
  carousel_dir: string | null;
  caption: string | null;
  tiktok_description: string | null;
  sheet_row?: number;
  created_at: string;
  updated_at: string;
  published_at: string | null;
  published_accounts?: string[];
  slide_count?: number;
  image_model?: ImageModel | null;
  text_model?: string | null;
  reference_image?: string | null;
  logs?: AutomationJobLog[];
  publish_result?: Record<string, unknown>;
}

export interface AutomationJobDetail {
  job: AutomationJob;
  slides: AutomationJobSlide[];
}

export interface AutomationConfigResponse {
  config: AutomationConfig;
  slot_times: string[];
  defaults: AutomationConfig;
}

export async function getAutomationConfig(): Promise<AutomationConfigResponse> {
  const res = await fetch(`${API_URL}/api/automation/config`);
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Erreur chargement config automation");
  }
  return res.json();
}

export async function saveAutomationConfig(config: AutomationConfig): Promise<{ config: AutomationConfig }> {
  const res = await fetch(`${API_URL}/api/automation/config`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(config),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Erreur sauvegarde config automation");
  }
  return res.json();
}

export function automationSlideUrl(relativeUrl: string): string {
  return `${API_URL}${relativeUrl}`;
}

export async function getAutomationJob(jobId: string): Promise<AutomationJobDetail> {
  const res = await fetch(`${API_URL}/api/automation/jobs/${jobId}`);
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Erreur chargement job");
  }
  return res.json();
}

export async function listAutomationJobs(): Promise<{ jobs: AutomationJob[]; total: number }> {
  const res = await fetch(`${API_URL}/api/automation/jobs`);
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Erreur chargement jobs");
  }
  return res.json();
}

export async function syncAutomationSheet(sheetCsvUrl?: string): Promise<{
  success: boolean;
  imported: number;
  skipped: number;
  scheduled: number;
  generated: number;
  rows_in_sheet: number;
}> {
  const res = await fetch(`${API_URL}/api/automation/sync-sheet`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(sheetCsvUrl ? { sheet_csv_url: sheetCsvUrl } : {}),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Erreur synchronisation Sheet");
  }
  return res.json();
}

export async function updateAutomationJobSchedule(
  jobId: string,
  scheduledAt: string,
): Promise<{ success: boolean; job: AutomationJob }> {
  const res = await fetch(`${API_URL}/api/automation/jobs/${jobId}/schedule`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ scheduled_at: scheduledAt }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Erreur mise à jour horaire");
  }
  return res.json();
}

export async function deleteAutomationJob(jobId: string): Promise<{ success: boolean }> {
  const res = await fetch(`${API_URL}/api/automation/jobs/${jobId}`, { method: "DELETE" });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Erreur suppression job");
  }
  return res.json();
}

export async function generateAutomationJob(jobId: string): Promise<{ success: boolean; job: AutomationJob }> {
  const res = await fetch(`${API_URL}/api/automation/jobs/${jobId}/generate`, { method: "POST" });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Erreur génération job");
  }
  return res.json();
}

export async function publishAutomationJob(jobId: string): Promise<{ success: boolean; job: AutomationJob }> {
  const res = await fetch(`${API_URL}/api/automation/jobs/${jobId}/publish`, { method: "POST" });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Erreur publication job");
  }
  return res.json();
}

export async function generatePendingAutomationJobs(limit = 5): Promise<{ success: boolean; generated: number }> {
  const res = await fetch(`${API_URL}/api/automation/generate-pending?limit=${limit}`, { method: "POST" });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Erreur génération jobs en attente");
  }
  return res.json();
}

export async function runDueAutomationJobs(): Promise<{
  success: boolean;
  scheduled: number;
  generated: number;
  published: number;
  errors: number;
}> {
  const res = await fetch(`${API_URL}/api/automation/run-due`, { method: "POST" });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Erreur exécution jobs dus");
  }
  return res.json();
}
