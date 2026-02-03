const messages = document.getElementById("messages");
// const typing = document.getElementById("typing");
const input = document.getElementById("userInput");

function sendMessage() {
  const text = input.value.trim();
  if (!text) return;

  addMessage(text, "user");
  input.value = "";

  typing.style.display = "block";

  setTimeout(() => {
    typing.style.display = "none";
    addMessage("This is where AI response will appear.", "bot");
  }, 1000);
}

function addMessage(text, sender) {
  const div = document.createElement("div");
  div.className = sender === "user" ? "user-msg" : "bot-msg";
  div.textContent = text;
  messages.appendChild(div);
  messages.scrollTop = messages.scrollHeight;
}

function newChat() {
  messages.innerHTML = `<div class="bot-msg">Hi 👋 New chat started.</div>`;
}

/* ENTER KEY */
input.addEventListener("keydown", function (e) {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});

function startVoice() {
  const SpeechRecognition =
    window.SpeechRecognition || window.webkitSpeechRecognition;

  if (!SpeechRecognition) {
    alert("Speech Recognition not supported in this browser. Use Chrome or Edge.");
    return;
  }

  const recognition = new SpeechRecognition();

  // 🔥 IMPORTANT SETTINGS
  recognition.lang = "en-US";
  recognition.continuous = false;
  recognition.interimResults = false;
  recognition.maxAlternatives = 1;

  recognition.start();

  // Optional UI feedback
  console.log("🎤 Listening...");

  recognition.onresult = function (event) {
    const transcript = event.results[0][0].transcript;
    console.log("Voice detected:", transcript);

    const inputBox = document.getElementById("msg");
    inputBox.value = transcript;

    sendMessage(); // auto send
  };

  recognition.onerror = function (event) {
    console.error("Speech recognition error:", event.error);
    alert("Mic error: " + event.error);
  };

  recognition.onend = function () {
    console.log("🎤 Voice recognition ended");
  };
}

let recognition = null;
let femaleVoice = null;

const inputBox = document.getElementById("msg");
const chatBox = document.getElementById("chat-box");
const typing = document.getElementById("typing");


function loadFemaleVoice() {
  const voices = window.speechSynthesis.getVoices();

  femaleVoice = voices.find(v =>
    v.name.toLowerCase().includes("female") ||
    v.name.toLowerCase().includes("zira") ||       // Windows female
    v.name.toLowerCase().includes("samantha") ||  // macOS female
    v.name.toLowerCase().includes("google")       // Chrome female
  );

  if (!femaleVoice && voices.length > 0) {
    femaleVoice = voices[0]; // fallback
  }
}

/* Needed because voices load async */
window.speechSynthesis.onvoiceschanged = loadFemaleVoice;

/* ---------------- SEND MESSAGE ---------------- */
function sendMessage() {
  const msg = inputBox.value.trim();
  if (!msg) return;

  stopAllAudio(); // 🔥 stop any running audio first

  addMessage(msg, "user");
  inputBox.value = "";
  typing.style.display = "block";

  fetch("/chat", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ message: msg })
  })
  .then(res => res.json())
  .then(data => {
    typing.style.display = "none";
    addMessage(data.reply, "bot");
    speakFemale(data.reply);
  })
  .catch(() => {
    typing.style.display = "none";
    addMessage("⚠️ AI not responding", "bot");
  });
}

/* ---------------- ENTER KEY ---------------- */
inputBox.addEventListener("keydown", e => {
  if (e.key === "Enter") {
    e.preventDefault();
    sendMessage();
  }
});

/* ---------------- ADD MESSAGE ---------------- */
function addMessage(text, cls) {
  const div = document.createElement("div");
  div.className = cls;
  div.innerText = text;
  chatBox.appendChild(div);
  chatBox.scrollTop = chatBox.scrollHeight;
}

/* ---------------- NEW CHAT ---------------- */
function newChat() {
  stopAllAudio();
  chatBox.innerHTML = `<div class="bot">🤖 New chat started. Ask me anything.</div>`;
}

/* ---------------- 🎤 START MIC ---------------- */
function startVoice() {
  stopAllAudio(); // 🔥 ensure clean start

  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SR) {
    alert("Voice input not supported. Use Chrome or Edge.");
    return;
  }

  recognition = new SR();
  recognition.lang = "en-US";
  recognition.continuous = false;
  recognition.interimResults = false;

  recognition.start();

  recognition.onresult = e => {
    inputBox.value = e.results[0][0].transcript;
    sendMessage();
  };

  recognition.onerror = e => {
    console.error("Mic error:", e.error);
  };
}

/* ---------------- ⏹ STOP EVERYTHING ---------------- */
function stopAllAudio() {
  // Stop mic
  if (recognition) {
    recognition.stop();
    recognition = null;
  }

  // Stop bot voice
  if (window.speechSynthesis.speaking) {
    window.speechSynthesis.cancel();
  }
}

/* ---------------- 🔊 FEMALE VOICE ---------------- */
function speakFemale(text) {
  if (!window.speechSynthesis) return;

  const utter = new SpeechSynthesisUtterance(text);
  utter.voice = femaleVoice;
  utter.rate = 1;
  utter.pitch = 1.2;

  window.speechSynthesis.speak(utter);
}



