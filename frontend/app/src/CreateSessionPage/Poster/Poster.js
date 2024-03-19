import React from "react";
import posterImage from "./media/poster.jpg";


function Poster() {
    return (
        <div>
            <div className="mb-3 fw-bolder fs-3">Elephants Dream (2006)</div>
            <div className="d-flex align-items-center justify-content-center">
                <div>
                    <img src={posterImage} alt="Elephants Dream"></img>
                </div>
            </div>
            <div className="mt-3 fs-5">
                <b>Elephants Dream</b> (code-named <b>Project Orange</b> during production and originally titled Machina) is a 2006 Dutch animated
                science fiction fantasy experimental short film produced by Blender Foundation using, almost exclusively, free and open-source software.
                The film is English-language and includes subtitles in over 30 languages.
                <p></p>
                An old man, Proog (voiced by Tygo Gernandt), guides the young Emo (voiced by Cas Jansen) through a giant surreal machine, in which the rooms have no clear transition to each other.
                After Proog saves Emo from flying plugs in a room consisting of a gigantic telephone switchboard, they run through a dark room filled with electrical cables and flee from a flock of bird-like robots.
                In the next room, Emo is tempted to answer a ringing phone, but Proog stops him and reveals a trap. The room is also occupied by a robot resembling a self-operating typewriter, which Emo appears to laugh at.
                The next room is a large abyss from which metal supports appear from below; Proog nimbly dances across the abyss on the supports, while Emo casually walks along and does not seem to notice the stilts supporting him.
            </div>
        </div>
    );
}

export default Poster;