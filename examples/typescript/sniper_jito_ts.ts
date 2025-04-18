import { SnipingModule } from 'solana-mvp-sdk';

async function runSniper() {
    const sniper = new SnipingModule({ provider: 'Jito' });
    await sniper.monitorNewPools();
    await sniper.snipe({
        pair: 'SOL/USDC',
        maxSlippage: 0.005,
        antiRugChecks: true
    });
}

runSniper().catch(console.error);
