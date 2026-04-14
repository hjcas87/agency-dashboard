"use client";

import { useEffect, useRef, useState } from "react";
import { toast } from "sonner";
import { IconRestore, IconDeviceFloppy, IconUpload, IconX, IconPhoto } from "@tabler/icons-react";

import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/core/ui/card";
import { Button } from "@/components/core/ui/button";
import { Label } from "@/components/core/ui/label";
import { Input } from "@/components/core/ui/input";
import { Textarea } from "@/components/core/ui/textarea";
import { Separator } from "@/components/core/ui/separator";
import { Badge } from "@/components/core/ui/badge";

import { PdfTemplate, PdfTemplateInput } from "@/lib/shared/pdf/types";
import { PDF_TEMPLATE_MESSAGES } from "@/lib/messages";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function PdfTemplatesPage() {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [template, setTemplate] = useState<PdfTemplate | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [uploadingLogo, setUploadingLogo] = useState(false);

  const [formData, setFormData] = useState<PdfTemplateInput>({
    logo_url: "",
    header_text: "",
    footer_text: "",
    bg_color: "#ffffff",
    text_color: "#1a1a1a",
    accent_color: "#2563eb",
  });

  useEffect(() => {
    loadTemplate();
  }, []);

  async function loadTemplate() {
    try {
      const res = await fetch(`${API_BASE}/api/v1/pdf/templates`);
      if (res.ok) {
        const data = await res.json();
        setTemplate(data);
        setFormData({
          logo_url: data.logo_url || "",
          header_text: data.header_text || "",
          footer_text: data.footer_text || "",
          bg_color: data.bg_color,
          text_color: data.text_color,
          accent_color: data.accent_color,
        });
      }
    } catch {
      toast.error(PDF_TEMPLATE_MESSAGES.loadError.title, {
        description: PDF_TEMPLATE_MESSAGES.loadError.description,
      });
    } finally {
      setLoading(false);
    }
  }

  async function handleSave() {
    setSaving(true);
    try {
      // Convert empty strings to null for optional fields
      const payload = {
        logo_url: formData.logo_url || null,
        header_text: formData.header_text || null,
        footer_text: formData.footer_text || null,
        bg_color: formData.bg_color,
        text_color: formData.text_color,
        accent_color: formData.accent_color,
      };

      const res = await fetch(`${API_BASE}/api/v1/pdf/templates`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (res.ok) {
        const data = await res.json();
        setTemplate(data);
        toast.success(PDF_TEMPLATE_MESSAGES.saveSuccess.title, {
          description: PDF_TEMPLATE_MESSAGES.saveSuccess.description,
        });
      } else {
        const error = await res.json().catch(() => ({ detail: "" }));
        toast.error(PDF_TEMPLATE_MESSAGES.saveError.title, {
          description: error.detail || PDF_TEMPLATE_MESSAGES.saveError.description,
        });
      }
    } catch {
      toast.error(PDF_TEMPLATE_MESSAGES.saveError.title, {
        description: PDF_TEMPLATE_MESSAGES.saveError.description,
      });
    } finally {
      setSaving(false);
    }
  }

  async function handleReset() {
    setSaving(true);
    try {
      const res = await fetch(`${API_BASE}/api/v1/pdf/templates/reset`, {
        method: "POST",
      });
      if (res.ok) {
        const data = await res.json();
        setTemplate(data);
        setFormData({
          logo_url: "",
          header_text: "",
          footer_text: "",
          bg_color: data.bg_color,
          text_color: data.text_color,
          accent_color: data.accent_color,
        });
        toast.success(PDF_TEMPLATE_MESSAGES.resetSuccess.title, {
          description: PDF_TEMPLATE_MESSAGES.resetSuccess.description,
        });
      }
    } catch {
      toast.error(PDF_TEMPLATE_MESSAGES.resetError.title, {
        description: PDF_TEMPLATE_MESSAGES.resetError.description,
      });
    } finally {
      setSaving(false);
    }
  }

  async function handleLogoUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploadingLogo(true);
    try {
      const form = new FormData();
      form.append("file", file);

      const res = await fetch(`${API_BASE}/api/v1/pdf/templates/logo`, {
        method: "POST",
        body: form,
      });

      if (res.ok) {
        const data = await res.json();
        setFormData({ ...formData, logo_url: data.logo_url });
        toast.success(PDF_TEMPLATE_MESSAGES.logoUploadSuccess.title, {
          description: PDF_TEMPLATE_MESSAGES.logoUploadSuccess.description,
        });
      } else {
        const error = await res.json().catch(() => ({ detail: "" }));
        toast.error(PDF_TEMPLATE_MESSAGES.logoUploadError.title, {
          description: error.detail || PDF_TEMPLATE_MESSAGES.logoUploadError.description,
        });
      }
    } catch {
      toast.error(PDF_TEMPLATE_MESSAGES.logoUploadError.title, {
        description: PDF_TEMPLATE_MESSAGES.logoUploadError.description,
      });
    } finally {
      setUploadingLogo(false);
    }
  }

  function removeLogo() {
    setFormData({ ...formData, logo_url: "" });
    if (fileInputRef.current) fileInputRef.current.value = "";
  }

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center gap-2 p-8">
        <p className="text-sm text-muted-foreground">
          {PDF_TEMPLATE_MESSAGES.loading.title}
        </p>
        <p className="text-xs text-muted-foreground">
          {PDF_TEMPLATE_MESSAGES.loading.description}
        </p>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-8 px-4 max-w-3xl">
      <Card>
        <CardHeader>
          <CardTitle>{PDF_TEMPLATE_MESSAGES.cardTitle}</CardTitle>
          <CardDescription>{PDF_TEMPLATE_MESSAGES.cardDescription}</CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col gap-6">
          {/* Logo Upload */}
          <div className="flex flex-col gap-2">
            <Label>{PDF_TEMPLATE_MESSAGES.labels.logo}</Label>
            {formData.logo_url ? (
              <div className="flex items-center gap-3 rounded-lg border p-3">
                <div className="flex size-16 items-center justify-center overflow-hidden rounded border bg-muted">
                  <img
                    src={`${API_BASE}${formData.logo_url}`}
                    alt="Logo"
                    className="size-full object-contain"
                  />
                </div>
                <div className="flex-1">
                  <p className="text-sm font-medium">
                    {PDF_TEMPLATE_MESSAGES.logoConfigured}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {formData.logo_url.split("/").pop()}
                  </p>
                </div>
                <Button variant="ghost" size="sm" onClick={removeLogo}>
                  <IconX className="size-4" data-icon="inline-start" />
                </Button>
              </div>
            ) : (
              <div
                className="flex flex-col items-center justify-center gap-2 rounded-lg border-2 border-dashed p-6 cursor-pointer hover:border-primary transition-colors"
                onClick={() => fileInputRef.current?.click()}
              >
                <IconPhoto className="size-8 text-muted-foreground" />
                <p className="text-sm text-muted-foreground">
                  {PDF_TEMPLATE_MESSAGES.clickToUploadLogo}
                </p>
              </div>
            )}
            <input
              ref={fileInputRef}
              type="file"
              accept="image/png,image/jpeg,image/svg+xml,image/webp"
              onChange={handleLogoUpload}
              className="hidden"
              disabled={uploadingLogo}
            />
            {uploadingLogo && (
              <Badge variant="secondary">
                {PDF_TEMPLATE_MESSAGES.uploadingLogo}
              </Badge>
            )}
          </div>

          <Separator />

          {/* Colors */}
          <div className="flex flex-col gap-2">
            <Label>{PDF_TEMPLATE_MESSAGES.labels.bgColor}</Label>
            <div className="flex items-center gap-3">
              <input
                type="color"
                value={formData.bg_color}
                onChange={(e) => setFormData({ ...formData, bg_color: e.target.value })}
                className="size-10 cursor-pointer rounded border"
              />
              <Input
                type="text"
                value={formData.bg_color}
                onChange={(e) => setFormData({ ...formData, bg_color: e.target.value })}
                className="w-32"
              />
            </div>
          </div>

          <div className="flex flex-col gap-2">
            <Label>{PDF_TEMPLATE_MESSAGES.labels.textColor}</Label>
            <div className="flex items-center gap-3">
              <input
                type="color"
                value={formData.text_color}
                onChange={(e) => setFormData({ ...formData, text_color: e.target.value })}
                className="size-10 cursor-pointer rounded border"
              />
              <Input
                type="text"
                value={formData.text_color}
                onChange={(e) => setFormData({ ...formData, text_color: e.target.value })}
                className="w-32"
              />
            </div>
          </div>

          <div className="flex flex-col gap-2">
            <Label>{PDF_TEMPLATE_MESSAGES.labels.accentColor}</Label>
            <div className="flex items-center gap-3">
              <input
                type="color"
                value={formData.accent_color}
                onChange={(e) => setFormData({ ...formData, accent_color: e.target.value })}
                className="size-10 cursor-pointer rounded border"
              />
              <Input
                type="text"
                value={formData.accent_color}
                onChange={(e) => setFormData({ ...formData, accent_color: e.target.value })}
                className="w-32"
              />
            </div>
          </div>

          <Separator />

          {/* Texts */}
          <div className="flex flex-col gap-2">
            <Label>{PDF_TEMPLATE_MESSAGES.labels.headerText}</Label>
            <Textarea
              value={formData.header_text || ""}
              onChange={(e) => setFormData({ ...formData, header_text: e.target.value })}
              placeholder={PDF_TEMPLATE_MESSAGES.labels.headerTextPlaceholder}
              rows={3}
            />
          </div>

          <div className="flex flex-col gap-2">
            <Label>{PDF_TEMPLATE_MESSAGES.labels.footerText}</Label>
            <Textarea
              value={formData.footer_text || ""}
              onChange={(e) => setFormData({ ...formData, footer_text: e.target.value })}
              placeholder={PDF_TEMPLATE_MESSAGES.labels.footerTextPlaceholder}
              rows={3}
            />
          </div>
        </CardContent>
        <CardFooter className="flex justify-between">
          <Button variant="outline" onClick={handleReset} disabled={saving}>
            <IconRestore className="size-4" data-icon="inline-start" />
            {PDF_TEMPLATE_MESSAGES.labels.restoreButton}
          </Button>
          <Button onClick={handleSave} disabled={saving}>
            <IconDeviceFloppy className="size-4" data-icon="inline-start" />
            {PDF_TEMPLATE_MESSAGES.labels.saveButton}
          </Button>
        </CardFooter>
      </Card>
    </div>
  );
}
