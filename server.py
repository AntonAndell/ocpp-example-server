import asyncio
import logging
import random
import json
from datetime import datetime

try:
    import websockets
except ModuleNotFoundError:
    print("This example relies on the 'websockets' package.")
    print("Please install it by running: ")
    print()
    print(" $ pip install websockets")
    import sys
    sys.exit(1)

from ocpp.routing import on, after
from ocpp.v16 import ChargePoint as cp
from ocpp.v16.enums import Action, RegistrationStatus, AuthorizationStatus, DataTransferStatus, ChargePointStatus
from ocpp.v16 import call_result, call
logging.basicConfig(level=logging.INFO)


class ChargePoint(cp):
    def __init__(self, _id, connection):
        cp.__init__(self,  _id, connection)
        self.status = ChargePointStatus.available
        self.transaction_id = None
        self.update_db()

    #dummy database showing all connected chargepoints and their status
    def update_db(self):
        with open('db.json') as json_file:
            db = json.load(json_file)
            db[self.id] = {
                "status": self.status
            }
        with open('db.json', 'w') as json_file:
            json.dump(db, json_file)

    #Start charging after authorization
    #usually triggerd by app or webb remotely
    @after(Action.Authorize)
    async def remote_start_transaction(self, id_tag):
        """
        Tell chargepoint to start a transaction with the given id_tag.
        """
        payload = call.RemoteStartTransactionPayload(id_tag = id_tag )
        await self.call(payload)


    @on(Action.Authorize)
    def on_authorize(self, id_tag:str, **kwargs):
        """
        verifies a tag and responds with a status
        """
        #Verify id_tag
        tag_info =  {
            "status": AuthorizationStatus.accepted
        }
        return call_result.AuthorizePayload(
            id_tag_info = tag_info
        )

    @on(Action.BootNotification)
    def on_boot_notification(self, charge_point_vendor: str, charge_point_model: str, **kwargs):
        """
        init message beteween server and chargepoint
        """
        return call_result.BootNotificationPayload(
            current_time =datetime.utcnow().isoformat(),
            interval     =10,
            status       =RegistrationStatus.accepted
        )
    @on(Action.StartTransaction)
    def on_start_transaction(self, connector_id: int, id_tag: int, meter_start:int, reservation_id:int , timestamp:datetime):
        """
        if chargepoint is avaiable and the tag is correct/authorized start charging/transacting 
        """
        if self.status != ChargePointStatus.available:
            status = AuthorizationStatus.blocked
            
        else:
            status = AuthorizationStatus.accepted

        tag_info =  {
            "status": status
        }
        self.transaction_id = random.randint(1,1000)
        self.meter_start
        return call_result.StartTransactionPayload(
            id_tag_info    = tag_info,
            transaction_id = self.transaction_id
        )

    @after(Action.StartTransaction)
    def after_start_transaction(self, connector_id: int, id_tag: int, meter_start:int, reservation_id:int , timestamp:datetime):
        """
        updates charger status and database afer a transaction has been started
        """
        self.status = ChargePointStatus.charging 
        self.update_db()


    @on(Action.StopTransaction)
    def on_stop_transaction(self, id_tag: int, meter_stop:int , timestamp:datetime, transaction_id:int):
        """
        validates transaction id, accepts and stops charging if valid
        """
        if transaction_id != self.transaction_id:
            status = AuthorizationStatus.invalid
        else:
            status = AuthorizationStatus.accepted
        tag_info =  {
            "status": status
        }
        self.status = ChargePointStatus.available
        self.transaction_id = None
        self.update_db()
        return call_result.StopTransactionPayload(
            id_tag_info    = tag_info,
        )

        
    @on(Action.Heartbeat)
    def on_heartbeat(self):
        return call_result.HeartbeatPayload(
            current_time=datetime.utcnow().isoformat(),
        )

    #transact own logic here, only used if ocpp does not support the message
    @on(Action.DataTransfer)
    def on_data_transfer(self, vendor_id:str, message_id:str, data:str):
        return call_result.DataTransferPayload(
            status=DataTransferStatus.accepted
        )





async def on_connect(websocket, path):
    """ For every new charge point that connects, create a ChargePoint
    instance and start listening for messages.
    """
    try:
        requested_protocols = websocket.request_headers[
            'Sec-WebSocket-Protocol']
    except KeyError:
        logging.error(
            "Client hasn't requested any Subprotocol. Closing Connection"
        )
        return await websocket.close()
    if websocket.subprotocol:
        logging.info("Protocols Matched: %s", websocket.subprotocol)
    else:
        # In the websockets lib if no subprotocols are supported by the
        # client and the server, it proceeds without a subprotocol,
        # so we have to manually close the connection.
        logging.warning('Protocols Mismatched | Expected Subprotocols: %s,'
                        ' but client supports  %s | Closing connection',
                        websocket.available_subprotocols,
                        requested_protocols)
        return await websocket.close()

    charge_point_id = path.strip('/')
    cp = ChargePoint(charge_point_id, websocket)
    await cp.start()



async def main():
    #DUMMY DB
    with open('db.json', 'w') as json_file:
        json.dump({}, json_file)


    server =  await websockets.serve(
        on_connect,
        '0.0.0.0',
        9000,
        subprotocols=['ocpp1.6']
    )
    logging.info("Server Started listening to new connections...")
    await server.wait_closed()


if __name__ == '__main__':
    
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()