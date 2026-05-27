---
title: Integração Urgente — Pipeline Híbrido
type: feature
namespace: designer
tags:
  - designer
  - design-document
  - hybrid-design
  - frontend
  - backend
sources:
  - designer/backend/src/routes/ai.ts
  - designer/frontend/src/lib/designDocument.ts
  - designer/frontend/src/app/[marca]/fabrica/page.tsx
  - designer/frontend/src/app/[marca]/editor/[postId]/page.tsx
created: 2026-05-15
updated: 2026-05-15
status: active
---

# Integração Urgente — Pipeline Híbrido

## Resumo

Registro da integração urgente do pipeline híbrido entre backend e frontend no Designer. A Fábrica agora salva o post como `hybrid-design` contendo o `document` semântico gerado pelo Gemini. O frontend realiza a compilação desse documento e mantém um fallback seguro para o formato legado (`DesignPage[]`).

## Detalhes

Esta integração completa a união das pontas trabalhadas anteriormente na arquitetura de `DesignDocument` híbrido:
- **Backend (`routes/ai.ts`)**: Atualizado para retornar e salvar o conteúdo no formato `{ kind: 'hybrid-design', version: 1, source: 'codegen', document: <payload> }`.
- **Frontend Core (`lib/designDocument.ts` / `lib/designContent.ts`)**: Tipagens e helpers estabilizados para reconhecer o novo formato híbrido.
- **Fábrica (`page.tsx`)**: O componente de criação (Fábrica) agora processa corretamente a resposta do backend e despacha o salvamento no novo formato.
- **Editor (`page.tsx`)**: O CanvasEditor agora consome o formato `hybrid-design`, utilizando o compiler frontend (Fase 2) para transformar o documento em layers editáveis. Se o formato for antigo, aplica fallback automático para legado.

## Decisões Tomadas

- O backend foi alterado para já salvar a fonte primária como `hybrid-design`. O frontend assume a responsabilidade da compilação inicial (`document -> pages`) para não sobrecarregar o backend e destravar a compatibilidade imediata.
- Mantivemos fallback estrito para o formato legado para não quebrar posts antigos da Galeria.

## Learnings

- A adoção do formato `hybrid-design` de forma unificada exigiu alinhamento entre os payloads de criação (Fábrica) e leitura (Editor/Galeria), confirmando a importância dos helpers centralizados de extração e conversão visual (`extractEditablePages`).

## Relacionados

- [[design-document-hibrido]]
- [[design-document-compiler]]
- [[design-document-renderer]]
- [[fabrica-v2]]