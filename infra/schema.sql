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

-- Capa editable de productos por el superadmin (alta/edicion/borrado SOBRE el catalogo base estatico).
-- buscarPrecio mezcla: catalogo base (Excel/GitHub) + estos overrides.
create table if not exists productos (
  id          bigserial primary key,
  tenant_id   bigint references tenants(id) on delete cascade,
  clave       text,            -- nombre normalizado: matchea el catalogo base para editar/borrar; o id propio si es alta nueva
  n           text,            -- nombre para mostrar
  p           numeric,         -- precio lista
  w           numeric,         -- precio web efectivo (si null se calcula -15%)
  c           text default '', -- rubro/categoria
  activo      boolean default true,  -- false = borrado/oculto
  origen      text default 'admin',
  updated_at  timestamptz default now()
);
create unique index if not exists productos_tenant_clave_idx on productos(tenant_id, clave);

-- Alias / sinonimos para la busqueda (ej "ceresita" -> "hidrofugo", "pastina" -> "pegamento")
create table if not exists aliases (
  id          bigserial primary key,
  tenant_id   bigint references tenants(id) on delete cascade,
  alias       text,            -- lo que escribe el cliente
  canonico    text,            -- termino real del catalogo
  updated_at  timestamptz default now()
);
create unique index if not exists aliases_tenant_alias_idx on aliases(tenant_id, alias);

-- Usuarios con rol por tenant (super_admin = dueña; a futuro empleado/repartidor/contador).
-- Quien no esta aca = cliente comun. El Router lee el numero -> rol -> habilita herramientas.
create table if not exists usuarios (
  id          bigserial primary key,
  tenant_id   bigint references tenants(id) on delete cascade,
  telefono    text,
  rol         text default 'cliente',   -- super_admin | empleado | repartidor | contador | cliente
  nombre      text,
  activo      boolean default true,
  created_at  timestamptz default now()
);
create unique index if not exists usuarios_tenant_tel_idx on usuarios(tenant_id, telefono);

-- Bitacora de cambios de admin (quien, que, antes, despues, cuando) — barandilla obligatoria.
create table if not exists audit_log (
  id          bigserial primary key,
  tenant_id   bigint,
  telefono    text,
  rol         text,
  accion      text,        -- actualizarPrecio | altaProducto | bajaProducto | agregarSinonimo | pausarBot ...
  detalle     jsonb,
  antes       jsonb,
  despues     jsonb,
  created_at  timestamptz default now()
);
create index if not exists audit_tenant_idx on audit_log(tenant_id, created_at);

-- Seed: Corralón 2 de Abril como tenant 1
insert into tenants (slug, nombre, tipo, config)
values ('corralon-2-de-abril', 'Corralón 2 de Abril', 'cliente',
  '{"descuento_web":15,"whatsapp":"5492235938651","instancia":"ASISTENTEDEMOGERMAN","web":"grupoimpactomkt-pixel.github.io/corralon-2-de-abril"}'::jsonb)
on conflict (slug) do nothing;

-- Alias util de arranque (hidrofugo se pide como "ceresita")
insert into aliases (tenant_id, alias, canonico) values
  (1,'ceresita','hidrofugo'),(1,'ceresit','hidrofugo'),(1,'serecita','hidrofugo')
on conflict (tenant_id, alias) do nothing;

-- Seed: Micaela (dueña) = super_admin; German (Grupo Impacto) = soporte
insert into usuarios (tenant_id, telefono, rol, nombre) values
  (1,'5492236927655','super_admin','Micaela'),
  (1,'5492235262423','soporte','German (Soporte Impacto)')
on conflict (tenant_id, telefono) do nothing;
