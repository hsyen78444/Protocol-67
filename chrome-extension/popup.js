const inputText = document.getElementById("inputText");
const translateButton = document.getElementById("translateButton");
const selectionButton = document.getElementById("selectionButton");
const copyButton = document.getElementById("copyButton");
const buttonText = document.getElementById("buttonText");
const spinner = document.getElementById("spinner");
const errorBox = document.getElementById("errorBox");
const resultPanel = document.getElementById("resultPanel");
const translationOutput = document.getElementById("translationOutput");
const statusDot = document.getElementById("statusDot");

const API_BASE = "http://127.0.0.1:8000";

function setLoading(isLoading) {
  translateButton.disabled = isLoading;
  buttonText.textContent = isLoading ? "Translating" : "Translate";
  spinner.hidden = !isLoading;
}

function showError(message) {
  errorBox.textContent = message;
  errorBox.hidden = false;
  statusDot.className = "status-dot bad";
}

function clearError() {
  errorBox.textContent = "";
  errorBox.hidden = true;
}

function renderResult(payload) {
  translationOutput.textContent = payload.formal_translation || "";
  resultPanel.hidden = false;
}

async function translate() {
  const text = inputText.value.trim();

  clearError();
  if (!text) {
    showError("Enter text to translate first.");
    inputText.focus();
    return;
  }

  setLoading(true);

  try {
    const response = await fetch(`${API_BASE}/translate`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ text })
    });

    if (!response.ok) {
      let detail = response.statusText;
      try {
        const body = await response.json();
        detail = body.detail || detail;
      } catch {
        // Keep the browser-provided error text.
      }
      throw new Error(detail || `Request failed with ${response.status}`);
    }

    const payload = await response.json();
    renderResult(payload);
    statusDot.className = "status-dot ok";
  } catch (error) {
    showError(
      `${error.message}. Check that the backend is running.`
    );
  } finally {
    setLoading(false);
  }
}

async function useSelectedText() {
  clearError();

  try {
    const [tab] = await chrome.tabs.query({
      active: true,
      currentWindow: true
    });

    if (!tab?.id) {
      showError("No active tab found.");
      return;
    }

    const [{ result }] = await chrome.scripting.executeScript({
      target: { tabId: tab.id },
      func: () => window.getSelection().toString()
    });

    if (!result || !result.trim()) {
      showError("Select text on the page first.");
      return;
    }

    inputText.value = result.trim();
    inputText.focus();
  } catch (error) {
    showError(`Could not read selected text: ${error.message}`);
  }
}

async function copyOutput() {
  const text = translationOutput.textContent.trim();
  if (!text) {
    return;
  }
  await navigator.clipboard.writeText(text);
  copyButton.textContent = "Copied";
  setTimeout(() => {
    copyButton.textContent = "Copy";
  }, 1200);
}

translateButton.addEventListener("click", translate);
selectionButton.addEventListener("click", useSelectedText);
copyButton.addEventListener("click", copyOutput);
inputText.addEventListener("keydown", (event) => {
  if ((event.ctrlKey || event.metaKey) && event.key === "Enter") {
    translate();
  }
});
