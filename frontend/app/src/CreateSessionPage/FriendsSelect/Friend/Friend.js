import React from "react";
import "./Friend.css";

function Friend(props) {

    const handleFriendSelect = () => {
        let selectedFriends = props.selectedFriends;

        if (!selectedFriends.includes(props.friendData.id)) {
            selectedFriends.push(props.friendData.id);
        } else {
            selectedFriends.splice(selectedFriends.indexOf(props.friendData.id), 1);
        }

        props.setSelectedFriends([...selectedFriends]);
    };

    const getFriendInitials = () => {
        return props.friendData.first_name.charAt(0) + props.friendData.last_name.charAt(0);
        // const words = props.friendData.name.split(" ");
        // return words.map((word) => {
        //     return word.charAt(0);
        // }).join("");
    };

    return (
        <div className="my-3 d-flex align-items-center">
            <div className="pl-2 me-2 d-inline-block rounded-circle fs-5 initials">
                <div className="initials-frame-text">{getFriendInitials()}</div>
            </div>
            <div className="p-2 d-inline-block rounded-3 text-dark friend-name">
                <div className="px-1 fs-4">{props.friendData.first_name} {props.friendData.last_name}</div>
            </div>
            <div className="checkbox-container">
                <input
                    className="form-check-input"
                    type="checkbox"
                    id="checkboxNoLabel"
                    value=""
                    aria-label="..."
                    onClick={handleFriendSelect}
                />
            </div>
        </div>
    );
}

export default Friend;