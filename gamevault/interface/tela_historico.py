import tkinter as tk
from collections.abc import Callable
from tkinter import ttk

from gamevault.interface.estilos import CORES, FONTE
from gamevault.modelos.emprestimo import Emprestimo
from gamevault.sistema import SistemaGameVault


STATUS_FILTRO = ("Todos", "Ativos", "Finalizados")


def filtrar_historico(
    emprestimos: list[Emprestimo],
    busca: str = "",
    status: str = "Todos",
) -> list[Emprestimo]:
    termo = busca.strip().casefold()
    resultado = list(emprestimos)

    if status == "Ativos":
        resultado = [item for item in resultado if item.esta_ativo()]
    elif status == "Finalizados":
        resultado = [item for item in resultado if not item.esta_ativo()]

    if termo:
        resultado = [
            item
            for item in resultado
            if termo in item.membro.nome.casefold()
            or termo in item.membro.email.casefold()
            or termo in item.exemplar.codigo.casefold()
        ]
    return resultado


class TelaHistorico(ttk.Frame):
    def __init__(
        self,
        master: tk.Misc,
        sistema: SistemaGameVault,
        ao_notificar: Callable[[str, str], None] | None = None,
    ):
        super().__init__(master, style="App.TFrame", padding=(26, 22, 26, 16))
        self.sistema = sistema
        self.ao_notificar = ao_notificar
        self.busca_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Todos")
        self.contagem_var = tk.StringVar(value="0 registros")

        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)
        self._criar_cabecalho()
        self._criar_filtros()
        self._criar_tabela()

        self.busca_var.trace_add("write", self._ao_alterar_busca)
        self.atualizar()

    def _criar_cabecalho(self) -> None:
        cabecalho = ttk.Frame(self, style="App.TFrame")
        cabecalho.grid(row=0, column=0, sticky="ew", pady=(0, 18))
        cabecalho.columnconfigure(0, weight=1)

        textos = ttk.Frame(cabecalho, style="App.TFrame")
        textos.grid(row=0, column=0, sticky="w")
        ttk.Label(
            textos,
            text="Histórico de empréstimos",
            style="PageTitle.TLabel",
        ).pack(anchor="w")
        ttk.Label(
            textos,
            text="Consulte empréstimos ativos e finalizados.",
            style="PageSubtitle.TLabel",
        ).pack(anchor="w", pady=(4, 0))

        ttk.Label(
            cabecalho,
            textvariable=self.contagem_var,
            style="Count.TLabel",
        ).grid(row=0, column=1, padx=(12, 10))
        ttk.Button(
            cabecalho,
            text="Atualizar",
            style="Secondary.TButton",
            command=self._atualizar_manualmente,
        ).grid(row=0, column=2)

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

        self.busca_entry = ttk.Entry(
            filtros,
            textvariable=self.busca_var,
            style="Input.TEntry",
        )
        self.busca_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        self.status_combo = ttk.Combobox(
            filtros,
            textvariable=self.status_var,
            values=STATUS_FILTRO,
            state="readonly",
            width=18,
            style="Input.TCombobox",
        )
        self.status_combo.grid(row=0, column=1, padx=(0, 10))
        self.status_combo.bind("<<ComboboxSelected>>", self._ao_alterar_status)

        ttk.Button(
            filtros,
            text="Limpar filtros",
            style="Secondary.TButton",
            command=self.limpar_filtros,
        ).grid(row=0, column=2)

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

        colunas = (
            "id",
            "membro",
            "exemplar",
            "inicio",
            "devolucao",
            "status",
        )
        self.tabela = ttk.Treeview(
            card,
            columns=colunas,
            show="headings",
            selectmode="browse",
            style="GameVault.Treeview",
        )
        configuracao = {
            "id": ("ID", 60, tk.CENTER),
            "membro": ("MEMBRO", 230, tk.W),
            "exemplar": ("EXEMPLAR", 135, tk.W),
            "inicio": ("INÍCIO", 120, tk.CENTER),
            "devolucao": ("DEVOLUÇÃO", 120, tk.CENTER),
            "status": ("STATUS", 115, tk.CENTER),
        }
        for coluna, (titulo, largura, alinhamento) in configuracao.items():
            self.tabela.heading(coluna, text=titulo, anchor=alinhamento)
            self.tabela.column(
                coluna,
                width=largura,
                minwidth=largura,
                anchor=alinhamento,
                stretch=coluna == "membro",
            )

        rolagem = ttk.Scrollbar(
            card,
            orient=tk.VERTICAL,
            command=self.tabela.yview,
            style="GameVault.Vertical.TScrollbar",
        )
        self.tabela.configure(yscrollcommand=rolagem.set)
        self.tabela.grid(row=0, column=0, sticky="nsew")
        rolagem.grid(row=0, column=1, sticky="ns")
        self.tabela.tag_configure("ativo", foreground=CORES["menta"])
        self.tabela.tag_configure(
            "finalizado",
            foreground=CORES["texto_secundario"],
        )

        self.estado_vazio = tk.Label(
            card,
            text="Ainda não há empréstimos registrados.",
            bg=CORES["superficie"],
            fg=CORES["texto_secundario"],
            font=(FONTE, 11),
        )

    def atualizar(self) -> None:
        emprestimos = filtrar_historico(
            self.sistema.gestor_emprestimos.emprestimos,
            self.busca_var.get(),
            self.status_var.get(),
        )

        for item in self.tabela.get_children():
            self.tabela.delete(item)

        for emprestimo in emprestimos:
            ativo = emprestimo.esta_ativo()
            self.tabela.insert(
                "",
                tk.END,
                iid=f"emprestimo-{emprestimo.id_emprestimo}",
                values=(
                    emprestimo.id_emprestimo,
                    emprestimo.membro.nome,
                    emprestimo.exemplar.codigo,
                    emprestimo.data_inicio.strftime("%d/%m/%Y"),
                    "—"
                    if emprestimo.data_devolucao is None
                    else emprestimo.data_devolucao.strftime("%d/%m/%Y"),
                    "Ativo" if ativo else "Finalizado",
                ),
                tags=("ativo" if ativo else "finalizado",),
            )

        total = len(emprestimos)
        self.contagem_var.set(
            f"{total} registro" if total == 1 else f"{total} registros"
        )
        self._atualizar_estado_vazio(total)

    def limpar_filtros(self) -> None:
        self.busca_var.set("")
        self.status_var.set("Todos")
        self.atualizar()

    def _atualizar_estado_vazio(self, total: int) -> None:
        if total:
            self.estado_vazio.place_forget()
            return
        if self.sistema.gestor_emprestimos.emprestimos:
            texto = "Nenhum empréstimo corresponde aos filtros."
        else:
            texto = "Ainda não há empréstimos registrados."
        self.estado_vazio.configure(text=texto)
        self.estado_vazio.place(relx=0.5, rely=0.46, anchor=tk.CENTER)
        self.estado_vazio.lift()

    def _ao_alterar_busca(self, *_args: object) -> None:
        self.atualizar()

    def _ao_alterar_status(self, _evento: tk.Event) -> None:
        self.atualizar()

    def _atualizar_manualmente(self) -> None:
        self.atualizar()
        if self.ao_notificar is not None:
            self.ao_notificar("Histórico atualizado.", "sucesso")
