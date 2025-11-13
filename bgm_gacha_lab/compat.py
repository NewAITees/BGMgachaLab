"""Compatibility helpers for third-party libraries."""

from __future__ import annotations


def patch_torch_pytree() -> None:
    """Shim torch<2.2 so new consumers can call register_pytree_node."""

    try:
        from torch.utils import _pytree  # type: ignore
    except Exception:
        return

    if hasattr(_pytree, "register_pytree_node"):
        return

    fallback = getattr(_pytree, "_register_pytree_node", None)
    if fallback is None:
        return

    # Wrap the fallback to ignore new kwargs like serialized_type_name
    def register_pytree_node_wrapper(
        cls,
        flatten_fn,
        unflatten_fn,
        *,
        serialized_type_name=None,
        to_dumpable_context=None,
        from_dumpable_context=None,
        **kwargs
    ):
        # Call the original with only the args it supports
        return fallback(cls, flatten_fn, unflatten_fn)

    _pytree.register_pytree_node = register_pytree_node_wrapper  # type: ignore[attr-defined]

