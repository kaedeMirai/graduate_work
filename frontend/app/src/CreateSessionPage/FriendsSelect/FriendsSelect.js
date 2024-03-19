import React from "react";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import Cookies from "js-cookie";

import Friend from "./Friend/Friend";

import "./FriendsSelect.css";


function FriendsSelect(props) {
    const [selectedFriends, setSelectedFriends] = useState([]);

    const navigate = useNavigate();

    const handleInviteFriends = async () => {
        console.log("SELECTED FRIENDS: " + selectedFriends);

        const movieId = "a181cb2f-35f7-4a73-84d3-3cc64902dd44"
        const requestData = {
            selected_participants: selectedFriends,
            movie_id: movieId,
        }

        const createSessionResponse = await fetch("http://localhost:8090/api/v1/session/create_session", {
            method: "POST",
            headers: {
                "Content-Type": "application/json;charset=utf-8",
                "Authorization": "Bearer " + Cookies.get("access_token")
            },
            body: JSON.stringify(requestData)
        });

        if (createSessionResponse.status !== 200) {
            console.log("FAILED TO CREATE SESSION")
        }

        const createSessionResponseJson = await createSessionResponse.json();
        console.log(createSessionResponseJson);

        const sessionId = createSessionResponseJson["session_id"];
        console.log(sessionId);

        navigate("/join_session?session_id=" + sessionId)
    };

    return (
        <div>
            <div className="mb-3 fw-normal fs-3 friends-select-header">Invite friends</div>
            <div style={{ height: "730px" }} className="text-light">
                <div className="border rounded-1 px-3 mb-3" style={{ height: "670px", overflow: "auto" }}>
                    {
                        props.friends.map(function (friend) {
                            return (
                                <Friend
                                    key={friend.id}
                                    friendData={friend}
                                    selectedFriends={selectedFriends}
                                    setSelectedFriends={setSelectedFriends}
                                />
                            );
                        })
                    }
                </div>
                <div>
                    <button
                        type="button"
                        style={{ width: "100%" }}
                        className="shadow-sm btn buttons-bg text-light"
                        onClick={handleInviteFriends}
                    >Create Session</button>
                </div>
            </div>
        </div>
    );
}

export default FriendsSelect;