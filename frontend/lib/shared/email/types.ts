export interface EmailTemplate {
  id: number;
  name: string;
  subject: string;
  body: string;
  is_default: boolean;
}

export interface EmailTemplateInput {
  name: string;
  subject: string;
  body: string;
  is_default?: boolean;
}

export interface EmailSendRequest {
  to: string;
  cc?: string | null;
  subject: string;
  body: string;
  html_body?: string | null;
  attach_proposal_pdf?: number | null;
}
