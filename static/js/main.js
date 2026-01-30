// Populate districts dynamically
document.getElementById("stateSelect").addEventListener("change", async function(){
    const state = this.value;
    const res = await fetch(`/districts/${state}`);
    const districts = await res.json();
    const districtSelect = document.getElementById("districtSelect");
    districtSelect.innerHTML = "";
    districts.forEach(d => {
        const option = document.createElement("option");
        option.value = d.name;
        option.text = d.name;
        districtSelect.appendChild(option);
    });
});

// Crop Disease Detection
document.getElementById("detectBtn").addEventListener("click", async function(){
    const fileInput = document.getElementById("diseaseImage");
    if(fileInput.files.length === 0) { alert("Select an image"); return; }
    const formData = new FormData();
    formData.append("image", fileInput.files[0]);
    formData.append("lang", "hi");
    const res = await fetch("/detect_disease", {method: "POST", body: formData});
    const data = await res.json();
    document.getElementById("diseaseResult").innerText = data.result;
});

// Chat
const chatBox = document.getElementById("chatBox");
document.getElementById("sendBtn").addEventListener("click", async function(){
    const msg = document.getElementById("chatInput").value;
    if(msg.trim() === "") return;
    chatBox.innerHTML += `<p><b>You:</b> ${msg}</p>`;
    const res = await fetch("/chat", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({message: msg, lang: "hi"})
    });
    const data = await res.json();
    chatBox.innerHTML += `<p><b>Assistant:</b> ${data.reply}</p>`;
    document.getElementById("chatInput").value = "";
});

// Voice Input
let recognition;
document.getElementById("voiceBtn").addEventListener("click", function(){
    if(!('webkitSpeechRecognition' in window)) { alert("Voice not supported"); return; }
    recognition = new webkitSpeechRecognition();
    recognition.lang = "hi-IN";
    recognition.interimResults = false;
    recognition.onresult = async function(event){
        const transcript = event.results[0][0].transcript;
        document.getElementById("chatInput").value = transcript;
        document.getElementById("sendBtn").click();
    };
    recognition.start();
});
