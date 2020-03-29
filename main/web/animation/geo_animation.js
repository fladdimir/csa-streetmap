// called by animation-client:

const INITIAL_COORDS = [53.55668, 9.92815];
const INITIAL_ZOOM = 16;

const ICON_BASE_URL = "files?filepath=";
const ICON_SIZE = 25 // px

let markers = {};
let map;

function initialize_animation() {
    console.log("initialize_animation");
    _init_map();
}

function animate_simulation(state) {
    for (let key in state) {
        element = state[key];
        let marker;
        if (!(key in markers)) {
            // compute if absent
            // future to do: compare the icon_path to check whether the icon changed
            const url = ICON_BASE_URL + element.icon_path;
            let leaf_icon = new L.Icon({
                iconUrl: url,
                iconSize: [ICON_SIZE, ICON_SIZE],
                iconAnchor: [ICON_SIZE / 2, ICON_SIZE / 2] // center
            });
            marker = L.marker(INITIAL_COORDS, { icon: leaf_icon }).addTo(map);
            marker.bindPopup(element.text);
            marker.openPopup();
            markers[key] = marker;
        }
        marker = markers[key];
        marker.setLatLng({ lat: element.lat, lon: element.lon });
        marker.setRotationAngle(element.direction);
    }
    for (let present_key in markers) {
        if (!(present_key in state)) {
            markers[present_key].remove();
            delete markers[present_key];
        }
    }
}

// helper:

function _init_map() {
    if (map === undefined) {
        map = L.map('map');
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(map);
    }
    map.setView(INITIAL_COORDS, INITIAL_ZOOM);

    for (let key in markers) {
        let marker = markers[key];
        marker.remove();
    }
    markers = {};
}
