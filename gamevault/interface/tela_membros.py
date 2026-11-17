import tkinter as tk
from collections.abc import Callable
from tkinter import ttk

from gamevault.interface.estilos import CORES, FONTE
from gamevault.interface.formulario_membro import FormularioMembro
from gamevault.modelos.membro import Membro
from gamevault.sistema import SistemaGameVault


class TelaMembros(ttk.Frame):
    def __init__(
        self,
        master: tk.Misc,
        sistema: SistemaGameVault,
        ao_notificar: Callable[[str, str], None] | None = None,
    ):
        super().__init__(master, style="App.TFrame", padding=(26, 22, 26, 16))
        self.sistema = sistema
        self.ao_notificar = ao_notificar
        self._membros_por_item: dict[str, Membro] = {}
        self._id_selecionado: int | None = None
        self._formulario: FormularioMembro | None = None
        self.contagem_var = tk.StringVar(value="0 membros")

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self._criar_cabecalho()
        self._criar_conteudo()
        self.atualizar()

    def _criar_cabecalho(self) -> None:
        cabecalho = ttk.Frame(self, style="App.TFrame")
        cabecalho.grid(row=0, column=0, sticky="ew", pady=(0, 18))
        cabecalho.columnconfigure(0, weight=1)

        textos = ttk.Frame(cabecalho, style="App.TFrame")
        textos.grid(row=0, column=0, sticky="w")
        ttk.Label(
            textos,
            text="Membros",
            style="PageTitle.TLabel",
        ).pack(anchor="w")
        ttk.Label(
            textos,
            text="Cadastros e empréstimos ativos.",
            style="PageSubtitle.TLabel",
        ).pack(anchor="w", pady=(4, 0))

        ttk.Label(
            cabecalho,
            textvariable=self.contagem_var,
            style="Count.TLabel",
        ).grid(row=0, column=1, padx=(12, 10))
        ttk.Button(
            cabecalho,
            text="Novo membro",
            style="Primary.TButton",
            command=self._novo_membro,
        ).grid(row=0, column=2)

    def _criar_conteudo(self) -> None:
        painel = ttk.Panedwindow(
            self,
            orient=tk.HORIZONTAL,
            style="GameVault.TPanedwindow",
        )
        painel.grid(row=1, column=0, sticky="nsew")

        tabela_card = tk.Frame(
            painel,
            bg=CORES["superficie"],
            highlightthickness=1,
            highlightbackground=CORES["borda"],
        )
        tabela_card.columnconfigure(0, weight=1)
        tabela_card.rowconfigure(0, weight=1)

        self.tabela = ttk.Treeview(
            tabela_card,
            columns=("id", "nome", "email", "ativos"),
            show="headings",
            selectmode="browse",
            style="GameVault.Treeview",
        )
        configuracao = {
            "id": ("ID", 70, tk.CENTER),
            "nome": ("NOME", 220, tk.W),
            "email": ("E-MAIL", 280, tk.W),
            "ativos": ("ATIVOS", 80, tk.CENTER),
        }
        for coluna, (titulo, largura, alinhamento) in configuracao.items():
            self.tabela.heading(coluna, text=titulo, anchor=alinhamento)
            self.tabela.column(
                coluna,
                width=largura,
                minwidth=largura,
                anchor=alinhamento,
                stretch=coluna in ("nome", "email"),
            )
        self.tabela.grid(row=0, column=0, sticky="nsew")
        self.tabela.bind("<<TreeviewSelect>>", self._ao_selecionar)

        rolagem = ttk.Scrollbar(
            tabela_card,
            orient=tk.VERTICAL,
            command=self.tabela.yview,
            style="GameVault.Vertical.TScrollbar",
        )
        rolagem.grid(row=0, column=1, sticky="ns")
        self.tabela.configure(yscrollcommand=rolagem.set)

        self.estado_vazio = tk.Label(
            tabela_card,
            text="Ainda não há membros cadastrados.",
            bg=CORES["superficie"],
            fg=CORES["texto_secundario"],
            font=(FONTE, 11),
        )

        self.detalhes = tk.Frame(
            painel,
            bg=CORES["superficie"],
            width=300,
            highlightthickness=1,
            highlightbackground=CORES["borda"],
            padx=20,
            pady=20,
        )
        painel.add(tabela_card, weight=1)
        painel.add(self.detalhes, weight=0)

    def atualizar(self) -> None:
        membros = self.sistema.cadastro_membros.listar()
        for item in self.tabela.get_children():
            self.tabela.delete(item)
        self._membros_por_item.clear()

        for membro in membros:
            item = f"membro-{membro.id_membro}"
            self._membros_por_item[item] = membro
            self.tabela.insert(
                "",
                tk.END,
                iid=item,
                values=(
                    membro.id_membro,
                    membro.nome,
                    membro.email,
                    membro.contar_ativos(),
                ),
            )

        total = len(membros)
        self.contagem_var.set(
            f"{total} membro" if total == 1 else f"{total} membros"
        )
        self._atualizar_estado_vazio(total)

        item_anterior = (
            f"membro-{self._id_selecionado}"
            if self._id_selecionado is not None
            else None
        )
        itens = self.tabela.get_children()
        item = item_anterior if item_anterior in itens else None
        if item is None and itens:
            item = itens[0]
        if item is None:
            self._id_selecionado = None
            self._mostrar_sem_selecao()
            return
        self.tabela.selection_set(item)
        self.tabela.focus(item)
        self._mostrar_detalhes(self._membros_por_item[item])

    def _atualizar_estado_vazio(self, total: int) -> None:
        if total:
            self.estado_vazio.place_forget()
            return
        self.estado_vazio.place(relx=0.5, rely=0.46, anchor=tk.CENTER)
        self.estado_vazio.lift()

    def _ao_selecionar(self, _evento: tk.Event) -> None:
        selecao = self.tabela.selection()
        if not selecao:
            self._mostrar_sem_selecao()
            return
        membro = self._membros_por_item.get(selecao[0])
        if membro is not None:
            self._mostrar_detalhes(membro)

    def _novo_membro(self) -> None:
        if self._formulario is not None and self._formulario.winfo_exists():
            self._formulario.lift()
            return
        self._formulario = FormularioMembro(
            self,
            self.sistema,
            ao_salvar=self._apos_cadastrar,
        )

    def _apos_cadastrar(self, membro: Membro) -> None:
        self._id_selecionado = membro.id_membro
        self.atualizar()
        if self.ao_notificar is not None:
            self.ao_notificar("Membro cadastrado.", "sucesso")

    def _limpar_detalhes(self) -> None:
        for filho in self.detalhes.winfo_children():
            filho.destroy()

    def _mostrar_sem_selecao(self) -> None:
        self._limpar_detalhes()
        tk.Label(
            self.detalhes,
            text="Selecione um membro",
            bg=CORES["superficie"],
            fg=CORES["texto"],
            font=(FONTE, 15, "bold"),
        ).pack(anchor="w", pady=(6, 8))
        tk.Label(
            self.detalhes,
            text="Selecione um cadastro para ver os detalhes.",
            bg=CORES["superficie"],
            fg=CORES["texto_secundario"],
            font=(FONTE, 9),
            wraplength=250,
            justify=tk.LEFT,
        ).pack(anchor="w")

    def _mostrar_detalhes(self, membro: Membro) -> None:
        self._id_selecionado = membro.id_membro
        self._limpar_detalhes()
        tk.Label(
            self.detalhes,
            text=membro.nome,
            bg=CORES["superficie"],
            fg=CORES["texto"],
            font=(FONTE, 16, "bold"),
            wraplength=260,
            justify=tk.LEFT,
        ).pack(anchor="w")
        tk.Label(
            self.detalhes,
            text=f"ID {membro.id_membro}",
            bg=CORES["superficie"],
            fg=CORES["texto_secundario"],
            font=(FONTE, 9),
        ).pack(anchor="w", pady=(4, 18))

        self._campo_detalhe("E-MAIL", membro.email)
        self._campo_detalhe(
            "EMPRÉSTIMOS ATIVOS",
            f"{membro.contar_ativos()} de 3",
        )

        pode_emprestar = membro.pode_emprestar()
        tk.Label(
            self.detalhes,
            text="PODE EMPRESTAR" if pode_emprestar else "LIMITE ATINGIDO",
            bg=CORES["elevada"],
            fg=CORES["menta"] if pode_emprestar else CORES["amarelo"],
            font=(FONTE, 8, "bold"),
            padx=9,
            pady=4,
        ).pack(anchor="w", pady=(2, 0))

    def _campo_detalhe(self, rotulo: str, valor: str) -> None:
        tk.Label(
            self.detalhes,
            text=rotulo,
            bg=CORES["superficie"],
            fg=CORES["texto_sutil"],
            font=(FONTE, 8, "bold"),
        ).pack(anchor="w", pady=(0, 3))
        tk.Label(
            self.detalhes,
            text=valor,
            bg=CORES["superficie"],
            fg=CORES["texto"],
            font=(FONTE, 10),
            wraplength=260,
            justify=tk.LEFT,
        ).pack(anchor="w", pady=(0, 14))
