"""
Disk cache of generated diagrams, so that large orders are only computed once.

A result is stored under a hash of the theory (all its terms), the order, the process and the source code of the
engine, so it is recomputed automatically when any of them changes. The default directory is
$XDG_CACHE_HOME/rgpep_dgt or ~/.cache/rgpep_dgt. Deleting the directory clears the cache.
"""
import hashlib
import os
import pickle
from pathlib import Path


def cache_dir(directory=None):
    if directory is not None:
        return Path(directory)
    base = os.environ.get("XDG_CACHE_HOME") or os.path.join(os.path.expanduser("~"), ".cache")
    return Path(base) / "rgpep_dgt"


def _engine_source():
    here = Path(__file__).parent
    return b"".join((here / name).read_bytes() for name in ("generate.py", "theory.py"))


def cache_key(theory, order, n_in, n_out):
    data = repr((theory, order, list(n_in), list(n_out))).encode() + _engine_source()
    return hashlib.sha256(data).hexdigest()


def cached(theory, order, n_in, n_out, workers=1, directory=None):
    """generate_diagrams with the result kept on disk."""
    from rgpep_dgt.engine.generate import generate_diagrams

    path = cache_dir(directory) / f"{theory.name}_order{order}_{cache_key(theory, order, n_in, n_out)[:16]}.pkl"
    if path.exists():
        try:
            with open(path, "rb") as f:
                return pickle.load(f)
        except Exception:
            pass  # A broken file is recomputed and overwritten
    diagrams = generate_diagrams(theory, order, n_in, n_out, workers=workers)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    with open(temporary, "wb") as f:
        pickle.dump(diagrams, f, protocol=pickle.HIGHEST_PROTOCOL)
    temporary.replace(path)
    return diagrams
