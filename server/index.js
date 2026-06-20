const express = require('express');
const cors = require('cors');
const { v4: uuidv4 } = require('uuid');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = 3000;

app.use(cors());
app.use(express.json());
app.use(express.json({ limit: '50mb' }));
app.use(express.static(path.join(__dirname, 'public')));

// Storage for pins and results
const pins = {}; // { pin: { created, suspect, result } }

// ============================================
// STAFF - Create a new PIN
// ============================================
app.post('/api/create-pin', (req, res) => {
    const pin = Math.random().toString(36).substring(2, 8).toUpperCase();
    const suspect = req.body.suspect || 'Unknown';
    pins[pin] = {
        pin,
        suspect,
        created: new Date().toISOString(),
        result: null,
        status: 'waiting' // waiting, scanned
    };
    console.log(`[+] New PIN created: ${pin} for suspect: ${suspect}`);
res.json({ pin, link: `https://blanching-reflector-alabaster.ngrok-free.dev/scan/${pin}` });
});

// ============================================
// SUSPECT - Download scanner by PIN
// ============================================
app.get('/scan/:pin', (req, res) => {
    const pin = req.params.pin.toUpperCase();
    if (!pins[pin]) {
        return res.status(404).send('Invalid PIN');
    }
    res.sendFile(path.join(__dirname, 'public', 'scan.html'));
});

// ============================================
// SCANNER - Submit scan results
// ============================================
app.post('/api/submit/:pin', (req, res) => {
    const pin = req.params.pin.toUpperCase();
    if (!pins[pin]) {
        return res.status(404).json({ error: 'Invalid PIN' });
    }
    pins[pin].result = req.body;
    pins[pin].status = 'scanned';
    pins[pin].scanned_at = new Date().toISOString();
    console.log(`[+] Results received for PIN: ${pin}`);
    res.json({ success: true });
});

// ============================================
// STAFF - Get all PINs
// ============================================
app.get('/api/pins', (req, res) => {
    res.json(Object.values(pins));
});

// ============================================
// STAFF - Get result for a PIN
// ============================================
app.get('/api/result/:pin', (req, res) => {
    const pin = req.params.pin.toUpperCase();
    if (!pins[pin]) {
        return res.status(404).json({ error: 'PIN not found' });
    }
    res.json(pins[pin]);
});

app.listen(PORT, () => {
    console.log(`\n✅ AntiCheat Server running at http://localhost:${PORT}`);
    console.log(`📋 Staff Dashboard: http://localhost:${PORT}/dashboard.html\n`);
});