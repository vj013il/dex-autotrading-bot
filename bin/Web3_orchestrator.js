const { ethers } = require('ethers');

async function executeDeFiStrategy(strategy) {
    const wallet = new ethers.Wallet(privateKey, provider);
    const tx = await wallet.sendTransaction({
        to: strategy.contract,
        data: strategy.calldata
    });
    await tx.wait();
    console.log(`TX hash: ${tx.hash}`);
}
