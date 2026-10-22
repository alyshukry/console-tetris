from typing import Annotated, TypeAlias

from pydantic import Field

Username: TypeAlias = Annotated[str, Field(pattern=r"^[a-z0-9_]{3,16}$")]
