# MIGRATE-KB-CONTENT.ps1
# ----------------------
# Move o conteúdo da wiki antiga em `designer/knowledge-base/wiki/`
# para a nova KB em `Assinatura/knowledge-base/wiki/` aplicando namespaces.
#
# Uso (a partir da raiz do Projeto Assinatura):
#   .\Assinatura\knowledge-base\MIGRATE-KB-CONTENT.ps1
#
# Após a execução:
#   - A wiki antiga será renomeada para `designer/knowledge-base.legacy/`
#   - O conteúdo migrado vive em `Assinatura/knowledge-base/wiki/`
#   - Páginas classificadas por namespace (secretaria/, designer/, marcelle/)
#   - Páginas cross-cutting ficam planas
#
# Reversível: tudo via Move-Item, nada é deletado.

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$newKb = $scriptDir                                          # Assinatura/knowledge-base/
$newWiki = Join-Path $newKb "wiki"
$assinaturaRoot = Resolve-Path (Join-Path $scriptDir "..")   # Assinatura/
$oldKb = Join-Path $assinaturaRoot "designer\knowledge-base"
$oldWiki = Join-Path $oldKb "wiki"

if (-not (Test-Path $oldWiki)) {
    Write-Host "ERRO: KB antiga nao encontrada em $oldWiki" -ForegroundColor Red
    exit 1
}

Write-Host "KB antiga: $oldWiki"
Write-Host "KB nova:   $newWiki"
Write-Host ""

# Classificação por namespace
$namespaceMap = @{
    # secretaria/ (Gabi)
    "features/bot-gabi.md"                  = "features/secretaria/bot-gabi.md"
    "features/secretaria-ai-gabi.md"        = "features/secretaria/secretaria-ai-gabi.md"
    "features/secretaria-ai-mes2.md"        = "features/secretaria/secretaria-ai-mes2.md"
    "workflows/secretaria-ai-sistema.md"    = "workflows/secretaria/secretaria-ai-sistema.md"

    # designer/
    "features/agente-designer.md"                = "features/designer/agente-designer.md"
    "features/fabrica-v2.md"                     = "features/designer/fabrica-v2.md"
    "features/fabrica-redesign.md"               = "features/designer/fabrica-redesign.md"
    "features/fabrica-biblioteca-layouts.md"     = "features/designer/fabrica-biblioteca-layouts.md"
    "features/galeria-gestao.md"                 = "features/designer/galeria-gestao.md"
    "architecture/designer-frontend.md"          = "architecture/designer/designer-frontend.md"
    "architecture/designer-backend.md"           = "architecture/designer/designer-backend.md"
    "architecture/render-layout-as-data.md"      = "architecture/designer/render-layout-as-data.md"
    "architecture/agente-multimodelo.md"         = "architecture/designer/agente-multimodelo.md"
    "integrations/canva-connect-api.md"          = "integrations/canva-connect-api.md"
    "workflows/qualidade-lint-build.md"          = "workflows/designer/qualidade-lint-build.md"
    "workflows/designer-timeline-execucao.md"    = "workflows/designer/designer-timeline-execucao.md"
    "decisions/adr-001-next-express-separados.md"= "decisions/adr-001-next-express-separados.md"
    "decisions/adr-002-gemini-llm-designer.md"   = "decisions/adr-002-gemini-llm-designer.md"
    "decisions/adr-004-fabrica-arquitetura-v3.md"= "decisions/adr-004-fabrica-arquitetura-v3.md"
    "decisions/adr-005-canva-api-migracao.md"    = "decisions/adr-005-canva-api-migracao.md"
    "decisions/adr-006-editor-visual-alternativas-canva.md" = "decisions/adr-006-editor-visual-alternativas-canva.md"
    "outputs/pesquisa-geracao-imagens-pdf-designer.md"      = "outputs/designer/pesquisa-geracao-imagens-pdf-designer.md"
    "outputs/designer-auditoria-jornada.canvas"             = "outputs/designer/designer-auditoria-jornada.canvas"
    "outputs/designer-plano-implementacao.md"               = "outputs/designer/designer-plano-implementacao.md"
    "outputs/auditoria-libs-configs.md"                     = "outputs/designer/auditoria-libs-configs.md"
    "outputs/auditoria-ux-logica-designer.md"               = "outputs/designer/auditoria-ux-logica-designer.md"
    "outputs/benchmarking-fabrica-ux.md"                    = "outputs/designer/benchmarking-fabrica-ux.md"
    "outputs/auditoria-geral-designer-2026-05-13.md"        = "outputs/designer/auditoria-geral-designer-2026-05-13.md"

    # marcelle/
    "features/automacao-notificacao-marcelle.md" = "features/marcelle/automacao-notificacao-marcelle.md"

    # Cross-cutting (sem namespace — planos)
    "stakeholders/amanda-coelho.md"            = "stakeholders/amanda-coelho.md"
    "stakeholders/assinatura-marca-propria.md" = "stakeholders/assinatura-marca-propria.md"
    "stakeholders/gabi.md"                     = "stakeholders/gabi.md"
    "stakeholders/marcelle.md"                 = "stakeholders/marcelle.md"
    "decisions/adr-003-infra-compartilhada.md" = "decisions/adr-003-infra-compartilhada.md"
    "integrations/infraestrutura-tecnica.md"   = "integrations/infraestrutura-tecnica.md"
    "integrations/stripe-webhook.md"           = "integrations/stripe-webhook.md"
    "workflows/escopo-projeto-assinatura.md"   = "workflows/escopo-projeto-assinatura.md"
    "outputs/agentes-mapa-funcoes.canvas"      = "outputs/agentes-mapa-funcoes.canvas"
    "outputs/calendario-notion-execucao-2026-04-01-2026-05-13.md"  = "outputs/calendario-notion-execucao-2026-04-01-2026-05-13.md"
    "outputs/calendario-notion-execucao-2026-04-01-2026-05-13.csv" = "outputs/calendario-notion-execucao-2026-04-01-2026-05-13.csv"
    "outputs/relatorio-entregas-valor-agregado-2026-05-14.md"      = "outputs/relatorio-entregas-valor-agregado-2026-05-14.md"
    "outputs/timeline-calendario-obsidian-2026-04-01-2026-05-14.md"= "outputs/timeline-calendario-obsidian-2026-04-01-2026-05-14.md"
    "outputs/revisao-contratual-escopo-cronograma-aceite-2026-05-14.md" = "outputs/revisao-contratual-escopo-cronograma-aceite-2026-05-14.md"

    # Migrations (vão para wiki/migrations/, planas)
    "migrations/2026-04-22.md" = "migrations/2026-04-22.md"
    "migrations/2026-05-03.md" = "migrations/2026-05-03.md"
    "migrations/2026-05-05.md" = "migrations/2026-05-05.md"

    # Root-level wiki files
    "overview.md"        = "overview.md"
    "log.md"             = "log.md"
    "index.md"           = "index.md"        # vai precisar reescrita manual com novos paths
    "tracking.canvas"    = "tracking.canvas" # idem
}

$moved = 0
$skipped = 0
$missing = 0
$unmapped = @()

# 1. Criar todas as subpastas necessárias na nova wiki
$subdirs = @(
    "architecture\secretaria", "architecture\designer", "architecture\marcelle",
    "features\secretaria", "features\designer", "features\marcelle",
    "workflows\secretaria", "workflows\designer", "workflows\marcelle",
    "outputs\designer", "outputs\secretaria", "outputs\marcelle",
    "integrations", "security", "decisions", "stakeholders", "migrations"
)
foreach ($sd in $subdirs) {
    $full = Join-Path $newWiki $sd
    if (-not (Test-Path $full)) { New-Item -ItemType Directory -Force -Path $full | Out-Null }
}

# 2. Mover arquivos conforme map
foreach ($entry in $namespaceMap.GetEnumerator()) {
    $src = Join-Path $oldWiki $entry.Key
    $dst = Join-Path $newWiki $entry.Value

    if (-not (Test-Path $src)) {
        Write-Host "[MISS]  $($entry.Key) — não encontrado na KB antiga" -ForegroundColor DarkGray
        $missing++
        continue
    }
    if (Test-Path $dst) {
        Write-Host "[SKIP]  $($entry.Key) — já existe no destino" -ForegroundColor Yellow
        $skipped++
        continue
    }

    # Garantir que o diretório-pai existe
    $dstParent = Split-Path -Parent $dst
    if (-not (Test-Path $dstParent)) {
        New-Item -ItemType Directory -Force -Path $dstParent | Out-Null
    }

    Move-Item -Path $src -Destination $dst
    Write-Host "[MOVE]  $($entry.Key)  ->  $($entry.Value)" -ForegroundColor Green
    $moved++
}

# 3. Detectar arquivos não mapeados
Get-ChildItem $oldWiki -Recurse -File | ForEach-Object {
    $rel = $_.FullName.Substring($oldWiki.Length + 1).Replace("\", "/")
    if (-not $namespaceMap.ContainsKey($rel)) {
        $unmapped += $rel
    }
}

# 4. Mover .obsidian e git config para a nova KB (se ainda não existirem)
$obsidianSrc = Join-Path $oldKb ".obsidian"
$obsidianDst = Join-Path $newKb ".obsidian"
if ((Test-Path $obsidianSrc) -and (-not (Test-Path $obsidianDst))) {
    Move-Item -Path $obsidianSrc -Destination $obsidianDst
    Write-Host "[MOVE]  .obsidian/  ->  nova KB" -ForegroundColor Green
}

$gitSrc = Join-Path $oldKb "git"
$gitDst = Join-Path $newKb "git"
if ((Test-Path $gitSrc) -and (-not (Test-Path $gitDst))) {
    Move-Item -Path $gitSrc -Destination $gitDst
    Write-Host "[MOVE]  git/  ->  nova KB" -ForegroundColor Green
}

# 5. Renomear KB antiga
$oldKbLegacy = Join-Path $assinaturaRoot "designer\knowledge-base.legacy"
if ((Test-Path $oldKb) -and (-not (Test-Path $oldKbLegacy))) {
    Rename-Item -Path $oldKb -NewName "knowledge-base.legacy"
    Write-Host "[RENAME] designer/knowledge-base/  ->  designer/knowledge-base.legacy/" -ForegroundColor Cyan
}

# 6. Resumo
Write-Host ""
Write-Host "===== RESUMO ====="
Write-Host "Movidos:           $moved" -ForegroundColor Green
Write-Host "Ja existentes:     $skipped" -ForegroundColor Yellow
Write-Host "Nao encontrados:   $missing" -ForegroundColor DarkGray
Write-Host "Nao mapeados:      $($unmapped.Count)" -ForegroundColor Red
if ($unmapped.Count -gt 0) {
    Write-Host ""
    Write-Host "Arquivos NAO MAPEADOS (verifique manualmente):" -ForegroundColor Red
    $unmapped | ForEach-Object { Write-Host "  - $_" }
    Write-Host ""
    Write-Host "Eles continuam em $oldKb (agora renomeada para legacy)." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "PROXIMOS PASSOS:" -ForegroundColor Cyan
Write-Host "  1. Abrir Assinatura/knowledge-base/wiki/index.md e ATUALIZAR todos os links"
Write-Host "     com os novos caminhos (incluindo namespaces). Use Edit do Claude para isso."
Write-Host "  2. Abrir Assinatura/knowledge-base/wiki/tracking.canvas e atualizar os 'file:'"
Write-Host "     references para o novo path."
Write-Host "  3. Executar /memory-lint para checar links quebrados."
Write-Host "  4. Atualizar Assinatura/CLAUDE.md (linha 'KB canônica') para apontar para o novo path."
Write-Host "  5. Quando confirmar que tudo funciona, deletar designer/knowledge-base.legacy/"
