import tkinter as tk
from collections.abc import Callable
from tkinter import ttk

from gamevault.interface.estilos import CORES, FONTE
from gamevault.modelos.categoria import Categoria
from gamevault.sistema import SistemaGameVault


class JanelaCategorias(tk.Toplevel):
    def __init__(
        self,
        master: tk.Misc,
        sistema: SistemaGameVault,
        ao_alterar: Callable[[], None] | None = None,
    ):
        super().__init__(master)
        self.sistema = sistema
        self.ao_alterar = ao_alterar
        self._categorias_por_item: dict[str, Categoria] = {}
        self.nome_var = tk.StringVar()
        self.feedback_var = tk.StringVar()

        self.title("Categorias")
        self.geometry("520x470")
        self.resizable(False, False)
        self.configure(bg=CORES["fundo"])
        self.transient(master.winfo_toplevel())
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self._criar_cabecalho()
        self._criar_lista()
        self._criar_formulario()
        self._recarregar()
        self.bind("<Escape>", lambda _evento: self.destroy())
        self._centralizar(520, 470)
        self._ativar()

    def _criar_cabecalho(self) -> None:
        cabecalho = ttk.Frame(self, style="App.TFrame")
        cabecalho.grid(row=0, column=0, sticky="ew", padx=24, pady=(22, 16))
        ttk.Label(
            cabecalho,
            text="Categorias",
            style="PageTitle.TLabel",
        ).pack(anchor="w")
        ttk.Label(
            cabecalho,
            text="Cadastre uma categoria ou altere o nome de uma existente.",
            style="PageSubtitle.TLabel",
        ).pack(anchor="w", pady=(3, 0))

    def _criar_lista(self) -> None:
        card = tk.Frame(
            self,
            bg=CORES["superficie"],
            highlightthickness=1,
            highlightbackground=CORES["borda"],
        )
        card.grid(row=1, column=0, sticky="nsew", padx=24)
        card.columnconfigure(0, weight=1)
        card.rowconfigure(0, weight=1)

        self.tabela = ttk.Treeview(
            card,
            columns=("id", "nome"),
            show="headings",
            selectmode="browse",
            height=8,
            style="GameVault.Treeview",
        )
        self.tabela.heading("id", text="ID", anchor=tk.CENTER)
        self.tabela.heading("nome", text="NOME", anchor=tk.W)
        self.tabela.column("id", width=64, minwidth=64, anchor=tk.CENTER)
        self.tabela.column("nome", width=360, minwidth=260, anchor=tk.W)
        self.tabela.grid(row=0, column=0, sticky="nsew")
        self.tabela.bind("<<TreeviewSelect>>", self._ao_selecionar)

        rolagem = ttk.Scrollbar(
            card,
            orient=tk.VERTICAL,
            command=self.tabela.yview,
            style="GameVault.Vertical.TScrollbar",
        )
        rolagem.grid(row=0, column=1, sticky="ns")
        self.tabela.configure(yscrollcommand=rolagem.set)

    def _criar_formulario(self) -> None:
        card = tk.Frame(
            self,
            bg=CORES["superficie"],
            highlightthickness=1,
            highlightbackground=CORES["borda"],
            padx=14,
            pady=13,
        )
        card.grid(row=2, column=0, sticky="ew", padx=24, pady=(14, 22))
        card.columnconfigure(0, weight=1, uniform="acoes")
        card.columnconfigure(1, weight=1, uniform="acoes")

        tk.Label(
            card,
            text="NOME",
            bg=CORES["superficie"],
            fg=CORES["texto_sutil"],
            font=(FONTE, 8, "bold"),
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 5))

        self.campo_nome = ttk.Entry(
            card,
            textvariable=self.nome_var,
            style="Input.TEntry",
        )
        self.campo_nome.grid(row=1, column=0, columnspan=2, sticky="ew")

        self.feedback = tk.Label(
            card,
            textvariable=self.feedback_var,
            bg=CORES["superficie"],
            fg=CORES["erro"],
            font=(FONTE, 9),
            anchor="w",
        )
        self.feedback.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(7, 8))

        ttk.Button(
            card,
            text="Cadastrar",
            style="Primary.TButton",
            command=self._cadastrar,
        ).grid(row=3, column=0, sticky="ew", padx=(0, 5))
        ttk.Button(
            card,
            text="Renomear selecionada",
            style="Secondary.TButton",
            command=self._renomear,
        ).grid(row=3, column=1, sticky="ew", padx=(5, 0))

    def _ativar(self) -> None:
        if not self.winfo_exists():
            return
        self.grab_set()
        self.campo_nome.focus_set()

    def _centralizar(self, largura: int, altura: int) -> None:
        self.update_idletasks()
        pai = self.master.winfo_toplevel()
        x = pai.winfo_rootx() + max(0, (pai.winfo_width() - largura) // 2)
        y = pai.winfo_rooty() + max(0, (pai.winfo_height() - altura) // 2)
        self.geometry(f"{largura}x{altura}+{x}+{y}")

    def _proximo_id(self) -> int:
        categorias = self.sistema.catalogo.listar_categorias()
        return max(
            (categoria.id_categoria for categoria in categorias),
            default=0,
        ) + 1

    def _recarregar(self, id_selecionado: int | None = None) -> None:
        for item in self.tabela.get_children():
            self.tabela.delete(item)
        self._categorias_por_item.clear()

        categorias = sorted(
            self.sistema.catalogo.listar_categorias(),
            key=lambda categoria: categoria.id_categoria,
        )
        for categoria in categorias:
            item = f"categoria-{categoria.id_categoria}"
            self._categorias_por_item[item] = categoria
            self.tabela.insert(
                "",
                tk.END,
                iid=item,
                values=(categoria.id_categoria, categoria.nome),
            )

        if id_selecionado is not None:
            item = f"categoria-{id_selecionado}"
            if item in self.tabela.get_children():
                self.tabela.selection_set(item)
                self.tabela.focus(item)
                self.tabela.see(item)

    def _ao_selecionar(self, _evento: tk.Event) -> None:
        selecao = self.tabela.selection()
        if not selecao:
            return
        categoria = self._categorias_por_item.get(selecao[0])
        if categoria is not None:
            self.nome_var.set(categoria.nome)
            self._feedback("")

    def _cadastrar(self) -> None:
        try:
            categoria = Categoria(self._proximo_id(), self.nome_var.get())
            self.sistema.cadastrar_categoria(categoria)
        except (TypeError, ValueError) as erro:
            self._feedback(str(erro), erro=True)
            return

        self._recarregar(categoria.id_categoria)
        self._feedback("Categoria cadastrada.")
        if self.ao_alterar is not None:
            self.ao_alterar()

    def _renomear(self) -> None:
        selecao = self.tabela.selection()
        if not selecao:
            self._feedback("Selecione uma categoria.", erro=True)
            return
        categoria = self._categorias_por_item[selecao[0]]
        try:
            self.sistema.renomear_categoria(
                categoria.id_categoria,
                self.nome_var.get(),
            )
        except (TypeError, ValueError) as erro:
            self._feedback(str(erro), erro=True)
            return

        self._recarregar(categoria.id_categoria)
        self._feedback("Nome atualizado.")
        if self.ao_alterar is not None:
            self.ao_alterar()

    def _feedback(self, mensagem: str, erro: bool = False) -> None:
        self.feedback_var.set(mensagem)
        self.feedback.configure(
            fg=CORES["erro"] if erro else CORES["menta"],
        )
