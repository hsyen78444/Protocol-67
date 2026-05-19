# Frontend

React JS app for the Protocol 67 translator.

## Owner

Frontend member owns the user experience, API integration, feedback form, and demo polish.

## Suggested Setup

Create the React app here with Vite:

```powershell
cd frontend
npm create vite@latest . -- --template react
npm install
npm run dev
```

Use `.env.example` as the backend URL reference.

## Suggested Screens

- Translator page: input box, translate button, output panel.
- Details panel: sentiment, confidence, detected slang, unknown terms.
- Feedback modal: corrected translation and notes.
- Optional review page: unknown-term queue for active learning.
