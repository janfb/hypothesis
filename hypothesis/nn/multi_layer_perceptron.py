r"""Multilayer Perceptron
"""

import hypothesis
import torch

from hypothesis.nn.util import compute_dimensionality
from hypothesis.nn.util import allocate_output_transform



class MultiLayerPerceptron(torch.nn.Module):

    def __init__(self, shape_xs, shape_ys,
        activation=hypothesis.default.activation,
        dropout=0.0,
        layers=(128, 128),
        transform_output="normalize"):
        super(MultiLayerPerceptron, self).__init__()
        mappings = []
        dropout = float(dropout)
        # Dimensionality properties
        self.xs_dimensionality = compute_dimensionality(shape_xs)
        self.ys_dimensionality = compute_dimensionality(shape_ys)
        # Allocate input mapping
        mappings.append(torch.nn.Linear(self.xs_dimensionality, layers[0]))
        # Allocate internal network structure
        for index in range(1, len(layers)):
            mappings.append(self._make_layer(activation, dropout,
                layers[index - 1], layers[index]))
        # Allocate tail
        mappings.append(activation(inplace=True))
        mappings.append(torch.nn.Linear(layers[-1], self.ys_dimensionality))
        operation = allocate_output_transform(transform_output, self.ys_dimensionality)
        if operation is not None:
            mappings.append(operation)
        # Allocate sequential mapping
        self.mapping = torch.nn.Sequential(*mappings)

    def _make_layer(self, activation, dropout, num_a, num_b):
        mappings = []

        mappings.append(activation(inplace=True))
        if dropout > 0:
            mappings.append(torch.nn.Dropout(p=dropout))
        mappings.append(torch.nn.Linear(num_a, num_b))

        return torch.nn.Sequential(*mappings)

    def forward(self, xs):
        xs = xs.view(-1, self.xs_dimensionality)
        y = self.mapping(xs)

        return y
