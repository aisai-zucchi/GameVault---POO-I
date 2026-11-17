import tkinter as tk
from collections.abc import Callable
from datetime import date, datetime
from tkinter import ttk

from gamevault.interface.estilos import CORES, FONTE
from gamevault.modelos.emprestimo import Emprestimo
from gamevault.modelos.exemplar import Exemplar
from gamevault.modelos.jogo import JogoFisico
from gamevault.modelos.membro import Membro
from gamevault.sistema import SistemaGameVault


SEM_MEMBROS = "Nenhum membro cadastrado"
SEM_EXEMPLARES = "Nenhum exemplar disponível"


def converter_data(texto: str, nome: str) -> date:
    try:
        return datetime.strptime(texto.strip(), "%d/%m/%Y").date()
    except (TypeError, ValueError) as erro:
        raise ValueError(
            f"A data de {nome} deve usar o formato DD/MM/AAAA."
        ) from erro


class TelaEmprestimos(ttk.Frame):
    def __init__(
        self,
        master: tk.Misc,
        sistema: SistemaGameVault,
        ao_notificar: Callable[[str, str], None] | None = None,
    ):
        super().__init__(master, style="App.TFrame", padding=(26, 22, 26, 16))
        self.sistema = sistema
        self.ao_notificar = ao_notificar
        self._membros_por_rotulo: dict[str, Membro] = {}
        self._exemplares_por_rotulo: dict[str, Exemplar] = {}
        self._emprestimos_por_item: dict[str, Emprestimo] = {}
        self._id_selecionado: int | None = None

        hoje = date.today().strftime("%d/%m/%Y")
        self.membro_var = tk.StringVar()
        self.exemplar_var = tk.StringVar()
        self.data_inicio_var = tk.StringVar(value=hoje)
        self.data_devolucao_var = tk.StringVar(value=hoje)
        self.contagem_var = tk.StringVar(value="0 ativos")
        self.selecionado_var = tk.StringVar(value="Selecione um empréstimo")
        self.feedback_var = tk.StringVar()

        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)
        self._criar_cabecalho()
        self._criar_formulario()
        self._criar_tabela()
        self._criar_devolucao()
        self.atualizar()

    def _criar_cabecalho(self) -> None:
        cabecalho = ttk.Frame(self, style="App.TFrame")
        cabecalho.grid(row=0, column=0, sticky="ew", pady=(0, 18))
        cabecalho.columnconfigure(0, weight=1)

        textos = ttk.Frame(cabecalho, style="App.TFrame")
        textos.grid(row=0, column=0, sticky="w")
        ttk.Label(
            textos,
            text="Empréstimos",
            style="PageTitle.TLabel",
        ).pack(anchor="w")
        ttk.Label(
            textos,
            text="Registre empréstimos e devoluções.",
            style="PageSubtitle.TLabel",
        ).pack(anchor="w", pady=(4, 0))

        ttk.Label(
            cabecalho,
            textvariable=self.contagem_var,
            style="Count.TLabel",
        ).grid(row=0, column=1)

    def _criar_formulario(self) -> None:
        card = tk.Frame(
            self,
            bg=CORES["superficie"],
            highlightthickness=1,
            highlightbackground=CORES["borda"],
            padx=14,
            pady=13,
        )
        card.grid(row=1, column=0, sticky="ew", pady=(0, 14))
        card.columnconfigure(0, weight=2)
        card.columnconfigure(1, weight=2)

        self._rotulo(card, 0, 0, "MEMBRO")
        self._rotulo(card, 0, 1, "EXEMPLAR DISPONÍVEL")
        self._rotulo(card, 0, 2, "DATA DE INÍCIO")

        self.membro_combo = ttk.Combobox(
            card,
            textvariable=self.membro_var,
            state="readonly",
            style="Input.TCombobox",
        )
        self.membro_combo.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=(0, 10),
        )

        self.exemplar_combo = ttk.Combobox(
            card,
            textvariable=self.exemplar_var,
            state="readonly",
            style="Input.TCombobox",
        )
        self.exemplar_combo.grid(
            row=1,
            column=1,
            sticky="ew",
            padx=(0, 10),
        )

        self.data_inicio_entry = ttk.Entry(
            card,
            textvariable=self.data_inicio_var,
            style="Input.TEntry",
            width=16,
        )
        self.data_inicio_entry.grid(row=1, column=2, padx=(0, 10))

        ttk.Button(
            card,
            text="Registrar",
            style="Primary.TButton",
            command=self._registrar,
        ).grid(row=1, column=3, sticky="ew")

        self.feedback = tk.Label(
            card,
            textvariable=self.feedback_var,
            bg=CORES["superficie"],
            fg=CORES["texto_secundario"],
            font=(FONTE, 9),
            anchor="w",
        )
        self.feedback.grid(
            row=2,
            column=0,
            columnspan=4,
            sticky="ew",
            pady=(8, 0),
        )

    def _criar_tabela(self) -> None:
        card = tk.Frame(
            self,
            bg=CORES["superficie"],
            highlightthickness=1,
            highlightbackground=CORES["borda"],
        )
        card.grid(row=2, column=0, sticky="nsew")
        card.columnconfigure(0, weight=1)
        card.rowconfigure(0, weight=1)

        colunas = ("id", "membro", "exemplar", "inicio")
        self.tabela = ttk.Treeview(
            card,
            columns=colunas,
            show="headings",
            selectmode="browse",
            style="GameVault.Treeview",
        )
        configuracao = {
            "id": ("ID", 70, tk.CENTER),
            "membro": ("MEMBRO", 260, tk.W),
            "exemplar": ("EXEMPLAR", 230, tk.W),
            "inicio": ("INÍCIO", 120, tk.CENTER),
        }
        for coluna, (titulo, largura, alinhamento) in configuracao.items():
            self.tabela.heading(coluna, text=titulo, anchor=alinhamento)
            self.tabela.column(
                coluna,
                width=largura,
                minwidth=largura,
                anchor=alinhamento,
                stretch=coluna in ("membro", "exemplar"),
            )
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

        self.estado_vazio = tk.Label(
            card,
            text="Nenhum empréstimo ativo.",
            bg=CORES["superficie"],
            fg=CORES["texto_secundario"],
            font=(FONTE, 11),
        )

    def _criar_devolucao(self) -> None:
        card = tk.Frame(
            self,
            bg=CORES["elevada"],
            highlightthickness=1,
            highlightbackground=CORES["borda"],
            padx=14,
            pady=12,
        )
        card.grid(row=3, column=0, sticky="ew", pady=(14, 0))
        card.columnconfigure(0, weight=1)

        tk.Label(
            card,
            textvariable=self.selecionado_var,
            bg=CORES["elevada"],
            fg=CORES["texto"],
            font=(FONTE, 9, "bold"),
            anchor="w",
        ).grid(row=0, column=0, sticky="ew", padx=(0, 12))

        tk.Label(
            card,
            text="DEVOLUÇÃO",
            bg=CORES["elevada"],
            fg=CORES["texto_sutil"],
            font=(FONTE, 8, "bold"),
        ).grid(row=0, column=1, padx=(0, 6))

        ttk.Entry(
            card,
            textvariable=self.data_devolucao_var,
            style="Input.TEntry",
            width=16,
        ).grid(row=0, column=2, padx=(0, 10))

        ttk.Button(
            card,
            text="Registrar devolução",
            style="Secondary.TButton",
            command=self._devolver,
        ).grid(row=0, column=3)

    def _rotulo(
        self,
        master: tk.Misc,
        linha: int,
        coluna: int,
        texto: str,
    ) -> None:
        tk.Label(
            master,
            text=texto,
            bg=CORES["superficie"],
            fg=CORES["texto_sutil"],
            font=(FONTE, 8, "bold"),
        ).grid(
            row=linha,
            column=coluna,
            sticky="w",
            pady=(0, 5),
        )

    def atualizar(self) -> None:
        self._atualizar_membros()
        self._atualizar_exemplares()
        self._atualizar_emprestimos()

    def _atualizar_membros(self) -> None:
        atual = self.membro_var.get()
        membros = sorted(
            self.sistema.cadastro_membros.listar(),
            key=lambda membro: membro.nome.casefold(),
        )
        self._membros_por_rotulo = {
            self._rotulo_membro(membro): membro for membro in membros
        }
        valores = list(self._membros_por_rotulo) or [SEM_MEMBROS]
        self.membro_combo.configure(values=valores)
        self.membro_var.set(atual if atual in valores else valores[0])

    def _atualizar_exemplares(self) -> None:
        atual = self.exemplar_var.get()
        pares: list[tuple[str, Exemplar]] = []
        for jogo in self.sistema.catalogo.listar_jogos():
            if not isinstance(jogo, JogoFisico):
                continue
            for exemplar in jogo.exemplares:
                if exemplar.esta_disponivel():
                    pares.append(
                        (f"{exemplar.codigo} · {jogo.titulo}", exemplar)
                    )
        pares.sort(key=lambda par: par[0].casefold())
        self._exemplares_por_rotulo = dict(pares)
        valores = list(self._exemplares_por_rotulo) or [SEM_EXEMPLARES]
        self.exemplar_combo.configure(values=valores)
        self.exemplar_var.set(atual if atual in valores else valores[0])

    def _atualizar_emprestimos(self) -> None:
        for item in self.tabela.get_children():
            self.tabela.delete(item)
        self._emprestimos_por_item.clear()

        emprestimos = self.sistema.listar_emprestimos_ativos()
        for emprestimo in emprestimos:
            item = f"emprestimo-{emprestimo.id_emprestimo}"
            self._emprestimos_por_item[item] = emprestimo
            self.tabela.insert(
                "",
                tk.END,
                iid=item,
                values=(
                    emprestimo.id_emprestimo,
                    emprestimo.membro.nome,
                    emprestimo.exemplar.codigo,
                    emprestimo.data_inicio.strftime("%d/%m/%Y"),
                ),
            )

        total = len(emprestimos)
        self.contagem_var.set(f"{total} ativo" if total == 1 else f"{total} ativos")
        if total:
            self.estado_vazio.place_forget()
        else:
            self.estado_vazio.place(relx=0.5, rely=0.48, anchor=tk.CENTER)
            self.estado_vazio.lift()

        item = (
            f"emprestimo-{self._id_selecionado}"
            if self._id_selecionado is not None
            else None
        )
        if item in self.tabela.get_children():
            self.tabela.selection_set(item)
            self.tabela.focus(item)
            self._mostrar_selecionado(self._emprestimos_por_item[item])
        else:
            self._id_selecionado = None
            self.selecionado_var.set("Selecione um empréstimo")

    @staticmethod
    def _rotulo_membro(membro: Membro) -> str:
        return f"{membro.id_membro} · {membro.nome}"

    def _registrar(self) -> None:
        membro = self._membros_por_rotulo.get(self.membro_var.get())
        if membro is None:
            self._feedback("Selecione um membro.", "erro")
            return
        exemplar = self._exemplares_por_rotulo.get(self.exemplar_var.get())
        if exemplar is None:
            self._feedback("Selecione um exemplar disponível.", "erro")
            return
        try:
            inicio = converter_data(self.data_inicio_var.get(), "início")
            emprestimo = self.sistema.registrar_emprestimo(
                membro,
                exemplar,
                inicio,
            )
        except (TypeError, ValueError) as erro:
            self._feedback(str(erro), "erro")
            return

        self._id_selecionado = emprestimo.id_emprestimo
        self.atualizar()
        self._feedback("Empréstimo registrado.", "sucesso")

    def _ao_selecionar(self, _evento: tk.Event | None) -> None:
        selecao = self.tabela.selection()
        if not selecao:
            self._id_selecionado = None
            self.selecionado_var.set("Selecione um empréstimo")
            return
        emprestimo = self._emprestimos_por_item.get(selecao[0])
        if emprestimo is not None:
            self._id_selecionado = emprestimo.id_emprestimo
            self._mostrar_selecionado(emprestimo)

    def _mostrar_selecionado(self, emprestimo: Emprestimo) -> None:
        self.selecionado_var.set(
            f"#{emprestimo.id_emprestimo} · {emprestimo.membro.nome} · "
            f"{emprestimo.exemplar.codigo}"
        )

    def _devolver(self) -> None:
        if self._id_selecionado is None:
            self._feedback("Selecione um empréstimo ativo.", "erro")
            return
        try:
            devolucao = converter_data(
                self.data_devolucao_var.get(),
                "devolução",
            )
            devolvido = self.sistema.devolver_emprestimo(
                self._id_selecionado,
                devolucao,
            )
            if not devolvido:
                raise ValueError("O empréstimo não está mais ativo.")
        except (TypeError, ValueError) as erro:
            self._feedback(str(erro), "erro")
            return

        self._id_selecionado = None
        self.atualizar()
        self._feedback("Devolução registrada.", "sucesso")

    def _feedback(self, mensagem: str, tipo: str) -> None:
        cores = {
            "sucesso": CORES["menta"],
            "erro": CORES["erro"],
            "alerta": CORES["amarelo"],
        }
        self.feedback_var.set(mensagem)
        self.feedback.configure(fg=cores.get(tipo, CORES["texto_secundario"]))
        if self.ao_notificar is not None:
            self.ao_notificar(mensagem, tipo)
