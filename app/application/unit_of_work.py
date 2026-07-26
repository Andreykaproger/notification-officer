from typing import Protocol


class UnitOfWork(Protocol):
    async def commit(self) -> None:
        """Persist all pending changes."""
        pass

    async def rollback(self) -> None:
        """Rollback current transaction."""
        pass
