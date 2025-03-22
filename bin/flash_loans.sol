function arbBetweenExchanges(address asset, uint amount) external {
    IAaveLendingPool(aave).flashLoan(
        address(this),
        asset,
        amount,
        abi.encode(ExecutionParams(msg.sender))
    );
}

function executeOperation(
    address asset,
    uint amount,
    uint premium,
    bytes calldata params
) external {
    // 1. Buy on exchange A
    // 2. Sell on the B exchange
    // 3. Repay the loan + commission
}
