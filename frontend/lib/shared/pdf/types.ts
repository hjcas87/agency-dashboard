export interface PdfTemplate {
  id: number;
  logo_url: string | null;
  header_text: string | null;
  footer_text: string | null;
  bg_color: string;
  text_color: string;
  accent_color: string;
  is_default: boolean;
}

export interface PdfTemplateInput {
  logo_url?: string | null;
  header_text?: string | null;
  footer_text?: string | null;
  bg_color?: string;
  text_color?: string;
  accent_color?: string;
  is_default?: boolean;
}
