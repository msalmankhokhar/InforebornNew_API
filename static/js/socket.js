import { io } from "https://cdn.socket.io/4.7.4/socket.io.esm.min.js";
  
const socket = io({autoConnect : false});

socket.connect();

let inputBox =  document.getElementById("inputBox");
let sendBtn =  document.getElementById("sendBtn");
let chatBox =  document.getElementById("chatBox");

sendBtn.addEventListener("click", (e)=>{
    let msg = inputBox.value;
    socket.emit('new_msg', msg);   
})

function makeMsg(msg, type) {
    let span = document.createElement("span");
    span.classList.add("messegeBox", type);
    span.innerText = msg;
    chatBox.appendChild(span);
}

socket.on("new_msg", (msg)=>{
    makeMsg(msg, "my")
})