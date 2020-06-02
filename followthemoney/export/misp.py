#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Dict, Tuple, List, TextIO, Optional

from pymisp import MISPObject

from followthemoney.graph import Node, Edge
from followthemoney.types import registry
from followthemoney.proxy import EntityProxy
from followthemoney.export.graph import GraphExporter


DEFAULT_EDGE_TYPES: Tuple[str] = (registry.entity.name,)


class MISPExporter(GraphExporter):

    def __init__(self, fh: Optional[TextIO]=None, edge_types: Tuple[str]=DEFAULT_EDGE_TYPES):
        super(MISPExporter, self).__init__(edge_types=edge_types)
        self._nodes_mapping: Dict[str, MISPObject] = {}
        self._references_to_add: List[Tuple[MISPObject, str]] = []

        self.misp_objects: List[MISPObject] = []
        self.fh: Optional[TextIO] = fh

    def add_entity(self, proxy: EntityProxy, **kwargs):
        self.graph.add(proxy)

    def write_graph(self):
        for node in self.graph.iternodes():
            self.write_node(node)

        for src, dst in self._references_to_add:
            src.add_reference(self._nodes_mapping[dst], 'related-to')

        for edge in self.graph.iteredges():
            self.write_edge(edge)

    def write_node(self, node: Node):
        if node.is_entity:
            # NOTE: if the node is an entity, schema cannot be None
            misp_object = MISPObject(f'ftm-{node.schema.name}', standalone=False)  # type: ignore
            if not node.proxy:
                return
            for prop, value in self.exportable_fields(node.proxy):
                if not value:
                    continue
                if prop.type.name == 'entity':
                    # reference
                    node_id = prop.type.node_id_safe(value)
                    if node_id:
                        self._references_to_add.append((misp_object, node_id))
                    continue
                misp_object.add_attributes(prop.name, *value)

            self._nodes_mapping[node.id] = misp_object
            self.misp_objects.append(misp_object)

    def write_edge(self, edge: Edge):
        source_object = self._nodes_mapping[edge.source_id]
        target_object = self._nodes_mapping[edge.target_id]
        if edge.schema is None or not edge.schema.edge_label:
            relation = 'related-to'
        else:
            relation = '-'.join(edge.schema.edge_label.split())
        source_object.add_reference(target_object, relation)

    def finalize_graph(self):
        if not self.fh:
            raise Exception('File handle required to dump the objects')
        for obj in self.misp_objects:
            self.fh.write(obj.to_json())
