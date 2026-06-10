# Protocol 67 Chrome Extension

Small Chrome extension for translating slang text through the local Protocol 67 backend.

## Run the backend

From the backend folder:

```powershell
cd "D:\Protocol 67\backend"
uvicorn app.main:app --reload
```

The extension defaults to:

```text
http://127.0.0.1:8000
```

## Load the extension in Chrome

1. Open `chrome://extensions`.
2. Turn on **Developer mode**.
3. Click **Load unpacked**.
4. Select this folder: `D:\Protocol 67\chrome-extension`.

## Use it

Paste text into the popup and click **Translate**, or select text on a web page and click **Use selected text**.
