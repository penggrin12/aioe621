import base64
import unittest
from typing import Sequence

import httpx
import respx
from pydantic import ValidationError

from aioe621 import Auth, Client
from aioe621.enums import PoolCategory
from aioe621.exceptions import NotFoundError
from aioe621.objects import TagSet
from aioe621.schemas.pools import Pool
from aioe621.schemas.posts import Post, PostRating
from aioe621.schemas.tags import RelatedTag, Tag

MOCK_POST_JSON = '{"id":6543578,"created_at":"2026-07-13T17:36:26.837+03:00","updated_at":"2026-07-15T02:29:27.631+03:00","change_seq":78095660,"files":{"meta":{"md5":"077e4bbffe0ea5d5acb0fca479de8fdd","ext":"png","size":36622,"duration":null,"has_sample":true},"original":{"width":1745,"height":1698,"url":"https://static1.e621.net/data/07/7e/077e4bbffe0ea5d5acb0fca479de8fdd.png"},"preview":{"width":263,"height":256,"jpg":"https://static1.e621.net/data/preview/07/7e/077e4bbffe0ea5d5acb0fca479de8fdd.jpg","webp":"https://static1.e621.net/data/preview/07/7e/077e4bbffe0ea5d5acb0fca479de8fdd.webp"},"sample":{"width":874,"height":850,"jpg":"https://static1.e621.net/data/sample/07/7e/077e4bbffe0ea5d5acb0fca479de8fdd.jpg","webp":"https://static1.e621.net/data/sample/07/7e/077e4bbffe0ea5d5acb0fca479de8fdd.webp"}},"uploader_id":94865,"uploader_name":"Strikerman","approver_id":null,"stats":{"score":{"up":35,"down":-1,"total":34},"fav_count":36,"is_favorited":false,"vote":0,"comment_count":1,"hotness":4131.053207706494},"flags":{"pending":false,"flagged":false,"note_locked":false,"status_locked":false,"rating_locked":false,"deleted":false},"has":{"parent":true,"children":false,"active_children":false,"notes":false,"sample":true},"relationships":{"parent_id":6543578,"children":[]},"pools":[],"rating":"s","locked_tags":[],"sources":["https://x.com/DalueArt/status/2076512463059894388","https://pbs.twimg.com/media/HNFBBh6aUAA4DA5?format=png&name=orig"],"description":"The secret 3rd option","tags":{"general":["anthro","anthro_on_anthro","bedroom_eyes","black_collar","black_eyes","black_nose","blue_eyes","blush","bodily_fluids","collar","duo","emanata","exposed_shoulder","eye_contact","floppy_ears","grin","half-closed_eyes","hand_on_chest","heart_symbol","intraspecies","looking_at_another","male","male/male","narrowed_eyes","nervous","nervous_smile","pupils","seductive","selfcest","side_view","simple_background","smile","square_crossover","surprised","sweat","white_background"],"artist":["dalueart"],"contributor":[],"copyright":[],"character":["dalue_(dalueart)"],"species":["canid","canine","canis","domestic_dog","mammal"],"invalid":[],"meta":["hi_res"],"lore":[]}}'
MOCK_POSTS_JSON = f"[{MOCK_POST_JSON}]"
MOCK_TAG_JSON = '{"id":1068,"name":"canine","post_count":1611254,"related_tags":"canid 300 canine 300 mammal 300 anthro 257 hi_res 208 male 206 fur 175 canis 174 genitals 168 female 160 clothing 134 solo 127 duo 126 hair 119 penis 113 tail 110 breasts 107 bodily_fluids 105 nude 95 text 95 digital_media_(artwork) 93 nipples 92 wolf 91 fox 89 balls 85","related_tags_updated_at":"2026-07-08T07:00:44.477-04:00","category":5,"is_locked":false,"created_at":"2020-03-05T05:49:37.994-05:00","updated_at":"2026-07-08T07:00:44.477-04:00"}'
MOCK_TAGS_JSON = f"[{MOCK_TAG_JSON}]"
MOCK_POOL_JSON = '{"id":36878,"name":"TinyGayPirate_-_Random-word-tober","created_at":"2023-10-09T07:35:14.029+03:00","updated_at":"2025-07-01T20:29:27.857+03:00","creator_id":277038,"description":"The list so far:\\r\\n1. proper\\r\\n2. frost\\r\\n3. tribe\\r\\n4. bus\\r\\n5. rugby\\r\\n6. domestic\\r\\n7. glide\\r\\n8. rifle\\r\\n9. feeling\\r\\n10. regular\\r\\n11. swear\\r\\n12. crowd\\r\\n13. available","is_active":true,"category":"collection","post_ids":[4341598],"creator_name":"g273435d","post_count":1}'
MOCK_POOLS_JSON = f"[{MOCK_POOL_JSON}]"

MOCK_404_JSON = '{"success":false,"reason":"not found"}'

MOCK_USERAGENT = "mock useragent/1.0"
MOCK_USERNAME, MOCK_API_KEY = "coolUsername", "coolApiKey"
MOCK_AUTHORIZATION_HEADER = "Basic " + base64.b64encode(
    f"{MOCK_USERNAME}:{MOCK_API_KEY}".encode(encoding="utf-8")
).decode(encoding="utf-8")


class MyTestCase(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.auth = Auth(MOCK_USERNAME, MOCK_API_KEY)
        self.client = Client(user_agent=MOCK_USERAGENT, auth=self.auth)

    def test_auth(self) -> None:
        auth = Auth(MOCK_USERNAME, MOCK_API_KEY)
        self.assertEqual(auth.username, MOCK_USERNAME)
        self.assertEqual(auth.api_key, MOCK_API_KEY)

    def test_client_init(self) -> None:
        self.assertEqual(self.client.user_agent, MOCK_USERAGENT)
        self.assertEqual(self.client.auth, self.auth)
        self.assertEqual(self.client.session.base_url, self.client.E621_BASE_URL)

    def test_client_auth(self) -> None:
        self.assertIsNotNone(self.client.session.auth)
        resp = next(self.client.session.auth.auth_flow(httpx.Request("", "")))
        self.assertEqual(resp.headers["Authorization"], MOCK_AUTHORIZATION_HEADER)

    # posts

    @respx.mock
    async def test_posts_list(self) -> None:
        route = respx.get(f"{self.client.E621_BASE_URL}/posts.json").mock(
            return_value=httpx.Response(200, text=MOCK_POSTS_JSON)
        )

        posts = await self.client.posts.list(tags="nervous", limit=1)

        self.assertTrue(route.called)
        request = route.calls.last.request
        self.assertEqual(request.headers.get("User-Agent"), MOCK_USERAGENT)

        self.assertIsInstance(posts, Sequence)
        self.assertNotIsInstance(posts, str)
        self.assertEqual(len(posts), 1)

        post = posts[0]
        self.assertIsInstance(post, Post)
        self.assertEqual(post.id, 6543578)
        self.assertEqual(post.files.meta.ext, "png")
        self.assertEqual(post.files.meta.size, 36622)
        self.assertEqual(post.stats.score.up, 35)
        self.assertIsInstance(post.tags.artist, TagSet)
        self.assertNotIsInstance(post.tags.artist, str)
        self.assertIn("dalueart", post.tags.artist)
        self.assertEqual(post.description, "The secret 3rd option")
        self.assertEqual(post.rating, PostRating.SAFE)

    @respx.mock
    async def test_posts_get(self) -> None:
        respx.get(f"{self.client.E621_BASE_URL}/posts/6543578.json").mock(
            return_value=httpx.Response(200, text=MOCK_POST_JSON)
        )
        post = await self.client.posts.get(id=6543578)

        self.assertIsInstance(post, Post)
        self.assertEqual(post.id, 6543578)

    @respx.mock
    async def test_posts_random(self) -> None:
        respx.get(f"{self.client.E621_BASE_URL}/posts/random.json").mock(
            return_value=httpx.Response(200, text=MOCK_POST_JSON)
        )
        post = await self.client.posts.random()

        self.assertIsInstance(post, Post)
        self.assertEqual(post.id, 6543578)

    @respx.mock
    async def test_posts_get_immutability(self) -> None:
        respx.get(f"{self.client.E621_BASE_URL}/posts/6543578.json").mock(
            return_value=httpx.Response(200, text=MOCK_POST_JSON)
        )

        post = await self.client.posts.get(id=6543578)

        with self.assertRaises(ValidationError):
            # pyrefly: ignore [read-only]
            post.id = 0

    @respx.mock
    async def test_posts_get_404(self) -> None:
        status_code, method = 404, "GET"

        url = f"{self.client.E621_BASE_URL}/posts/999999999.json"
        route = respx.request(method, url).mock(
            return_value=httpx.Response(status_code, text=MOCK_404_JSON)
        )

        with self.assertRaises(NotFoundError) as cm:
            await self.client.posts.get(id=999999999)

        self.assertTrue(route.called)
        self.assertIn(str(status_code), str(cm.exception))
        self.assertIn(f"{method} {url}", str(cm.exception))

    @respx.mock
    async def test_posts_get_invalid_id(self) -> None:
        with self.assertRaises(ValueError):
            await self.client.posts.get(id=-10)

        self.assertEqual(len(respx.calls), 0)

    @respx.mock
    async def test_posts_fetch_stuff(self) -> None:
        url = f"{self.client.E621_BASE_URL}/posts/6543578.json"
        respx.get(url).mock(return_value=httpx.Response(200, text=MOCK_POST_JSON))

        # the og post parent is not actually the same
        # but it's easier to mock this way
        post = await self.client.posts.get(id=6543578)
        self.assertEqual(await post.fetch_parent(), post)

    # tags

    @respx.mock
    async def test_tags_list(self) -> None:
        respx.get(f"{self.client.E621_BASE_URL}/tags.json").mock(
            return_value=httpx.Response(200, text=MOCK_TAGS_JSON)
        )
        tags = await self.client.tags.list(query="canine", limit=1)

        self.assertIsInstance(tags, Sequence)
        self.assertNotIsInstance(tags, str)
        self.assertEqual(len(tags), 1)

        tag = tags[0]
        self.assertIsInstance(tag, Tag)

        self.assertEqual(tag.id, 1068)
        self.assertEqual(tag.name, "canine")
        self.assertEqual(tag.post_count, 1611254)
        self.assertIsInstance(tag.related_tags, Sequence)
        self.assertNotIsInstance(tag.related_tags, str)
        self.assertEqual(len(tag.related_tags), 25)
        self.assertEqual(tag.related_tags[24], RelatedTag(name="balls", relatedness=85))

    @respx.mock
    async def test_tags_get(self) -> None:
        respx.get(f"{self.client.E621_BASE_URL}/tags/1068.json").mock(
            return_value=httpx.Response(200, text=MOCK_TAG_JSON)
        )
        tag = await self.client.tags.get(id=1068)

        self.assertIsInstance(tag, Tag)
        self.assertEqual(tag.name, "canine")

    @respx.mock
    async def test_tags_get_by_name(self) -> None:
        respx.get(f"{self.client.E621_BASE_URL}/tags.json").mock(
            return_value=httpx.Response(200, text=MOCK_TAGS_JSON)
        )
        tag = await self.client.tags.get_by_name("canine")

        self.assertIsInstance(tag, Tag)
        self.assertEqual(tag.id, 1068)

    # pools

    @respx.mock
    async def test_pools_list(self) -> None:
        route = respx.get(f"{self.client.E621_BASE_URL}/pools.json").mock(
            return_value=httpx.Response(200, text=MOCK_POOLS_JSON)
        )

        pools = await self.client.pools.list(
            name="TinyGayPirate_-_Random-word-tober", limit=1
        )

        self.assertTrue(route.called)
        self.assertIsInstance(pools, Sequence)
        self.assertNotIsInstance(pools, str)
        self.assertEqual(len(pools), 1)

        pool = pools[0]
        self.assertIsInstance(pool, Pool)
        self.assertEqual(pool.id, 36878)
        self.assertEqual(pool.name, "TinyGayPirate_-_Random-word-tober")
        self.assertEqual(pool.post_count, 1)
        self.assertEqual(pool.category, PoolCategory.COLLECTION)
        self.assertEqual(list(pool.post_ids), [4341598])

    @respx.mock
    async def test_pools_list_invalid_args(self) -> None:
        # Pools endpoint requires at least id, name, or description
        with self.assertRaises(ValueError) as cm:
            await self.client.pools.list(limit=10)

        self.assertEqual(
            str(cm.exception), "Either id or name or description is required."
        )
        self.assertEqual(len(respx.calls), 0)

    @respx.mock
    async def test_pools_list_invalid_id(self) -> None:
        with self.assertRaises(ValueError) as cm:
            await self.client.pools.list(id=-5)

        self.assertEqual(
            str(cm.exception), "The pool ID must not be less than or equal to zero."
        )
        self.assertEqual(len(respx.calls), 0)

    @respx.mock
    async def test_pools_get(self) -> None:
        respx.get(f"{self.client.E621_BASE_URL}/pools/36878.json").mock(
            return_value=httpx.Response(200, text=MOCK_POOL_JSON)
        )
        pool = await self.client.pools.get(id=36878)

        self.assertIsInstance(pool, Pool)
        self.assertEqual(pool.id, 36878)
        self.assertEqual(pool.name, "TinyGayPirate_-_Random-word-tober")

    @respx.mock
    async def test_pools_get_invalid_id(self) -> None:
        with self.assertRaises(ValueError) as cm:
            await self.client.pools.get(id=0)

        self.assertEqual(
            str(cm.exception), "The pool ID must not be less than or equal to zero."
        )
        self.assertEqual(len(respx.calls), 0)

    @respx.mock
    async def test_pools_fetch_posts(self) -> None:
        respx.get(f"{self.client.E621_BASE_URL}/pools/36878.json").mock(
            return_value=httpx.Response(200, text=MOCK_POOL_JSON)
        )
        posts_route = respx.get(f"{self.client.E621_BASE_URL}/posts.json").mock(
            return_value=httpx.Response(200, text=MOCK_POSTS_JSON)
        )

        pool = await self.client.pools.get(id=36878)
        posts = await pool.fetch_posts()

        self.assertTrue(posts_route.called)
        self.assertIn("tags=pool%3A36878", str(posts_route.calls.last.request.url))

        self.assertIsInstance(posts, Sequence)
        self.assertEqual(len(posts), 1)
        self.assertIsInstance(posts[0], Post)
        self.assertEqual(posts[0].id, 6543578)

    async def asyncTearDown(self) -> None:
        await self.client.session.aclose()


if __name__ == "__main__":
    unittest.main()
