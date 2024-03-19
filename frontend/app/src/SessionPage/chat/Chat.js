import React from "react";
import Message from "./Message";

import "./Chat.css";

function Chat(props) {
    const handleSendMessage = () => {
        const input = document.getElementById("message-input");
        props.ws.send(JSON.stringify({
            author_id: props.userId,
            message: input.value,
            type: "message"
        }));

        input.value = "";
    }

    return (
        <div>
            <div className="mb-3 fw-normal fs-3 chat-header">Chat with your friends</div>
            <div style={{ height: "730px" }} className="text-light">
                <div className="shadow-sm rounded-1 px-3 mb-3 chat-bg" style={{ height: "675px", overflow: "auto" }}>
                    {
                        props.messages.map(function (message) {
                            return (
                                <Message key={message.id} messageData={message} userId={props.userId} />
                            );
                        })
                    }
                </div>

                <div className="d-grid gap-3" style={{ gridTemplateColumns: `4fr 1fr` }}>
                    <div>
                        <input id="message-input" type="text" style={{ width: "100%" }} placeholder="Enter message..." className="form-control shadow-sm" />
                    </div>
                    <div>
                        <button type="button" style={{ width: "100%" }} className="shadow-sm btn buttons-bg text-light" onClick={handleSendMessage}>Send</button>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default Chat;