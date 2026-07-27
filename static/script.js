document.addEventListener("DOMContentLoaded", () => {
  const chatBox = document.getElementById("chat-box");
  const userInput = document.getElementById("user-input");
  const sendBtn = document.getElementById("send-btn");
  const chatToggle = document.getElementById("chat-toggle");
  const chatContainer = document.getElementById("chat-container");
  const closeBtn = document.getElementById("close-btn");

  let chatOpenedOnce = false;

  chatToggle.addEventListener("click", () => {
    const isOpen = chatContainer.style.display === "flex";
    chatContainer.style.display = isOpen ? "none" : "flex";
    chatContainer.style.flexDirection = "column";

    if (!chatOpenedOnce && !isOpen) {
      setTimeout(() => {
        addMessage("Hello, How can I assist you?", "bot");
      }, 500);
      chatOpenedOnce = true;
    }
  });

  closeBtn.addEventListener("click", () => {
    chatContainer.style.display = "none";
  });

  function formatTime() {
    const now = new Date();
    return now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }

  function formatBotReply(text) {
    const rawHTML = marked.parse(text); // ✅ Convert Markdown to HTML
    return DOMPurify.sanitize(rawHTML); // ✅ Sanitize HTML
  }

  function addMessage(text, type, sourceUrl = null) {
    const wrapper = document.createElement("div");
    wrapper.classList.add("message-wrapper");
    if (type === "user") wrapper.classList.add("user");

    const message = document.createElement("div");
    message.classList.add("message", type);

    const isShort = text.length <= 30;
    const timestampClass = isShort ? "inline-time" : "block-time";
    const timestampHTML = `<span class="timestamp ${timestampClass}">${formatTime()}</span>`;

    let formattedText =
      type === "bot" ? formatBotReply(text) : text.replace(/\n/g, "<br>");

    if (type === "bot" && sourceUrl) {
      formattedText += `
        <p style="margin-top: 10px; font-size: 0.7rem; color: #555;">
          <em>Source:</em> 
          <a href="${sourceUrl}" target="_blank" style="color: #3a6d9c; text-decoration: underline;">
            ${sourceUrl}
          </a>
        </p>`;
    }

    message.innerHTML = `${formattedText}<br>${timestampHTML}`;

    if (type === "bot") {
      const avatar = document.createElement("div");
      avatar.classList.add("bot-avatar");
      wrapper.appendChild(avatar);
      wrapper.appendChild(message);
    } else {
      wrapper.appendChild(message);
    }

    chatBox.appendChild(wrapper);
    chatBox.scrollTop = chatBox.scrollHeight;
  }

async function sendMessage() {
  const message = userInput.value.trim();
  if (!message) return;

  addMessage(message, "user");
  userInput.value = "";

  showTyping();
  await new Promise(res => setTimeout(res, 1000));

  try {
    const res = await fetch("/chat", {  // ✅ Local relative endpoint
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message })
    });

    const data = await res.json();
    removeTyping();

    addMessage(data.response, "bot");

  } catch (err) {
    console.error("Chat error:", err);
    removeTyping();
    addMessage("Hmm, I didn't catch that. Can you try again?", "bot");
  }
}



  function showTyping() {
    const wrapper = document.createElement("div");
    wrapper.classList.add("message-wrapper");
    wrapper.id = "typing-indicator-wrapper";

    const avatar = document.createElement("div");
    avatar.classList.add("bot-avatar");

    const bubble = document.createElement("div");
    bubble.classList.add("message", "bot");

    const dots = document.createElement("div");
    dots.classList.add("typing-dots");
    dots.innerHTML = "<span></span><span></span><span></span>";

    bubble.appendChild(dots);
    wrapper.appendChild(avatar);
    wrapper.appendChild(bubble);
    chatBox.appendChild(wrapper);
    chatBox.scrollTop = chatBox.scrollHeight;
  }

  function removeTyping() {
    const typingWrapper = document.getElementById("typing-indicator-wrapper");
    if (typingWrapper) typingWrapper.remove();
  }

  sendBtn.addEventListener("click", sendMessage);
  userInput.addEventListener("keypress", e => {
    if (e.key === "Enter") sendMessage();
  });
});
