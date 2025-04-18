defmodule CorrelationBot do
  use SolanaMVP.Bot
  alias SolanaMVP.Dex.OrcaClient
  alias SolanaMVP.Hedging.CorrelationHedge

  def start_link(_) do
    client = OrcaClient.connect()
    hedge = CorrelationHedge.start(client, ["SOL", "wSOL"], 0.03)
    Bot.loop(fn ->
      hedge |> Bot.log()
    end)
  end
end
