import typing as t

import torch
import torch.fx
from torch.fx.passes.operator_support import OperatorSupport
from torch.fx.passes.tools_common import CALLABLE_NODE_OPS

try:
    from torch._C._nvfuser import FusionDefinition as fd  # type: ignore[import]
except ImportError:
    # Not all PyTorch builds have nvfuser
    pass

class NvFuserOperatorSupport(OperatorSupport):
    """
    Operator support for nvFuser backend.

    Note: When adding a rule, please add it to the corresponding secion and follow the
    alphabetical order.
    """

    def __init__(self):
        support_dict = {
            # ===============================================================
            # call_function aten
            # ===============================================================
            # Following supported aten ops is copied from torch/csrc/jit/codegen/cuda/parser.cpp
            # TODO: might need to update according to supported input types
            "torch.ops.aten.add": None,
            "torch.ops.aten.sub": None,
            "torch.ops.aten.rsub": None,
            "torch.ops.aten.div": None,
            "torch.ops.aten.atan2": None,
            "torch.ops.aten.mul": None,
            "torch.ops.aten.max": None,
            "torch.ops.aten.min": None,
            "torch.ops.aten.pow": None,
            "torch.ops.aten.remainder": None,
            "torch.ops.aten.fmod": None,
            "torch.ops.aten.bitwise_and": None,
            "torch.ops.aten.__and__": None,
            "torch.ops.aten.bitwise_or": None,
            "torch.ops.aten.__or__": None,
            "torch.ops.aten.bitwise_xor": None,
            "torch.ops.aten.__xor__": None,
            "torch.ops.aten.bitwise_left_shift": None,
            "torch.ops.aten.__lshift__": None,
            "torch.ops.aten.bitwise_right_shift": None,
            "torch.ops.aten.__rshift__": None,
            "torch.ops.aten.eq": None,
            "torch.ops.aten.ne": None,
            "torch.ops.aten.ge": None,
            "torch.ops.aten.gt": None,
            "torch.ops.aten.le": None,
            "torch.ops.aten.lt": None,
            "torch.ops.aten.abs": None,
            "torch.ops.aten.bitwise_not": None,
            "torch.ops.aten.ceil": None,
            "torch.ops.aten.floor": None,
            "torch.ops.aten.frac": None,
            "torch.ops.aten.neg": None,
            "torch.ops.aten.relu": None,
            "torch.ops.aten.round": None,
            "torch.ops.aten.silu": None,
            "torch.ops.aten.trunc": None,
            "torch.ops.aten.log": None,
            "torch.ops.aten.log10": None,
            "torch.ops.aten.log1p": None,
            "torch.ops.aten.log2": None,
            "torch.ops.aten.lgamma": None,
            "torch.ops.aten.exp": None,
            "torch.ops.aten.expm1": None,
            "torch.ops.aten.erf": None,
            "torch.ops.aten.erfc": None,
            "torch.ops.aten.cos": None,
            "torch.ops.aten.acos": None,
            "torch.ops.aten.cosh": None,
            "torch.ops.aten.sin": None,
            "torch.ops.aten.asin": None,
            "torch.ops.aten.sinh": None,
            "torch.ops.aten.tan": None,
            "torch.ops.aten.atan": None,
            "torch.ops.aten.tanh": None,
            "torch.ops.aten.atanh": None,
            "torch.ops.aten.sqrt": None,
            "torch.ops.aten.rsqrt": None,
            "torch.ops.aten.reciprocal": None,
            "torch.ops.aten.sigmoid": None,
            "torch.ops.aten.isfinite": None,
            "torch.ops.aten.isinf": None,
            "torch.ops.aten.isnan": None,
            "torch.ops.aten.isneginf": None,
            "torch.ops.aten.isposinf": None,
            "torch.ops.aten.isreal": None,
            "torch.ops.aten.rand_like": None,
            "torch.ops.aten.softplus": None,
            "torch.ops.aten.threshold": None,
            "torch.ops.aten.threshold_backward": None,
            "torch.ops.aten.clamp": None,
            "torch.ops.aten.where": None,
            "torch.ops.aten.lerp": None,
            "torch.ops.aten.addcmul": None,
            "torch.ops.aten.native_dropout": None,
            "torch.ops.aten.dropout": None,
            "torch.ops.aten.native_dropout_backward": None,
            "torch.ops.aten.instance_norm": None,
            "torch.ops.aten._batch_norm_impl_index": None,
            "torch.ops.aten.native_batch_norm": None,
            "torch.ops.aten.batch_norm": None,
            "torch.ops.aten.cudnn_batch_norm": None,
            "torch.ops.aten._batch_norm_impl_index_backward": None,
            "torch.ops.aten.native_batch_norm_backward": None,
            "torch.ops.aten.native_layer_norm": None,
            "torch.ops.aten.layer_norm": None,
            "torch.ops.aten.native_layer_norm_backward": None,
            "torch.ops.aten.softmax.int": None,
            "torch.ops.aten.log_softmax.int": None,
            "torch.ops.aten._softmax": None,
            "torch.ops.aten._log_softmax_backward_data": None,
            "torch.ops.aten._softmax_backward_data": None,
            "torch.ops.aten.var.dim": None,
            "torch.ops.aten.std.dim": None,
            "torch.ops.aten.sum.dim_IntList": None,
            "torch.ops.aten.mean.dim": None,
            "torch.ops.aten._grad_sum_to_size": None,
            "torch.ops.aten.sum_to_size": None,
            "torch.ops.aten._autocast_to_reduced_precision": None,
            "torch.ops.aten._autocast_to_full_precision": None,
            "torch.ops.aten.to.dtype": None,
            "torch.ops.aten.type_as": None,
            "torch.ops.aten.linear": None,
            "torch.ops.aten.gelu": None,
            "torch.ops.aten.gelu_backward": None,
            "torch.ops.aten.tanh_backward": None,
            "torch.ops.aten.amax": None,
            "torch.ops.aten.amin": None,
            "torch.ops.aten.reshape": None,
            "torch.ops.aten.view": None,
            "torch.ops.aten.flatten.using_ints": None,

            # ===============================================================
            # call_function aten: inplace variants
            # ===============================================================
            # These nodes shouldn't show up, the functionalization pass should have removed inplace ops
            "torch.ops.aten.add_": None,
            "torch.ops.aten.relu_": None,

            # ===============================================================
            # call_function builtins and operator
            # ===============================================================
            "getattr": None,
            #     "_operator.add": None,
            #     "_operator.div": None,
            "_operator.getitem": None,
            #     "_operator.mul": None,
            #     "_operator.sub": None,
            #     "_operator.truediv": None,
        }

        prim_nvfuser_ops = set(torch._prims.__all__).intersection(dir(fd.Ops))

        ops_with_nvfuser_impl = {
            "torch.ops.prims." + name + ".default" : None
            for name in prim_nvfuser_ops
            if getattr(torch.ops.prims, name).default.impl_nvfuser is not None
        }

        merged_support_dict = {**support_dict, **ops_with_nvfuser_impl}

        super().__init__(merged_support_dict)

    def is_node_supported(
        self, submodules: t.Mapping[str, torch.nn.Module], node: torch.fx.Node
    ) -> bool:

        # nvFuser FX subgraph should be purely functional
        if node.op not in CALLABLE_NODE_OPS:
            return False

        return super().is_node_supported(submodules, node)