import { w3cwebsocket as W3CWebSocket } from "websocket"

const createClient = () => {
    let client = new W3CWebSocket('ws://localhost:9000',["ocpp1.6"]);

    client.onopen = function() {
        console.log('WebSocket Client Connected');
    }
    client.on('message', function(message) {
            console.log("Received: '" + message.utf8Data + "'");
        })
    
    return client
}


const getChargePoints = (ws, id) => {
}


const StartCharge = (ws, id) => {
    var Auth = JSON.stringify([2, id, "RemoteStartTransaction", {"idTag": id}]);
    ws.send(Auth);
}
const StopCharge = (ws, id) => {
   
}
export {createClient,StartCharge}