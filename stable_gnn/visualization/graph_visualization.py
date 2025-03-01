from copy import deepcopy

import matplotlib.pyplot as plt

from stable_gnn.visualization.base_visualization import BaseVisualization

from stable_gnn.visualization.config.parameters.edge_styles import EdgeStyles
from stable_gnn.visualization.constructors.layout_constructor import LayoutConstructor
from stable_gnn.visualization.constructors.size_constructor import SizeConstructor
from stable_gnn.visualization.constructors.graph_strength_constructor import GraphStrengthConstructor
from stable_gnn.visualization.constructors.graph_style_constructor import GraphStyleConstructor
from stable_gnn.visualization.contracts.draw_circle_edges_contract import DrawEdgesContract
from stable_gnn.visualization.contracts.draw_line_edges_contract import DrawLineEdgesContract
from stable_gnn.visualization.contracts.draw_vertex_contract import DrawVertexContract
from stable_gnn.visualization.contracts.graph_contract import GraphContract
from stable_gnn.visualization.contracts.graph_visualization_contract import GraphVisualizationContract
from stable_gnn.visualization.contracts.layout_contract import LayoutContract
from stable_gnn.visualization.contracts.size_constructor_contract import SizeConstructorContract
from stable_gnn.visualization.contracts.strength_constructor_contract import StrengthConstructorContract
from stable_gnn.visualization.contracts.style_constructor_contract import GraphStyleConstructorContract
from stable_gnn.visualization.exceptions.exceptions_classes import ParamsValidationException
from stable_gnn.visualization.config.parameters.defaults import Defaults
from stable_gnn.visualization.equations.calc_arrow_head_width import calc_arrow_head_width
from stable_gnn.visualization.equations.calc_direction import calc_direction


class GraphVisualizer(BaseVisualization):
    """
    Draw arrowed or undirected graph.
    Common methods defined in Base class.
    """
    contract = None

    def __init__(self, contract: GraphVisualizationContract):
        """
        Class initialization with contract GraphVisualizationContract and parameter validation.
        GraphVisualizationContract:
            graph - GraphContract
            edge_style - Edge Style
            edge_color - Edge Color
            edge_fill_color - Edge fill Color
            edge_line_width - Edge line width
            vertex_label - Labels for vertexes
            vertex_size - Sizes of vertexes
            vertex_color - Vertex Colors
            vertex_line_width - Line width
            font_size - Font Size
            font_family - Font Family
            push_vertex_strength - Strength value for vertexes push
            push_edge_strength - Strength value for Edges push
            pull_edge_strength - Strength value for Edges pull
            pull_center_strength - Strength value for centers pull
        GraphContract:
            edge_num - Number of edges
            vertex_num - Number of vertexes
            edge_list - List of the edges
            edge_weights - Weights of the edges
        """
        self.contract = contract

        self.validate()

    def draw(self):
        """
        Draw graph interface based on Contract.
        """
        # Define base matplotlib Plot with axes (mutable object)
        fig, axes = plt.subplots(figsize=Defaults.figure_size)

        # Copy data from source
        vertex_num, edge_list = self.contract.graph.vertex_num, deepcopy(self.contract.graph.edge_list[0])

        # Define style contract
        default_style_contract: GraphStyleConstructorContract = GraphStyleConstructorContract(
            vertex_num=self.contract.graph.vertex_num,
            edges_num=self.contract.graph.edge_num,
            vertex_color=self.contract.vertex_color,
            edge_color=self.contract.edge_color,
            edge_fill_color=self.contract.edge_fill_color
        )

        # Construct styles
        default_style_constructor: GraphStyleConstructor = GraphStyleConstructor()
        (
            vertex_color,
            edge_color,
            edge_fill_color
         ) = default_style_constructor(default_style_contract)

        # Define size contract
        default_size_contract: SizeConstructorContract = SizeConstructorContract(vertex_num=vertex_num,
                                                                                 edge_list=edge_list,
                                                                                 vertex_size=self.contract.vertex_size,
                                                                                 vertex_line_width=self.contract.vertex_line_width,
                                                                                 edge_line_width=self.contract.edge_line_width,
                                                                                 font_size=self.contract.font_size)
        # Construct element sizes
        default_size_constructor: SizeConstructor = SizeConstructor()
        (
            vertex_size,
            vertex_line_width,
            edge_line_width,
            font_size
        ) = default_size_constructor(default_size_contract)

        # Define strength contract
        default_strength_contract: StrengthConstructorContract = StrengthConstructorContract(
            self.contract.push_vertex_strength,
            self.contract.push_edge_strength,
            self.contract.pull_edge_strength,
            self.contract.pull_center_strength)

        # Construct strengths
        default_strength_constructor: GraphStrengthConstructor = GraphStrengthConstructor()
        (
            push_vertex_strength,
            push_edge_strength,
            pull_edge_strength,
            pull_center_strength,
        ) = default_strength_constructor(default_strength_contract)

        # Define layout contract
        layout_contract: LayoutContract = LayoutContract(vertex_num=vertex_num,
                                                         edge_list=edge_list,
                                                         push_vertex_strength=push_vertex_strength,
                                                         push_edge_strength=None,
                                                         pull_edge_strength=pull_edge_strength,
                                                         pull_center_strength=pull_center_strength)

        # Construct layout
        layout_constructor: LayoutConstructor = LayoutConstructor()
        vertex_coordinates = layout_constructor(layout_contract)

        # Define edge styles
        if self.contract.edge_style == EdgeStyles.line:
            draw_line_edges_contract: DrawLineEdgesContract = DrawLineEdgesContract(vertex_coordinates=vertex_coordinates,
                                                                                    vertex_size=vertex_size,
                                                                                    edge_list=edge_list,
                                                                                    show_arrow=False,
                                                                                    edge_color=edge_color,
                                                                                    edge_line_width=edge_line_width)
            self.draw_line_edges(axes=axes, contract=draw_line_edges_contract)
        elif self.contract.edge_style == EdgeStyles.circle:
            draw_circle_edges_contract: DrawEdgesContract = DrawEdgesContract(vertex_coordinates=vertex_coordinates,
                                                                              vertex_size=vertex_size,
                                                                              edge_list=edge_list,
                                                                              edge_color=edge_color,
                                                                              edge_fill_color=edge_fill_color,
                                                                              edge_line_width=edge_line_width)
            self.draw_circle_edges(axes=axes, contract=draw_circle_edges_contract)
        else:
            raise ParamsValidationException("Parameters are not valid")

        # Define vertex contract
        draw_vertex_contract: DrawVertexContract = DrawVertexContract(vertex_coordinates=vertex_coordinates,
                                                                      vertex_label=self.contract.vertex_label,
                                                                      font_size=font_size,
                                                                      font_family=self.contract.font_family,
                                                                      vertex_size=vertex_size,
                                                                      vertex_color=vertex_color,
                                                                      vertex_line_width=vertex_line_width)
        # Draw vertexes on plot
        self.draw_vertex(axes=axes, contract=draw_vertex_contract)

        # Apply plot changes
        plt.xlim(Defaults.x_limits)
        plt.ylim(Defaults.y_limits)
        plt.axis(Defaults.axes_on_off)
        fig.tight_layout()

        return fig

    @staticmethod
    def draw_line_edges(axes, contract: DrawLineEdgesContract):
        """
        Draw edges based on contract DrawLineEdgesContract
        DrawLineEdgesContract:
            vertex_coordinates - Coordinates for vertexes
            vertex_size - Sizes for vertexes
            edge_list - List of the edges
            show_arrow - Show arrows or not
            edge_color - Colors for edges
            edge_line_width - Line width for edge drawing

        """
        # Define arrow sizes
        arrow_head_width = calc_arrow_head_width(contract.edge_line_width,
                                                 contract.show_arrow,
                                                 contract.edge_list)

        for edge_index, e in enumerate(contract.edge_list):
            # For every edge in list
            # Define positions for direction
            start_position = contract.vertex_coordinates[e[0]]
            end_position = contract.vertex_coordinates[e[1]]
            # Define direction
            direction = end_position - start_position
            direction = calc_direction(direction)
            # Define positions for arrow
            start_position = start_position + direction * contract.vertex_size[e[0]]
            end_position = end_position - direction * contract.vertex_size[e[1]]
            # Place arrow on plot
            axes.arrow(start_position[0],
                       start_position[1],
                       end_position[0] - start_position[0],
                       end_position[1] - start_position[1],
                       head_width=arrow_head_width[edge_index],
                       color=contract.edge_color[edge_index],
                       linewidth=contract.edge_line_width[edge_index],
                       length_includes_head=True)

    def validate(self):
        """
        Validate parameters:
            - graph type
            - edge style
            - vertex number
        """
        graph_type_is_correct = isinstance(self.contract.graph, GraphContract)

        edge_style_are_valid = self.contract.edge_style in EdgeStyles().values
        node_quantity_is_positive = self.contract.graph.vertex_num > 0

        if not graph_type_is_correct or not edge_style_are_valid or not node_quantity_is_positive:
            raise ParamsValidationException("Parameters are not valid")
