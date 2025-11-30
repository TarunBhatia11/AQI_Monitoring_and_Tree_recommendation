// app.js
const searchBtn = document.getElementById("searchBtn");
const qInput = document.getElementById("q");
const stationsContainer = document.getElementById("stationsContainer");
const statusEl = document.getElementById("status");
let map = null;
let markersLayer = null;

function setStatus(msg, isError=false) {
  statusEl.textContent = msg;
  statusEl.style.color = isError ? "red" : "black";
}

function clearLeftPanel() {
  stationsContainer.innerHTML = "";
}

function renderStationCard(st) {
  const card = document.createElement("div");
  card.className = "stationCard";

  const title = document.createElement("h3");
  title.textContent = st.station_name || "Unknown Station";
  card.appendChild(title);

  const meta = document.createElement("div");
  meta.className = "meta";
  meta.innerHTML = `<span class="badge">AQI: ${st.aqi}</span> Lat: ${st.lat || "N/A"} Lon: ${st.lon || "N/A"}`;
  card.appendChild(meta);

  const poll = document.createElement("div");
  poll.className = "pollutants";
  if (st.pollutants && Object.keys(st.pollutants).length > 0) {
    for (const [k, v] of Object.entries(st.pollutants)) {
      const row = document.createElement("div");
      row.innerHTML = `<strong>${k.toUpperCase()}:</strong> ${v}`;
      poll.appendChild(row);
    }
  } else {
    poll.textContent = "No pollutant data available";
  }
  card.appendChild(poll);

  return card;
}

function initMap(center) {
  if (!map) {
    map = L.map('map').setView(center, 11);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors'
    }).addTo(map);
    markersLayer = L.layerGroup().addTo(map);
  } else {
    map.setView(center, 11);
    markersLayer.clearLayers();
  }
}

function addMarkerToMap(st) {
  if (!st.lat || !st.lon) return;
  const marker = L.marker([st.lat, st.lon]);
  let popup = `<b>${st.station_name}</b><br/>AQI: ${st.aqi}<br/><br/>`;
  if (st.pollutants && Object.keys(st.pollutants).length > 0) {
    popup += "<b>Pollutants</b><br/>";
    for (const [k, v] of Object.entries(st.pollutants)) {
      popup += `${k.toUpperCase()}: ${v}<br/>`;
    }
  } else {
    popup += "No pollutant data available";
  }
  marker.bindPopup(popup);
  marker.addTo(markersLayer);
}

async function doSearch() {
  const q = qInput.value.trim();
  if (!q) {
    setStatus("Please enter a search query", true);
    return;
  }
  setStatus("Searching...");
  clearLeftPanel();

  try {
    const res = await fetch(`/api/search?q=${encodeURIComponent(q)}`);
    if (!res.ok) {
      const err = await res.json();
      setStatus("Server error: " + (err.error || res.statusText), true);
      return;
    }
    const data = await res.json();
    const stations = data.stations || [];

    if (stations.length === 0) {
      setStatus("No stations found for that query.");
      return;
    }

    // populate left panel and gather first valid coord
    let firstCoord = null;
    stations.forEach(st => {
      const card = renderStationCard(st);
      stationsContainer.appendChild(card);
      if (!firstCoord && st.lat && st.lon) {
        firstCoord = [st.lat, st.lon];
      }
    });

    if (!firstCoord) {
      setStatus("Stations returned but no valid coordinates to show on map.");
      return;
    }

    initMap(firstCoord);

    stations.forEach(st => addMarkerToMap(st));

    setStatus(`Found ${stations.length} stations for "${data.query}"`);
  } catch (err) {
    console.error(err);
    setStatus("Unexpected error: " + err.message, true);
  }
}

searchBtn.addEventListener("click", doSearch);

// allow Enter to trigger search
qInput.addEventListener("keypress", function(e){
  if (e.key === "Enter") {
    doSearch();
  }
});


function displayTreeRecommendations(recommendations) {
    const container = document.getElementById("treeResults");
    container.innerHTML = `<h2>🌳 Tree Recommendations</h2>`;

    recommendations.forEach(st => {
        let html = `
        <div class="station-card">
            <h3>${st.station_name}</h3>
        `;

        for (const group in st.tree_groups) {
            const grp = st.tree_groups[group]; // single object, NOT array

            html += `
              <h4>➡ For ${group} Trees:</h4>
              <ul>
                <li><strong>${grp.tree_name}</strong></li>
                <li>Species: ${grp.scientific_name}</li>
                <li>Density: ${grp.canopy_density}</li>
              </ul>

              <details>
                <summary>Show Benefits</summary>
                <pre>${JSON.stringify(grp.benefits, null, 2)}</pre>
              </details>
              <hr>
          `;
        }


        html += `</div>`;
        container.innerHTML += html;
    });
}


// -------------------------------------
// TREE RECOMMENDATION BUTTON HANDLER
// -------------------------------------
document.getElementById("treeBtn").addEventListener("click", async () => {
    const q = document.getElementById("q").value.trim();
    const container = document.getElementById("treeResults");

    if (!q) {
        container.innerHTML = "<p style='color:red'>Enter a location first</p>";
        return;
    }

    container.innerHTML = "<p>Loading tree recommendations...</p>";

    try {
        const res = await fetch(`/tree_recommendations?location=${encodeURIComponent(q)}`);
        const json = await res.json();

        if (json.error) {
            container.innerHTML = `<p style='color:red'>${json.error}</p>`;
            return;
        }

        const recs = json.recommendations || [];

        if (recs.length === 0) {
            container.innerHTML = "<p>No recommendations available</p>";
            return;
        }

        let html = "<h2>🌳 Tree Recommendations</h2>";

        recs.forEach(st => {
            html += `<div class="tree-box">
                       <h3>${st.station_name}</h3>
                    `;

            const groups = st.tree_groups;

            [50, 100, 200].forEach(num => {
                const grp = groups[num];
                if (!grp) {
                    html += `<p><b>${num} Trees:</b> No data</p>`;
                    return;
                }

                html += `
                    <h4>➡ For ${num} Trees:</h4>
                    <ul>
                        <li><b>${grp.tree_name}</b> (${grp.scientific_name})</li>
                        <li>Canopy: ${grp.canopy_density}</li>
                    </ul>

                    <details>
                        <summary>Show Benefits</summary>
                        <pre>${JSON.stringify(grp.benefits, null, 2)}</pre>
                    </details>
                `;
            });

            html += "</div><hr/>";
        });

        container.innerHTML = html;

    } catch (err) {
        console.error(err);
        container.innerHTML = `<p style='color:red'>Failed to fetch recommendations</p>`;
    }
});
