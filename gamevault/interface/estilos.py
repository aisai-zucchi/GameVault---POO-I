import tkinter as tk
from tkinter import ttk


CORES = {
    "fundo": "#0B1118",
    "sidebar": "#0E1724",
    "superficie": "#121D2A",
    "elevada": "#182638",
    "borda": "#293A50",
    "borda_foco": "#2DD4A3",
    "texto": "#E8EEF7",
    "texto_secundario": "#91A2B8",
    "texto_sutil": "#64748B",
    "menta": "#2DD4A3",
    "menta_hover": "#24B98F",
    "azul": "#38BDF8",
    "amarelo": "#FBBF24",
    "coral": "#FF705D",
    "erro": "#F87171",
    "selecao": "#1D4F61",
}

FONTE = "Segoe UI"


def configurar_estilos(root: tk.Misc) -> ttk.Style:
    estilo = ttk.Style(root)
    if "clam" in estilo.theme_names():
        estilo.theme_use("clam")

    root.option_add("*Font", (FONTE, 10))
    root.option_add("*TCombobox*Listbox.background", CORES["elevada"])
    root.option_add("*TCombobox*Listbox.foreground", CORES["texto"])
    root.option_add("*TCombobox*Listbox.selectBackground", CORES["selecao"])
    root.option_add("*TCombobox*Listbox.selectForeground", CORES["texto"])

    estilo.configure(".", background=CORES["fundo"], foreground=CORES["texto"])
    estilo.configure("App.TFrame", background=CORES["fundo"])
    estilo.configure("Sidebar.TFrame", background=CORES["sidebar"])
    estilo.configure("Surface.TFrame", background=CORES["superficie"])
    estilo.configure("Elevated.TFrame", background=CORES["elevada"])

    estilo.configure(
        "PageTitle.TLabel",
        background=CORES["fundo"],
        foreground=CORES["texto"],
        font=(FONTE, 22, "bold"),
    )
    estilo.configure(
        "PageSubtitle.TLabel",
        background=CORES["fundo"],
        foreground=CORES["texto_secundario"],
        font=(FONTE, 10),
    )
    estilo.configure(
        "Brand.TLabel",
        background=CORES["sidebar"],
        foreground=CORES["texto"],
        font=(FONTE, 17, "bold"),
    )
    estilo.configure(
        "SidebarMuted.TLabel",
        background=CORES["sidebar"],
        foreground=CORES["texto_secundario"],
        font=(FONTE, 9),
    )
    estilo.configure(
        "Eyebrow.TLabel",
        background=CORES["sidebar"],
        foreground=CORES["menta"],
        font=(FONTE, 8, "bold"),
    )
    estilo.configure(
        "Count.TLabel",
        background=CORES["elevada"],
        foreground=CORES["menta"],
        font=(FONTE, 9, "bold"),
        padding=(10, 5),
    )
    estilo.configure(
        "CardTitle.TLabel",
        background=CORES["superficie"],
        foreground=CORES["texto"],
        font=(FONTE, 14, "bold"),
    )
    estilo.configure(
        "CardMuted.TLabel",
        background=CORES["superficie"],
        foreground=CORES["texto_secundario"],
        font=(FONTE, 9),
    )
    estilo.configure(
        "DetailLabel.TLabel",
        background=CORES["superficie"],
        foreground=CORES["texto_sutil"],
        font=(FONTE, 8, "bold"),
    )
    estilo.configure(
        "DetailValue.TLabel",
        background=CORES["superficie"],
        foreground=CORES["texto"],
        font=(FONTE, 10),
    )

    estilo.configure(
        "SidebarActive.TButton",
        background=CORES["selecao"],
        foreground=CORES["texto"],
        borderwidth=0,
        focusthickness=0,
        padding=(14, 11),
        anchor="w",
        font=(FONTE, 10, "bold"),
    )
    estilo.map(
        "SidebarActive.TButton",
        background=[("active", CORES["selecao"])],
        foreground=[("active", CORES["texto"])],
    )
    estilo.configure(
        "Primary.TButton",
        background=CORES["menta"],
        foreground=CORES["fundo"],
        borderwidth=0,
        focusthickness=0,
        padding=(13, 8),
        font=(FONTE, 9, "bold"),
    )
    estilo.map(
        "Primary.TButton",
        background=[("active", CORES["menta_hover"])],
        foreground=[("active", CORES["fundo"])],
    )
    estilo.configure(
        "Secondary.TButton",
        background=CORES["elevada"],
        foreground=CORES["texto"],
        bordercolor=CORES["borda"],
        borderwidth=1,
        focusthickness=0,
        padding=(12, 8),
        font=(FONTE, 9),
    )
    estilo.map(
        "Secondary.TButton",
        background=[("active", CORES["selecao"])],
        bordercolor=[("focus", CORES["borda_foco"])],
    )

    estilo.configure(
        "Input.TEntry",
        fieldbackground=CORES["elevada"],
        foreground=CORES["texto"],
        insertcolor=CORES["texto"],
        bordercolor=CORES["borda"],
        lightcolor=CORES["borda"],
        darkcolor=CORES["borda"],
        padding=8,
    )
    estilo.map(
        "Input.TEntry",
        bordercolor=[("focus", CORES["borda_foco"])],
        lightcolor=[("focus", CORES["borda_foco"])],
        darkcolor=[("focus", CORES["borda_foco"])],
    )
    estilo.configure(
        "Input.TCombobox",
        fieldbackground=CORES["elevada"],
        background=CORES["elevada"],
        foreground=CORES["texto"],
        arrowcolor=CORES["texto_secundario"],
        bordercolor=CORES["borda"],
        lightcolor=CORES["borda"],
        darkcolor=CORES["borda"],
        padding=7,
    )
    estilo.map(
        "Input.TCombobox",
        fieldbackground=[("readonly", CORES["elevada"])],
        foreground=[("readonly", CORES["texto"])],
        selectbackground=[("readonly", CORES["elevada"])],
        selectforeground=[("readonly", CORES["texto"])],
        bordercolor=[("focus", CORES["borda_foco"])],
    )

    estilo.configure(
        "GameVault.Treeview",
        background=CORES["superficie"],
        fieldbackground=CORES["superficie"],
        foreground=CORES["texto"],
        borderwidth=0,
        relief="flat",
        rowheight=34,
        font=(FONTE, 9),
    )
    estilo.map(
        "GameVault.Treeview",
        background=[("selected", CORES["selecao"])],
        foreground=[("selected", CORES["texto"])],
    )
    estilo.configure(
        "GameVault.Treeview.Heading",
        background=CORES["elevada"],
        foreground=CORES["texto_secundario"],
        borderwidth=0,
        relief="flat",
        padding=(8, 9),
        font=(FONTE, 8, "bold"),
    )
    estilo.map(
        "GameVault.Treeview.Heading",
        background=[("active", CORES["selecao"])],
        foreground=[("active", CORES["texto"])],
    )
    estilo.configure(
        "GameVault.Vertical.TScrollbar",
        background=CORES["elevada"],
        troughcolor=CORES["superficie"],
        bordercolor=CORES["superficie"],
        arrowcolor=CORES["texto_secundario"],
    )
    estilo.configure(
        "GameVault.Horizontal.TScrollbar",
        background=CORES["elevada"],
        troughcolor=CORES["superficie"],
        bordercolor=CORES["superficie"],
        arrowcolor=CORES["texto_secundario"],
    )
    estilo.configure(
        "GameVault.TPanedwindow",
        background=CORES["fundo"],
        sashwidth=8,
    )
    return estilo
