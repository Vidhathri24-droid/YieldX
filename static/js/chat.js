function sendChat(){
    const msg = document.getElementById('chatInput').value;
    document.getElementById('chatOutput').innerText = "You: " + msg + "\nFetching recommendation...";
    const lang = document.getElementById('languageSelect').value;

    fetch('/get_crop_recommendations',{
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body: JSON.stringify({
            soilPh: 6.5, temperature: 30, humidity: 70, language: lang
        })
    }).then(res=>res.json())
      .then(data=>{
          document.getElementById('chatOutput').innerText += "\nRecommended: " + data.crops.join(', ');
      });
}
y
