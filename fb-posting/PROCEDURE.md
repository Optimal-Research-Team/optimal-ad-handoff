# Posting to the Optimal Health Clinic Facebook Page (Meta Business Suite)

These steps were tested on Oct 28, 2026: post 1 (C5, photos) and post 2 (L8, reel) went up this way.
The manifest is `manifest.json` next to this file. It lists posts in order, each with `kind` (photos | video), `files`, `cover` and `caption`. The captions are already Facebook-ready: "link in bio" has been swapped for a real link.

## Rules

- **Facebook Page only.** Always untick the Instagram account (beoptimal.ca) in "Post to".
- **No AI label, ever.** Meta Business Suite shows no AI toggle in these flows. If one ever appears, leave it OFF.
- **Never** delete or edit an existing post, change Page settings, choose "Stop sharing all posts", add music, or boost.
- **Sign-in prompts.** If Meta asks you to confirm your identity or sign in (for example "Use Google to confirm it's you"), close it with its X. Never click Continue or enter anything. If you can't continue without signing in, stop and report.
- **Leave-site dialogs.** If a "Leave site?" dialog blocks navigation between posts, navigate with `force: true` (it only discards an unpublished draft).
- **Record progress.** After each post is published, set that post's `status` to "posted" and `fb_note` to the time in `manifest.json`, so a restart never double-posts. Skip any post whose status is already "posted".
- **Stop and report** if anything looks wrong: an upload fails, the caption is garbled, the preview shows the wrong media, or there's an error banner.

## File-picker hook (run first on every composer page load)

The upload buttons open a native file dialog you can't use. Run this in the page first. It catches the file input so `file_upload` can fill it:

```js
if (!window.__claudeFileHook) { window.__claudeFileHook = true; const orig = HTMLInputElement.prototype.click;
  HTMLInputElement.prototype.click = function () { if (this.type === 'file') {
    this.id = 'claude-file-input-' + (this.accept.includes('image') && !this.accept.includes('video') ? 'img' : 'any');
    this.setAttribute('aria-label', 'claude file input'); if (!this.isConnected) { this.style.display = 'none'; document.body.appendChild(this); } return; }
    return orig.apply(this, arguments); }; }
```

After clicking an upload button, use `find` with "claude file input" to get the ref, then `file_upload` with the absolute paths. Stay under 10 MB per call; every manifest file is already under it.

## Photos (kind = "photos"): Create post

1. Navigate to `https://business.facebook.com/latest/composer/?asset_id=338188682707707&business_id=7507562662631570`, wait about 5 s, then run the hook.
2. **Post to.** Click the "Post to" dropdown (it reads "Optimal Health Clinic and beoptimal.ca"). Use `find` for the "beoptimal.ca" checkbox option, click it to untick, then press Escape. Check that the field now reads only "Optimal Health Clinic".
3. **Images.** Click "Add photo/video", find "claude file input", and `file_upload` all of the post's images in manifest order. Wait about 4 s until the image rows appear.
4. **Caption.** Click the Text box and type the caption with ONE TRAILING SPACE added after the last hashtag. Without that space, the hashtag suggestion popup can swallow the last hashtag.
5. **Check the caption.** Run `document.querySelector('[contenteditable=true]').innerText`. Blank lines show up tripled, which is normal. If the end is wrong: click at the end of the hashtag line, press End, Backspace the broken part, and retype it with a trailing space. Don't move the caret with JavaScript; it scrambles the editor.
6. **Publish.** Click "Publish", wait about 6 s, and dismiss "Are there more posts…?" with "Maybe later".

## Videos (kind = "video"): Create reel

1. Navigate to `https://business.facebook.com/latest/reels_composer/?asset_id=338188682707707&business_id=7507562662631570`, wait about 5 s, then run the hook.
2. **Post to.** Same as photos: untick beoptimal.ca, press Escape, and check it reads "Optimal Health Clinic".
3. **Video.** Click "Add Video", find "claude file input", `file_upload` the video, and wait until it shows 100% (about 8–10 s).
4. **Caption.** Use `find` for the Description editable box, click it, and type the caption plus a trailing space. Check the end as in photos step 5.
5. **Thumbnail** (when `cover` is set).
   - In "Thumbnail", click the "Upload image" tab, then the blue "Upload image" link on the right.
   - Run `document.getElementById('claude-file-input-img').setAttribute('aria-label','claude thumbnail input')`.
   - `find` "claude thumbnail input" and `file_upload` the cover.
   - Check that "Change image" and the thumbnail appear.
   - When there's no cover (IG17, IG18), leave "Choose suggested".
6. **Edit step.** Click "Next". Add no music and leave Audio Optimizations unticked.
7. **Share step.** Click "Next", then:
   - **Closed captions:** untick it. It says "Auto-generated captions on", and our captions are burned in.
   - **Share to · Facebook story:** turn the toggle off. In the dialog, keep "Don't share this post" selected and click Confirm. Never pick "Stop sharing all posts".
   - **Who can see this?:** leave it on Public.
8. **Share.** Click "Share" (bottom right). When "Reel processing" appears, click Done.

## After the last post

Open `https://www.facebook.com/profile.php?id=61560306810907` and check the new posts and reels are there with their captions. Report what's done, and anything skipped or wrong.
