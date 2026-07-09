# LM Moda — Catálogo Web (Next.js)

Frontend React/Next.js do catálogo de moda feminina, migrado do Streamlit.

## Stack

- Next.js 16 + React 19 + TypeScript
- Tailwind CSS 4
- Supabase (banco, auth, storage, RPCs)
- Mercado Pago PIX + WhatsApp checkout
- Deploy: Vercel (grátis)

## Desenvolvimento local

```bash
cd web
cp .env.local.example .env.local
# Preencha com credenciais do Supabase e Mercado Pago
npm install
npm run dev
```

Acesse http://localhost:3000

## Deploy no Vercel

1. Conecte o repositório `catalogo` no [Vercel](https://vercel.com)
2. Defina **Root Directory** como `web`
3. Configure as variáveis de ambiente:

| Variável | Descrição |
|----------|-----------|
| `NEXT_PUBLIC_SUPABASE_URL` | URL do projeto Supabase |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Chave anon do Supabase |
| `SUPABASE_SERVICE_ROLE_KEY` | Service role (server only) |
| `MERCADOPAGO_ACCESS_TOKEN` | Token MP para PIX |
| `MERCADOPAGO_WEBHOOK_URL` | URL da Edge Function webhook |
| `APP_BASE_URL` | URL de produção (ex: https://sua-loja.vercel.app) |
| `PAYMENTS_ENABLED` | `true` |
| `MELHOR_ENVIO_TOKEN` | Opcional — cotação de frete |

4. Após deploy, atualize `APP_BASE_URL` com a URL real
5. O webhook Mercado Pago continua na Edge Function Supabase (`supabase/functions/mercadopago-webhook`)

## Estrutura

```
web/
├── src/app/(loja)/     # Loja pública
├── src/app/admin/      # Painel admin
├── src/app/api/        # Checkout PIX, frete, pagamentos
├── src/lib/            # Lógica de negócio (profit, shipping, payments)
└── src/components/     # UI components
```

## Admin

Acesse `/admin/login` com usuário Supabase Auth (mesmo do Streamlit).

## Banco de dados

Usa as migrations existentes em `../supabase/migrations` — não recria o schema.
