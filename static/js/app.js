let currentLat = 0, currentLon = 0;

function getLocation() {
    if(navigator.geolocation){
        navigator.geolocation.getCurrentPosition(function(position){
            currentLat = position.coords.latitude;
            currentLon = position.coords.longitude;
            document.getElementById('location').innerText = `Latitude: ${currentLat}, Longitude: ${currentLon}`;
        });
    } else {
        document.getElementById('location').innerText = "Geolocation not supported.";
    }
}

function getWeather(){
    fetch('/get_weather', {
        method: 'POST',
        headers: { 'Content-Type':'application/json' },
        body: JSON.stringify({latitude: currentLat, longitude: currentLon})
    }).then(res => res.json())
      .then(data => {
          document.getElementById('weather').innerText = `Temp: ${data.temperature}°C, Humidity: ${data.humidity}%, Climate: ${data.climate}`;
      });
}

document.getElementById('cropForm').addEventListener('submit', function(e){
    e.preventDefault();
    const lang = document.getElementById('languageSelect').value;
    fetch('/get_crop_recommendations',{
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body: JSON.stringify({
            soilPh: document.getElementById('soilPh').value,
            temperature: document.getElementById('temperature').value,
            humidity: document.getElementById('humidity').value,
            language: lang
        })
    }).then(res=>res.json())
      .then(data=>{
          document.getElementById('cropRecommendations').innerText = data.crops.join(', ');
      });
});

document.getElementById('imageUploadForm').addEventListener('submit', function(e){
    e.preventDefault();
    const lang = document.getElementById('languageSelect').value;
    const formData = new FormData();
    formData.append('image', document.getElementById('image').files[0]);
    formData.append('language', lang);
    fetch('/upload_image',{method:'POST', body: formData})
      .then(res=>res.json())
      .then(data=>{
          document.getElementById('diseaseStatus').innerText = data.disease;
      });
});
