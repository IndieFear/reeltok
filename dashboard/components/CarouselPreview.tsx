"use client";

interface CarouselPreviewProps {
  slides: { base64: string; filename: string }[];
  onClose?: () => void;
}

export function CarouselPreview({ slides }: CarouselPreviewProps) {
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
        {slides.map((slide, i) => (
          <div
            key={i}
            className="relative aspect-[9/16] overflow-hidden rounded-lg border border-stone-200 bg-stone-100"
          >
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={`data:image/jpeg;base64,${slide.base64}`}
              alt={`Slide ${i + 1}`}
              className="w-full h-full object-cover"
            />
            <span className="absolute bottom-2 left-2 bg-black/60 text-white text-xs px-2 py-1 rounded">
              Slide {i + 1}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
