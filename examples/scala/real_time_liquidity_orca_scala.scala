import solana.mvp.{OrcaClient, LiquidityTracker}

object RealtimeLiquidity extends App {
  val client = new OrcaClient()
  val tracker = new LiquidityTracker(client)
  tracker.onUpdate { (pool, liquidity) =>
    println(s"Pool $pool liquidity: $liquidity")
  }
  tracker.start()
}
