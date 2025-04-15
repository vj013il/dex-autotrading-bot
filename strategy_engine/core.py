import asyncio
from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, List, Optional
import logging

@dataclass(frozen=True)
class StrategyConfig:
    min_profit: Decimal
    max_slippage: Decimal
    blacklist: List[str]
    dex_priority: List[str]

class StrategyEngine:
    def __init__(self, config: StrategyConfig):
        self.active = False
        self.strategies: Dict[str, BaseStrategy] = {}
        self.config = config
        self.logger = logging.getLogger('strategy_engine')
        self._lock = asyncio.Lock()

    async def register_strategy(self, strategy: 'BaseStrategy'):
        async with self._lock:
            if strategy.name in self.strategies:
                raise ValueError(f"Strategy {strategy.name} already registered")
            self.strategies[strategy.name] = strategy
            self.logger.info(f"Registered strategy: {strategy.name}")

    async def execute_cycle(self):
        """Main strategy execution loop"""
        self.active = True
        while self.active:
            try:
                tasks = [
                    strategy.execute(self.config)
                    for strategy in self.strategies.values()
                ]
                await asyncio.gather(*tasks)
                await asyncio.sleep(0.1)  # 100ms cycle
            except Exception as e:
                self.logger.error(f"Strategy cycle failed: {e}")
                raise

    async def shutdown(self):
        """Graceful shutdown of all strategies"""
        self.active = False
        async with self._lock:
            for strategy in self.strategies.values():
                await strategy.teardown()
            self.strategies.clear()

class BaseStrategy:
    """Abstract base class for trading strategies"""
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f'strategy.{name}')
        
    async def execute(self, config: StrategyConfig):
        """Main strategy execution method"""
        raise NotImplementedError
        
    async def teardown(self):
        """Clean up strategy resources"""
        pass
