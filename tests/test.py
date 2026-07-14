import unittest
from unittest.mock import MagicMock, patch

from aioe621 import Auth, Client
from aioe621.schemas import Post

MOCK_POST_JSON = '{"post":{"id":4842101,"created_at":"2024-06-10T10:52:11.177+03:00","updated_at":"2026-07-14T02:31:17.553+03:00","file":{"width":380,"height":380,"ext":"png","size":113245,"md5":"1610e96ca2e0af6b7c5e06b03cda83c8","url":"https://static1.e621.net/data/16/10/1610e96ca2e0af6b7c5e06b03cda83c8.png"},"preview":{"width":256,"height":256,"url":"https://static1.e621.net/data/preview/16/10/1610e96ca2e0af6b7c5e06b03cda83c8.jpg","alt":"https://static1.e621.net/data/preview/16/10/1610e96ca2e0af6b7c5e06b03cda83c8.webp"},"sample":{"has":false,"width":380,"height":380,"url":null,"alt":null,"alternates":{}},"score":{"up":3805,"down":-33,"total":3772},"tags":{"general":["ambiguous_gender","black_eyes","eye_bags","feral","fur","half-closed_eyes","humor","looking_at_viewer","narrowed_eyes","papyrus_(font)","pink_background","pink_nose","quadruped","shitpost","simple_background","solo","sparkles","text","the_truth","tired_eyes","white_body","white_fur"],"artist":["akeivi"],"contributor":[],"copyright":[],"character":["cansado_(akeivi)"],"species":["domestic_cat","felid","feline","felis","mammal"],"invalid":[],"meta":["1:1","2024","aliasing","digital_media_(artwork)","english_text","lol_comments","low_res","meme","reaction_image","rotoscoping"],"lore":[]},"locked_tags":[],"change_seq":77116893,"flags":{"pending":false,"flagged":false,"note_locked":false,"status_locked":false,"rating_locked":false,"deleted":false},"rating":"s","fav_count":4526,"sources":["https://x.com/akeivi_official/status/1799453243799666869","https://pbs.twimg.com/media/GPjxL0mXgAAsaEt?format=png&name=orig"],"pools":[],"relationships":{"parent_id":null,"has_children":false,"has_active_children":false,"children":[]},"approver_id":45665,"uploader_id":1349007,"uploader_name":"keysmasher123","description":"me fr","comment_count":93,"is_favorited":false,"vote":0,"has_notes":false,"duration":null}}'
MOCK_USERNAME, MOCK_API_KEY = "coolUsername", "coolApiKey"


class MyTestCase(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.auth = Auth(MOCK_USERNAME, MOCK_API_KEY)
        self.client = Client(auth=self.auth)

    async def test_auth(self) -> None:
        auth = Auth(MOCK_USERNAME, MOCK_API_KEY)
        self.assertEqual(auth.username, MOCK_USERNAME)
        self.assertEqual(auth.api_key, MOCK_API_KEY)

    async def test_client_init(self) -> None:
        self.assertEqual(self.client.auth, self.auth)
        self.assertEqual(self.client.session.base_url, self.client.E621_BASE_URL)

    @patch("httpx.AsyncClient.request")
    async def test_posts_get(self, mock_request) -> None:
        mock_response = MagicMock()
        mock_response.text = MOCK_POST_JSON
        mock_request.return_value = mock_response

        post = await self.client.posts.get(id=4842101)
        self.assertIsInstance(post, Post)
        self.assertEqual(post.id, 4842101)
        self.assertEqual(post.file.ext, "png")
        self.assertEqual(post.file.size, 113245)
        self.assertEqual(post.score.down, -33)
        self.assertIn("akeivi", post.tags.artist)
        self.assertEqual(post.description, "me fr")

    async def asyncTearDown(self) -> None:
        await self.client.session.aclose()


if __name__ == "__main__":
    unittest.main()
