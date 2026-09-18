/**
 * Vercel Serverless Function: API Gateway for Google Flow -> GitHub Actions
 * Endpoint: POST /api/trigger (also aliased by /api/render)
 *
 * Accepts story metadata (title, description, script, audio, images, upload time)
 * from Google Flow AI, validates security token, and dispatches GitHub Actions
 * workflow to render 1080x1920 video and notify Make.com.
 */

export default async function handler(req, res) {
  // 1. Handle CORS Preflight
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type, Authorization, x-api-key");

  if (req.method === "OPTIONS") {
    return res.status(200).end();
  }

  // 2. GET Documentation / Health Check
  if (req.method === "GET") {
    return res.status(200).json({
      service: "FB-2minutes Storymaker Vercel API Gateway",
      version: "2.0",
      status: "online",
      endpoints: {
        trigger: "POST /api/trigger",
        render: "POST /api/render"
      },
      description: "Automated API bridge connecting Google Flow AI -> GitHub Actions (FFmpeg 9:16 Video Render) -> Make.com (Auto Upload)",
      authentication: {
        header: "x-api-key: <YOUR_SECRET_KEY> or Authorization: Bearer <YOUR_SECRET_KEY>",
        env_var: "API_SECRET_KEY (Configure in Vercel project environment variables)"
      },
      expected_payload: {
        title: "The Secret of the Whispering Woods",
        description: "Episode 1: The journey begins #story #tiktok",
        upload_date: "2026-09-20T18:00:00Z",
        audio_url: "https://example.com/narration.mp3",
        images: [
          "https://example.com/scene_1.png",
          "https://example.com/scene_2.png"
        ],
        script: "Scene 1: Introduction...\n(Next image)\nScene 2: The Cave...",
        make_webhook_url: "https://hook.eu1.make.com/your-webhook-id"
      }
    });
  }

  if (req.method !== "POST") {
    return res.status(405).json({ ok: false, error: "Method Not Allowed. Use POST." });
  }

  // 3. Security: Bearer Secret Token / API Key Verification
  const requiredSecret = process.env.API_SECRET_KEY || process.env.API_KEY || "";
  if (requiredSecret) {
    const authHeader = req.headers["authorization"] || "";
    const apiKeyHeader = req.headers["x-api-key"] || "";
    let providedToken = apiKeyHeader;

    if (!providedToken && authHeader.startsWith("Bearer ")) {
      providedToken = authHeader.slice(7).trim();
    }

    if (!providedToken || providedToken !== requiredSecret) {
      return res.status(401).json({
        ok: false,
        error: "Unauthorized: Invalid or missing API key. Provide matching 'x-api-key' or 'Authorization: Bearer <token>' header."
      });
    }
  }

  // 4. Parse & Normalize Payload from Google Flow
  const body = typeof req.body === "string" ? JSON.parse(req.body || "{}") : (req.body || {});

  const title = body.title || "StoryShorts Video";
  const description = body.description || "";
  const scheduledTime = body.scheduled_time || body.upload_time || body.upload_date || body.date_time || "";
  const audioUrl = body.audio_url || body.audio || "";
  const audioBase64 = body.audio_base64 || "";
  const scenes = Array.isArray(body.scenes) ? body.scenes : [];
  const visualsUrl = body.visuals_url || body.visuals_zip_url || (Array.isArray(body.images) ? body.images[0] : (body.images || ""));
  const visualsBase64 = body.visuals_base64 || "";
  const scriptText = body.script_text || body.script || "";
  const makeWebhookUrl = body.make_webhook_url || body.webhook_url || "";

  // Calculate Scene Count for Detailed Response
  let sceneCount = 1;
  if (scenes.length > 0) {
    sceneCount = scenes.length;
  } else if (scriptText) {
    if (scriptText.includes("(Next image)")) {
      sceneCount = scriptText.split(/\(Next image\)/i).filter(s => s.trim().length > 0).length;
    } else {
      try {
        const parsed = JSON.parse(scriptText);
        if (Array.isArray(parsed)) sceneCount = parsed.length;
      } catch {
        sceneCount = scriptText.split("\n").filter(l => l.trim().length > 0).length || 1;
      }
    }
  } else if (Array.isArray(body.images) && body.images.length > 0) {
    sceneCount = body.images.length;
  }

  // 5. GitHub Configuration & Dispatch
  const githubToken = process.env.GH_PAT || process.env.GITHUB_TOKEN || process.env.GH_TOKEN || "";
  const githubRepo = process.env.GITHUB_REPOSITORY || "AllensCreations/FB-2minutes-Storymaker";

  if (!githubToken) {
    return res.status(500).json({
      ok: false,
      error: "GITHUB_TOKEN (or GH_PAT) is not configured in Vercel environment variables.",
      hint: "Add GH_PAT with repo scope in Vercel Project Settings -> Environment Variables."
    });
  }

  const dispatchUrl = `https://api.github.com/repos/${githubRepo}/dispatches`;
  const dispatchBody = {
    event_type: "generate-video",
    client_payload: {
      title,
      description,
      scheduled_time: scheduledTime,
      scenes: scenes,
      images: Array.isArray(body.images) ? body.images : [],
      visuals_url: visualsUrl,
      visuals_base64: visualsBase64,
      audio_url: audioUrl,
      audio_base64: audioBase64,
      script_text: scriptText,
      make_webhook_url: makeWebhookUrl
    }
  };

  try {
    const ghResponse = await fetch(dispatchUrl, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${githubToken}`,
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "FB-2minutes-Storymaker-Vercel-Gateway",
        "Content-Type": "application/json"
      },
      body: JSON.stringify(dispatchBody)
    });

    if (ghResponse.status !== 204 && !ghResponse.ok) {
      const errText = await ghResponse.text();
      return res.status(ghResponse.status).json({
        ok: false,
        error: `GitHub API dispatch failed (${ghResponse.status}): ${errText}`
      });
    }

    const jobId = `job_${Date.now()}_${Math.random().toString(36).substring(2, 8)}`;
    const actionsUrl = `https://github.com/${githubRepo}/actions`;

    // 6. Return Detailed Queued Confirmation (202 Accepted)
    return res.status(202).json({
      ok: true,
      status: "queued",
      job_id: jobId,
      title: title,
      scenes_detected: sceneCount,
      scheduled_for: scheduledTime || "immediate",
      audio_source: audioUrl ? "remote_url" : (audioBase64 ? "base64" : "demo_fallback"),
      visuals_source: visualsUrl ? "remote_url" : (visualsBase64 ? "base64" : "demo_fallback"),
      make_webhook_configured: Boolean(makeWebhookUrl),
      actions_url: actionsUrl,
      repository: githubRepo,
      timestamp: new Date().toISOString(),
      message: "Story video generation successfully queued in GitHub Actions. Make.com will receive the published video once rendering completes."
    });

  } catch (err) {
    return res.status(500).json({
      ok: false,
      error: `Failed to dispatch workflow: ${err.message || String(err)}`
    });
  }
}
