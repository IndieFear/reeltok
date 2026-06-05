"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ImageLibrary } from "@/components/ImageLibrary";
import { ChevronLeft, Images } from "lucide-react";

export default function LibraryPage() {
  return (
    <div className="min-h-screen bg-stone-50 text-stone-950">
      <div className="mx-auto max-w-6xl px-4 py-6 sm:px-6 lg:px-8">
        <header className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <div className="mb-2 inline-flex items-center gap-2 rounded-full border border-stone-200 bg-white px-3 py-1 text-xs font-medium text-stone-600">
              <Images className="h-3.5 w-3.5" />
              Assets
            </div>
            <h1 className="text-2xl font-semibold tracking-tight">Bibliothèque d&apos;images</h1>
            <p className="mt-1 text-sm text-stone-500">
              Ajoute des photos une fois, réutilise-les dans l&apos;éditeur et l&apos;automatisation.
            </p>
          </div>
          <div className="flex gap-2">
            <Link href="/editor">
              <Button variant="outline" className="border-stone-200">
                <ChevronLeft className="h-4 w-4" />
                Éditeur
              </Button>
            </Link>
            <Link href="/automation">
              <Button variant="outline" className="border-stone-200">
                Automatisation
              </Button>
            </Link>
          </div>
        </header>

        <Card className="border-stone-200 bg-white shadow-sm">
          <CardHeader>
            <CardTitle className="text-base">Mes images</CardTitle>
          </CardHeader>
          <CardContent>
            <ImageLibrary />
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
