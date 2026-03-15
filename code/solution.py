import marimo

__generated_with = "0.20.4"
app = marimo.App()


@app.cell
def _(mo):
    mo.md(r"""
    # Олимпиада «Россети», 2 этап, 8—9 класс
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Импорт библиотек. Подготовка
    """)
    return


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _():
    from typing import Tuple, List, Self
    import numpy as np
    from scipy.spatial.distance import euclidean as euclidean_distance
    from fastcore.basics import store_attr
    from fastcore.meta import delegates
    from matplotlib import pyplot as plt
    from matplotlib.ticker import MultipleLocator
    import plotly
    from plotly import graph_objects as go
    from plotly import express as px
    from dash import Dash, Output, dcc, html, callback, Input

    return (
        Dash,
        Input,
        List,
        MultipleLocator,
        Output,
        Self,
        Tuple,
        callback,
        dcc,
        delegates,
        euclidean_distance,
        go,
        html,
        plt,
        px,
        store_attr,
    )


@app.cell
def _():
    font_dict=dict(family='Arial',
                   size=26,
                   color='black'
                   )
    return (font_dict,)


@app.cell
def _(font_dict, go):
    fig = go.Figure()

    fig.update_xaxes(
        range=(0, 15),
        showgrid=True,
        gridwidth=1,
        minor=dict(
            ticklen=2,
            showgrid=True,
            gridcolor="Gray",
            gridwidth=0.25,
        )
    )

    fig.update_xaxes(
        title_text='X-axis',
        showline=True,
        showticklabels=True,
        linecolor='black',
        linewidth=2.4,
        ticks='outside',
        tickfont=font_dict,
        mirror='allticks',
        tickwidth=2.4,
        tickcolor='black',
    )

    fig.update_yaxes(
        range=(0, 15),
        showgrid=True,
        gridwidth=1,
        minor=dict(
            ticklen=2,
            showgrid=True,
            gridcolor="Gray",
            gridwidth=0.5
        )
    )

    fig.update_yaxes(title_text='Y-axis',  # axis label
                     showline=True,  # add line at x=0
                     linecolor='black',  # line color
                     linewidth=2.4, # line size
                     ticks='outside',  # ticks outside axis
                     tickfont=font_dict, # tick label font
                     mirror='allticks',  # add ticks to top/right axes
                     tickwidth=2.4,  # tick width
                     tickcolor='black',  # tick color
                     )

    fig.update_layout(plot_bgcolor='black',
                      autosize=False,
                      width=750,
                      height=750)
    fig.show()
    return


@app.cell
def _():
    # # 1. Create a figure and axes object
    # fig, ax = plt.subplots()

    # # 2. Turn the grid lines on
    # # By default, this applies to major ticks on both axes
    # ax.grid(True)

    # # Optional: Set axis limits manually to ensure the grid is visible,
    # # as Matplotlib determines limits automatically based on data (which is none here).
    # ax.set_xlim(0, 15)
    # ax.set_ylim(0, 15)

    # # Optional: Add minor grid lines for a denser grid
    # ax.minorticks_on() # Enables minor ticks
    # ax.grid(which='minor', linestyle='-', linewidth=0.1)

    # # 3. Display the plot
    # plt.show()
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Объявление констант из условий
    """)
    return


@app.cell
def _():
    # Постоянные
    OUTAGES_FREQ_PER_KM = 0.05
    LOSS_PER_POWER = 200
    LOSS_PER_WORK = 50
    PRICE_PER_KM = 500000
    return (PRICE_PER_KM,)


@app.cell
def _(mo):
    mo.md(r"""
    | Название переменной   | Название в условии кейса                    |
    | :-------------------: | :-----------------------------------------: |
    | `OUTAGES_FREQ_PER_KM` | $\lambda = 0.05 \ \text{раз/км}$            |
    | `LOSS_PER_POWER`      | $у_{\lambda} = 200 \ \text{руб./кВт}$       |
    | `LOSS_PER_WORK`       | $у_D = 50 \ \text{руб./кВт} \cdot \text{ч}$ |
    | `PRICE_PER_KM`        | Цена за километр линии                      |
    """)
    return


@app.cell
def _():
    # Расположения и мощности
    COORDS = [
        (0.5, 4.5),
        (1, 6),
        (2, 9.5),
        (3, 14),
        (3, 2),
        (3, 6.5),
        (3, 13),
        (3.5, 11.5),
        (4, 4.5),
        (4, 0.5),
        (4, 8),
        (4.5, 14.5),
        (5.5, 11),
        (6, 6),
        (6.5, 10.5),
        (7.5, 13),
        (8, 6.5),
        (8, 15),
        (9, 11.5),
        (10, 1.5),
        (10.5, 6),
        (11.5, 3),
        (11.5, 7),
        (12.5, 0),
        (13, 11),
        (13, 3),
        (13.5, 9.5),
        (14, 6),
        (15, 13),
    ]


    POWERS = [300, 20, 300, 150, 20, 40, 300, 150, 500, 200, 20, 40, 500, 20, 60, 40, 40, 60, 200, 150, 60, 200, 60, 300, 500, 500, 200, 150, 40]
    return COORDS, POWERS


@app.cell
def _(COORDS, POWERS):
    print(len(COORDS), len(POWERS))
    print(list(zip(COORDS, POWERS, strict=True)))
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Представление элементов сети как классов
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### `Node` — потребители (вершины графа)
    """)
    return


@app.cell
def _(List, Tuple, delegates, store_attr):
    class Node:
        def __init__(self, coords: Tuple[int, int], connections: List["Connection"] = []) -> None:
            self.connections = connections
            self._coords = coords

        @property
        def coords(self) -> Tuple[int, int]:
            return self._coords

        @coords.setter
        def coords(self, value: Tuple[int, int]) -> None:
            raise TypeError(f"Попытка изменить координаты нода, который не является ConsumerNode. Истинный класс нода {type(self)}.")

        def add_connection(self, connection: "Connection") -> None:
            self.connections.append(connection)
            connection.get_opposite_node(self).connections.append(connection)


    class ConsumerNode(Node):
        @delegates(Node.__init__)
        def __init__(self, power: int, **kwargs) -> None:
            super().__init__(**kwargs)
            store_attr()


    class SolderingNode(Node):
        @delegates(Node.__init__)
        def __init__(self, **kwargs) -> None:
            super().__init__(**kwargs)


    class SubstationNode(Node):
        def __init__(self, coords: Tuple[int, int] = (0, 0)) -> None:
            if 0 not in coords:
                raise ValueError("Координаты подстанции {coords} не содержат 0.")

            super().__init__(coords)

        @Node.coords.setter
        def coords(self, value: Tuple[int, int]) -> None:
            if 0 not in value:
                raise ValueError("Координаты подстанции {coords} не содержат 0.")
            self._coords = value

    return ConsumerNode, Node, SubstationNode


@app.cell
def _(mo):
    mo.md(r"""
    ### `Equipment` — оборудование на соединениях
    """)
    return


@app.cell
def _():
    class Equipment:
        def __init__(self, price: int) -> None:
            self._price = price

        @property
        def price(self) -> int:
            return self._price


    class ManualSwitch(Equipment):
        def __init__(self) -> None:
            super().__init__(50000)


    class AutoSwitch(Equipment):
        def __init__(self) -> None:
            super().__init__(250000)


    class SubstationSwitch(Equipment):
        def __init__(self) -> None:
            super().__init__(150000)

    return (Equipment,)


@app.cell
def _(mo):
    mo.md(r"""
    ### `Connection` — линия электропередач (ребро)
    """)
    return


@app.cell
def _(
    Equipment,
    Node,
    PRICE_PER_KM,
    delegates,
    euclidean_distance,
    store_attr,
):
    class NoConnectionError(Exception):
        @delegates(Exception.__init__)
        def __init__(self, **kwargs) -> None:
            super().__init__(**kwargs)


    class Connection:
        def __init__(
            self,
            node1: Node,
            node2: Node,
            node1_equip: Equipment | None = None,
            node2_equip: Equipment | None = None,
        ) -> None:
            store_attr()

        @property
        def length(self) -> float:
            return euclidean_distance(self.node1.coords, self.node2.coords)

        @property
        def cost(self) -> float:
            return (self.length * PRICE_PER_KM) + self.node1_equip.price + self.node2_equip.price

        def get_opposite_node(self, caller: Node) -> Node:
            if caller is self.node1:
                return self.node2
            if caller is self.node2:
                return self.node1
            else:
                raise NoConnectionError(f"ПЕРЕХОД НЕВОЗМОЖЕН. Произведена попытка перейти по ребру, соединяющему {self.node1.coords} и {self.node2.coords}, но сaller {caller.coords} не является вершиной этого ребра.")

    return


@app.cell
def _(mo):
    mo.md(r"""
    ### `Network` — сеть
    """)
    return


@app.cell
def _(
    COORDS,
    ConsumerNode,
    Dash,
    Input,
    List,
    MultipleLocator,
    Node,
    Output,
    POWERS,
    Self,
    SubstationNode,
    callback,
    dcc,
    f,
    html,
    plt,
    store_attr,
):
    class Network:
        def __init__(self, nodes: List[Node], substation_node: SubstationNode) -> None:
            store_attr()

        @classmethod
        def init_from_default(cls) -> Self:
            nodes = []
            for c, p in zip(COORDS, POWERS, strict=True):
                n = ConsumerNode(power=p, coords=c)
                nodes.append(n)
            return cls(nodes, SubstationNode())

        # @classmethod
        # def init_from_custom(cls, nodes: List[Node]) -> Self:
        #     return cls(nodes)

        @property
        def cost(self) -> int:
            self._cost = 0
            self._seen_nodes = set()
            self._seen_connections = set()

            cur = self.consumer_node


        def _get_():
            pass

        def visualize(self) -> None:
            fig, ax = plt.subplots(figsize=(10, 10))

            ax.grid(True)
            ax.set(xlim=(0, 15), ylim=(0, 15))
            ax.minorticks_on()
            ax.xaxis.set_major_locator(MultipleLocator(1))
            ax.yaxis.set_major_locator(MultipleLocator(1))
            ax.xaxis.set_minor_locator(MultipleLocator(0.5))
            ax.yaxis.set_minor_locator(MultipleLocator(0.5))
            ax.grid(which='minor', linestyle='-', linewidth=0.25)

            x, y = list(zip(*[node.coords for node in self.nodes]))
            ax.scatter(x, y, s=100, c="r")

            plt.show()
    
        def start_interactive(self) -> None:
            self.app = Dash()

            self.app.layout = [
                html.Header(children="Просто кнопка"),
                dcc.Button(children="Connect", id="connect-val", n_clicks=0),
                html.Div(children="ЖМИ!", id="connect-container")
            ]

            @callback(
                Output(component_id="connect-container", component_property="children"),
                Input(component_id="connect-val", component_property="n_clicks"),
                prevent_initial_call=True
            )
            def connect(n_clicks: int) -> None:
                return f"Сделано 'ЖМИ!' {n_clicks} раз"
        
            f

    return (Network,)


@app.cell
def _(Network):
    Network.init_from_default().visualize()
    return


@app.cell
def _():
    # class MyDashApp:
    #     def __init__(self):
    #         self.app = Dash()

    #         self.app.layout = [
    #             html.Header(children="Просто кнопка"),
    #             dcc.Button(children="Connect", id="connect-val", n_clicks=0),
    #             html.Div(children="ЖМИ!", id="connect-container")
    #         ]

    #         @callback(
    #             Output(component_id="connect-container", component_property="children"),
    #             Input(component_id="connect-val", component_property="n_clicks"),
    #             prevent_initial_call=True
    #         )
    #         def connect(n_clicks: int) -> None:
    #             return f"Сделано 'ЖМИ!' {n_clicks} раз"
        
    #         subpro
    return


@app.cell
def _():
    # from dash import Dash, Output, dcc, html, callback, Input

    # app = Dash()

    # app.layout = [
    #     html.Header(children="Просто кнопка"),
    #     dcc.Button(children="Connect", id="connect-val", n_clicks=0),
    #     html.Div(children="ЖМИ!", id="connect-container")
    # ]


    # @callback(
    #     Output(component_id="connect-container", component_property="children"),
    #     Input(component_id="connect-val", component_property="n_clicks"),
    #     prevent_initial_call=True
    # )
    # def connect(n_clicks: int) -> None:
    #     return f"Сделано 'ЖМИ!' {n_clicks} раз"

    # import dash_app_starter as das
    # das.s(app, dict(debug=True))
    # import subprocess
    # # subprocess.run(["conda activate env_ml"])
    # out = subprocess.run(["python", r"C:\Users\vladi\OneDrive\Projects\Code\Python\Olympic_games\RN\2026\code\dash_app_starter.py"])
    return


@app.cell
def _(mo, px):
    import pandas as pd


    plot = px.scatter(pd.DataFrame({"x": [1, 2, 3], "y": [3, 1, 2]}))
    out = mo.ui.plotly(plot)
    out
    return (out,)


@app.cell
def _(out):
    out.value
    return


if __name__ == "__main__":
    app.run()
