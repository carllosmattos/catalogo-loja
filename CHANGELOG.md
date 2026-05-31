# Changelog

Todas as mudanças relevantes deste projeto estão documentadas neste arquivo.

O formato segue [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/).

## [1.1.0] — 2026-05-31

Catálogo com categorias, grade em 2 colunas e paginação.

### Adicionado

- **Categorias** — tabela `categories`, migração `010`, aba no admin de produtos
- **Filtro por categoria** no catálogo público (pills horizontais com scroll)
- **Grade 2 colunas** com cards compactos (textos com clamp, sem quebra feia)
- **Paginação** de 20 produtos por página (Anterior / Próxima)
- Fallback por texto `products.category` quando a migração 010 ainda não rodou

### Alterado

- Admin de produtos usa select de categorias (em vez de texto livre, quando disponível)
- Largura máxima do catálogo ampliada para acomodar 2 colunas

---

## [1.0.0] — 2026-05-31

Primeira versão completa do MVP — catálogo LM moda feminina em produção.

### Adicionado

- **Catálogo público** mobile-first com identidade da loja (logo, cores, nome)
- **Produtos** com foto, preço, estoque, frete e descrição no card
- **Promoções** (% ou valor fixo) e **brindes** com foto, estoque e repasse
- **WhatsApp** — mensagem automática com peça, promo, brinde e valor final
- **Carrinho de compras** — adicionar, alterar quantidade, remover e checkout em lote
- **Comprar agora** — checkout direto de um item via WhatsApp
- **Minha conta** — login por telefone, nome, CPF e endereço (estilo anota.ai)
- **Painel admin** com login Supabase:
  - Produtos (CRUD, fotos, arquivar, duplicar)
  - Promoções (CRUD, arquivar)
  - Brindes (CRUD, foto, arquivar)
  - Configurações da loja
  - Lucro & margem (potencial + realizado no mês)
  - Vendas (registro manual, CPF, quantidade, cancelamento com estorno)
- **Clientes** — cadastro com CPF, busca e autofill no admin de vendas
- **Migrações Supabase** versionadas (`001`–`009`) em `supabase/migrations/`
- **Branches** `main` (produção) e `dev` (desenvolvimento)

### Banco de dados (migrações)

| Migração | Descrição |
|----------|-----------|
| 001 | Schema inicial — produtos, promoções, brindes, loja, RLS |
| 002 | Storage — bucket de fotos |
| 003 | Branding LM — nome e cores padrão |
| 004 | Foto do brinde (`image_url`) |
| 005 | Vendas, decremento de estoque, RPC `register_sale` |
| 006 | Lifecycle — arquivar brindes, cancelar vendas com estorno |
| 007 | Quantidade de peças por venda |
| 008 | Tabela `customers`, CPF obrigatório, vínculo em vendas |
| 009 | Endereço do cliente, RPCs de login por telefone |

### Removido

- Scripts legados `supabase/schema.sql` e `supabase/storage.sql` (substituídos pelas migrações numeradas)

---

## [0.1.0] — 2026-05-30

Versão inicial do repositório.

### Adicionado

- Catálogo básico Streamlit + Supabase + WhatsApp
- Admin: produtos, promoções, brindes, loja e lucro
- Schema SQL monolítico (`schema.sql`, `storage.sql`)

[1.1.0]: https://github.com/carllosmattos/catalogo-loja/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/carllosmattos/catalogo-loja/compare/06d5e0e...v1.0.0
[0.1.0]: https://github.com/carllosmattos/catalogo-loja/commit/06d5e0e
