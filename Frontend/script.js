const map = L.map("map").setView([28.6139, 77.2090], 12);

L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  attribution: "© OpenStreetMap"
}).addTo(map);

// Load existing potholes
fetch("/potholes")
  .then(res => res.json())
  .then(data => {
    data.forEach(p => addMarker(p));
  });

function addMarker(p) {
  const marker = L.marker([p.latitude, p.longitude]).addTo(map);

  marker.bindPopup(`
    <b>Pothole</b><br>
    Severity: ${p.severity}<br>
    Status: ${p.status}<br><br>
    <img src="/uploads/${p.image}" width="200"><br><br>
    <button onclick="deletePothole('${p.id}')">❌ Delete</button>
  `);
}

function reportPothole() {
  navigator.geolocation.getCurrentPosition(pos => {
    const formData = new FormData();

    formData.append("image", document.getElementById("image").files[0]);
    formData.append("severity", document.getElementById("severity").value);
    formData.append("latitude", pos.coords.latitude);
    formData.append("longitude", pos.coords.longitude);

    fetch("/report", {
      method: "POST",
      body: formData
    })
    .then(res => res.json())
    .then(result => {
      addMarker(result.data);
      alert("✅ Pothole reported");
    });
  });
}

function deletePothole(id) {
  if (!confirm("Delete this pothole?")) return;

  fetch(`/delete/${id}`, {
    method: "DELETE"
  })
  .then(res => res.json())
  .then(() => {
    alert("🗑️ Deleted");
    location.reload();
  });
}
