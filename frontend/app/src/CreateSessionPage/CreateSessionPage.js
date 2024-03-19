import React from "react";
import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import Cookies from "js-cookie";

import Header from "../header/Header";
import Poster from "./Poster/Poster";
import FriendsSelect from "./FriendsSelect/FriendsSelect";


function CreateSessionPage(props) {
    const [friends, setFriends] = useState([]);

    const navigate = useNavigate();

    useEffect(() => {
        async function fetchUserFriends() {
            if (!props.isAuthorized) {
                navigate("/login");
                return;
            }

            const friendsResponse = await fetch("http://localhost:8080/api/v1/auth/get_user_friends", {
                method: "GET",
                headers: {
                    "Content-Type": "application/json;charset=utf-8",
                    "Authorization": "Bearer " + Cookies.get("access_token")
                }
            });

            if (friendsResponse.status !== 200) {
                console.log("FAILED TO RETRIEVE FRIENDS FROM AUTH")
            }

            const friendsResponseJson = await friendsResponse.json();
            console.log(friendsResponseJson)

            setFriends(friendsResponseJson);
        }

        fetchUserFriends();
    }, []);

    return (
        <div style={{ height: "100vh" }} className="main-bg">
            <Header />

            <div className="pt-5">
                <div className="d-grid gap-3" style={{ gridTemplateColumns: `1fr 4fr 0.5fr 3fr 1fr` }}>
                    <div></div>
                    <div>
                        <Poster />
                    </div>
                    <div></div>
                    <div>
                        <FriendsSelect friends={friends} />
                    </div>
                    <div></div>
                </div>
            </div>
        </div>
    );
}

export default CreateSessionPage;
