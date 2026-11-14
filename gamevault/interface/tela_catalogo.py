import tkinter as tk
from collections.abc import Callable
from tkinter import messagebox, ttk

from gamevault.interface.formulario_exemplar import FormularioExemplar
from gamevault.interface.formulario_jogo import FormularioJogo
from gamevault.interface.janela_categorias import JanelaCategorias
from gamevault.interface.estilos import CORES, FONTE
from gamevault.modelos.jogo import Jogo, JogoDigital, JogoFisico
from gamevault.servicos.catalogo import Catalogo
from gamevault.sistema import SistemaGameVault


TIPOS_FILTRO = {
    "Todos os tipos": None,
    "Físicos": "fisico",
    "Digitais": "digital",
}


def nome_tipo(jogo: Jogo) -> str:
    return "Físico" if isinstance(jogo, JogoFisico) else "Digital"


def nome_categoria(jogo: Jogo) -> str:
    return jogo.categoria.nome if jogo.categoria is not None else "Sem categoria"


def disponibilidade(jogo: Jogo) -> str:
    if isinstance(jogo, JogoDigital):
        return "Acesso digital"
    total = len(jogo.exemplares)
    if total == 0:
        return "Sem exemplares"
    disponiveis = sum(
        1 for exemplar in jogo.exemplares if exemplar.esta_disponivel()
    )
    return f"{disponiveis}/{total} disponíveis"


def filtrar_catalogo(
    catalogo: Catalogo,
    titulo: str = "",
    tipo: str = "Todos os tipos",
    categoria: str = "Todas as categorias",
    plataforma: str = "Todas as plataformas",
) -> list[Jogo]:
    return catalogo.filtrar_jogos(
        titulo=titulo.strip() or None,
        tipo=TIPOS_FILTRO.get(tipo),
        categoria=None if categoria == "Todas as categorias" else categoria,
        plataforma=None if plataforma == "Todas as plataformas" else plataforma,
    )


class TelaCatalogo(ttk.Frame):
    def __init__(
        self,
        master: tk.Misc,
        sistema: SistemaGameVault,
        ao_notificar: Callable[[str, str], None] | None = None,
    ):
        super().__init__(master, style="App.TFrame", padding=(26, 22, 26, 16))
        self.sistema = sistema
        self.catalogo = sistema.catalogo
        self.ao_notificar = ao_notificar
        self._jogos_por_item: dict[str, Jogo] = {}
        self._id_selecionado: int | None = None
        self._formulario_jogo: FormularioJogo | None = None
        self._janela_categorias: JanelaCategorias | None = None
        self._formulario_exemplar: FormularioExemplar | None = None

        self.busca_var = tk.StringVar()
        self.tipo_var = tk.StringVar(value="Todos os tipos")
        self.categoria_var = tk.StringVar(value="Todas as categorias")
        self.plataforma_var = tk.StringVar(value="Todas as plataformas")
        self.contagem_var = tk.StringVar(value="0 jogos")

        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)
        self._criar_cabecalho()
        self._criar_filtros()
        self._criar_conteudo()

        self.busca_var.trace_add("write", self._ao_alterar_busca)
        self.atualizar(silencioso=True)

    def _criar_cabecalho(self) -> None:
        cabecalho = ttk.Frame(self, style="App.TFrame")
        cabecalho.grid(row=0, column=0, sticky="ew", pady=(0, 18))
        cabecalho.columnconfigure(0, weight=1)

        textos = ttk.Frame(cabecalho, style="App.TFrame")
        textos.grid(row=0, column=0, sticky="w")
        ttk.Label(
            textos,
            text="Biblioteca de jogos",
            style="PageTitle.TLabel",
        ).pack(anchor="w")
        ttk.Label(
            textos,
            text="Pesquise por título, tipo, categoria ou plataforma.",
            style="PageSubtitle.TLabel",
        ).pack(anchor="w", pady=(4, 0))

        ttk.Label(
            cabecalho,
            textvariable=self.contagem_var,
            style="Count.TLabel",
        ).grid(row=0, column=1, padx=(12, 10))
        ttk.Button(
            cabecalho,
            text="Categorias",
            style="Secondary.TButton",
            command=self._abrir_categorias,
        ).grid(row=0, column=2, padx=(0, 8))
        ttk.Button(
            cabecalho,
            text="Atualizar",
            style="Secondary.TButton",
            command=self._atualizar_manualmente,
        ).grid(row=0, column=3, padx=(0, 8))
        ttk.Button(
            cabecalho,
            text="Novo jogo",
            style="Primary.TButton",
            command=self._novo_jogo,
        ).grid(row=0, column=4)

    def _criar_filtros(self) -> None:
        filtros = tk.Frame(
            self,
            bg=CORES["superficie"],
            highlightthickness=1,
            highlightbackground=CORES["borda"],
            padx=14,
            pady=13,
        )
        filtros.grid(row=1, column=0, sticky="ew", pady=(0, 14))
        filtros.columnconfigure(0, weight=1)

        busca = ttk.Entry(
            filtros,
            textvariable=self.busca_var,
            style="Input.TEntry",
        )
        busca.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        busca.insert(0, "")

        self.tipo_combo = ttk.Combobox(
            filtros,
            textvariable=self.tipo_var,
            values=list(TIPOS_FILTRO),
            state="readonly",
            width=17,
            style="Input.TCombobox",
        )
        self.tipo_combo.grid(row=0, column=1, padx=(0, 10))

        self.categoria_combo = ttk.Combobox(
            filtros,
            textvariable=self.categoria_var,
            state="readonly",
            width=20,
            style="Input.TCombobox",
        )
        self.categoria_combo.grid(row=0, column=2, padx=(0, 10))

        self.plataforma_combo = ttk.Combobox(
            filtros,
            textvariable=self.plataforma_var,
            state="readonly",
            width=20,
            style="Input.TCombobox",
        )
        self.plataforma_combo.grid(row=0, column=3, padx=(0, 10))

        ttk.Button(
            filtros,
            text="Limpar filtros",
            style="Secondary.TButton",
            command=self.limpar_filtros,
        ).grid(row=0, column=4)

        for combo in (
            self.tipo_combo,
            self.categoria_combo,
            self.plataforma_combo,
        ):
            combo.bind("<<ComboboxSelected>>", self._ao_alterar_filtro)

    def _criar_conteudo(self) -> None:
        painel = ttk.Panedwindow(
            self,
            orient=tk.HORIZONTAL,
            style="GameVault.TPanedwindow",
        )
        painel.grid(row=2, column=0, sticky="nsew")

        tabela_card = tk.Frame(
            painel,
            bg=CORES["superficie"],
            highlightthickness=1,
            highlightbackground=CORES["borda"],
        )
        tabela_card.columnconfigure(0, weight=1)
        tabela_card.rowconfigure(0, weight=1)

        colunas = (
            "id",
            "titulo",
            "ano",
            "tipo",
            "categoria",
            "plataforma",
            "disponibilidade",
        )
        self.tabela = ttk.Treeview(
            tabela_card,
            columns=colunas,
            show="headings",
            selectmode="browse",
            style="GameVault.Treeview",
        )
        configuracao = {
            "id": ("ID", 44, tk.CENTER),
            "titulo": ("TÍTULO", 180, tk.W),
            "ano": ("ANO", 55, tk.CENTER),
            "tipo": ("TIPO", 68, tk.CENTER),
            "categoria": ("CATEGORIA", 100, tk.W),
            "plataforma": ("PLATAFORMA", 100, tk.W),
            "disponibilidade": ("DISPONIBILIDADE", 118, tk.W),
        }
        for coluna, (titulo, largura, alinhamento) in configuracao.items():
            self.tabela.heading(coluna, text=titulo, anchor=alinhamento)
            self.tabela.column(
                coluna,
                width=largura,
                minwidth=largura,
                anchor=alinhamento,
                stretch=coluna == "titulo",
            )

        rolagem_y = ttk.Scrollbar(
            tabela_card,
            orient=tk.VERTICAL,
            command=self.tabela.yview,
            style="GameVault.Vertical.TScrollbar",
        )
        rolagem_x = ttk.Scrollbar(
            tabela_card,
            orient=tk.HORIZONTAL,
            command=self.tabela.xview,
            style="GameVault.Horizontal.TScrollbar",
        )
        self.tabela.configure(
            yscrollcommand=rolagem_y.set,
            xscrollcommand=rolagem_x.set,
        )
        self.tabela.grid(row=0, column=0, sticky="nsew")
        rolagem_y.grid(row=0, column=1, sticky="ns")
        rolagem_x.grid(row=1, column=0, sticky="ew")
        self.tabela.bind("<<TreeviewSelect>>", self._ao_selecionar)
        self.tabela.tag_configure("fisico", foreground=CORES["texto"])
        self.tabela.tag_configure("digital", foreground="#B9E6FF")

        self.estado_vazio = tk.Label(
            tabela_card,
            text="Ainda não há jogos cadastrados.",
            bg=CORES["superficie"],
            fg=CORES["texto_secundario"],
            font=(FONTE, 11),
            justify=tk.CENTER,
        )

        self.detalhes = tk.Frame(
            painel,
            bg=CORES["superficie"],
            width=310,
            highlightthickness=1,
            highlightbackground=CORES["borda"],
            padx=20,
            pady=20,
        )
        self.detalhes.columnconfigure(0, weight=1)
        self.detalhes.rowconfigure(20, weight=1)

        painel.add(tabela_card, weight=1)
        painel.add(self.detalhes, weight=0)
        self._mostrar_estado_sem_selecao()

    def _ao_alterar_busca(self, *_args: object) -> None:
        self.atualizar(silencioso=True)

    def _ao_alterar_filtro(self, _evento: tk.Event) -> None:
        self.atualizar(silencioso=True)

    def _atualizar_manualmente(self) -> None:
        self.atualizar(silencioso=False)

    def limpar_filtros(self) -> None:
        self.busca_var.set("")
        self.tipo_var.set("Todos os tipos")
        self.categoria_var.set("Todas as categorias")
        self.plataforma_var.set("Todas as plataformas")
        self.atualizar(silencioso=True)

    def _novo_jogo(self) -> None:
        if self._janela_esta_aberta(self._formulario_jogo):
            self._formulario_jogo.lift()
            return
        self._formulario_jogo = FormularioJogo(
            self,
            self.sistema,
            ao_salvar=lambda jogo: self._apos_salvar_jogo(
                jogo,
                "Jogo cadastrado.",
            ),
        )

    def _editar_jogo(self) -> None:
        jogo = self._jogo_selecionado()
        if jogo is None:
            self._notificar("Selecione um jogo para editar.", "alerta")
            return
        if self._janela_esta_aberta(self._formulario_jogo):
            self._formulario_jogo.lift()
            return
        self._formulario_jogo = FormularioJogo(
            self,
            self.sistema,
            jogo=jogo,
            ao_salvar=lambda atualizado: self._apos_salvar_jogo(
                atualizado,
                "Jogo atualizado.",
            ),
        )

    def _excluir_jogo(self) -> None:
        jogo = self._jogo_selecionado()
        if jogo is None:
            self._notificar("Selecione um jogo para excluir.", "alerta")
            return
        confirmou = messagebox.askyesno(
            "Excluir jogo",
            f"Excluir '{jogo.titulo}' do catálogo?",
            parent=self.winfo_toplevel(),
        )
        if not confirmou:
            return
        try:
            self.sistema.excluir_jogo(jogo.id_jogo)
        except (TypeError, ValueError) as erro:
            self._notificar(str(erro), "erro")
            return
        self._id_selecionado = None
        self.atualizar(silencioso=True)
        self._notificar("Jogo excluído.", "sucesso")

    def _abrir_categorias(self) -> None:
        if self._janela_esta_aberta(self._janela_categorias):
            self._janela_categorias.lift()
            return
        self._janela_categorias = JanelaCategorias(
            self,
            self.sistema,
            ao_alterar=self._apos_alterar_categorias,
        )

    def _adicionar_exemplar(self) -> None:
        jogo = self._jogo_selecionado()
        if not isinstance(jogo, JogoFisico):
            self._notificar("Selecione um jogo físico.", "alerta")
            return
        if self._janela_esta_aberta(self._formulario_exemplar):
            self._formulario_exemplar.lift()
            return
        self._formulario_exemplar = FormularioExemplar(
            self,
            self.sistema,
            jogo,
            ao_salvar=lambda _exemplar: self._apos_adicionar_exemplar(jogo),
        )

    def _apos_salvar_jogo(self, jogo: Jogo, mensagem: str) -> None:
        self._id_selecionado = jogo.id_jogo
        self.limpar_filtros()
        self._notificar(mensagem, "sucesso")

    def _apos_alterar_categorias(self) -> None:
        self.atualizar(silencioso=True)
        self._notificar("Categorias atualizadas.", "sucesso")

    def _apos_adicionar_exemplar(self, jogo: JogoFisico) -> None:
        self._id_selecionado = jogo.id_jogo
        self.atualizar(silencioso=True)
        self._notificar("Exemplar cadastrado.", "sucesso")

    def _jogo_selecionado(self) -> Jogo | None:
        if self._id_selecionado is None:
            return None
        return self.catalogo.buscar_jogo(self._id_selecionado)

    @staticmethod
    def _janela_esta_aberta(janela: tk.Toplevel | None) -> bool:
        return janela is not None and bool(janela.winfo_exists())

    def _notificar(self, mensagem: str, tipo: str) -> None:
        if self.ao_notificar is not None:
            self.ao_notificar(mensagem, tipo)

    def atualizar(self, silencioso: bool = False) -> None:
        self._atualizar_opcoes_filtro()
        try:
            jogos = filtrar_catalogo(
                self.catalogo,
                titulo=self.busca_var.get(),
                tipo=self.tipo_var.get(),
                categoria=self.categoria_var.get(),
                plataforma=self.plataforma_var.get(),
            )
        except (TypeError, ValueError) as erro:
            if self.ao_notificar is not None:
                self.ao_notificar(str(erro), "erro")
            return

        for item in self.tabela.get_children():
            self.tabela.delete(item)
        self._jogos_por_item.clear()

        for jogo in jogos:
            item = f"jogo-{jogo.id_jogo}"
            self._jogos_por_item[item] = jogo
            self.tabela.insert(
                "",
                tk.END,
                iid=item,
                values=(
                    jogo.id_jogo,
                    jogo.titulo,
                    jogo.ano,
                    nome_tipo(jogo),
                    nome_categoria(jogo),
                    jogo.plataforma or "Não informada",
                    disponibilidade(jogo),
                ),
                tags=("fisico" if isinstance(jogo, JogoFisico) else "digital",),
            )

        total = len(jogos)
        self.contagem_var.set(f"{total} jogo" if total == 1 else f"{total} jogos")
        self._atualizar_estado_vazio(total)

        item_anterior = (
            f"jogo-{self._id_selecionado}"
            if self._id_selecionado is not None
            else None
        )
        itens = self.tabela.get_children()
        item_para_selecionar = item_anterior if item_anterior in itens else None
        if item_para_selecionar is None and itens:
            item_para_selecionar = itens[0]
        if item_para_selecionar is not None:
            self.tabela.selection_set(item_para_selecionar)
            self.tabela.focus(item_para_selecionar)
            self._mostrar_detalhes(self._jogos_por_item[item_para_selecionar])
        else:
            self._id_selecionado = None
            self._mostrar_estado_sem_selecao()

        if not silencioso and self.ao_notificar is not None:
            self.ao_notificar("Catálogo atualizado.", "sucesso")

    def _atualizar_opcoes_filtro(self) -> None:
        categorias = sorted(
            {categoria.nome for categoria in self.catalogo.listar_categorias()},
            key=str.casefold,
        )
        plataformas = sorted(
            {
                jogo.plataforma
                for jogo in self.catalogo.listar_jogos()
                if jogo.plataforma
            },
            key=str.casefold,
        )
        valores_categoria = ["Todas as categorias", *categorias]
        valores_plataforma = ["Todas as plataformas", *plataformas]
        self.categoria_combo.configure(values=valores_categoria)
        self.plataforma_combo.configure(values=valores_plataforma)
        if self.categoria_var.get() not in valores_categoria:
            self.categoria_var.set("Todas as categorias")
        if self.plataforma_var.get() not in valores_plataforma:
            self.plataforma_var.set("Todas as plataformas")

    def _atualizar_estado_vazio(self, total: int) -> None:
        if total:
            self.estado_vazio.place_forget()
            return
        if self.catalogo.listar_jogos():
            texto = "Nenhum jogo corresponde aos filtros atuais."
        else:
            texto = "Ainda não há jogos cadastrados."
        self.estado_vazio.configure(text=texto)
        self.estado_vazio.place(relx=0.5, rely=0.46, anchor=tk.CENTER)
        self.estado_vazio.lift()

    def _ao_selecionar(self, _evento: tk.Event) -> None:
        selecao = self.tabela.selection()
        if not selecao:
            self._mostrar_estado_sem_selecao()
            return
        jogo = self._jogos_por_item.get(selecao[0])
        if jogo is not None:
            self._mostrar_detalhes(jogo)

    def _limpar_detalhes(self) -> None:
        for filho in self.detalhes.winfo_children():
            filho.destroy()

    def _mostrar_estado_sem_selecao(self) -> None:
        self._limpar_detalhes()
        self.titulo_detalhe = tk.Label(
            self.detalhes,
            text="Selecione um jogo",
            bg=CORES["superficie"],
            fg=CORES["texto"],
            font=(FONTE, 15, "bold"),
        )
        self.titulo_detalhe.pack(anchor="w", pady=(6, 8))
        tk.Label(
            self.detalhes,
            text="Selecione um jogo para ver os detalhes.",
            bg=CORES["superficie"],
            fg=CORES["texto_secundario"],
            font=(FONTE, 9),
            justify=tk.LEFT,
            wraplength=260,
        ).pack(anchor="w")

    def _mostrar_detalhes(self, jogo: Jogo) -> None:
        self._id_selecionado = jogo.id_jogo
        self._limpar_detalhes()

        self.titulo_detalhe = tk.Label(
            self.detalhes,
            text=jogo.titulo,
            bg=CORES["superficie"],
            fg=CORES["texto"],
            font=(FONTE, 16, "bold"),
            justify=tk.LEFT,
            wraplength=270,
        )
        self.titulo_detalhe.pack(anchor="w")
        tk.Label(
            self.detalhes,
            text=f"ID {jogo.id_jogo}  •  {jogo.ano}",
            bg=CORES["superficie"],
            fg=CORES["texto_secundario"],
            font=(FONTE, 9),
        ).pack(anchor="w", pady=(4, 12))

        badges = tk.Frame(self.detalhes, bg=CORES["superficie"])
        badges.pack(fill=tk.X, pady=(0, 18))
        self._adicionar_badge(
            badges,
            nome_tipo(jogo),
            CORES["azul"] if isinstance(jogo, JogoDigital) else CORES["menta"],
        )
        if isinstance(jogo, JogoFisico):
            disponivel = any(
                exemplar.esta_disponivel() for exemplar in jogo.exemplares
            )
            self._adicionar_badge(
                badges,
                "Disponível" if disponivel else "Indisponível",
                CORES["menta"] if disponivel else CORES["amarelo"],
            )
        else:
            self._adicionar_badge(badges, "Acesso digital", CORES["texto_secundario"])

        acoes = tk.Frame(self.detalhes, bg=CORES["superficie"])
        acoes.pack(fill=tk.X, pady=(0, 18))
        acoes.columnconfigure(0, weight=1)
        acoes.columnconfigure(1, weight=1)
        ttk.Button(
            acoes,
            text="Editar",
            style="DetailAction.TButton",
            command=self._editar_jogo,
        ).grid(row=0, column=0, sticky="ew", padx=(0, 5))
        coluna_excluir = 1
        if isinstance(jogo, JogoFisico):
            acoes.columnconfigure(2, weight=1)
            ttk.Button(
                acoes,
                text="+ Exemplar",
                style="DetailAction.TButton",
                command=self._adicionar_exemplar,
            ).grid(row=0, column=1, sticky="ew", padx=(0, 5))
            coluna_excluir = 2
        ttk.Button(
            acoes,
            text="Excluir",
            style="DetailDanger.TButton",
            command=self._excluir_jogo,
        ).grid(row=0, column=coluna_excluir, sticky="ew")

        dados = tk.Frame(self.detalhes, bg=CORES["superficie"])
        dados.pack(fill=tk.X)
        self._campo_detalhe(dados, "CATEGORIA", nome_categoria(jogo))
        self._campo_detalhe(
            dados,
            "PLATAFORMA",
            jogo.plataforma or "Não informada",
        )
        self._campo_detalhe(dados, "DISPONIBILIDADE", disponibilidade(jogo))

        if isinstance(jogo, JogoDigital):
            self._campo_detalhe(dados, "LOJA DE ORIGEM", jogo.loja_origem)
        else:
            self._criar_lista_exemplares(jogo)

    def _adicionar_badge(self, master: tk.Misc, texto: str, cor: str) -> None:
        tk.Label(
            master,
            text=texto.upper(),
            bg=CORES["elevada"],
            fg=cor,
            font=(FONTE, 8, "bold"),
            padx=9,
            pady=4,
        ).pack(side=tk.LEFT, padx=(0, 7))

    def _campo_detalhe(self, master: tk.Misc, rotulo: str, valor: str) -> None:
        tk.Label(
            master,
            text=rotulo,
            bg=CORES["superficie"],
            fg=CORES["texto_sutil"],
            font=(FONTE, 8, "bold"),
        ).pack(anchor="w", pady=(0, 3))
        tk.Label(
            master,
            text=valor,
            bg=CORES["superficie"],
            fg=CORES["texto"],
            font=(FONTE, 10),
            wraplength=270,
            justify=tk.LEFT,
        ).pack(anchor="w", pady=(0, 13))

    def _criar_lista_exemplares(self, jogo: JogoFisico) -> None:
        tk.Label(
            self.detalhes,
            text="EXEMPLARES",
            bg=CORES["superficie"],
            fg=CORES["texto_sutil"],
            font=(FONTE, 8, "bold"),
        ).pack(anchor="w", pady=(4, 7))
        if not jogo.exemplares:
            tk.Label(
                self.detalhes,
                text="Nenhum exemplar cadastrado.",
                bg=CORES["superficie"],
                fg=CORES["texto_secundario"],
                font=(FONTE, 9),
            ).pack(anchor="w")
        else:
            lista = ttk.Treeview(
                self.detalhes,
                columns=("codigo", "status"),
                show="headings",
                height=min(5, max(2, len(jogo.exemplares))),
                style="GameVault.Treeview",
            )
            lista.heading("codigo", text="CÓDIGO", anchor=tk.W)
            lista.heading("status", text="STATUS", anchor=tk.W)
            lista.column("codigo", width=120, minwidth=90, anchor=tk.W)
            lista.column("status", width=105, minwidth=90, anchor=tk.W)
            for exemplar in jogo.exemplares:
                lista.insert(
                    "",
                    tk.END,
                    values=(
                        exemplar.codigo,
                        "Disponível"
                        if exemplar.esta_disponivel()
                        else "Emprestado",
                    ),
                )
            lista.pack(fill=tk.X)
