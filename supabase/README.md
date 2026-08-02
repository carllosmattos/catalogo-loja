# Migrações Supabase

> **Fonte de verdade da loja em produção:**  
> `catalogo-loja-web/supabase/` (Next.js).  
> Esta pasta no repo Streamlit é espelho legado — **novas** migrations devem ir primeiro no web.

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
| 015 | [`migrations/015_customer_email.sql`](migrations/015_customer_email.sql) | E-mail do cliente (Mercado Pago) |
| 016 | [`migrations/016_orders_payments.sql`](migrations/016_orders_payments.sql) | Pedidos, PIX, reembolsos |
| 017 | [`migrations/017_repair_payment_rpcs.sql`](migrations/017_repair_payment_rpcs.sql) | Reparo se 016 parou no meio (RPC ausente) |
| 018 | [`migrations/018_fix_create_checkout_uuid.sql`](migrations/018_fix_create_checkout_uuid.sql) | Corrige UUID no checkout |
| 019 | [`migrations/019_store_banners.sql`](migrations/019_store_banners.sql) | Vários banners da loja + carrossel |
| 020 | [`migrations/020_fix_get_order_by_tracking.sql`](migrations/020_fix_get_order_by_tracking.sql) | Corrige RPC `get_order_by_tracking` (token da URL) |
| 021 | [`migrations/021_phone_lookup_and_payment_rpcs.sql`](migrations/021_phone_lookup_and_payment_rpcs.sql) | Telefone normalizado + RPCs de pedidos (reparo) |
| 023 | [`migrations/023_customer_address_fields.sql`](migrations/023_customer_address_fields.sql) | Endereço com campos separados (CEP, rua, etc.) |
| 024 | [`migrations/024_pix_orders.sql`](migrations/024_pix_orders.sql) | PIX com expiração (15 min), sync de status, anti-duplicata |
| 025 | [`migrations/025_shipping_zones.sql`](migrations/025_shipping_zones.sql) | Zonas de frete (grátis/pago/bloqueado) + endereço remetente |
| 026 | [`migrations/026_stock_reservation.sql`](migrations/026_stock_reservation.sql) | Reserva temporária de estoque durante o PIX |
| 027 | [`migrations/027_customer_delete_order.sql`](migrations/027_customer_delete_order.sql) | Cliente pode excluir pedido da lista (soft-delete) |
| 028 | [`migrations/028_melhor_envio_oauth.sql`](migrations/028_melhor_envio_oauth.sql) | Credenciais OAuth Melhor Envio (tokens com refresh) |

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
- E-mail em clientes → **015**
- Pagamentos PIX / pedidos → **016** + Edge Function `mercadopago-webhook`
- Erro `create_checkout_order not found` → rode **017**
- Erro `uuid_generate_v4 does not exist` → rode **018**
- Vários banners com carrossel no admin → **019**
- Erro ao abrir pedido pelo link `?order=` → **020**
- Login por telefone não encontra cliente / erro em Minhas compras → **021**
- Endereço estruturado no cadastro → **023**
- PIX expira em 15 min / botão Atualizar status não confirma pagamento → **024**
- Frete por região ou Melhor Envio → **025**
- Dois clientes comprando o último item ao mesmo tempo → **026**
- Cliente quer excluir pedido da lista (Minhas compras) → **027**
- Conectar Melhor Envio via OAuth (tokens com refresh) → **028**

## Secrets opcionais (Streamlit Cloud)

Além de `SUPABASE_URL` e `SUPABASE_ANON_KEY`, para pagamentos e frete:

```toml
MERCADOPAGO_ACCESS_TOKEN = "..."
MERCADOPAGO_WEBHOOK_URL = "https://<projeto>.supabase.co/functions/v1/mercadopago-webhook"
APP_BASE_URL = "https://seu-app.streamlit.app"
PAYMENTS_ENABLED = true

# Opcional — Melhor Envio (preferir OAuth no admin da loja web)
MELHOR_ENVIO_CLIENT_ID = "..."
MELHOR_ENVIO_CLIENT_SECRET = "..."
# MELHOR_ENVIO_TOKEN = "..."  # legado / teste rápido
```

Ative **Melhor Envio** em Admin → Frete e clique em **Conectar Melhor Envio** (OAuth).

## Projeto do zero

Rode **001 → 002 → 003** em sequência, uma query por arquivo.
