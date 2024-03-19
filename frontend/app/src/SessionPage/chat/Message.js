import React from "react";

import "./Message.css";

function Message(props) {

    const getAuthorInitials = () => {
        const words = props.messageData.author.name.split(" ");
        return words.map((word) => {
            return word.charAt(0);
        }).join("");
    };

    if (props.userId === props.messageData.author.id) {
        return (
            <div className="my-3 d-flex align-items-center justify-content-end">
                <div className="p-2 d-inline-block rounded-3 my-message-bg msg">
                    <div className="px-1 message-text">{props.messageData.message}</div>
                </div>
                <div className="pl-2 ms-2 d-inline-block rounded-circle author fs-5">
                    <div className="author-frame-text">{getAuthorInitials()}</div>
                </div>
            </div>
        );
    } else {
        return (
            <div className="my-3 d-flex align-items-center">
                <div className="pl-2 me-2 d-inline-block rounded-circle author fs-5">
                    <div className="author-frame-text">{getAuthorInitials()}</div>
                </div>
                <div className="p-2 d-inline-block rounded-3 message-bg msg">
                    <div className="px-1 message-text">{props.messageData.message}</div>
                </div>
            </div>
        )
    }
}

export default Message;