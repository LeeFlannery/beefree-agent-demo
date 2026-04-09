import { z } from 'zod'

// ---------------------------------------------------------------------------
// BEE JSON module types
// ---------------------------------------------------------------------------

const ImageModuleSchema = z.object({
  type: z.literal('mailup-bee-newsletter-modules-image'),
  descriptor: z.object({
    image: z.object({
      src: z.string(),
      alt: z.string().optional(),
      href: z.string().optional(),
      width: z.string().optional(),
    }),
    style: z.record(z.string()).optional(),
  }),
})

const TextModuleSchema = z.object({
  type: z.literal('mailup-bee-newsletter-modules-text'),
  descriptor: z.object({
    text: z.object({ html: z.string() }),
    style: z.record(z.string()).optional(),
  }),
})

const ButtonModuleSchema = z.object({
  type: z.literal('mailup-bee-newsletter-modules-button'),
  descriptor: z.object({
    button: z.object({
      label: z.string(),
      href: z.string().optional(),
      style: z.record(z.string()).optional(),
    }),
  }),
})

const ModuleSchema = z.union([ImageModuleSchema, TextModuleSchema, ButtonModuleSchema])

const ColumnSchema = z.object({
  id: z.string(),
  modules: z.array(ModuleSchema),
  style: z.record(z.string()).optional(),
})

const RowSchema = z.object({
  id: z.string(),
  cells: z.array(z.number()),
  columns: z.array(ColumnSchema),
  style: z.record(z.string()).optional(),
})

// ---------------------------------------------------------------------------
// Full template
// ---------------------------------------------------------------------------

export const EmailTemplateSchema = z.object({
  id: z.string(),
  name: z.string(),
  subject: z.string(),
  theme: z.string(),
  createdAt: z.string(),
  updatedAt: z.string().optional(),
  tags: z.array(z.string()),
  page: z.object({
    body: z.object({
      backgroundColor: z.string().optional(),
      contentWidth: z.string().optional(),
      rows: z.array(RowSchema),
    }),
    template: z.object({
      name: z.string(),
      version: z.string(),
      pluginVersion: z.string(),
    }),
  }),
})

export type EmailTemplate = z.infer<typeof EmailTemplateSchema>

// ---------------------------------------------------------------------------
// Template stub (list view)
// ---------------------------------------------------------------------------

export const TemplateStubSchema = z.object({
  id: z.string(),
  name: z.string(),
  theme: z.string(),
  createdAt: z.string(),
  tags: z.array(z.string()),
  thumbnailUrl: z.string().optional(),
})

export type TemplateStub = z.infer<typeof TemplateStubSchema>

// ---------------------------------------------------------------------------
// Tool result payloads — what arrives in {"type":"tool_result","content":{...}}
// ---------------------------------------------------------------------------

export const CreateEmailResultSchema = EmailTemplateSchema
export const GetTemplateResultSchema = EmailTemplateSchema

export const ListTemplatesResultSchema = z.object({
  templates: z.array(TemplateStubSchema),
  total: z.number(),
})

export const UpdateSectionResultSchema = z.object({
  templateId: z.string(),
  section: z.object({
    id: z.string(),
    updatedAt: z.string(),
    column: ColumnSchema,
  }),
  success: z.boolean(),
})

export const MCPToolResultSchema = z.union([
  CreateEmailResultSchema,
  ListTemplatesResultSchema,
  UpdateSectionResultSchema,
])

export type MCPToolResult = z.infer<typeof MCPToolResultSchema>
