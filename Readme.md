Chargebox html has simple ui to test chargebox fucntionality.
It also has support for remote starting of transactions.
Address format ws://ip:port/ID ex. ws://localhost:9000/CP_1
Can easily be modified to support custom opperations, like mocking the plugging in of a car

python OCCP follows ocpp protocol names but with python name standard, for references of the ocpp library check:
https://github.com/mobilityhouse/ocpp/tree/master/ocpp

#Chargestation
Chargestation is currently split into a websocket server and a http server.

The websocket server handles all communication with the charge boxes through the ocpp protocol.

The http server takes outside request from admin and users. 



