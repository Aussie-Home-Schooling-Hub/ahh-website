# Wattlewood Smart Scanner

A phone scanner for weekly pages. It photographs a page, straightens it, and packs that batch into one zip. Black and white is the normal scan, so handwriting stays readable. Colour is there for paintings and diagrams.

There is no sign-in and no setup. The child's name stays on this device so it can be changed. The scanner does not keep accounts of its own.

It needs a network connection for the scanner libraries. It is not an offline app, and the camera does not work if the HTML file is opened from Downloads.

## Put it on Netlify

This folder is its own site. Leave the rest of the repository as the main website.

1. In Netlify, add a new site from this GitHub repository.
2. Choose the branch you want to publish.
3. Set the base directory to `wattlewood-smart-scanner`.
4. Leave the build command empty.
5. Set the publish directory to `.` (this folder). The `netlify.toml` in this folder says the same thing.
6. Deploy, then open the site URL on the phone.

## File names

Every page name includes the date and the child's name.

- With a subject: `2026-10-07 - Sam - Maths p1.jpg`
- Without a subject: `2026-10-07 - Sam p1.jpg`
- One packing list beside the pages: `2026-10-07 - Sam - Maths.json` (or `2026-10-07 - Sam.json` when the subject is empty)

The packing list records the date, the day, the child's name, the subject, the total pages, and the file names.

Export & Share Batch packs those files into `Evidence_2026-10-07_Sam.zip`. If the phone can share a file, the share sheet opens. Otherwise the zip downloads.

## Install on a phone

Open the Netlify site in Chrome or Safari, then add it to the home screen. The name is Wattlewood Smart Scanner.
