import tkinter as tk
from pathlib import Path
from tkinter import ttk

from gamevault.interface.estilos import CORES, FONTE, configurar_estilos
from gamevault.interface.tela_catalogo import TelaCatalogo
from gamevault.sistema import SistemaGameVault


class GameVaultApp(tk.Tk):
    def __init__(
        self,
        sistema: SistemaGameVault | None = None,
        modo_demonstracao: bool = False,
    ):
        super().__init__()
        self.sistema = sistema if sistema is not None else SistemaGameVault()
        self.modo_demonstracao = modo_demonstracao
        self._temporizador_status: str | None = None
        self._logo_original: tk.PhotoImage | None = None
        self._logo: tk.PhotoImage | None = None

        self.title("GameVault | Catálogo de Jogos")
        self.geometry("1240x720")
        self.minsize(1024, 640)
        self.configure(bg=CORES["fundo"])
        configurar_estilos(self)

        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self._criar_sidebar()
        self._criar_area_principal()

    def _criar_sidebar(self) -> None:
        sidebar = tk.Frame(self, bg=CORES["sidebar"], width=216)
        sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew")
        sidebar.grid_propagate(False)
        sidebar.columnconfigure(0, weight=1)
        sidebar.rowconfigure(3, weight=1)

        marca = tk.Frame(sidebar, bg=CORES["sidebar"])
        marca.grid(row=0, column=0, sticky="ew", padx=18, pady=(22, 28))
        self._carregar_logo(marca)

        ttk.Label(
            sidebar,
            text="NAVEGAÇÃO",
            style="Eyebrow.TLabel",
        ).grid(row=1, column=0, sticky="w", padx=20, pady=(0, 8))
        ttk.Button(
            sidebar,
            text="  Catálogo",
            style="SidebarActive.TButton",
            command=self._abrir_catalogo,
        ).grid(row=2, column=0, sticky="ew", padx=12)

        if self.modo_demonstracao:
            tk.Label(
                sidebar,
                text="DADOS DE EXEMPLO",
                bg=CORES["elevada"],
                fg=CORES["amarelo"],
                font=(FONTE, 8, "bold"),
                padx=9,
                pady=5,
            ).grid(row=4, column=0, sticky="sw", padx=20, pady=20)

    def _carregar_logo(self, master: tk.Misc) -> None:
        caminho = Path(__file__).parent / "assets" / "logo.png"
        try:
            self._logo_original = tk.PhotoImage(file=str(caminho))
            fator = max(1, self._logo_original.width() // 52)
            self._logo = self._logo_original.subsample(fator, fator)
            tk.Label(
                master,
                image=self._logo,
                bg=CORES["sidebar"],
            ).pack(side=tk.LEFT, padx=(0, 10))
            self.iconphoto(True, self._logo_original)
        except tk.TclError:
            tk.Label(
                master,
                text="GV",
                bg=CORES["menta"],
                fg=CORES["fundo"],
                font=(FONTE, 11, "bold"),
                padx=8,
                pady=7,
            ).pack(side=tk.LEFT, padx=(0, 10))

        textos = tk.Frame(master, bg=CORES["sidebar"])
        textos.pack(side=tk.LEFT, fill=tk.Y)
        ttk.Label(textos, text="GameVault", style="Brand.TLabel").pack(anchor="w")
        ttk.Label(
            textos,
            text="BIBLIOTECA",
            style="Eyebrow.TLabel",
        ).pack(anchor="w", pady=(2, 0))

    def _criar_area_principal(self) -> None:
        area = ttk.Frame(self, style="App.TFrame")
        area.grid(row=0, column=1, sticky="nsew")
        area.columnconfigure(0, weight=1)
        area.rowconfigure(0, weight=1)

        self.tela_catalogo = TelaCatalogo(
            area,
            self.sistema,
            ao_notificar=self.notificar,
        )
        self.tela_catalogo.grid(row=0, column=0, sticky="nsew")

        status = tk.Frame(
            self,
            bg=CORES["superficie"],
            height=34,
            highlightthickness=1,
            highlightbackground=CORES["borda"],
        )
        status.grid(row=1, column=1, sticky="ew")
        status.grid_propagate(False)
        self.status_var = tk.StringVar(value="Pronto.")
        self.status_label = tk.Label(
            status,
            textvariable=self.status_var,
            bg=CORES["superficie"],
            fg=CORES["texto_secundario"],
            font=(FONTE, 9),
        )
        self.status_label.pack(side=tk.LEFT, padx=26)

    def _abrir_catalogo(self) -> None:
        self.tela_catalogo.atualizar(silencioso=True)

    def notificar(self, mensagem: str, tipo: str = "info") -> None:
        cores = {
            "sucesso": CORES["menta"],
            "erro": CORES["erro"],
            "alerta": CORES["amarelo"],
            "info": CORES["texto_secundario"],
        }
        self.status_var.set(mensagem)
        self.status_label.configure(fg=cores.get(tipo, CORES["texto_secundario"]))
        if self._temporizador_status is not None:
            self.after_cancel(self._temporizador_status)
        self._temporizador_status = self.after(4200, self._restaurar_status)

    def _restaurar_status(self) -> None:
        self._temporizador_status = None
        self.status_var.set("Pronto.")
        self.status_label.configure(fg=CORES["texto_secundario"])


def executar(
    sistema: SistemaGameVault | None = None,
    modo_demonstracao: bool = False,
) -> None:
    app = GameVaultApp(sistema, modo_demonstracao)
    app.mainloop()
