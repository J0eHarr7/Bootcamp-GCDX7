// server.js

const express = require("express");
const path = require("path");
const app = express();

const FLAG = "GCDXN7{real_csti_attack_retrieve_me_from_server}";

app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static("static"));

// ❌ Forbidden endpoint: frontend cannot normally access it
app.get("/internal/flag", (req, res) => {
    res.set("Access-Control-Allow-Origin", ""); // deny all CORS
    return res.json({
        message: "Access Denied. This endpoint is internal only."
    });
});

// ❌ Hidden endpoint accessible ONLY to localhost (optional)
app.get("/internal/flag-real", (req, res) => {
    if (req.ip !== "127.0.0.1") {
        return res.status(403).send("Forbidden. Localhost only.");
    }
    return res.send(FLAG);
});

app.listen(80, () => console.log("CSTI lab running"));
