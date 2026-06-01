# LM Moda — Catálogo Streamlit + Supabase + WhatsApp

Catálogo mobile-first para Instagram. Clientes navegam, montam carrinho e finalizam pelo WhatsApp. A loja gerencia produtos, promoções, brindes, vendas e lucro em um painel admin com login.

Repositório: [github.com/carllosmattos/catalogo-loja](https://github.com/carllosmattos/catalogo-loja)

## Branches

| Branch | Ambiente | Uso |
|--------|----------|-----|
| `main` | **Produção (PRD)** | Deploy no Streamlit Cloud — link na bio do Instagram |
| `dev` | **Desenvolvimento** | Testes e novas funcionalidades antes de ir para produção |

Fluxo sugerido: desenvolver em `dev` → validar → merge em `main` → redeploy automático do PRD.

## Funcionalidades

### Catálogo público

- Layout mobile-first (iPhone / Instagram)
- Identidade da loja: banner no catálogo, cores (logo só como favicon)
- Produtos com foto, preço, estoque, frete e descrição no card
- Promoções (% ou valor fixo) e brindes visíveis no card
- **Carrinho**: adicionar peças, alterar quantidade, remover
- **Comprar agora** (item único) ou **Finalizar carrinho** via WhatsApp
- **Minha conta**: login por telefone, nome, CPF e endereço (autofill em pedidos)
- **Filtro por categoria** e **paginação** (20 peças por página)
- **Grade 2 colunas** no catálogo (mobile-friendly)
- Mensagem WhatsApp com peças, promoções, brindes e totais

### Painel admin

| Página | Função |
|--------|--------|
| Login | Autenticação Supabase (só admin) |
| Produtos | CRUD, fotos, estoque, arquivar / duplicar |
| Promoções | CRUD, arquivar |
| Brindes | CRUD com foto, estoque, arquivar |
| Loja | Nome, banner, cores, WhatsApp |
| Lucro & Margem | Custo, margem, potencial e realizado no mês |
| Vendas | Registrar venda, CPF, quantidade, cancelar com estorno |

## Stack

| Serviço | Uso | Custo |
|---------|-----|-------|
| [Streamlit Community Cloud](https://share.streamlit.io) | Hospedagem | Grátis |
| [Supabase](https://supabase.com) | Banco, auth, storage | Grátis (tier free) |
| WhatsApp (`wa.me`) | Pedidos | Grátis |

## Setup local

### 1. Clonar e instalar

```bash
git clone https://github.com/carllosmattos/catalogo-loja.git
cd catalogo-loja
pip install -r requirements.txt
```

### 2. Configurar Supabase

1. Crie um projeto em [supabase.com](https://supabase.com) (plano Free)
2. No **SQL Editor**, execute as migrações em ordem — veja [`supabase/README.md`](supabase/README.md):

   | # | Arquivo |
   |---|---------|
   | 001 | `001_initial_schema.sql` — tabelas + RLS |
   | 002 | `002_storage.sql` — bucket de fotos |
   | 003 | `003_lm_branding.sql` — branding LM |
   | 004 | `004_gift_image.sql` — foto do brinde |
   | 005 | `005_sales.sql` — vendas + estoque |
   | 006 | `006_lifecycle.sql` — arquivar / cancelar |
   | 007 | `007_sale_quantity.sql` — quantidade por venda |
   | 008 | `008_customers.sql` — clientes + CPF |
   | 009 | `009_customer_address.sql` — endereço + login por telefone |
   | 010 | `010_categories.sql` — categorias + filtro no catálogo |
   | 011 | `011_banners.sql` — banner padrão e por promoção |

3. Em **Authentication > Users**, crie o usuário admin
4. Copie **URL** e **anon key** em Settings → API

> As migrações ficam versionadas no GitHub, mas **não rodam sozinhas** — é preciso executá-las manualmente no Supabase (local e produção usam o mesmo projeto ou projetos separados, conforme sua escolha).

### 3. Secrets locais

Copie `secrets.toml.example` para `.streamlit/secrets.toml`:

```toml
SUPABASE_URL = "https://xxxxx.supabase.co"
SUPABASE_ANON_KEY = "eyJ..."
```

O arquivo `.streamlit/secrets.toml` está no `.gitignore` e **nunca** deve ir para o GitHub.

### 4. Rodar localmente

```bash
streamlit run app.py
```

| Página | URL local |
|--------|-----------|
| Catálogo | http://localhost:8501 |
| Admin | http://localhost:8501/Admin_Login |

## Deploy (Streamlit Cloud)

### Produção (`main`)

1. Conecte o repo em [share.streamlit.io](https://share.streamlit.io)
2. Branch: **`main`**
3. Main file: **`app.py`**
4. Em **Settings → Secrets**:

```toml
SUPABASE_URL = "https://xxxxx.supabase.co"
SUPABASE_ANON_KEY = "eyJ..."
```

5. Confirme que todas as migrações (001–009) foram aplicadas no Supabase de produção

### Desenvolvimento (`dev`) — opcional

Crie um segundo app no Streamlit Cloud apontando para a branch **`dev`**, com os mesmos secrets (ou um Supabase de staging separado).

| Página | URL |
|--------|-----|
| Catálogo (clientes) | `https://seu-app.streamlit.app/` |
| Admin | `https://seu-app.streamlit.app/Admin_Login` |

## Estrutura do projeto

```
catalogo/
├── app.py                      # Catálogo público (catálogo, carrinho, minha conta)
├── pages/                      # Painel admin
│   ├── 1_Admin_Login.py
│   ├── 2_Admin_Produtos.py
│   ├── 3_Admin_Promocoes.py
│   ├── 4_Admin_Brindes.py
│   ├── 5_Admin_Loja.py
│   ├── 6_Admin_Lucro.py
│   └── 7_Admin_Vendas.py
├── lib/
│   ├── auth.py                 # Login admin
│   ├── branding.py             # Logo e identidade
│   ├── cart.py                 # Carrinho (session)
│   ├── catalog.py              # Produtos, promoções, brindes
│   ├── catalog_display.py      # Cards HTML
│   ├── customer_session.py     # Login cliente por telefone
│   ├── customers.py            # CPF e cadastro admin
│   ├── profit.py               # Cálculo de lucro
│   ├── sales.py                # Registro de vendas
│   ├── theme.py                # CSS mobile-first
│   ├── utils.py                # CPF, moeda
│   └── whatsapp.py             # Mensagens wa.me
├── supabase/
│   ├── README.md               # Ordem das migrações
│   └── migrations/             # Scripts SQL versionados
├── resources/                  # Assets estáticos (logo)
├── requirements.txt
├── CHANGELOG.md
└── secrets.toml.example
```

## Fluxo de compra

1. Cliente abre o link do catálogo (Instagram)
2. (Opcional) Entra em **Minha conta** com telefone — dados salvos para próximos pedidos
3. Adiciona peças ao **Carrinho** ou usa **Comprar agora** em um item
4. Toca em **Finalizar no WhatsApp** — abre conversa com mensagem pronta
5. Loja registra a venda no painel **Vendas** (estoque baixa automaticamente)

## Cálculo de lucro

```
custo_peça = preço_compra + frete_compra
custo_brindes = Σ (preço_brinde + frete_brinde) × quantidade
preço_catálogo = preço_venda + repasse_brinde
preço_final = preço_catálogo - desconto + frete_cliente
lucro = preço_final - custo_peça - custo_brindes
```

Detalhes na página **Lucro & Margem** do admin.

## Limitações do MVP

- Sem pagamento online (PIX fase 2) — fluxo 100% WhatsApp
- Carrinho não persiste entre sessões/dispositivos
- Venda admin registra um produto por vez (multi-item fase 2)
- App Streamlit free pode demorar a “acordar” após inatividade
- Supabase free: 500 MB banco, 1 GB storage

## Changelog

Veja [CHANGELOG.md](CHANGELOG.md) para o histórico de versões.

## Licença

Uso livre para a loja.
