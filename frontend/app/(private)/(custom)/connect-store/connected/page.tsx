"use client";

import { useSearchParams } from "next/navigation";
import { Suspense } from "react";

import { Button } from "@/components/core/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/core/ui/card";
import Link from "next/link";

function ConnectedContent() {
  const searchParams = useSearchParams();
  const storeName = searchParams.get("store_name") ?? "Tu tienda";
  const error = searchParams.get("error");

  if (error) {
    return (
      <Card className="w-full max-w-md border-destructive/50">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl text-destructive">
            Error de conexión
          </CardTitle>
          <CardDescription>{error}</CardDescription>
        </CardHeader>
        <CardContent>
          <Button asChild className="w-full">
            <Link href="/(private)/(custom)/connect-store">
              Intentar de nuevo
            </Link>
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="w-full max-w-md">
      <CardHeader className="text-center">
        <CardTitle className="text-2xl text-green-600">
          ¡Tienda conectada!
        </CardTitle>
        <CardDescription>
          <strong>{storeName}</strong> se conectó correctamente a Mendri Loyalty
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="rounded-md border bg-muted p-4 text-sm">
          <p className="font-medium">Próximos pasos:</p>
          <ul className="mt-2 list-inside space-y-1 text-muted-foreground">
            <li>• Configurar la ratio de puntos</li>
            <li>• Configurar los emails de recuperación de carritos</li>
            <li>• Ver las métricas del programa</li>
          </ul>
        </div>
        <Button asChild className="w-full">
          <Link href="/">Ir al dashboard</Link>
        </Button>
      </CardContent>
    </Card>
  );
}

export default function ConnectedPage() {
  return (
    <div className="flex min-h-[80vh] items-center justify-center p-4">
      <Suspense
        fallback={
          <Card className="w-full max-w-md">
            <CardHeader className="text-center">
              <CardTitle>Conectando...</CardTitle>
            </CardHeader>
          </Card>
        }
      >
        <ConnectedContent />
      </Suspense>
    </div>
  );
}
