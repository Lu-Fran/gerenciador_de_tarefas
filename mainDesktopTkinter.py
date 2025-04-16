import tkinter as tk
from tkinter import messagebox, Toplevel, Label, Entry, Button, ttk
import json
import uuid
from datetime import datetime
import locale
from tkcalendar import Calendar

class AplicativoTarefas:
    def __init__(self, root):
        self.root = root
        self.root.title("Gerenciador de Tarefas / Projetos")
        self.root.resizable(True, True)
        
        self.tarefas = {} # Agora usamos um dicionário com ID como chave
        
        # Configurar idioma para datas
        try:
            locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
        except:
            locale.setlocale(locale.LC_TIME, '')
            
        # Frame central para o filtro (adicionado antes do uso)
        center_frame = ttk.Frame(root)
        center_frame.pack(padx=5)
                
        # Dropdown de filtro de status
        status_filtro_label = ttk.Label(center_frame, text="Filtrar tarefa por status:")
        status_filtro_label.grid(row=0, column=0, padx=(0,10), pady=5, sticky="w")
        
        self.status_filtro_var = tk.StringVar()        
        status_filtro_combobox = ttk.Combobox(center_frame, textvariable=self.status_filtro_var, state="readonly")
        status_filtro_combobox['values'] = ("Todos", "A iniciar", "Em andamento", "Concluída")
        status_filtro_combobox.current(0) # Seleciona "Todos" por padrão
        status_filtro_combobox.grid(row=0, column=1, padx=(0, 10), pady=5, sticky="w")
        
        # Quando o usuário escolher algo no dropdown, chamamos a função de filtro
        status_filtro_combobox.bind("<<ComboboxSelected>>", lambda event: self.filtrar_tarefa_por_status(self.status_filtro_var.get()))
        
        # Estrutura da árvore
        self.estrutura_arvore = ttk.Frame(center_frame)
        self.estrutura_arvore.grid(row=1, column=0, columnspan=4, pady=10)
        
        # Define colunas da árvore
        self.arvore_tarefas = ttk.Treeview(
            self.estrutura_arvore,
            columns=("Descrição", "Início", "Término", "Status"),
            show="tree headings"
        )
        
        self.arvore_tarefas.heading("Descrição", text="Descrição")
        self.arvore_tarefas.heading("Início", text="Início")
        self.arvore_tarefas.heading("Término", text="Término")
        self.arvore_tarefas.heading("Status", text="Status")
        self.arvore_tarefas.pack()
        
        # Ajuste de largura das colunas
        self.arvore_tarefas.column("#0", width=20, anchor=tk.CENTER)
        self.arvore_tarefas.column("Descrição", width=300)
        self.arvore_tarefas.column("Início", width=80, anchor=tk.CENTER)
        self.arvore_tarefas.column("Término", width=80, anchor=tk.CENTER)
        self.arvore_tarefas.column("Status", width=100, anchor=tk.CENTER)
        
        # Botões de ação
        btn_estrutura = ttk.Frame(root)
        btn_estrutura.pack(pady=7)
        
        ttk.Button(btn_estrutura, text="Criar Tarefa", command=self.abrir_formulário_tarefa).grid(row=0, column=0, padx=5)
        ttk.Button(btn_estrutura, text="Adicionar Subtarefa", command=self.abrir_formulario_subtarefa).grid(row=0, column=1, padx=5)
        ttk.Button(btn_estrutura, text="Editar Tarefa e Subtarefas", command=self.editar_tarefa).grid(row=0, column=2, padx=5)
        ttk.Button(btn_estrutura, text="Remover Tarefa ou Subtarefa", command=self.remover_tarefa).grid(row=0, column=3, padx=5)
        ttk.Button(btn_estrutura, text="Concluir Tarefa ou Subtarefa", command=self.concluir_tarefa).grid(row=0, column=4, padx=5)
        ttk.Button(btn_estrutura, text="Salvar Alterações", command=self.salvar_tarefas).grid(row=0, column=5, padx=5)

        self.carregar_tarefas()
    
    def filtrar_tarefa_por_status(self, status_selecionado):
        # Limpar a árvore atual
        for item in self.arvore_tarefas.get_children():
            self.arvore_tarefas.delete(item)
               
        for tarefa_id, tarefa in self.tarefas.items():
            if status_selecionado == "Todos" or tarefa["status"] == status_selecionado:
                self.arvore_tarefas.insert("", "end", iid=tarefa_id, text="",
                                           values=(tarefa["descricao"], tarefa["data_inicio"], tarefa["data_termino"], tarefa["status"]))
                
            for subtarefa in tarefa.get("subtarefas", []):
                if status_selecionado == "Todos" or subtarefa["status"] == status_selecionado:
                    self.arvore_tarefas.insert(tarefa_id, "end", iid=f"{tarefa_id}_sub_{subtarefa['id']}", text="",
                                               values=(f" ↳ {subtarefa['descricao']}", subtarefa["data_inicio"], subtarefa["data_termino"], subtarefa["status"]))
    
    def carregar_tarefas(self):
        # Carrega as tarefas do arquivo JSON e as exibe na interface.
        try:
            with open("lista_tarefas.json", "r", encoding='utf-8') as arquivo:
                lista_tarefas = json.load(arquivo)
                
                if not isinstance(lista_tarefas, list):
                    raise ValueError("Formato inválido: esperada uma lista.")
                
                self.tarefas = {} # Resetar o dicionário interno
                
                # Limpa a árvore Treeview antes de carregar novos dados
                self.arvore_tarefas.delete(*self.arvore_tarefas.get_children())
                
                for tarefa in lista_tarefas:
                    tarefa_id = tarefa.get("id", str(uuid.uuid4()))
                    self.tarefas[tarefa_id] = tarefa
                    
                    # Adiciona a tarefa principal na árvore
                    self.arvore_tarefas.insert("", "end", iid=tarefa_id,
                                               values=(tarefa["descricao"],
                                                       tarefa["data_inicio"],
                                                       tarefa["data_termino"],
                                                       tarefa["status"]))

                    # Adiciona subtarefas, se houver
                    for sub in tarefa.get("subtarefas", []):
                        subtarefa_id = sub.get("id", str(uuid.uuid4()))
                        subtarefa_arvore_id = f"{tarefa_id}_sub_{subtarefa_id}"
                        self.arvore_tarefas.insert(tarefa_id, "end", iid=subtarefa_arvore_id,
                                                   values=(f" ↳ {sub["descricao"]}",
                                                           sub["data_inicio"],
                                                           sub["data_termino"],
                                                           sub["status"]))
        except (FileNotFoundError, json.JSONDecodeError, ValueError) as e:
            print(f"Erro ao carregar tarefas: {e}")
            self.tarefas = {}
            
    def salvar_tarefas(self):
        lista_tarefas = []
        
        for tarefa_id, tarefa in self.tarefas.items():
            nova_tarefa = {
                "id": tarefa_id,
                "descricao": tarefa["descricao"],
                "data_inicio": tarefa["data_inicio"],
                "data_termino": tarefa["data_termino"],
                "status": tarefa["status"],
                "subtarefas": []
            }
            
            for sub in tarefa.get("subtarefas", []):
                subtarefa = {
                    "id": sub["id"],
                    "descricao": sub["descricao"],
                    "data_inicio": sub["data_inicio"],
                    "data_termino": sub["data_termino"],
                    "status": sub["status"]
                }
                nova_tarefa["subtarefas"].append(subtarefa)
                
            lista_tarefas.append(nova_tarefa)
        
        with open("lista_tarefas.json", 'w', encoding='utf-8') as arquivo:
            json.dump(lista_tarefas, arquivo, indent=4, ensure_ascii=False)
            
    def criar_tarefa(self, descricao, data_inicio, data_termino, status):
                        
        if descricao:
            tarefa_id = str(uuid.uuid4())
            nova_tarefa = {
                "id": tarefa_id,
                "descricao": descricao,
                "data_inicio": data_inicio,
                "data_termino": data_termino,
                "status": status,
                "subtarefas": []
            }
                
            self.tarefas[tarefa_id] = nova_tarefa
                
            self.arvore_tarefas.insert("", tk.END, iid=tarefa_id,
                                        values=(descricao, data_inicio, data_termino, status))
        
    def abrir_formulário_tarefa(self):
        janela_tarefa = tk.Toplevel(self.root)
        janela_tarefa.title("Criar Tarefa")
        janela_tarefa.resizable(True, True)
        janela_tarefa = ttk.Frame(janela_tarefa, padding=10)
        janela_tarefa.pack(fill='both', expand=True)
        
        ttk.Label(janela_tarefa, text="Descrição").pack(padx=5)
        entrada_descricao = ttk.Entry(janela_tarefa, width=40)
        entrada_descricao.pack()
        
        ttk.Label(janela_tarefa, text="Data Início:").pack(padx=5)
        calendario_inicio = Calendar(janela_tarefa, selectmode="day", locale='pt_BR', date_pattern='dd/mm/yyyy')
        calendario_inicio.pack()
        
        ttk.Label(janela_tarefa, text="Data Término:").pack(padx=5)
        calendario_termino = Calendar(janela_tarefa, selectmode="day", locale='pt_BR', date_pattern='dd/mm/yyyy')
        calendario_termino.pack()
        
        ttk.Label(janela_tarefa, text="Status:").pack(pady=5)
        entrada_status = ttk.Combobox(janela_tarefa, values=["A iniciar", "Em andamento", "Concluída"])
        entrada_status.set("A iniciar")
        entrada_status.pack()
        
        def salvar_tarefa():
            descricao = entrada_descricao.get()
            data_inicio = calendario_inicio.get_date()
            data_termino = calendario_termino.get_date()
            status = entrada_status.get()
            
            self.criar_tarefa(descricao, data_inicio, data_termino, status)
            
            janela_tarefa.destroy()
        
        ttk.Button(janela_tarefa, text="Salvar nova Tarefa", command=salvar_tarefa).pack(pady=10)
        
    def adicionar_subtarefa(self, descricao, data_inicio, data_termino, status):
        item_selecionado = self.arvore_tarefas.selection()
        if not item_selecionado:
            messagebox.showwarning("Aviso", "Selecione uma tarefa para adicionar a subtarefa.")
            return
        
        parent_id = item_selecionado[0]
        if self.arvore_tarefas.parent(parent_id):
            messagebox.showwarning("Aviso", "Selecione uma tarefa principal, não uma subtarefa.")
            return
        
        if not descricao:
                messagebox.showwarning("Aviso", "A descrição é obrigatória.")
                return
            
        subtarefa_id = str(uuid.uuid4())
        nova_subtarefa = {
            "id": subtarefa_id,
            "descricao": descricao,
            "data_inicio": data_inicio,
            "data_termino": data_termino,
            "status": status
        }
            
        self.tarefas[parent_id]["subtarefas"].append(nova_subtarefa)
            
        vista_arvore_id = f"{parent_id}_sub_{subtarefa_id}"
        self.arvore_tarefas.insert(
            parent_id,
            "end",
            iid=vista_arvore_id,
            values=(f" ↳ {descricao}", data_inicio, data_termino, status)
        )
        
        self.salvar_tarefas()
        
    def abrir_formulario_subtarefa(self):
        
        janela_subtarefa = tk.Toplevel(self.root)
        janela_subtarefa.title("Adicionar Subtarefa")
        janela_subtarefa.resizable(True, True)
        janela_subtarefa = ttk.Frame(janela_subtarefa, padding=10)
        janela_subtarefa.pack(fill='both', expand=True)
        
        ttk.Label(janela_subtarefa, text="Descrição:").pack(pady=5)
        entrada_descricao = ttk.Entry(janela_subtarefa, width=40)
        entrada_descricao.pack()
        
        ttk.Label(janela_subtarefa, text="Data Início:").pack(padx=5)
        calendario_inicio = Calendar(janela_subtarefa, selectmode="day", locale='pt_BR', date_pattern='dd/mm/yyyy')
        calendario_inicio.pack()
    
        ttk.Label(janela_subtarefa, text="Data Término:").pack(padx=5)
        calendario_termino = Calendar(janela_subtarefa, selectmode="day", locale='pt_BR', date_pattern='dd/mm/yyyy')
        calendario_termino.pack()
        
        ttk.Label(janela_subtarefa, text="Status:").pack(pady=5)
        entrada_status = ttk.Combobox(janela_subtarefa, values=["A iniciar", "Em andamento", "Concluída"])
        entrada_status.set("A iniciar")
        entrada_status.pack()
        
        def salvar_subtarefa():
            descricao = entrada_descricao.get()
            data_inicio = calendario_inicio.get_date()
            data_termino = calendario_termino.get_date()
            status = entrada_status.get()
            
            self.adicionar_subtarefa(descricao, data_inicio, data_termino, status)

            janela_subtarefa.destroy()
        
        ttk.Button(janela_subtarefa, text="Salvar Subtarefa", command=salvar_subtarefa).pack(pady=10)
    
    def editar_tarefa(self):
        item_selecionado = self.arvore_tarefas.selection()
        if not item_selecionado:
            messagebox.showwarning("Aviso", "Selecione uma tarefa para editar.")
            return
        
        tarefa_id = item_selecionado[0]
        
        # Verifica se é tarefa principal
        tarefa = self.tarefas.get(tarefa_id)
        
        # Se não for, verifica se é uma subtarefa
        if not tarefa:
            for parent_id, tarefa in self.tarefas.items():
                for subtarefa in tarefa.get("subtarefas", []):
                    subtarefa_id = f"{parent_id}_sub_{subtarefa['id']}"
                    if subtarefa_id == tarefa_id:
                       self.editar_subtarefa(tarefa, subtarefa, tarefa_id)
                       return
            messagebox.showinfo("Erro", "Tarefa não encontrada.")
            return
        
        janela_editar_tarefa = Toplevel(self.root)
        janela_editar_tarefa.title("Editar Tarefa")
        janela_editar_tarefa.resizable(True, True)
        janela_editar_tarefa = ttk.Frame(janela_editar_tarefa, padding=10)
        janela_editar_tarefa.pack(fill='both', expand=True)
        
        # Campo: Descrição
        Label(janela_editar_tarefa, text="Descrição:").pack()
        entrada_descricao = Entry(janela_editar_tarefa, width=40)
        entrada_descricao.insert(0, tarefa["descricao"])
        entrada_descricao.pack()
        
        # Campo: Data Início com Calendário
        ttk.Label(janela_editar_tarefa, text="Data Início:").pack(pady=5)
        calendario_inicio = Calendar(janela_editar_tarefa, selectmode="day", locale='pt_BR', date_pattern='dd/mm/yyyy')
        calendario_inicio.pack()
        calendario_inicio.selection_set(tarefa["data_inicio"]) # Busca a data selecionada
        
        # Campo: Data Término com Calendário
        ttk.Label(janela_editar_tarefa, text="Data Término:").pack(padx=5)
        calendario_termino = Calendar(janela_editar_tarefa, selectmode="day", locale='pt_BR', date_pattern='dd/mm/yyyy')
        calendario_termino.pack()
        calendario_termino.selection_set(tarefa["data_termino"]) # Busca a data selecionada
        
        # Campo: Status
        ttk.Label(janela_editar_tarefa, text="Status:").pack(pady=5)
        entrada_status = ttk.Combobox(janela_editar_tarefa, values=["A iniciar", "Em andamento", "Concluída"])
        entrada_status.set(tarefa["status"])
        entrada_status.pack()
        
        def salvar_edicao_tarefa():
            tarefa["descricao"] = entrada_descricao.get()
            tarefa["data_inicio"] = calendario_inicio.get_date()
            tarefa["data_termino"] = calendario_termino.get_date()
            tarefa["status"] = entrada_status.get()
            
            # Atualiza a exibição na árvore 
            self.arvore_tarefas.item(tarefa_id, values=(tarefa["descricao"],
                                                        tarefa["data_inicio"],
                                                        tarefa["data_termino"],
                                                        tarefa["status"]))
            
            self.salvar_tarefas() # Salva os dados atualizados
            
            janela_editar_tarefa.destroy()
                
        ttk.Button(janela_editar_tarefa, text="Salvar edição tarefa", command=salvar_edicao_tarefa).pack(pady=10)
    
    def editar_subtarefa(self, tarefa, subtarefa, tarefa_id):
        
        janela_editar_subtarefa = tk.Toplevel(self.root)
        janela_editar_subtarefa.title("Editar Subtarefa")
        janela_editar_subtarefa.resizable(True, True)
        janela_editar_subtarefa = ttk.Frame(janela_editar_subtarefa, padding=10)
        janela_editar_subtarefa.pack(fill='both', expand=True)
        
        # Campo: Descrição
        Label(janela_editar_subtarefa, text="Descrição:").pack()
        entrada_descricao = Entry(janela_editar_subtarefa, width=40)
        entrada_descricao.insert(0, subtarefa["descricao"])
        entrada_descricao.pack()
        
        # Campo: Data Início com Calendário
        ttk.Label(janela_editar_subtarefa, text="Data Início:").pack(pady=5)
        calendario_inicio = Calendar(janela_editar_subtarefa, selectmode="day", locale='pt_BR', date_pattern='dd/mm/yyyy')
        calendario_inicio.pack()
        calendario_inicio.selection_set(subtarefa["data_inicio"])
        
        # Campo: Data Término com Calendário
        ttk.Label(janela_editar_subtarefa, text="Data Término:").pack(padx=5)
        calendario_termino = Calendar(janela_editar_subtarefa, selectmode="day", locale='pt_BR', date_pattern='dd/mm/yyyy')
        calendario_termino.pack()
        calendario_termino.selection_set(subtarefa["data_termino"])
        
        # Campo: Status
        ttk.Label(janela_editar_subtarefa, text="Status:").pack(pady=5)
        entrada_status = ttk.Combobox(janela_editar_subtarefa, values=["A iniciar", "Em andamento", "Concluída"])
        entrada_status.set(subtarefa["status"])
        entrada_status.pack()
        
        def salvar_edicao_subtarefa():
            subtarefa["descricao"] = entrada_descricao.get()
            subtarefa["data_inicio"] = calendario_inicio.get_date()
            subtarefa["data_termino"] = calendario_termino.get_date()
            subtarefa["status"] = entrada_status.get()
            
            # Atualiza exibição na árvore
            self.arvore_tarefas.item(tarefa_id, values=(
                f" ↳ {subtarefa['descricao']}",
                subtarefa['data_inicio'],
                subtarefa['data_termino'],
                subtarefa['status']
            ))
            
            self.salvar_tarefas()
            janela_editar_subtarefa.destroy()
        
        ttk.Button(janela_editar_subtarefa, text="Salvar edição Subtarefa", command=salvar_edicao_subtarefa).pack(pady=10)
    
    def remover_subtarefa(self, subtarefa_id):
        for parent_id, tarefa in self.tarefas.items():
            subtarefas = tarefa.get("subtarefas", [])
            for subtarefa in subtarefas:
                arvore_subtarefa_id = f"{parent_id}_sub_{subtarefa['id']}"
                if subtarefa_id == arvore_subtarefa_id:
                    subtarefas.remove(subtarefa)
                    self.arvore_tarefas.delete(subtarefa_id)
                    self.salvar_tarefas()
                    return True # Para indicar que removeu
        return False # Se não encontrou
    
    def remover_tarefa(self):
        item_selecionado = self.arvore_tarefas.selection()
        if not item_selecionado:
            messagebox.showwarning("Aviso", "Selecione uma tarefa para remover.")
            return
        
        tarefa_id = item_selecionado[0]
        
        if tarefa_id in self.tarefas:
            del self.tarefas[tarefa_id]
            # Remove do Treeview (tarefa ou subtarefa)
            self.arvore_tarefas.delete(tarefa_id)
        else:
            if not self.remover_subtarefa(tarefa_id):
                messagebox.showerror("Erro", "Subtarefa não encontrada.")
        
        self.salvar_tarefas()
        
    def concluir_tarefa(self):
        item_selecionado = self.arvore_tarefas.selection()
        if not item_selecionado:
            messagebox.showwarning("Aviso", "Selecione uma tarefa para concluir.")
            return
        
        tarefa_id = item_selecionado[0]
        
        # Tarefa Principal
        if tarefa_id in self.tarefas:
            self.tarefas[tarefa_id]["status"] = "Concluída"
            tarefa = self.tarefas[tarefa_id]
            self.arvore_tarefas.item(tarefa_id, values=(tarefa["descricao"],
                                                        tarefa["data_inicio"],
                                                        tarefa["data_termino"],
                                                        "Concluída"))

        # Subtarefa
        else:
            for parent_id, tarefa in self.tarefas.items():
                for subtarefa in tarefa.get("subtarefas", []):
                    arvore_subtarefa_id = f"{parent_id}_sub_{subtarefa['id']}"
                    if tarefa_id == arvore_subtarefa_id:
                        subtarefa["status"] = "Concluída"
                        self.arvore_tarefas.item(tarefa_id, values=(f" ↳ {subtarefa['descricao']}",
                                                                    subtarefa["data_inicio"],
                                                                    subtarefa["data_termino"],
                                                                    "Concluída"))
                        self.salvar_tarefas()
                        return
    
# Execução principal
if __name__ == "__main__":
    root = tk.Tk()
    app = AplicativoTarefas(root)
    root.mainloop()


