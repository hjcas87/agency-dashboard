"use client";

import { useState, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense } from "react";

import { Button } from "@/components/core/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/core/ui/card";
import { Input } from "@/components/core/ui/input";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

function ConnectForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const urlError = searchParams.get("error");

  const [storeId, setStoreId] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(urlError);

  // Show URL error on mount if present
  useEffect(() => {
    if (urlError) {
      setError(decodeURIComponent(urlError));
    }
  }, [urlError]);

  const handleConnect = async () => {
    if (!storeId.trim()) {
      setError("Ingresa el ID de tu tienda");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const res = await fetch(
        `${API_URL}/api/v1/tiendanube/auth/initiate?store_id=${encodeURIComponent(storeId)}`,
        { method: "GET" },
      );

      if (!res.ok) {
        const err = await res.json().catch(() => null);
        throw new Error(
          err?.detail ?? "Error al iniciar la conexión. Verifica el ID de tu tienda.",
        );
      }

      const data = await res.json();

      // Redirect to Tiendanube authorization page
      window.location.href = data.auth_url;
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Error inesperado");
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      void handleConnect();
    }
  };

  return (
    <div className="flex min-h-[80vh] items-center justify-center p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl">Conectar con Tiendanube</CardTitle>
          <CardDescription>
            Ingresa el ID de tu tienda para conectarla con Mendri Loyalty
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label
              htmlFor="storeId"
              className="mb-2 block text-sm font-medium"
            >
              ID de la tienda
            </label>
            <Input
              id="storeId"
              type="text"
              placeholder="Ej: 123456"
              value={storeId}
              onChange={(e) => setStoreId(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={loading}
            />
            <p className="mt-1 text-xs text-muted-foreground">
              Lo encontrás en la URL de tu admin de Tiendanube o en{" "}
              <a
                href="https://www.tiendanube.com/admin/"
                target="_blank"
                rel="noopener noreferrer"
                className="text-primary underline hover:text-primary/80"
              >
                tu panel de Tiendanube
              </a>
            </p>
          </div>

          {error && (
            <div className="rounded-md border border-destructive/50 bg-destructive/10 p-3 text-sm text-destructive">
              {error}
            </div>
          )}

          <Button
            className="w-full"
            onClick={() => void handleConnect()}
            disabled={loading}
          >
            {loading ? "Conectando..." : "Conectar tienda"}
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}

export default function ConnectStorePage() {
  return (
    <Suspense
      fallback={
        <div className="flex min-h-[80vh] items-center justify-center p-4">
          <p>Cargando...</p>
        </div>
      }
    >
      <ConnectForm />
    </Suspense>
  );
}
