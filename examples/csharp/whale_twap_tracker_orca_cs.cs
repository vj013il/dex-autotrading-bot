using System;
using SolanaMVP;
using SolanaMVP.Dex;

namespace WhaleTWAPTracker
{
    class Program
    {
        static void Main(string[] args)
        {
            var orca = new OrcaClient();
            var tracker = new WhaleTWAPTracker(orca);
            tracker.TrackOrders("SOL/USDC", whaleThreshold: 1000);
            Console.WriteLine("Whale TWAP tracking started.");
        }
    }
}
