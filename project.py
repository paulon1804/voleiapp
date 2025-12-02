import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import webbrowser
from datetime import datetime
from collections import defaultdict, deque

class AplicacaoVolei:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Vôlei")
        self.root.geometry("1000x800")
        
        # Dados
        self.jogadores = []
        self.posicoes = ["Ponta", "Central", "Saída", "Líbero", "Levantador"]
        self.status_jogador = ["Titular", "Reserva"]
        self.tipos_passe = ["A", "B", "C"]
        self.tipos_levantamento = ["Ponta", "Meio", "Saída", "Pipe Meio", "Pipe Saída"]
        self.status_ataque = ["ponto", "defesa", "erro"]
        
        # Variáveis de controle
        self.pontos_time = 0
        self.pontos_adversario = 0
        self.modulo_atual = "cadastro"
        self.historico_acoes = []
        self.pilha_desfazer = deque(maxlen=50)
        
        # Carregar dados existentes
        self.carregar_dados()
        
        # Frame principal
        self.frame_principal = ttk.Frame(root)
        self.frame_principal.pack(fill="both", expand=True)
        
        # Iniciar com o módulo de cadastro
        self.criar_modulo_cadastro()
    
    def carregar_dados(self):
        if os.path.exists("jogadores.json"):
            try:
                with open("jogadores.json", "r") as f:
                    self.jogadores = json.load(f)
            except:
                self.jogadores = []
    
    def salvar_dados(self):
        with open("jogadores.json", "w") as f:
            json.dump(self.jogadores, f)
    
    def confirmar_acao(self, titulo, mensagem, callback):
        if messagebox.askyesno(titulo, mensagem):
            callback()
    
    def desfazer_ultima_acao(self):
        if not self.pilha_desfazer:
            messagebox.showinfo("Informação", "Nenhuma ação para desfazer")
            return
        
        ultimo_estado = self.pilha_desfazer.pop()
        self.pontos_time = ultimo_estado['pontos_time']
        self.pontos_adversario = ultimo_estado['pontos_adversario']
        self.historico_acoes = ultimo_estado['historico_acoes']
        
        self.label_placar.config(text=str(self.pontos_time))
        self.label_placar_adv.config(text=str(self.pontos_adversario))
        self.atualizar_historico()
        
        messagebox.showinfo("Sucesso", "Última ação desfeita com sucesso")
    
    def salvar_estado(self):
        estado = {
            'pontos_time': self.pontos_time,
            'pontos_adversario': self.pontos_adversario,
            'historico_acoes': self.historico_acoes.copy()
        }
        self.pilha_desfazer.append(estado)
    
    def criar_modulo_cadastro(self):
        for widget in self.frame_principal.winfo_children():
            widget.destroy()
        
        self.modulo_atual = "cadastro"
        
        # Frame de cadastro
        frame_cadastro = ttk.LabelFrame(self.frame_principal, text="Cadastrar Novo Jogador", padding=10)
        frame_cadastro.pack(pady=10, padx=10, fill="x")
        
        # Campos do formulário
        ttk.Label(frame_cadastro, text="Nome:").grid(row=0, column=0, sticky="w")
        self.entry_nome = ttk.Entry(frame_cadastro, width=30)
        self.entry_nome.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(frame_cadastro, text="Posição:").grid(row=1, column=0, sticky="w")
        self.combo_posicao = ttk.Combobox(frame_cadastro, values=self.posicoes, state="readonly")
        self.combo_posicao.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(frame_cadastro, text="Status:").grid(row=2, column=0, sticky="w")
        self.combo_status = ttk.Combobox(frame_cadastro, values=self.status_jogador, state="readonly")
        self.combo_status.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        
        btn_cadastrar = ttk.Button(frame_cadastro, text="Cadastrar", command=self.cadastrar_jogador)
        btn_cadastrar.grid(row=3, column=0, columnspan=2, pady=10)
        
        # Frame de listagem
        frame_lista = ttk.LabelFrame(self.frame_principal, text="Jogadores Cadastrados", padding=10)
        frame_lista.pack(pady=10, padx=10, fill="both", expand=True)
        
        # Treeview para exibir jogadores
        colunas = ("Nome", "Posição", "Status")
        self.tree = ttk.Treeview(frame_lista, columns=colunas, show="headings")
        
        for col in colunas:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100 if col != "Nome" else 200)
        
        vsb = ttk.Scrollbar(frame_lista, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        
        frame_lista.grid_rowconfigure(0, weight=1)
        frame_lista.grid_columnconfigure(0, weight=1)
        
        # Frame de botões
        frame_botoes = ttk.Frame(self.frame_principal)
        frame_botoes.pack(pady=10)
        
        btn_remover = ttk.Button(frame_botoes, text="Remover Jogador", command=self.remover_jogador)
        btn_remover.pack(side="left", padx=5)
        
        if len(self.jogadores) > 0:
            btn_relatorio = ttk.Button(frame_botoes, text="Gerar Relatório", command=self.mostrar_relatorio)
            btn_relatorio.pack(side="left", padx=5)
        
        if len(self.jogadores) >= 6:
            btn_marcacao = ttk.Button(frame_botoes, text="Marcação de Pontos", command=self.criar_modulo_marcacao)
            btn_marcacao.pack(side="left", padx=5)
        else:
            ttk.Label(self.frame_principal, 
                     text=f"Cadastre pelo menos {6 - len(self.jogadores)} jogadores para marcação").pack(pady=10)
        
        self.atualizar_lista()
    
    def criar_modulo_marcacao(self):
        for widget in self.frame_principal.winfo_children():
            widget.destroy()
        
        self.modulo_atual = "marcacao"
        
        # Frame superior com placar
        frame_superior = ttk.Frame(self.frame_principal)
        frame_superior.pack(fill="x", padx=10, pady=10)
        
        # Placar do time
        frame_placar_time = ttk.Frame(frame_superior)
        frame_placar_time.pack(side="left", padx=10)
        ttk.Label(frame_placar_time, text="Nosso Time:", font=("Arial", 12)).pack()
        self.label_placar = ttk.Label(frame_placar_time, text=str(self.pontos_time), font=("Arial", 14, "bold"))
        self.label_placar.pack()
        
        # Placar do adversário
        frame_placar_adv = ttk.Frame(frame_superior)
        frame_placar_adv.pack(side="left", padx=10)
        ttk.Label(frame_placar_adv, text="Adversário:", font=("Arial", 12)).pack()
        self.label_placar_adv = ttk.Label(frame_placar_adv, text=str(self.pontos_adversario), font=("Arial", 14, "bold"))
        self.label_placar_adv.pack()
        
        # Botões de controle
        btn_voltar = ttk.Button(frame_superior, text="Voltar", command=self.criar_modulo_cadastro)
        btn_voltar.pack(side="right", padx=5)
        
        btn_desfazer = ttk.Button(frame_superior, text="Desfazer", command=self.desfazer_ultima_acao)
        btn_desfazer.pack(side="right", padx=5)
        
        btn_relatorio = ttk.Button(frame_superior, text="Relatório", command=self.mostrar_relatorio)
        btn_relatorio.pack(side="right", padx=5)
        
        # Frame principal de ações
        frame_acoes = ttk.Frame(self.frame_principal)
        frame_acoes.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Seção Saque
        frame_saque = ttk.LabelFrame(frame_acoes, text="Saque", padding=10)
        frame_saque.pack(fill="x", pady=5)
        
        ttk.Label(frame_saque, text="Jogador que sacou:").grid(row=0, column=0, sticky="w", padx=5)
        self.combo_saque_jogador = ttk.Combobox(frame_saque, values=[j["nome"] for j in self.jogadores if j['status'] == 'Titular'], state="readonly", width=25)
        self.combo_saque_jogador.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        btn_ponto_saque = ttk.Button(frame_saque, text="Ponto de Saque", command=lambda: self.registrar_ponto("saque"))
        btn_ponto_saque.grid(row=0, column=2, padx=5)
        
        # Seção Passe
        frame_passe = ttk.LabelFrame(frame_acoes, text="Passe", padding=10)
        frame_passe.pack(fill="x", pady=5)
        
        ttk.Label(frame_passe, text="Jogador que passou:").grid(row=0, column=0, sticky="w", padx=5)
        self.combo_passe_jogador = ttk.Combobox(frame_passe, values=[j["nome"] for j in self.jogadores if j['status'] == 'Titular'], state="readonly", width=25)
        self.combo_passe_jogador.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(frame_passe, text="Tipo de passe:").grid(row=0, column=2, sticky="w", padx=5)
        self.combo_tipo_passe = ttk.Combobox(frame_passe, values=self.tipos_passe, state="readonly", width=5)
        self.combo_tipo_passe.grid(row=0, column=3, padx=5, pady=5, sticky="w")
        
        btn_registrar_passe = ttk.Button(frame_passe, text="Registrar Passe", command=self.registrar_passe)
        btn_registrar_passe.grid(row=0, column=4, padx=5)
        
        # Seção Levantamento
        frame_levantamento = ttk.LabelFrame(frame_acoes, text="Levantamento", padding=10)
        frame_levantamento.pack(fill="x", pady=5)
        
        ttk.Label(frame_levantamento, text="Tipo de levantamento:").grid(row=0, column=0, sticky="w", padx=5)
        self.combo_tipo_levantamento = ttk.Combobox(frame_levantamento, values=self.tipos_levantamento, state="readonly", width=15)
        self.combo_tipo_levantamento.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(frame_levantamento, text="Bola de segunda:").grid(row=0, column=2, sticky="w", padx=5)
        self.var_bola_segunda = tk.BooleanVar()
        tk.Checkbutton(frame_levantamento, variable=self.var_bola_segunda).grid(row=0, column=3, padx=5, sticky="w")
        
        btn_ponto_segunda = ttk.Button(frame_levantamento, text="Ponto em Bola de Segunda", command=self.registrar_ponto_segunda)
        btn_ponto_segunda.grid(row=0, column=4, padx=5)
        
        btn_registrar_levantamento = ttk.Button(frame_levantamento, text="Registrar Levantamento", command=self.registrar_levantamento)
        btn_registrar_levantamento.grid(row=0, column=5, padx=5)
        
        # Seção Ataque
        frame_ataque = ttk.LabelFrame(frame_acoes, text="Ataque", padding=10)
        frame_ataque.pack(fill="x", pady=5)
        
        ttk.Label(frame_ataque, text="Jogador que atacou:").grid(row=0, column=0, sticky="w", padx=5)
        self.combo_ataque_jogador = ttk.Combobox(frame_ataque, values=[j["nome"] for j in self.jogadores if j['status'] == 'Titular'], state="readonly", width=25)
        self.combo_ataque_jogador.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(frame_ataque, text="Resultado:").grid(row=0, column=2, sticky="w", padx=5)
        self.combo_status_ataque = ttk.Combobox(frame_ataque, values=self.status_ataque, state="readonly", width=10)
        self.combo_status_ataque.grid(row=0, column=3, padx=5, pady=5, sticky="w")
        
        btn_registrar_ataque = ttk.Button(frame_ataque, text="Registrar Ataque", command=self.registrar_ataque)
        btn_registrar_ataque.grid(row=0, column=4, padx=5)
        
        # Seção Substituição
        frame_substituicao = ttk.LabelFrame(frame_acoes, text="Substituição", padding=10)
        frame_substituicao.pack(fill="x", pady=5)
        
        ttk.Label(frame_substituicao, text="Jogador que sai:").grid(row=0, column=0, sticky="w", padx=5)
        self.combo_jogador_sai = ttk.Combobox(frame_substituicao, state="readonly", width=25)
        self.combo_jogador_sai.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(frame_substituicao, text="Jogador que entra:").grid(row=0, column=2, sticky="w", padx=5)
        self.combo_jogador_entra = ttk.Combobox(frame_substituicao, state="readonly", width=25)
        self.combo_jogador_entra.grid(row=0, column=3, padx=5, pady=5, sticky="w")
        
        btn_substituir = ttk.Button(frame_substituicao, text="Realizar Substituição", command=self.registrar_substituicao)
        btn_substituir.grid(row=0, column=4, padx=5)
        
        # Seção Adversário
        frame_adv = ttk.LabelFrame(frame_acoes, text="Ações do Adversário", padding=10)
        frame_adv.pack(fill="x", pady=5)
        
        # Frame para organizar os botões
        frame_adv_botoes = ttk.Frame(frame_adv)
        frame_adv_botoes.pack(fill="x", pady=5)
        
        btn_ponto_adv = ttk.Button(frame_adv_botoes, text="Ponto Direto do Adversário", 
                                 command=self.registrar_ponto_adversario)
        btn_ponto_adv.pack(side="left", padx=5)
        
        btn_saque_adv = ttk.Button(frame_adv_botoes, text="Saque do Adversário", 
                                 command=self.registrar_saque_adversario)
        btn_saque_adv.pack(side="left", padx=5)
        
        # Seção Histórico
        frame_historico = ttk.LabelFrame(frame_acoes, text="Histórico", padding=10)
        frame_historico.pack(fill="both", expand=True, pady=5)
        
        self.text_historico = tk.Text(frame_historico, height=10, wrap="word")
        vsb_historico = ttk.Scrollbar(frame_historico, orient="vertical", command=self.text_historico.yview)
        self.text_historico.configure(yscrollcommand=vsb_historico.set)
        
        self.text_historico.grid(row=0, column=0, sticky="nsew")
        vsb_historico.grid(row=0, column=1, sticky="ns")
        
        frame_historico.grid_rowconfigure(0, weight=1)
        frame_historico.grid_columnconfigure(0, weight=1)
        
        self.atualizar_listas_substituicao()
        self.atualizar_historico()
    
    def registrar_saque_adversario(self):
        def registrar_como_ponto():
            self.salvar_estado()
            self.pontos_adversario += 1
            self.label_placar_adv.config(text=str(self.pontos_adversario))
            
            acao = f"[{datetime.now().strftime('%H:%M:%S')}] Ponto de saque do adversário | Placar: {self.pontos_time}x{self.pontos_adversario}"
            self.historico_acoes.append(acao)
            self.atualizar_historico()
            
            messagebox.showinfo("Sucesso", f"Ponto de saque do adversário registrado!\nPlacar: {self.pontos_time}x{self.pontos_adversario}")
        
        def registrar_sem_ponto():
            acao = f"[{datetime.now().strftime('%H:%M:%S')}] Saque do adversário (sem ponto) | Placar: {self.pontos_time}x{self.pontos_adversario}"
            self.historico_acoes.append(acao)
            self.atualizar_historico()
            
            messagebox.showinfo("Registrado", "Saque do adversário registrado (sem ponto)")
        
        # Diálogo para escolher se foi ponto ou não
        resposta = messagebox.askyesno("Saque do Adversário", "O saque do adversário resultou em ponto direto?")
        
        if resposta:
            registrar_como_ponto()
        else:
            registrar_sem_ponto()
    
    def atualizar_listas_substituicao(self):
        """Atualiza as listas de jogadores para substituição"""
        if self.modulo_atual != "marcacao":
            return
            
        # Separar titulares e reservas
        self.jogadores_em_campo = [j for j in self.jogadores if j['status'] == 'Titular']
        self.jogadores_reservas = [j for j in self.jogadores if j['status'] == 'Reserva']
        
        # Atualizar comboboxes
        if hasattr(self, 'combo_jogador_sai') and self.combo_jogador_sai:
            self.combo_jogador_sai['values'] = [j['nome'] for j in self.jogadores_em_campo]
            self.combo_jogador_entra['values'] = [j['nome'] for j in self.jogadores_reservas]
            
            # Limpar seleções
            self.combo_jogador_sai.set('')
            self.combo_jogador_entra.set('')
        
        # Atualizar também os comboboxes de ações que usam apenas titulares
        if hasattr(self, 'combo_saque_jogador'):
            self.combo_saque_jogador['values'] = [j['nome'] for j in self.jogadores_em_campo]
            self.combo_passe_jogador['values'] = [j['nome'] for j in self.jogadores_em_campo]
            self.combo_ataque_jogador['values'] = [j['nome'] for j in self.jogadores_em_campo]
    
    def atualizar_historico(self):
        self.text_historico.delete(1.0, tk.END)
        for acao in self.historico_acoes:
            self.text_historico.insert(tk.END, acao + "\n")
        self.text_historico.see(tk.END)
    
    def atualizar_lista(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for jogador in self.jogadores:
            self.tree.insert("", "end", values=(jogador["nome"], jogador["posicao"], jogador["status"]))
    
    def cadastrar_jogador(self):
        nome = self.entry_nome.get().strip()
        posicao = self.combo_posicao.get()
        status = self.combo_status.get()
        
        if not nome:
            messagebox.showerror("Erro", "Por favor, insira o nome do jogador.")
            return
        
        if not posicao:
            messagebox.showerror("Erro", "Por favor, selecione a posição do jogador.")
            return
        
        if not status:
            messagebox.showerror("Erro", "Por favor, selecione se o jogador é titular ou reserva.")
            return
        
        jogador = {
            "nome": nome,
            "posicao": posicao,
            "status": status
        }
        
        self.jogadores.append(jogador)
        self.salvar_dados()
        self.atualizar_lista()
        
        # Limpar campos
        self.entry_nome.delete(0, tk.END)
        self.combo_posicao.set('')
        self.combo_status.set('')
        
        messagebox.showinfo("Sucesso", "Jogador cadastrado com sucesso!")
        
        # Atualizar listas se estiver no módulo de marcação
        if self.modulo_atual == "marcacao":
            self.atualizar_listas_substituicao()
        else:
            # Recriar o módulo de cadastro para atualizar os botões
            self.criar_modulo_cadastro()
    
    def remover_jogador(self):
        selecionado = self.tree.selection()
        
        if not selecionado:
            messagebox.showerror("Erro", "Por favor, selecione um jogador para remover.")
            return
        
        item = selecionado[0]
        index = self.tree.index(item)
        
        confirmacao = messagebox.askyesno("Confirmar", "Tem certeza que deseja remover este jogador?")
        
        if confirmacao:
            jogador_removido = self.jogadores[index]
            del self.jogadores[index]
            self.salvar_dados()
            self.atualizar_lista()
            
            if self.modulo_atual == "marcacao":
                self.atualizar_listas_substituicao()
                if len(self.jogadores) < 6:
                    messagebox.showwarning("Aviso", "Mínimo de 6 jogadores não atingido. Voltando para cadastro.")
                    self.criar_modulo_cadastro()
                else:
                    messagebox.showinfo("Sucesso", f"Jogador {jogador_removido['nome']} removido com sucesso!")
            else:
                # Recriar o módulo de cadastro para atualizar os botões
                self.criar_modulo_cadastro()
                messagebox.showinfo("Sucesso", f"Jogador {jogador_removido['nome']} removido com sucesso!")
    
    def registrar_substituicao(self):
        jogador_sai = self.combo_jogador_sai.get()
        jogador_entra = self.combo_jogador_entra.get()
        
        if not jogador_sai:
            messagebox.showerror("Erro", "Selecione o jogador que vai sair.")
            return
        
        if not jogador_entra:
            messagebox.showerror("Erro", "Selecione o jogador que vai entrar.")
            return
        
        def realizar_substituicao():
            # Encontrar os jogadores
            jogador_sai_obj = next(j for j in self.jogadores if j['nome'] == jogador_sai)
            jogador_entra_obj = next(j for j in self.jogadores if j['nome'] == jogador_entra)
            
            # Alterar status
            jogador_sai_obj['status'] = 'Reserva'
            jogador_entra_obj['status'] = 'Titular'
            
            # Registrar no histórico
            acao = f"[{datetime.now().strftime('%H:%M:%S')}] Substituição: {jogador_sai} ({jogador_sai_obj['posicao']}) → {jogador_entra} ({jogador_entra_obj['posicao']})"
            self.historico_acoes.append(acao)
            
            # Atualizar e salvar
            self.salvar_dados()
            self.atualizar_listas_substituicao()
            self.atualizar_historico()
            self.atualizar_lista()
            
            messagebox.showinfo("Sucesso", f"Substituição realizada:\n{jogador_sai} → {jogador_entra}")
        
        self.confirmar_acao(
            "Confirmar Substituição",
            f"Confirmar substituição?\n{jogador_sai} sai / {jogador_entra} entra",
            realizar_substituicao
        )
    
    def registrar_ponto_segunda(self):
        tipo_levantamento = self.combo_tipo_levantamento.get()
        if not tipo_levantamento:
            messagebox.showerror("Erro", "Selecione o tipo de levantamento.")
            return
        
        def acao():
            self.salvar_estado()
            self.pontos_time += 1
            self.label_placar.config(text=str(self.pontos_time))
            
            acao_texto = f"[{datetime.now().strftime('%H:%M:%S')}] Ponto em bola de segunda ({tipo_levantamento}) | Placar: {self.pontos_time}x{self.pontos_adversario}"
            self.historico_acoes.append(acao_texto)
            self.atualizar_historico()
            
            # Limpar campos
            self.combo_tipo_levantamento.set('')
            self.var_bola_segunda.set(False)
        
        self.confirmar_acao(
            "Confirmar Ponto",
            f"Registrar ponto em bola de segunda ({tipo_levantamento})?\nPlacar atual: {self.pontos_time}x{self.pontos_adversario}",
            acao
        )
    
    def registrar_ponto_adversario(self):
        def acao():
            self.salvar_estado()
            self.pontos_adversario += 1
            self.label_placar_adv.config(text=str(self.pontos_adversario))
            
            acao_texto = f"[{datetime.now().strftime('%H:%M:%S')}] Ponto do adversário | Placar: {self.pontos_time}x{self.pontos_adversario}"
            self.historico_acoes.append(acao_texto)
            self.atualizar_historico()
        
        self.confirmar_acao(
            "Confirmar Ponto",
            f"Registrar ponto para o adversário?\nPlacar atual: {self.pontos_time}x{self.pontos_adversario}",
            acao
        )
    
    def registrar_ponto(self, tipo):
        if tipo == "saque":
            jogador = self.combo_saque_jogador.get()
            if not jogador:
                messagebox.showerror("Erro", "Selecione o jogador que sacou.")
                return
            
            def acao():
                self.salvar_estado()
                self.pontos_time += 1
                self.label_placar.config(text=str(self.pontos_time))
                acao_texto = f"[{datetime.now().strftime('%H:%M:%S')}] Ponto de saque - {jogador} | Placar: {self.pontos_time}x{self.pontos_adversario}"
                self.historico_acoes.append(acao_texto)
                self.atualizar_historico()
            
            self.confirmar_acao(
                "Confirmar Ponto",
                f"Registrar ponto de saque para {jogador}?\nPlacar atual: {self.pontos_time}x{self.pontos_adversario}",
                acao
            )
    
    def registrar_passe(self):
        jogador = self.combo_passe_jogador.get()
        tipo_passe = self.combo_tipo_passe.get()
        
        if not jogador:
            messagebox.showerror("Erro", "Selecione o jogador que passou.")
            return
        
        if not tipo_passe:
            messagebox.showerror("Erro", "Selecione o tipo de passe.")
            return
        
        acao = f"[{datetime.now().strftime('%H:%M:%S')}] Passe {tipo_passe} - {jogador}"
        self.historico_acoes.append(acao)
        self.atualizar_historico()
        messagebox.showinfo("Sucesso", f"Passe {tipo_passe} registrado para {jogador}")
    
    def registrar_levantamento(self):
        tipo_levantamento = self.combo_tipo_levantamento.get()
        bola_segunda = self.var_bola_segunda.get()
        
        if not tipo_levantamento:
            messagebox.showerror("Erro", "Selecione o tipo de levantamento.")
            return
        
        if bola_segunda:
            messagebox.showwarning("Aviso", "Para bola de segunda que resulta em ponto, use o botão 'Ponto em Bola de Segunda'")
            return
        
        acao = f"[{datetime.now().strftime('%H:%M:%S')}] Levantamento - {tipo_levantamento}"
        self.historico_acoes.append(acao)
        self.atualizar_historico()
        
        # Limpar campos
        self.combo_tipo_levantamento.set('')
        
        messagebox.showinfo("Sucesso", f"Levantamento registrado como {tipo_levantamento}")
    
    def registrar_ataque(self):
        jogador = self.combo_ataque_jogador.get()
        status = self.combo_status_ataque.get().lower()
        
        if not jogador:
            messagebox.showerror("Erro", "Selecione o jogador que atacou.")
            return
        
        if not status:
            messagebox.showerror("Erro", "Selecione o resultado do ataque.")
            return
        
        def acao():
            self.salvar_estado()
            if status == "ponto":
                self.pontos_time += 1
                self.label_placar.config(text=str(self.pontos_time))
            
            acao_texto = f"[{datetime.now().strftime('%H:%M:%S')}] Ataque - {jogador} | Resultado: {status} | Placar: {self.pontos_time}x{self.pontos_adversario}"
            self.historico_acoes.append(acao_texto)
            self.atualizar_historico()
            
            # Limpar campos
            self.combo_ataque_jogador.set('')
            self.combo_status_ataque.set('')
        
        self.confirmar_acao(
            "Confirmar Ataque",
            f"Registrar ataque de {jogador} como {status}?\nPlacar atual: {self.pontos_time}x{self.pontos_adversario}",
            acao
        )

    def mostrar_relatorio(self):
        # Criar janela de relatório
        janela_relatorio = tk.Toplevel(self.root)
        janela_relatorio.title("Relatório de Desempenho")
        janela_relatorio.geometry("800x600")
        
        # Frame principal
        frame_principal = ttk.Frame(janela_relatorio)
        frame_principal.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Área de texto com scroll
        scrollbar = ttk.Scrollbar(frame_principal)
        scrollbar.pack(side="right", fill="y")
        
        texto_relatorio = tk.Text(
            frame_principal,
            wrap="word",
            yscrollcommand=scrollbar.set,
            font=("Courier New", 10),
            padx=10,
            pady=10
        )
        texto_relatorio.pack(fill="both", expand=True)
        scrollbar.config(command=texto_relatorio.yview)

        # Gerar conteúdo do relatório
        self.gerar_conteudo_relatorio(texto_relatorio)
        
        # Botões de ação
        frame_botoes = ttk.Frame(janela_relatorio)
        frame_botoes.pack(pady=10)

        btn_exportar = ttk.Button(frame_botoes, text="Exportar HTML", command=self.exportar_relatorio_html)
        btn_exportar.pack(side="left", padx=5)

        btn_fechar = ttk.Button(frame_botoes, text="Fechar", command=janela_relatorio.destroy)
        btn_fechar.pack(side="left", padx=5)

    def analisar_estatisticas(self):
        estatisticas = defaultdict(lambda: {
            'pontos_saque': 0,
            'pontos_ataque': 0,
            'total_ataques': 0,
            'passes': 0,
            'tipos_passe': defaultdict(int),
            'levantamentos': 0,
            'substituicoes': 0,
            'entrou_em_campo': False,
            'posicao': '',
            'status': '',
            'eficiencia_ataque': 0.0,
            'eficiencia_passe': 0.0
        })

        for jogador in self.jogadores:
            estatisticas[jogador['nome']]['posicao'] = jogador['posicao']
            estatisticas[jogador['nome']]['status'] = jogador['status']

        total_pontos_saque = 0
        total_pontos_ataque = 0
        total_ataques = 0
        total_passes = 0

        for acao in self.historico_acoes:
            if "Ponto de saque - " in acao:
                nome = acao.split("Ponto de saque - ")[1].split(" |")[0]
                estatisticas[nome]['pontos_saque'] += 1
                total_pontos_saque += 1

            elif "Ataque - " in acao and "Resultado: " in acao:
                nome = acao.split("Ataque - ")[1].split(" |")[0]
                resultado = acao.split("Resultado: ")[1].split(" |")[0]
                estatisticas[nome]['total_ataques'] += 1
                total_ataques += 1
                if resultado.strip().lower() == "ponto":
                    estatisticas[nome]['pontos_ataque'] += 1
                    total_pontos_ataque += 1

            elif "Passe " in acao and " - " in acao:
                partes = acao.split("Passe ")[1].split(" - ")
                tipo_passe = partes[0].strip()
                nome = partes[1].split(" |")[0] if " |" in partes[1] else partes[1]
                estatisticas[nome]['passes'] += 1
                estatisticas[nome]['tipos_passe'][tipo_passe] += 1
                total_passes += 1

            elif "Substituição: " in acao and " → " in acao:
                partes = acao.split("Substituição: ")[1].split(" → ")
                jogador_sai = partes[0].split(" (")[0]
                jogador_entra = partes[1].split(" (")[0]
                estatisticas[jogador_sai]['substituicoes'] += 1
                estatisticas[jogador_entra]['substituicoes'] += 1
                estatisticas[jogador_entra]['entrou_em_campo'] = True

        for stats in estatisticas.values():
            if stats['total_ataques'] > 0:
                stats['eficiencia_ataque'] = (stats['pontos_ataque'] / stats['total_ataques']) * 100
            if stats['passes'] > 0:
                eficiencia = 0
                for tipo, qtd in stats['tipos_passe'].items():
                    if tipo == 'A':
                        eficiencia += qtd * 1.0
                    elif tipo == 'B':
                        eficiencia += qtd * 0.75
                    elif tipo == 'C':
                        eficiencia += qtd * 0.5
                stats['eficiencia_passe'] = (eficiencia / stats['passes']) * 100
            stats['tipos_passe'] = dict(stats['tipos_passe'])

        sets = []
        pontos_time_set = 0
        pontos_adversario_set = 0
        acoes_set = []

        for acao in self.historico_acoes:
            acoes_set.append(acao)
            if "Placar: " in acao:
                try:
                    placar = acao.split("Placar: ")[1]
                    pontos_time, pontos_adversario = map(int, placar.split("x"))
                except (IndexError, ValueError):
                    continue

                if pontos_time >= 25 or pontos_adversario >= 25:
                    if abs(pontos_time - pontos_adversario) >= 2:
                        sets.append({
                            'numero': len(sets) + 1,
                            'pontos_time': pontos_time - pontos_time_set,
                            'pontos_adversario': pontos_adversario - pontos_adversario_set,
                            'acoes': acoes_set.copy()
                        })
                        pontos_time_set = pontos_time
                        pontos_adversario_set = pontos_adversario
                        acoes_set = []

        if acoes_set:
            sets.append({
                'numero': len(sets) + 1,
                'pontos_time': self.pontos_time - pontos_time_set,
                'pontos_adversario': self.pontos_adversario - pontos_adversario_set,
                'acoes': acoes_set.copy()
            })

        eficiencia_ataque_geral = (total_pontos_ataque / total_ataques * 100) if total_ataques > 0 else 0
        eficiencias_passe = [stats['eficiencia_passe'] for stats in estatisticas.values() if stats['passes'] > 0]
        eficiencia_passe_media = sum(eficiencias_passe) / len(eficiencias_passe) if eficiencias_passe else 0
        total_substituicoes = sum(stats['substituicoes'] for stats in estatisticas.values()) // 2

        recomendacoes = []
        if eficiencia_ataque_geral < 40:
            recomendacoes.append(
                f"A eficiência de ataque está baixa ({eficiencia_ataque_geral:.1f}%). Trabalhe em variações de ataque."
            )
        elif eficiencia_ataque_geral > 60:
            recomendacoes.append(
                f"Ótima eficiência de ataque ({eficiencia_ataque_geral:.1f}%). Continue explorando essas jogadas."
            )

        if total_pontos_saque < 3 and self.pontos_time > 0:
            recomendacoes.append(
                f"Poucos pontos diretos de saque ({total_pontos_saque}). Treinar saques agressivos pode ajudar."
            )

        if total_substituicoes == 0 and any(j['status'] == 'Reserva' for j in self.jogadores):
            recomendacoes.append("Nenhuma substituição registrada. Considere usar mais o banco de reservas.")

        if not recomendacoes:
            recomendacoes.append("O desempenho geral foi consistente. Mantenha a estratégia e pequenos ajustes finos.")

        return {
            "estatisticas": dict(estatisticas),
            "totais": {
                "pontos_saque": total_pontos_saque,
                "pontos_ataque": total_pontos_ataque,
                "total_ataques": total_ataques,
                "passes": total_passes,
                "eficiencia_ataque": eficiencia_ataque_geral,
                "eficiencia_passe": eficiencia_passe_media,
                "substituicoes": total_substituicoes
            },
            "sets": sets,
            "recomendacoes": recomendacoes
        }

    def gerar_conteudo_relatorio(self, texto_widget):
        dados = self.analisar_estatisticas()
        estatisticas = dados["estatisticas"]
        totais = dados["totais"]
        sets = dados["sets"]
        recomendacoes = dados["recomendacoes"]

        # Configurar tags para formatação
        texto_widget.tag_configure("titulo", font=("Arial", 14, "bold"), justify="center")
        texto_widget.tag_configure("subtitulo", font=("Arial", 12, "bold"), underline=True)
        texto_widget.tag_configure("destaque", font=("Arial", 10, "bold"))
        texto_widget.tag_configure("negrito", font=("Arial", 10, "bold"))
        
        # Cabeçalho
        texto_widget.insert("end", "RELATÓRIO DE DESEMPENHO\n", "titulo")
        texto_widget.insert("end", f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n")
        texto_widget.insert("end", f"Placar Final: {self.pontos_time} x {self.pontos_adversario}\n\n")
        
        # Resumo
        texto_widget.insert("end", "RESUMO EXECUTIVO\n", "subtitulo")
        texto_widget.insert("end", "Estatísticas gerais do time durante a partida:\n\n")
        texto_widget.insert("end", f"• Pontos Totais: {self.pontos_time}\n")
        texto_widget.insert("end", f"• Pontos de Saque: {totais['pontos_saque']}\n")
        texto_widget.insert("end", f"• Pontos de Ataque: {totais['pontos_ataque']}\n")
        texto_widget.insert("end", f"• Eficiência de Ataque: {totais['eficiencia_ataque']:.1f}%\n")
        texto_widget.insert("end", f"• Eficiência Média de Passe: {totais['eficiencia_passe']:.1f}%\n")
        texto_widget.insert("end", f"• Substituições: {totais['substituicoes']}\n\n")

        texto_widget.insert("end", "ESTATÍSTICAS POR JOGADOR\n", "subtitulo")
        if not estatisticas:
            texto_widget.insert("end", "Nenhum dado disponível. Cadastre jogadores e registre ações.\n\n")
        else:
            cabecalho = "{:<20} {:<12} {:<10} {:<6} {:<6} {:<8} {:<8} {:<6}\n".format(
                "Jogador", "Posição", "Status", "Saque", "Ataque", "Total A", "Efic.A", "Passes"
            )
            texto_widget.insert("end", cabecalho, "negrito")
            for nome in sorted(estatisticas.keys()):
                stats = estatisticas[nome]
                linha = "{:<20} {:<12} {:<10} {:<6} {:<6} {:<8} {:<8} {:<6}\n".format(
                    nome,
                    stats['posicao'] or "-",
                    stats['status'] or "-",
                    stats['pontos_saque'],
                    stats['pontos_ataque'],
                    stats['total_ataques'],
                    f"{stats['eficiencia_ataque']:.1f}%" if stats['total_ataques'] > 0 else "-",
                    stats['passes']
                )
                texto_widget.insert("end", linha)
            texto_widget.insert("end", "\n")

        if sets:
            texto_widget.insert("end", "ANÁLISE POR SET\n", "subtitulo")
            for set_ in sets:
                resultado = "Vitória" if set_['pontos_time'] > set_['pontos_adversario'] else "Derrota"
                texto_widget.insert(
                    "end",
                    f"Set {set_['numero']}: {set_['pontos_time']} x {set_['pontos_adversario']} ({resultado})\n"
                )
            texto_widget.insert("end", "\n")

        texto_widget.insert("end", "RECOMENDAÇÕES TÁTICAS\n", "subtitulo")
        for rec in recomendacoes:
            texto_widget.insert("end", f"• {rec}\n")
        texto_widget.insert("end", "\n")

    def exportar_relatorio_html(self):
        dados = self.analisar_estatisticas()
        estatisticas = dados["estatisticas"]
        totais = dados["totais"]
        sets = dados["sets"]
        recomendacoes = dados["recomendacoes"]

        jogadores_ordenados = sorted(estatisticas.items(), key=lambda item: item[0])

        melhor_jogador = "-"
        melhor_jogador_pontos = 0
        if jogadores_ordenados:
            melhor_jogador, melhor_stats = max(
                jogadores_ordenados,
                key=lambda item: item[1]['pontos_saque'] + item[1]['pontos_ataque']
            )
            melhor_jogador_pontos = melhor_stats['pontos_saque'] + melhor_stats['pontos_ataque']

        linhas_tabela = []
        for nome, stats in jogadores_ordenados:
            linhas_tabela.append(
                f"<tr>"
                f"<td>{nome}</td>"
                f"<td>{stats['posicao'] or '-'}</td>"
                f"<td>{stats['status'] or '-'}</td>"
                f"<td>{stats['pontos_saque']}</td>"
                f"<td>{stats['pontos_ataque']}</td>"
                f"<td>{stats['total_ataques']}</td>"
                f"<td>{stats['eficiencia_ataque']:.1f}%</td>"
                f"<td>{stats['passes']}</td>"
                f"<td>{stats['eficiencia_passe']:.1f}%</td>"
                f"<td>{stats['substituicoes']}</td>"
                f"</tr>"
            )

        total_ataques = totais['total_ataques']
        media_eficiencia_passe = totais['eficiencia_passe']

        total_passes = totais['passes']
        total_substituicoes = totais['substituicoes']

        dados_pontos = [stats['pontos_saque'] + stats['pontos_ataque'] for _, stats in jogadores_ordenados]
        labels_jogadores = [nome for nome, _ in jogadores_ordenados]

        posicoes = defaultdict(lambda: {'total': 0.0, 'count': 0})
        for _, stats in jogadores_ordenados:
            if stats['total_ataques'] > 0:
                pos = stats['posicao'] or 'Indefinido'
                posicoes[pos]['total'] += stats['eficiencia_ataque']
                posicoes[pos]['count'] += 1

        labels_posicoes = list(posicoes.keys())
        dados_posicoes = [
            (info['total'] / info['count']) if info['count'] > 0 else 0 for info in posicoes.values()
        ]

        eficiencia_total_ataque = (totais['pontos_ataque'] / total_ataques * 100) if total_ataques else 0
        linhas_tabela_html = ''.join(linhas_tabela)
        labels_jogadores_json = json.dumps(labels_jogadores, ensure_ascii=False)
        dados_pontos_json = json.dumps(dados_pontos)
        labels_posicoes_json = json.dumps(labels_posicoes, ensure_ascii=False)
        dados_posicoes_json = json.dumps(dados_posicoes)

        html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Relatório de Desempenho</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f7f9fc;
            color: #2c3e50;
        }}
        h1, h2 {{
            color: #1f3a93;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            background: #fff;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        }}
        th, td {{
            padding: 10px;
            border: 1px solid #dfe6e9;
            text-align: left;
        }}
        th {{
            background-color: #3498db;
            color: white;
        }}
        .resumo, .recomendacoes {{
            background: #fff;
            padding: 15px;
            margin-top: 20px;
            border-radius: 6px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        }}
        .set-container {{
            background: #fff;
            padding: 15px;
            border-radius: 6px;
            margin-top: 15px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        }}
        .total-row {{
            font-weight: bold;
            background-color: #ecf0f1;
        }}
    </style>
</head>
<body>
    <h1>Relatório de Desempenho</h1>
    <p><strong>Data:</strong> {datetime.now().strftime("%d/%m/%Y %H:%M")}</p>
    <p><strong>Placar Final:</strong> {self.pontos_time} x {self.pontos_adversario}</p>

    <div class="resumo">
        <h2>Resumo Executivo</h2>
        <p><strong>Pontos Totais:</strong> {self.pontos_time}</p>
        <p><strong>Pontos de Saque:</strong> {totais['pontos_saque']}</p>
        <p><strong>Pontos de Ataque:</strong> {totais['pontos_ataque']}</p>
        <p><strong>Eficiência de Ataque:</strong> {totais['eficiencia_ataque']:.1f}%</p>
        <p><strong>Eficiência Média de Passe:</strong> {media_eficiencia_passe:.1f}%</p>
        <p><strong>Substituições:</strong> {total_substituicoes}</p>
        <p><strong>Melhor Jogador:</strong> {melhor_jogador} ({melhor_jogador_pontos} pontos)</p>
    </div>

    <h2>Estatísticas por Jogador</h2>
    <table>
        <thead>
            <tr>
                <th>Jogador</th>
                <th>Posição</th>
                <th>Status</th>
                <th>Pontos Saque</th>
                <th>Pontos Ataque</th>
                <th>Total Ataques</th>
                <th>Eficiência Ataque</th>
                <th>Passes</th>
                <th>Eficiência Passe</th>
                <th>Substituições</th>
            </tr>
        </thead>
        <tbody>
            {linhas_tabela_html if linhas_tabela_html else '<tr><td colspan="10">Nenhum dado disponível.</td></tr>'}
            <tr class="total-row">
                <td>TOTAL</td>
                <td>-</td>
                <td>-</td>
                <td>{totais['pontos_saque']}</td>
                <td>{totais['pontos_ataque']}</td>
                <td>{total_ataques}</td>
                <td>{eficiencia_total_ataque:.1f}%</td>
                <td>{total_passes}</td>
                <td>{media_eficiencia_passe:.1f}%</td>
                <td>{total_substituicoes}</td>
            </tr>
        </tbody>
    </table>

    <h2>Recomendações Táticas</h2>
    <div class="recomendacoes">
        {"".join(f"<p>• {rec}</p>" for rec in recomendacoes)}
    </div>

    <h2>Análise por Set</h2>
    {"".join(
        f"<div class='set-container'>"
        f"<h3>Set {set_['numero']} - {set_['pontos_time']} x {set_['pontos_adversario']}</h3>"
        f"<p><strong>Resultado:</strong> {'Vitória' if set_['pontos_time'] > set_['pontos_adversario'] else 'Derrota'}</p>"
        f"</div>" for set_ in sets
    ) if sets else "<p>Nenhum set analisado.</p>"}

    <h2>Histórico Completo</h2>
    <ul>
        {"".join(f"<li>{acao}</li>" for acao in self.historico_acoes) if self.historico_acoes else "<li>Sem registros.</li>"}
    </ul>

    <canvas id="graficoPontos" height="120"></canvas>
    <canvas id="graficoPosicoes" height="120"></canvas>

    <script>
        const ctxPontos = document.getElementById('graficoPontos').getContext('2d');
        new Chart(ctxPontos, {{
            type: 'bar',
            data: {{
                labels: {labels_jogadores_json},
                datasets: [{{
                    label: 'Total de Pontos',
                    data: {dados_pontos_json},
                    backgroundColor: 'rgba(52, 152, 219, 0.7)',
                    borderColor: 'rgba(41, 128, 185, 1)',
                    borderWidth: 1
                }}]
            }},
            options: {{
                responsive: true,
                scales: {{
                    y: {{
                        beginAtZero: true
                    }}
                }}
            }}
        }});

        const ctxPosicoes = document.getElementById('graficoPosicoes').getContext('2d');
        new Chart(ctxPosicoes, {{
            type: 'bar',
            data: {{
                labels: {labels_posicoes_json},
                datasets: [{{
                    label: 'Eficiência Média de Ataque (%)',
                    data: {dados_posicoes_json},
                    backgroundColor: 'rgba(46, 204, 113, 0.7)',
                    borderColor: 'rgba(39, 174, 96, 1)',
                    borderWidth: 1
                }}]
            }},
            options: {{
                responsive: true,
                scales: {{
                    y: {{
                        beginAtZero: true,
                        max: 100
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""

        filepath = filedialog.asksaveasfilename(
            defaultextension=".html",
            filetypes=[("Arquivos HTML", "*.html"), ("Todos os arquivos", "*.*")],
            title="Salvar relatório como"
        )

        if not filepath:
            return

        try:
            with open(filepath, "w", encoding="utf-8") as arquivo:
                arquivo.write(html)
            if messagebox.askyesno("Relatório Gerado", "Relatório salvo com sucesso! Deseja abrir o arquivo agora?"):
                webbrowser.open(filepath)
        except Exception as erro:
            messagebox.showerror("Erro", f"Falha ao salvar o relatório:\n{erro}")

if __name__ == "__main__":
    root = tk.Tk()
    app = AplicacaoVolei(root)
    root.mainloop()
