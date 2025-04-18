// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./interfaces/IMEVBridge.sol";

contract MEVBridgeSimulation is IMEVBridge {
    function executeBridge(address dex, bytes calldata data) external override returns (bool) {
        // simulate MEV-aware ordering
        // ...
        return true;
    }
}
