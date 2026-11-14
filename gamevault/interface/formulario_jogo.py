import tkinter as tk
from collections.abc import Callable
from tkinter import ttk

from gamevault.interface.estilos import CORES, FONTE
from gamevault.modelos.categoria import Categoria
from gamevault.modelos.jogo import Jogo, JogoDigital, JogoFisico
from gamevault.sistema import SistemaGameVault


SEM_CATEGORIA = "Sem categoria"


class FormularioJogo(tk.Toplevel):
    def __init__(
        self,
        master: tk.Misc,
        sistema: SistemaGameVault,
        jogo: Jogo | None = None,
        ao_salvar: Callable[[Jogo], None] | None = None,
    ):
        super().__init__(master)
        self.sistema = sistema
        self.jogo = jogo
        self.ao_salvar = ao_salvar
        self._categorias_por_rotulo: dict[str, Categoria] = {}

        self.titulo_var = tk.StringVar(value=jogo.titulo if jogo else "")
        self.ano_var = tk.StringVar(value=str(jogo.ano) if jogo else "")
        self.tipo_var = tk.StringVar(value=self._tipo_inicial())
        self.plataforma_var = tk.StringVar(
            value=(jogo.plataforma or "") if jogo else ""
        )
        self.categoria_var = tk.StringVar()
        self.loja_var = tk.StringVar(
            value=jogo.loja_origem if isinstance(jogo, JogoDigital) else ""
        )
        self.erro_var = tk.StringVar()

        self.title("Editar jogo" if jogo else "Novo jogo")
        self.geometry("480x590")
        self.resizable(False, False)
        self.configure(bg=CORES["fundo"])
        self.transient(master.winfo_toplevel())

        self._criar_conteudo()
        self._carregar_categorias()
        self._atualizar_tipo()
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.bind("<Escape>", lambda _evento: self.destroy())
        self._centralizar(480, 590)
        self._ativar()

    def _tipo_inicial(self) -> str:
        if isinstance(self.jogo, JogoDigital):
            return "Digital"
        return "Físico"

    def _ativar(self) -> None:
        if not self.winfo_exists():
            return
        self.grab_set()
        self.campo_titulo.focus_set()

    def _centralizar(self, largura: int, altura: int) -> None:
        self.update_idletasks()
        pai = self.master.winfo_toplevel()
        x = pai.winfo_rootx() + max(0, (pai.winfo_width() - largura) // 2)
        y = pai.winfo_rooty() + max(0, (pai.winfo_height() - altura) // 2)
        self.geometry(f"{largura}x{altura}+{x}+{y}")

    def _criar_conteudo(self) -> None:
        cabecalho = tk.Frame(self, bg=CORES["fundo"])
        cabecalho.pack(fill=tk.X, padx=28, pady=(24, 18))
        tk.Label(
            cabecalho,
            text="Editar jogo" if self.jogo else "Novo jogo",
            bg=CORES["fundo"],
            fg=CORES["texto"],
            font=(FONTE, 20, "bold"),
        ).pack(anchor="w")
        tk.Label(
            cabecalho,
            text="Atualize os dados do catálogo."
            if self.jogo
            else "Adicione um jogo à biblioteca.",
            bg=CORES["fundo"],
            fg=CORES["texto_secundario"],
            font=(FONTE, 9),
        ).pack(anchor="w", pady=(4, 0))

        formulario = tk.Frame(self, bg=CORES["fundo"])
        formulario.pack(fill=tk.BOTH, expand=True, padx=28)
        formulario.columnconfigure(0, weight=1)

        self.campo_titulo = self._criar_campo(
            formulario,
            0,
            "Título *",
            self.titulo_var,
        )
        self._criar_campo(formulario, 2, "Ano *", self.ano_var)

        self._rotulo(formulario, 4, "Tipo *")
        self.tipo_combo = ttk.Combobox(
            formulario,
            textvariable=self.tipo_var,
            values=("Físico", "Digital"),
            state="disabled" if self.jogo else "readonly",
            style="Input.TCombobox",
        )
        self.tipo_combo.grid(row=5, column=0, sticky="ew", pady=(0, 12))
        self.tipo_combo.bind(
            "<<ComboboxSelected>>",
            lambda _evento: self._atualizar_tipo(),
        )

        self._criar_campo(
            formulario,
            6,
            "Plataforma *",
            self.plataforma_var,
        )

        self._rotulo(formulario, 8, "Categoria")
        self.categoria_combo = ttk.Combobox(
            formulario,
            textvariable=self.categoria_var,
            state="readonly",
            style="Input.TCombobox",
        )
        self.categoria_combo.grid(row=9, column=0, sticky="ew", pady=(0, 12))

        self.loja_label = self._rotulo(formulario, 10, "Loja de origem *")
        self.loja_entry = ttk.Entry(
            formulario,
            textvariable=self.loja_var,
            style="Input.TEntry",
        )
        self.loja_entry.grid(row=11, column=0, sticky="ew", pady=(0, 12))

        tk.Label(
            formulario,
            textvariable=self.erro_var,
            bg=CORES["fundo"],
            fg=CORES["erro"],
            font=(FONTE, 9),
            justify=tk.LEFT,
            wraplength=410,
        ).grid(row=12, column=0, sticky="w", pady=(2, 8))

        acoes = tk.Frame(self, bg=CORES["fundo"])
        acoes.pack(fill=tk.X, padx=28, pady=(8, 24))
        ttk.Button(
            acoes,
            text="Cancelar",
            style="Secondary.TButton",
            command=self.destroy,
        ).pack(side=tk.RIGHT)
        ttk.Button(
            acoes,
            text="Salvar",
            style="Primary.TButton",
            command=self._salvar,
        ).pack(side=tk.RIGHT, padx=(0, 10))

    def _rotulo(self, master: tk.Misc, linha: int, texto: str) -> tk.Label:
        rotulo = tk.Label(
            master,
            text=texto,
            bg=CORES["fundo"],
            fg=CORES["texto_secundario"],
            font=(FONTE, 9, "bold"),
        )
        rotulo.grid(row=linha, column=0, sticky="w", pady=(0, 5))
        return rotulo

    def _criar_campo(
        self,
        master: tk.Misc,
        linha: int,
        rotulo: str,
        variavel: tk.StringVar,
    ) -> ttk.Entry:
        self._rotulo(master, linha, rotulo)
        campo = ttk.Entry(
            master,
            textvariable=variavel,
            style="Input.TEntry",
        )
        campo.grid(row=linha + 1, column=0, sticky="ew", pady=(0, 12))
        return campo

    def _carregar_categorias(self) -> None:
        categorias = sorted(
            self.sistema.catalogo.listar_categorias(),
            key=lambda categoria: categoria.nome.casefold(),
        )
        self._categorias_por_rotulo = {
            self._rotulo_categoria(categoria): categoria
            for categoria in categorias
        }
        permitir_sem_categoria = self.jogo is None or self.jogo.categoria is None
        valores = list(self._categorias_por_rotulo)
        if permitir_sem_categoria:
            valores.insert(0, SEM_CATEGORIA)
        self.categoria_combo.configure(values=valores)

        if self.jogo is not None and self.jogo.categoria is not None:
            self.categoria_var.set(self._rotulo_categoria(self.jogo.categoria))
        elif valores:
            self.categoria_var.set(valores[0])

    @staticmethod
    def _rotulo_categoria(categoria: Categoria) -> str:
        return f"{categoria.id_categoria} · {categoria.nome}"

    def _atualizar_tipo(self) -> None:
        if self.tipo_var.get() == "Digital":
            self.loja_label.grid()
            self.loja_entry.grid()
            return
        self.loja_label.grid_remove()
        self.loja_entry.grid_remove()

    def _categoria_selecionada(self) -> Categoria | None:
        rotulo = self.categoria_var.get()
        if not rotulo or rotulo == SEM_CATEGORIA:
            return None
        categoria = self._categorias_por_rotulo.get(rotulo)
        if categoria is None:
            raise ValueError("Selecione uma categoria válida.")
        return categoria

    def _salvar(self) -> None:
        try:
            titulo = self.titulo_var.get().strip()
            plataforma = self.plataforma_var.get().strip()
            if not plataforma:
                raise ValueError("Informe a plataforma.")
            try:
                ano = int(self.ano_var.get().strip())
            except ValueError as erro:
                raise ValueError("O ano deve ser um número inteiro.") from erro
            categoria = self._categoria_selecionada()
            jogo = self._salvar_jogo(titulo, ano, plataforma, categoria)
        except (TypeError, ValueError) as erro:
            self.erro_var.set(str(erro))
            return

        if self.ao_salvar is not None:
            self.ao_salvar(jogo)
        self.destroy()

    def _salvar_jogo(
        self,
        titulo: str,
        ano: int,
        plataforma: str,
        categoria: Categoria | None,
    ) -> Jogo:
        if self.jogo is None:
            if self.tipo_var.get() == "Digital":
                jogo: Jogo = JogoDigital(
                    titulo,
                    ano,
                    self.loja_var.get(),
                    plataforma=plataforma,
                    categoria=categoria,
                )
            else:
                jogo = JogoFisico(
                    titulo,
                    ano,
                    plataforma=plataforma,
                    categoria=categoria,
                )
            self.sistema.cadastrar_jogo(jogo)
            return jogo

        if self.jogo.id_jogo is None:
            raise ValueError("Jogo não encontrado.")
        dados: dict[str, object] = {
            "titulo": titulo,
            "ano": ano,
            "plataforma": plataforma,
            "id_categoria": (
                categoria.id_categoria if categoria is not None else None
            ),
        }
        if isinstance(self.jogo, JogoDigital):
            dados["loja_origem"] = self.loja_var.get()
        return self.sistema.atualizar_jogo(self.jogo.id_jogo, **dados)
