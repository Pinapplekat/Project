# Written by @DanTCA1

import os, types

def webSocketFormat(sock, content = "", opcode="Text", FIN = True, RSV1 = False, RSV2 = False, RSV3 = False, MASKED = False, errorCode = None):
    content = bytes(content, "utf-8")
    fByte = b""
    fBit = 0x00
    if FIN : fBit = fBit | 0x80
    if RSV1: fBit = fBit | 0x40
    if RSV2: fBit = fBit | 0x20
    if RSV3: fBit = fBit | 0x10

    opcode = opcode.lower()
    if opcode == "continuation": fBit = fBit | 0x00
    elif opcode == "text"      : fBit = fBit | 0x01
    elif opcode == "binary"    : fBit = fBit | 0x02
    elif opcode == "close"     : fBit = fBit | 0x08
    elif opcode == "ping"      : fBit = fBit | 0x09
    elif opcode == "pong"      : fBit = fBit | 0x0A
    else : raise ValueError(f"The opcode {opcode} is not a valid code.")

    if opcode == "close":
        if errorCode == None:
            errorCode = int.from_bytes(content[0:2], "big")
            content = content[2:]
        if errorCode in [1000, 1001, 1002, 1003, 1007, 1008, 1009, 1010, 1011] or errorCode >= 3000 and errorCode < 5000:
            content = errorCode.to_bytes(2, "big") + content
        else:
            raise ValueError(f"{errorCode} is not a valid error code")

    fByte += fBit.to_bytes(1, "big")
    contentLen = len(content)
    if contentLen > 125 and opcode in ["close", "ping", "pong"]:
        raise ValueError(f"Close, ping, and pong opcodes cannot have payloads longer than 125 (The request had a length of {contentLen})")
    if contentLen <= 125:
        fBit = contentLen
    elif contentLen < 2**16:
        fBit = 0x7E
    elif contentLen < 2**63:
        fBit = 0x7F
    else:
        raise OverflowError("Your data's length was over 9223.372PiB. How did you manage that?")
    
    if MASKED:
        fBit = fBit | 0b10000000
    else:
        fBit = fBit & 0b01111111

    fByte += fBit.to_bytes(1, "big")
    if contentLen > 125:
        if contentLen <= 2**16:
            fByte += contentLen.to_bytes(2, "big")
        else:
            fByte += contentLen.to_bytes(8, "big")
    
    if MASKED:
        MASKING_KEY = os.urandom(4)
        fByte += MASKING_KEY
        temp = b""
        for j in range(contentLen):
            temp += (content[j] ^ MASKING_KEY[j % 4]).to_bytes(1, "big")
        fByte += temp
    else:
        fByte += content
    sock.send(fByte)

def parseReq(sock):
    protocol="WEBSOCKET"
    data = types.SimpleNamespace(protocol="WEBSOCKET", pendingReq=b"")
    # WebSocket uses a 2 way close cycle, if the status has this, than than the cycle has just completed
    if data.protocol.endswith("CLOSING"):
        data.protocol = "CLOSED"
        sock.close()
        return
    if data.protocol == "CLOSED":
        return

    # Reading data from the socket
    # sockBuffer = b""
    # sockBuffer += sock.recv(1024)
    # if sockBuffer == b"": # If the first thing that was read was blank, then the socket is closing
    #     sock.close()
    #     print("Sock closed")
    #     return
    
    # try: # Janky way to read all the data in the socket buffer
    #     while True:
    #         sockBuffer += sock.recv(1024)
    # except BlockingIOError:
    #     pass
    # req = data.pendingReq + sockBuffer
    req = sock.recv(9999)
    
    # All the processing for webSockets (They parse the same whether server or client)
    if protocol.startswith("WEBSOCKET"):
        frame = req
        reader = b""
        error = []

        reader = frame[0]
        FIN =  False if reader & 0b10000000 == 0b0 else True
        RSV1 = False if reader & 0b01000000 == 0b0 else True
        RSV2 = False if reader & 0b00100000 == 0b0 else True
        RSV3 = False if reader & 0b00010000 == 0b0 else True
        if RSV1 | RSV2 | RSV3:
            if RSV1:
                error.append("RSV1 ")
            if RSV2:
                error.append("RSV2 ")
            if RSV3:
                error.append("RSV3 ")
            error.append("is 1 when that state is not defined. ")
        opcodeInt = reader & 0b00001111
        opcode = "Reserved"
        if opcodeInt == 0x00: opcode = "Continuation"
        if opcodeInt == 0x01: opcode = "Text"
        if opcodeInt == 0x02: opcode = "Binary"
        if opcodeInt == 0x08: opcode = "Close"
        if opcodeInt == 0x09: opcode = "Ping"
        if opcodeInt == 0x0A: opcode = "Pong"
        if opcode == "Reserved": error.append(f"Opcode is " + str(opcodeInt.to_bytes(1, "big")) + " (reserved)")
        reader = frame[1]
        MASKED = False if reader & 0b10000000 == 0b0 else True
        i = 2
        payLength = int(reader & 0x7F)
        if payLength == 126:
            i += 2
            payLength = (int(frame[2]) << 8) + int(frame[3])
        if payLength == 127:
            i += 8
            payLength = 0
            for j in range(8):
                payLength += int(frame[j + 2]) << 8 * (7 - j)
        
        if MASKED:
            MASKING_KEY = frame[i:i+4]
            i += 4
        
        payload = frame[i:i + payLength]
        if MASKED:
            temp = b""
            for j in range(len(payload)):
                temp += (payload[j] ^ MASKING_KEY[j % 4]).to_bytes(1, "big")
            payload = temp
        
        if len(payload) != payLength:
            data.pendingReq = req # The request hasn't fully arrived yet and needs to be reprocessed when new data arrives
            return
        if len(frame) > i + payLength:
            data.pendingReq = frame[i + payLength:] # Client might have sent 2 requests back to back
        return(str(payload, "utf-8"))
        # if len(error) != 0:
        #     errorStr = b""
        #     for i in error:
        #         errorStr += bytes(i, "latin-1")
        #     data.reqBuffer.append("SendClose", webSocketFormat(content=0x03EA + errorStr, opcode="Close", returnData=True))
        #     return
        # if opcode == "Close":
        #     data.reqBuffer.append("SendClose", webSocketFormat(content=payload, opcode="Close", returnData=True))
        # if opcode == "Ping":
        #     data.reqBuffer.append("SendManual", webSocketFormat(content=payload, opcode="Pong", returnData=True))
        # data.reqBuffer.append("SelfProcess", types.SimpleNamespace(protocol="WEBSOCKET", FIN=FIN, RSV1=RSV1, RSV2=RSV2, RSV3=RSV3, opcode=opcode, payloadLength=payLength, body=payload, unprocessed=req))