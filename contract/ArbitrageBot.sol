// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@uniswap/v3-periphery/contracts/interfaces/ISwapRouter.sol";

contract ArbitrageBot {
    address public owner;
    ISwapRouter public uniswapRouter;
    address public sushiswapRouter;
    uint24 public poolFee = 3000; // 0.3% fee pool
    uint256 public minProfitPercent = 50; // 0.5% minimum profit

    constructor(address _uniswapRouter, address _sushiswapRouter) {
        owner = msg.sender;
        uniswapRouter = ISwapRouter(_uniswapRouter);
        sushiswapRouter = _sushiswapRouter;
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner");
        _;
    }

    // Execute arbitrage with user-specified token
    function executeArbitrage(
        address tokenIn,
        address tokenOut,
        uint256 amountIn,
        uint256 minProfit,
        address dexToSell
    ) external onlyOwner {
        // Simplified price check
        uint256 expectedOut = getPriceFromUniswap(tokenIn, tokenOut, amountIn);
        uint256 sellPrice = getPriceFromSushiSwap(tokenOut, tokenIn);

        require(
            sellPrice >= expectedOut * (10000 + minProfitPercent) / 10000,
            "Insufficient profit"
        );

        // Approve Uniswap to spend tokens
        IERC20(tokenIn).approve(address(uniswapRouter), amountIn);

        // Perform swap on Uniswap
        uniswapRouter.exactInputSingle(
            ISwapRouter.ExactInputSingleParams({
                tokenIn: tokenIn,
                tokenOut: tokenOut,
                fee: poolFee,
                recipient: address(this),
                deadline: block.timestamp + 1200, // 20 minutes
                amountIn: amountIn,
                amountOutMinimum: 0, // Add slippage protection
                sqrtPriceLimitX96: 0
            })
        );

        // Sell on SushiSwap
        uint256 tokenOutBalance = IERC20(tokenOut).balanceOf(address(this));
        IERC20(tokenOut).approve(sushiswapRouter, tokenOutBalance);
        sellOnSushiSwap(tokenOut, tokenIn, tokenOutBalance);
    }

    // Placeholder: Fetch Uniswap price
    function getPriceFromUniswap(
        address tokenIn,
        address tokenOut,
        uint256 amountIn
    ) internal view returns (uint256) {
        // In production, use Uniswap V3 Quoter
        return amountIn; // Simplified
    }

    // Placeholder: Fetch SushiSwap price
    function getPriceFromSushiSwap(
        address tokenIn,
        address tokenOut
    ) internal view returns (uint256) {
        // In production, use SushiSwap SDK
        return 0; // Simplified
    }

    // Placeholder: Sell on SushiSwap
    function sellOnSushiSwap(
        address tokenIn,
        address tokenOut,
        uint256 amountIn
    ) internal {
        // In production, call SushiSwap Router
    }

    // Withdraw profits
    function withdraw(address token) external onlyOwner {
        uint256 balance = IERC20(token).balanceOf(address(this));
        IERC20(token).transfer(owner, balance);
    }
}
