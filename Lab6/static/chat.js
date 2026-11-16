
const form = document.getElementById("chat-form");
const input = document.getElementById("message-input");
const sendButton = document.getElementById("send-button");
const resetButton = document.getElementById("reset-button");
const messages = document.getElementById("messages");
const modelSelect = document.getElementById("model-select");

let busy = false;

function modelName() {
    return modelSelect.value === "gpt"
        ? "GPT-OSS"
        : "Gemini";
}

function addMessage(text, type) {
    const div = document.createElement("div");
    div.className = "message " + type;
    div.textContent = text;

    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
}

function setBusy(value) {
    busy = value;
    input.disabled = value;
    sendButton.disabled = value;
    resetButton.disabled = value;
    modelSelect.disabled = value;
}

modelSelect.addEventListener("change", () => {
    messages.innerHTML = "";

    addMessage(
        modelName() + "：你好，請輸入問題。",
        "ai"
    );
});

form.addEventListener("submit", async (event) => {
    event.preventDefault();

    if (busy) return;

    const message = input.value.trim();
    if (!message) return;

    const selectedModel = modelSelect.value;
    const selectedName = modelName();

    addMessage("You：" + message, "user-message");

    input.value = "";
    setBusy(true);

    try {
        const response = await fetch("/api/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                message: message,
                model: selectedModel
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.error || "伺服器發生錯誤"
            );
        }

        addMessage(
            selectedName + "：" + data.reply,
            "ai"
        );

    } catch (error) {
        addMessage(
            "Error：" + error.message,
            "error-message"
        );
    } finally {
        setBusy(false);
        input.focus();
    }
});

resetButton.addEventListener("click", async () => {
    if (busy) return;

    setBusy(true);

    try {
        const response = await fetch("/api/reset", {
            method: "POST"
        });

        if (!response.ok) {
            throw new Error("重設對話失敗");
        }

        messages.innerHTML = "";
        addMessage(
            modelName() + "：已開始新的對話。",
            "ai"
        );
    } catch (error) {
        addMessage(
            "Error：" + error.message,
            "error-message"
        );
    } finally {
        setBusy(false);
    }
});
