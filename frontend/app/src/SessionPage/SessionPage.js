import React from "react";
import { useState, useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";

import Header from "../header/Header";
import Chat from "./chat/Chat";
import VideoPlayer from "./video_player/VideoPlayer";

function SessionPage(props) {
    const [preventEvents, setPreventEvents] = useState(false);
    const [searchParams, setSearchParams] = useSearchParams();

    const [messages, setMessages] = useState([]);

    const navigate = useNavigate();
    const [ws, setWs] = useState(null);
    const sessionId = searchParams.get("session_id");

    useEffect(() => {
        if (!props.userId) {
            navigate("/login");
        } else {
            if (!ws) {
                const ws = new WebSocket("ws://localhost:8090/api/v1/session/ws/join_session/" + sessionId);

                ws.onmessage = (messageData) => {
                    console.log(messageData);
                    try {
                        const message = JSON.parse(messageData.data);
                        console.log("Received message:", message);

                        if (message.type === "message") {
                            setMessages(prevMessages => [...prevMessages, message]);
                        } else if (message.type === "command") {
                            if (message.userId !== props.userId) {
                                const videoPlayerCmp = document.getElementById("video-player");

                                if (message.commandType === "seeked") {
                                    setPreventEvents(true);
                                    videoPlayerCmp.currentTime = message.timestamp;
                                } else if (message.commandType === "play") {
                                    setPreventEvents(true);
                                    videoPlayerCmp.play();
                                } else if (message.commandType === "pause") {
                                    setPreventEvents(true);
                                    videoPlayerCmp.pause();
                                }
                            }
                        }
                    } catch (e) {
                        console.log(e);
                    }
                };

                setWs(ws);
            }
        }
    }, [props.userId, navigate, ws, sessionId]);

    return (
        <div style={{ height: "100vh" }} className="main-bg">
            <Header />

            <div className="pt-5">
                <div className="d-grid gap-3" style={{ gridTemplateColumns: `1fr 4fr 0.5fr 3fr 1fr` }}>
                    <div></div>
                    <div>
                        <VideoPlayer ws={ws} userId={props.userId} preventEvents={preventEvents} setPreventEvents={setPreventEvents} />
                    </div>
                    <div></div>
                    <div>
                        <Chat messages={messages} ws={ws} userId={props.userId} />
                    </div>
                    <div></div>
                </div>
            </div>
        </div>
    );
}

export default SessionPage;
