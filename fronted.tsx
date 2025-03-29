// StrategyConfig.tsx
import { useConnection, useWallet } from '@solana/wallet-adapter-react';
import { Box, Slider, Button, Typography } from '@mui/material';

export default function StrategyConfig() {
  const { publicKey } = useWallet();
  const [spread, setSpread] = useState<number>(0.5);
  const [leverage, setLeverage] = useState<number>(2);

  // Submit strategy to Solana program
  const deployStrategy = async () => {
    if (!publicKey) return;
    const tx = await buildTransaction({
      spread,
      leverage,
      owner: publicKey.toBase58(),
    });
    await sendTransaction(tx);
  };

  return (
    <Box>
      <Typography variant="h6">Dynamic Spread: {spread}%</Typography>
      <Slider
        value={spread}
        onChange={(e, v) => setSpread(v as number)}
        min={0.1}
        max={5}
        step={0.1}
      />
      <Typography variant="h6">Leverage: {leverage}x</Typography>
      <Slider
        value={leverage}
        onChange={(e, v) => setLeverage(v as number)}
        min={1}
        max={10}
      />
      <Button onClick={deployStrategy} variant="contained">
        Deploy Bot
      </Button>
    </Box>
  );
}
