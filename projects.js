/* ============================================================
   YOUR PROJECTS — the only file to edit to add one.

   1. Copy the template block below (from { to },).
   2. Paste it inside the PROJECTS square brackets, remove the // at
      the start of each line, and fill it in.
   3. Save and refresh the page. Nothing to build, nothing to submit.

   A project appears on the projects page (work/index.html) and, if it
   is one of the first six listed, in the drawer on the cover page.
   Only `title` is required; leave out anything you don't have.
   List projects newest first — that is the order they show in.

   PHOTOS  put the images in assets/projects/ (about 1200 × 750, .webp or
           .jpg) and list them in `images`. The first is the card's cover;
           all of them appear in the gallery.
   VIDEO   `video` can be a YouTube or Vimeo link, or a video file of your
           own (.mp4 or .webm, in assets/projects/). Either plays inside
           the gallery. Any other link becomes a "watch the video" link.
   ============================================================ */


window.PROJECTS = [

  // {
  //   title:   "Project name",
  //   kind:    "Wagtail CMS",           // Wagtail CMS, Django, Frontend, Integrations, AWS, Takeover or Other
  //   summary: "One or two sentences: what it is, and what the demo shows.",
  //   stack:   ["Wagtail", "Django", "PostgreSQL"],
  //   year:    2026,
  //   images:  ["assets/projects/name-1.webp", "assets/projects/name-2.webp"],
  //   video:   "https://www.youtube.com/watch?v=…",   // or "assets/projects/name.mp4"
  //   demo:    "https://example.com",   // live demo link — optional
  //   demoLabel: "View demo",            // the words on that button — optional
  //   source:  "https://github.com/…",  // source code link — optional
  //   page:    "",                      // a longer write-up page or PDF — optional
  //   pageLabel: "read the write-up",    // the words on that link — optional
  //   credit:  ""                       // a small note under it in the gallery — optional
  // },

  {
    title:   "ProjectIMS — QA & Document Control",
    kind:    "Django",
    summary: "A custom web application that runs engineering projects through quality assurance, from templated checklists and PIN-verified phase sign-off to controlled drawing issue and client share links. Built in Django, it replaces a legacy PHP system with one audited source of truth.",
    stack:   ["Python", "Django", "PostgreSQL", "HTMX", "Alpine.js", "Playwright"],
    year:    2026,
    images:  [
      "assets/projects/projectims/cover.webp",
      "assets/projects/projectims/01-dashboard.webp",
      "assets/projects/projectims/02-checklist.webp",
      "assets/projects/projectims/03-signoff.webp",
      "assets/projects/projectims/04-transmittal.webp",
      "assets/projects/projectims/05-reports.webp",
      "assets/projects/projectims/06-client.webp"
    ],
    video:   "https://www.youtube.com/watch?v=GLcMxrO0tkk",
    page:    "assets/projects/projectims/ProjectIMS-System-Documentation.pdf",
    pageLabel: "read the system documentation (PDF)",
    credit:  "9 modules, 35 data models, 69 routes and 342 automated tests. All data shown is fictional and the client is not named. Live demo coming soon."
  },

  {
    title:   "Dr. Parchi — Clinic Software That Works Offline",
    kind:    "Full-stack",
    summary: "A clinic management system for Indian clinics that keeps working without internet. Reception, the doctor, the waiting-room display and the owner's phone each keep the day on the device and sync automatically, and medical records never reach the reception computer.",
    stack:   ["TypeScript", "React", "PowerSync", "PostgreSQL", "Fastify", "Electron", "Vitest"],
    year:    2026,
    images:  [
      "assets/projects/drparchi/cover.webp",
      "assets/projects/drparchi/01-front-desk.webp",
      "assets/projects/drparchi/02-consultation.webp",
      "assets/projects/drparchi/03-waiting-room.webp",
      "assets/projects/drparchi/04-billing.webp",
      "assets/projects/drparchi/05-safe-commands.webp",
      "assets/projects/drparchi/06-offline.webp"
    ],
    video:   "https://www.youtube.com/watch?v=wYXOb7Z9mng",
    credit:  "A working prototype, demonstrated end to end with sample data and not yet used with real patients. 21 database tables and 401 automated tests. Every patient and the clinic shown are fictional."
  },

  {
    title:   "Cairn — Tab Manager & Workspace Saver for Chrome",
    kind:    "Chrome Extension",
    summary: "A Chrome extension that saves everything you have open as a named workspace, so you can close 30 tabs and get them all back in one click. Search, cleanup, notes and crash recovery all run on your own device, with no account and no server.",
    stack:   ["TypeScript", "React", "Chrome Manifest V3", "Vite", "Bootstrap 5", "Vitest"],
    year:    2026,
    images:  [
      "assets/projects/cairn/cover.webp",
      "assets/projects/cairn/01-overview.webp",
      "assets/projects/cairn/02-workspaces.webp",
      "assets/projects/cairn/03-notes.webp",
      "assets/projects/cairn/04-cleanup.webp",
      "assets/projects/cairn/05-search.webp"
    ],
    video:   "https://www.youtube.com/watch?v=fvWrDqO2-_A",
    demo:    "https://chromewebstore.google.com/detail/nhjinpljinhggphpohdjlgkbjkabhkhh",
    demoLabel: "Get it on the Chrome Web Store",
    page:    "https://apequaltowork.github.io/cairn/",
    pageLabel: "visit the Cairn website",
    credit:  "Live on the Chrome Web Store. The images show version 1.4.0, with crash recovery and the redesign, which is in review (September 2026); until it is approved the store version looks different. About 7,000 lines of TypeScript and 112 unit tests. All workspaces and sites shown are fictional."
  },

];
