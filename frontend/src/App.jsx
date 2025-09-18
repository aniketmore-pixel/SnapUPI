import React, { useState, useEffect } from 'react';
import { Container, Box, Button, Typography, Stack, Paper, Chip, Divider } from '@mui/material';

function App() {
  const [upi, setUpi] = useState('');
  const [tx, setTx] = useState(null);
  const [status, setStatus] = useState(null);

  async function genUPI() {
    const r = await fetch(`${process.env.REACT_APP_API_URL}/api/generate_upi`, { method: 'POST' });
    const j = await r.json();
    setUpi(j.upi);
  }

  async function sendCollect() {
    const r = await fetch(`${process.env.REACT_APP_API_URL}/api/collect`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ to_upi: upi, amount: 10.0 }),
    });
    const j = await r.json();
    setTx(j.tx_id);
    setStatus(j.status);
  }

  useEffect(() => {
    let t;
    if (tx) {
      t = setInterval(async () => {
        const r = await fetch(`${process.env.REACT_APP_API_URL}/api/status/${tx}`);
        const j = await r.json();
        setStatus(j.status);
      }, 1500);
    }
    return () => clearInterval(t);
  }, [tx]);

  const getStatusColor = (s) => {
    switch (s) {
      case 'PENDING': return 'warning';
      case 'SUCCESS': return 'success';
      case 'FAILED': return 'error';
      default: return 'default';
    }
  };

  const handleRefresh = () => {
    window.location.reload();
  };

  return (
    <Container maxWidth="sm" sx={{ mt: 8, mb: 8, position: 'relative' }}>
      {/* Refresh Button at top-left */}
      <Button
        variant="outlined"
        color="primary"
        onClick={handleRefresh}
        sx={{ position: 'absolute', top: -40, left: 0, textTransform: 'none' }}
      >
        Refresh
      </Button>

      <Paper 
        elevation={12} 
        sx={{ p: 5, borderRadius: 5, background: 'linear-gradient(145deg, #f0f4f8, #ffffff)' }}
      >
        <Stack spacing={3} alignItems="center">
          <Typography variant="h4" color="primary" fontWeight="bold">SnapUPI</Typography>

          <Button
            variant="contained"
            color="primary"
            onClick={genUPI}
            sx={{
              textTransform: 'none',
              fontWeight: 'bold',
              px: 4,
              py: 1.5,
              borderRadius: 3,
              boxShadow: 4,
              '&:hover': { transform: 'scale(1.05)', boxShadow: 6 }
            }}
          >
            Generate UPI
          </Button>

          {upi && (
            <Paper 
              elevation={8} 
              sx={{ p: 3, width: '100%', borderRadius: 4, background: '#ffffff', transition: '0.3s', '&:hover': { transform: 'translateY(-4px)', boxShadow: 10 } }}
            >
              <Stack spacing={2}>
                <Stack direction="row" spacing={2} alignItems="center">
                  <Typography variant="body1" fontWeight="bold">UPI:</Typography>
                  <Typography variant="body1" sx={{ wordBreak: 'break-all' }}>{upi}</Typography>
                  <Button
                    variant="contained"
                    color="secondary"
                    onClick={sendCollect}
                    sx={{ ml: 'auto', textTransform: 'none', fontWeight: 'bold' }}
                  >
                    Request Collect ₹10
                  </Button>
                </Stack>

                {tx && (
                  <Stack direction="row" spacing={2} alignItems="center">
                    <Typography variant="body2"><b>Tx ID:</b> {tx}</Typography>
                    <Chip
                      label={status}
                      color={getStatusColor(status)}
                      variant="filled"
                      sx={{ ml: 2, fontWeight: 'bold', px: 2, py: 0.5 }}
                    />
                  </Stack>
                )}
              </Stack>
            </Paper>
          )}
        </Stack>

        <Divider sx={{ my: 5 }} />

        <Box>
          <Typography variant="h6" gutterBottom fontWeight="bold">How it Works (Technical Explanation)</Typography>
          <Typography variant="body2" sx={{ mb: 1 }}>
            1. The frontend calls <code>/api/generate_upi</code> to request a unique UPI ID from the backend.
          </Typography>
          <Typography variant="body2" sx={{ mb: 1 }}>
            2. The backend generates a unique UPI by creating a random identifier and appending a bank handle, returning it as JSON.
          </Typography>
          <Typography variant="body2" sx={{ mb: 1 }}>
            3. Clicking “Request Collect” sends <code>/api/collect</code> with the UPI and amount.
          </Typography>
          <Typography variant="body2" sx={{ mb: 1 }}>
            4. The backend stores the transaction in PostgreSQL & Redis with <b>PENDING</b> status and pushes it to a queue.
          </Typography>
          <Typography variant="body2" sx={{ mb: 1 }}>
            5. A background worker updates the status to <b>SUCCESS</b> or <b>FAILED</b>.
          </Typography>
          <Typography variant="body2" sx={{ mb: 1 }}>
            6. Frontend polls <code>/api/status/{'{tx_id}'}</code> every 1.5s to update status live.
          </Typography>
          <Typography variant="body2">
            7. This simulates a real UPI gateway with instant feedback, async processing, and persistence.
          </Typography>
        </Box>
      </Paper>
    </Container>
  );
}

export default App;
