# aioe621 ![GitHub Tag](https://img.shields.io/github/v/tag/penggrin12/aioe621?label=version)

![uv](https://img.shields.io/badge/uv-261230.svg?logo=uv&logoColor=#de5fe9)
![PyPI Python Version](https://img.shields.io/pypi/pyversions/aioe621)

![GitHub License](https://img.shields.io/github/license/penggrin12/aioe621)
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/penggrin12/aioe621/release.yml)

A simple asynchronous httpx+pydantic wrapper over the
[e621 API](https://e621.net/help/api).

The library API is considered unstable until version 1.0.0.
Minor releases may include breaking changes.

## Quickstart

```python
from aioe621 import Client
from aioe621.schemas.posts import Post
import asyncio

# a user agent is required
client = Client(user_agent="MyProject/1.0 (by username on e621)")


async def main() -> None:
    post: Post = await client.posts.get(5937863)
    print(f"i love {post.tags.artist[0]}!!!")


asyncio.run(main())
```

## Installation

```bash
pip install aioe621
```

or using uv (recommended):

```bash
uv add aioe621
```

## TagSet

`TagSet` is a small query-building helper around e621's tag syntax. It behaves mostly like a normal `set[str]`
(it actually inherits from actually `frozenset[Tag]`), but adds convenient methods for composing searches.

Using `TagSet` is not required. All endpoints that accept tags also work with other "Tag"-like or "Tag list"-like
types (including plain strings and iterables of strings). `TagSet` is provided as a convenience for building, combining,
and reusing complex queries.

### Build searches fluently

```python
# find posts by the same artists, but include a specific feature
query = post.tags.artist.with_tag("tail")
print(str(query))  # cool_artist tail
posts = await client.posts.list(tags=query)
```

### Exclude tags

Negated tags are useful for filtering out things you don't want:

```python
# with the same species, but no humans
# each list item here is like a blacklist line in e621
query = post.tags.species.with_blacklist(["human"])
# or you could just do .with_tag("-human")
```

Which for a post of a dog with a cat produces the equivalent of `canine feline -human`

### Combine tag groups

Tag groups can be merged together:

```python
# search for the characters of the specific artists and copyrights
query = post.tags.character + post.tags.species + post.tags.copyright
```

### Build reusable search presets

Because `TagSet` is composable, you can keep common searches around:

```python
from aioe621.objects import TagSet
from aioe621.enums import PostRating

anthro_pups_with_fangs = TagSet({"fangs", "canine", "-feral"})
rating = PostRating.SAFE  # just "s" or "safe" also works!

favorites = anthro_pups_with_fangs.with_rating(rating)
```

### All TagSet methods

| Method             | Purpose                                                 |
|--------------------|---------------------------------------------------------|
| `+`                | Combine tag groups                                      |
| `with_tag()`       | Add a tag                                               |
| `with_tags()`      | Add multiple tags                                       |
| `with_blacklist()` | Add and negate lists of TagSet, like the e621 blacklist |
| `negated_tags()`   | Negate tags                                             |
| `with_order()`     | Add search ordering                                     |
| `with_rating()`    | Add search rating                                       |
| `flattened()`      | Flatten into a `str`                                    |

## Schema helpers

Some schema objects provide small helper methods that use the attached client to
fetch related resources.

### Post

```python
# get posts that have this post as their parent
children: Sequence[Post] = await post.fetch_children()

# get the parent if it has one
parent: Post | None = await post.fetch_parent()
```

### Pool

```python
pool = await client.pools.get(12345)

# this is only the ids
print(pool.post_ids)  # [69420, 42069, ...]

# fetch the full Post objects
posts: list[Post] = await pool.fetch_posts()

print(posts[0].rating)  # PostRating.EXPLICIT
```

## Currently implemented API endpoints

| e621 API                      | aioe621                             |
|-------------------------------|-------------------------------------|
| `GET /posts.json`             | `.posts.list`                       |
| `GET /posts/{id}.json`        | `.posts.get`                        |
| `GET /posts/random.json`      | `.posts.random`                     |
| `GET /popular.json`           | `.posts.popular`                    |
| `GET /tags.json`              | `.tags.list` and `tags.get_by_name` |
| `GET /tags/{id}.json`         | `.tags.get`                         |
| `GET /pools.json`             | `.pools.list`                       |
| `GET /pools/{id}.json`        | `.pools.get`                        |
| `GET /forum_posts.json`       | `.forum.posts`                      |
| `GET /forum_posts/{id}.json`  | `.forum.post`                       |
| `GET /forum_topics.json`      | `.forum.topics`                     |
| `GET /forum_topics/{id}.json` | `.forum.topic`                      |

