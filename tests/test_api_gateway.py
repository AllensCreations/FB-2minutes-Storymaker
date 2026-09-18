import json
import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
API_TRIGGER_JS = REPO_ROOT / "api" / "trigger.js"


class TestApiGatewayNode(unittest.TestCase):

    def run_node_eval(self, script: str) -> dict:
        full_code = f"""
        process.env.API_SECRET_KEY = process.env.API_SECRET_KEY || '';
        process.env.GH_PAT = process.env.GH_PAT || 'mock_gh_token';
        process.env.GITHUB_REPOSITORY = process.env.GITHUB_REPOSITORY || 'AllensCreations/FB-2minutes-Storymaker';

        global.fetch = async (url, opts) => ({{
            status: 204,
            ok: true,
            text: async () => ''
        }});

        import('{API_TRIGGER_JS.as_uri()}').then(async (mod) => {{
            const handler = mod.default;
            const res = {{
                statusCode: 200,
                headers: {{}},
                setHeader(k, v) {{ this.headers[k] = v; }},
                status(c) {{ this.statusCode = c; return this; }},
                json(data) {{ this.body = data; return this; }},
                end() {{ return this; }}
            }};

            {script}
        }}).catch(err => {{
            console.error(err);
            process.exit(1);
        }});
        """
        proc = subprocess.run(
            ["node", "--input-type=module", "-e", full_code],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT)
        )
        if proc.returncode != 0:
            raise RuntimeError(f"Node execution failed:\n{proc.stderr}\n{proc.stdout}")
        return json.loads(proc.stdout.strip())

    def test_get_documentation(self):
        script = """
        const req = { method: 'GET', headers: {} };
        await handler(req, res);
        console.log(JSON.stringify(res.body));
        """
        body = self.run_node_eval(script)
        self.assertEqual(body.get("status"), "online")
        self.assertIn("endpoints", body)

    def test_post_unauthorized_when_secret_set(self):
        script = """
        process.env.API_SECRET_KEY = 'supersecret123';
        const req = {
            method: 'POST',
            headers: { 'x-api-key': 'wrong_key' },
            body: {}
        };
        await handler(req, res);
        console.log(JSON.stringify({ statusCode: res.statusCode, body: res.body }));
        """
        result = self.run_node_eval(script)
        self.assertEqual(result.get("statusCode"), 401)
        self.assertFalse(result.get("body", {}).get("ok"))
        self.assertIn("Unauthorized", result.get("body", {}).get("error", ""))

    def test_post_authorized_dispatches_successfully(self):
        script = """
        process.env.API_SECRET_KEY = 'mysecret';
        const req = {
            method: 'POST',
            headers: { 'x-api-key': 'mysecret' },
            body: {
                title: 'Story Title',
                description: 'Story Description',
                upload_date: '2026-09-20T18:00:00Z',
                script_text: 'Scene 1: Hi\\n(Next image)\\nScene 2: Bye',
                make_webhook_url: 'https://hook.make.com/123'
            }
        };
        await handler(req, res);
        console.log(JSON.stringify({ statusCode: res.statusCode, body: res.body }));
        """
        result = self.run_node_eval(script)
        self.assertEqual(result.get("statusCode"), 202)
        body = result.get("body", {})
        self.assertTrue(body.get("ok"))
        self.assertEqual(body.get("status"), "queued")
        self.assertEqual(body.get("scenes_detected"), 2)
        self.assertEqual(body.get("title"), "Story Title")

    def test_post_scenes_array_dispatches_with_image_urls(self):
        script = """
        process.env.API_SECRET_KEY = 'mysecret';
        const req = {
            method: 'POST',
            headers: { 'x-api-key': 'mysecret' },
            body: {
                title: 'Google Flow Story',
                description: 'Episode 1 #shorts',
                upload_date: '2026-09-20T18:00:00Z',
                audio_url: 'https://example.com/narration.mp3',
                scenes: [
                    { scene: 1, text: 'Intro', image_url: 'https://example.com/1.png' },
                    { scene: 2, text: 'Middle', image_url: 'https://example.com/2.png' },
                    { scene: 3, text: 'Outro', image_url: 'https://example.com/3.png' }
                ],
                make_webhook_url: 'https://hook.make.com/123'
            }
        };
        await handler(req, res);
        console.log(JSON.stringify({ statusCode: res.statusCode, body: res.body }));
        """
        result = self.run_node_eval(script)
        self.assertEqual(result.get("statusCode"), 202)
        body = result.get("body", {})
        self.assertTrue(body.get("ok"))
        self.assertEqual(body.get("status"), "queued")
        self.assertEqual(body.get("scenes_detected"), 3)
        self.assertEqual(body.get("title"), "Google Flow Story")


if __name__ == "__main__":
    unittest.main()
