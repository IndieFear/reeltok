"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Skeleton } from "@/components/ui/skeleton";
import { toast } from "sonner";
import {
  getContentTypes,
  type ContentType,
  getPromptConfig,
  savePromptConfig,
  type PromptOverridesResponse,
  getPromptPreview,
} from "@/lib/api";

export default function ConfigPage() {
  const [contentTypes, setContentTypes] = useState<ContentType[]>([]);
  const [overrides, setOverrides] = useState<PromptOverridesResponse["overrides"]>({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [selectedTypeId, setSelectedTypeId] = useState<string | null>(null);
  const [promptPreview, setPromptPreview] = useState<string>("");
  const [loadingPreview, setLoadingPreview] = useState(false);

  useEffect(() => {
    async function load() {
      try {
        const [cts, cfg] = await Promise.all([getContentTypes(), getPromptConfig()]);
        setContentTypes(cts);
        setOverrides(cfg.overrides || {});
        if (cts.length > 0) {
          setSelectedTypeId(cts[0].id);
        }
      } catch (e) {
        toast.error(e instanceof Error ? e.message : "Erreur chargement configuration");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  useEffect(() => {
    async function loadPreview() {
      if (!selectedTypeId) {
        setPromptPreview("");
        return;
      }
      setLoadingPreview(true);
      try {
        const numSlides =
          selectedTypeId === "top-x" || selectedTypeId === "top-signs" || selectedTypeId === "decor" || selectedTypeId === "astrology"
            ? 7
            : 6;
        // On utilise un keyword d'exemple pour visualiser le prompt final
        const result = await getPromptPreview("Monstera deliciosa", selectedTypeId, numSlides);
        setPromptPreview(result.prompt);
      } catch (e) {
        setPromptPreview(
          e instanceof Error ? `Erreur chargement du prompt : ${e.message}` : "Erreur chargement du prompt",
        );
      } finally {
        setLoadingPreview(false);
      }
    }
    loadPreview();
  }, [selectedTypeId]);

  const handleExtraChange = (id: string, value: string) => {
    setOverrides((prev) => ({
      ...prev,
      [id]: {
        extra_instructions: value,
        full_prompt: prev[id]?.full_prompt ?? null,
      },
    }));
  };

  const handleFullPromptChange = (id: string, value: string) => {
    setOverrides((prev) => ({
      ...prev,
      [id]: {
        extra_instructions: prev[id]?.extra_instructions ?? "",
        full_prompt: value || null,
      },
    }));
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      await savePromptConfig({ overrides });
      toast.success("Configuration sauvegardée");
      // Recharger l'aperçu du prompt pour refléter les changements
      if (selectedTypeId) {
        const numSlides =
          selectedTypeId === "top-x" || selectedTypeId === "top-signs" || selectedTypeId === "decor" || selectedTypeId === "astrology"
            ? 7
            : 6;
        const result = await getPromptPreview("Monstera deliciosa", selectedTypeId, numSlides);
        setPromptPreview(result.prompt);
      }
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "Erreur lors de la sauvegarde");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="min-h-screen bg-stone-50 text-stone-950">
      <div className="container mx-auto px-6 py-8 max-w-6xl space-y-8">
        <header className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div>
            <h1 className="text-2xl font-semibold tracking-tight">Configuration des prompts</h1>
            <p className="mt-1 text-sm text-stone-500">
              À gauche : choisis un type de contenu. À droite : vois le prompt actuel et ajuste-le sans toucher au code.
            </p>
          </div>
          <div className="flex items-center gap-2">
            <Link href="/automation">
              <Button variant="outline" className="border-stone-200 bg-white hover:bg-stone-100">
                Automatisation
              </Button>
            </Link>
            <Link href="/editor">
              <Button variant="outline" className="border-stone-200 bg-white hover:bg-stone-100">
                Revenir à l&apos;éditeur
              </Button>
            </Link>
            <Button onClick={handleSave} disabled={saving} className="bg-stone-950 text-white hover:bg-stone-800">
              {saving ? "Sauvegarde..." : "Sauvegarder"}
            </Button>
          </div>
        </header>

        {loading ? (
          <div className="grid gap-6 md:grid-cols-[260px,1fr]">
            <Skeleton className="h-64 w-full bg-stone-200" />
            <Skeleton className="h-64 w-full bg-stone-200" />
          </div>
        ) : (
          <div className="grid gap-6 md:grid-cols-[260px,1fr]">
            {/* Colonne gauche : liste des types */}
            <Card className="h-full border-stone-200 bg-white shadow-sm">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium">Types de contenu</CardTitle>
              </CardHeader>
              <CardContent className="space-y-1">
                {contentTypes.map((ct) => {
                  const selected = ct.id === selectedTypeId;
                  return (
                    <button
                      key={ct.id}
                      type="button"
                      className={`w-full text-left px-3 py-2 rounded-md text-sm transition-colors ${
                        selected
                          ? "bg-stone-950 text-white"
                          : "bg-stone-50 text-stone-700 hover:bg-stone-100"
                      }`}
                      onClick={() => setSelectedTypeId(ct.id)}
                    >
                      <div className="flex items-center justify-between gap-2">
                        <span>{ct.name}</span>
                        <span className="text-[10px] font-mono opacity-70">{ct.id}</span>
                      </div>
                      <p className="mt-1 text-[11px] text-stone-500 line-clamp-2">{ct.description}</p>
                    </button>
                  );
                })}
              </CardContent>
            </Card>

            {/* Colonne droite : édition pour le type sélectionné */}
            <Card className="h-full border-stone-200 bg-white shadow-sm">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium">
                  {selectedTypeId
                    ? `Prompt pour "${contentTypes.find((c) => c.id === selectedTypeId)?.name ?? selectedTypeId}"`
                    : "Sélectionne un type de contenu"}
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-5">
                {selectedTypeId && (
                  <>
                    <div className="space-y-2">
                      <div className="flex items-center justify-between gap-2">
                        <Label className="text-xs text-stone-600">Prompt actuel (lecture seule)</Label>
                        <div className="flex items-center gap-2">
                          <span className="text-[10px] text-stone-500">
                            Exemple avec keyword &quot;Monstera deliciosa&quot;
                          </span>
                          <Button
                            type="button"
                            variant="outline"
                            size="xs"
                            className="h-7 border-stone-200 bg-white text-[11px] hover:bg-stone-100"
                            onClick={() => {
                              navigator.clipboard.writeText(promptPreview);
                              toast.success("Prompt copié dans le presse-papiers");
                            }}
                            disabled={!promptPreview}
                          >
                            Copier
                          </Button>
                        </div>
                      </div>
                      <Textarea
                        className="min-h-[180px] border-stone-200 bg-stone-50 text-xs font-mono text-stone-800"
                        readOnly
                        value={
                          loadingPreview
                            ? "Chargement du prompt..."
                            : promptPreview || "Aucun prompt disponible pour l'instant."
                        }
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor={`full-${selectedTypeId}`} className="text-xs text-stone-600">
                        Prompt complet (optionnel)
                      </Label>
                      <Textarea
                        id={`full-${selectedTypeId}`}
                        className="min-h-[180px] border-stone-200 bg-stone-50 text-xs font-mono text-stone-900"
                        placeholder={
                          "Si tu remplis ce champ, il remplacera intégralement le prompt par défaut pour ce type.\n" +
                          "Tu peux utiliser {keyword} et {num_slides} comme variables dans le texte."
                        }
                        value={overrides[selectedTypeId]?.full_prompt ?? ""}
                        onChange={(e) => handleFullPromptChange(selectedTypeId, e.target.value)}
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor={`extra-${selectedTypeId}`} className="text-xs text-stone-600">
                        Instructions additionnelles (ajoutées à la fin du prompt)
                      </Label>
                      <Textarea
                        id={`extra-${selectedTypeId}`}
                        className="min-h-[120px] border-stone-200 bg-stone-50 text-sm text-stone-900"
                        placeholder="Ex: insiste sur le ton ultra casual, évite de trop parler de Leafee, etc."
                        value={overrides[selectedTypeId]?.extra_instructions ?? ""}
                        onChange={(e) => handleExtraChange(selectedTypeId, e.target.value)}
                      />
                    </div>
                  </>
                )}
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
}

