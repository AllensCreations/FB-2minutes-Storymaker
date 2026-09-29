"""
Unit tests for Items Queue Manager & API.
"""

import io
import json
import shutil
import tempfile
import unittest
import zipfile
from pathlib import Path

import sys
REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from items_manager import ItemsManager, parse_multipart_request


class TestItemsManager(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.manager = ItemsManager(items_dir=Path(self.temp_dir))

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_save_and_list_items(self):
        # Create a mock zip archive with a story.json and 2 image files
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            story = {
                "title": "Test Story Title",
                "description": "Test description",
                "scenes": [
                    {"scene": 1, "text": "Scene 1 text"},
                    {"scene": 2, "text": "Scene 2 text"}
                ]
            }
            zf.writestr("story.json", json.dumps(story))
            zf.writestr("01.png", b"IMAGE1")
            zf.writestr("02.png", b"IMAGE2")

        item = self.manager.save_zip_item(buf.getvalue(), filename="test.zip")
        self.assertEqual(item["title"], "Test Story Title")
        self.assertEqual(item["scene_count"], 2)
        self.assertEqual(len(item["images"]), 2)

        items = self.manager.list_items()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["id"], item["id"])

    def test_delete_item(self):
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("script.txt", "Scene 1: Hello\n(Next image)\nScene 2: World")
            zf.writestr("1.png", b"IMG")

        item = self.manager.save_zip_item(buf.getvalue(), filename="pkg.zip")
        self.assertEqual(len(self.manager.list_items()), 1)

        res = self.manager.delete_item(item["id"])
        self.assertTrue(res)
        self.assertEqual(len(self.manager.list_items()), 0)

    def test_parse_multipart_request(self):
        headers = {"Content-Type": "multipart/form-data; boundary=X123"}
        body = (
            b"--X123\r\n"
            b'Content-Disposition: form-data; name="file"; filename="test.zip"\r\n'
            b"Content-Type: application/zip\r\n\r\n"
            b"ZIP_BYTES_MOCK\r\n"
            b"--X123--\r\n"
        )
        fields, files = parse_multipart_request(headers, body)
        self.assertIn("file", files)
        self.assertEqual(files["file"]["filename"], "test.zip")
        self.assertEqual(files["file"]["bytes"], b"ZIP_BYTES_MOCK")

    def test_image_only_zip_without_json(self):
        # Archive with only images and no JSON or TXT
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("01.png", b"IMAGE1")
            zf.writestr("02.png", b"IMAGE2")
            zf.writestr("03.png", b"IMAGE3")

        item = self.manager.save_zip_item(buf.getvalue(), filename="images_only.zip", title="Custom Title")
        self.assertEqual(item["title"], "Custom Title")
        self.assertEqual(item["scene_count"], 3)
        self.assertEqual(len(item["scenes"]), 3)
        self.assertIn("(Next image)", item["script_text"])
        self.assertEqual(item["scenes"][0]["scene"], 1)

    def test_save_images_item_directly(self):
        images = [
            ("01.png", b"IMAGE_BYTES_1"),
            ("02.png", b"IMAGE_BYTES_2")
        ]
        item = self.manager.save_images_item(images, title="Direct Image Package")
        self.assertEqual(item["title"], "Direct Image Package")
        self.assertEqual(item["scene_count"], 2)
        self.assertEqual(len(item["images"]), 2)
        self.assertTrue(item["script_text"].startswith("Scene 1:"))

    def test_parse_multipart_multiple_files(self):
        headers = {"Content-Type": "multipart/form-data; boundary=B123"}
        body = (
            b"--B123\r\n"
            b'Content-Disposition: form-data; name="title"\r\n\r\n'
            b"My Story Title\r\n"
            b"--B123\r\n"
            b'Content-Disposition: form-data; name="file"; filename="01.png"\r\n'
            b"Content-Type: image/png\r\n\r\n"
            b"PNG1\r\n"
            b"--B123\r\n"
            b'Content-Disposition: form-data; name="file"; filename="02.png"\r\n'
            b"Content-Type: image/png\r\n\r\n"
            b"PNG2\r\n"
            b"--B123--\r\n"
        )
        fields, files = parse_multipart_request(headers, body)
        self.assertEqual(fields.get("title"), "My Story Title")
        self.assertIn("_list", files)
        self.assertEqual(len(files["_list"]), 2)
        self.assertEqual(files["_list"][0]["filename"], "01.png")
        self.assertEqual(files["_list"][1]["filename"], "02.png")

    def test_parse_user_reference_json_schema(self):
        user_json = {
            "Title": "The 'Validation' Addiction",
            "Caption": "What if the applause you are chasing is actually keeping you a prisoner? 🎭",
            "Description": "Stop performing for an audience that doesn't care. Build a life for yourself.",
            "script": [
                {
                    "scene_number": 0,
                    "scene_type": "illustration",
                    "visual_style_tag": "illustration",
                    "aspect_ratio": "1:1",
                    "narration": "What if the reason you are always exhausted is because you are spending all your energy performing?",
                    "prompt_description": "A low-angle shot of a stickman figure dancing on a stage."
                },
                {
                    "scene_number": 1,
                    "scene_type": "infograph",
                    "visual_style_tag": "infograph",
                    "aspect_ratio": "1:1",
                    "narration": "This is The Validation Trap, explained by Tobi.",
                    "prompt_description": "A minimalist chart showing a stickman figure."
                }
            ]
        }
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("story.json", json.dumps(user_json))
            zf.writestr("0.png", b"IMG0")
            zf.writestr("1.png", b"IMG1")

        item = self.manager.save_zip_item(buf.getvalue(), filename="validation.zip")
        self.assertEqual(item["title"], "The 'Validation' Addiction")
        self.assertIn("applause", item["caption"])
        self.assertEqual(item["aspect_ratio"], "1:1")
        self.assertEqual(item["scene_count"], 2)
        self.assertIn("What if the reason", item["script_text"])
        self.assertIn("This is The Validation Trap", item["script_text"])
        # Ensure no 'Scene X:' numbers in the clean extracted script
        self.assertNotIn("Scene 0:", item["script_text"])

    def test_mark_publish_complete(self):
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("01.png", b"IMG")

        item = self.manager.save_zip_item(buf.getvalue(), filename="pkg.zip")
        self.assertFalse(item.get("published_complete", False))

        # Mark complete
        updated = self.manager.mark_publish_complete(item["id"], True)
        self.assertTrue(updated["published_complete"])

        # Re-fetch from index
        fetched = self.manager.get_item(item["id"])
        self.assertTrue(fetched["published_complete"])

        # Revert
        reverted = self.manager.mark_publish_complete(item["id"], False)
        self.assertFalse(reverted["published_complete"])

    def test_update_item_package_in_place(self):
        # 1. Create initial item with 2 images
        buf1 = io.BytesIO()
        with zipfile.ZipFile(buf1, "w") as zf:
            zf.writestr("story.json", json.dumps({"title": "Original Story", "scenes": [{"text": "Original Scene 1"}]}))
            zf.writestr("01.png", b"OLD_IMG_1")
            zf.writestr("voiceover.wav", b"AUDIO_WAV_BYTES")

        item1 = self.manager.save_zip_item(buf1.getvalue(), filename="orig.zip")
        orig_id = item1["id"]
        self.assertEqual(item1["title"], "Original Story")
        self.assertEqual(item1["audio_status"], "ready")

        # 2. Update with new zip (3 images, updated script, no audio -> should preserve audio!)
        buf2 = io.BytesIO()
        with zipfile.ZipFile(buf2, "w") as zf:
            zf.writestr("story.json", json.dumps({"title": "Updated Story", "scenes": [{"text": "New 1"}, {"text": "New 2"}, {"text": "New 3"}]}))
            zf.writestr("01.png", b"NEW_IMG_1")
            zf.writestr("02.png", b"NEW_IMG_2")
            zf.writestr("03.png", b"NEW_IMG_3")

        updated_item = self.manager.update_item(orig_id, buf2.getvalue(), filename="updated.zip")
        self.assertIsNotNone(updated_item)
        self.assertEqual(updated_item["id"], orig_id)
        self.assertEqual(updated_item["title"], "Updated Story")
        self.assertEqual(updated_item["scene_count"], 3)
        self.assertEqual(len(updated_item["images"]), 3)
        # Audio was preserved!
        self.assertEqual(updated_item["audio_status"], "ready")
        self.assertEqual(updated_item["audio_file"], "voiceover.wav")

        # Index item count is still 1 (not duplicated)
        all_items = self.manager.list_items()
        self.assertEqual(len(all_items), 1)
        self.assertEqual(all_items[0]["title"], "Updated Story")

    def test_find_item_by_title_or_id(self):
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("story.json", json.dumps({"title": "The Comfort Zone Cage", "scenes": [{"text": "Scene 1"}]}))
            zf.writestr("01.png", b"IMG")

        item = self.manager.save_zip_item(buf.getvalue(), filename="comfort.zip")

        # Find by ID
        self.assertIsNotNone(self.manager.find_item_by_title_or_id(item["id"]))
        # Find by exact title
        self.assertIsNotNone(self.manager.find_item_by_title_or_id("The Comfort Zone Cage"))
        # Find by lowercase
        self.assertIsNotNone(self.manager.find_item_by_title_or_id("the comfort zone cage"))
        # Find by slug
        self.assertIsNotNone(self.manager.find_item_by_title_or_id("the_comfort_zone_cage"))

    def test_update_metadata_and_social_locking(self):
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("story.json", json.dumps({"title": "Initial Title", "scenes": [{"text": "S1"}]}))
            zf.writestr("01.png", b"IMG")

        item = self.manager.save_zip_item(buf.getvalue(), filename="test_lock.zip")
        item_id = item["id"]

        # 1. Edit metadata freely when neither FB nor YT is published
        res1 = self.manager.update_metadata(item_id, title="Edited Title", caption="New Caption", description="New Desc")
        self.assertIsNotNone(res1)
        self.assertEqual(res1["title"], "Edited Title")
        self.assertEqual(res1["caption"], "New Caption")
        self.assertEqual(res1["description"], "New Desc")

        # 2. Mark published on Facebook
        res2 = self.manager.update_metadata(item_id, fb_published=True)
        self.assertTrue(res2["fb_published"])

        # 3. Try editing title when FB is published -> should be LOCKED
        res3 = self.manager.update_metadata(item_id, title="Illegal Title Edit")
        self.assertIn("error", res3)
        self.assertTrue(res3.get("locked"))

        # 4. Item remains unchanged
        curr = self.manager.get_item(item_id)
        self.assertEqual(curr["title"], "Edited Title")

        # 5. Unlock override allows edit
        res4 = self.manager.update_metadata(item_id, title="Unlocked Title", unlock=True)
        self.assertEqual(res4["title"], "Unlocked Title")


if __name__ == "__main__":
    unittest.main()


