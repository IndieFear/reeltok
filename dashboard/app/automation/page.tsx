"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { toast } from "sonner";
import { Loader2, RefreshCw, Play, Upload, Zap, X, ChevronLeft, ChevronRight, Trash2 } from "lucide-react";
import {
  getAutomationConfig,
  saveAutomationConfig,
  listAutomationJobs,
  getAutomationJob,
  automationSlideUrl,
  syncAutomationSheet,
  deleteAutomationJob,
  updateAutomationJobSchedule,
  generateAutomationJob,
  publishAutomationJob,
  generatePendingAutomationJobs,
  runDueAutomationJobs,
  getContentTypes,
  listGirlsImages,
  IMAGE_MODELS,
  type GirlsImage,
  type AutomationConfig,
  type AutomationJob,
  type AutomationJobDetail,
  type AutomationJobLog,
  type ContentType,
} from "@/lib/api";

const UPLOAD_ACCOUNTS = [
  { id: "leftonreadgirl", label: "@leftonreadgirl" },
  { id: "leftonreadgirlUS", label: "@leftonreadgirlUS" },
  { id: "watereddownbf", label: "@watereddownbf" },
];

const STATUS_LABELS: Record<string, string> = {
  imported: "Importé",
  scheduled: "Planifié",
  generating: "Génération…",
  ready: "Prêt",
  publishing: "Publication…",
  published: "Publié",
  failed: "Échec",
  skipped: "Ignoré",
};

function statusBadgeClass(status: string): string {
  switch (status) {
    case "published":
      return "bg-emerald-100 text-emerald-800";
    case "ready":
      return "bg-sky-100 text-sky-800";
    case "scheduled":
      return "bg-amber-100 text-amber-800";
    case "generating":
    case "publishing":
      return "bg-violet-100 text-violet-800";
    case "failed":
      return "bg-red-100 text-red-800";
    default:
      return "bg-stone-100 text-stone-700";
  }
}

function formatDate(value: string | null): string {
  if (!value) return "—";
  try {
    return new Date(value).toLocaleString("fr-FR", {
      day: "2-digit",
      month: "short",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return value;
  }
}

function toDatetimeLocalValue(iso: string | null): string {
  if (!iso) return "";
  const d = new Date(iso);
  const pad = (n: number) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

function referenceImageLabel(ref: string | null | undefined): string {
  if (!ref) return "—";
  if (ref === "random") return "Aléatoire";
  return ref;
}

function imageModelLabel(modelId: string | null | undefined): string {
  if (!modelId) return "—";
  return IMAGE_MODELS.find((m) => m.id === modelId)?.label ?? modelId;
}

function logLevelClass(level: AutomationJobLog["level"]): string {
  switch (level) {
    case "success":
      return "text-emerald-700 bg-emerald-50 border-emerald-100";
    case "error":
      return "text-red-700 bg-red-50 border-red-100";
    case "warning":
      return "text-amber-700 bg-amber-50 border-amber-100";
    default:
      return "text-stone-700 bg-stone-50 border-stone-100";
  }
}

export default function AutomationPage() {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const [running, setRunning] = useState(false);
  const [generatingPending, setGeneratingPending] = useState(false);
  const [actionJobId, setActionJobId] = useState<string | null>(null);
  const [config, setConfig] = useState<AutomationConfig | null>(null);
  const [slotTimes, setSlotTimes] = useState<string[]>([]);
  const [jobs, setJobs] = useState<AutomationJob[]>([]);
  const [contentTypes, setContentTypes] = useState<ContentType[]>([]);
  const [girlsImages, setGirlsImages] = useState<GirlsImage[]>([]);
  const [selectedJobId, setSelectedJobId] = useState<string | null>(null);
  const [selectedDetail, setSelectedDetail] = useState<AutomationJobDetail | null>(null);
  const [loadingDetail, setLoadingDetail] = useState(false);
  const [previewIndex, setPreviewIndex] = useState(0);
  const [deletingJobId, setDeletingJobId] = useState<string | null>(null);
  const [editingSchedule, setEditingSchedule] = useState("");
  const [savingSchedule, setSavingSchedule] = useState(false);

  const refresh = useCallback(async () => {
    const [cfgRes, jobsRes] = await Promise.all([getAutomationConfig(), listAutomationJobs()]);
    const cfg = cfgRes.config;
    setConfig({
      ...cfg,
      upload_post_users: cfg.upload_post_users?.length ? cfg.upload_post_users : [cfg.upload_post_user],
      privacy_level: cfg.privacy_level ?? "PUBLIC_TO_EVERYONE",
      auto_add_music: cfg.auto_add_music ?? true,
      scheduler_interval_seconds: cfg.scheduler_interval_seconds ?? 300,
      reference_image: cfg.reference_image ?? "random",
    });
    setSlotTimes(cfgRes.slot_times);
    setJobs(jobsRes.jobs);
    if (selectedJobId) {
      const stillExists = jobsRes.jobs.some((j) => j.id === selectedJobId);
      if (!stillExists) {
        setSelectedJobId(null);
        setSelectedDetail(null);
      } else {
        try {
          const detail = await getAutomationJob(selectedJobId);
          setSelectedDetail(detail);
          setEditingSchedule(toDatetimeLocalValue(detail.job.scheduled_at));
        } catch {
          // ignore refresh detail errors
        }
      }
    }
  }, [selectedJobId]);

  const loadJobDetail = useCallback(async (jobId: string) => {
    setLoadingDetail(true);
    setPreviewIndex(0);
    try {
      const detail = await getAutomationJob(jobId);
      setSelectedDetail(detail);
      setEditingSchedule(toDatetimeLocalValue(detail.job.scheduled_at));
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "Erreur chargement détail");
    } finally {
      setLoadingDetail(false);
    }
  }, []);

  const handleSelectJob = useCallback(
    async (jobId: string) => {
      if (selectedJobId === jobId) {
        setSelectedJobId(null);
        setSelectedDetail(null);
        return;
      }
      setSelectedJobId(jobId);
      await loadJobDetail(jobId);
    },
    [selectedJobId, loadJobDetail],
  );

  useEffect(() => {
    async function load() {
      try {
        const [cts, girls] = await Promise.all([getContentTypes(), listGirlsImages()]);
        setContentTypes(cts);
        setGirlsImages(girls);
        await refresh();
      } catch (e) {
        toast.error(e instanceof Error ? e.message : "Erreur chargement");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [refresh]);

  const toggleAccount = (accountId: string) => {
    if (!config) return;
    setConfig((prev) => {
      if (!prev) return prev;
      const users = prev.upload_post_users ?? [prev.upload_post_user];
      const next = users.includes(accountId)
        ? users.filter((id) => id !== accountId)
        : [...users, accountId].sort();
      return {
        ...prev,
        upload_post_users: next,
        upload_post_user: next[0] ?? prev.upload_post_user,
      };
    });
  };

  const handleSave = async () => {
    if (!config) return;
    if (!config.upload_post_users?.length) {
      toast.error("Sélectionne au moins un compte TikTok");
      return;
    }
    setSaving(true);
    try {
      await saveAutomationConfig(config);
      const cfgRes = await getAutomationConfig();
      setSlotTimes(cfgRes.slot_times);
      toast.success("Configuration sauvegardée");
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "Erreur sauvegarde");
    } finally {
      setSaving(false);
    }
  };

  const handleSync = async () => {
    if (!config?.sheet_csv_url?.trim()) {
      toast.error("Ajoute l'URL de ton Google Sheet");
      return;
    }
    setSyncing(true);
    try {
      const result = await syncAutomationSheet(config.sheet_csv_url.trim());
      await refresh();
      toast.success(
        `${result.imported} sujet(s) importé(s), ${result.skipped} ignoré(s). Génération au moment de la publication.`,
      );
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "Erreur synchronisation");
    } finally {
      setSyncing(false);
    }
  };

  const handleGeneratePending = async () => {
    setGeneratingPending(true);
    try {
      const result = await generatePendingAutomationJobs(5);
      await refresh();
      toast.success(
        result.generated > 0
          ? `${result.generated} carousel(s) généré(s) (jobs dus uniquement)`
          : "Aucun job dû à générer pour l'instant",
      );
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "Erreur génération");
    } finally {
      setGeneratingPending(false);
    }
  };

  const handleRunDue = async () => {
    setRunning(true);
    try {
      const result = await runDueAutomationJobs();
      await refresh();
      toast.success(
        `Planifiés: ${result.scheduled}, générés: ${result.generated}, publiés: ${result.published}, erreurs: ${result.errors}`,
      );
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "Erreur exécution");
    } finally {
      setRunning(false);
    }
  };

  const handleGenerateJob = async (jobId: string) => {
    setActionJobId(jobId);
    try {
      await generateAutomationJob(jobId);
      await refresh();
      if (selectedJobId === jobId) await loadJobDetail(jobId);
      toast.success("Carousel généré");
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "Erreur");
    } finally {
      setActionJobId(null);
    }
  };

  const handlePublishJob = async (jobId: string) => {
    setActionJobId(jobId);
    try {
      await publishAutomationJob(jobId);
      await refresh();
      if (selectedJobId === jobId) await loadJobDetail(jobId);
      toast.success("Publié sur TikTok");
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "Erreur");
    } finally {
      setActionJobId(null);
    }
  };

  const handleSaveSchedule = async () => {
    if (!selectedJobId || !editingSchedule) {
      toast.error("Choisis une date et une heure");
      return;
    }
    setSavingSchedule(true);
    try {
      const scheduledAt = new Date(editingSchedule).toISOString();
      await updateAutomationJobSchedule(selectedJobId, scheduledAt);
      await refresh();
      toast.success("Heure de publication mise à jour");
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "Erreur mise à jour horaire");
    } finally {
      setSavingSchedule(false);
    }
  };

  const handleDeleteJob = async (jobId: string, topic: string) => {
    if (!window.confirm(`Supprimer le sujet « ${topic} » ?`)) return;
    setDeletingJobId(jobId);
    try {
      await deleteAutomationJob(jobId);
      if (selectedJobId === jobId) {
        setSelectedJobId(null);
        setSelectedDetail(null);
      }
      await refresh();
      toast.success("Sujet supprimé");
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "Erreur suppression");
    } finally {
      setDeletingJobId(null);
    }
  };

  if (loading || !config) {
    return (
      <div className="min-h-screen bg-stone-50 p-8">
        <Skeleton className="h-10 w-64 mb-6 bg-stone-200" />
        <Skeleton className="h-48 w-full mb-4 bg-stone-200" />
        <Skeleton className="h-64 w-full bg-stone-200" />
      </div>
    );
  }

  const pendingCount = jobs.filter((j) => ["imported", "scheduled"].includes(j.status)).length;
  const readyCount = jobs.filter((j) => j.status === "ready").length;

  return (
    <div className="min-h-screen bg-stone-50 text-stone-950">
      <div className="container mx-auto max-w-6xl space-y-8 px-6 py-8">
        <header className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div>
            <p className="text-xs font-medium uppercase tracking-[0.2em] text-stone-400">Automatisation</p>
            <h1 className="text-2xl font-semibold tracking-tight">Google Sheets → Carrousels → TikTok</h1>
            <p className="mt-1 text-sm text-stone-500">
              Importe une liste de sujets, planifie les publications, puis génère et publie chaque carousel uniquement à l&apos;heure prévue.
            </p>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <Link href="/editor">
              <Button variant="outline" className="border-stone-200 bg-white hover:bg-stone-100">
                Éditeur
              </Button>
            </Link>
            <Link href="/config">
              <Button variant="outline" className="border-stone-200 bg-white hover:bg-stone-100">
                Config prompts
              </Button>
            </Link>
            <Button onClick={handleSave} disabled={saving} className="bg-stone-950 text-white hover:bg-stone-800">
              {saving ? "Sauvegarde…" : "Sauvegarder"}
            </Button>
          </div>
        </header>

        <div className="grid gap-6 lg:grid-cols-2">
          <Card className="border-stone-200 bg-white shadow-sm">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium">Lier Google Sheet</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label className="text-[10px] uppercase tracking-[0.2em] text-stone-500">URL du Sheet (CSV public)</Label>
                <Input
                  value={config.sheet_csv_url}
                  onChange={(e) => setConfig({ ...config, sheet_csv_url: e.target.value })}
                  placeholder="https://docs.google.com/spreadsheets/d/..."
                  className="border-stone-200"
                />
                <p className="text-xs text-stone-500">
                  Publie ton Sheet sur le web (Fichier → Partager → Publier sur le web → CSV). Colonnes attendues:{" "}
                  <code className="rounded bg-stone-100 px-1">topic</code> ou{" "}
                  <code className="rounded bg-stone-100 px-1">sujet</code> (obligatoire), optionnellement{" "}
                  <code className="rounded bg-stone-100 px-1">content_type</code>,{" "}
                  <code className="rounded bg-stone-100 px-1">account</code>,{" "}
                  <code className="rounded bg-stone-100 px-1">status</code>.
                </p>
              </div>
              <Button
                onClick={handleSync}
                disabled={syncing}
                className="w-full bg-stone-950 text-white hover:bg-stone-800"
              >
                {syncing ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <RefreshCw className="mr-2 h-4 w-4" />}
                Synchroniser le Sheet
              </Button>
            </CardContent>
          </Card>

          <Card className="border-stone-200 bg-white shadow-sm">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium">Planification</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <label className="flex items-center gap-3 rounded-xl border border-stone-200 bg-stone-50 px-4 py-3">
                <input
                  type="checkbox"
                  checked={config.enabled}
                  onChange={(e) => setConfig({ ...config, enabled: e.target.checked })}
                  className="h-4 w-4 rounded border-stone-300"
                />
                <span className="text-sm font-medium">Activer l&apos;automatisation (scheduler backend)</span>
              </label>

              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-2">
                  <Label className="text-[10px] uppercase tracking-[0.2em] text-stone-500">Posts / jour</Label>
                  <Input
                    type="number"
                    min={1}
                    max={10}
                    value={config.posts_per_day}
                    onChange={(e) => setConfig({ ...config, posts_per_day: Number(e.target.value) })}
                    className="border-stone-200"
                  />
                </div>
                <div className="space-y-2">
                  <Label className="text-[10px] uppercase tracking-[0.2em] text-stone-500">Fuseau</Label>
                  <Input
                    value={config.timezone}
                    onChange={(e) => setConfig({ ...config, timezone: e.target.value })}
                    className="border-stone-200"
                  />
                </div>
                <div className="space-y-2">
                  <Label className="text-[10px] uppercase tracking-[0.2em] text-stone-500">Début (h)</Label>
                  <Input
                    type="number"
                    min={0}
                    max={23}
                    value={config.start_hour}
                    onChange={(e) => setConfig({ ...config, start_hour: Number(e.target.value) })}
                    className="border-stone-200"
                  />
                </div>
                <div className="space-y-2">
                  <Label className="text-[10px] uppercase tracking-[0.2em] text-stone-500">Fin (h)</Label>
                  <Input
                    type="number"
                    min={1}
                    max={23}
                    value={config.end_hour}
                    onChange={(e) => setConfig({ ...config, end_hour: Number(e.target.value) })}
                    className="border-stone-200"
                  />
                </div>
              </div>

              <p className="text-xs text-stone-500">
                Créneaux calculés: {slotTimes.length ? slotTimes.join(", ") : "—"} ({config.timezone})
              </p>

              <div className="space-y-2">
                <Label className="text-[10px] uppercase tracking-[0.2em] text-stone-500">
                  Vérification scheduler (minutes)
                </Label>
                <Input
                  type="number"
                  min={1}
                  max={60}
                  value={Math.round((config.scheduler_interval_seconds ?? 300) / 60)}
                  onChange={(e) =>
                    setConfig({
                      ...config,
                      scheduler_interval_seconds: Math.max(60, Number(e.target.value) * 60),
                    })
                  }
                  className="border-stone-200"
                />
                <p className="text-xs text-stone-500">
                  Le backend vérifie les jobs dus toutes les {Math.round((config.scheduler_interval_seconds ?? 300) / 60)} min.
                  Suffisant pour 3 posts/jour — pas besoin de tourner chaque minute.
                </p>
              </div>

              <div className="space-y-2">
                <Label className="text-[10px] uppercase tracking-[0.2em] text-stone-500">Type de contenu par défaut</Label>
                <Select
                  value={config.default_content_type}
                  onValueChange={(v) => setConfig({ ...config, default_content_type: v })}
                >
                  <SelectTrigger className="border-stone-200">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {contentTypes.map((ct) => (
                      <SelectItem key={ct.id} value={ct.id}>
                        {ct.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-2">
                  <Label className="text-[10px] uppercase tracking-[0.2em] text-stone-500">Modèle image</Label>
                  <Select
                    value={config.image_model}
                    onValueChange={(v) => setConfig({ ...config, image_model: v as AutomationConfig["image_model"] })}
                  >
                    <SelectTrigger className="border-stone-200">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {IMAGE_MODELS.map((m) => (
                        <SelectItem key={m.id} value={m.id}>
                          {m.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label className="text-[10px] uppercase tracking-[0.2em] text-stone-500">Référence selfie</Label>
                  <Select
                    value={config.reference_image ?? "random"}
                    onValueChange={(v) => setConfig({ ...config, reference_image: v })}
                  >
                    <SelectTrigger className="border-stone-200">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="random">Aléatoire (fille1–fille9)</SelectItem>
                      {girlsImages.map((img) => (
                        <SelectItem key={img.id} value={img.id}>
                          {img.id}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <Card className="border-stone-200 bg-white shadow-sm">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Publication TikTok</CardTitle>
            <p className="text-xs text-stone-500">
              Paramètres envoyés à upload-post.com lors de chaque publication automatique.
            </p>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label className="text-[10px] uppercase tracking-[0.2em] text-stone-500">Comptes TikTok</Label>
              <div className="grid gap-2 sm:grid-cols-3">
                {UPLOAD_ACCOUNTS.map((acc) => {
                  const selected = (config.upload_post_users ?? [config.upload_post_user]).includes(acc.id);
                  return (
                    <label
                      key={acc.id}
                      className={`flex cursor-pointer items-center gap-3 rounded-xl border p-3 transition-colors ${
                        selected ? "border-stone-900 bg-stone-100" : "border-stone-200 bg-stone-50 hover:bg-white"
                      }`}
                    >
                      <input
                        type="checkbox"
                        checked={selected}
                        onChange={() => toggleAccount(acc.id)}
                        className="rounded"
                      />
                      <span className="text-sm">{acc.label}</span>
                    </label>
                  );
                })}
              </div>
              <p className="text-xs text-stone-500">
                Si une colonne <code className="rounded bg-stone-100 px-1">account</code> est renseignée dans le Sheet, elle remplace cette liste pour ce sujet.
              </p>
            </div>

            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              <div className="space-y-2">
                <Label className="text-[10px] uppercase tracking-[0.2em] text-stone-500">Mode de publication</Label>
                <Select
                  value={config.post_mode}
                  onValueChange={(v) => setConfig({ ...config, post_mode: v as AutomationConfig["post_mode"] })}
                >
                  <SelectTrigger className="border-stone-200">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="DIRECT_POST">Publication directe</SelectItem>
                    <SelectItem value="MEDIA_UPLOAD">Brouillon (inbox TikTok)</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label className="text-[10px] uppercase tracking-[0.2em] text-stone-500">Visibilité</Label>
                <Select
                  value={config.privacy_level}
                  onValueChange={(v) => setConfig({ ...config, privacy_level: v as AutomationConfig["privacy_level"] })}
                >
                  <SelectTrigger className="border-stone-200">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="PUBLIC_TO_EVERYONE">Public</SelectItem>
                    <SelectItem value="MUTUAL_FOLLOW_FRIENDS">Amis mutuels</SelectItem>
                    <SelectItem value="SELF_ONLY">Moi uniquement (privé)</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <label className="flex items-center gap-3 rounded-xl border border-stone-200 bg-stone-50 px-4 py-3 sm:mt-6">
                <input
                  type="checkbox"
                  checked={config.auto_add_music}
                  onChange={(e) => setConfig({ ...config, auto_add_music: e.target.checked })}
                  className="h-4 w-4 rounded border-stone-300"
                />
                <span className="text-sm font-medium">Ajouter une musique automatiquement</span>
              </label>
            </div>
          </CardContent>
        </Card>

        <Card className="border-stone-200 bg-white shadow-sm">
          <CardHeader className="flex flex-row items-center justify-between pb-3">
            <div>
              <CardTitle className="text-sm font-medium">Actions</CardTitle>
              <p className="mt-1 text-xs text-stone-500">
                {pendingCount} en attente · {readyCount} prêt(s) à publier
              </p>
            </div>
            <div className="flex flex-wrap gap-2">
              <Button
                variant="outline"
                onClick={handleGeneratePending}
                disabled={generatingPending}
                className="border-stone-200"
              >
                {generatingPending ? (
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                ) : (
                  <Zap className="mr-2 h-4 w-4" />
                )}
                Générer les jobs dus
              </Button>
              <Button
                onClick={handleRunDue}
                disabled={running}
                className="bg-stone-950 text-white hover:bg-stone-800"
              >
                {running ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Play className="mr-2 h-4 w-4" />}
                Publier les jobs dus
              </Button>
            </div>
          </CardHeader>
        </Card>

        <div className="grid gap-6 xl:grid-cols-[1fr_380px]">
          <Card className="border-stone-200 bg-white shadow-sm">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium">File de sujets ({jobs.length})</CardTitle>
              <p className="text-xs text-stone-500">Clique sur un sujet pour voir l&apos;aperçu et les logs.</p>
            </CardHeader>
            <CardContent>
              {jobs.length === 0 ? (
                <p className="py-8 text-center text-sm text-stone-500">
                  Aucun sujet importé. Synchronise ton Google Sheet pour commencer.
                </p>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-stone-100 text-left text-[10px] uppercase tracking-[0.15em] text-stone-400">
                        <th className="pb-3 pr-4 font-medium">Sujet</th>
                        <th className="pb-3 pr-4 font-medium">Type</th>
                        <th className="pb-3 pr-4 font-medium">Compte</th>
                        <th className="pb-3 pr-4 font-medium">Statut</th>
                        <th className="pb-3 pr-4 font-medium">Planifié</th>
                        <th className="pb-3 font-medium">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {jobs.map((job) => (
                        <tr
                          key={job.id}
                          className={`cursor-pointer border-b border-stone-50 transition-colors ${
                            selectedJobId === job.id ? "bg-stone-100" : "hover:bg-stone-50"
                          }`}
                          onClick={() => handleSelectJob(job.id)}
                        >
                          <td className="py-3 pr-4">
                            <div className="font-medium text-stone-900">{job.topic}</div>
                            {job.error && <p className="mt-1 text-xs text-red-600 line-clamp-1">{job.error}</p>}
                          </td>
                          <td className="py-3 pr-4 text-stone-600">{job.content_type}</td>
                          <td className="py-3 pr-4 text-stone-600">
                            {job.account || (config.upload_post_users ?? [config.upload_post_user]).join(", ")}
                          </td>
                          <td className="py-3 pr-4">
                            <span
                              className={`inline-flex rounded-full px-2.5 py-0.5 text-xs font-medium ${statusBadgeClass(job.status)}`}
                            >
                              {STATUS_LABELS[job.status] ?? job.status}
                            </span>
                          </td>
                          <td className="py-3 pr-4 text-stone-600">{formatDate(job.scheduled_at)}</td>
                          <td className="py-3" onClick={(e) => e.stopPropagation()}>
                            <div className="flex gap-1">
                              {job.status !== "published" && job.status !== "generating" && (
                                <Button
                                  size="sm"
                                  variant="outline"
                                  className="h-8 border-stone-200 text-xs"
                                  disabled={actionJobId === job.id}
                                  onClick={() => handleGenerateJob(job.id)}
                                >
                                  {actionJobId === job.id ? (
                                    <Loader2 className="h-3 w-3 animate-spin" />
                                  ) : (
                                    <Zap className="h-3 w-3" />
                                  )}
                                </Button>
                              )}
                              {["ready", "scheduled", "failed"].includes(job.status) && (
                                <Button
                                  size="sm"
                                  variant="outline"
                                  className="h-8 border-stone-200 text-xs"
                                  disabled={actionJobId === job.id}
                                  onClick={() => handlePublishJob(job.id)}
                                >
                                  {actionJobId === job.id ? (
                                    <Loader2 className="h-3 w-3 animate-spin" />
                                  ) : (
                                    <Upload className="h-3 w-3" />
                                  )}
                                </Button>
                              )}
                              <Button
                                size="sm"
                                variant="outline"
                                className="h-8 border-stone-200 text-xs text-red-600 hover:bg-red-50 hover:text-red-700"
                                disabled={deletingJobId === job.id}
                                onClick={() => handleDeleteJob(job.id, job.topic)}
                              >
                                {deletingJobId === job.id ? (
                                  <Loader2 className="h-3 w-3 animate-spin" />
                                ) : (
                                  <Trash2 className="h-3 w-3" />
                                )}
                              </Button>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </CardContent>
          </Card>

          <Card className="border-stone-200 bg-white shadow-sm xl:sticky xl:top-6 xl:self-start">
            <CardHeader className="flex flex-row items-start justify-between pb-3">
              <div>
                <CardTitle className="text-sm font-medium">Détail du sujet</CardTitle>
                {selectedDetail?.job && (
                  <p className="mt-1 text-xs text-stone-500 line-clamp-2">{selectedDetail.job.topic}</p>
                )}
              </div>
              {selectedJobId && (
                <Button
                  size="sm"
                  variant="ghost"
                  className="h-8 w-8 p-0"
                  onClick={() => {
                    setSelectedJobId(null);
                    setSelectedDetail(null);
                  }}
                >
                  <X className="h-4 w-4" />
                </Button>
              )}
            </CardHeader>
            <CardContent>
              {!selectedJobId ? (
                <p className="py-12 text-center text-sm text-stone-500">Sélectionne un sujet dans la liste.</p>
              ) : loadingDetail ? (
                <div className="flex items-center justify-center py-12">
                  <Loader2 className="h-6 w-6 animate-spin text-stone-400" />
                </div>
              ) : selectedDetail ? (
                <div className="space-y-5">
                  <div className="grid grid-cols-2 gap-2 text-xs">
                    <div className="rounded-lg bg-stone-50 px-3 py-2">
                      <p className="text-stone-400">Statut</p>
                      <p className="font-medium">{STATUS_LABELS[selectedDetail.job.status] ?? selectedDetail.job.status}</p>
                    </div>
                    <div className="rounded-lg bg-stone-50 px-3 py-2">
                      <p className="text-stone-400">Planifié</p>
                      <p className="font-medium">{formatDate(selectedDetail.job.scheduled_at)}</p>
                    </div>
                    <div className="rounded-lg bg-stone-50 px-3 py-2">
                      <p className="text-stone-400">Modèle texte</p>
                      <p className="font-medium">
                        {selectedDetail.job.text_model === "gemini" ? "Gemini" : selectedDetail.job.text_model ?? "Gemini (prévu)"}
                      </p>
                    </div>
                    <div className="rounded-lg bg-stone-50 px-3 py-2">
                      <p className="text-stone-400">Modèle image</p>
                      <p className="font-medium">
                        {selectedDetail.job.image_model
                          ? imageModelLabel(selectedDetail.job.image_model)
                          : `${imageModelLabel(config.image_model)} (prévu)`}
                      </p>
                    </div>
                    <div className="rounded-lg bg-stone-50 px-3 py-2">
                      <p className="text-stone-400">Référence selfie</p>
                      <p className="font-medium">
                        {selectedDetail.job.reference_image
                          ? referenceImageLabel(selectedDetail.job.reference_image)
                          : `${referenceImageLabel(config.reference_image)} (prévu)`}
                      </p>
                    </div>
                    <div className="rounded-lg bg-stone-50 px-3 py-2">
                      <p className="text-stone-400">Créé</p>
                      <p className="font-medium">{formatDate(selectedDetail.job.created_at)}</p>
                    </div>
                    <div className="rounded-lg bg-stone-50 px-3 py-2">
                      <p className="text-stone-400">Publié</p>
                      <p className="font-medium">{formatDate(selectedDetail.job.published_at)}</p>
                    </div>
                  </div>

                  {selectedDetail.job.status !== "published" && (
                    <div className="space-y-2 rounded-xl border border-stone-200 bg-stone-50 p-3">
                      <Label className="text-[10px] uppercase tracking-[0.2em] text-stone-500">
                        Modifier l&apos;heure de publication
                      </Label>
                      <Input
                        type="datetime-local"
                        value={editingSchedule}
                        onChange={(e) => setEditingSchedule(e.target.value)}
                        className="border-stone-200 bg-white"
                      />
                      <Button
                        size="sm"
                        onClick={handleSaveSchedule}
                        disabled={savingSchedule || !editingSchedule}
                        className="bg-stone-950 text-white hover:bg-stone-800"
                      >
                        {savingSchedule ? (
                          <Loader2 className="mr-2 h-3 w-3 animate-spin" />
                        ) : null}
                        Enregistrer l&apos;heure
                      </Button>
                    </div>
                  )}

                  {selectedDetail.slides.length > 0 ? (
                    <div className="space-y-2">
                      <Label className="text-[10px] uppercase tracking-[0.2em] text-stone-500">
                        Aperçu carousel ({selectedDetail.slides.length} slides)
                      </Label>
                      <div className="relative overflow-hidden rounded-2xl border border-stone-200 bg-stone-950">
                        <img
                          src={automationSlideUrl(selectedDetail.slides[previewIndex].url)}
                          alt={`Slide ${previewIndex + 1}`}
                          className="mx-auto max-h-[420px] w-full object-contain"
                        />
                        {selectedDetail.slides.length > 1 && (
                          <>
                            <button
                              type="button"
                              className="absolute left-2 top-1/2 -translate-y-1/2 rounded-full bg-black/50 p-1.5 text-white"
                              onClick={() =>
                                setPreviewIndex((i) => (i === 0 ? selectedDetail.slides.length - 1 : i - 1))
                              }
                            >
                              <ChevronLeft className="h-4 w-4" />
                            </button>
                            <button
                              type="button"
                              className="absolute right-2 top-1/2 -translate-y-1/2 rounded-full bg-black/50 p-1.5 text-white"
                              onClick={() =>
                                setPreviewIndex((i) => (i === selectedDetail.slides.length - 1 ? 0 : i + 1))
                              }
                            >
                              <ChevronRight className="h-4 w-4" />
                            </button>
                            <div className="absolute bottom-2 left-1/2 -translate-x-1/2 rounded-full bg-black/60 px-2 py-0.5 text-xs text-white">
                              {previewIndex + 1} / {selectedDetail.slides.length}
                            </div>
                          </>
                        )}
                      </div>
                      <div className="flex gap-1 overflow-x-auto pb-1">
                        {selectedDetail.slides.map((slide, i) => (
                          <button
                            key={slide.filename}
                            type="button"
                            onClick={() => setPreviewIndex(i)}
                            className={`shrink-0 overflow-hidden rounded-lg border-2 ${
                              i === previewIndex ? "border-stone-900" : "border-transparent opacity-60"
                            }`}
                          >
                            <img
                              src={automationSlideUrl(slide.url)}
                              alt={`Miniature ${i + 1}`}
                              className="h-16 w-10 object-cover"
                            />
                          </button>
                        ))}
                      </div>
                    </div>
                  ) : (
                    <div className="rounded-xl border border-dashed border-stone-200 bg-stone-50 px-4 py-8 text-center text-sm text-stone-500">
                      Aperçu indisponible — le carousel sera généré à l&apos;heure de publication.
                    </div>
                  )}

                  {(selectedDetail.job.caption || selectedDetail.job.tiktok_description) && (
                    <div className="space-y-2">
                      {selectedDetail.job.caption && (
                        <div>
                          <Label className="text-[10px] uppercase tracking-[0.2em] text-stone-500">Caption</Label>
                          <p className="mt-1 text-xs text-stone-700 whitespace-pre-wrap">{selectedDetail.job.caption}</p>
                        </div>
                      )}
                      {selectedDetail.job.tiktok_description && (
                        <div>
                          <Label className="text-[10px] uppercase tracking-[0.2em] text-stone-500">Description TikTok</Label>
                          <p className="mt-1 text-xs text-stone-700 whitespace-pre-wrap">
                            {selectedDetail.job.tiktok_description}
                          </p>
                        </div>
                      )}
                    </div>
                  )}

                  <div className="space-y-2">
                    <Label className="text-[10px] uppercase tracking-[0.2em] text-stone-500">Logs</Label>
                    <div className="max-h-64 space-y-1.5 overflow-y-auto rounded-xl border border-stone-200 bg-stone-50 p-2">
                      {(selectedDetail.job.logs ?? []).length === 0 ? (
                        <p className="px-2 py-4 text-center text-xs text-stone-500">Aucun log pour l&apos;instant.</p>
                      ) : (
                        [...(selectedDetail.job.logs ?? [])].reverse().map((log, i) => (
                          <div
                            key={`${log.at}-${i}`}
                            className={`rounded-lg border px-2.5 py-2 text-xs ${logLevelClass(log.level)}`}
                          >
                            <p className="text-[10px] opacity-60">{formatDate(log.at)}</p>
                            <p className="mt-0.5">{log.message}</p>
                          </div>
                        ))
                      )}
                    </div>
                  </div>

                  {selectedDetail.job.error && (
                    <div className="rounded-xl border border-red-200 bg-red-50 px-3 py-2 text-xs text-red-700">
                      {selectedDetail.job.error}
                    </div>
                  )}

                  <Button
                    variant="outline"
                    className="w-full border-red-200 text-red-600 hover:bg-red-50 hover:text-red-700"
                    disabled={deletingJobId === selectedDetail.job.id}
                    onClick={() => handleDeleteJob(selectedDetail.job.id, selectedDetail.job.topic)}
                  >
                    {deletingJobId === selectedDetail.job.id ? (
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    ) : (
                      <Trash2 className="mr-2 h-4 w-4" />
                    )}
                    Supprimer ce sujet
                  </Button>
                </div>
              ) : null}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
