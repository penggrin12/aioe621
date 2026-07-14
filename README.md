# aioe621 ![uv](https://img.shields.io/badge/uv-261230.svg?logo=uv&logoColor=#de5fe9)

![PyPI Python Version](https://img.shields.io/pypi/pyversions/aioe621)

![GitHub License](https://img.shields.io/github/license/penggrin12/aioe621)
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/penggrin12/aioe621/release.yml)

A simple asynchronous httpx+pydantic wrapper over the E621's API

## Quickstart

```python
from aioe621 import Client, Auth
from aioe621.schemas import Post
import asyncio

auth = Auth(
    username="hexerade",
    api_key="1nHrmzmsvJf26EhU1F7CjnjC",
)

# all parameters are optional
client = Client(
    auth=auth,
    user_agent="MyProject/1.0 (by username on e621)"
)


async def main() -> None:
    post: Post = await client.posts.get(id=5937863)
    print(f"i love {post.tags.artist[0]}!!!")


asyncio.run(main())
```

## Currently implemented

- [x] `GET /posts.json` via `.posts.list`
- [x] `GET /posts/{id}.json` via `.posts.get`
- [x] `GET /posts/random.json` via `.posts.random`
