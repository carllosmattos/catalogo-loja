# Catálogo de Roupas — Streamlit + Supabase + WhatsApp

Catálogo mobile-first para Instagram, 100% gratuito. Clientes veem as peças e compram via WhatsApp com mensagem pré-preenchida. A dona da loja gerencia tudo em um painel admin com login.

## Funcionalidades

- **Catálogo público** otimizado para iPhone (link na bio do Instagram)
- **Identidade da loja**: logo, cores personalizadas, nome
- **Produtos** com fotos, preços, estoque, frete
- **Promoções** (% ou valor fixo)
- **Brindes** com estoque, custo, frete e repasse ao cliente
- **Cálculo de lucro** considerando compra, frete e brindes
- **WhatsApp** com mensagem automática (peça, promoção, brinde, valor final)
- **Login admin** — só a dona da loja acessa o painel

## Stack (grátis)

| Serviço | Uso | Custo |
|---------|-----|-------|
| [Streamlit Community Cloud](https://share.streamlit.io) | Hospedagem do app | Grátis |
| [Supabase](https://supabase.com) | Banco, auth, imagens | Grátis (tier free) |
| WhatsApp (`wa.me`) | Pedidos | Grátis |

## Setup local

### 1. Clonar e instalar

```bash
git clone <seu-repo>
cd catalogo
pip install -r requirements.txt
```

### 2. Configurar Supabase

1. Crie um projeto em [supabase.com](https://supabase.com) (plano Free)
2. No **SQL Editor**, execute os arquivos nesta ordem:
   - [`supabase/schema.sql`](supabase/schema.sql)
   - [`supabase/storage.sql`](supabase/storage.sql)
3. Em **Authentication > Users**, crie o usuário admin (e-mail e senha da dona da loja)
4. Copie a **URL** e a **anon key** em Settings > API

### 3. Secrets locais

Copie `secrets.toml.example` para `.streamlit/secrets.toml`:

```toml
SUPABASE_URL = "https://xxxxx.supabase.co"
SUPABASE_ANON_KEY = "eyJ..."
```

### 4. Rodar localmente

```bash
streamlit run app.py
```

- Catálogo: `http://localhost:8501`
- Admin: `http://localhost:8501/Admin_Login`

## Deploy grátis (Streamlit Cloud)

1. Suba o código para um repositório **público** no GitHub
2. Acesse [share.streamlit.io](https://share.streamlit.io) e conecte o repo
3. Main file: `app.py`
4. Em **Settings > Secrets**, adicione:

```toml
SUPABASE_URL = "https://xxxxx.supabase.co"
SUPABASE_ANON_KEY = "eyJ..."
```

5. Deploy! O link gerado vai para a bio do Instagram

### Links úteis após deploy

| Página | URL |
|--------|-----|
| Catálogo (clientes) | `https://seu-app.streamlit.app/` |
| Admin (dona da loja) | `https://seu-app.streamlit.app/Admin_Login` |

## Estrutura do projeto

```
catalogo/
├── app.py                  # Catálogo público
├── pages/                  # Painel admin
│   ├── 1_Admin_Login.py
│   ├── 2_Admin_Produtos.py
│   ├── 3_Admin_Promocoes.py
│   ├── 4_Admin_Brindes.py
│   ├── 5_Admin_Loja.py
│   └── 6_Admin_Lucro.py
├── lib/                    # Lógica compartilhada
├── supabase/schema.sql     # Schema do banco
└── requirements.txt
```

## Fluxo de compra

1. Cliente abre o link do catálogo no Instagram
2. Escolhe uma peça e toca em **Comprar no WhatsApp**
3. WhatsApp abre com mensagem pronta: peça, tamanho, preço, promoção, brinde e valor final
4. Cliente envia a mensagem para a loja

## Cálculo de lucro

```
custo_peça = preço_compra + frete_compra
custo_brindes = Σ (preço_brinde + frete_brinde) × quantidade
preço_catálogo = preço_venda + repasse_brinde
preço_final = preço_catálogo - desconto + frete_cliente
lucro = preço_final - custo_peça - custo_brindes
```

Veja detalhes na página **Lucro & Margem** do painel admin.

## Limitações do tier grátis

- App pode demorar alguns segundos para "acordar" após inatividade
- Supabase free: 500 MB de banco, 1 GB de storage
- Sem pagamento online — fluxo 100% WhatsApp

## Licença

Uso livre para a loja.
