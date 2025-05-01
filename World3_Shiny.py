from shiny import App, ui, render, reactive
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib as mpl
from pyworld3 import World3

# Appliquer thème de graphique
sns.set_theme(style='white', font='Fira Sans', palette='Set2')
mpl.rcParams['font.family'] = 'Fira Sans'

# UI
app_ui = ui.page_fluid(
    ui.tags.style("""
        @import url('https://fonts.googleapis.com/css2?family=Fira+Sans&display=swap');
        :root { --cired: rgb(5,100,109); }
        body { font-family: 'Fira Sans', sans-serif; }
        .btn { background-color: var(--cired) !important; color: #fff; }
        .navbar-nav .nav-link.active { background-color: var(--cired) !important; color: #fff; }
    """),
    ui.h1("Explorateur de scénario World3"),
    ui.navset_tab(
        ui.nav_panel(
            "Construction de scénario",
            ui.h3("Ici, vous pouvez configurer votre scénario…")
        ),
        ui.nav_panel(
            "Analyse du scénario",
            ui.layout_sidebar(
                ui.sidebar(
                    ui.input_slider(
                        "nri",
                        "Dotation en ressources non renouvelables (NRI) :",
                        min=1e11, max=1e13, value=2e12, step=1e11
                    ),
                    ui.input_slider(
                        "icor2",
                        "Technologie d'extraction des ressources (icor2) :",
                        min=0.1, max=5.0, value=1.0, step=0.1
                    ),
                    ui.input_action_button("reset", "Réinitialiser les valeurs par défaut")
                ),
                ui.h4("État du monde"),
                ui.output_plot("plot_state"),
                ui.h4("Niveau de vie matériel"),
                ui.output_plot("plot_material"),
                ui.h4("Bien-être humain et empreinte"),
                ui.output_plot("plot_welfare")
            )
        )
    )
)

# Server
def server(input, output, session):
    DEFAULTS = {"nri": 2e12, "icor2": 1.0}

    @reactive.effect
    @reactive.event(input.reset)
    def _reset():
        for name, val in DEFAULTS.items():
            ui.update_slider(name, value=val)

    def run_world3(nri, icor2):
        w = World3(pyear=2002)
        w.init_world3_constants(nri=nri, icor2=icor2)
        w.init_world3_variables()
        w.set_world3_table_functions()
        w.set_world3_delay_functions()
        w.run_world3(fast=True)
        return w

    @render.plot
    def plot_state():
        w = run_world3(input.nri(), input.icor2())
        vars_ = [
            ("Population", w.pop),
            ("Production alimentaire", w.fpc),
            ("Production industrielle", w.iopc),
            ("Pollution", w.ppolx),
            ("Ressources non renouvelables", w.nrfr),
        ]
        colors = sns.color_palette("Set2", len(vars_))
        fig, host = plt.subplots(figsize=(7, 4))
        axes = [host] + [host.twinx() for _ in vars_[1:]]
        for i, ax in enumerate(axes[2:], start=2):
            ax.spines["right"].set_position(("axes", 1 + 0.1*(i-1)))
        for ax, (label, data), color in zip(axes, vars_, colors):
            ax.plot(w.time, data, color=color, label=label)
            ax.set_ylabel(label, color=color)
            ax.tick_params(axis='y', colors=color)
            ax.grid(False)
        host.set_xlabel("Année")
        host.grid(True)
        fig.tight_layout()
        return fig

    @render.plot
    def plot_material():
        w = run_world3(input.nri(), input.icor2())
        vars_ = [
            ("Alimentation / personne", w.fpc / w.pop),
            ("Services / personne", w.iopc / w.pop),
            ("Espérance de vie", w.ly),
            ("Biens / personne", w.io / w.pop),
        ]
        colors = sns.color_palette("Set2", len(vars_))
        fig, host = plt.subplots(figsize=(7, 4))
        axes = [host] + [host.twinx() for _ in vars_[1:]]
        for i, ax in enumerate(axes[2:], start=2):
            ax.spines["right"].set_position(("axes", 1 + 0.1*(i-1)))
        for ax, (label, data), color in zip(axes, vars_, colors):
            ax.plot(w.time, data, color=color, label=label)
            ax.set_ylabel(label, color=color)
            ax.tick_params(axis='y', colors=color)
            ax.grid(False)
        host.set_xlabel("Année")
        host.grid(True)
        fig.tight_layout()
        return fig

    @render.plot
    def plot_welfare():
        w = run_world3(input.nri(), input.icor2())
        vars_ = [
            ("Empreinte écologique", w.ppolx),
            ("Indice de bien-être", w.fioac),
        ]
        colors = sns.color_palette("Set2", len(vars_))
        fig, host = plt.subplots(figsize=(7, 4))
        axes = [host] + [host.twinx() for _ in vars_[1:]]
        for ax, (label, data), color in zip(axes, vars_, colors):
            ax.plot(w.time, data, color=color, label=label)
            ax.set_ylabel(label, color=color)
            ax.tick_params(axis='y', colors=color)
            ax.grid(False)
        host.set_xlabel("Année")
        host.grid(True)
        fig.tight_layout()
        return fig

app = App(app_ui, server)
app.run()