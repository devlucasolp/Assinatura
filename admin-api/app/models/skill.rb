# Catálogo canônico de skills built-in — fonte única para Rails e (via API) frontend.
# Skills com always_on: true não podem ser desligadas.
# Nome/descrição podem ser sobrescritos via bots.skill_customizations.
class Skill
  CATALOG = [
    { id: "chat",            name: "Conversa geral",       category: "core",  always_on: true,  description: "Resposta livre via Gemini para perguntas e pedidos sem intent específica." },
    { id: "asana_task",      name: "Criar tarefas",        category: "asana", always_on: false, description: "Cria tarefas e reuniões no Asana a partir de pedidos em linguagem natural." },
    { id: "asana_query",     name: "Consultar tarefas",    category: "asana", always_on: false, description: "Lista tarefas atrasadas, do dia, da semana ou pendentes." },
    { id: "asana_update",    name: "Atualizar tarefas",    category: "asana", always_on: false, description: "Altera nome, data ou notas de uma tarefa existente." },
    { id: "asana_complete",  name: "Concluir tarefas",     category: "asana", always_on: false, description: "Marca tarefas como concluídas." },
    { id: "asana_delete",    name: "Remover tarefas",      category: "asana", always_on: false, description: "Exclui tarefas do Asana." },
    { id: "asana_search",    name: "Buscar tarefa",        category: "asana", always_on: false, description: "Busca tarefa pelo nome e retorna o link permanente." },
    { id: "link_request",    name: "Link da última tarefa", category: "asana", always_on: false, description: "Devolve o link da última tarefa criada na conversa." },
    { id: "ata",             name: "Atas de reunião",      category: "core",  always_on: false, description: "Transforma transcrição em ata estruturada e cria tarefa no Asana." },
    { id: "media",           name: "Mídia (áudio/imagem)", category: "media", always_on: true,  description: "Transcreve áudios e extrai texto de imagens." },
  ].freeze

  def self.find(id)
    CATALOG.find { |s| s[:id] == id }
  end

  def self.toggleable_ids
    CATALOG.reject { |s| s[:always_on] }.map { |s| s[:id] }
  end

  # Catálogo com customizações aplicadas (nome e descrição vindos do banco se existirem)
  def self.catalog_with_overrides
    overrides = SkillCustomization.all.index_by(&:skill_id)
    CATALOG.map do |s|
      o = overrides[s[:id]]
      {
        id:           s[:id],
        name:         o&.custom_name.presence        || s[:name],
        description:  o&.custom_description.presence || s[:description],
        category:     s[:category],
        always_on:    s[:always_on],
        customized:   !o.nil?,
        default_name:         s[:name],
        default_description:  s[:description],
      }
    end
  end
end
