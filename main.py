import tkinter as tk
from tkinter import messagebox, Toplevel, Label, Entry, Button, ttk
import json
import uuid
from datetime import datetime
import locale
from tkcalendar import Calendar

class TaskApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gerenciador de Tarefas / Projetos")
        self.root.geometry("675x325")

        self.tasks = {}  # Agora usamos um dicionário com ID como chave
        
        # Configurar idioma para datas
        try:
            locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
        except:
            locale.setlocale(locale.LC_TIME, '')
        
        self.tree_frame = ttk.Frame(root)
        self.tree_frame.pack(pady=20)

        # Define as colunas da árvore
        self.task_tree = ttk.Treeview(
            self.tree_frame,
            columns=("Descrição", "Início", "Término", "Status"),
            show="tree headings"
        )
        
        self.task_tree.heading("Descrição", text="Descrição")
        self.task_tree.heading("Início", text="Início")
        self.task_tree.heading("Término", text="Término")
        self.task_tree.heading("Status", text="Status")
        self.task_tree.pack()
        
        # Ajuste de largura das colunas
        self.task_tree.column("#0", width=20, anchor=tk.CENTER)
        self.task_tree.column("Descrição", width=250)
        self.task_tree.column("Início", width=100, anchor=tk.CENTER)
        self.task_tree.column("Término", width=100, anchor=tk.CENTER)
        self.task_tree.column("Status", width=100, anchor=tk.CENTER)

        # Botões de ação
        btn_frame = ttk.Frame(root)
        btn_frame.pack(pady=7)

        ttk.Button(btn_frame, text="Nova Tarefa", command=self.create_task).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="Subtarefa", command=self.add_subtask).grid(row=0, column=1, padx=5)
        ttk.Button(btn_frame, text="Editar Tarefa e Subtarefas", command=self.edit_task).grid(row=0, column=2, padx=5)
        ttk.Button(btn_frame, text="Remover Tarefa", command=self.remove_task).grid(row=0, column=3, padx=5)
        ttk.Button(btn_frame, text="Concluir Tarefa", command=self.complete_task).grid(row=0, column=4, padx=5)
        ttk.Button(btn_frame, text="Salvar Tarefa", command=self.save_tasks).grid(row=0, column=5, padx=5)
        
        self.load_task()

    def load_task(self):
        # Carrega as tarefas do arquivo JSON e as exibe na interface.
        try:
            with open("task_list.json", "r", encoding='utf-8') as arquivo:
                tasks_list = json.load(arquivo)

                if not isinstance(tasks_list, list):
                    raise ValueError("Formato inválido: esperada uma lista.")

                self.tasks = {} # Resetar o dicionário interno
                
                # Limpa a árvore Treeview antes de carregar novos dados
                self.task_tree.delete(*self.task_tree.get_children())

                for task in tasks_list:
                    task_id = task.get("id", str(uuid.uuid4()))
                    self.tasks[task_id] = task
                    
                    # Adiciona a tarefa principal na árvore
                    self.task_tree.insert("", "end", iid=task_id,
                                                   values=(task["descricao"],
                                                           task["data_inicio"],
                                                           task["data_termino"],
                                                           task["status"]))

                    # Adiciona subtarefas, se houver
                    for sub in task.get("subtarefas", []):
                        sub_id = sub.get("id", str(uuid.uuid4()))
                        subtree_id = f"{task_id}_sub_{sub_id}"
                        self.task_tree.insert(task_id, "end", iid=subtree_id,
                                              values=(f" ↳ {sub['descricao']}",
                                                      sub["data_inicio"],
                                                      sub["data_termino"],
                                                      sub["status"]))

        except (FileNotFoundError, json.JSONDecodeError, ValueError) as e:
            print(f"Erro ao carregar tarefas: {e}")
            self.tasks = {}

    def save_tasks(self):
        task_list = []

        for task_id, task in self.tasks.items():
            tarefa = {
                "id": task_id,
                "descricao": task["descricao"],
                "data_inicio": task["data_inicio"],
                "data_termino": task["data_termino"],
                "status": task["status"],
                "subtarefas": []
            }

            for sub in task.get("subtarefas", []):
                subtarefa = {
                    "id": sub["id"],
                    "descricao": sub["descricao"],
                    "data_inicio": sub["data_inicio"],
                    "data_termino": sub["data_termino"],
                    "status": sub["status"]
                }
                tarefa["subtarefas"].append(subtarefa)

            task_list.append(tarefa)

        with open("task_list.json", "w", encoding="utf-8") as arquivo:
            json.dump(task_list, arquivo, indent=4, ensure_ascii=False)

    def create_task(self):
        def save():
            descricao = entry_desc.get()
            data_inicio = cal_inicio.get_date()
            data_termino = cal_termino.get_date()

            if descricao:
                task_id = str(uuid.uuid4())
                nova_tarefa = {
                    "id": task_id,
                    "descricao": descricao,
                    "data_inicio": data_inicio,
                    "data_termino": data_termino,
                    "status": "Pendente",
                    "subtarefas": []
                }

                self.tasks[task_id] = nova_tarefa

                self.task_tree.insert("", tk.END, iid=task_id,
                                      values=(descricao, data_inicio, data_termino, "Pendente"))

            top.destroy()

        top = tk.Toplevel(self.root)
        top.title("Nova Tarefa")
        top.geometry("300x500")

        ttk.Label(top, text="Descrição:").pack(padx=5)
        entry_desc = ttk.Entry(top, width=30)
        entry_desc.pack()

        ttk.Label(top, text="Data de Início:").pack(padx=5)
        cal_inicio = Calendar(top, selectmode="day", locale='pt_BR', date_pattern='dd/mm/yyyy')
        cal_inicio.pack()

        ttk.Label(top, text="Data de Término:").pack()
        cal_termino = Calendar(top, selectmode="day", locale='pt_BR', date_pattern='dd/mm/yyyy')
        cal_termino.pack()

        ttk.Button(top, text="Salvar", command=save).pack(pady=10)
        
    def add_subtask(self):
        selected_item = self.task_tree.selection()
        if not selected_item:
            messagebox.showwarning("Aviso", "Selecione uma tarefa para adicionar a subtarefa")
            return

        parent_id = selected_item[0]
        if self.task_tree.parent(parent_id):
            messagebox.showwarning("Aviso", "Selecione uma tarefa principal, não uma subtarefa.")
            return

        # Janela para o formulário de subtarefa
        subtask_window = tk.Toplevel(self.root)
        subtask_window.title("Nova Subtarefa")
        subtask_window.geometry("300x600")

        # Campo: Descrição
        ttk.Label(subtask_window, text="Descrição:").pack(pady=5)
        descricao_entry = ttk.Entry(subtask_window, width=30)
        descricao_entry.pack()

        # Campo: Data Início com Calendário
        ttk.Label(subtask_window, text="Data de Início:").pack(pady=5)
        cal_inicio = Calendar(subtask_window, selectmode="day", locale='pt_BR', date_pattern='dd/mm/yyyy')
        cal_inicio.pack()

        # Campo: Data Término com Calendário
        ttk.Label(subtask_window, text="Data de Término:").pack(pady=5)
        cal_termino = Calendar(subtask_window, selectmode="day", locale='pt_BR', date_pattern='dd/mm/yyyy')
        cal_termino.pack()

        # Campo: Status
        ttk.Label(subtask_window, text="Status:").pack(pady=5)
        status_entry = ttk.Combobox(subtask_window, values=["Pendente", "Em andamento", "Concluída"])
        status_entry.set("Pendente")
        status_entry.pack()
                     
        def salvar_subtarefa():
            descricao = descricao_entry.get()
            data_inicio = cal_inicio.get_date()
            data_termino = cal_termino.get_date()
            status = status_entry.get()
            
            if not descricao:
                messagebox.showwarning("Aviso", "A descrição é obrigatória.")
                return

            sub_id = str(uuid.uuid4())
            new_subtask = {
                "id": sub_id,
                "descricao": descricao,
                "data_inicio": data_inicio,
                "data_termino": data_termino,
                "status": status
                }

            self.tasks[parent_id]["subtarefas"].append(new_subtask)

            treeview_id = f"{parent_id}_sub_{sub_id}"
            self.task_tree.insert(
                parent_id,
                "end",
                iid=treeview_id,
                values=(f" ↳ {descricao}", data_inicio, data_termino, status)
                )
            
            self.save_tasks()
            subtask_window.destroy()
        ttk.Button(subtask_window, text="Salvar Subtarefa", command=salvar_subtarefa).pack(pady=10)
        
    def edit_task(self):
        selected_item = self.task_tree.selection()
        if not selected_item:
            messagebox.showwarning("Aviso", "Selecione uma tarefa para editar.")
            return

        task_id = selected_item[0]
        
        # Verifica se é tarefa principal
        task = self.tasks.get(task_id)
        
        # Se não for, verifica se é uma subtarefa
        if not task:
            for parent_id, task in self.tasks.items():
                for sub in task.get("subtarefas", []):
                    sub_id = f"{parent_id}_sub_{sub['id']}"
                    if sub_id == task_id:
                        self.edit_subtask(task, sub, task_id)
                        return
            messagebox.showinfo("Erro", "Tarefa não encontrada.")
            return
        
        top = Toplevel(self.root)
        top.title("Editar Tarefa")
        top.geometry("300x575")
        
        Label(top, text="Descrição:").pack()
        entry_desc = Entry(top)
        entry_desc.insert(0, task["descricao"])
        entry_desc.pack()
        
        # Campo: Data Início com Calendário
        ttk.Label(top, text="Data de Início:").pack(pady=5)
        cal_inicio = Calendar(top, selectmode="day", locale='pt_BR', date_pattern='dd/mm/yyyy')
        cal_inicio.pack()

        # Campo: Data Término com Calendário
        ttk.Label(top, text="Data de Término:").pack(pady=5)
        cal_termino = Calendar(top, selectmode="day", locale='pt_BR', date_pattern='dd/mm/yyyy')
        cal_termino.pack()

        Label(top, text="Status:").pack()
        status_combobox = ttk.Combobox(top, values=["Pendente", "Em andamento", "Concluída"])
        status_combobox.set(task["status"])
        status_combobox.pack()

        def salvar_edicao():
            task["descricao"] = entry_desc.get()
            task["data_inicio"] = cal_inicio.get_date()
            task["data_termino"] = cal_termino.get_date()
            task["status"] = status_combobox.get()
            
            # Atualiza a exibição na árvore 
            self.task_tree.item(task_id, values=(task["descricao"],
                                                 task["data_inicio"],
                                                 task["data_termino"], 
                                                 task["status"]))
            
            self.save_tasks() # Salva os dados atualizados

            top.destroy()

        ttk.Button(top, text="Salvar", command=salvar_edicao).pack(pady=10)
    
    def edit_subtask(self, parent_task, subtask, treeview_id):
        
        edit_subtask_window = tk.Toplevel(self.root)
        edit_subtask_window.title("Editar Subtarefa")
        edit_subtask_window.geometry("300x600")
        
        # Campo descricao
        ttk.Label(edit_subtask_window, text="Descrição:").pack(pady=5)
        descricao_entry = ttk.Entry(edit_subtask_window, width=30)
        descricao_entry.insert(0, subtask["descricao"])
        descricao_entry.pack()
        
        # Campo: Data Início com calendário
        ttk.Label(edit_subtask_window, text="Data de Início:").pack(pady=5)
        cal_inicio = Calendar(edit_subtask_window, selectmode="day", locale='pt_BR', date_pattern='dd/mm/yyyy')
        cal_inicio.pack()
                
        # Campo Data Término com calendário
        ttk.Label(edit_subtask_window, text="Data de Término:").pack(pady=5)
        cal_termino = Calendar(edit_subtask_window, selectmode="day", locale='pt_BR', date_pattern='dd/mm/yyyy')
        cal_termino.pack()
        
        # Campo Status
        ttk.Label(edit_subtask_window, text="Status:").pack(pady=5)
        status_combobox = ttk.Combobox(edit_subtask_window, values=["Pendente", "Em andamento", "Concluída"])
        status_combobox.set(subtask["status"])
        status_combobox.pack()
        
        def salvar_edicao_subtarefa():
            subtask["descricao"] = descricao_entry.get()
            subtask["data_inicio"] = cal_inicio.get_date()
            subtask["data_termino"] = cal_termino.get_date()
            subtask["status"] = status_combobox.get()
            
            # Atualiza exibição na árvore
            self.task_tree.item(treeview_id, values=(
                f" ↳ {subtask['descricao']}",
                subtask["data_inicio"],
                subtask['data_termino'],
                subtask['status']
            ))
            
            self.save_tasks()
            edit_subtask_window()
            
        ttk.Button(edit_subtask_window, text="Salvar", command=salvar_edicao_subtarefa).pack(pady=10)

    def remove_task(self):
        selected = self.task_tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione uma tarefa para remover.")
            return

        task_id = selected[0]

        if task_id in self.tasks:
            del self.tasks[task_id]

        # Remove do Treeview (tarefa ou subtarefa)
        self.task_tree.delete(task_id)

    def complete_task(self):
        selected = self.task_tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione uma tarefa para concluir.")
            return

        task_id = selected[0]

        # Tarefa principal
        if task_id in self.tasks:
            self.tasks[task_id]["status"] = "Concluído"
            task = self.tasks[task_id]
            self.task_tree.item(task_id, values=(task["descricao"],
                                                 task["data_inicio"],
                                                 task["data_termino"],
                                                 "Concluído"))

        # Subtarefa
        else:
            for parent_id, task in self.tasks.items():
                for sub in task.get("subtarefas", []):
                    sub_tree_id = f"{parent_id}_sub_{sub["id"]}"
                    if task_id == sub_tree_id:
                        sub["status"] = "Concluído"
                        self.task_tree.item(task_id, values=(f" ↳ {sub['descricao']}",
                                                             sub["data_inicio"],
                                                             sub["data_termino"],
                                                             "Concluído"))
                        self.save_tasks()
                        return

# Execução principal
if __name__ == "__main__":
    root = tk.Tk()
    app = TaskApp(root)
    root.mainloop()


