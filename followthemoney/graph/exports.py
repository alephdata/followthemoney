
# def to_digraph(self, graph):
#     if self.inverted:
#         return self.invert().to_digraph(graph)
#     subject_id = self.subject.id
#     graph.add_node(subject_id, label=self.subject)
#     if self.prop.caption:
#         graph.nodes[subject_id]['label'] = self.value
#     if self.prop.type.group is None:
#         graph.nodes[subject_id][self.prop.name] = self.value
#         return
#     if self.weight == 0:
#         return
#     value_id = self.value_node.id
#     graph.add_node(value_id)
#     if self.prop.caption:
#         graph.nodes[subject_id]['label'] = self.value
#     edge = {
#         'weight': self.weight,
#         'label': self.prop.label,
#         'prop': self.prop.qname,
#         'inferred': self.inferred
#     }
#     graph.add_edge(subject_id, value_id, **edge)