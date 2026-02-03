let currentChat = null;

function loadChats() {
  fetch("/chat_list")
  .then(r => r.json())
  .then(data => {
    let list = document.getElementById("chatList");
    list.innerHTML = "";
    data.forEach(chat => {
      let div = document.createElement("div");
      div.innerText = chat.title;
      div.onclick = () => openChat(chat.id);
      list.appendChild(div);
    });
  });
}

function openChat(id) {
  currentChat = id;
  fetch("/load_chat/" + id)
  .then(r => r.json())
  .then(data => {
    let box = document.getElementById("chatbox");
    box.innerHTML = "";
    data.forEach(m => {
      let div = document.createElement("div");
      div.className = m.role;
      div.innerText = m.message;
      box.appendChild(div);
    });
  });
}

document.getElementById("newChat").onclick = () => {
  fetch("/new_chat", {method:"POST"})
  .then(r => r.json())
  .then(d => {
    currentChat = d.chat_id;
    loadChats();
    document.getElementById("chatbox").innerHTML = "";
  });
};

function sendMessage() {
  let msg = document.getElementById("message").value;
  if(!msg || !currentChat) return;

  fetch("/chat", {
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body:JSON.stringify({message:msg, chat_id:currentChat})
  })
  .then(r => r.json())
  .then(d => {
    openChat(currentChat);
  });

  document.getElementById("message").value = "";
}

loadChats();
