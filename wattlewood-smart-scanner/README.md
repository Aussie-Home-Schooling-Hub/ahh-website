# Wattlewood Smart Scanner

A phone scanner for weekly pages. It photographs a page, straightens it, and uploads that batch to a Google Drive folder the signed-in person has chosen.

Each person signs in with their own Google account. The scanner does not keep accounts of its own. Black and white is the normal scan, so handwriting stays readable. Colour is there for paintings and diagrams.

It needs a network connection. It is not an offline app, and it does not work if the HTML file is opened from Downloads. Camera, home-screen install, and Google sign-in need the hosted site.

## Put it on Netlify

This folder is its own site. Leave the rest of the repository as the main website.

1. In Netlify, add a new site from this GitHub repository.
2. Choose the branch you want to publish.
3. Set the base directory to `wattlewood-smart-scanner`.
4. Leave the build command empty.
5. Set the publish directory to `.` (this folder). The `netlify.toml` in this folder says the same thing.
6. Deploy, then copy the site URL, such as `https://something.netlify.app`.

## The two Google values

Paste both into Set up Google Drive on the scanner page. This browser remembers the client ID, the API key, the folder, and the child's name. It does not remember the Google sign-in. Sign in again when you come back.

1. Create a project in Google Cloud Console.
2. Enable the Google Drive API and the Google Picker API.
3. Open the OAuth consent screen. Leave it in Testing. Add your Gmail address as a test user.
4. Create an OAuth client ID. Application type: Web application. Under Authorised JavaScript origins, add the Netlify URL only, with no path on the end. Example: `https://something.netlify.app`.
5. Create an API key for the Picker. Restrict it to the Google Picker API, and to that same Netlify URL as an HTTP referrer.

The client ID starts with the Cloud project number. The scanner uses that number so the Picker can hand this app the folder you choose. You do not paste a third value.

Sign in, then choose the upload folder. The folder name is shown on the page.

Sign-in uses only `https://www.googleapis.com/auth/drive.file`. The scanner can write to the folder you pick. It does not ask for full Drive access.

Shop customers cannot sign in until you publish that consent screen. While it stays in Testing, only the Gmail addresses you added as test users can sign in.

## File names

Every file name includes the date, so a later week does not reuse the previous name.

- With a subject: `2026-10-07 - Sam - Maths p1.jpg`
- Without a subject: `2026-10-07 - Sam p1.jpg`
- One packing list for the batch: `2026-10-07 - Sam - Maths.json` (or `2026-10-07 - Sam.json` when the subject is empty)

The packing list records the date, the day, the child's name, the subject override, the total pages, and the file names.

Upload to Drive sends that batch into the chosen folder. Download zip saves the same pages and the same packing list if Drive does not take them.

## The weekly loop

When the week is finished, copy the upload folder to your archive and empty the upload folder. Claude reads whatever is still in the upload folder. This scanner does not copy or empty that folder. Each upload is only the pages on the screen at the time.

Empty the upload folder before the next batch if this week's pages should be the only ones Claude sees. A second batch on the same day, with the same child and subject, uses the same file names. Drive keeps both copies. It does not replace the earlier file.

## Install on a phone

Open the Netlify site in Chrome or Safari, then add it to the home screen. The name is Wattlewood Smart Scanner.
