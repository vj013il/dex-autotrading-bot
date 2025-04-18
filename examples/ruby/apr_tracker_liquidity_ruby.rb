require 'solana_mvp'
require 'solana_mvp/dex/raydium'

tracker = SolanaMVP::APRTracker.new(Raydium.new)
pools = tracker.top_pools(limit: 5)
puts "Top pool APRs:"
pools.each { |p| puts "\#{p.pair}: \#{p.apr}%" }
