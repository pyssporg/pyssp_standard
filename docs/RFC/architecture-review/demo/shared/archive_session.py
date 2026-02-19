from pathlib import Path


class ArchiveStateError(RuntimeError):
    pass


class ArchiveSession:
    """Minimal archive/session abstraction for discussion.

    In this mockup, the session wraps plain files (not zip archives) to
    demonstrate dirty tracking and explicit persistence points.
    """

    def __init__(self, path: Path, mode: str = "r"):
        self.path = Path(path)
        self.mode = mode
        self._dirty = False

    @property
    def dirty(self) -> bool:
        return self._dirty

    def read_text(self) -> str:
        if not self.path.exists():
            if self.mode == "r":
                raise FileNotFoundError(self.path)
            return ""
        return self.path.read_text(encoding="utf-8")

    def write_text(self, content: str):
        if self.mode == "r":
            raise ArchiveStateError("Cannot write in read-only mode")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(content, encoding="utf-8")
        self._dirty = True

    def save_as(self, target: Path):
        if self.mode == "r":
            raise ArchiveStateError("Cannot save_as in read-only mode")
        target = Path(target)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(self.path.read_text(encoding="utf-8"), encoding="utf-8")
