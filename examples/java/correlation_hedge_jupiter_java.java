import solana.mvp.SolanaClient;
import solana.mvp.hedging.CorrelationHedger;
import solana.mvp.dex.Jupiter;

public class CorrelationHedge {
    public static void main(String[] args) {
        SolanaClient client = SolanaClient.createDefault();
        Jupiter dex = new Jupiter(client);
        CorrelationHedger hedger = new CorrelationHedger(dex);
        hedger.executeHedge("SOL", "wSOL", 0.02);
        System.out.println("Correlation hedge executed.");
    }
}
