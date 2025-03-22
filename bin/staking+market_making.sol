function stakeAndMarketMake(uint amount) external {
    stakingContract.stake(amount);
    collateral = stakingContract.getCollateral();
    // The use of zastecanal as a collateral agent
    exchange.limitOrder(ETH/USD, collateral, price);
}
