# Migrações Supabase

Scripts versionados em ordem numérica. Execute no **SQL Editor** do Supabase.

## Ordem de execução

| # | Arquivo | Quando rodar |
|---|---------|--------------|
| 001 | [`migrations/001_initial_schema.sql`](migrations/001_initial_schema.sql) | Projeto novo — tabelas + RLS |
| 002 | [`migrations/002_storage.sql`](migrations/002_storage.sql) | Após o 001 — bucket de fotos |
| 003 | [`migrations/003_lm_branding.sql`](migrations/003_lm_branding.sql) | Após 001/002 — nome e cores LM |
| 004 | [`migrations/004_gift_image.sql`](migrations/004_gift_image.sql) | Foto do brinde (`image_url`) |
| 005 | [`migrations/005_sales.sql`](migrations/005_sales.sql) | Vendas + estoque + relatórios |
| 006 | [`migrations/006_lifecycle.sql`](migrations/006_lifecycle.sql) | Arquivar brindes + cancelar vendas |
| 007 | [`migrations/007_sale_quantity.sql`](migrations/007_sale_quantity.sql) | Quantidade de peças por venda |
| 008 | [`migrations/008_customers.sql`](migrations/008_customers.sql) | Clientes (CPF) + vínculo nas vendas |
| 009 | [`migrations/009_customer_address.sql`](migrations/009_customer_address.sql) | Endereço + login por telefone (RPC) |
| 010 | [`migrations/010_categories.sql`](migrations/010_categories.sql) | Categorias + filtro no catálogo |
| 011 | [`migrations/011_banners.sql`](migrations/011_banners.sql) | Banner padrão + banner por promoção |
| 012 | [`migrations/012_product_sizes_and_galleries.sql`](migrations/012_product_sizes_and_galleries.sql) | Estoque P/M/G + galerias de fotos |
| 013 | [`migrations/013_sale_size_stock.sql`](migrations/013_sale_size_stock.sql) | Vendas decrementam estoque por tamanho |
| 014 | [`migrations/014_size_unique.sql`](migrations/014_size_unique.sql) | Tamanho único (U) + P/M/G |

## Já rodou o schema antes?

Não execute o **001** de novo. Rode apenas o que ainda falta:

- Bucket de fotos ausente → **002**
- Cores/nome ainda genéricos → **003**
- Foto de brinde (campo `image_url`) → **004**
- Módulo de vendas → **005**
- Arquivar brindes / cancelar vendas → **006**
- Quantidade por venda → **007**
- Clientes e CPF → **008**
- Endereço e login por telefone → **009**
- Categorias de produtos → **010**
- Banners (padrão e promoções) → **011**
- Estoque por tamanho e galerias → **012**
- Vendas por tamanho (RPC) → **013**
- Tamanho único (U) → **014**

## Projeto do zero

Rode **001 → 002 → 003** em sequência, uma query por arquivo.
