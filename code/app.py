# %% [markdown]
# # Олимпиада «Россети», 2 этап, 8—9 класс

# %% [markdown]
# ## Импорт библиотек. Подготовка

# %%
from typing import Tuple, List, Self
import pickle
from collections import defaultdict
from scipy.spatial.distance import euclidean as euclidean_distance
from fastcore.basics import store_attr
from fastcore.meta import delegates, patch_to
from matplotlib import pyplot as plt
from matplotlib.ticker import MultipleLocator
from plotly import graph_objects as go
from plotly import express as px
from dash import Dash, Output, dcc, html, callback, Input, State
from uuid import uuid4 as uuid

# %%
# from rich.traceback import install
# from rich.console import Console

# install(
#     console=Console(force_jupyter=True),
#     width=100,
#     code_width=100,
#     word_wrap=True,
#     show_locals=True,
# )

# %%
# font_dict=dict(family='Arial',
#                size=26,
#                color='black'
#                )

# %%
# fig = go.Figure()

# fig.update_xaxes(
#     range=(0, 15),
#     showgrid=True,
#     gridwidth=1,
#     minor=dict(
#         ticklen=2,
#         showgrid=True,
#         gridcolor="Gray",
#         gridwidth=0.25,
#     )
# )

# fig.update_xaxes(
#     title_text='X-axis',
#     showline=True,
#     showticklabels=True,
#     linecolor='black',
#     linewidth=2.4,
#     ticks='outside',
#     tickfont=font_dict,
#     mirror='allticks',
#     tickwidth=2.4,
#     tickcolor='black',
# )

# fig.update_yaxes(
#     range=(0, 15),
#     showgrid=True,
#     gridwidth=1,
#     minor=dict(
#         ticklen=2,
#         showgrid=True,
#         gridcolor="Gray",
#         gridwidth=0.5
#     )
# )

# fig.update_yaxes(title_text='Y-axis',  # axis label
#                  showline=True,  # add line at x=0
#                  linecolor='black',  # line color
#                  linewidth=2.4, # line size
#                  ticks='outside',  # ticks outside axis
#                  tickfont=font_dict, # tick label font
#                  mirror='allticks',  # add ticks to top/right axes
#                  tickwidth=2.4,  # tick width
#                  tickcolor='black',  # tick color
#                  )

# fig.update_layout(plot_bgcolor='black',
#                   autosize=False,
#                   width=750,
#                   height=750)
# fig.show()

# %%
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

# %% [markdown]
# ## Объявление констант из условий

# %%
# Постоянные
OUTAGES_FREQ_PER_KM = 0.05
LOSS_PER_POWER = 200
LOSS_PER_WORK = 50
COST_PER_KM = 500000

# %% [markdown]
# | Название переменной   | Название в условии кейса                    |
# | :-------------------: | :-----------------------------------------: |
# | `OUTAGES_FREQ_PER_KM` | $\lambda = 0.05 \ \text{раз/км}$            |
# | `LOSS_PER_POWER`      | $у_{\lambda} = 200 \ \text{руб./кВт}$       |
# | `LOSS_PER_WORK`       | $у_D = 50 \ \text{руб./кВт} \cdot \text{ч}$ |
# | `COST_PER_KM`        | Цена за километр линии (назовём $\mu$)                      |

# %%
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


POWERS = [
    300,
    20,
    300,
    150,
    20,
    40,
    300,
    150,
    500,
    200,
    20,
    40,
    500,
    20,
    60,
    40,
    40,
    60,
    200,
    150,
    60,
    200,
    60,
    300,
    500,
    500,
    200,
    150,
    40,
]

# %%
print(len(COORDS), len(POWERS))
print(list(zip(COORDS, POWERS, strict=True)))

# %% [markdown]
# ## Представление элементов сети как классов

# %% [markdown]
# ### `Node` — потребители (вершины графа)

# %%
class Node:
    def __init__(
        self, coords: Tuple[int, int], connections: List["Connection"] = None
    ) -> None:
        self.connections = connections if connections is not None else []
        self._coords = coords
        self.id = str(uuid())

    @property
    def coords(self) -> Tuple[int, int]:
        return self._coords

    @coords.setter
    def coords(self, value: Tuple[int, int]) -> None:
        raise TypeError(
            f"Попытка изменить координаты нода, который не является ConsumerNode. Истинный класс нода {type(self)}."
        )
    
    def __eq__(self, other: "Node") -> bool:
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    # def add_connection(self, connection: "Connection") -> None:
    #     self.connections.append(connection)
    #     connection.get_opposite_node(self).connections.append(connection)

# %%
class ConsumerNode(Node):
    @delegates(Node.__init__)
    def __init__(self, power: int, **kwargs) -> None:
        super().__init__(**kwargs)
        store_attr()

# %%
class SolderingNode(Node):
    @delegates(Node.__init__)
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

# %%
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

# %% [markdown]
# ### `Equipment` — оборудование на соединениях

# %%
class Equipment:
    def __init__(self, cost: int) -> None:
        self._cost = cost

    @property
    def cost(self) -> int:
        return self._cost

# %%
class ManualSwitch(Equipment):
    def __init__(self) -> None:
        super().__init__(50000)

# %%
class AutoSwitch(Equipment):
    def __init__(self) -> None:
        super().__init__(250000)

# %%
class SubstationSwitch(Equipment):
    def __init__(self) -> None:
        super().__init__(150000)

# %% [markdown]
# ### `Connection` — линия электропередач (ребро)

# %%
class NoConnectionError(Exception):
    pass

# %%
class Connection:
    def __init__(
        self,
        node1: Node,
        node2: Node,
        node1_equip: Equipment | None = None,
        node2_equip: Equipment | None = None,
    ) -> None:
        store_attr()
        self.id = str(uuid())
        if self not in node1.connections:
            node1.connections.append(self)
        if self not in node2.connections:
            node2.connections.append(self)

    @property
    def length(self) -> float:
        return euclidean_distance(self.node1.coords, self.node2.coords)

    @property
    def cost(self) -> float:
        out = self.length * COST_PER_KM
        if self.node1_equip is not None:
            out += self.node1_equip.cost
        if self.node2_equip is not None:
            out += self.node2_equip.cost
        return out

    def get_opposite_node(self, caller: Node) -> Node:
        # if caller is self.node1:
        #     return self.node2
        # if caller is self.node2:
        #     return self.node1
        if caller.id == self.node1.id:
            return self.node2
        if caller.id == self.node2.id:
            return self.node1
        else:
            raise NoConnectionError(
                f"ПЕРЕХОД НЕВОЗМОЖЕН. Произведена попытка перейти по ребру, соединяющему {self.node1.coords} и {self.node2.coords}, но сaller {caller.coords} не является вершиной этого ребра."
            )
    
    def __eq__(self, other: "Connection") -> bool:
        return self.id == other.id
    
    def __hash__(self) -> int:
        return hash(self.id)

# %% [markdown]
# ### `Network` — сеть

# %%
class Network:
    def __init__(self, nodes: List[Node], substation_node: SubstationNode) -> None:
        store_attr()

# %% [markdown]
# #### Фабричный метод `init_from_default` инициализации как из условия

# %%
@patch_to(Network, cls_method=True)
def init_from_default(cls) -> Self:
    nodes = []
    for c, p in zip(COORDS, POWERS, strict=True):
        n = ConsumerNode(power=p, coords=c)
        nodes.append(n)
    return cls(nodes, SubstationNode())

# %% [markdown]
# #### Методы `save` и фабричный `init_from_saved`, реализующие сохранение и открытие из сохранённого (на данный момент не работают)

# %%
@patch_to(Network, cls_method=True)
def init_from_saved(cls, basename: str) -> Self:
    with open(f"./networks/{basename}.pkl", "rb") as f:
        return pickle.load(f)

@patch_to(Network)
def save(self, basename: str) -> None:
    with open(f"./networks/{basename}.pkl", "xb") as f:
        pickle.dump(self, f, pickle.HIGHEST_PROTOCOL)

# %% [markdown]
# #### Свойство `cost`, считающее и возвращающее общие затраты на постройку и содержание
# 
# $$
# У = у_{\lambda} \cdot \lambda_{\sum} \cdot P + у_D \cdot D_{\sum} \cdot P \\
# У = 200 \cdot \lambda_{\sum} \cdot P + 50 \cdot D_{\sum} \cdot P \\
# У = 50 \cdot P \cdot (4 \cdot \lambda_{\sum} + D_{\sum})
# $$
# 
# При этом мы считаем, что единственный путь до точки — все рёбра от корня дерева до неё, а также, что у нас нет вспомогательного оборудования и частота отключения — это общая частота отключения на всём дереве.
# 
# $$
# У = 50 P \cdot (4 \cdot (\lambda L_{\sum}) + 6 \cdot \lambda L_{\sum}) \\
# У = 100 P \cdot (2 \cdot \lambda L_{\sum} + 3 \cdot \lambda L_{\sum}) \\
# У = 500 \cdot P \cdot \lambda L_{\sum} \\
# \left( L_{\sum} \text{ — сумма длин всех рёбер} \right)
# $$
# 
# Это был ущерб для каждого потребителя. Нам нужен общий ущерб, что является суммой ущербов потребителей
# 
# $$
# У_{\sum} = \sum _{i=1} ^n (500 \cdot P_i \cdot \lambda L_{\sum}) \\
# \textcolor{cyan}{У_{\sum} = 500 \cdot \lambda L_{\sum} \cdot P_{\sum}}
# $$
# 
# $$
# \textcolor{yellow}{З_{\sum} = \mu L_{\sum} + З.О.}
# $$
# 
# ---
# 
# Общая стоимость — ущерб + затраты на строительство
# 
# $$
# С_{\sum} = \textcolor{cyan}{У_{\sum}} + \textcolor{yellow}{З_{\sum}} \\[1em]
# С_{\sum} = \textcolor{cyan}{500 \cdot \lambda L_{\sum} \cdot P_{\sum}} + \textcolor{yellow}{\mu L_{\sum} + З.О.} \\[1em]
# С_{\sum} = L_{\sum} (500 \cdot \lambda P_{\sum} + \mu) + З.О.
# $$

# %%
print(sum(POWERS))

# %% [markdown]
# $$
# З.О. = 150000 \cdot \alpha \\[1em]
# С_{\sum} = L_{\sum} (500 \cdot 0.05 \cdot 5120) + 150000 \cdot \alpha \\[1em]
# С_{\sum} = 128000 \cdot L_{\sum} + 150000 \cdot \alpha + 500000 \\[1em]
# $$

# %%
@patch_to(Network, as_prop=True)
def length(self) -> float:
    self._length = 0.0
    self._seen_connections = set()
    self._get_surrounding_length(node=self.substation_node)
    return self._length

@patch_to(Network)
def _get_surrounding_length(self, node: Node) -> None:
    # print(node.coords, [(i.node1.coords, i.node2.coords) for i in node.connections])
    for c in node.connections:
        if c is not None and c not in self._seen_connections:
            self._length += c.length
            self._seen_connections.add(c)
            self._get_surrounding_length(node=c.get_opposite_node(caller=node))

@patch_to(Network, as_prop=True)
def formula_cost(self) -> float:
    substation_equip_count = 0
    for c in self.substation_node.connections:
        if c is not None:
            substation_equip_count += 1
    
    l = self.length
    return 150000 * substation_equip_count + 500000 * l + 128000 * l

# %%
@patch_to(Network, as_prop=True)
def cost(self) -> int:
    self._cost = 0
    self._seen_connections = set()
    self._get_surrounding_cost(node=self.substation_node)
    return self._cost


@patch_to(Network)
def _get_surrounding_cost(self, node: Node) -> None:
    for c in node.connections:
        print(node.coords, c.node1.coords, c.node2.coords)
        if c is not None and c not in self._seen_connections:
            print(c, type(c))
            self._cost += c.cost
            self._seen_connections.add(c)
            self._get_surrounding_cost(c.get_opposite_node(caller=node))

# %% [markdown]
# #### Метод `interactive` для интерактивной визуализации сети и соединений в ней на плоскости

# %%
@patch_to(Network)
def interactive(self) -> Dash:
    # Создание приложения
    self.app = Dash(__name__)
    self.server = self.app.server

    # Создания начального графика (без соединений, только точки)
    MARKER_SIZE = 10
    df = defaultdict(list)

    for i, node in enumerate(self.nodes):
        x, y = node.coords
        power = node.power
        df["x"].append(x)
        df["y"].append(y)
        df["power"].append(power)
        df["id"].append([i])

    main_scatter = px.scatter(
        data_frame=df, x="x", y="y", custom_data="id", height=720, width=720
    ).update_traces(marker_color="black", marker_size=MARKER_SIZE)

    # Разметка приложения
    self.app.layout = [
        html.Div(
            [
                main_scatter := dcc.Graph(figure=main_scatter, id="main_scatter"),
                html.Div(
                    [
                        html.Div(
                            [
                                x_coord_slider := dcc.Slider(
                                    min=0,
                                    max=15,
                                    step=0.5,
                                    value=0,
                                    id="x_coord_slider",
                                ),
                                html.Div("x"),
                            ]
                        ),
                        html.Div(
                            [
                                y_coord_slider := dcc.Slider(
                                    min=0,
                                    max=15,
                                    step=0.5,
                                    value=0,
                                    id="y_coord_slider",
                                ),
                                html.Div("y"),
                            ]
                        ),
                    ]
                ),
                html.Div(
                    [
                        set_substation_coords_button := dcc.Button(
                            children="Установить координаты подстанции",
                            id="set_substation_coords_button",
                        ),
                        substation_coords_change_result := html.Div(
                            children="", id="substation_coords_change_result"
                        ),
                        set_soldering_node_coords_button := dcc.Button(
                            children="Установить координаты паечной точки",
                            id="set_soldering_node_coords_button",
                        ),
                        soldering_node_coords_change_result := html.Div(
                            children="", id="soldering_node_coords_change_result"
                        ),
                    ]
                ),
                html.Div(
                    [
                        connect_button := dcc.Button(
                            children="Соединить выбранные точки",
                            id="connect_button",
                        ),
                        connect_result := html.Div(
                            children="", id="connect_result"
                        ),
                    ]
                ),
                html.Div(
                    [
                        get_cost_button := dcc.Button(
                            children="Рассчитать затраты", id="get_cost_button"
                        ),
                        cost_result := html.Div(children="", id="cost_result"),
                    ]
                ),
                html.Div(
                    [
                        html.Div("Введите имя файла сохранения"),
                        save_basename_input := dcc.Input(
                            value="",
                            type="text",
                            id="save_filename_input" 
                        ),
                        save_button := dcc.Button(
                            children="Сохранить сеть", id="save_button"
                        ),
                        save_result := html.Div(children="", id="save_result")
                    ]
                )
            ]
        )
    ]

    # Событие установки координат ПС
    @callback(
        Output(main_scatter, "figure"),
        Output(substation_coords_change_result, "children"),
        Input(set_substation_coords_button, "n_clicks"),
        State(x_coord_slider, "value"),
        State(y_coord_slider, "value"),
        State(main_scatter, "figure"),
        prevent_initial_call=True,
    )
    def set_substation_coords_callback(
        n_clicks: int, x: int, y: int, cur_scatter: dict
    ) -> Tuple[go.Figure, str]:
        cur_scatter = go.Figure(cur_scatter)

        if 0 not in (x, y):
            return (
                cur_scatter,
                "Ошибка: одна из координат подстанции должна быть равна 0.",
            )
        self.substation_node.coords = (x, y)
        new_scatter = cur_scatter.add_trace(
            px.scatter(x=[x], y=[y], custom_data=[[[-1]]])
            .update_traces(marker_color="red", marker_size=MARKER_SIZE)
            .data[0]
        )
        return new_scatter, f"Успешно: координаты подстанции изменены на {x, y}."

    # Событие установки точки спайки
    @callback(
        Output(main_scatter, "figure", allow_duplicate=True),
        Output(soldering_node_coords_change_result, "children"),
        Input(set_soldering_node_coords_button, "n_clicks"),
        State(x_coord_slider, "value"),
        State(y_coord_slider, "value"),
        State(main_scatter, "figure"),
        prevent_initial_call=True,
    )
    def set_soldering_node_coords_callback(
        n_clicks: int, x: int, y: int, cur_scatter: dict
    ) -> Tuple[go.Figure, str]:
        cur_scatter = go.Figure(cur_scatter)

        new_node = SolderingNode(coords=(x, y))
        self.nodes.append(new_node)
        new_scatter = cur_scatter.add_trace(
            px.scatter(x=[x], y=[y], custom_data=[[[len(self.nodes) - 1]]])
            .update_traces(marker_color="blue", marker_size=MARKER_SIZE)
            .data[0]
        )
        return (
            new_scatter,
            f"Успешно: добавлена паечная точка с координатами {x, y}.",
        )

    # Событие для соединения двух нод
    @callback(
        Output(
            component_id=main_scatter,
            component_property="figure",
            allow_duplicate=True,
        ),
        Output(component_id=connect_result, component_property="children"),
        Input(component_id=connect_button, component_property="n_clicks"),
        State(component_id=main_scatter, component_property="figure"),
        State(component_id=main_scatter, component_property="selectedData"),
        prevent_initial_call=True,
    )
    def connect_callback(
        n_clicks: int, cur_scatter: dict, selected_data: str
    ) -> Tuple[go.Figure, str]:
        cur_scatter = go.Figure(cur_scatter)

        if selected_data is None or len(selected_data["points"]) == 0:
            return cur_scatter, "Ошибка: ни одной точки не выбрано."

        nodes_to_connect = [
            (
                self.nodes[p["customdata"][0][0]]
                if p["customdata"][0][0] != -1
                else self.substation_node
            )
            for p in selected_data["points"]
        ]

        if len(nodes_to_connect) == 2:
            for i in nodes_to_connect:
                print(i.id, i.coords, [(j.node1.coords, j.node2.coords) for j in i.connections])
            Connection(*nodes_to_connect)
            for i in nodes_to_connect:
                print(i.id, i.coords, [(j.node1.coords, j.node2.coords) for j in i.connections])

            node1, node2 = nodes_to_connect
            x_to_connect = [node1.coords[0], node2.coords[0]]
            y_to_connect = [node1.coords[1], node2.coords[1]]
            new_scatter = cur_scatter.add_trace(
                px.scatter(x=x_to_connect, y=y_to_connect)
                .update_traces(mode="lines")
                .data[0]
            )
            return new_scatter, "Успешно: точки соеденены."
        else:
            return (
                cur_scatter,
                f"Ошибка: можно соединить только 2 точки за раз. Вместо 2 точек выбрано {len(nodes_to_connect)} точек.",
            )

    # Событие вывода стоимости
    @callback(
        Output(component_id=cost_result, component_property="children"),
        Input(component_id=get_cost_button, component_property="n_clicks"),
        prevent_initial_call=True,
    )
    def get_cost_callback(n_clicks: int) -> str:
        return self.formula_cost
    
    @callback(
        Output(save_result, "children"),
        Input(save_button, "n_clicks"),
        State(save_basename_input, "value"),
        prevent_initial_call=True
    )
    def save_callback(n_clicks: int, basename: str) -> str:
        if len(basename) == 0:
            return "Ошибка: невозможно создать файл с пустым именем."
        try:
            self.save(basename)
            return f"Успешно: сеть сохранена в файл ./networks/{basename}.pkl"
        except FileExistsError:
            return "Ошибка: файл с таким именем уже существует"

    if __name__ == "main":
        self.app.run_server(debug=False)
    # self.app.run(debug=True, jupyter_mode="external")


network = Network.init_from_default().interactive()
