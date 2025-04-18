const { LiquidityMiningOptimizer } = require('solana-mvp-sdk');
const { Meteora } = require('solana-mvp-sdk/dex');

async function optimizeFarm() {
    const optimizer = new LiquidityMiningOptimizer(new Meteora());
    const opportunities = await optimizer.findBestPools(['SOL/USDC', 'wSOL/USDC']);
    await optimizer.shiftCapital(opportunities);
}

optimizeFarm().catch(console.error);
