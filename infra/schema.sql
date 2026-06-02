-- ============================================================
--  ESTUAPP / Grupo Impacto — Esquema multi-tenant de asistentes
--  Correr esto en un Supabase NUEVO (de la agencia) para dejarlo listo.
--  Diseñado para migrar: todo cuelga de tenant_id (Corralón = tenant 1).
-- ============================================================
create extension if not exists vector;

-- Maestro de clientes/comercios (tenants)
create table if not exists tenants (
  id          bigserial primary key,
  slug        text unique,                 -- ej 'corralon-2-de-abril'
  nombre      text,
  tipo        text default 'cliente',      -- 'cliente' | 'demo'
  activo      boolean default true,
  config      jsonb default '{}'::jsonb,    -- descuento, whatsapp, web, instancia evolution, etc.
  created_at  timestamptz default now()
);

-- Base de conocimiento (RAG) por tenant
create table if not exists kb (
  id          bigserial primary key,
  tenant_id   bigint references tenants(id) on delete cascade,
  content     text,
  metadata    jsonb,
  embedding   vector(1536),
  created_at  timestamptz default now()
);
create index if not exists kb_emb_idx on kb using ivfflat (embedding vector_cosine_ops) with (lists = 10);
create index if not exists kb_tenant_idx on kb(tenant_id);

-- Pedidos por tenant
create table if not exists pedidos (
  id            bigserial primary key,
  tenant_id     bigint references tenants(id),
  nro           text,
  cliente       text,
  nombre_cliente text,
  items         jsonb,
  total_lista   numeric,
  total_final   numeric,
  entrega       text,
  pago          text,
  direccion     text,
  chat_id       text,
  estado        text default 'nuevo',
  created_at    timestamptz default now()
);
create index if not exists pedidos_tenant_idx on pedidos(tenant_id, created_at);

-- Sesiones de demo en vivo (modo prospección)
create table if not exists demo_tenants (
  chat_id     text primary key,
  nombre      text default '',
  rubro       text default '',
  brief       text default '',
  descuento   int  default 10,
  productos   jsonb default '[]'::jsonb,
  step        text default 'pedir_nombre',
  updated_at  timestamptz default now()
);

-- Historial de mensajes (auditoría / mejora / ventas perdidas)
create table if not exists mensajes (
  id          bigserial primary key,
  tenant_id   bigint,
  chat_id     text,
  rol         text,        -- 'in' (cliente) | 'out' (abril)
  texto       text,
  created_at  timestamptz default now()
);
create index if not exists mensajes_chat_idx on mensajes(chat_id, created_at);

-- Búsqueda semántica filtrada por tenant
create or replace function match_kb(query_embedding vector(1536), p_tenant bigint, match_count int default 5)
returns table(id bigint, content text, metadata jsonb, similarity float)
language plpgsql as $$
begin
  return query
  select k.id, k.content, k.metadata, 1 - (k.embedding <=> query_embedding) as similarity
  from kb k
  where k.tenant_id = p_tenant
  order by k.embedding <=> query_embedding
  limit match_count;
end; $$;

-- Seed: Corralón 2 de Abril como tenant 1
insert into tenants (slug, nombre, tipo, config)
values ('corralon-2-de-abril', 'Corralón 2 de Abril', 'cliente',
  '{"descuento_web":15,"whatsapp":"5492235938651","instancia":"ASISTENTEDEMOGERMAN","web":"grupoimpactomkt-pixel.github.io/corralon-2-de-abril"}'::jsonb)
on conflict (slug) do nothing;
