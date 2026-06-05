"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { Button } from "@/components/ui/button";
import {
  deleteUserImage,
  listUserImages,
  uploadUserImage,
  userImagePreviewUrl,
  type UserImage,
} from "@/lib/api";
import { toast } from "sonner";
import { ImagePlus, Loader2, Trash2 } from "lucide-react";

interface ImageLibraryProps {
  onSelect?: (image: UserImage) => void;
  selectedId?: string | null;
  compact?: boolean;
  title?: string;
}

export function ImageLibrary({
  onSelect,
  selectedId,
  compact = false,
  title = "Bibliothèque d'images",
}: ImageLibraryProps) {
  const [images, setImages] = useState<UserImage[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      const items = await listUserImages();
      setImages(items);
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "Erreur chargement bibliothèque");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  const handleUpload = useCallback(
    async (file: File) => {
      setUploading(true);
      try {
        const created = await uploadUserImage(file);
        setImages((prev) => [created, ...prev]);
        toast.success("Image ajoutée à la bibliothèque");
      } catch (e) {
        toast.error(e instanceof Error ? e.message : "Upload impossible");
      } finally {
        setUploading(false);
      }
    },
    [],
  );

  const handleDelete = useCallback(
    async (id: string) => {
      setDeletingId(id);
      try {
        await deleteUserImage(id);
        setImages((prev) => prev.filter((img) => img.id !== id));
        toast.success("Image supprimée");
      } catch (e) {
        toast.error(e instanceof Error ? e.message : "Suppression impossible");
      } finally {
        setDeletingId(null);
      }
    },
    [],
  );

  const gridClass = compact
    ? "grid grid-cols-3 gap-2 sm:grid-cols-4"
    : "grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5";

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between gap-2">
        <p className="text-sm font-medium text-stone-900">{title}</p>
        <div className="flex gap-2">
          <input
            ref={fileInputRef}
            type="file"
            accept="image/jpeg,image/png,image/webp"
            className="hidden"
            onChange={(e) => {
              const file = e.target.files?.[0];
              if (file) void handleUpload(file);
              e.target.value = "";
            }}
          />
          <Button
            type="button"
            variant="outline"
            size="sm"
            disabled={uploading}
            onClick={() => fileInputRef.current?.click()}
            className="border-stone-200"
          >
            {uploading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <ImagePlus className="h-4 w-4" />
            )}
            <span className="ml-1.5">{uploading ? "Ajout…" : "Ajouter"}</span>
          </Button>
        </div>
      </div>

      {loading ? (
        <p className="text-sm text-stone-500">Chargement…</p>
      ) : images.length === 0 ? (
        <p className="rounded-xl border border-dashed border-stone-200 bg-stone-50 px-4 py-8 text-center text-sm text-stone-500">
          Aucune image sauvegardée. Ajoute des photos pour les réutiliser dans l&apos;éditeur et
          l&apos;automatisation.
        </p>
      ) : (
        <div className={gridClass}>
          {images.map((image) => {
            const isSelected = selectedId === image.id;
            return (
              <div
                key={image.id}
                className={`group overflow-hidden rounded-xl border bg-white shadow-sm transition ${
                  isSelected
                    ? "border-stone-900 ring-2 ring-stone-900/10"
                    : "border-stone-200 hover:border-stone-400"
                }`}
              >
                <button
                  type="button"
                  onClick={() => onSelect?.(image)}
                  className="block w-full text-left"
                  title={image.filename}
                >
                  <div className="relative aspect-[9/16] overflow-hidden bg-stone-100">
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img
                      src={userImagePreviewUrl(image.id)}
                      alt={image.filename}
                      className="h-full w-full object-cover"
                      loading="lazy"
                    />
                  </div>
                  <div className="truncate px-2 py-1.5 text-xs text-stone-600">
                    {image.filename}
                  </div>
                </button>
                <div className="flex justify-end border-t border-stone-100 px-2 py-1">
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    className="h-7 px-2 text-stone-500 hover:text-red-600"
                    disabled={deletingId === image.id}
                    onClick={() => void handleDelete(image.id)}
                  >
                    {deletingId === image.id ? (
                      <Loader2 className="h-3.5 w-3.5 animate-spin" />
                    ) : (
                      <Trash2 className="h-3.5 w-3.5" />
                    )}
                  </Button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
