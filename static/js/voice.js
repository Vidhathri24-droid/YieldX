const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
recognition.onresult = function(event){
    const transcript = event.results[0][0].transcript;
    document.getElementById('chatInput').value = transcript;
};

function startVoiceRecognition(){
    const lang = document.getElementById('languageSelect').value + '-IN';
    recognition.lang = lang;
    recognition.start();
}
